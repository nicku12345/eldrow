from collections import Counter

f = open("./wordlist.txt")
WORDLIST = [line.strip() for line in f.readlines()]
f.close()

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

WORDLIST.sort(key = lambda word : max(ctr[m] for m in masks[word]), reverse=True)

print(WORDLIST)
