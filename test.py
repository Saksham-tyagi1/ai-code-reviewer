# This is a sample file with multiple intentional issues

import os
import math  # unused import

def calculate_area(radius):
    area = math.pi * radius ** 2  # math used
    unused_var = 42  # unused variable
    return area

def calculate_area(radius):  # duplicate function
    return 3.14 * radius * radius

def check_value(val):
    if val:  # redundant if
        return True
    else:
        return False

def loop_check(numbers):
    for i in range(len(numbers)):
        print(numbers[i])

def unreachable_example():
    print("This is reachable")
    return
    print("This is NOT reachable")  # unreachable code

x = 10  # unused
y = 20  # unused
