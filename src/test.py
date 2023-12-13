import os, sys
from tester.tester import Tester

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

if __name__ == "__main__":
    phase = 2
    tester = Tester(os.path.join('..', "test_data", "P" + str(phase)))
    tester.test(phase, keep_output=False, passive=True)