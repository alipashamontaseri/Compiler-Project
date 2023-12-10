from collections import defaultdict
from .constants import *
from utils import add_dict_list

class DFA:
    def __init__(self):
        num_states = 23
        table = [dict() for i in range(num_states + 1)]  # dfa transition
        # 1
        add_dict_list(table[1], NUM, 2)
        add_dict_list(table[1], SYMBOLS, 5)
        add_dict_list(table[1], WHITESPACES, 20)

        table[1]['/'] = 6
        table[1]['*'] = 12
        table[1]['='] = 16
        add_dict_list(table[1], ID, 21)
        table[1] = defaultdict(lambda: 0, table[1])
        # 2
        add_dict_list(table[2], NUM, 2)
        add_dict_list(table[2], WHITESPACES, 3)
        add_dict_list(table[2], SYMBOLS, 3)
        table[2] = defaultdict(lambda: 4, table[2])
        # 3,4,5 : terminal
        # 6
        add_dict_list(table[6], ID, 8)
        add_dict_list(table[6], NUM, 8)
        add_dict_list(table[6], WHITESPACES, 8)
        table[6]['*'] = 9
        table[6] = defaultdict(lambda: 7, table[6])
        # 7,8 : terminal
        # 9
        table[9]['*'] = 10
        table[9] = defaultdict(lambda: 9, table[9])
        # 10
        table[10]['*'] = 10
        table[10]['/'] = 11
        table[10] = defaultdict(lambda: 9, table[10])
        # 11 : terminal
        # 12
        add_dict_list(table[12], ID, 13)
        add_dict_list(table[12], NUM, 13)
        add_dict_list(table[12], WHITESPACES, 13)
        add_dict_list(table[12], SYMBOLS, 13)
        table[12]['/'] = 14
        table[12] = defaultdict(lambda: 15, table[12])
        # 13,14,15 : terminal
        # 16
        add_dict_list(table[16], ID, 18)
        add_dict_list(table[16], NUM, 18)
        add_dict_list(table[16], WHITESPACES, 18)
        add_dict_list(table[16], SYMBOLS, 18)
        table[16]['='] = 17
        table[16] = defaultdict(lambda: 19, table[16])
        # 17,18,19,20 : terminal
        # 21
        add_dict_list(table[21], ID, 21)
        add_dict_list(table[21], NUM, 21)
        add_dict_list(table[21], SYMBOLS, 22)
        add_dict_list(table[21], WHITESPACES, 22)
        table[21] = defaultdict(lambda: 23, table[21])
        # 22,23 : terminal

        # how to proceed after reaching a state
        state_type = ['NORMAL' for i in range(num_states + 1)]
        # whether we should redo a character or not
        should_redo = [0 for i in range(num_states + 1)]
        should_redo[3] = should_redo[7] = should_redo[8] = should_redo[13] = should_redo[18] = should_redo[22] = 1
        state_type[0] = state_type[4] = state_type[15] = state_type[19] = state_type[23] = 'ERROR'
        state_type[3] = 'NUM'
        state_type[5] = "SYMBOL"
        state_type[7] = "SYMBOL"
        state_type[8] = 'SYMBOL'
        state_type[11] = 'COMMENT'
        state_type[13] = 'SYMBOL'
        state_type[14] = 'UNCLOSED COMMENT'
        state_type[17] = 'SYMBOL'
        state_type[18] = 'SYMBOL'
        state_type[20] = "WHITESPACE"
        state_type[22] = 'ID'

        self.table = table
        self.state_type = state_type
        self.should_redo = should_redo
        
        self.current_state = 1

    def next_state(self, character):
        self.current_state = self.table[self.current_state][character]
        
        return self.current_state


