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

def format_raw_grammar(input_file, output_file):
    with open(input_file, "r") as f:
        formatted_lines = []
        lines = f.readlines()
        
        for line in lines:
            # Drop the first part, the number of line
            parts = line.split()[1:]
            
            lhs = parts[0]
            current_rule = [lhs]
            # Excluding ->
            for part in parts[2:]:
                if part == "|":
                    formatted_lines.append(" ".join(current_rule.copy()))
                    current_rule = [lhs]
                elif part == "EPSILON":
                    # Special case for epsilon
                    formatted_lines.append(f"{lhs} ")
                    current_rule = [lhs]
                else:
                    current_rule.append(part)
            if len(current_rule) > 1:
                formatted_lines.append(" ".join(current_rule.copy()))
        with open(output_file, "w") as o:
            o.write("\n".join(formatted_lines))

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
            parts = line.split()
            if parts[1] != "EPSILON":
                result[parts[0]].append(parts[1:].copy())
            else:
                result[parts[0]].append([])

    return result

format_raw_grammar(os.path.join("grammar", "raw_grammar.txt"), os.path.join("grammar", "Grammar.txt"))
# save_dict(read_set_from_file(os.path.join("grammar", "First-Sets.txt")), os.path.join("grammar", "first.set"))
# save_dict(read_set_from_file(os.path.join("grammar", "Follow-Sets.txt")), os.path.join("grammar", "follow.set"))
# save_dict(read_rules(os.path.join("grammar", "Grammar.txt")), os.path.join("grammar", "rules"))