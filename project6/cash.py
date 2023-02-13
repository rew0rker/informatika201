def main():
    while True:
        change_get = float(input("Change owned: "))
        if change_get >= 0.0:
            break
    change = int(change_get * 100)
    counter = 0
    while change > 0:
        if change >= 25:
            counter +=1
            change %= 25
        elif change >= 10:
            counter += change // 10  # fdff
            change %= 10
        elif change >= 5:
            counter += change // 5
            change %= 5
        elif change >= 1:
            counter += change / 1
            change %= 1
    print(int(counter))


if __name__ == "__main__":
    main()
