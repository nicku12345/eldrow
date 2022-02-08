
import functools
from tqdm import tqdm
from collections import Counter
import re
import ast

def load_wordlist():
    f = open("./wordlist.txt", "r")
    ans = [line.strip() for line in f]
    f.close()
    return ans

def sort_wordlist(WORDLIST):
    ctr = Counter()
    masks = dict()

    for word in WORDLIST:
        masks[word] = list()
        for mask in range(1<<5):
            s = ""
            for i in range(5):
                if mask&(1<<i):
                    s += word[i]
                else:
                    s += "."

            if s.count(".") >= 3:
                continue

            ctr[s] += 1
            masks[word].append(s)

    for char in ctr:
        cnt = char.count(".")
        ctr[char] = ctr[char]**(5 - cnt)

    WORDLIST.sort(key = lambda word : max(ctr[m] for m in masks[word]), reverse = True)

best_guess_sequence = []
mx = 0

def load_checked():
    global mx, best_guess_sequence
    f = open("./checked.txt", "r")
    lines = f.readlines()

    assert(len(lines)%2 == 0)

    ans = set()

    for i in range(0, len(lines), 2):
        word = lines[i].strip()
        seq = ast.literal_eval(lines[i+1].strip()[1:-1])
        if len(seq) > mx:
            mx = len(seq)
            best_guess_sequence = seq
        ans.add(word)

    f.close()
    return ans

def add_checked(word, guess_seq):
    f = open("./checked.txt", "a")
    f.write(word + "\n")
    f.write(guess_seq.__repr__() + "\n")
    f.close()
    
    CHECKED.add(word)
    

WORDLIST = load_wordlist()
sort_wordlist(WORDLIST)
CHECKED = load_checked()

WORDLIST_INDEX = {word:i for i,word in enumerate(WORDLIST)}
POW2 = {(1<<i):i for i in range(len(WORDLIST))}


def GetColor(word, target_word):
    color = ["B"]*5
    present = Counter()
    for i in range(5):
        if word[i] == target_word[i]:
            color[i] = "G"
        else:
            present[target_word[i]] += 1
    
    for i in range(5):
        if color[i] == "B" and present[word[i]]>0:
            present[word[i]] -= 1
            color[i] = "Y"
            
    return color

def GetMask(word, target_word):
    color = GetColor(word, target_word)
    
    pattern = ["."]*5
    yellow = Counter()
    black = set()
    for i in range(5):
        if color[i] == "G":
            pattern[i] = word[i]
        elif color[i] == "Y":
            yellow[word[i]] += 1
        else:
            black.add(word[i])
    
    pattern = re.compile("".join(pattern))
    filtered = [word0 for word0 in WORDLIST if (pattern.match(word0) and word0 != word)]
    
    ans = 0
    for word0 in filtered:
        ok = True
        yellow0 = Counter()
        for i in range(5):
            if color[i] == "G":
                pass
            else:
                yellow0[word0[i]] += 1
                
            if color[i] == "Y":
                if word[i] == word0[i]:
                    ok = False
                    break
        
        for char in yellow:
            if yellow[char] > yellow0[char]:
                ok = False
                break
                
        for char in yellow0:
            if char in black:
                ok = False
                break
        if ok:
            ans |= 1<<WORDLIST_INDEX[word0]            
                
    return ans


def f(TARGET_WORD):
    print(f"Target word: {TARGET_WORD}")
    
    MASKS = []
    
    print("Preparing masks")    
    for word in tqdm(WORDLIST):
        MASKS.append(GetMask(word, TARGET_WORD))
    
    print("ok!")
    
    nxt = dict()

    @functools.lru_cache(None)
    def dp(mask, word):
        # given mask, how far we can go?
        ans = 0

        mask0 = mask    
        while mask0:
            y = mask0&(-mask0)
            mask0 -= y

            idx = POW2[y]

            ans = max(ans, dp(mask & MASKS[idx], WORDLIST[idx]))

        return 1 + ans
    
    @functools.lru_cache(None)
    def dp_save(mask, word):
        nonlocal nxt
        # given mask, how far we can go?
        ans = 0

        mask0 = mask    
        while mask0:
            y = mask0&(-mask0)
            mask0 -= y

            idx = POW2[y]

            case = dp_save(mask & MASKS[idx], WORDLIST[idx])
            if case > ans:
                ans = case
                nxt[mask,word] = (mask & MASKS[idx], WORDLIST[idx])

        return 1 + ans
    
    mx = 0
    best_begin_word = ""
    print("Checking against WORDLIST...")
    for BEGIN_WORD in tqdm(WORDLIST):
        case = dp(GetMask(BEGIN_WORD, TARGET_WORD), BEGIN_WORD)
        if case > mx:
            mx = case
            best_begin_word = BEGIN_WORD
            
        # print(f"Checked {BEGIN_WORD} has length {case}. Current best: {best_begin_word}, length: {mx}")
        
    print("ok!")
    print(f"Printing the longest guess sequence of target word: {TARGET_WORD}")
    dp_save(GetMask(best_begin_word, TARGET_WORD), best_begin_word)
    ans = list()
    
    cur = (GetMask(best_begin_word, TARGET_WORD), best_begin_word)
    while cur in nxt:
        ans.append(cur[1])        
        cur = nxt[cur]
    
    ans.append(cur[1])
    
    print(f"Target word: {TARGET_WORD}. Longest guess sequence: {ans}")
    return ans

for TARGET_WORD in WORDLIST:
    if TARGET_WORD in CHECKED:
        continue
        
    case = f(TARGET_WORD)
    if len(case) > mx:
        mx = len(case)
        best_guess_sequence = case
    
    add_checked(TARGET_WORD, case)
    print(f"Current max length: {mx}, best guess sequence: {best_guess_sequence}")
