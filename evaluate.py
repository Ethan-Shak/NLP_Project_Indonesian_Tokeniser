#Span-based precision/recall/F1 for tokenisers
from collections import Counter


def read_conllu(path):
    #Yield (text, gold_surface_tokens). A multiword token (e.g. 'Namaku' = Nama+ku) counts as ONE token.
    sents, text, toks, skip_until = [], None, [], 0
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("# text ="):
            text = line.split("=", 1)[1].strip()
        elif not line:
            if text is not None:
                sents.append((text, toks))
            text, toks, skip_until = None, [], 0
        elif not line.startswith("#"):
            cols = line.split("\t")
            idx = cols[0]
            if "." in idx:
                continue
            if "-" in idx:
                skip_until = int(idx.split("-")[1])
                toks.append(cols[1])
            elif int(idx) > skip_until:
                toks.append(cols[1])
    return sents


def read_informal(path):
    #Yield (text, gold_surface_tokens). Raises ValueError if the file is malformed.
    sents, errors = [], []
    text, toks, pos, head_no, broken = None, [], 0, 0, False

    def close():
        if text is None:
            return
        if not broken and text[pos:].strip():
            errors.append(f"line {head_no}: gold tokens do not cover the text, left over: {text[pos:].strip()!r}")
        sents.append((text, toks))

    for no, line in enumerate(open(path, encoding="utf-8-sig"), 1):
        line = line.rstrip("\n")
        if line.startswith("# text ="):
            close()
            text, toks, pos, head_no, broken = line.split("=", 1)[1].strip(), [], 0, no, False
        elif line.startswith("## "):         # comment; '#sedih' or '##' alone is a real token
            continue
        elif not line.strip():
            close()
            text = None
        elif text is None:
            errors.append(f"line {no}: token {line.strip()!r} has no '# text =' header")
        else:
            tok = line.strip()
            toks.append(tok)
            if broken:                       # already reported for this sentence
                continue
            start = len(text) - len(text[pos:].lstrip())
            if text.startswith(tok, start):
                pos = start + len(tok)
            else:
                broken = True
                errors.append(f"line {no}: gold token {tok!r} does not match the text at {text[start:start + 20]!r}")
    close()
    if errors:
        raise ValueError(f"{path}: {len(errors)} format error(s)\n  " + "\n  ".join(errors))
    return sents


def spans(text, tokens):
    out, pos = [], 0
    for t in tokens:
        i = text.find(t, pos)
        if i < 0:
            return None
        out.append((i, i + len(t)))
        pos = i + len(t)
    return out


def evaluate(sents, tok_fn, name=""):
    tp = n_pred = n_gold = skipped = 0
    missed, spurious = Counter(), Counter()
    for text, gold in sents:
        g, p = spans(text, gold), spans(text, tok_fn(text))
        if g is None or p is None:
            skipped += 1
            continue
        gs, ps = set(g), set(p)
        tp += len(gs & ps); n_pred += len(ps); n_gold += len(gs)
        missed.update(text[s:e] for s, e in gs - ps)
        spurious.update(text[s:e] for s, e in ps - gs)
    P = tp / n_pred if n_pred else 0.0
    R = tp / n_gold if n_gold else 0.0
    F = 2 * P * R / (P + R) if P + R else 0.0
    print(f"{name:<28} sentences={len(sents):<5} gold_tokens={n_gold:<7} P={P:.4f}  R={R:.4f}  F1={F:.4f}  (skipped: {skipped})")
    return {"P": P, "R": R, "F1": F, "missed": missed, "spurious": spurious}
