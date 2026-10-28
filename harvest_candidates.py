"""Pick CANDIDATE sentences from public datasets you already downloaded, for you to vet by hand.

 * Does NOT import tokenizer.py: phenomena are tagged by its own simple regexes, so selection
   is independent of the system under test (otherwise your test set would be biased towards what it handles).
 * Output uses the raw_informal.tsv columns:  id <TAB> source <TAB> tags <TAB> text
 * Vet every row (delete bad ones), then copy the keepers into data/raw_informal.tsv.
 * Does not touch gold annotations.

"""
import argparse, csv, random, re
from pathlib import Path

TAGS = {  # phenomenon -> (regex, target number of FINAL sentences)
    "emoticon":   (re.compile(r"(?<!\w)(?::-?[()DPp]|;-?\)|xD|T_T|\^_\^)(?!\w)"), 8),
    "hashtag":    (re.compile(r"(?<!\w)#\w+"), 8),
    "mention":    (re.compile(r"(?<!\w)@\w+"), 8),
    "url":        (re.compile(r"https?://|www\."), 5),
    "elongation": (re.compile(r"(\w)\1{2,}"), 8),
    "abbrev":     (re.compile(r"\b(dll|dsb|dkk|tsb|yth|dr|drs|prof|no|tgl|hlm|jl)\.", re.I), 6),
    "number":     (re.compile(r"\b\d+\s?(rb|ribu|k|jt)\b|\b\d{1,2}[.:]\d{2}\b|\bRp\.?\s?\d", re.I), 10),
    "hyphen":     (re.compile(r"\w-\w"), 8),
    # vowel-omitted spellings of an ordinary word (disemvowelling): an orthographic shortcut, NOT slang
    # (Wibowo et al. 2021, IndoCollex: "Disemvowelling" is a spelling transformation, separate from "Jargon"/"Loan words")
    "shortform":  (re.compile(r"\b(?:yg|tdk|dg|dgn|utk|tp|bgt|udh|sdh|emg|jgn|krn|blm|skrg|lgi|lg|msi|drpd|smpe|smngt|mntp|"
                              r"klo|klw|kmrn|kdg|gmn|pdhl|dpt|jd|jdi|bny|bnr|pgn|trs|tnggl|wlpun|sy|kyk|bs|gk|gw)2?\b", re.I), 10),
    # slang = a colloquial lexeme written out in full (gue, banget, nggak, sih ...); bgt/udh/yg are shortforms, see above
    "slang":      (re.compile(r"\b(gak|ga|ngga|nggak|gue|lu|banget|nih|sih|dong|kok|deh)\b", re.I), 20),
}
CONTROL_TARGET = 10
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿\U0001F1E6-\U0001F1FF]")

ap = argparse.ArgumentParser()
ap.add_argument("--input", action="append", required=True, help='"path|source_name|text_column"')
ap.add_argument("--out", default="data/candidates.tsv")
ap.add_argument("--min-chars", type=int, default=30)
ap.add_argument("--max-chars", type=int, default=150)
ap.add_argument("--oversample", type=float, default=2.0, help="candidates = target x this, so you can reject some")
ap.add_argument("--fill-placeholders", action="store_true",
                help="turn [USERNAME]/[URL] placeholders into @userN / https://example.com/N (SYNTHETIC: say so in the report)")
ap.add_argument("--seed", type=int, default=13)
args = ap.parse_args()
rng = random.Random(args.seed)

pool, seen = [], set()
for spec in args.input:
    path, source, col = spec.split("|")
    for row in csv.DictReader(open(path, encoding="utf-8", newline="")):
        text = " ".join(row[col].split())               # one line, no tabs/newlines
        if args.fill_placeholders:
            n = [0]
            text = re.sub(r"\[USERNAME\]", lambda m: f"@user{(n.__setitem__(0, n[0] + 1) or n[0])}", text)
            text = re.sub(r"\[URL\]", "https://example.com/" + str(rng.randint(100, 999)), text)
        elif re.search(r"\[(USERNAME|URL)\]", text):
            continue
        if not (args.min_chars <= len(text) <= args.max_chars) or text.lower() in seen:
            continue
        seen.add(text.lower())
        tags = [t for t, (rx, _) in TAGS.items() if rx.search(text)]
        if EMOJI.search(text):
            tags.append("emoji")
        pool.append((source, tags, text))

chosen, used = [], set()
def take(tag, k):
    cands = [i for i, (_, tags, _) in enumerate(pool) if (tag in tags if tag else not tags) and i not in used]
    rng.shuffle(cands)
    for i in cands[:k]:
        used.add(i); chosen.append(pool[i])
    return len(cands[:k])

report = {}
for tag in sorted(TAGS, key=lambda t: sum(t in p[1] for p in pool)):       # rarest phenomenon first
    report[tag] = (TAGS[tag][1], take(tag, int(TAGS[tag][1] * args.oversample)))
report["control"] = (CONTROL_TARGET, take(None, int(CONTROL_TARGET * args.oversample)))

Path(args.out).parent.mkdir(parents=True, exist_ok=True)
with open(args.out, "w", encoding="utf-8", newline="\n") as f:
    f.write("## CANDIDATES to vet. Delete bad rows, copy keepers into data/raw_informal.tsv and renumber ids.\n")
    f.write("## Cite sources (NusaX: Winata et al. 2023, CC BY-SA 4.0; IndoNLU EmoT: Wilie et al. 2020 / Saputri et al. 2018).\n")
    for i, (source, tags, text) in enumerate(chosen, 1):
        f.write(f"C{i:03d}\t{source}\t{','.join(tags) or 'control'}\t{text}\n")

print(f"pool after filters: {len(pool)} sentences; wrote {len(chosen)} candidates to {args.out}")
print(f"{'phenomenon':<12}{'target':>7}{'candidates':>11}")
for tag, (want, got) in report.items():
    print(f"{tag:<12}{want:>7}{got:>11}{'   <-- below target' if got < want else ''}")
print(f"{'emoji':<12}{'15+6':>7}{sum('emoji' in c[1] for c in chosen):>11}   <-- datasets have none: collect these yourself")
