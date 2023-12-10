import os, sys
from tester.tester import Tester

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

if __name__ == "__main__":
    tester = Tester(os.path.join(os.getcwd(), "test_data", "P2"))
    tester.test(phase=2)