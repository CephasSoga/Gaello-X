
b = [[1],  [2],  [3]]
a = b[0]
a.extend(b[i] for i in range(1, len(b)))
print(a)