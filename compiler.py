import os, sys
from scanner.scanner import Scanner
from llparser.parser import Parser

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

class Compiler:
    def __init__(self, inputfile="input.txt", compile_mode="full",
    verbose_scanner=False,
    verbose_parser=False,
    tokens_file="tokens.txt",
    lexical_errors_file="lexical_errors.txt",
    symbol_table_file="symbol_table.txt",
    parse_tree_file="parse_tree.txt",
    syntax_errors_file="syntax_errors.txt"
    ):

        self.input_file = inputfile
        self.verbose_scanner = verbose_scanner
        self.verbose_parser = verbose_parser
        self.compile_mode = compile_mode

        scanner = Scanner(inputfile, tokens_file=tokens_file,
                                lexical_errors_file=lexical_errors_file,
                                symbol_table_file=symbol_table_file)
        parser = Parser(scanner, parse_tree_file=parse_tree_file,
                             syntax_errors_file=syntax_errors_file)
        
        self.scanner = scanner
        self.parser = parser

    def compile(self):
        if self.compile_mode == "scanner":
            while self.scanner.get_next_token() != "$":
                continue
        elif self.compile_mode in ["parser", "full"]:
            pass
    
        if self.verbose_scanner:
            self.scanner.write_logs()

        if self.verbose_parser:
            self.parser.write_logs()


if __name__ == "__main__":
    
    ## Phase 1

    ## Phase 2
    pass
