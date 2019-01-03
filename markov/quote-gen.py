from collections import deque
from constants import section_break_token,line_start_token
import os
import pickle
import random
import sys

attempts = int(sys.argv[1])
depth = 2
bin_path = os.environ['BIN_PATH']
with open("{0}/quotes.dat".format(bin_path), "rb") as f:
    trie_quotes = pickle.load(f)
with open("{0}/attributions.dat".format(bin_path), "rb") as f:
    trie_attributions = pickle.load(f)

def generate_text(trie, length):
    output = list()
    history = deque(maxlen=depth)

    def add_token(token):
        history.append(token)
        output.append(token)
    
    add_token(line_start_token)
    for i in range(0, length):
        if history[-1] == section_break_token:
            break
        # get our deepest token
        child = trie
        for i in range(0, len(history)):
            child = child[1][history[i]]
        selection = random.randint(0, child[0])
        for token in child[1]:
            leaf = child[1][token]
            if leaf[0] >= selection:
                # this is the selection
                add_token(token)
                break
            else:
                selection -= leaf[0]
    
    return output[1:-1] # remove the start and end tokens

for attempt in range(0, attempts):
    print((" ".join(generate_text(trie_quotes, 500)).replace(line_start_token, "\n")))
    print("-" + (" ".join(generate_text(trie_attributions, 50)).replace(line_start_token, "\n")))
    print()