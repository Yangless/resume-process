import pandas as pd
with open('position.txt','r',encoding='utf-8') as f:
    a=[i.replace('\n','') for i in f.readlines()]
print(set(a))