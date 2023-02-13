import random

# здесь запрашиваем строку и через метод split и разделитель ", " из строки получаем список, каждый элемент которого
# это имя и фамилия 1 чувака
ls_of_classmates = input("Введите имена и фамили всех участников в формате: Фамилия1 Имя1, Фамилия2 Имя2\n").split(", ")
size_class = len(ls_of_classmates)

ls_of_pairs = []

for i in range(size_class // 2):

    rand_ind_1 = random.randrange(len(ls_of_classmates))
    student1 = ls_of_classmates[rand_ind_1]
    del ls_of_classmates[rand_ind_1]

    rand_ind_2 = random.randrange(len(ls_of_classmates))
    student2 = ls_of_classmates[rand_ind_2]
    del ls_of_classmates[rand_ind_2]

    pair = f"{student1} + {student2}"
    ls_of_pairs.append(pair)

print("\nПолучились вот такие пары:")
print(*ls_of_pairs, sep="\n")

