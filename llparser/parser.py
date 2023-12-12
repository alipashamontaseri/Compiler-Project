import os
from anytree import Node, RenderTree
from .utils import load_set
from .constants import firsts, follows, terminals

END_TOKEN = "$"

class Parser:
    def __init__(self, scanner, parse_tree_file, syntax_errors_file):
        self.scanner = scanner
        self.parse_tree_file = parse_tree_file
        self.syntax_errors_file = syntax_errors_file

        self.look_ahead = scanner.get_next_token()

        # self.firsts = load_set(os.path.join("llparser", "grammar", "first.set"))
        # self.follows = load_set(os.path.join("llparser", "grammar", "follow.set"))

        self.non_terminals = list(firsts.keys())

        self.parse_tree = None

        self.parse_table = {}

        for nt in non_terminals:
            for terminal in terminals:
                pass

    def match(self, to_be_matched):
        pass

    def start_parsing(self):
        stack = [self.non_terminals[0]]
        
        while True:
            if self.stack[-1] == END_TOKEN == self.look_ahead:
                return
            
    def write_parse_tree(self):
        pass

    def write_syntax_errors(self):
        pass

    def write_logs(self):
        self.write_parse_tree()
        self.write_syntax_errors()

A = Node("A")
B = Node("B", parent=A)
C = Node("C", parent=A)
D = Node("D", parent=C)

for pre, _, node in RenderTree(A):
    print("%s%s" % (pre, node.name))