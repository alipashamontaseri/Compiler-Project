import os

class Tester:
    def __init__(self, test_dir):
        self.test_dir = test_dir
    
    def test(self, num_tests=10):
        for i in range(1, 1+num_tests):
            