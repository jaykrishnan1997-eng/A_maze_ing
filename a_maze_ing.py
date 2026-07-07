import sys


def config_parse(config: str):
    rconfig = {}
    lines: list[str] = config.split("\n")
    lines = [line for line in lines if not line.startswith("#")]
    mandatory = ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"]
    if (not set(mandatory) <= {line.split("=")[0] for line in lines}):
        raise Exception(
            f"Missing mandatory fields in '{sys.argv[1]}':\n"
            f"{set(mandatory) - {line.split("=")[0] for line in lines}}")
    rconfig['WIDTH'], rconfig['HEIGHT'] = [
        int(v) for v in
        [l.split("=")[1] for l in lines if l.split("=")[0] in mandatory[:2]]]
    rconfig['ENTRY'], rconfig['EXIT'] = [
        (int(x), int(y)) for x, y in
        [l.split("=")[1].split(",")
         for l in lines if l.split("=")[0] in mandatory[2:4]]]
    rconfig['OUTPUT_FILE'] = [
        x for x in
        [l.split("=")[1] for l in lines if l.split("=")[0] == mandatory[4]]]
    rconfig['PERFECT'] = [
        x.capitalize() for x in
        [l.split("=")[1] for l in lines if l.split("=")[0] == mandatory[5]]
        if x.capitalize() == "true".capitalize() or
        x.capitalize == "false".capitalize() or
        x in (0, 1)]
    return (rconfig)


def main():
    if (len(sys.argv) != 2):
        print("Usage: python3 a-maze-ing.py config.txt")
        exit(1)
    config: str
    try:
        with open(sys.argv[1]) as file:
            config = file.read()
            config = config_parse(config)
    except Exception as e:
        print(e)
        exit(1)


if __name__ == "__main__":
    main()
