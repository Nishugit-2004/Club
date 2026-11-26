"""
game/puzzles.py — All 10 rounds, 30 questions with per-team randomisation.

Each round is a dict:
  {
    "number": int,
    "name": str,
    "description": str,
    "fragment": str,
    "questions": [Question, ...],   # 3 questions
  }

Each question (also a dict):
  {
    "index": int,            # 0-based within round
    "text": str,             # question displayed to participant
    "difficulty": "EASY"|"MEDIUM"|"HARD"|"VERY HARD",
    "hint": str,
    "points": int,
    "validate": callable,    # fn(answer: str) -> bool  — SERVER SIDE ONLY
    "answer_display": str,   # shown ONLY after solving (or on organizer dashboard)
  }

The `seed` parameter (derived from team_code) is used to randomise puzzle
variables while keeping answers deterministic per team.
"""
from __future__ import annotations

import hashlib
import random
import string
from typing import Callable


def _seeded_rng(seed: int, salt: str) -> random.Random:
    combined = hashlib.sha256(f"{seed}:{salt}".encode()).digest()
    return random.Random(int.from_bytes(combined[:8], "big"))


def _normalise(answer: str) -> str:
    return (
        answer.strip()
        .lower()
        .replace(" ", "")
        .replace("-", "")
        .replace("_", "")
        .replace("°", "")
        .replace("deg", "")
        .replace("degrees", "")
    )


# ═══════════════════════════════════════════════════════════════════════════
# ROUND 1 — CIPHER BREAKER
# ═══════════════════════════════════════════════════════════════════════════

def _build_round_1(seed: int) -> dict:
    rng = _seeded_rng(seed, "r1")

    # Q1 — Caesar cipher
    shift = rng.randint(3, 10)
    plaintext_words = ["BINARY", "SYNTAX", "KERNEL", "VECTOR", "MATRIX",
                       "CIPHER", "PYTHON", "LAMBDA", "SIGNAL", "BUFFER"]
    word = rng.choice(plaintext_words)

    def _caesar_encrypt(text: str, s: int) -> str:
        return "".join(
            chr((ord(c) - ord("A") + s) % 26 + ord("A")) if c.isalpha() else c
            for c in text.upper()
        )

    ciphertext = _caesar_encrypt(word, shift)

    def q1_validate(ans: str) -> bool:
        return _normalise(ans) == word.lower()

    # Q2 — Reverse alphabet (ROT-25 variant = atbash)
    secret_word_options = ["DECODE", "HIDDEN", "SECRET", "UNLOCK", "ENCODE"]
    secret_word = rng.choice(secret_word_options)

    def _atbash(text: str) -> str:
        return "".join(chr(ord("Z") - (ord(c) - ord("A"))) if c.isalpha() else c for c in text.upper())

    atbash_cipher = _atbash(secret_word)

    def q2_validate(ans: str) -> bool:
        return _normalise(ans) == secret_word.lower()

    # Q3 — Double encryption: first Caesar (shift), then atbash
    base_word_options = ["ALGORITHM", "RECURSION", "COMPILER", "VARIABLE", "FUNCTION"]
    base_word = rng.choice(base_word_options)
    double_shift = rng.randint(2, 7)
    step1 = _caesar_encrypt(base_word, double_shift)
    step2 = _atbash(step1)

    def q3_validate(ans: str) -> bool:
        return _normalise(ans) == base_word.lower()

    return {
        "number": 1,
        "name": "CIPHER BREAKER",
        "description": "Three layers of cryptographic obfuscation stand between you and the first fragment. Break each cipher to advance.",
        "fragment": f"FR-{_seeded_rng(seed,'frag1').randint(1000,9999)}",
        "icon": "🔐",
        "questions": [
            {
                "index": 0,
                "text": f"**[EASY]** The following message was encrypted using a Caesar cipher with a shift of **{shift}**.\n\n`{ciphertext}`\n\nDecrypt it and enter the original word.",
                "difficulty": "EASY",
                "hint": f"Shift each letter **backward** by {shift} positions in the alphabet. A→Z when going below A.",
                "points": 10,
                "validate": q1_validate,
                "answer_display": word,
            },
            {
                "index": 1,
                "text": f"**[MEDIUM]** This message was encoded using a **reverse alphabet** (Atbash) cipher — A becomes Z, B becomes Y, and so on.\n\n`{atbash_cipher}`\n\nDecrypt it.",
                "difficulty": "MEDIUM",
                "hint": "Map each letter to its mirror: position 1 (A) ↔ position 26 (Z), position 2 (B) ↔ position 25 (Y), etc.",
                "points": 10,
                "validate": q2_validate,
                "answer_display": secret_word,
            },
            {
                "index": 2,
                "text": f"**[HARD]** A message was **double-encrypted**: first with a Caesar cipher (shift = **{double_shift}**), then with an Atbash cipher, producing:\n\n`{step2}`\n\nReverse both operations to find the original plaintext word.",
                "difficulty": "HARD",
                "hint": f"Reverse the Atbash first, then reverse the Caesar shift of {double_shift}.",
                "points": 10,
                "validate": q3_validate,
                "answer_display": base_word,
            },
        ],
    }


