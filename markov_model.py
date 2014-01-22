import re
import string
import sys
from collections import defaultdict
from random import random
from random import choice as rchoice

def generateMarkovMap(statuses, lookback=2):
    markov_map = defaultdict(lambda:defaultdict(int))
    for status in statuses[:-1]:
        status = re.sub('(['+'!#%&()*+,-./:;<=>?@[\\]^_`{|}~'+'])', r' \1 ', status)
        words = status.split()
        if len(words) > lookback:
            for i in range(len(words)+1):
                markov_map[' '.join(words[max(0,i-lookback):i])][' '.join(words[i:i+1])] += 1

    for word, following in markov_map.items():
        total = float(sum(following.values()))
        for key in following:
            following[key] /= total                             
    return markov_map

 
def letters_only(text):
    for c in string.whitespace+string.punctuation:
        text = text.replace(c,"")
    return text

def letters_and_whitespace(text):
    for c in string.punctuation:
        text = text.replace(c,"")
    return text

def fix_formatting(text):
    """
    >>> fix_formatting('" this is a test " string , you see ? " of course')
    '"this is a test" string, you see? "of course'
    """
    for c in '!#%)*+,-./:;<=>?@\\]^_`|}~':
        text = text.replace(" "+c, c)
    for c in '([{-:/$':
        text = text.replace(c+" ", c)
    
    new_text = ''
    left = True
    use_next = True
    for c in text:
        if not use_next:
            use_next = True
            continue
        if c == '"':
            if left:
                use_next = True
            else:
                if len(new_text) > 0:
                    new_text = new_text[:]
            left = not left
        new_text += c
    return new_text

def generateStatus(markov_map, statuses, lookback=2):
    success = False
    sentence = []
    while not sentence:
        sentence = []
        next_word = sample(markov_map[''].items())
        while next_word != '':
            sentence.append(next_word)
            next_word = sample(markov_map[' '.join(sentence[-lookback:])].items())
        sentence = ' '.join(sentence)
        sentence = fix_formatting(sentence)
        
        for status in statuses: #Prune titles that are substrings of actual titles
            if letters_only(sentence) in letters_only(status):
                sentence = []
                break
    return sentence

def sample(items):
    next_word = None
    t = 0.0
    for k, v in items:
        t += v
        if t and random() < v/t:
            next_word = k
    return next_word

def makeSimilarStatus(status, generator):
    choices = [generator() for i in range(250)]
    status = set(letters_and_whitespace(status).lower().split())
    common = set(['a', 'in', 'the', 'and', 'to', 'do', 'are', 'you', 'so', 'is', 'of'])
    status = status - common
    best_choice = rchoice(choices)
    best = 0
    for choice in choices:
        choice = choice.split('.')[0]
        match = set(letters_and_whitespace(choice.lower()).split()) & status
        if len(match) > best:
            best = len(match)
            best_choice = choice
            print(best_choice, match)
    return best_choice



