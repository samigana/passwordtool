# passwordtool
secure password generation in python 
# Password Tool

A small, dependency-light Python tool with two features:

1. **Generate** a secure, randomized password based on your preferences
   (length, uppercase, lowercase, digits, special characters).
2. **Rate** any password you type in, based on length and character
   diversity, with a colored strength bar and concrete feedback.

Everything lives in a single file, `password_tool.py`, organized into
clearly labeled sections so it's easy to scan and modify.




## Requirements

- Python 3.9+
- Optional: `colorama` (for colored output). Without it, the tool still
  works — it just prints without color.

```bash
pip install colorama
```

---

## Usage

### Interactive mode (recommended for first use)

Just run the script with no arguments and follow the menu:

```bash

```

### Command-line mode (for scripting)

Generate a password:

```bash
python3 password_tool.py generate --length 20
```

Options for `generate`:

| Flag                  | Meaning                                   |
|------------------------|--------------------------------------------|
| `-l, --length N`       | Password length (default: 16)              |
| `--no-lower`           | Exclude lowercase letters                  |
| `--no-upper`           | Exclude uppercase letters                  |
| `--no-digits`          | Exclude digits                             |
| `--no-special`         | Exclude special characters                 |
| `--exclude-ambiguous`  | Exclude look-alike chars (`l`, `1`, `I`, `O`, `0`) |

Rate a password:

```bash
python3 password_tool.py rate "MyP@ssw0rd123"
```

---

## Example output

**Generating a password:**

```
Generated password:
  4$+cq_!65/qKPQ+N#oCK

  Length : 20
  Sets   : lower upper digits special
  Strength: [██████████████████████████████] 100%  (Very Strong)
  Estimated entropy: ~129.2 bits
```

**Rating a weak password:**

```
Password strength report
  Strength : [███████████░░░░░░░░░░░░░░░░░░░] 36%  (Weak)
  Length   : 11 characters
  Entropy  : ~56.9 bits (brute-force search space)
  Feedback :
    - Consider a longer password (12+ characters) for extra safety.
    - Add uppercase letters.
    - Add special characters (e.g. !@#$%^&*...).
    - Avoid common words like 'password' or 'qwerty'.
```

The colored bar (green/yellow/red/cyan depending on score) makes it easy
to judge password strength at a glance rather than reading raw numbers.

---

## How the strength score is calculated

The score (0–100) combines three signals, then subtracts penalties:

- **Length (0–40 pts):** scales up to 20 characters, then caps out.
- **Diversity (0–40 pts):** 10 points for each of the 4 character
  categories present (lowercase, uppercase, digits, special).
- **Entropy (0–20 pts):** an estimate of brute-force search space,
  `length × log2(pool_size)`, capped at 80 bits for full marks.
- **Penalties:** repeated characters (`aaaa`), simple sequences
  (`abcd`, `1234`), and common weak words (`password`, `qwerty`, etc.)
  each subtract points.

This gives a score that rewards both length *and* variety, and flags
obvious bad habits — not a substitute for a professional password
auditor, but a solid, explainable heuristic.

---

## Code structure (for the owner / maintainer)

The file is split into numbered sections with docstrings, so you can
jump straight to what you need:

1. **Character sets** — the raw character pools used everywhere else.
2. **Password generation** — `GeneratorOptions`, `build_character_pool`,
   `generate_password`.
3. **Strength rating** — `StrengthResult`, `estimate_entropy_bits`,
   `rate_password`.
4. **Visual output** — colored strength bar rendering
   (`render_strength_bar`) and print helpers.
5. **Interactive CLI menu** — the guided, question-by-question flow.
6. **Command-line (argparse) mode** — for scripting / automation.

Every public function has type hints and a docstring explaining *why*,
not just *what*, so the reasoning (e.g. "why `secrets` and not
`random`") stays visible in the code itself.

### Extending it

- Add a new character category: extend the constants in **Section 1**
  and thread a new `use_x` flag through `GeneratorOptions` and
  `build_character_pool`.
- Change scoring weights: everything lives in `rate_password()` in
  **Section 3** — the point values are plain constants, easy to tune.
- Swap the visual style: `render_strength_bar()` in **Section 4** is
  the only place that draws the bar; change the characters or width
  there without touching any logic.

---

## License

Free to use and modify for personal or academic projects.