# ═══════════════════════════════════════════════════════════════════════════
# ROUND 2 — THE FIVE HOUSES
# ═══════════════════════════════════════════════════════════════════════════

def _build_round_2(seed: int) -> dict:
    rng = _seeded_rng(seed, "r2")

    colors = ["Red", "Blue", "Green", "Yellow", "White"]
    animals = ["Cat", "Dog", "Lion", "Bird", "Fish"]
    rng.shuffle(colors)
    rng.shuffle(animals)

    # Fixed logic puzzle — positions 1-5 (1-indexed)
    # House assignments
    house_colors = dict(zip(range(1, 6), colors))
    house_animals = dict(zip(range(1, 6), animals))

    lion_house = [h for h, a in house_animals.items() if a == "Lion"][0]
    lion_color = house_colors[lion_house]

    bird_house = [h for h, a in house_animals.items() if a == "Bird"][0]
    bird_color = house_colors[bird_house]

    # Clues we give:
    clue_color_1 = house_colors[1]
    clue_color_3 = house_colors[3]
    clue_animal_2 = house_animals[2]

    def q1_validate(ans: str) -> bool:
        return _normalise(ans) == str(lion_house)

    def q2_validate(ans: str) -> bool:
        return _normalise(ans) == lion_color.lower()

    def q3_validate(ans: str) -> bool:
        return _normalise(ans) == bird_color.lower()

    clue_text = f"""Five houses stand in a row, numbered 1 to 5 from left to right.

**Known facts:**
- House 1 is painted **{clue_color_1}**.
- House 3 is painted **{clue_color_3}**.
- The resident of House 2 owns a **{clue_animal_2}**.
- The remaining colors are assigned in this exact order: {', '.join(colors)}.
- The remaining animals are assigned in this exact order: {', '.join(animals)}.
*(Use the sequences above to map each house to its color and animal.)*"""

    return {
        "number": 2,
        "name": "THE FIVE HOUSES",
        "description": "A classic logic grid puzzle. Deduce the arrangement of houses, colors, and animals from the given clues.",
        "fragment": f"FR-{_seeded_rng(seed,'frag2').randint(1000,9999)}",
        "icon": "🏠",
        "questions": [
            {
                "index": 0,
                "text": clue_text + "\n\n**[EASY]** Which house number contains the **Lion**? (Enter a number 1–5)",
                "difficulty": "EASY",
                "hint": f"Map the colors sequence {colors} to houses 1-5. Map the animals sequence {animals} the same way.",
                "points": 10,
                "validate": q1_validate,
                "answer_display": str(lion_house),
            },
            {
                "index": 1,
                "text": clue_text + "\n\n**[MEDIUM]** What color is the house that contains the **Lion**?",
                "difficulty": "MEDIUM",
                "hint": f"Once you find the Lion's house number, look up its color from the mapping.",
                "points": 10,
                "validate": q2_validate,
                "answer_display": lion_color,
            },
            {
                "index": 2,
                "text": clue_text + "\n\n**[HARD]** The Bird is jealous of the Lion. What color is the **Bird's** house?",
                "difficulty": "HARD",
                "hint": "Find the Bird in the animals sequence and map it to its house number, then to its color.",
                "points": 10,
                "validate": q3_validate,
                "answer_display": bird_color,
            },
        ],
    }


# ═══════════════════════════════════════════════════════════════════════════
# ROUND 3 — THE SOUND OF SECRETS
# ═══════════════════════════════════════════════════════════════════════════

