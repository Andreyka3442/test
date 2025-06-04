s = [1, 2, 3, 4, 5, 6]
polovina = len(s)
if polovina == 0:
    result = [[], []]
elif polovina % 2 == 0:
    v = polovina // 2
    v1 = s[:v]
    v2 = s[v:]
    result = [v1, v2]
else:
    g = polovina // 2 + 1
    g1 = s[:g]
    g2 = s[g:]
    result = [g1, g2]

print(result)
