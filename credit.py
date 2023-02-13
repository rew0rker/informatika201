type_card = {"AMEX": [34, 37], "MASTERCARD": [51, 52, 53, 54, 55], "VISA": [4]}


def main():
    while True:
        card = input("Number: ")
        if card.isdigit():
            break

    if len(card) in [13, 15, 16]:
        if check_valid(card):
            for key, value in type_card.items():
                if int(card[:2]) in value or int(card[0]) == value[0]:
                    print(key)
        else:
            print("INVALID ALG\n")
    else:
        print("INVALID LEN\n")


def check_valid(numb):
    numb = [int(x) for x in numb]  # преобразуем номер в список с цифрами номера
    print(numb)
    first = list(map(lambda x: str(int(x) * 2), numb[1::2]))  # умножаем каждое 2 число на 2
    print(first)
    first = sum(map(lambda x: int(x), list("".join(first))))  # сложим цифры этого результата
    print(first)
    second = sum(numb[::2])
    res = str(first + second)
    print(res)
    return res[-1] == "0"


if __name__ == "__main__":
    main()