class Scanner:
    def __init__(self, inputfile="input.txt"):
        with open(inputfile, "r") as f:
            self.content = f.read()
            self.content += "\n"
            self.length = len(self.content)
        self.current_state = 1
        self.pointer = 0
        self.all_tokens = []
        self.line_tokens = []
        self.all_errors = []
        self.line_errors = []
        self.symbol_table = KEYWORDS.copy()

        self.line_number = 1
        self.cc_line_number = 1
        
        self.dfa = DFA()

        
    def write_errors(self, filepath="lexical_errors.txt"):
        with open(filepath, 'w') as f:
            line_no = 0
            have_written = False
            for error_line in self.all_errors:
                line_no += 1
                if len(error_line) == 0:
                    continue
                have_written = True
                f.write(str(line_no) + ".\t")
                cnt = 0
                for error in error_line:
                    if cnt > 0:
                        f.write(" ")
                    cnt += 1
                    f.write("(" + error[0] + ", " + error[1] + ")")
                f.write("\n")
            if not have_written:
                f.write("There is no lexical error.")


    def write_tokens(self, filepath="tokens.txt"):
        with open(filepath, "w") as f:
            line_no = 0

            for token_line in self.all_tokens:
                line_no += 1
                if len(token_line) == 0:
                    continue

                f.write(str(line_no) + ".\t")
                cnt = 0
                for token in token_line:
                    if cnt > 0:
                        f.write(" ")
                    cnt += 1
                    f.write("(" + token[0] + ", " + token[1] + ")")
                f.write("\n")


    def write_symbol_table(self, filepath="symbol_table.txt"):
        with open(filepath, "w") as f:
            cnt = 0
            for k in self.symbol_table:
                cnt += 1
                f.write(str(cnt) + ".\t" + k + "\n")

    def get_next_token(self):
        current_token = ""
        token_found = False
        state_type = self.dfa.state_type

        while self.pointer < self.length:
            current_char = self.content[self.pointer]
            if current_char == '\n':
                self.line_number += 1

            next_state = self.dfa.next_state(current_char)
            did_forward = 0
            if self.dfa.should_redo[next_state] == 0:
                did_forward = 1
                self.pointer += 1
                current_token += current_char

            if state_type[next_state] != 'NORMAL':
                self.dfa.current_state = 1
                self.cc_line_number = self.line_number

            if state_type[next_state] == 'ERROR':
                if current_token[-1] in ID and current_token[0] in NUM:
                    self.line_errors.append([current_token, "Invalid number"])
                else:
                    self.line_errors.append([current_token, "Invalid input"])
                current_token = ""

            if state_type[next_state] == 'NUM':
                self.line_tokens.append(["NUM", current_token])
                token_found = True

            if state_type[next_state] == 'SYMBOL':
                self.line_tokens.append(["SYMBOL", current_token])
                token_found = True
            
            if state_type[next_state] in ['WHITESPACE', 'COMMENT']:
                current_token = ""

            if state_type[next_state] == 'UNCLOSED COMMENT':
                self.line_errors.append([current_token, "Unmatched comment"])
                current_token = ""

            if state_type[next_state] == 'ID':
                if current_token not in self.symbol_table:  # this has high complexity maybe I should fix it later
                    self.symbol_table.append(current_token)
                if current_token in KEYWORDS:
                    self.line_tokens.append(["KEYWORD", current_token])
                else:
                    self.line_tokens.append(["ID", current_token])
                token_found = True

            if current_char == '\n':
                self.all_tokens.append(self.line_tokens)
                self.all_errors.append(self.line_errors)
                self.line_tokens = []
                self.line_errors = []
                if did_forward == 0:
                    self.pointer += 1
            if token_found:
                return self.line_tokens[-1]

        current_state = self.dfa.current_state

        if current_state in [9, 10, 11]:
            if len(current_token) > 7:
                self.all_errors[self.cc_line_number -
                        1].append([current_token[:7] + "...", "Unclosed comment"])
            else:
                self.all_errors[self.cc_line_number - 1].append([current_token, "Unclosed comment"])
        
        return "$"