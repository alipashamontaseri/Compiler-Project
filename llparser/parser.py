import os
from collections import defaultdict
from anytree import Node, RenderTree
from .constants import firsts, follows, terminals, rules
# from .utils import load_dict

END_TOKEN = "$"
EPSILON = 'EPSILON'

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

        for nt in self.non_terminals:
            for rule in rules[nt]:
                if not len(rule):
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
        return self.scanner.get_next_token()

    def add_node(self, name, parent, token=None):

        if not parent:
            node = self.root = Node(name)
        else:
            node = Node(name, parent=parent)
        return node

    def start_parsing(self):
        look_ahead = self.get_next_token()
        self.root = self.add_node(self.non_terminals[0], None)
        stack = [("$", None), (self.non_terminals[0], self.root)]
        
        while True:
            if stack[-1][0] == END_TOKEN == look_ahead.get_terminal():
                return

            if look_ahead.get_terminal() == stack[-1][0]:
                stack.pop(-1)
                look_ahead = self.get_next_token()
                continue
            current_node = stack[-1][1]
            action = self.parse_table[stack[-1][0]][look_ahead.get_terminal()]
            
            if not action:
                stack.pop(-1)
            elif len(action) == 0:
                # error
                pass
            else:
                stack.pop(-1)
                for part in reversed(action):
                    stack.append((part, self.add_node(part, parent=current_node)))
            
            
    def write_parse_tree(self):
        for pre, _, node in RenderTree(self.root):
            print("%s%s" % (pre, node.name))

    def write_syntax_errors(self):
        with open(self.syntax_errors_file, "w") as f:
            if not len(self.errors):
                f.write("There is no syntax error.")
            else:
                f.writelines(self.errors)
            
    def write_logs(self):
        self.write_parse_tree()
        self.write_syntax_errors()
