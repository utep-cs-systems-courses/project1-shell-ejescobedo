import os

while True:
        if 'PS1' in os.environ:
            os.write(1, (os.environ['PS1']).encode())
        else:
            os.write(1, ('$ ').encode())
            try:
                userInput = input()
            except EOFError:
                sys.exit(1)

        if userInput == "": # Empty input, will prompt again
            continue
        if 'exit' in userInput: # Terminates shell
            break
