import sys
from .standalone import Main

if __name__ == "__main__":
    main = Main()
    if len(sys.argv) > 1:
        main.load_file(sys.argv[1])
    main.run()
