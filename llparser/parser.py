
class Parser:
    def __init__(self, scanner, parse_tree_file, syntax_errors_file):
        self.scanner = scanner
        self.parse_tree_file = parse_tree_file
        self.syntax_errors_file = syntax_errors_file

    def write_parse_tree(self):
        pass

    def write_syntax_errors(self):
        pass

    def write_logs(self):
        self.write_parse_tree()
        self.write_syntax_errors()