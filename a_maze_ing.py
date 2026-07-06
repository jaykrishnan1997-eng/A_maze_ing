import sys


def main():
    if (len(sys.argv) != 2):
        print("Usage: python3 a-maze-ing.py config.txt")
        exit(1)
    try:
        with open(sys.argv[1]) as file:
            pass
    except FileNotFoundError as e:
        print(e)
        exit(1)


if __name__ == "__main__":
    main()
