
num = int(input('Введите первое число: '))
action = input('Введите действие(+,-,/,*) ')
num2 = int(input('Введите второе число: '))


if num2 == 0:
    print('Ошибка: делить на 0 нельзя!!!')
elif action == '+':
    print('Результат:', num + num2)
elif action == '-':
    print('Результат:', num - num2)
elif action == '/':
    print('Результат:', num / num2)
elif action == '*':
    print('Результат:', num * num2)


