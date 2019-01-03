from collections import deque
from constants import section_break_token,line_start_token
import os
import pickle
from pymongo import MongoClient

def add_to_trie(trie, tokens, depth):
    history = deque(maxlen=depth)
    for leaf_token in tokens:
        trie[0] += 1
        history.append(leaf_token)
        for i in range(0, len(history)):
            child=trie
            for j in range(i, len(history)-1):
                child = child[1][history[j]]
            if leaf_token not in child[1]:
                child[1][leaf_token] = [0,{}]
            child[1][leaf_token][0] += 1

def tokenize_line(line):
    # strip the text bare and split on whitespace
    split_tokens = line.split()

    # filter out empty tokens and make sure punctuation is separated
    tokens = []
    for split_token in split_tokens:
        if len(split_token) == 0:
            continue
        elif len(split_token) == 1:
            # prevent mulitple consecutive line breaks, or we'll end up with too many infinite newline spirals
            #if (split_token == line_start_token) and (tokens[-1] == line_start_token):
                #continue
            tokens.append(split_token)
        else:
            final_char = split_token[-1]
            if final_char in [',','.','?','!',';',':','…']:
                tokens.append(split_token[:-1])
                tokens.append(final_char)
            else:
                tokens.append(split_token)

    return tokens

def tokenize_text(text):
    tokens = [line_start_token]
    lines = text.lower().replace('”','').replace('“','').replace('‘','').replace('’','').split("\n")
    for line in lines:
        line_tokens = tokenize_line(line)
        if len(line_tokens) > 0:
            tokens.extend(line_tokens)
            tokens.append(line_start_token)
    # terminate all snippets with a section break
    if len(tokens) > 0:
        tokens[-1] = section_break_token
    return tokens

bin_path = os.environ['BIN_PATH']
client = MongoClient(os.environ['MONGO_CONNECTION_URI'])
db = client.pgte

print("Compiling")
trie_depth = 5
trie_quotes = [0, {}]
trie_attributions = [0, {}]
for chapter in db.chapters.find():
    print("Adding quote from {0}: {1}".format(chapter['book'], chapter['title']))
    quote_tokens = tokenize_text(chapter['quote'])
    add_to_trie(trie_quotes, quote_tokens, trie_depth)

    attribution_tokens = tokenize_text(chapter['attribution'][1:]) # prune initial '-'
    add_to_trie(trie_attributions, attribution_tokens, trie_depth)

print("Saving compiled quotes")
with open("{0}/quotes.dat".format(bin_path), "wb") as f:
    pickle.dump(trie_quotes, f)

print("Saving compiled attributions")
with open("{0}/attributions.dat".format(bin_path), "wb") as f:
    pickle.dump(trie_attributions, f)