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

def save_set(dictionary, filepath):
    with open(filepath, 'w') as f:
        f.write(json.dumps(dictionary))

def load_set(filepath):
    with open(filepath, 'r') as f:
        return json.loads(f.read())

# save_set(read_set_from_file(os.path.join("grammar", "First-Sets.txt")), os.path.join("grammar", "first.set"))
# save_set(read_set_from_file(os.path.join("grammar", "Follow-Sets.txt")), os.path.join("grammar", "follow.set"))