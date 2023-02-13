def func(n, k):
    #n, k = map(int, input().split())
    st1 = [i for i in range(1, n+1, 2)]
    st2 = [i for i in range(2, n+1, 2)]
    if k == 1:
        print(*(st1 + st2[::-1]))
    elif k == 2:
        print(*(st2 + st1[::-1]))
    elif k == n and n % 2 != 0:
        print(*(st1[::-1] + st2))
    elif k == n and n % 2 == 0:
        print(*(st2[::-1] + st1))
    elif k == n - 1 and n-1 % 2 == 0:
        print(*(st2[::-1] + st1))
    elif k == n - 1 and n-1 % 2 != 0:
        print(*(st1[::-1] + st2))


for n in range(7, 9):
    for k in [1, 2, n-1, n]:
        func(n, k)