# Annotation guideline: informal Indonesian tokenisation set (v1)

**Purpose.** This guideline defines the gold (single chunk) tokens for `data/informal_dev.txt` and `data/informal_test.txt`. Where possible it follows UD Indonesian-GSD at the surface level (clitics stay attached, reduplication stays whole). Rows marked * deliberately differ from GSD, because the set covers social-media text that GSD does not contain.

The tokeniser's output was never used or consulted while annotating. Doubtful cases are logged in section 3.

## 1. Rules

| # | Phenomenon | Rule | Gold tokens (examples) |
|---|---|---|---|
| 1a | Shortforms (vowel-omitted spellings) | Whole, as written. No normalisation or spelling correction. Not slang, see section 2a | `yg` `tdk` `bgt` `dgn` |
| 1b | Slang, colloquial words | Whole, as written. No normalisation or spelling correction | `gak` `gue` `sih` `lebay` |
| 2 | Elongation, laughter | Whole, as written | `bangeeet` `wkwkwkwk` |
| 3 | Reduplication, hyphens | Whole | `anak-anak` `ke-18` `di-update` `gue-nya` |
| 4 | Clitics (-nya -ku -mu -lah -kah) | Attached to the host | `bukunya` `ayahku` |
| 5 | Punctuation | Each punctuation character is its own token, even without surrounding spaces | `,` `!` `(` `)` |
| 6 | Abbreviations with a period* | One token, period kept inside, for any conventional abbreviation or dotted initialism, whether or not the tokeniser's list contains it. A sentence-final abbreviation keeps its one period (no extra `.` token). Ordinary words followed by a period are split | `Dr.` `dll.` `Yth.` `S.Kom.` `U.S.A.` |
| 7 | Numbers | Whole, including Indonesian separators; the per cent sign is separate | `1.500.000` `1,5` `20` `%` |
| 8 | Letter+digit runs | Whole | `50rb` `2jt` `km2` |
| 9 | Currency | Symbol or `Rp` is separate from the amount | `Rp` `1.500.000` |
| 10 | Times | Whole; a time zone label is separate | `19.30` `07.30` `WIB` |
| 11 | Emoji | One token per emoji, including skin-tone modifiers, ZWJ sequences, flags and keycaps. Repeated emoji are separate tokens | `😂` `😂` `🙏🏽` `👨‍👩‍👧` `🇮🇩` |
| 12 | Emoticons | A text face is one token, even if not in any list | `:(` `xD` `T_T` `^_^` `:v` |
| 13 | Hashtags, mentions* | Whole, trailing punctuation excluded (GSD splits `#`) | `#terbaik` `@user1` |
| 14 | URLs, emails | Whole, trailing punctuation or closing bracket excluded | `https://example.com/a` `)` `.` |
| 15 | English words and contractions | Same rules; English contractions (`'s` `'m` `'re` `'ve` `'ll` `'d` `n't`) stay whole | `meeting` `Lloyd's` `I'm` `We're` `don't` |
| 16 | Quotes and brackets | Separate characters | `"` `(` `)` |
| 17 | Glued text | Split at emoji and punctuation boundaries even without a space; do not insert or remove spaces between words | `enak😂` -> `enak` `😂`; `dirumah` stays one token |

Rule 5a*. Ellipsis: a run of three or more ASCII dots (`...`, `....`, `...........`) or the single character `…` is ONE token.
Two dots (`..`) are annotated as separate dots. Other repeated punctuation
(`!!!`, `???`) stays one token per character, because that is emphasis by repetition, whereas an ellipsis is a conventional unit.

Rule 6 details.
- Gold does not depend on `exceptions.txt`: `Ny.`, `S.Kom.` and `M.Sc.` are whole even if the list lacks them. The tokeniser will miss some; that is a finding about the list's limits.
- No duplicated period: `... buku, pena dll.` gives `dll.` and no separate `.`, since there is only one period character.
- Ordinary words or missing whitespace  are not treated as abbreviations and still split.
- Dotted initials and acronyms stay whole: `H.` `U.S.A.` `S.H.`
- Unclear cases go in the decision log (section 3). `no.` is an abbreviation of "nomor" only when a number or a capitalised name follows; otherwise split the period.
- Abbreviations written without a period (`dll`, `yg`, `tp`) are ordinary shortforms (rule 1a), whole as written.
- Acronyms written without internal periods (`TPQ`, `DPR`, `TNI`) are ordinary words for this rule: a following period is sentence-final and is split (`TPQ` `.`). `JL.` is an abbreviation of "Jalan" and stays whole.

## 2. Where this differs from GSD, and why

- Abbreviation periods kept whole (rule 6): the brief asks for exception lists; the cost is measured by the ablation without the list.
- Hashtags and mentions kept whole (rule 13): they are single units in social-media text.
- Dot runs of three or more (`...`, `....`, `...........`) kept as one token (rule 5a): a deliberate informal-set convention. GSD gives no basis either way: `...` is split 3 one-token vs 3 three-dot cases in train, and runs of four or more dots never occur (0 cases). Long dot runs are common in social-media text, where they work as one ellipsis. The tokeniser's PUNCT rule follows this convention. Extending it from exactly three dots to three or more leaves GSD scores unchanged, since GSD has no longer runs.
- Everything else follows GSD's surface convention (clitics attached, reduplication whole, letter+digit runs whole).

## 2a. Shortform vs slang (affects the `tags` column of `raw_informal.tsv`, not the gold tokens)

