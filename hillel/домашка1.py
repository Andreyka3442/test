import random

numbers = [random.randint(1, 59) for _ in range(random.randint(3,10))]
print(numbers)
new_list = [numbers[0], numbers[-2], numbers[-1]]
print(new_list)
