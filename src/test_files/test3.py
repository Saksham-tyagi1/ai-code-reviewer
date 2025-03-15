def compute_square(n):
    return n * n  # Could use exponentiation

def compute_cube(n):
    return n * n * n  # Could use exponentiation

def repeat_task():
    for i in range(10):
        print(f"Processing {i}")  # Repeated print in a loop

def main():
    print(compute_square(5))
    print(compute_cube(3))
    repeat_task()