def _build_round_3(seed: int) -> dict:
    rng = _seeded_rng(seed, "r3")

    # Musical note → number mapping (A=1, B=2, … G=7, then repeat)
    note_map = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7}
    notes = list(note_map.keys())

    # Q1: Note sequence sums to a secret number
    seq_len = 5
    seq = [rng.choice(notes) for _ in range(seq_len)]
    seq_sum = sum(note_map[n] for n in seq)

    def q1_validate(ans: str) -> bool:
        try:
            return int(_normalise(ans)) == seq_sum
        except ValueError:
            return False

    # Q2: Rhythm pattern — count beats (1=quarter, 2=half, 4=whole)
    beat_symbols = {"♩": 1, "♪": 1, "𝅗𝅥": 2, "𝅝": 4}
    display_beats = ["QUARTER(1)", "QUARTER(1)", "HALF(2)", "WHOLE(4)",
                     "QUARTER(1)", "HALF(2)", "QUARTER(1)"]
    beat_values = [1, 1, 2, 4, 1, 2, 1]
    num_beats = rng.randint(3, 5)
    chosen = rng.choices(range(len(display_beats)), k=num_beats)
    beat_seq = [display_beats[i] for i in chosen]
    beat_total = sum(beat_values[i] for i in chosen)

    def q2_validate(ans: str) -> bool:
        try:
            return int(_normalise(ans)) == beat_total
        except ValueError:
            return False

    # Q3: Note code → ASCII decode
    secret_num = rng.randint(10, 99)
    digits = [int(d) for d in str(secret_num)]
    # Map digits to notes: 1→A, 2→B, … 7→G, 0→rest
    digit_note_map = {1: "A", 2: "B", 3: "C", 4: "D", 5: "E", 6: "F", 7: "G", 0: "REST"}
    code_notes = [digit_note_map.get(d, "REST") for d in digits]

    def q3_validate(ans: str) -> bool:
        try:
            return int(_normalise(ans)) == secret_num
        except ValueError:
            return _normalise(ans) == str(secret_num)

    return {
        "number": 3,
        "name": "THE SOUND OF SECRETS",
        "description": "Musical notes carry hidden numerical values. Decode the rhythm and harmony to unlock the third fragment.",
        "fragment": f"FR-{_seeded_rng(seed,'frag3').randint(1000,9999)}",
        "icon": "🎵",
        "questions": [
            {
                "index": 0,
                "text": f"**[EASY]** Each musical note maps to a number: A=1, B=2, C=3, D=4, E=5, F=6, G=7.\n\nNote sequence: **{' - '.join(seq)}**\n\nWhat is the **sum** of these notes?",
                "difficulty": "EASY",
                "hint": f"Add up: {' + '.join(str(note_map[n]) for n in seq)} = ?",
                "points": 10,
                "validate": q1_validate,
                "answer_display": str(seq_sum),
            },
            {
                "index": 1,
                "text": f"**[MEDIUM]** A rhythm pattern is given below. Each note type has a beat value:\n- QUARTER(1) = 1 beat\n- HALF(2) = 2 beats\n- WHOLE(4) = 4 beats\n\nPattern: **{' | '.join(beat_seq)}**\n\nWhat is the **total number of beats** in this pattern?",
                "difficulty": "MEDIUM",
                "hint": f"Sum each note's beat value: {' + '.join(str(beat_values[i]) for i in chosen)} = ?",
                "points": 10,
                "validate": q2_validate,
                "answer_display": str(beat_total),
            },
            {
                "index": 2,
                "text": f"**[HARD]** A secret message was encoded as musical notes using this key:\n1→A, 2→B, 3→C, 4→D, 5→E, 6→F, 7→G, 0→REST\n\nEncoded message: **{' - '.join(code_notes)}**\n\nRead the digits back from the notes and enter the **2-digit number**.",
                "difficulty": "HARD",
                "hint": "Reverse the mapping: A→1, B→2, C→3, D→4, E→5, F→6, G→7. Concatenate the digits.",
                "points": 10,
                "validate": q3_validate,
                "answer_display": str(secret_num),
            },
        ],
    }


# ═══════════════════════════════════════════════════════════════════════════
# ROUND 4 — VIBE CODING
# ═══════════════════════════════════════════════════════════════════════════

def _build_round_4(seed: int) -> dict:
    rng = _seeded_rng(seed, "r4")

    # Q1: What does this function return?
    n = rng.randint(3, 8)
    # Fibonacci
    def fib(x):
        a, b = 0, 1
        for _ in range(x):
            a, b = b, a + b
        return a

    fib_result = fib(n)

    def q1_validate(ans: str) -> bool:
        try:
            return int(_normalise(ans)) == fib_result
        except ValueError:
            return False

    # Q2: Complete the pattern
    # Pattern: n, n+2, n+4, n+6 ... next two
    start = rng.randint(2, 15)
    step = rng.randint(2, 5)
    series = [start + i * step for i in range(5)]
    next_val = series[-1] + step

    def q2_validate(ans: str) -> bool:
        try:
            return int(_normalise(ans)) == next_val
        except ValueError:
            return False

    # Q3: Password validation
    rng2 = _seeded_rng(seed, "r4q3")
    min_len = rng2.randint(6, 9)
    min_digits = rng2.randint(1, 3)
    # Generate a valid password
    base = "PyT" + "".join(str(rng2.randint(0, 9)) for _ in range(min_digits + 1)) + "!"
    # Extend to min_len
    while len(base) < min_len:
        base += rng2.choice(string.ascii_lowercase)
    test_password = base

    def q3_validate(ans: str) -> bool:
        a = ans.strip()
        has_upper = any(c.isupper() for c in a)
        has_digit = sum(1 for c in a if c.isdigit()) >= min_digits
        has_special = any(c in "!@#$%^&*" for c in a)
        long_enough = len(a) >= min_len
        return has_upper and has_digit and has_special and long_enough

    return {
        "number": 4,
        "name": "VIBE CODING",
        "description": "Code speaks. Patterns emerge. Can you trace the logic, complete the sequence, and forge a password that passes?",
        "fragment": f"FR-{_seeded_rng(seed,'frag4').randint(1000,9999)}",
        "icon": "💻",
        "questions": [
            {
                "index": 0,
                "text": f"**[EASY]** What does this Python function return when called with `n = {n}`?\n\n```python\ndef mystery(n):\n    a, b = 0, 1\n    for _ in range(n):\n        a, b = b, a + b\n    return a\n```",
                "difficulty": "EASY",
                "hint": "This is the Fibonacci sequence. mystery(0)=0, mystery(1)=1, mystery(2)=1, mystery(3)=2, ...",
                "points": 10,
                "validate": q1_validate,
                "answer_display": str(fib_result),
            },
            {
                "index": 1,
                "text": f"**[MEDIUM]** Complete the pattern. What is the **next number** in this sequence?\n\n`{', '.join(map(str, series))}, ?`",
                "difficulty": "MEDIUM",
                "hint": f"Each number increases by a constant value. What is {series[1]} - {series[0]}?",
                "points": 10,
                "validate": q2_validate,
                "answer_display": str(next_val),
            },
            {
                "index": 2,
                "text": f"**[HARD]** A password validation function requires:\n- Minimum length: **{min_len}** characters\n- At least **{min_digits}** digit(s)\n- At least **1** uppercase letter\n- At least **1** special character from: `! @ # $ % ^ & *`\n\nEnter **any** valid password that satisfies all these rules.",
                "difficulty": "HARD",
                "hint": f"Example structure: Mix uppercase + lowercase + {min_digits} digit(s) + a special char (!@#$). Keep it at least {min_len} chars.",
                "points": 10,
                "validate": q3_validate,
                "answer_display": test_password + " (any valid password)",
            },
        ],
    }


