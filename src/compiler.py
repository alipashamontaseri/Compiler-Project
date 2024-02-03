import os, sys
from scanner.scanner import Scanner
from llparser.parser import Parser as Parser
from codegen.parser import Parser as CodeGenParser

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

class Compiler:
    def __init__(self, inputfile="input.txt", compile_mode="full",
    log_scanner=False,
    log_parser=False,
    log_code_gen=False,
    tokens_file="tokens.txt",
    lexical_errors_file="lexical_errors.txt",
    symbol_table_file="symbol_table.txt",
    parse_tree_file="parse_tree.txt",
    syntax_errors_file="syntax_errors.txt",
    code_gen_file="output.txt",
    semantic_error_file="semantic_errors.txt"
    ):

        self.input_file = inputfile
        self.log_scanner = log_scanner
        self.log_parser = log_parser
        self.compile_mode = compile_mode
        self.log_code_gen = log_code_gen

        scanner = Scanner(inputfile, tokens_file=tokens_file,
                                lexical_errors_file=lexical_errors_file,
                                symbol_table_file=symbol_table_file)
        parser = Parser(scanner, parse_tree_file=parse_tree_file,
                             syntax_errors_file=syntax_errors_file)
        codegenerator = CodeGenParser(scanner, parse_tree_file=parse_tree_file,
                                      syntax_errors_file=syntax_errors_file, 
                                      code_gen_file=code_gen_file,
                                      semantic_errors_file=semantic_error_file)
        self.scanner = scanner
        self.parser = parser
        self.codegenerator = codegenerator

    def compile(self):
        if self.compile_mode == "scanner":
            while self.scanner.get_next_token().get_terminal() != "$":
                continue
        elif self.compile_mode == "parser":
            try:
                self.parser.start_parsing()
            except Exception as e:
                print("The following error has been occured during parsing:")
                print(e)
        elif self.compile_mode == "full":
            # try:
                self.codegenerator.start_parsing()
            # except Exception as e:
            #     print("The following error has been occured during code generation:")
            #     print(e)
            #     exc_type, exc_obj, exc_tb = sys.exc_info()
            #     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            #     print(exc_type, fname, exc_tb.tb_lineno)

        if self.log_scanner:
            self.scanner.write_logs()

        if self.log_parser:
            self.parser.write_logs()

        if self.log_code_gen:
            self.codegenerator.write_logs()


if __name__ == "__main__":
    
    ## Phase 1
    # compiler = Compiler(compile_mode='scanner', log_scanner=True)

    ## Phase 2
    # compiler = Compiler(compile_mode='parse', log_parser=True)

    ## Phase 3
    compiler = Compiler(compile_mode='full', log_code_gen=True)
    
    compiler.compile()
