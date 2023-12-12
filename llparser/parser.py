import os
from utils import load_set

class Parser:
    def __init__(self, scanner, parse_tree_file, syntax_errors_file):
        self.scanner = scanner
        self.parse_tree_file = parse_tree_file
        self.syntax_errors_file = syntax_errors_file

        self.look_ahead = None
        self.firsts = load_set(os.path.join("grammar", "first.set"))
        self.follows = load_set(os.path.join("grammar", "follow.set"))

    def write_parse_tree(self):
        pass

    def write_syntax_errors(self):
        pass

    def write_logs(self):
        self.write_parse_tree()
        self.write_syntax_errors()