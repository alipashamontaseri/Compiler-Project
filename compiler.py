from scanner.scanner import Scanner
import os, sys
from tester.tester import Tester

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

if __name__ == "__main__":
    
    ## Phase 1
    # tester = Tester(os.path.join(os.getcwd(), "tester", "P1"))
    # tester.test()

    ## Phase 2