- **shortform**: an ordinary word spelled with its vowels (partly or wholly) left out: `yg` (yang), `tdk` (tidak), `dgn` (dengan), `utk` (untuk), `tp` (tapi), `bgt` (banget), `skrg` (sekarang). The word is unchanged; only the spelling is shortened. Not slang.
- **slang**: a colloquial or in-group lexeme written out in full: `gue`, `gak`, `banget`, `sih`, `dong`, `lebay`, `anjir`. A spelling shortcut of such a word (`bgt`) is a shortform; the full lexeme (`banget`) is slang.
- Typos and one-off respellings (`abngnya`, `brusaha`) are tagged `shortform` when vowels were dropped, otherwise left untagged.
- Basis. Wibowo et al. (2021, Section 3.1) list *disemvowelling* ("elimination of some or all the vowels", for example `jangan` -> `jgn`) as one of nine word-formation mechanisms of colloquial Indonesian, separate from their "loan words" and "jargon" categories. The paper does not define "slang" or "shortform", so the rule above is my operational reading of that taxonomy, not a category of the resource.
- Tokenisation is unaffected: both classes stay whole (rules 1a/1b), so no gold token changes.

**Tag definitions** (a row gets every tag that applies; `control` = none apply; order as listed):
`emoticon` text face (rule 12) · `hashtag` `#word`, including `#1` · `mention` `@user1` (not a bare `@`) · `url` ·
`elongation` letters repeated beyond the standard spelling (`yaaahhh`, `Kereen`, `yuukk`) or laughter (`wkwk`, `haha`) ·
`abbrev` abbreviation with a period (rule 6) · `number` any digit run outside a hashtag/URL, including letter+digit runs
and digit reduplication (`50rb`, `3bulan`, `pura2`, `sehat²`, `+62`) · `hyphen` word-internal hyphen (rule 3) ·
`shortform` / `slang` as above (`gw`, `w`, `u` are shortforms of `gue`/`you`) · `codeswitch` English (or other-language)
words or clauses not respelled as Indonesian (`trending`, `deadline-nya`, `dichat`), not names or acronyms ·
`emoji_mod` emoji with skin tone, ZWJ, flag or keycap · `emoji` any other emoji.

## 3. Decision log (add a row for every doubtful case)

| Date | Sentence id | Case | Decision | Rule |
|---|---|---|---|---|
| 2026-10-20 | S010-S028, C-rows | `yg` `bgt` `tdk` `udh` ... tagged `slang` by the first harvest regex | Retagged `shortform`; `slang` kept only where a colloquial lexeme is written out (C014, C028, C030, C053, C067 lost `slang`) | 1a, 2a |
| 2026-10-20 | all rows | Tags re-checked by hand against the tag definitions in 2a (73 of 132 rows changed) | `gw` is a shortform, not slang; laughter counts as elongation; digit reduplication counts as number | 2a |
| 2026-10-20 | (rule) | `no.` : abbreviation of "nomor" or the word "no" ending a sentence | Abbreviation (`no.` whole) only when a number or capitalised name follows; otherwise `no` `.` | 6 |
| 2026-10-21 | C039 | Case change inside a word (`giniEhh`) | Not a boundary; kept whole as one token | 17 |
| 2026-10-21 | S013 | Country calling code `+62` (used as "Indonesian"): `+` `62` or whole | Whole `+62`: a country code reads as one unit. Splitting is also defensible | 7 |
| 2026-10-21 | C075 | `tuh.g,` | A typo with a dropped space, not an abbreviation; split at the punctuation | 5, 17 |
| 2026-10-21 | (rule) | Dot runs longer than three (`....`, `...........`) were separate dots | Any run of three or more dots is one token; earlier annotations with separate dots merged. `..` stays two dots | 5a |
| 2026-10-21 | C016 | Apostrophe inside an Indonesian word (`do'anya`, "doa" + `-nya`) | Whole: the apostrophe is part of the spelling, as for English `'s`/`n't` | 15 |
| 2026-10-21 | C071 | Stylised name with punctuation inside (`p!nk`, the singer P!nk) | Whole: a name, not a word followed by `!` | 5 |
| 2026-10-21 | C013 | Time written with a colon (`10:25`) | Whole, like dot times (`19.30`) | 10 |
| 2026-10-21 | C063 (dev) | `:"` : crying face or `:` + `"` | One emoticon token | 12 |
| 2026-10-21 | C021, C087 (dev), C043 | Emoticons with a repeated or doubled mouth/tears (`:((`, `:''(`, `:))`) | Whole: rule 12 (text face is one token) takes precedence over 5a's one-token-per-character for repeated punctuation | 12, 5a |
| 2026-10-21 | C038 (dev) | `dikejar` `2` split, while `ngejar2` in the same sentence was whole. Found in the tokeniser's dev error output (`run_all.py --errors`), after annotation | Corrected to `dikejar2` (letter+digit run whole). Dev gold only; this edit brought informal dev F1 to 1.0000 | 8 |
| 2026-10-24 | C070 (dev), C067 | Rule 15 named only `'s` and `n't`, but gold already had `I'm` and `We're` whole | Rule text widened to all English contractions (`'s 'm 're 've 'll 'd n't`), matching the existing gold and the CONTRACTION rule. Wording only: no gold token changed | 15 |

## 4. Limitations

Single annotator; no inter-annotator agreement unless measured separately; the set was built to cover phenomena, not to be a representative sample of informal Indonesian.

Glued words are kept whole because only spaces, punctuation and emoji count as boundaries (rule 17): missing spaces
(`dirumah`, `yguda`) and case changes inside a word (`giniEhh`) stay one token. Gold therefore under-segments these,
and neither the gold nor the tokeniser recovers the underlying words.
