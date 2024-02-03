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

        self.syntax_error = []
        self.semantic_errors = []

        self.semantic_stack = []
        self.symbol_table_heap = defaultdict(lambda: []) # dict -> list[(address, type, size)]
        self.symbol_table_stack = defaultdict(lambda: []) # dict -> list[(address, type, size, scope)]
        self.scope_stack = []

        self.stack_pointer_addr = 1
        self.base_pointer_addr = 2
        self.temp_addr = 3
        for i in range(3,10):
            self.set_zero(i, False)
        # we can use 3-9 memories as temp
        self.stack_pointer_start = 1000
        self.base_pointer_diff = 0
        self.heap_pointer_addr = 10

        # initializing BP and SP
        self.code_gen_list.append(['ASSIGN', f'#{self.stack_pointer_start}', f'{self.stack_pointer_addr}', ''])
        self.code_gen_list.append(['ASSIGN', f'#{self.stack_pointer_start}', f'{self.base_pointer_addr}', ''])



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

    def set_zero(self, loc, indirect):
        if not indirect:
            self.code_gen_list.append(['ASSIGN', '#0', str(loc), ''])
        else:
            self.code_gen_list.append(['ASSIGN', '#0', '@' + str(loc), ''])

        
    
    def add_to_symbol_heap(self, varname, vartype, varsize):
        self.symbol_table_heap[varname].append([self.heap_pointer_addr, vartype, varsize])
        # print(varsize)
        for i in range(int(varsize)):
            self.set_zero(self.heap_pointer_addr + i, False)
        self.heap_pointer_addr += int(varsize)

    def add_to_symbol_stack(self, varname, vartype, varsize):
        self.symbol_table_stack[varname].append([self.base_pointer_diff, vartype, varsize, len(self.scope_stack)])
        self.set_zero(self.temp_addr, False)
        # print(varsize)
        for i in range(int(varsize)):
            self.code_gen_list.append(['ADD', '#' + str(i + self.base_pointer_diff), str(self.base_pointer_addr), str(self.temp_addr)])
            self.set_zero(self.temp_addr, True)
        self.base_pointer_diff += int(varsize)

    def get_temp_stack(self):
        addr = self.base_pointer_diff
        self.code_gen_list.append(['ADD', str(self.base_pointer_addr), '#' + str(addr), str(self.temp_addr)])
        self.set_zero(self.temp_addr, True)
        self.base_pointer_diff += 1
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
        self.base_pointer_diff = 0
        self.scope_stack.append(self.base_pointer_diff)

    def func_end_action(self):
        self.code_gen_list.append(["SUB", 
                                   str(self.base_pointer_addr), '#2', str(self.stack_pointer_addr)])
        self.code_gen_list.append(["SUB", 
                                   str(self.base_pointer_addr), '#1', str(self.temp_addr)])
        self.code_gen_list.append(["ASSIGN", 
                                   '@'+str(self.temp_addr), str(self.base_pointer_addr), ''])
        self.code_gen_list.append(["JP", 
                                   '@' + str(self.stack_pointer_addr), '', ''])
        # withour ret
        # set SP = BP - 2
        # BP = @(BP-1)

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
            elem_score = elem[3]
            # actual address is BP + elem_loc
            self.semantic_stack.append([elem_loc, 'local'])
        elif self.symbol_table_heap[id] != []:
            elem = self.symbol_table_heap[id][-1]
            elem_loc = elem[0]
            # actual address is elem_loc
            self.semantic_stack.append([elem_loc, 'global'])
            # print(self.semantic_stack)
        else:
            # now we should handle function
            print(id, 'not defined or is a func') # handle later for semantic analysis


    def construct_address(self, addr, which, where): # addr is its address, which is either 'local' or 'global', where is the location we want actual address in
        if which == 'global':
            self.code_gen_list.append(['ASSIGN', '#' + str(addr), str(where), ''])
        elif which == 'local':
            self.code_gen_list.append(['ADD', self.base_pointer_addr, '#' + str(addr), str(where)])
        elif which == 'indexed':
            self.code_gen_list.append(['ADD', self.base_pointer_addr, str(addr), str(where)])
    def assign_action(self):
        lhs = self.semantic_stack[-2]
        rhs = self.semantic_stack[-1]
        # print(lhs, rhs)
        self.semantic_stack.pop()
        self.semantic_stack.pop()
        self.construct_address(lhs[0], lhs[1], self.temp_addr)
        self.construct_address(rhs[0], rhs[1], self.temp_addr + 1)
        self.code_gen_list.append(['ASSIGN', '@' + str(self.temp_addr + 1), '@' + str(self.temp_addr), ''])


    def eval_action(self):
    
        lhs = self.semantic_stack[-3]
        op = self.semantic_stack[-2]
        rhs = self.semantic_stack[-1]
        
        self.semantic_stack.pop()
        self.semantic_stack.pop()
        self.semantic_stack.pop()

        # print(self.semantic_stack)
        self.construct_address(lhs[0], lhs[1], self.temp_addr)
        self.construct_address(rhs[0], rhs[1], self.temp_addr + 1)
        newaddr = self.get_temp_stack()
        self.construct_address(newaddr, 'local', self.temp_addr + 2)
        if op == '+':
            self.code_gen_list.append(['ADD', '@' + str(self.temp_addr), '@' + str(self.temp_addr + 1), '@' + str(self.temp_addr + 2)])
        elif op == '-':
            self.code_gen_list.append(['SUB', '@' + str(self.temp_addr), '@' + str(self.temp_addr + 1), '@' + str(self.temp_addr + 2)])
        elif op == '*':
            self.code_gen_list.append(['MULT', '@' + str(self.temp_addr), '@' + str(self.temp_addr + 1), '@' + str(self.temp_addr + 2)])
        elif op == '<':
            self.code_gen_list.append(['LT', '@' + str(self.temp_addr), '@' + str(self.temp_addr + 1), '@' + str(self.temp_addr + 2)])
        elif op == '==':
            self.code_gen_list.append(['EQ', '@' + str(self.temp_addr), '@' + str(self.temp_addr + 1), '@' + str(self.temp_addr + 2)])
        self.semantic_stack.append([newaddr, 'local'])

    def prepare_call_action(self): # Alliance implements
        pass
    
    def jump_action(self): # Alliance implements
        pass
    
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

    def get_element_action(self): # pasha implements
        id = self.semantic_stack[-2]
        exp = self.semantic_stack[-1]
        
        self.semantic_stack.pop()
        self.semantic_stack.pop()

        newaddr = self.get_temp_stack()

        self.construct_address(id[0], id[1], self.temp_addr)
        self.construct_address(exp[0], exp[1], self.temp_addr + 1)
        self.construct_address(newaddr, 'local', self.temp_addr + 2)

        self.code_gen_list.append(['ADD', '@' + str(self.temp_addr), '@' + str(self.temp_addr + 1), '@' + str(self.temp_addr + 2)])
        
        self.semantic_stack.append([newaddr, 'indexed'])
    



    def handle_actions(self, action):
        # print(action)
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

        # print(action)
        # print(self.semantic_stack)

        # print()

         
        
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
        with open(self.code_gen_file, 'w', encoding="utf-8") as f:
            f.write('\n'.join([f'{line_no}\t({x[0]}, {x[1]}, {x[2]}, {x[3]})' for line_no,x in enumerate(self.code_gen_list)]))

    def write_semantic_errors(self):
        pass
    
    def write_logs(self):
        self.write_code_gen()
        self.write_semantic_errors()
        