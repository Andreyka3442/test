num = int(input("Введи четырёхзначное число: "))

if 1000 <= num <= 9999:
    number1 = num // 1000
    number2 = (num // 100) % 10
    number3 = (num // 10) % 10
    number4 = num % 10

    print(number1)
    print(number2)
    print(number3)
    print(number4)
else:
    print("Ошибка: нужно ввести именно четырёхзначное число.")