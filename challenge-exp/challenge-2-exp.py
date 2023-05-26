import json
import spacy
import nltk
from nltk.tokenize import word_tokenize

import spacy
from spacy.tokens import Doc

class WhitespaceTokenizer:
    def __init__(self, vocab):
        self.vocab = vocab

    def __call__(self, text):
        words = text.split(" ")
        spaces = [True] * len(words)
        for i, word in enumerate(words):
            if word == "":
                words[i] = " "
                spaces[i] = False
        if words[-1] == " ":
            words = words[0:-1]
            spaces = spaces[0:-1]
        else:
           spaces[-1] = False

        return Doc(self.vocab, words=words, spaces=spaces)

nlp = spacy.load("en_core_web_sm")
nlp.tokenizer = WhitespaceTokenizer(nlp.vocab)


def automate_head(text):
    text = text.replace("-","")
    doc = nlp(text)
    remove = ""
    entities = []
    for item in doc.ents:
        if item.label_ not in ('DATE', 'TIME', 'ORDINAL', 'CARDINAL'):
            entities.append(str(item))
    seen_noun = False
    for token in doc:
        if ((token.pos_ == 'VERB' and seen_noun == True)):# or str(token) in ['who','which','that']):
            remove = str(token)
            break
        if token.pos_ == 'NOUN':
            seen_noun = True
    if remove != "":
        text = text[:text.index(remove)]
    doc = nlp(text)
    head = ""
    for token in doc:
        anc_list = [an for an in token.ancestors]
        if anc_list == []:
            head = str(token)
    for item in entities:
        if head in item:
            if word_tokenize(item)[0].lower() == "the":
                head = item[4:]
            else:
                head = item
    return head

def extract_entity_heads(fname):
    arr = []
    with open(fname, "r") as f2r:
        for each_line in f2r:
            dat = json.loads(each_line)
            arr.append(dat)
    consider = []
    for doc in arr:
        events = doc["events"]
        sentence_starts = doc["_sentence_start"]
        for i in range(0,len(events)):
            if events[i] == []:
                continue
            else:
                for e in events[i]:
                    for arg in e[1:]:
                        start_index = sentence_starts[i]
                        end_index = None
                        if i < len(events)-1:
                            end_index = sentence_starts[i+1]
                        if arg[3] not in consider:
                            consider.append(arg[3].replace('\n',' '))
    return consider
def main(fname):
    print("Starting...")
    consider = extract_entity_heads(fname)
    both = []
    for item in consider: 
        ind = item.index('....')
        both.append((item[:ind],item[ind+4:]))
    diff_mult = 0
    total_ace_mult = 0
    diff_nonmult = 0
    total = 0
    for tup in both:
        head = tup[0]
        extent = tup[1]
        aut_head = automate_head(extent).replace("-","")
        ace_head = head.replace("-","")
        if "and" in extent:
            continue
        if " " in ace_head:
            total_ace_mult = total_ace_mult + 1
        if aut_head != ace_head:
            if " " in head:
                diff_mult = diff_mult + 1
                print(aut_head,"      ",ace_head)
            else:
                diff_nonmult = diff_nonmult + 1
        total = total + 1
    total_ace_nonmult = total- total_ace_mult
    print("Proportion of discrepancies when ACE considers a head as multiple words:",diff_mult/total_ace_mult)
    print("Proportion of discrepancies when ACE considers a head as a single word:",diff_nonmult/total_ace_nonmult)






import argparse
parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("output_name", help="Name for output directory.")
args = parser.parse_args()
fname = f"./construct-preprocess-data/data/ace-event/processed-data/{args.output_name}/json/data.json"
main(fname)
