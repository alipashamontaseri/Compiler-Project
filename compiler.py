from scanner.scanner import Scanner
import os, sys

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

if __name__ == "__main__":
    
    ## Phase 1
    while scanner.get_next_token() != "$":
        continue

    scanner.write_errors()
    scanner.write_symbol_table()
    scanner.write_tokens()