# ═══════════════════════════════════════════════════════════════════════════
# ROUND 5 — TRIANGLE OF LOGIC
# ═══════════════════════════════════════════════════════════════════════════

def _build_round_5(seed: int) -> dict:
    rng = _seeded_rng(seed, "r5")

    # Q1: Find the missing angle
    angle_a = rng.randint(30, 70)
    angle_b = rng.randint(20, 60)
    while angle_a + angle_b >= 170:
        angle_b -= 5
    angle_c = 180 - angle_a - angle_b

    def q1_validate(ans: str) -> bool:
        try:
            return abs(float(_normalise(ans)) - angle_c) < 0.5
        except ValueError:
            return False

    # Q2: Area of a right triangle
    base = rng.randint(4, 15)
    height = rng.randint(4, 15)
    area = (base * height) // 2  # integer result by design
    # Adjust to ensure integer
    if base * height % 2 != 0:
        height += 1
    area = (base * height) // 2

    def q2_validate(ans: str) -> bool:
        try:
            return abs(float(_normalise(ans)) - area) < 0.5
        except ValueError:
            return False

    # Q3: Triangle inequality + determine if valid
    sides_set = rng.choice([
        (3, 4, 5, True),   # valid right triangle
        (1, 2, 10, False), # invalid
        (5, 12, 13, True), # valid
        (2, 3, 6, False),  # invalid
        (6, 8, 10, True),  # valid
        (7, 24, 25, True), # valid
        (1, 1, 3, False),  # invalid
    ])
    s1, s2, s3, is_valid = sides_set
    answer_str = "yes" if is_valid else "no"

    def q3_validate(ans: str) -> bool:
        return _normalise(ans) in (["yes", "valid", "true", "1"] if is_valid else ["no", "invalid", "false", "0"])

    return {
        "number": 5,
        "name": "TRIANGLE OF LOGIC",
        "description": "Triangles hold mathematical truths. Find the missing angles, compute the area, and determine validity.",
        "fragment": f"FR-{_seeded_rng(seed,'frag5').randint(1000,9999)}",
        "icon": "📐",
        "questions": [
            {
                "index": 0,
                "text": f"**[EASY]** A triangle has two known angles: **{angle_a}°** and **{angle_b}°**.\n\nWhat is the third angle (in degrees)?",
                "difficulty": "EASY",
                "hint": "The sum of all angles in a triangle is always 180°.",
                "points": 10,
                "validate": q1_validate,
                "answer_display": f"{angle_c}°",
            },
            {
                "index": 1,
                "text": f"**[MEDIUM]** A right triangle has a base of **{base}** units and a height of **{height}** units.\n\nCalculate its **area** (in square units).",
                "difficulty": "MEDIUM",
                "hint": "Area of a triangle = (base × height) / 2",
                "points": 10,
                "validate": q2_validate,
                "answer_display": str(area),
            },
            {
                "index": 2,
                "text": f"**[HARD]** Three segments have lengths: **{s1}**, **{s2}**, and **{s3}**.\n\nCan these form a valid triangle? (Answer: **yes** or **no**)",
                "difficulty": "HARD",
                "hint": f"Triangle inequality: each side must be less than the sum of the other two. Check: {s1}+{s2}>{s3}? {s1}+{s3}>{s2}? {s2}+{s3}>{s1}?",
                "points": 10,
                "validate": q3_validate,
                "answer_display": answer_str.upper(),
            },
        ],
    }


# ═══════════════════════════════════════════════════════════════════════════
# ROUND 6 — THE BUG HUNTER
# ═══════════════════════════════════════════════════════════════════════════

