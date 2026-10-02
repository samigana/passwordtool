

from __future__ import annotations

import argparse
import math
import secrets
import string
import sys
from dataclasses import dataclass, field

try:
    from colorama import Fore, Style
    from colorama import init as colorama_init
    colorama_init(autoreset=True)
    COLOR = True
except ImportError:
    COLOR = False

    class _NoColor:
        def __getattr__(self, _name):
            return ""

    Fore = _NoColor()
    Style = _NoColor()



AMBIGUOUS_CHARS = "il1LoO0"

LOWER = string.ascii_lowercase
UPPER = string.ascii_uppercase
DIGITS = string.digits
SPECIAL = "!@#$%^&*()-_=+[]{};:,.<>?/"


@dataclass
class GeneratorOptions:
    length: int = 16
    use_lower: bool = True
    use_upper: bool = True
    use_digits: bool = True
    use_special: bool = True
    exclude_ambiguous: bool = False


def build_character_pool(opts: GeneratorOptions) -> tuple[str, list[str]]:
    
    required_pools: list[str] = []

    if opts.use_lower:
        required_pools.append(LOWER)
    if opts.use_upper:
        required_pools.append(UPPER)
    if opts.use_digits:
        required_pools.append(DIGITS)
    if opts.use_special:
        required_pools.append(SPECIAL)

    if not required_pools:
        raise ValueError("At least one character set must be enabled.")

    if opts.exclude_ambiguous:
        required_pools = [
            "".join(c for c in pool if c not in AMBIGUOUS_CHARS)
            for pool in required_pools
        ]

    full_pool = "".join(required_pools)
    return full_pool, required_pools


def generate_password(opts: GeneratorOptions) -> str:
 
    full_pool, required_pools = build_character_pool(opts)

    if opts.length < len(required_pools):
        raise ValueError(
            f"Length must be at least {len(required_pools)} to fit "
            f"one character from each of the {len(required_pools)} "
            f"selected character sets."
        )

    password_chars = [secrets.choice(pool) for pool in required_pools]

    remaining = opts.length - len(password_chars)
    password_chars += [secrets.choice(full_pool) for _ in range(remaining)]

    secrets.SystemRandom().shuffle(password_chars)

    return "".join(password_chars)


@dataclass
class StrengthResult:
    score: int                     # 0-100
    label: str                     
    entropy_bits: float
    feedback: list[str] = field(default_factory=list)


def _character_pool_size(password: str) -> int:
    """Estimate the size of the character pool the password draws from."""
    pool = 0
    if any(c.islower() for c in password):
        pool += len(LOWER)
    if any(c.isupper() for c in password):
        pool += len(UPPER)
    if any(c.isdigit() for c in password):
        pool += len(DIGITS)
    if any(c in SPECIAL for c in password):
        pool += len(SPECIAL)
    others = set(password) - set(LOWER + UPPER + DIGITS + SPECIAL)
    if others:
        pool += len(others)
    return max(pool, 1)


def estimate_entropy_bits(password: str) -> float:
   
    pool_size = _character_pool_size(password)
    if not password:
        return 0.0
    return len(password) * math.log2(pool_size)


def rate_password(password: str) -> StrengthResult:
 
    feedback: list[str] = []

    if not password:
        return StrengthResult(0, "Empty", 0.0, ["Password is empty."])

    length = len(password)
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in SPECIAL for c in password)
    diversity = sum([has_lower, has_upper, has_digit, has_special])

    length_score = min(40, (length / 20) * 40)
    if length < 8:
        feedback.append("Too short: use at least 8 characters (12+ recommended).")
    elif length < 12:
        feedback.append("Consider a longer password (12+ characters) for extra safety.")

    diversity_score = diversity * 10
    if not has_lower:
        feedback.append("Add lowercase letters.")
    if not has_upper:
        feedback.append("Add uppercase letters.")
    if not has_digit:
        feedback.append("Add numbers.")
    if not has_special:
        feedback.append(f"Add special characters (e.g. {SPECIAL[:8]}...).")

    entropy_bits = estimate_entropy_bits(password)
    entropy_score = min(20, (entropy_bits / 80) * 20)

    penalty = 0
    lowered = password.lower()

    if any(password[i] == password[i + 1] == password[i + 2]
           for i in range(len(password) - 2)):
        penalty += 10
        feedback.append("Avoid repeating the same character 3+ times in a row.")

    sequences = ["abcdefghijklmnopqrstuvwxyz", "0123456789"]
    for seq in sequences:
        for i in range(len(seq) - 3):
            chunk = seq[i:i + 4]
            if chunk in lowered or chunk[::-1] in lowered:
                penalty += 10
                feedback.append("Avoid simple sequences like 'abcd' or '1234'.")
                break

    common_weak = {"password", "qwerty", "letmein", "admin", "welcome", "azerty"}
    if any(weak in lowered for weak in common_weak):
        penalty += 20
        feedback.append("Avoid common words like 'password' or 'qwerty'.")

    raw_score = length_score + diversity_score + entropy_score - penalty
    score = int(max(0, min(100, round(raw_score))))

    if score >= 90:
        label = "Very Strong"
    elif score >= 70:
        label = "Strong"
    elif score >= 50:
        label = "Moderate"
    elif score >= 25:
        label = "Weak"
    else:
        label = "Very Weak"

    if not feedback:
        feedback.append("Looks good! No obvious weaknesses detected.")

    return StrengthResult(score, label, entropy_bits, feedback)


