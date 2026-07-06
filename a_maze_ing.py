import sys


def config_parse(config: str):
    lines: list[str] = config.split("\n")
    # ignoring comment-lines
    lines = [line for line in lines if not line.startswith("#")]
    mandatory = {"WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"}
    if (not mandatory <= {line.split("=")[0] for line in lines}):
        raise Exception(
            f"Missing mandatory fields in {sys.argv[1]}:\n"
            f"{mandatory - {line.split("=")[0] for line in lines}}")


def main():
    if (len(sys.argv) != 2):
        print("Usage: python3 a-maze-ing.py config.txt")
        exit(1)
    config: str
    try:
        with open(sys.argv[1]) as file:
            config = file.read()
            config_parse(config)
    except Exception as e:
        print(e)
        exit(1)


if __name__ == "__main__":
    main()