def _build_round_6(seed: int) -> dict:
    rng = _seeded_rng(seed, "r6")

    # Q1: Predict output
    a = rng.randint(1, 9)
    b = rng.randint(1, 9)
    # Simple expression: a * b + b
    result1 = a * b + b

    def q1_validate(ans: str) -> bool:
        try:
            return int(_normalise(ans)) == result1
        except ValueError:
            return False

    # Q2: Find the bug
    bug_options = [
        {
            "code": "def factorial(n):\n    result = 1\n    for i in range(1, n):   # Bug here\n        result *= i\n    return result",
            "bug_line": "range(1, n)",
            "fix": "range(1, n+1)",
            "explain": "The range should be `range(1, n+1)` — it currently misses multiplying by n itself.",
        },
        {
            "code": "def is_even(n):\n    return n % 2 == 1   # Bug here",
            "bug_line": "n % 2 == 1",
            "fix": "n % 2 == 0",
            "explain": "Even numbers have remainder 0 when divided by 2, not 1.",
        },
        {
            "code": "def reverse_string(s):\n    return s[::1]   # Bug here",
            "bug_line": "s[::1]",
            "fix": "s[::-1]",
            "explain": "s[::1] returns the string unchanged. s[::-1] reverses it.",
        },
    ]
    bug = rng.choice(bug_options)

    def q2_validate(ans: str) -> bool:
        a_norm = _normalise(ans)
        if not a_norm:
            return False
        fix_norm = _normalise(bug["fix"])
        line_norm = _normalise(bug["bug_line"])
        return (
            fix_norm in a_norm or
            (len(a_norm) >= 3 and a_norm in fix_norm) or
            line_norm in a_norm or
            (len(a_norm) >= 3 and a_norm in line_norm) or
            "off" in a_norm or
            _normalise(bug["explain"]) in a_norm
        )

    # Q3: Infinite loop detection
    loop_options = [
        {
            "code": "i = 0\nwhile i < 5:\n    print(i)\n    # i += 1 is missing",
            "is_infinite": True,
            "reason": "i is never incremented, so the condition i < 5 is always True."
        },
        {
            "code": "i = 10\nwhile i > 0:\n    print(i)\n    i -= 1",
            "is_infinite": False,
            "reason": "i decreases by 1 each iteration and eventually reaches 0."
        },
        {
            "code": "x = 1\nwhile x != 100:\n    x += 3",
            "is_infinite": True,
            "reason": "x starts at 1 and increments by 3, so it goes 1, 4, 7... and skips 100."
        },
    ]
    loop_q = rng.choice(loop_options)
    loop_ans = "yes" if loop_q["is_infinite"] else "no"

    def q3_validate(ans: str) -> bool:
        a = _normalise(ans)
        if loop_q["is_infinite"]:
            return a in ("yes", "true", "infinite", "1", "y")
        else:
            return a in ("no", "false", "finite", "0", "n")

    return {
        "number": 6,
        "name": "THE BUG HUNTER",
        "description": "Every program hides a flaw. Find the bugs, predict the outputs, and detect the infinite loops.",
        "fragment": f"FR-{_seeded_rng(seed,'frag6').randint(1000,9999)}",
        "icon": "🐛",
        "questions": [
            {
                "index": 0,
                "text": f"**[EASY]** What does this Python code **print**?\n\n```python\na = {a}\nb = {b}\nprint(a * b + b)\n```",
                "difficulty": "EASY",
                "hint": f"Evaluate: {a} × {b} + {b} = ?",
                "points": 10,
                "validate": q1_validate,
                "answer_display": str(result1),
            },
            {
                "index": 1,
                "text": f"**[MEDIUM]** The following Python function contains a **bug**. Identify what the bug is.\n\n```python\n{bug['code']}\n```\n\nDescribe the bug (or write the corrected line).",
                "difficulty": "MEDIUM",
                "hint": bug["explain"],
                "points": 10,
                "validate": q2_validate,
                "canonical_answer": bug["fix"],
                "answer_display": f"{bug['fix']} (Bug was: `{bug['bug_line']}`)",
            },
            {
                "index": 2,
                "text": f"**[HARD]** Does this code produce an **infinite loop**? Answer **yes** or **no**.\n\n```python\n{loop_q['code']}\n```",
                "difficulty": "HARD",
                "hint": loop_q["reason"],
                "points": 10,
                "validate": q3_validate,
                "answer_display": loop_ans.upper() + f" — {loop_q['reason']}",
            },
        ],
    }


# ═══════════════════════════════════════════════════════════════════════════
# ROUND 7 — THE NETWORK MAZE
# ═══════════════════════════════════════════════════════════════════════════

