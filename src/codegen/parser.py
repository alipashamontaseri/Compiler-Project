import os
from collections import defaultdict
from anytree import Node, RenderTree
from .constants import firsts, follows, terminals, rules
# from .utils import load_dict

END_TOKEN = "$"
EPSILON = 'EPSILON'


def get_correct_non_terminal_name(name):
    correct_name = ""
    upper = False
    for c in name:
        if c == "_":
            upper = True
        else:
            correct_name += c.upper() if upper else c
            upper = False
    return correct_name

class Parser:
    def __init__(self, scanner, parse_tree_file, syntax_errors_file, code_gen_file, semantic_errors_file):
        self.scanner = scanner
        self.parse_tree_file = parse_tree_file
        self.syntax_errors_file = syntax_errors_file
        self.code_gen_file = code_gen_file
        self.semantic_errors_file = semantic_errors_file

        self.non_terminals = list(firsts.keys())

        parse_table = defaultdict(lambda: defaultdict(lambda: []))
        self.code_gen_list = [] # should contain 4 address codes
        self.word_size = 4

        self.syntax_error = []
        self.semantic_errors = []

        self.semantic_stack = []
        self.break_stack = []
        self.symbol_table_heap = defaultdict(lambda: []) # dict -> list[(address, type, size)]
        self.symbol_table_stack = defaultdict(lambda: []) # dict -> list[(address, type, size, scope)]
        self.symbol_table_function = defaultdict(lambda: {}) # dict -> each element has following keys: params->[(name, isarray), ...], start_point->PC to where function begins, return_type 
        self.scope_stack = []

        self.stack_pointer_addr = 0
        self.base_pointer_addr = self.stack_pointer_addr + self.word_size
        self.temp_addr = self.base_pointer_addr + self.word_size
        
        for i in range(6):
            self.code_gen_list.append(['ASSIGN', '#0', self.temp_addr + i * self.word_size, ''])
            
        # we can use 3-9 memories as temp
        self.stack_pointer_start = 1000 * self.word_size
        self.base_pointer_diff = 0
        self.heap_pointer_addr = 10 * self.word_size

        # initializing BP and SP
        self.code_gen_list.append(['ASSIGN', f'#{self.stack_pointer_start}', f'{self.stack_pointer_addr}', ''])
        self.code_gen_list.append(['ASSIGN', f'#{self.stack_pointer_start}', f'{self.base_pointer_addr}', ''])

        # parsing stuff

        self.has_epsilon = defaultdict(lambda: False)
        self.look_ahead = None
        self.last_token = None

        for nt in self.non_terminals:
            for rule in rules[nt]:
                if not len(rule):
                    self.has_epsilon[nt] = True
                    continue

                idx = 0
                while(rule[idx][0] == '#'):
                    idx += 1
                first = rule[idx]
                    
                
                if first in terminals:
                    parse_table[nt][first] = rule
                    continue

                for terminal in firsts[first]:
                    if terminal == EPSILON:
                        for t in follows[first]:
                            parse_table[nt][t] = rule
                    else:
                        parse_table[nt][terminal] = rule

            for terminal in follows[nt]:
                if not len(parse_table[nt][terminal]):
                    parse_table[nt][terminal] = None

        self.parse_table = parse_table
        
        #Maybe TODO: Handle setting zero initial variables
        self.jump_main_line = len(self.code_gen_list)
        self.code_gen_list.append(["JP", "?", "", ""])

    def set_zero(self, loc, indirect):
        if not indirect:
            self.code_gen_list.append(['ASSIGN', '#0', str(loc), ''])
        else:
            self.code_gen_list.append(['ASSIGN', '#0', '@' + str(loc), ''])

    def add_to_symbol_heap(self, varname, vartype, varsize):
        self.symbol_table_heap[varname].append([self.heap_pointer_addr, vartype, varsize])
        # print(varsize)
        for i in range(int(varsize)):
            self.set_zero(self.heap_pointer_addr + i * self.word_size, False)
        self.heap_pointer_addr += int(varsize) * self.word_size

    def add_to_symbol_stack(self, varname, vartype, varsize):
        self.symbol_table_stack[varname].append([self.base_pointer_diff, vartype, varsize, len(self.scope_stack)])
        self.set_zero(self.temp_addr, False)
        # print(varsize)
        for i in range(int(varsize)):
            self.code_gen_list.append(['ADD', '#' + str(i * self.word_size + self.base_pointer_diff), str(self.base_pointer_addr), str(self.temp_addr)])
            self.set_zero(self.temp_addr, True)
        self.base_pointer_diff += int(varsize) * self.word_size

    def get_temp_stack(self):
        addr = self.base_pointer_diff
        self.code_gen_list.append(['ADD', str(self.base_pointer_addr), '#' + str(addr), str(self.temp_addr + 6 * self.word_size)])
        self.set_zero(self.temp_addr + 6 * self.word_size, True)
        self.base_pointer_diff += 1 * self.word_size
        return addr

    def pnext_action(self):
        self.semantic_stack.append(self.look_ahead.lexeme)

    def type_action(self):
        self.semantic_stack.append('$')
        self.semantic_stack.append(self.look_ahead.lexeme)

    def scope_plus_action(self):
        self.scope_stack.append(self.base_pointer_diff)

    def scope_minus_action(self):
        self.base_pointer_diff = self.scope_stack[-1]
        self.scope_stack.pop()
        
        # we should know set SP = BP + base_pointer_diff
        self.code_gen_list.append(["ADD", 
                                   str(self.base_pointer_addr), '#' + str(self.base_pointer_diff), str(self.stack_pointer_addr)])
        for key,val in self.symbol_table_stack.items():
            if len(val) > 0 and val[-1][3] > len(self.scope_stack):
                self.symbol_table_stack[key].pop()
        
    # stack_pointer , base_pointer

    def func_start_action(self):
        self.semantic_stack.append('%')
        self.base_pointer_diff = 0


    def func_end_action(self):
        # executes when no return statement is faced
        # withour ret
        # set SP = BP - 2
        # BP = @(BP-1)
        self.code_gen_list.append(["SUB", 
                                   str(self.base_pointer_addr), '#8', str(self.stack_pointer_addr)])
        self.code_gen_list.append(["SUB", 
                                   str(self.base_pointer_addr), '#4', str(self.temp_addr)])
        self.code_gen_list.append(["ASSIGN", 
                                   '@'+str(self.temp_addr), str(self.base_pointer_addr), ''])
        
        self.code_gen_list.append(["ASSIGN", 
                                   '@'+str(self.stack_pointer_addr), str(self.temp_addr + 3 * self.word_size), ''])
        
        self.code_gen_list.append(["JP", 
                                   '@' + str(self.temp_addr + 3 * self.word_size), '', ''])
        

        # with ret
        # set SP = BP - 1
        # BP = @(BP-1)
        # set return->SP-1


    def pvar_action(self):
        # TODO: check if varname has been defined before for semantic analysis
        until_dollar = [] 
        while(self.semantic_stack[-1] != '$'):
            until_dollar.append(self.semantic_stack.pop())
        # print(until_dollar)
        self.semantic_stack.pop()
        if len(until_dollar) == 2: # simple int
            if len(self.scope_stack) == 0: # global variable
                self.add_to_symbol_heap(until_dollar[0], 'int', 1)
            else: # local variable
                self.add_to_symbol_stack(until_dollar[0], 'int', 1)
        elif len(until_dollar) == 3: # array
            if len(self.scope_stack) == 0: # global variable
                self.add_to_symbol_heap(until_dollar[1], 'array', until_dollar[0])
            else: # local variable
                self.add_to_symbol_stack(until_dollar[1], 'array', until_dollar[0])
        else:
            raise Exception("error while defining a variable in semantic stack")

    def pid_action(self):
        id = self.look_ahead.lexeme

        if self.symbol_table_stack[id] != []:
            elem = self.symbol_table_stack[id][-1]
            elem_loc = elem[0]
            elem_type = elem[1]
            elem_size = elem[2]
            elem_scope = elem[3]
            # actual address is BP + elem_loc

            if elem_type not in ['array_func', 'array', 'int']:
                raise ValueError("Error here")
            
            if elem_type == 'array_func':
                self.semantic_stack.append([elem_loc, 'indexed', None])
            else:
                self.semantic_stack.append([elem_loc, 'local'])
                if elem_type == 'array':
                    self.semantic_stack[-1].append(None)
        elif self.symbol_table_heap[id] != []:
            elem = self.symbol_table_heap[id][-1]
            elem_loc = elem[0]
            elem_type = elem[1]
            # actual address is elem_loc
            self.semantic_stack.append([elem_loc, 'global'])
            if elem_type == 'array':
                self.semantic_stack[-1].append(None)
            # print(self.semantic_stack)
        else:
            #Alliance
            self.semantic_stack.append(id)


    def construct_address(self, addr, which, where): # addr is its address, which is either 'local' or 'global', where is the location we want actual address in
        if which == 'global':
            self.code_gen_list.append(['ASSIGN', '#' + str(addr), str(where), ''])
        elif which == 'local':
            self.code_gen_list.append(['ADD', self.base_pointer_addr, '#' + str(addr), str(where)])
        elif which == 'indexed':
            self.code_gen_list.append(['ADD', self.base_pointer_addr, '#' + str(addr), str(where)])
            self.code_gen_list.append(['ASSIGN', '@' + str(where), str(where), ''])
            
    def assign_action(self):
        lhs = self.semantic_stack[-2]
        rhs = self.semantic_stack[-1]
        
        # print(lhs, rhs)
        self.semantic_stack.pop()
        self.semantic_stack.pop()
        self.construct_address(lhs[0], lhs[1], self.temp_addr)
        self.construct_address(rhs[0], rhs[1], self.temp_addr + 1 * self.word_size)
        self.code_gen_list.append(['ASSIGN', '@' + str(self.temp_addr + 1 * self.word_size), '@' + str(self.temp_addr), ''])
        self.semantic_stack.append(lhs)

    def eval_action(self):
    
        lhs = self.semantic_stack[-3]
        op = self.semantic_stack[-2]
        rhs = self.semantic_stack[-1]
        
        # print(self.semantic_stack)
        self.semantic_stack.pop()
        self.semantic_stack.pop()
        self.semantic_stack.pop()


        self.construct_address(lhs[0], lhs[1], self.temp_addr)
        self.construct_address(rhs[0], rhs[1], self.temp_addr + 1 * self.word_size)
        newaddr = self.get_temp_stack()
        self.construct_address(newaddr, 'local', self.temp_addr + 2 * self.word_size)
        if op == '+':
            self.code_gen_list.append(['ADD', '@' + str(self.temp_addr), '@' + str(self.temp_addr + 1 * self.word_size), '@' + str(self.temp_addr + 2 * self.word_size)])
        elif op == '-':
            self.code_gen_list.append(['SUB', '@' + str(self.temp_addr), '@' + str(self.temp_addr + 1 * self.word_size), '@' + str(self.temp_addr + 2 * self.word_size)])
        elif op == '*':
            self.code_gen_list.append(['MULT', '@' + str(self.temp_addr), '@' + str(self.temp_addr + 1 * self.word_size), '@' + str(self.temp_addr + 2 * self.word_size)])
        elif op == '<':
            self.code_gen_list.append(['LT', '@' + str(self.temp_addr), '@' + str(self.temp_addr + 1 * self.word_size), '@' + str(self.temp_addr + 2 * self.word_size)])
        elif op == '==':
            self.code_gen_list.append(['EQ', '@' + str(self.temp_addr), '@' + str(self.temp_addr + 1 * self.word_size), '@' + str(self.temp_addr + 2 * self.word_size)])
        self.semantic_stack.append([newaddr, 'local'])
    
    def add_to_symbol_table_function(self, function_name, start_point, return_type, params): # Alliance
        if self.symbol_table_function.get(function_name) is not None:
            # should be handled if the function has been already declared
            pass
        
        for name, isarray in params:
            self.add_to_symbol_stack(name, 'array_func' if isarray else 'int', 1)
        
        if function_name == 'main':
            self.code_gen_list[self.jump_main_line][1] = str(start_point)
        
        # now suppose it hasn't been declared
        self.symbol_table_function[function_name] = {
            'params': params,
            'start_point': start_point,
            'return_type': return_type
        }

    def add_func_sign_action(self): #Alliance
        start_point = len(self.code_gen_list)
        # In the form of (type, isarray)
        params = []
        while len(self.semantic_stack) and self.semantic_stack[-1] != '%':
            if self.semantic_stack.pop() != ',':
                raise ValueError("There is something wrong here")
            x = self.semantic_stack.pop()
            if x != None:
                params.append((x, False))
            else:
                params.append((self.semantic_stack.pop(), True))
        if self.semantic_stack.pop() != '%':
            raise ValueError("There is something wrong here")
        
        function_name = self.semantic_stack.pop()
        return_type = self.semantic_stack.pop()
        
        if self.semantic_stack.pop() != '$':
            raise ValueError("There is something wrong here")
        
        self.add_to_symbol_table_function(function_name, start_point, return_type, params)
    
    def addparam_action(self): #Alliance
        # Just push something to distinguish between parameters
        self.semantic_stack.append(',')

    def prepare_call_action(self): # Alliance implements
        self.semantic_stack.append('$')
    
    def jump_action(self): # Alliance implements
        return_address_temp = self.get_temp_stack()
        
        base_pointer_address_temp = self.get_temp_stack()
        # sets the previous base pointer address
        self.construct_address(base_pointer_address_temp, 'local', self.temp_addr)
        self.code_gen_list.append(["ASSIGN", f"{self.base_pointer_addr}", f"@{self.temp_addr}" , ""])
        
        last_base_diff = self.base_pointer_diff
        
        # self.code_gen_list.append(['ASSIGN', self.base_pointer_addr, f"{5  self.word_size + self.temp_addr}", ""])
        
        params = []
        while self.semantic_stack[-1] != '$':
            params.append(self.semantic_stack.pop(-1))
            
        if not self.semantic_stack or self.semantic_stack[-1] != '$':
            raise ValueError("Ridim")

        self.semantic_stack.pop(-1)
        function_name = self.semantic_stack.pop(-1)
        
        if function_name == 'output':
            if len(params) != 1:
                raise ValueError("output function requires exactly one parameter")
            if len(params[0]) != 2:
                raise ValueError("Only integer values can be printed, not arrays!")
            self.construct_address(params[0][0], params[0][1], self.temp_addr)
            self.code_gen_list.append(["PRINT", f"@{self.temp_addr}", "", ""])
            self.semantic_stack.append(None)
            return
        
        params = params[::-1]
        
        # TODO: semantic analysis, check function's signature
        
        for param in params:
            loc = param[0]
            which = param[1]
            if len(param) == 2:
                temp = self.get_temp_stack()
                self.construct_address(loc, which, self.temp_addr)
                self.construct_address(temp, 'local', self.temp_addr + self.word_size)
                self.code_gen_list.append(["ASSIGN", f"@{self.temp_addr}", f"@{self.temp_addr + self.word_size}", ''])
            elif len(params) == 3:
                # TODO array
                pass
            else:
                raise ValueError("There is something wrong here")
        
        # sets the return address
        self.construct_address(return_address_temp, 'local', self.temp_addr)
        self.code_gen_list.append(["ASSIGN", f"#{len(self.code_gen_list)+3}", f"@{self.temp_addr}", ''])
        
        # TODO check if function exists
        if self.symbol_table_function.get(function_name) is None:
            pass
        
        # sets the current base pointer address (for the function to be called)
        self.code_gen_list.append(["ADD", f"#{last_base_diff}", self.base_pointer_addr, self.base_pointer_addr])
        
        # finally jumps to the function that is being called
        self.code_gen_list.append(["JP", self.symbol_table_function[function_name]['start_point'], "", ""])
        self.base_pointer_diff = last_base_diff - 2 * self.word_size
        if self.symbol_table_function[function_name]['return_type'] == 'int':
            self.semantic_stack.append([self.base_pointer_diff, 'local'])
            self.base_pointer_diff += 1 * self.word_size
        else:
            self.semantic_stack.append(None)
    
    def pusharg_action(self): # Alliance implements
        pass

    def neg_action(self): # pasha implements
        tp = self.semantic_stack[-1]
        self.construct_address(tp[0], tp[1], self.temp_addr)
        self.code_gen_list.append(['SUB', '#0', '@' + str(self.temp_addr), '@' + str(self.temp_addr)])

    def pnum_action(self):
        num = self.look_ahead.lexeme
        addr = self.get_temp_stack()
        self.construct_address(addr, 'local', self.temp_addr)
        self.code_gen_list.append(['ASSIGN', '#' + str(num), '@' + str(self.temp_addr), ''])
        self.semantic_stack.append([addr, 'local'])

    def get_element_action(self):
        id = self.semantic_stack[-2]
        exp = self.semantic_stack[-1]
        
        self.semantic_stack.pop()
        self.semantic_stack.pop()

        newaddr = self.get_temp_stack()

        print('blah',newaddr)

        self.construct_address(id[0], id[1], self.temp_addr)
        self.construct_address(exp[0], exp[1], self.temp_addr + 1 * self.word_size)
        self.construct_address(newaddr, 'local', self.temp_addr + 2 * self.word_size)

        self.code_gen_list.append(['ADD', '@' + str(self.temp_addr), '@' + str(self.temp_addr + 1 * self.word_size), '@' + str(self.temp_addr + 2 * self.word_size)])
        
        self.semantic_stack.append([newaddr, 'indexed'])
    
    def parray_action(self):
        # Just push something to distinguish between array parameters and integers
        self.semantic_stack.append(None)

    def pop_action(self):
        self.semantic_stack.pop()


    def while_start_action(self):
        self.semantic_stack.append(len(self.code_gen_list))

    def while_end_action(self):
        
        jpf = self.semantic_stack[-1]
        jp = self.semantic_stack[-2]

        self.semantic_stack.pop()
        self.semantic_stack.pop()

        self.code_gen_list.append(['JP', str(jp), '', ''])

        while len(self.break_stack) > 0 and self.break_stack[-1][0] > len(self.scope_stack):
            self.code_gen_list[self.break_stack[-1][1]][1] = str(len(self.code_gen_list))
            self.break_stack.pop()

        self.code_gen_list[int(jpf)][2] = str(len(self.code_gen_list))


    def check_condition_while_action(self):
        addr = self.semantic_stack[-1]
        self.semantic_stack.pop()

        self.construct_address(addr[0], addr[1], self.temp_addr)
        self.semantic_stack.append(len(self.code_gen_list))

        self.code_gen_list.append(["JPF", '@' + str(self.temp_addr), '?', ''])

    def break_action(self):
        self.break_stack.append([len(self.scope_stack), len(self.code_gen_list)])
        self.code_gen_list.append(["JP", '?', '', ''])


    def start_if_action(self):
        addr = self.semantic_stack[-1]
        self.semantic_stack.pop()
        
        self.construct_address(addr[0], addr[1], self.temp_addr)
        
        self.semantic_stack.append(len(self.code_gen_list))

        self.code_gen_list.append(['JPF', '@' + str(self.temp_addr), '?' , ''])


    def start_else_action(self):
        line_addr = self.semantic_stack[-1]
        self.semantic_stack.pop()
        self.semantic_stack.append(len(self.code_gen_list))
        self.code_gen_list.append(["JP", "?" ,"" ,""])
        self.code_gen_list[int(line_addr)][2] = len(self.code_gen_list)
        

    def end_else_action(self):
        line_addr = self.semantic_stack[-1]
        self.semantic_stack.pop()
        self.code_gen_list[int(line_addr)][1] = len(self.code_gen_list)

    def return_value_action(self):
        
        if len(self.semantic_stack[-1]) != 2:
            raise ValueError("Some Error here")
        
        value_addr, which = self.semantic_stack.pop()
        
        # first construct the absolute address of the return value and store this address in temp[4]
        self.construct_address(value_addr, which, self.temp_addr + 4 * self.word_size)
    
        # self.code_gen_list.append(["ASSIGN", , ,])
        
        self.code_gen_list.append(["SUB", 
                                   str(self.base_pointer_addr), '#8', str(self.stack_pointer_addr)])
        # Now copy the return address to temp[5]
        self.code_gen_list.append(["ASSIGN", f"@{self.stack_pointer_addr}", str(self.temp_addr + 5 * self.word_size), ""])
        

        self.code_gen_list.append(["ASSIGN", f"@{self.temp_addr + 4 * self.word_size}", f"@{self.stack_pointer_addr}", ""])

        self.code_gen_list.append(["SUB", 
                                   str(self.base_pointer_addr), '#4', str(self.temp_addr)])
        self.code_gen_list.append(["ASSIGN", 
                                   '@'+str(self.temp_addr), str(self.base_pointer_addr), ''])
        
        self.code_gen_list.append(["ASSIGN", 
                                   '@' + str(self.temp_addr + 5 * self.word_size), '@' + str(self.temp_addr + 5 * self.word_size), ''])

        self.code_gen_list.append(["JP", 
                                   '@' + str(self.temp_addr + 5 * self.word_size), '', ''])

    def handle_actions(self, action):
        print(action)
        if action == 'pnext':
            self.pnext_action()
        elif action == 'type':
            self.type_action()
        elif action == 'pvar':
           self.pvar_action()
        elif action == 'scope_plus':
            self.scope_plus_action()
        elif action == 'scope_minus':
            self.scope_minus_action()
        elif action == 'func_start':
            self.func_start_action()
        elif action == 'func_end':
            self.func_end_action()
        elif action == 'pid':
            self.pid_action()
        elif action == 'assign':
            self.assign_action()
        elif action == 'eval':
            self.eval_action()
        elif action == 'neg':
            self.neg_action()
        elif action == 'pnum':
            self.pnum_action()
        elif action == 'get_element':
            self.get_element_action()
        elif action == 'prepare_call':
            self.prepare_call_action()
        elif action == 'jump':
            self.jump_action()
        elif action == 'pusharg':
            self.pusharg_action()
        elif action == 'pop':
            self.pop_action()
        elif action == 'while_start':
            self.while_start_action()
        elif action == 'while_end':
            self.while_end_action()
        elif action == 'check_condition_while':
            self.check_condition_while_action()
        elif action == 'break':
            self.break_action()
        elif action == 'start_if':
            self.start_if_action()
        elif action == 'start_else':
            self.start_else_action()
        elif action == 'end_else':
            self.end_else_action()
        elif action == 'add_func_sign':
            self.add_func_sign_action()
        elif action == 'addparam':
            self.addparam_action()
        elif action == 'parray':
            self.parray_action()
        elif action == 'return_value':
            self.return_value_action()
        else:
            raise Exception('action not defined')
        
        print(self.semantic_stack)
        print(len(self.code_gen_list))
        # print(self.code_gen_list)
        print()

        # print(self.symbol_table_stack)

    def get_next_token(self):
        if self.look_ahead and self.look_ahead.get_terminal() == END_TOKEN:
            self.look_ahead = None
            return
        self.look_ahead = self.scanner.get_next_token()
        self.last_token = self.look_ahead
        # print("Reading input, current_terminal:", self.look_ahead)

    def add_node(self, name, parent):
        if not parent:
            node = self.root = Node(name)
        else:
            node = Node(name, parent=parent)
        return node

    def add_syntax_error(self, token, kind):
        self.syntax_error.append((token.line_number, kind))

    def start_parsing(self):
        self.get_next_token()
        self.root = self.add_node(self.non_terminals[0], None)
        
        # (Name , is_terminal)
        stack = [("$", False), (self.non_terminals[0], True)]
        # None in stack means we should pop one node from current_path
        current_path = []
        
        while len(stack):
            if not self.look_ahead:
                self.add_syntax_error(self.last_token, "Unexpected EOF")
                return
            
            if not stack[-1]:
                stack.pop(-1)
                current_path.pop(-1)
                continue
            if not stack[-1][1] and stack[-1][0][0] == '#':
                self.handle_actions(stack[-1][0][1:])
                stack.pop(-1)
                continue 

            current_node = stack[-1][0]
            if current_node == self.look_ahead.get_terminal() == END_TOKEN:
                self.add_node("$", self.root)
                return

            if self.look_ahead.get_terminal() == current_node:
                self.add_node(str(self.look_ahead), current_path[-1])
                stack.pop(-1)
                self.get_next_token()
                continue
            
            # is a terminal and the terminal is not found
            if not stack[-1][1]:
                if current_node == END_TOKEN:
                    break
                # to be completed - Error handling - Unexpected stack[-1][0]
                self.add_syntax_error(self.look_ahead, f"missing {current_node}")
                stack.pop(-1)
                continue
            
            action = self.parse_table[current_node][self.look_ahead.get_terminal()]
            # print(f"Action[{current_node}][{self.look_ahead.get_terminal()}] = {action}")
            
            if action is None:
                if self.has_epsilon[current_node]:
                    node_of_tree = self.add_node(get_correct_non_terminal_name(current_node),
                     current_path[-1] if len(current_path) else None)
                    self.add_node("epsilon", node_of_tree)
                    stack.pop(-1)
                else:
                    # Missing some non-terminal
                    self.add_syntax_error(self.look_ahead, f"missing {current_node}")
                    # self.add_node(current_node, current_path[-1])
                    stack.pop(-1)
            elif len(action) == 0:
                if self.look_ahead.get_terminal() == END_TOKEN:
                    self.add_syntax_error(self.last_token, "Unexpected EOF")
                    return
                # error, Illegal something
                self.add_syntax_error(self.look_ahead, f"illegal {self.look_ahead.get_terminal()}")
                self.get_next_token()
            else:
                node_of_tree = self.add_node(get_correct_non_terminal_name(current_node),
                 current_path[-1] if len(current_path) else None)
                current_path.append(node_of_tree)
                stack.pop(-1)
                stack.append(None)
                for part in reversed(action):
                    stack.append((part, part in self.non_terminals))
        self.add_node("$", self.root)

    
    def write_parse_tree(self):
        with open(self.parse_tree_file, 'w', encoding="utf-8") as f:
            lines = []
            for pre, _, node in RenderTree(self.root):
                line = "%s%s" % (pre, node.name)
                # print(line)
                lines.append(line)
            f.write('\n'.join(lines))

    def write_syntax_errors(self):
        with open(self.syntax_errors_file, "w", encoding="utf-8") as f:
            if not len(self.errors):
                f.write("There is no syntax error.")
            else:
                f.write('\n'.join([f"#{line_number} : syntax error, {error}" for line_number, error in self.errors]))

    def write_code_gen(self):
        self.code_gen_list = self.code_gen_list[:-5]
        self.code_gen_list.append(['ASSIGN', '#0' ,'0', ''])
        with open(self.code_gen_file, 'w', encoding="utf-8") as f:
            f.write('\n'.join([f'{line_no}\t({x[0]}, {x[1]}, {x[2]}, {x[3]})' for line_no,x in enumerate(self.code_gen_list)]))

    def write_semantic_errors(self):
        pass
    
    def write_logs(self):
        self.write_code_gen()
        self.write_semantic_errors()
        