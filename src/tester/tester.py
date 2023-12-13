import os
import filecmp
from compiler import Compiler
from tester.utils import check_symbols, extract_tokens, check_lines, check_tokens

class Tester:
    def __init__(self, test_dir):
        self.test_dir = os.path.abspath(test_dir)
        
    def test(self, phase=1, num_tests=10, passive=False, keep_output=True):
    
        print(f"Testing the testcases of phase{phase} ...")
        cnt_correct = 0
        cnt_all = 0
        for i in range(1, 1+num_tests):
            print(f"Working on test {i} ...")
            try:
                simple_path = os.path.join(self.test_dir, f"T{i}")
                if os.path.exists(simple_path):
                    os.chdir(simple_path)
                else:
                    os.chdir(os.path.join(self.test_dir, f"T{i:02}"))
            except Exception as e:
                print("Testcase not found! Error:")
                print(e)
                return    
            if phase == 1:
                compiler = Compiler(tokens_file="()tokens.txt",
                                    lexical_errors_file="()lexical_errors.txt",
                                    symbol_table_file="()symbol_table.txt",
                                    compile_mode="scanner",
                                    log_scanner=True)
                                    
                targets = ["lexical_errors", "symbol_table", "tokens"]
            elif phase == 2:
                compiler = Compiler(parse_tree_file="()parse_tree.txt",
                                    syntax_errors_file="()syntax_errors.txt",
                                    compile_mode="parser",
                                    log_parser=True)

                targets = ["parse_tree", "syntax_errors"]
            try:
                compiler.compile()
            except Exception as e:
                print(e)
                continue
            correct = True
            
            for file in targets:
                try:
                    if file == "symbol_table":
                        eq_func = check_symbols
                    elif file == "tokens":
                        eq_func = check_tokens
                    else:
                        eq_func = check_lines
                        
                    if not eq_func(f"{file}.txt", f"(){file}.txt"):
                        print(file)
                        correct = False
                        break
                except Exception as e:
                    print("Exception occured during testing. Error:")
                    print(e)
                    correct = False
                    break
            
            
            if not keep_output:
                for file in targets:
                    try:
                        os.remove(f"(){file}.txt")
                    except Exception as e:
                        continue
            
            if not correct:
                print("Failed on test", i)
                all_correct = False
                if not passive:
                    break
            else:
                cnt_correct += 1
                print(f"Test {i} passed successfully!")

            cnt_all += 1
        if cnt_all == cnt_correct:
            print("All tests has been passed successfully! (100/100)")
        else:
            print(f"Failed! ({cnt_correct/cnt_all * 100:.2f})")
        
        