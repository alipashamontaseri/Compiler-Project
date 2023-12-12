import json
import os
from collections import defaultdict

def read_set_from_file(input_file):
    result = defaultdict(lambda: [])

    with open(input_file, 'r') as f:
        lines = f.readlines()

        terminals = lines[0].split()

        for line in lines[1:]:
            parts = line.split()
            nt = parts[0]
            for i, part in enumerate(parts[1:]):
                if part == '+':
                    result[nt].append(terminals[i])
        
    return result

def save_dict(dictionary, filepath):
    with open(filepath, 'w') as f:
        f.write(json.dumps(dictionary))

def load_dict(filepath):
    with open(filepath, 'r') as f:
        return json.loads(f.read())

def read_rules(filepath):
    result = defaultdict(lambda: [])

    with open(filepath, 'r') as f:
        lines = f.readlines()
        for line in lines:
            lhs = line.split()[0]
            rhs = line.split()[1:]
            current_rule = []
            for part in rhs:
                if part == "|":
                    result[lhs].append(current_rule.copy())
                    current_rule = []
                # EPSILON is always at the end of the rhs of the production
                elif part == 'EPSILON':
                    break
                else:
                    current_rule.append(part)
            result[lhs].append(current_rule.copy())

    return result



# save_dict(read_set_from_file(os.path.join("grammar", "First-Sets.txt")), os.path.join("grammar", "first.set"))
# save_dict(read_set_from_file(os.path.join("grammar", "Follow-Sets.txt")), os.path.join("grammar", "follow.set"))
save_dict(read_rules(os.path.join("grammar", "Grammar.txt")), os.path.join("grammar", "rules"))
