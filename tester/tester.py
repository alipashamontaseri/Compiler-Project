import os
from scanner.scanner import Scanner
import filecmp

class Tester:
    def __init__(self, test_dir):
        self.test_dir = test_dir
    
    def test(self, num_tests=10, passive=False):
        ok = True

        for i in range(1, 1+num_tests):
            os.chdir(os.path.join(self.test_dir, f"T{i}"))

            scanner = Scanner()

            while scanner.get_next_token() != "$":
                continue

            scanner.write_errors("lexical_errors().txt")
            scanner.write_symbol_table("symbol_table().txt")
            scanner.write_tokens("tokens().txt")

            files = ["lexical_errors", "symbol_table", "tokens"]
            
            for file in files:
                if not filecmp.cmp(f"{file}.txt", f"{file}().txt"):
                    break
            else:
                print("Failed on test", i)
                ok = False
                if not passive:
                    break
        if ok:
            print("All tests has been passed successfully!")