s = [22, 10, 0, 10, 9, 10, 99, 11, 10, 22, 10, 45, 55, 10]

ss = []

for x in s:
    if x != 10:
        ss.append(x)

ten = [10] * (len(s) - len(ss))
result = ss + ten
print(result)