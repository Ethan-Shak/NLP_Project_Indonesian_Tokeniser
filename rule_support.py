"""Does TRAIN support a candidate rule?   python rule_support.py
For every match of a candidate regex in the raw text of GSD train, count
  agree    = gold has exactly ONE token over the match span
  disagree = gold segments the match differently (the gold segmentation is printed).
Train only: never point this at dev or test."""
from collections import Counter
from pathlib import Path
import regex as re
from evaluate import read_conllu, spans

TRAIN = Path(__file__).parent / "data" / "id_gsd-ud-train.conllu"
CANDIDATES = {
    r"\d+-an  (1960-an)": r"(?<![\w.,-])\d+-an(?![\w-])",
    r"\d+\.\d+  (3.0, 10.00)": r"(?<![\w.,])\d+\.\d+(?![\w]|[.,]\d)",
    r"``  (GSD quote token)": r"``",
    r"''  (GSD closing quote)": r"(?<!')''(?!')",
    r"contraction  (Rubik's, I'm, don't)": r"(?<![\w'’])\p{L}+(?i:n['’]t|['’](?:s|m|re|ve|ll|d))(?!\w)",
    r"emoticon family  (:(( :-))) :''()": r"[:;](?:-|'{1,2})?[()]+(?![\p{L}\p{N}])",
    r"emoticon list extras  (:\" -_- xD :v)": r"(?:-_-|\^_\^|T_T|xD|XD|:v|:\"|:-?D|:[Pp]|<3)(?![\p{L}\p{N}])",
    r"...  (one token vs three dots)": r"(?<!\.)\.{3}(?!\.)",
    r"....+  (runs of 4+ dots, PUNCT rule 5a)": r"(?<!\.)\.{4,}(?!\.)",
    # frequency of forms the tokeniser deliberately leaves unsupported (guideline rule 6): disagree = GSD splits the period
    r"dotted initialism  (S.Kom., U.S.A.)": r"(?<![\w.])(?:\p{L}{1,4}\.){2,}(?!\w)",
    r"no. + number/Name  (no. 5, No. Budi)": r"(?<![\w.])[Nn]o\.(?=\s?(?:\d|\p{Lu}))",
}


def support(sents, pattern):
    agree, disagree, how = 0, 0, Counter()
    for text, gold in sents:
        g = spans(text, gold)
        if g is None:
            continue
        for m in re.finditer(pattern, text):
            if m.span() in g:
                agree += 1
            else:
                disagree += 1
                how[" | ".join(text[s:e] for s, e in g if s < m.end() and e > m.start())] += 1
    return agree, disagree, how


if __name__ == "__main__":
    sents = read_conllu(TRAIN)
    print(f"GSD train: {len(sents)} sentences, {sum(len(gold) for _, gold in sents)} gold tokens")
    for name, pattern in CANDIDATES.items():
        agree, disagree, how = support(sents, pattern)
        print(f"\n{name:<34} agree={agree:<5} disagree={disagree}")
        for seg, n in how.most_common(8):
            print(f"  {n:>4}  gold: {seg}")
