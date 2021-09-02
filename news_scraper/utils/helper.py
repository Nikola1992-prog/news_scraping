def user_input():
    while True:
        try:
            choice = int(input(
                'if you want to scrape RTS provider (1), Blic provider (2) or both (3) :'))
            if choice not in [1, 2, 3]:
                raise TypeError
            return choice
        except TypeError:
            print('Your input was inaccurate, use 1 or 2 or 3 for input \n')
        except ValueError:
            print(f"Please use numeric value, not strings and special characters  \n")


def user_method_input():
    while True:
        try:
            methods = input("if you want to print content (1), write ( exel (2), JSON (3) text (4) ) "
                            "!!!!(use , for separations) : ").strip(",").split(',')
            choice = list(map(int, methods))
            choice = set(choice)
            for num in choice:
                if num not in [1, 2, 3, 4]:
                    raise TypeError
            return choice
        except TypeError:
            print('Your input was inaccurate, use 1,2,3,4 for input \n')
        except ValueError:
            print(f"Please use (,) between numbers and numbers, (1,2,3,4)) \n")
