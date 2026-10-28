import argparse
from pathlib import Path
from evaluate import read_conllu, read_informal, evaluate, spans
from tokenizer import tokenize

DATA = Path(__file__).parent / "data"
ap = argparse.ArgumentParser()
ap.add_argument("--final", action="store_true", help="evaluate on the TEST split (do this once)")
ap.add_argument("--errors", type=int, default=15, help="how many top errors to print")
ap.add_argument("--no-exceptions", action="store_true",
                help="add an ablation row: regex tokeniser without the exception list")
args = ap.parse_args()

split = "test" if args.final else "dev"
informal_path = DATA / f"informal_{split}.txt"
informal = read_informal(informal_path) if informal_path.exists() else []

version = DATA / "VERSION.txt"
print(version.read_text() if version.exists() else "(no VERSION.txt: see README, Setup)")

systems = {
    "whitespace baseline": lambda t: t.split(),
    "regex tokenizer": lambda t: [x for x, _ in tokenize(t)],
}
if args.no_exceptions:
    systems["regex, no exception list"] = lambda t: [x for x, _ in tokenize(t, use_exceptions=False)]
gsd = read_conllu(DATA / f"id_gsd-ud-{split}.conllu")

results = {}
print(f"=== UD Indonesian-GSD ({split}) ===")
for name, fn in systems.items():
    results[name] = evaluate(gsd, fn, name)
if informal:
    print(f"\n=== Informal set ({split}: emoji / emoticons / shortforms / slang) ===")
    for name, fn in systems.items():
        evaluate(informal, fn, name)

r = results["regex tokenizer"]
print(f"\nTop {args.errors} gold tokens the regex tokenizer MISSED (GSD {split}):")
for tok, n in r["missed"].most_common(args.errors):
    print(f"  {n:>4}  {tok!r}")
print(f"\nTop {args.errors} tokens it produced that are NOT in gold:")
for tok, n in r["spurious"].most_common(args.errors):
    print(f"  {n:>4}  {tok!r}")
if informal:
    ids, sid = [], "?"
    for line in open(informal_path, encoding="utf-8-sig"):
        if line.startswith("## "):
            sid = line.split()[1] if len(line.split()) > 1 else "?"
        elif line.startswith("# text ="):
            ids.append(sid)
            sid = "?"
    bad = []
    for sid, (text, gold) in zip(ids, informal):
        pred = tokenize(text)
        p = spans(text, [t for t, _ in pred])
        if [t for t, _ in pred] != gold:
            gs = set(spans(text, gold) or [])
            bad.append((sid, text, gold, pred, [f"{t} ({rule})" for (t, rule), sp in zip(pred, p or []) if sp not in gs]))
    print(f"\nInformal {split} sentences where the regex tokenizer differs from gold: {len(bad)} of {len(informal)}"
          f" (first {args.errors})")
    for sid, text, gold, pred, wrong in bad[:args.errors]:
        print(f"\n  {sid}  # text = {text}")
        print(f"    gold: {' | '.join(gold)}")
        print(f"    pred: {' | '.join(t for t, _ in pred)}")
        print(f"    not in gold: {', '.join(wrong)}")
if not args.final:
    print("\n[dev mode] Tune rules using these errors. Run with --final only once at the end.")
