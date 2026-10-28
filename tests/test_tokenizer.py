import random
import sys
from pathlib import Path
import pytest
import regex as re
sys.path.insert(0, str(Path(__file__).parent.parent))
from evaluate import read_informal
from tokenizer import tokenize, PATTERN, PATTERN_NO_EXCEPTIONS


def toks(text, **kw):
    return [t for t, _ in tokenize(text, **kw)]


def test_reduplication_stays_whole():
    assert toks("anak-anak bermain") == ["anak-anak", "bermain"]

def test_ordinal_hyphen_digit():
    assert toks("abad ke-18") == ["abad", "ke-18"]

def test_abbreviation_keeps_period():
    assert toks("buku, pena dll. dijual") == ["buku", ",", "pena", "dll.", "dijual"]

def test_sentence_final_period_is_split():
    assert toks("Dia pulang.") == ["Dia", "pulang", "."]

def test_indonesian_number_format():
    assert toks("Rp1.250.000,50") == ["Rp", "1.250.000,50"]

def test_time_needs_context():
    assert toks("jam 07.30 WIB") == ["jam", "07.30", "WIB"]
    assert toks("harga 3.500") == ["harga", "3.500"]

def test_alphanumeric_tokens_stay_whole():
    assert toks("luas 60 km²") == ["luas", "60", "km²"]            # superscript digit
    assert toks("tank M1 mesin v9") == ["tank", "M1", "mesin", "v9"]
    assert toks("(CuSO4 · 5H2O)") == ["(", "CuSO4", "·", "5H2O", ")"]
    assert toks("lensa 18x zoom") == ["lensa", "18x", "zoom"]       # digits first
    assert toks("ga kira2?") == ["ga", "kira2", "?"]                # informal reduplication

def test_alphanumeric_rule_name():
    assert tokenize("km² M1") == [("km²", "ALNUM"), ("M1", "ALNUM")]

def test_alphanumeric_leaves_numbers_words_and_currency_alone():
    assert tokenize("tahun 1960") == [("tahun", "WORD"), ("1960", "NUMBER")]
    assert tokenize("abad ke-18") == [("abad", "WORD"), ("ke-18", "WORD")]
    assert toks("Rp8") == ["Rp", "8"]
    assert toks("rp50rb") == ["rp", "50rb"]
    assert toks("Rp1.250.000,50") == ["Rp", "1.250.000,50"]

def test_alphanumeric_is_not_clitic_split():
    assert toks("H2Olah", split_clitics=True) == ["H2Olah"]

def test_emoji_sequences_are_single_tokens():
    assert toks("😂") == ["😂"]
    assert toks("🙏🏽") == ["🙏🏽"]            # skin-tone modifier
    assert toks("👨‍👩‍👧") == ["👨‍👩‍👧"]        # ZWJ family
    assert toks("🇮🇩") == ["🇮🇩"]              # flag (two regional indicators)

def test_emoticon_and_hashtag():
    assert toks("capek :( #libur") == ["capek", ":(", "#libur"]

def test_mention_stays_whole():
    assert tokenize("halo @user1, cek") == [("halo", "WORD"), ("@user1", "HASHTAG_MENTION"), (",", "PUNCT"), ("cek", "WORD")]
    assert toks("kirim ke a@b.com") == ["kirim", "ke", "a@b.com"]  # EMAIL wins over mention
    assert toks("di @ sana") == ["di", "@", "sana"]                # bare @ is not a mention

def test_default_keeps_clitic_attached():
    assert toks("Bukunya mahal") == ["Bukunya", "mahal"]

def test_clitic_split_mode_and_no_split_list():
    assert toks("Bukunya", split_clitics=True) == ["Buku", "nya"]
    assert toks("sekolah", split_clitics=True) == ["sekolah"]


# --- catch-all rule / lossless tokenisation ---

def _no_space(text):
    return re.sub(r"\s+", "", text)       # same whitespace definition as the rules (regex \s)

LOSSLESS_FIXED = [
    "",
    "   \t\n ",
    "snake_case_name dan __init__",
    "GL_ARB_robustness",
    "Dr. Siti datang pukul 07.30 WIB, bayar Rp1.250.000,50 utk buku-buku dll. :( 😂 #liburan",
    "lihat https://id.wikipedia.org/wiki/Jakarta_(kota), www.kompas.com.",
    "é ä ́ ² ½ ‰ … “kutip” `` ''",
    "‍ ️ 🏽 🇮 👨‍",
    "1960-an 3.0 10.00 ... .. 1.2.3 12:30:45 a@b.c @ #",
    "\x00\x1f\x7f﻿ 　",
]

def test_catch_all_rule_keeps_otherwise_dropped_characters():
    assert tokenize("a_b") == [("a", "WORD"), ("_", "OTHER"), ("b", "WORD")]

