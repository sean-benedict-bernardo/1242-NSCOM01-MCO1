"""
Contains miscellaneous functions
"""

import files


def onStart() -> None:
    """Executes on start"""

    print(
        """\n\nTFTPv2 Client Implementation
by Bernardo and Strebel\n\n"""
    )
    files.makeFolder()


def getInput(prompt: str, options: list = []) -> str | int:
    """Gets user input, if options are provided, the user must choose from the options"""
    print(prompt)

    if len(options) != 0:
        for i in range(len(options)):
            print(f"[{i + 1}] {options[i]}")

    print("\n> ", end="")

    try:
        if len(options) != 0:
            while True:
                try:
                    choice = int(input()) - 1
                    if choice < 0 or len(options) <= choice:
                        print("> ", end="")
                    else:
                        print()
                        return choice
                except ValueError:
                    print("> ", end="")
        else:
            userInput = input()
            print()
            return userInput
    except KeyboardInterrupt:
        # If the user presses Ctrl+C, exit the program
        exit()