num = int(input("Введите 5-значное число: "))

if 10000 <= num <= 99999:
    reversed_num = 0

    while num > 0:
        digit = num % 10
        reversed_num = reversed_num * 10 + digit
        num //= 10

    print("Число в обратном порядке:", reversed_num)
else:
    print("Это не 5-значное число!")
