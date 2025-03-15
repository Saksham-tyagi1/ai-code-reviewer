import os  # Unused import

def large_function():
    total = 0
    for i in range(100000):  # Inefficient loop
        total += i
    
    if total > 500000000:
        print("Very large number detected!")  # Unnecessary print statement

    return total
