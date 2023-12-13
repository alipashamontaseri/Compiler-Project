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
    def __init__(self, scanner, parse_tree_file, syntax_errors_file):
        self.scanner = scanner
        self.parse_tree_file = parse_tree_file
        self.syntax_errors_file = syntax_errors_file

        # self.firsts = load_set(os.path.join("llparser", "grammar", "first.set"))
        # self.follows = load_set(os.path.join("llparser", "grammar", "follow.set"))

        self.non_terminals = list(firsts.keys())

        parse_table = defaultdict(lambda: defaultdict(lambda: []))

        self.errors = []

        self.has_epsilon = defaultdict(lambda: False)

        for nt in self.non_terminals:
            for rule in rules[nt]:
                if not len(rule):
                    self.has_epsilon[nt] = True
                    continue

                first = rule[0]
                
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

    def get_next_token(self):
        t = self.scanner.get_next_token()
        # print(t)
        return t

    def add_node(self, name, parent):

        if not parent:
            node = self.root = Node(name)
        else:
            node = Node(name, parent=parent)
        return node

    def add_error(self):
        pass

    def start_parsing(self):
        look_ahead = self.get_next_token()
        self.root = self.add_node(self.non_terminals[0], None)
        
        # (Name , is_terminal)
        stack = [("$", False), (self.non_terminals[0], True)]
        # None in stack means we should pop one node from current_path
        current_path = []
        
        while True:
            # print(stack)
            if not stack[-1]:
                stack.pop(-1)
                current_path.pop(-1)
                continue
            current_node = stack[-1][0]
            if current_node == look_ahead.get_terminal() == END_TOKEN:
                self.add_node("$", self.root)
                return

            if look_ahead.get_terminal() == current_node:
                self.add_node(str(look_ahead), current_path[-1])
                stack.pop(-1)
                look_ahead = self.get_next_token()
                continue
            
            # is a terminal and the terminal is not found
            if not stack[-1][1]:
                # to be completed - Error handling - Missing stack[-1][0]
                self.add_error()
                stack.pop(-1)
                continue
            
            action = self.parse_table[current_node][look_ahead.get_terminal()]
            # print(f"Action[{current_node}][{look_ahead.get_terminal()}] = [{action}]")
            
            if not action:
                if self.has_epsilon[current_node]:
                    node_of_tree = self.add_node(get_correct_non_terminal_name(current_node), current_path[-1] if len(current_path) else None)
                    self.add_node("epsilon", node_of_tree)
                    stack.pop(-1)
                else:
                    # Illegal error
                    self.add_error()
                    look_ahead = self.get_next_token()
            elif len(action) == 0:
                # error
                pass
            else:
                node_of_tree = self.add_node(get_correct_non_terminal_name(current_node), current_path[-1] if len(current_path) else None)
                current_path.append(node_of_tree)
                stack.pop(-1)
                stack.append(None)
                for part in reversed(action):
                    stack.append((part, part in self.non_terminals))
    
    
    def write_parse_tree(self):
        with open(self.parse_tree_file, 'w', encoding="utf-8") as f:
            lines = []
            for pre, _, node in RenderTree(self.root):
                line = "%s%s" % (pre, node.name)
                # print(line)
                lines.append(line)
            f.write('\n'.join(lines))

    def write_syntax_errors(self):
        with open(self.syntax_errors_file, "w") as f:
            if not len(self.errors):
                f.write("There is no syntax error.")
            else:
                f.writelines(self.errors)
            
    def write_logs(self):
        self.write_parse_tree()
        self.write_syntax_errors()