def _build_round_7(seed: int) -> dict:
    rng = _seeded_rng(seed, "r7")

    # Q1: Shortest path (simple graph — Dijkstra by inspection)
    # Fixed small graph, randomised weights
    w_ab = rng.randint(2, 6)
    w_ac = rng.randint(3, 8)
    w_bc = rng.randint(1, 5)
    w_bd = rng.randint(2, 7)
    w_cd = rng.randint(1, 4)

    # Paths from A to D:
    path_abd = w_ab + w_bd
    path_abcd = w_ab + w_bc + w_cd
    path_acd = w_ac + w_cd

    min_path = min(path_abd, path_abcd, path_acd)

    path_names = {
        path_abd: "A→B→D",
        path_abcd: "A→B→C→D",
        path_acd: "A→C→D",
    }

    def q1_validate(ans: str) -> bool:
        try:
            return int(_normalise(ans)) == min_path
        except ValueError:
            return False

    # Q2: Connected components
    n_nodes = rng.randint(5, 7)
    # Create a graph with 2 components deliberately
    comp1 = [1, 2, 3]
    comp2 = list(range(4, n_nodes + 1))
    n_components = 2

    edges_display = [(1, 2), (2, 3)]
    if len(comp2) > 1:
        edges_display.append((comp2[0], comp2[1]))

    def q2_validate(ans: str) -> bool:
        try:
            return int(_normalise(ans)) == n_components
        except ValueError:
            return False

    # Q3: Hamiltonian path exists in a cycle graph?
    # Always true for a cycle graph with n >= 3
    cycle_n = rng.randint(4, 7)
    has_ham = True  # cycle graph always has Hamiltonian path
    ham_ans = "yes"

    def q3_validate(ans: str) -> bool:
        return _normalise(ans) in ("yes", "true", "y", "1")

    edge_desc = f"A↔B (weight {w_ab}), A↔C (weight {w_ac}), B↔C (weight {w_bc}), B↔D (weight {w_bd}), C↔D (weight {w_cd})"
    edge_comp_desc = ", ".join(f"{a}↔{b}" for a, b in edges_display)
    comp2_str = "↔".join(str(c) for c in comp2)

    return {
        "number": 7,
        "name": "THE NETWORK MAZE",
        "description": "Graph theory is the backbone of networks. Navigate paths, count components, and find Hamiltonian routes.",
        "fragment": f"FR-{_seeded_rng(seed,'frag7').randint(1000,9999)}",
        "icon": "🕸️",
        "questions": [
            {
                "index": 0,
                "text": f"**[EASY]** A weighted graph has nodes A, B, C, D with edges:\n{edge_desc}\n\nFind the **cost of the shortest path** from **A to D**.",
                "difficulty": "EASY",
                "hint": f"Calculate all paths: A→B→D = {path_abd}, A→C→D = {path_acd}, A→B→C→D = {path_abcd}. Pick the minimum.",
                "points": 10,
                "validate": q1_validate,
                "answer_display": f"{min_path} ({path_names[min_path]})",
            },
            {
                "index": 1,
                "text": f"**[MEDIUM]** A graph has {n_nodes} nodes (1 to {n_nodes}) and edges: {edge_comp_desc}.\nNodes in group 1: {comp1}. Nodes in group 2: {comp2}. There are no edges between the groups.\n\nHow many **connected components** does this graph have?",
                "difficulty": "MEDIUM",
                "hint": "A connected component is a maximal set of nodes where every node can reach every other. Count the isolated groups.",
                "points": 10,
                "validate": q2_validate,
                "answer_display": str(n_components),
            },
            {
                "index": 2,
                "text": f"**[HARD]** A **cycle graph** C_{cycle_n} has {cycle_n} nodes arranged in a ring, each connected to its two neighbours.\n\nDoes a **Hamiltonian path** exist in this graph? (A Hamiltonian path visits every node exactly once.) Answer **yes** or **no**.",
                "difficulty": "HARD",
                "hint": f"A cycle graph C_n (n ≥ 3) always contains a Hamiltonian path — just traverse {cycle_n - 1} of the {cycle_n} edges without repeating a node.",
                "points": 10,
                "validate": q3_validate,
                "answer_display": "YES — cycle graphs always have a Hamiltonian path.",
            },
        ],
    }


# ═══════════════════════════════════════════════════════════════════════════
# ROUND 8 — THE MEMORY PALACE
# ═══════════════════════════════════════════════════════════════════════════

def _build_round_8(seed: int) -> dict:
    rng = _seeded_rng(seed, "r8")

    # Q1: Remember and answer a number sequence
    seq_len = 6
    seq = [rng.randint(1, 9) for _ in range(seq_len)]
    target_pos = rng.randint(1, seq_len)  # 1-indexed
    target_val = seq[target_pos - 1]

    def q1_validate(ans: str) -> bool:
        try:
            return int(_normalise(ans)) == target_val
        except ValueError:
            return False

    # Q2: Grid pattern — sum of a row
    grid = [[rng.randint(1, 9) for _ in range(3)] for _ in range(3)]
    row_idx = rng.randint(0, 2)  # 0-indexed
    row_sum = sum(grid[row_idx])

    grid_display = "\n".join(f"| {' | '.join(str(v) for v in row)} |" for row in grid)

    def q2_validate(ans: str) -> bool:
        try:
            return int(_normalise(ans)) == row_sum
        except ValueError:
            return False

    # Q3: Symbol pattern — what comes next
    symbols = ["★", "●", "▲", "◆", "✦"]
    pat_len = 4
    pattern = [rng.choice(symbols) for _ in range(pat_len)]
    next_sym = pattern[0]  # Repeating cycle pattern

    def q3_validate(ans: str) -> bool:
        a = ans.strip()
        # Accept the symbol name as well
        sym_names = {
            "★": ["star", "★"],
            "●": ["circle", "dot", "●"],
            "▲": ["triangle", "▲"],
            "◆": ["diamond", "◆"],
            "✦": ["sparkle", "star4", "✦"],
        }
        for key, names in sym_names.items():
            if key == next_sym and (a == key or any(n in a.lower() for n in names)):
                return True
        return False

    return {
        "number": 8,
        "name": "THE MEMORY PALACE",
        "description": "Your mind is the ultimate storage device. Memorise sequences, grids, and patterns to retrieve the hidden fragment.",
        "fragment": f"FR-{_seeded_rng(seed,'frag8').randint(1000,9999)}",
        "icon": "🧠",
        "questions": [
            {
                "index": 0,
                "text": f"**[EASY]** Memorise this number sequence:\n\n`{' — '.join(str(x) for x in seq)}`\n\nWhat is the number at **position {target_pos}** (counting from 1)?",
                "difficulty": "EASY",
                "hint": f"Count carefully from the left. Position 1 = {seq[0]}, Position 2 = {seq[1]}, ...",
                "points": 10,
                "validate": q1_validate,
                "answer_display": str(target_val),
            },
            {
                "index": 1,
                "text": f"**[MEDIUM]** Study this 3×3 grid:\n\n{grid_display}\n\nWhat is the **sum of row {row_idx + 1}** (counting from the top)?",
                "difficulty": "MEDIUM",
                "hint": f"Row {row_idx + 1} contains: {grid[row_idx]}. Add them together.",
                "points": 10,
                "validate": q2_validate,
                "answer_display": str(row_sum),
            },
            {
                "index": 2,
                "text": f"**[HARD]** This symbol sequence repeats on a cycle:\n\n`{' → '.join(pattern)} → ?`\n\nWhat symbol comes **next** in the pattern? (The pattern repeats from the beginning.)\n\nAvailable symbols: ★ ● ▲ ◆ ✦",
                "difficulty": "HARD",
                "hint": f"The pattern has {pat_len} symbols and then repeats. The 5th symbol is the same as the 1st.",
                "points": 10,
                "validate": q3_validate,
                "answer_display": next_sym,
            },
        ],
    }


