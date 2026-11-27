"""Bangladeshi number formatting (lakh/crore grouping) and Bangla numerals."""
from .money import D, q2

BN_DIGITS = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")
TAKA = "৳"


def group_indian(int_part: str) -> str:
    if len(int_part) <= 3:
        return int_part
    head, tail = int_part[:-3], int_part[-3:]
    parts = []
    while len(head) > 2:
        parts.insert(0, head[-2:])
        head = head[:-2]
    if head:
        parts.insert(0, head)
    return ",".join(parts + [tail])


def format_amount(value, bangla: bool = False, symbol: bool = False) -> str:
    v = q2(D(value))
    sign = "-" if v < 0 else ""
    whole, frac = f"{abs(v):.2f}".split(".")
    text = f"{sign}{group_indian(whole)}.{frac}"
    if symbol:
        text = f"{TAKA}{text}"
    return text.translate(BN_DIGITS) if bangla else text
