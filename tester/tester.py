import os
import filecmp
from compiler import Compiler

class Tester:
    def __init__(self, test_dir):
        self.test_dir = test_dir
        
    def test(self, phase=1, num_tests=10, passive=False):
        ok = True

        print(f"Testing the testcases of phase{phase} ...")

        for i in range(1, 1+num_tests):
            try:
                simple_path = os.path.join(self.test_dir, f"T{i}")
                if os.path.exists(simple_path):
                    os.chdir(simple_path)
                else:
                    os.chdir(os.path.join(self.test_dir, f"T{i:02}"))
            except:
                print("Testcases not found!")
                return    
            if phase == 1:
                compiler = Compiler(tokens_file="()tokens.txt",
                                    lexical_errors_file="()lexical_errors.txt",
                                    symbol_table_file="()symbol_table.txt",
                                    compile_mode="scanner",
                                    verbose_scanner=True)
                                    
                targets = ["lexical_errors", "symbol_table", "tokens"]
            elif phase == 2:
                compiler = Compiler(parse_tree_file="()parse_tree.txt",
                                    syntax_errors_file="()syntax_errors.txt",
                                    compile_mode="parser",
                                    verbose_parser=True)

                targets = ["parse_tree", "syntax_errors"]

            compiler.compile()

            for file in targets:
                try:
                    if not filecmp.cmp(f"{file}.txt", f"(){file}.txt"):
                        break
                except Exception as e:
                    print("Exception occured during testing:")
                    print(e)
                    return
            else:
                print("Failed on test", i)
                ok = False
                if not passive:
                    break
        if ok:
            print("All tests has been passed successfully!")
        