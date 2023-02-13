n = int(input())
c_st = n*(n-1)//2

ls_terms = []
for st in range(0, c_st):
    ls_terms.append(input())

ls_monets = "".join(ls_terms)
ls_monets = set(ls_monets)
ls_monets.remove(">")
ls_monets.remove("<")
ls_monets = list(ls_monets)

for _ in range(20):
    for i in ls_terms:
        a = i[0]
        b = i[2]
        ind_a = ls_monets.index(a)
        ind_b = ls_monets.index(b)
        if i[1] == ">":
            if ind_a < ind_b:
                ls_monets[ind_a], ls_monets[ind_b] = ls_monets[ind_b], ls_monets[ind_a]
        if i[1] == "<":
            if ind_a > ind_b:
                ls_monets[ind_a], ls_monets[ind_b] = ls_monets[ind_b], ls_monets[ind_a]

print("".join(ls_monets))
