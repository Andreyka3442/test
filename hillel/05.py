s = [22, 0, 0, 0, 9, 0, 99, 11, 0, 22, 0, 45, 55, 0]

ss = []

for x in s:
    if x != 0:
        ss.append(x)

zero = [0] * (len(s) - len(ss))
result = ss + zero
print(result)
