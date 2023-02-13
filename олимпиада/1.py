data = {
    'пара': [1, 4],
    'мало': [5, 9],
    'группа': [10, 19],
    'толпа': [20, 49],
    'орда': [50, 99],
    'сотня': [100, 249],
    'туча': [250, 499],
    'тьма': [500, 999],
    'легион': [1000, 10000]
}
bots = {
    "Storm": "группа",
    "SpyEye": "толпа",
    "Sality": "туча",
    "Carberp": "тьма",
    "Meriposa": "группа",
    "Zeus": "толпа",
    "Bredolab": "группа",
    "ZeroAccess": "группа",
    "Carna": "мало",
    "TDL": "туча"
}
protection = {
    "DDoS Prevention": "тьма",
    "DDoS Guard": "туча",
    "StormWall ": "толпа",
    "invGUARD": "группа",
    "Anti-DDOS": "орда",
    "Incapsula": "сотня",
    "Sucuri": "группа"
}

bots_value = [0, 0]
for value in bots.values():
    value = data[value]
    bots_value[0] += value[0]
    bots_value[1] += value[1]

protection_value = [0, 0]
for value in protection.values():
    value = data[value]
    protection_value[0] += value[0]
    protection_value[1] += value[1]


print(bots_value)
print(protection_value)