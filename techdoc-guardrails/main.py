from validators import validate_pii, validate_language


def main():
    print("Let's validate user input! If PII/Toxic Language is entered exception will be thrown ..")
    user_input = input("Please enter a info you need to validate: ")
    validate_language(user_input)


if __name__ == "__main__":
    main()
