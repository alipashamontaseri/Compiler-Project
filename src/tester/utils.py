def check_symbols(f1, f2):
    sets = []
    for f in [f1, f2]:
        with open(f, 'r', encoding='utf-8') as fl:
            new_set = set()
            lines = fl.readlines()
            for line in lines:
                parts = line.split()
                if len(parts) != 2:
                    return False
                new_set.add(parts[-1])
            sets.append(new_set)
    return sets[0] == sets[1]


def extract_tokens(line):
    tokens = []
    current_token = None
    # Extract number line
    line_number = ""
    for i, c in enumerate(line):
        if c == '.':
            line = line[i+1:]
            tokens.append(line_number)
            break
        elif c not in "0123456789":
            print(c)
            return None, None, None
        else:
            line_number += c
    current_part = ""
    for c in line:
        if c == '(':
            if current_token == None:
                current_token = [None, None]
            else:
                current_part = c
        elif c == ')':
            if not len(current_part):
                current_part = c
                continue
            current_token[1] = current_part
            tokens.append(tuple(current_token))
            current_token = None
        elif c == ' ':
            continue
        elif c == ',':
            if tuple(current_token) == (None, None):
                current_token[0] = current_part
                current_part = ""
            else:
                current_part = c
        else:
            current_part += c
    return tokens


def check_tokens(f1, f2):
    lines1 = []
    lines2 = []
    with open(f1, 'r', encoding='utf-8') as f:
        lines1 = f.readlines()
    with open(f2, 'r', encoding='utf-8') as f:
        lines2 = f.readlines()
    if len(lines1) != len(lines2):
        return False
    for l1, l2 in zip(lines1, lines2):
        t1 = extract_tokens(l1)
        t2 = extract_tokens(l2)
        if not t1 or not t2 or t1 != t2:
            return False
    return True


def check_lines(f1, f2):
    lines1 = []
    lines2 = []
    with open(f1, 'r', encoding='utf-8') as f:
        lines1 = f.readlines()
    with open(f2, 'r', encoding='utf-8') as f:
        lines2 = f.readlines()
    if len(lines1) != len(lines2):
        return False
    for l1, l2 in zip(lines1, lines2):
        if l1.strip() != l2.strip():
            return False
    return True