def test_lossless_on_fixed_strings():
    for text in LOSSLESS_FIXED:
        assert "".join(toks(text)) == _no_space(text), repr(text)
        assert "".join(toks(text, split_clitics=True)) == _no_space(text), repr(text)
        assert "".join(toks(text, use_exceptions=False)) == _no_space(text), repr(text)

def test_lossless_on_random_strings():
    rng = random.Random(91258)
    alphabet = list("abknyaRpDr 019 \t\n.,:;!?()-_#@/'\"`=%&<>") + [
        "😂", "🙏", "🏽", "‍", "️", "🇮", "🇩", "²", "é", "́", "…", " ", "http://", "www.", "dll.", "-an"]
    for _ in range(2000):
        if rng.random() < 0.5:
            text = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 40)))
        else:                               # arbitrary code points, surrogates excluded
            text = "".join(chr(rng.choice([rng.randrange(0x20, 0x250), rng.randrange(0x2000, 0x3100),
                                           rng.randrange(0x1F000, 0x1FB00), rng.randrange(0, 0xD800)]))
                           for _ in range(rng.randint(0, 40)))
        assert "".join(toks(text)) == _no_space(text), repr(text)


# --- URL ---

def test_url_does_not_swallow_trailing_punctuation():
    assert toks("lihat https://example.com/a?b=1.") == ["lihat", "https://example.com/a?b=1", "."]
    assert toks("(http://kompas.com/berita/), lalu") == ["(", "http://kompas.com/berita/", ")", ",", "lalu"]
    assert toks("buka www.detik.com!") == ["buka", "www.detik.com", "!"]
    assert toks("https://a.id/x#bagian-2, ya") == ["https://a.id/x#bagian-2", ",", "ya"]

def test_url_rule_name_and_allowed_endings():
    assert tokenize("www.kompas.com") == [("www.kompas.com", "URL")]
    for url in ["https://a.id/", "https://a.id/#", "https://a.id/?q=", "https://a.id/a%20", "https://a.id/a-", "https://a.id/a_b"]:
        assert tokenize(url) == [(url, "URL")]

def test_url_needs_something_after_the_prefix():
    assert toks("www. kosong") == ["www", ".", "kosong"]


# --- number rules supported by GSD train (python rule_support.py) ---

def test_decade_suffix_an_stays_whole():
    assert tokenize("tahun 1960-an dan 70-an.") == [
        ("tahun", "WORD"), ("1960-an", "NUM_AN"), ("dan", "WORD"), ("70-an", "NUM_AN"), (".", "PUNCT")]
    assert toks("1960-anak") == ["1960", "-", "anak"]              # only the bare suffix -an

def test_dot_decimal_stays_whole():
    assert tokenize("versi 3.0 pukul 10.00") == [("versi", "WORD"), ("3.0", "NUMBER"), ("pukul", "WORD"), ("10.00", "NUMBER")]
    assert toks("pi 3.1416") == ["pi", "3.1416"]                   # not 3.141 + 6
    assert toks("Rp1.250.000,50") == ["Rp", "1.250.000,50"]        # thousands + comma decimal unchanged
    assert toks("tahun 2010. Dia") == ["tahun", "2010", ".", "Dia"]  # sentence-final period still split

def test_ellipsis_convention_unchanged():
    # GSD train is split 3 vs 3 on '...' as one token vs three dots: no support for changing the rule
    assert toks("tunggu...") == ["tunggu", "..."]

def test_ellipsis_is_three_or_more_dots_or_the_single_character():
    assert toks("a... b") == ["a", "...", "b"]
    assert toks("a… b") == ["a", "…", "b"]
    assert toks("a.. b") == ["a", ".", ".", "b"]
    assert tokenize("a.... b") == [("a", "WORD"), ("....", "PUNCT"), ("b", "WORD")]   # longer runs are one token (rule 5a)
    assert toks("a..... b") == ["a", ".....", "b"]
    assert toks("Thailand........... Bertanding") == ["Thailand", "...........", "Bertanding"]
    assert toks("a!!! b") == ["a", "!", "!", "!", "b"]             # other repeated punctuation: one token per character


def test_double_backtick_quote_stays_whole():
    assert tokenize("kata ``Hai") == [("kata", "WORD"), ("``", "QUOTE_OPEN"), ("Hai", "WORD")]
    assert toks("`x`") == ["`", "x", "`"]                          # single backticks unchanged

def test_double_apostrophe_quote_stays_whole():
    assert tokenize("``superstar''?") == [("``", "QUOTE_OPEN"), ("superstar", "WORD"), ("''", "QUOTE_CLOSE"), ("?", "PUNCT")]
    assert toks("'x'") == ["'", "x", "'"]                          # single apostrophes unchanged