def _color_for_score(score: int) -> str:
    if score >= 90:
        return Fore.CYAN
    if score >= 70:
        return Fore.GREEN
    if score >= 50:
        return Fore.YELLOW
    if score >= 25:
        return Fore.RED
    return Fore.RED + Style.BRIGHT


def render_strength_bar(score: int, width: int = 30) -> str:
    filled = round((score / 100) * width)
    empty = width - filled
    color = _color_for_score(score)
    bar = f"{color}{'█' * filled}{Style.RESET_ALL}{'░' * empty}"
    return f"[{bar}] {score}%"


def print_generated_password(password: str, opts: GeneratorOptions) -> None:
    result = rate_password(password)
    print()
    print(f"{Fore.CYAN}{Style.BRIGHT}Generated password:{Style.RESET_ALL}")
    print(f"  {Fore.CYAN}{Style.BRIGHT}{password}{Style.RESET_ALL}")
    print()
    print(f"  Length : {opts.length}")
    print(f"  Sets   : "
          f"{'lower ' if opts.use_lower else ''}"
          f"{'upper ' if opts.use_upper else ''}"
          f"{'digits ' if opts.use_digits else ''}"
          f"{'special' if opts.use_special else ''}")
    print(f"  Strength: {render_strength_bar(result.score)}  ({result.label})")
    print(f"  Estimated entropy: ~{result.entropy_bits:.1f} bits")
    print()


def print_rating(password: str) -> None:
    result = rate_password(password)
    print()
    print(f"{Fore.CYAN}{Style.BRIGHT}Password strength report{Style.RESET_ALL}")
    print(f"  Strength : {render_strength_bar(result.score)}  ({result.label})")
    print(f"  Length   : {len(password)} characters")
    print(f"  Entropy  : ~{result.entropy_bits:.1f} bits (brute-force search space)")
    print("  Feedback :")
    for line in result.feedback:
        print(f"    {Fore.YELLOW}-{Style.RESET_ALL} {line}")
    print()


def ask_yes_no(prompt: str, default: bool = True) -> bool:
    suffix = " [Y/n] " if default else " [y/N] "
    answer = input(prompt + suffix).strip().lower()
    if not answer:
        return default
    return answer.startswith("y")


def ask_int(prompt: str, default: int, minimum: int = 1) -> int:
    raw = input(f"{prompt} [{default}] ").strip()
    if not raw:
        return default
    try:
        value = int(raw)
        return value if value >= minimum else default
    except ValueError:
        print(f"{Fore.RED}Not a number, using default ({default}).{Style.RESET_ALL}")
        return default


def menu_generate() -> None:
    print(f"\n{Fore.CYAN}{Style.BRIGHT}== Generate a password =={Style.RESET_ALL}")
    length = ask_int("Password length?", 16, minimum=1)
    use_lower = ask_yes_no("Include lowercase letters?", True)
    use_upper = ask_yes_no("Include uppercase letters?", True)
    use_digits = ask_yes_no("Include numbers?", True)
    use_special = ask_yes_no("Include special characters?", True)
    exclude_ambiguous = ask_yes_no("Exclude ambiguous characters (l,1,I,O,0)?", False)

    opts = GeneratorOptions(
        length=length,
        use_lower=use_lower,
        use_upper=use_upper,
        use_digits=use_digits,
        use_special=use_special,
        exclude_ambiguous=exclude_ambiguous,
    )
    try:
        password = generate_password(opts)
    except ValueError as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
        return
    print_generated_password(password, opts)


def menu_rate() -> None:
    print(f"\n{Fore.CYAN}{Style.BRIGHT}== Rate a password =={Style.RESET_ALL}")
    password = input("Enter a password to rate: ")
    print_rating(password)


def interactive_menu() -> None:
    banner = f"""
{Fore.CYAN}{Style.BRIGHT}╔══════════════════════════════════════╗
║        PASSWORD TOOL - main menu      ║
╚══════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)
    while True:
        print("1) Generate a secure password")
        print("2) Rate a password I enter")
        print("3) Quit")
        choice = input("> ").strip()
        if choice == "1":
            menu_generate()
        elif choice == "2":
            menu_rate()
        elif choice == "3":
            print("Bye!")
            break
        else:
            print(f"{Fore.RED}Invalid choice, try again.{Style.RESET_ALL}")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a secure password or rate one you already have."
    )
    sub = parser.add_subparsers(dest="command")

    gen = sub.add_parser("generate", help="Generate a secure password.")
    gen.add_argument("-l", "--length", type=int, default=16)
    gen.add_argument("--no-lower", action="store_true")
    gen.add_argument("--no-upper", action="store_true")
    gen.add_argument("--no-digits", action="store_true")
    gen.add_argument("--no-special", action="store_true")
    gen.add_argument("--exclude-ambiguous", action="store_true")

    rate = sub.add_parser("rate", help="Rate a password's strength.")
    rate.add_argument("password", type=str)

    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    if args.command == "generate":
        opts = GeneratorOptions(
            length=args.length,
            use_lower=not args.no_lower,
            use_upper=not args.no_upper,
            use_digits=not args.no_digits,
            use_special=not args.no_special,
            exclude_ambiguous=args.exclude_ambiguous,
        )
        try:
            password = generate_password(opts)
        except ValueError as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}", file=sys.stderr)
            sys.exit(1)
        print_generated_password(password, opts)

    elif args.command == "rate":
        print_rating(args.password)

    else:
        interactive_menu()


if __name__ == "__main__":
    main()