# ═══════════════════════════════════════════════════════════════════════════
# ROUND 9 — THE FINAL PROTOCOL
# ═══════════════════════════════════════════════════════════════════════════

def _build_round_9(seed: int) -> dict:
    rng = _seeded_rng(seed, "r9")

    # Q1: Binary to decimal
    num = rng.randint(10, 127)
    binary_str = bin(num)[2:]  # strip '0b'

    def q1_validate(ans: str) -> bool:
        try:
            return int(_normalise(ans)) == num
        except ValueError:
            return False

    # Q2: Logic gate
    # AND, OR, XOR, NAND, NOR
    gate = rng.choice(["AND", "OR", "XOR", "NAND", "NOR"])
    inp_a = rng.randint(0, 1)
    inp_b = rng.randint(0, 1)

    gate_ops = {
        "AND": inp_a & inp_b,
        "OR": inp_a | inp_b,
        "XOR": inp_a ^ inp_b,
        "NAND": int(not (inp_a & inp_b)),
        "NOR": int(not (inp_a | inp_b)),
    }
    gate_result = gate_ops[gate]

    def q2_validate(ans: str) -> bool:
        a = _normalise(ans)
        return a in (str(gate_result), "true" if gate_result else "false",
                     "yes" if gate_result else "no",
                     "one" if gate_result else "zero")

    # Q3: Multi-step protocol key
    # Steps: take seed digit, XOR with constant, convert to hex
    base_num = rng.randint(10, 50)
    xor_const = rng.randint(5, 15)
    step1 = base_num
    step2 = step1 ^ xor_const
    step3 = hex(step2)[2:].upper()

    def q3_validate(ans: str) -> bool:
        a = _normalise(ans).upper().lstrip("0X")
        return a == step3.lstrip("0") or a == step3

    return {
        "number": 9,
        "name": "THE FINAL PROTOCOL",
        "description": "The machine speaks in binary. Logic gates guard the penultimate fragment. Execute the protocol to advance.",
        "fragment": f"FR-{_seeded_rng(seed,'frag9').randint(1000,9999)}",
        "icon": "⚡",
        "questions": [
            {
                "index": 0,
                "text": f"**[EASY]** Convert this binary number to **decimal**:\n\n`{binary_str}`",
                "difficulty": "EASY",
                "hint": f"Each bit from right: {', '.join(f'{b}×2^{i}' for i, b in enumerate(reversed(binary_str)))}. Sum the powers of 2 where the bit is 1.",
                "points": 10,
                "validate": q1_validate,
                "answer_display": str(num),
            },
            {
                "index": 1,
                "text": f"**[MEDIUM]** A logic gate receives inputs **A = {inp_a}** and **B = {inp_b}**.\n\nUsing a **{gate}** gate, what is the output? (Answer: 0 or 1)",
                "difficulty": "MEDIUM",
                "hint": f"{gate} truth: AND=both must be 1, OR=at least one is 1, XOR=exactly one is 1, NAND=NOT AND, NOR=NOT OR.",
                "points": 10,
                "validate": q2_validate,
                "answer_display": str(gate_result),
            },
            {
                "index": 2,
                "text": f"**[VERY HARD]** Execute the following 3-step protocol:\n\n**Step 1:** Start with the number `{base_num}`\n**Step 2:** XOR it with `{xor_const}` (use bitwise XOR)\n**Step 3:** Convert the result to **hexadecimal** (without the `0x` prefix, uppercase)\n\nEnter the final hex value.",
                "difficulty": "VERY HARD",
                "hint": f"Step 1: {base_num} → Step 2: {base_num} XOR {xor_const} = {step2} → Step 3: hex({step2}) = ?",
                "points": 10,
                "validate": q3_validate,
                "answer_display": step3,
            },
        ],
    }


# ═══════════════════════════════════════════════════════════════════════════
# ROUND 10 — THE TREASURE VAULT
# ═══════════════════════════════════════════════════════════════════════════

