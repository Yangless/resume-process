def split_overlap(s):
    t=len(s)//3
    print(t)
    return [s[i:i+t+30] for i in range(0,len(s),t)]
print(split_overlap(('abcdefghijklmn12345678fghjkl;dfghjjhgfddfghjktrfklkj')))