def test_apostrophe_s_stays_whole():
    assert tokenize("Rubik's kuasa") == [("Rubik's", "CONTRACTION"), ("kuasa", "WORD")]
    assert toks("'saya' ya") == ["'", "saya", "'", "ya"]           # quotes around a word still split

def test_english_contractions_stay_whole():
    for w in ["I'm", "you're", "we've", "I'll", "he'd", "Lloyd's", "don't", "can't", "isn't", "I’m"]:
        assert tokenize(w) == [(w, "CONTRACTION")], w

def test_indonesian_apostrophe_is_not_a_contraction():
    assert toks("do'anya") == ["do", "'", "anya"]
    assert toks("ba'da") == ["ba", "'", "da"]
    assert toks("Jum'at") == ["Jum", "'", "at"]

def test_emoticon_family_is_one_token():
    for e in [":((", ":))", ":-)))", ":'(", ":''(", ":(", ";)", ":-("]:
        assert tokenize(f"kecewa {e}") == [("kecewa", "WORD"), (e, "EMOTICON")], e

def test_emoticon_list_faces():
    for e in [':"', "-_-", "^_^", "T_T", "xD", ":v", ":D", "<3"]:
        assert tokenize(f"wkwk {e} ya") == [("wkwk", "WORD"), (e, "EMOTICON"), ("ya", "WORD")], e

def test_emoticon_may_start_right_after_a_word():
    assert tokenize("ALLAH:( perkara") == [("ALLAH", "WORD"), (":(", "EMOTICON"), ("perkara", "WORD")]
    assert toks("happy meal-_-") == ["happy", "meal", "-_-"]
    assert toks("2:)") == ["2", ":)"]

def test_emoticon_not_followed_by_letter_or_digit():
    assert toks("Catatan:(1)") == ["Catatan", ":", "(", "1", ")"]
    assert toks('kata:"halo"') == ["kata", ":", '"', "halo", '"']
    assert toks("pukul 10:30") == ["pukul", "10:30"]
    assert toks("lihat:Dua") == ["lihat", ":", "Dua"]


# --- ablation: regex without the exception list ---

def test_no_exceptions_ablation_splits_abbreviation_periods():
    assert toks("buku dll. dijual") == ["buku", "dll.", "dijual"]
    assert toks("buku dll. dijual", use_exceptions=False) == ["buku", "dll", ".", "dijual"]
    assert "EXCEPTION" in PATTERN.groupindex and "EXCEPTION" not in PATTERN_NO_EXCEPTIONS.groupindex


# --- informal gold file reader ---

def _informal(tmp_path, content):
    path = tmp_path / "gold.txt"
    path.write_text(content, encoding="utf-8")
    return path

def test_informal_reader_keeps_hashtag_lines(tmp_path):
    path = _informal(tmp_path, "## comment line\n# text = bgt deh :( #sedih\nbgt\ndeh\n:(\n#sedih\n")
    assert read_informal(path) == [("bgt deh :( #sedih", ["bgt", "deh", ":(", "#sedih"])]

def test_informal_reader_comments_need_hash_hash_space(tmp_path):
    path = _informal(tmp_path, "## a comment\n# text = ## ##x #\n##\n## not a token, a comment\n##x\n#\n")
    assert read_informal(path) == [("## ##x #", ["##", "##x", "#"])]

def test_informal_reader_rejects_token_without_header(tmp_path):
    path = _informal(tmp_path, "## header\n\ngue\nlagi\n\n# text = ok\nok\n")
    with pytest.raises(ValueError) as e:
        read_informal(path)
    assert "line 3:" in str(e.value) and "line 4:" in str(e.value) and "line 7" not in str(e.value)

def test_informal_reader_rejects_gold_that_does_not_cover_text(tmp_path):
    cases = {
        "# text = jgn telat!!\njgn\ntelat\n!\n": "line 1:",            # last '!' missing
        "# text = jgn telat!!\njgn\ntelat\n!\n!\n!\n": "line 6:",      # one token too many
        "# text = jgn telat\njgn\ntelta\n": "line 3:",                 # typo in a token
        "# text = jgn telat\ntelat\njgn\n": "line 2:",                 # wrong order / skipped text
        "# text = a b\na\nb\n# text = c d\nc\n": "line 4:",            # second sentence incomplete
    }
    for content, where in cases.items():
        with pytest.raises(ValueError) as e:
            read_informal(_informal(tmp_path, content))
        assert where in str(e.value), (content, str(e.value))

def test_informal_gold_files_are_well_formed():
    for name in ("informal_dev.txt", "informal_test.txt"):
        read_informal(Path(__file__).parent.parent / "data" / name)   # raises on format errors
