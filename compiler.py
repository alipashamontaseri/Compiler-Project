from collections import defaultdict

input_file = open("input.txt", "r")
errors_file = open("lexical_errors.txt", "w")
symbol_file = open("symbol_table.txt", "w")
tokens_file = open("tokens.txt", "w")

content = input_file.read()
content += "\n"
length = len(content)

SYMBOLS = list(';:,[](){}+-*=</')
WHITESPACES = [chr(32), chr(10), chr(13), chr(9), chr(11), chr(12)]
NUM = list('0123456789')
ID = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
KEYWORDS = ['if', 'else', 'void', 'int', 'while', 'break', 'return']


def addDictList(dic, ls, val):
    for x in ls:
        dic[x] = val


def buildDFA():
    num_states = 23
    table = [dict() for i in range(num_states + 1)]  # dfa transition
    # 1
    addDictList(table[1], NUM, 2)
    addDictList(table[1], SYMBOLS, 5)
    addDictList(table[1], WHITESPACES, 20)
    table[1]['/'] = 6
    table[1]['*'] = 12
    table[1]['='] = 16
    addDictList(table[1], ID, 21)
    table[1] = defaultdict(lambda: 0, table[1])
    # 2
    addDictList(table[2], NUM, 2)
    addDictList(table[2], WHITESPACES, 3)
    addDictList(table[2], SYMBOLS, 3)
    table[2] = defaultdict(lambda: 4, table[2])
    # 3,4,5 : terminal
    # 6
    addDictList(table[6], ID, 8)
    addDictList(table[6], NUM, 8)
    addDictList(table[6], WHITESPACES, 8)
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
    addDictList(table[12], ID, 13)
    addDictList(table[12], NUM, 13)
    addDictList(table[12], WHITESPACES, 13)
    addDictList(table[12], SYMBOLS, 13)
    table[12]['/'] = 14
    table[12] = defaultdict(lambda: 15, table[12])
    # 13,14,15 : terminal
    # 16
    addDictList(table[16], ID, 18)
    addDictList(table[16], NUM, 18)
    addDictList(table[16], WHITESPACES, 18)
    addDictList(table[16], SYMBOLS, 18)
    table[16]['='] = 17
    table[16] = defaultdict(lambda: 19, table[16])
    # 17,18,19,20 : terminal
    # 21
    addDictList(table[21], ID, 21)
    addDictList(table[21], NUM, 21)
    addDictList(table[21], SYMBOLS, 22)
    addDictList(table[21], WHITESPACES, 22)
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

    return table, state_type, should_redo


table, state_type, should_redo = buildDFA()


current_state = 1
attribute = ""
pointer = 0
all_tokens = []
line_tokens = []
all_errors = []
line_errors = []
symbol_table = ["if", "else", "void", "int", "while", "break", "return"]

line_number = 1
cc_line_number = 1

while pointer < length:
    current_char = content[pointer]
    if current_char == '\n':
        line_number += 1
    # print(current_state, current_char)
    next_state = table[current_state][current_char]
    did_forward = 0
    if should_redo[next_state] == 0:
        did_forward = 1
        pointer += 1
        attribute += current_char
    current_state = next_state
    if state_type[current_state] != 'NORMAL':
        current_state = 1
        cc_line_number = line_number
    if state_type[next_state] == 'ERROR':
        if attribute[-1] in ID and attribute[0] in NUM:
            line_errors.append([attribute, "Invalid number"])
        else:
            line_errors.append([attribute, "Invalid input"])
        attribute = ""
    if state_type[next_state] == 'NUM':
        line_tokens.append(["NUM", attribute])
        attribute = ""
    if state_type[next_state] == 'SYMBOL':
        line_tokens.append(["SYMBOL", attribute])
        attribute = ""
    if state_type[next_state] == 'COMMENT':
        # line_tokens.append(["COMMENT",attribute])
        attribute = ""
    if state_type[next_state] == 'UNCLOSED COMMENT':
        line_errors.append([attribute, "Unmatched comment"])
        attribute = ""
    if state_type[next_state] == 'WHITESPACE':
        attribute = ""
    if state_type[next_state] == 'ID':
        if not attribute in symbol_table:  # this has high complexity maybe I should fix it later
            symbol_table.append(attribute)
        if attribute in KEYWORDS:
            line_tokens.append(["KEYWORD", attribute])
        else:
            line_tokens.append(["ID", attribute])
        attribute = ""

    if current_char == '\n':
        all_tokens.append(line_tokens)
        all_errors.append(line_errors)
        line_tokens = []
        line_errors = []
        if did_forward == 0:
            pointer += 1

if current_state == 9 or current_state == 10 or current_state == 11:
    if len(attribute) > 7:
        all_errors[cc_line_number -
                   1].append([attribute[:7] + "...", "Unclosed comment"])
    else:
        all_errors[cc_line_number - 1].append([attribute, "Unclosed comment"])


def write_errors():
    line_no = 0
    have_written = False
    for error_line in all_errors:
        line_no += 1
        if len(error_line) == 0:
            continue
        have_written = True
        errors_file.write(str(line_no) + ".\t")
        cnt = 0
        for error in error_line:
            if cnt > 0:
                errors_file.write(" ")
            cnt += 1
            errors_file.write("(" + error[0] + ", " + error[1] + ")")
        errors_file.write("\n")
    if not have_written:
        errors_file.write("There is no lexical error.")


def write_tokens():
    line_no = 0

    for token_line in all_tokens:
        line_no += 1
        if len(token_line) == 0:
            continue

        tokens_file.write(str(line_no) + ".\t")
        cnt = 0
        for token in token_line:
            if cnt > 0:
                tokens_file.write(" ")
            cnt += 1
            tokens_file.write("(" + token[0] + ", " + token[1] + ")")
        tokens_file.write("\n")


def write_symbol_table():
    cnt = 0
    for k in symbol_table:
        cnt += 1
        symbol_file.write(str(cnt) + ".\t" + k + "\n")


write_errors()
write_tokens()
write_symbol_table()

input_file.close()
errors_file.close()
symbol_file.close()
tokens_file.close()
