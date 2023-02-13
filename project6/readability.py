import math


def main():
    str_user = input("Text: ")
    count_letters = 0  # счетик букв
    count_words = 1  # счетчик слов
    count_sentences = 0  # счетчик предложений
    for i in range(len(str_user)):
        if str_user[i].isalpha():
            count_letters += 1
        elif str_user[i] == " ":  # по количеству пробелов считаем кол-во слов
            count_words += 1
        elif str_user[i] == "." or str_user[i] == "!" or str_user[i] == "?":
            count_sentences += 1
    let = count_letters // count_words * 100.0  # среднее число букв на 100 слов в тексте
    st = count_sentences // count_words * 100.0  # среднее число предложений на 100 слов в тексте
    x = 0.0588 * let - 0.296 * st - 15.8
    if x >= 16:
        print("Grade 16+")
    elif x < 1:
        print("Before Grade 1")
    else:
        print("Grade ", math.floor(x))


if __name__ == '__main__':
    main()
