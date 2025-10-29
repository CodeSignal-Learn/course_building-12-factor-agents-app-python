def sum_numbers(a: float, b: float) -> float:
    return a + b


def multiply_numbers(a: float, b: float) -> float:
    return a * b


def subtract_numbers(a: float, b: float) -> float:
    return a - b


def divide_numbers(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("Division by zero")
    return a / b


def power(base: float, exponent: float) -> float:
    return base ** exponent


def square_root(x: float) -> float:
    if x < 0:
        raise ValueError("Square root of negative number")
    return x ** 0.5