def _build_round_10(seed: int) -> dict:
    rng = _seeded_rng(seed, "r10")

    # Q1: Combined cipher from R1 — use the seed to create a unique word
    r1_shift = _seeded_rng(seed, "r1").randint(3, 10)
    final_words = ["TREASURE", "VICTORY", "ACHIEVED", "CHAMPION", "UNLOCKED"]
    final_word = rng.choice(final_words)

    def _caesar_encrypt(text, s):
        return "".join(chr((ord(c) - ord("A") + s) % 26 + ord("A")) if c.isalpha() else c for c in text.upper())

    encrypted_final = _caesar_encrypt(final_word, r1_shift)

    def q1_validate(ans: str) -> bool:
        return _normalise(ans) == final_word.lower()

    # Q2: Synthesis — combine fragments from R3 and R9
    r3_sum = sum({"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7}[n] for n in
                 [_seeded_rng(seed, "r3").choice(list("ABCDEFG")) for _ in range(5)])
    r9_base = _seeded_rng(seed, "r9").randint(10, 50)
    r9_xor = _seeded_rng(seed, "r9").randint(5, 15)
    combined = r3_sum + (r9_base ^ r9_xor)

    def q2_validate(ans: str) -> bool:
        try:
            return int(_normalise(ans)) == combined
        except ValueError:
            return False

    # Q3: Final treasure key — anagram of a hidden word
    hidden_words = ["ALGORITHM", "DISCOVERY", "KNOWLEDGE", "INVENTION", "EXCELLENCE"]
    hidden = rng.choice(hidden_words)
    anagram = list(hidden)
    rng.shuffle(anagram)
    # Ensure the anagram is different from the original
    while "".join(anagram) == hidden:
        rng.shuffle(anagram)
    anagram_str = "".join(anagram)

    def q3_validate(ans: str) -> bool:
        return _normalise(ans) == hidden.lower()

    return {
        "number": 10,
        "name": "THE TREASURE VAULT",
        "description": "The final chamber. Combine your knowledge from all previous rounds to unlock the Lost Algorithm's greatest secret.",
        "fragment": f"FR-{_seeded_rng(seed,'frag10').randint(1000,9999)}",
        "icon": "🏆",
        "questions": [
            {
                "index": 0,
                "text": f"**[MEDIUM]** Using the same cipher from Round 1 (Caesar shift = **{r1_shift}**), decrypt this final message:\n\n`{encrypted_final}`\n\nThis word represents your achievement.",
                "difficulty": "MEDIUM",
                "hint": f"Shift each letter backward by {r1_shift}. You solved this type of cipher in Round 1!",
                "points": 10,
                "validate": q1_validate,
                "answer_display": final_word,
            },
            {
                "index": 1,
                "text": f"**[HARD]** The vault requires a **synthesis code** combining the note sum from Round 3 and the XOR result from Round 9.\n\n`synthesis = note_sum_R3 + xor_result_R9`\n\nNote sum (R3) = **{r3_sum}** | XOR result (R9) = **{r9_base ^ r9_xor}**\n\nEnter the synthesis code.",
                "difficulty": "HARD",
                "hint": f"Simply add: {r3_sum} + {r9_base ^ r9_xor} = ?",
                "points": 10,
                "validate": q2_validate,
                "answer_display": str(combined),
            },
            {
                "index": 2,
                "text": f"**[VERY HARD]** The vault's final lock is a word scrambled beyond recognition:\n\n`{anagram_str}`\n\nUnscramble this anagram to reveal the **hidden word** (a 9-letter computer science concept).",
                "difficulty": "VERY HARD",
                "hint": f"The word has {len(hidden)} letters and is a fundamental CS concept. The letters are: {', '.join(sorted(hidden))}",
                "points": 10,
                "validate": q3_validate,
                "answer_display": hidden,
            },
        ],
    }


# ═══════════════════════════════════════════════════════════════════════════
# PUBLIC API
# ═══════════════════════════════════════════════════════════════════════════

_ROUND_BUILDERS = [
    _build_round_1,
    _build_round_2,
    _build_round_3,
    _build_round_4,
    _build_round_5,
    _build_round_6,
    _build_round_7,
    _build_round_8,
    _build_round_9,
    _build_round_10,
]


def get_round(round_number: int, seed: int) -> dict:
    """Get a single round (1-indexed) with puzzles generated for the given seed."""
    if not 1 <= round_number <= 10:
        raise ValueError(f"round_number must be 1-10, got {round_number}")
    return _ROUND_BUILDERS[round_number - 1](seed)


def get_all_rounds(seed: int) -> list[dict]:
    """Get all 10 rounds for the given seed."""
    return [builder(seed) for builder in _ROUND_BUILDERS]


def generate_treasure_code(team_code: str, seed: int) -> str:
    """Generate the final treasure code for a team."""
    h = hashlib.sha256(f"TREASURE:{team_code}:{seed}".encode()).hexdigest()[:8].upper()
    return f"TLA-VAULT-{h}"


def validate_answer(round_number: int, question_index: int, answer: str, seed: int) -> bool:
    """Server-side answer validation."""
    try:
        round_data = get_round(round_number, seed)
        question = round_data["questions"][question_index]
        return question["validate"](answer)
    except Exception:
        return False

