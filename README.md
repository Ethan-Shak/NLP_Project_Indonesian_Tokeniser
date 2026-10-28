# Indonesian regex tokeniser (NLP 91258)

Rule-based tokeniser: regular expressions + exception lists, with emoji/emoticon support,
evaluated against UD Indonesian-GSD and a small hand-annotated informal set.

## Setup
macOS / Linux:

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

Windows PowerShell (`python3` there is usually a Microsoft Store stub, so use `python` or `py`):

    python -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    $env:PYTHONUTF8 = "1"              # required: see below

On Windows, Python writes to the console and to redirected files in the legacy code page (cp1252),
so printing an emoji crashes with `UnicodeEncodeError`. That breaks `tokenizer.py` on the example
below and `run_all.py --final` partway through. Set `PYTHONUTF8=1` in every new shell
(`set PYTHONUTF8=1` in cmd), or run scripts as `python -X utf8 ...`. On Windows PowerShell 5.1, save
output with `| Out-File -Encoding utf8 <file>`, not `>`: `>` writes UTF-16.

UD Indonesian-GSD is not in the repo. Download these three files into `data/`, from the commit pinned
in `data/VERSION.txt`:

    https://raw.githubusercontent.com/UniversalDependencies/UD_Indonesian-GSD/bc23d75691fd97255bbd420c4dbacd423b0ede95/id_gsd-ud-train.conllu
    https://raw.githubusercontent.com/UniversalDependencies/UD_Indonesian-GSD/bc23d75691fd97255bbd420c4dbacd423b0ede95/id_gsd-ud-dev.conllu
    https://raw.githubusercontent.com/UniversalDependencies/UD_Indonesian-GSD/bc23d75691fd97255bbd420c4dbacd423b0ede95/id_gsd-ud-test.conllu

## Run
    python tokenizer.py "Dr. Siti datang pukul 07.30 WIB :( 😂"   # try it
    pytest -q                                                      # unit tests
    python run_all.py                                              # evaluate on DEV (while tuning)
    python run_all.py --final                                      # evaluate on TEST (once, at the end)

## Reproduce the reported results
    pytest -q                                   # all tests pass
    python run_all.py --no-exceptions           # dev tables
    python run_all.py --final --no-exceptions   # test tables (frozen system)
    python rule_support.py                      # GSD train support counts

Each `--no-exceptions` run prints the whitespace baseline, the primary system and the ablation (no
exception list) together. The frozen outputs in `results/` were produced as follows:

    python run_all.py --final                       > results/final_primary.txt
    python run_all.py --final --no-exceptions       > results/final_no_exceptions.txt
    python run_all.py --final --errors 100          > results/final_informal_errors.txt

`results/frozen_hashes.txt` holds SHA-256 hashes of the frozen system and gold files. Check them with
`sha256sum -c results/frozen_hashes.txt` (Git Bash / Linux) or `shasum -a 256 -c` (macOS).

## Layout
    rules/patterns.tsv    regex rules, in priority order
    rules/exceptions.txt  abbreviations that keep their period
    rules/emoticons.txt   text emoticons
    rules/no_split.txt    words that look like stem+clitic but are not
    data/informal_dev.txt   hand-annotated informal sentences, dev split (used by run_all.py)
    data/informal_test.txt  hand-annotated informal sentences, test split (used by run_all.py --final)
    rules/annotation_guideline.md  annotation rules for the informal set + decision log

Informal file format: `# text = <sentence>`, then one gold token per line, blank line between
sentences; a line starting `## ` (with the space) is a comment.
