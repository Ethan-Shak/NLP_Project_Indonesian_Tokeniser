"""Rule-based tokenizer for Indonesian. Rules live in rules/*.txt and rules/patterns.tsv."""
from pathlib import Path
import regex as re

RULES_DIR = Path(__file__).parent / "rules"
ENCLITICS = ("nya", "lah", "kah", "pun", "tah")


def _read_list(name: str) -> list[str]:
    lines = (RULES_DIR / name).read_text(encoding="utf-8").splitlines()
    return [l.strip() for l in lines if l.strip() and not l.startswith("#")]


def _alt(items: list[str]) -> str:
    # Longest first, so "dll." is tried before "d." would be
    return "|".join(re.escape(x) for x in sorted(items, key=len, reverse=True))


def _build_pattern(use_exceptions: bool = True) -> "re.Pattern":
    """use_exceptions=False drops the EXCEPTION rule (ablation: regex without the exception list)."""
    exceptions, emoticons = _read_list("exceptions.txt"), _read_list("emoticons.txt")
    parts = []
    for line in _read_list("patterns.tsv"):
        name, regex = line.split("\t", 1)
        if "{EXCEPTIONS}" in regex and not use_exceptions:
            continue
        regex = regex.replace("{EXCEPTIONS}", _alt(exceptions)).replace("{EMOTICONS}", _alt(emoticons))
        parts.append(f"(?P<{name}>{regex})")
    return re.compile("|".join(parts))


PATTERN = _build_pattern()
PATTERN_NO_EXCEPTIONS = _build_pattern(use_exceptions=False)
NO_SPLIT = set(_read_list("no_split.txt"))


def _split_clitic(word: str) -> list[str]:
    low = word.lower()
    if low in NO_SPLIT or "-" in word:
        return [word]
    for c in ENCLITICS:
        if low.endswith(c) and len(low) - len(c) >= 3:
            return [word[: -len(c)], word[-len(c):]]
    return [word]


def tokenize(text: str, split_clitics: bool = False, use_exceptions: bool = True) -> list[tuple[str, str]]:
    """Return [(token, rule_name), ...]. Default = surface tokens (matches UD GSD)."""
    out: list[tuple[str, str]] = []
    for m in (PATTERN if use_exceptions else PATTERN_NO_EXCEPTIONS).finditer(text):
        tok, rule = m.group(), m.lastgroup
        if split_clitics and rule == "WORD":
            out += [(t, "WORD") for t in _split_clitic(tok)]
        else:
            out.append((tok, rule))
    return out


if __name__ == "__main__":
    import sys
    text = " ".join(sys.argv[1:]) or "Dr. Siti datang pukul 07.30 WIB, bayar Rp1.250.000,50 utk buku-buku dll. :( 😂 #liburan"
    for tok, rule in tokenize(text):
        print(f"{rule:<10}{tok}")
