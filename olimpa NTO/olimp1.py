a = int(input())
h, m = map(int, input().split())

for hour in range(0, 12):
    for minute in range(0, 60):
        hour_degree = hour * 30 + minute * 0.5
        minute_degree = minute * 6

        degree = hour_degree - minute_degree
        if degree < 0:
            degree += 360
        if degree == a:
            h += hour
            m += minute
            if m >= 60:
                h += 1
                m -= 60
            if h >= 12:
                h %= 12

            h_d = h * 30 + m * 0.5
            m_d = m * 6
            answ_degree = h_d - m_d
            if answ_degree < 0:
                answ_degree += 360
            print(answ_degree)