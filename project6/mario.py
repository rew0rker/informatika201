while True:
    try:
        n = int(input())
        if 0 <= n <= 23:
            break
    except:
        pass

for i in range(1, n + 1):
    print(" " * (n - i) + "#" * i + " " + "#" * i)
