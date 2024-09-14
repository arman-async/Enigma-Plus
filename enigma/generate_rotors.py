import argparse
import random


BASE64 = "0123456789+/ABCDEFGHIJKLMNOPQRSTUVWXYZ=abcdefghijklmnopqrstuvwxyz"
def random_rotor(charset:str=BASE64)-> str:
    charset = list(charset)
    random.shuffle(charset)
    return "".join(charset)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-rc", "--rotor-count", type=int,
        help="number of rotors to generate",
        default=28,
    )
    parser.add_argument(
        '-o', '--output', type=str,
        help="output file",
        default="new",
    )

    args = parser.parse_args()
    with open(f'{args.output}.rotors', 'w') as f:
        f.write(f'{BASE64};')
        for _ in range(args.rotor_count):
            rotor = f'{random_rotor()};'
            f.write(rotor)

if __name__ == '__main__':
    main()