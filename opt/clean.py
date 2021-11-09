import os

exts = ('out', 'in', 'sub', 'xyz')

for folder in os.listdir():
    if not os.path.isdir(folder):
        continue
    if folder[0] == ".":
        continue
    
    for doc in os.listdir(folder):
        ext = doc.split('.')[-1]
        if ext not in exts:
            path = os.path.join(folder, doc)
            os.remove(path) 
