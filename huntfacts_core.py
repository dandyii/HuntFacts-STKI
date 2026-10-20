"""
HuntFacts core: preprocessing, inverted index, TF-IDF cosine, dan BM25.
Modul ini dipakai bersama oleh notebook dan aplikasi Streamlit (app.py).
"""
import html
import math
import pickle
import re
import unicodedata
from collections import Counter, defaultdict

import numpy as np
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# ----------------------------------------------------------------------------
# 1. Sumber daya preprocessing
# ----------------------------------------------------------------------------
URL_RE = re.compile(
    r"(?:https?://|www\.)\S+"
    r"|\b\S+\[dot\]\S+"
    r"|\b(?:bit\.ly|goo\.gl|s\.id|t\.me|wa\.me|tinyurl\.com)/\S+",
    re.I,
)
SHORTCODE_RE = re.compile(r":[a-z_]{2,}:")
EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\u2190-\u21FF\u200d\ufe0f]+"
)
REDUP_RE = re.compile(r"^([a-z]{3,})2$")  # teman2 -> teman, hati2 -> hati

# Stopword standar Sastrawi
# ditambah penanda struktur artikel turnbackhoax.id yang tidak membawa isi klaim
STRUCT_STOPWORDS = {"kategori", "sumber", "narasi", "penjelasan", "referensi", "kesimpulan"}
BASE_STOPWORDS = frozenset(set(StopWordRemoverFactory().get_stop_words()) | STRUCT_STOPWORDS)

# Stopword khusus pesan berantai. Dicocokkan pada kata mentah (sebelum stemming)
# supaya kata isi seperti "menyebarkan" (dalam konteks "ISIS menyebarkan AIDS")
# tidak ikut terbuang oleh stemming yang menyamakannya dengan "sebarkan".
CHAIN_STOPWORDS = frozenset("""
sebarkan sebarkanlah disebarkan sebarluaskan disebarluaskan viralkan diviralkan
viral share shared dishare sharing bagikan dibagikan forward diforward teruskan
diteruskan broadcast bc copas copy paste mohon tolong harap himbauan imbauan
info informasi infokan menginfokan diinformasikan sekedar sekadar kabar
assalamualaikum assalamu alaikum waalaikumsalam wr wb salam shalom
yth kepada bapak ibu bpk teman kawan sahabat saudara saudaraku dulur rekan
grup group sebelah wag fyi sob gaes guys gan
ya yaa yah nih lho loh dong deh sih kok lah kan nah mah tuh
semoga bermanfaat amin aamiin amiin mari ayo
""".split())

# Normalisasi kata tidak baku ke bentuk baku (disusun manual untuk proyek ini).
SLANG = {
    "yg": "yang", "yng": "yang", "dg": "dengan", "dgn": "dengan", "dng": "dengan",
    "utk": "untuk", "untk": "untuk", "krn": "karena", "karna": "karena",
    "sdh": "sudah", "udah": "sudah", "udh": "sudah", "dah": "sudah", "sudh": "sudah",
    "blm": "belum", "belom": "belum", "jgn": "jangan", "gak": "tidak", "ga": "tidak",
    "gk": "tidak", "nggak": "tidak", "ngga": "tidak", "engga": "tidak", "tdk": "tidak",
    "bkn": "bukan", "aja": "saja", "aj": "saja", "gmn": "bagaimana", "gimana": "bagaimana",
    "knp": "kenapa", "emg": "memang", "emang": "memang", "bgt": "sangat", "banget": "sangat",
    "bs": "bisa", "jd": "jadi", "tp": "tapi", "dpt": "dapat", "dapet": "dapat",
    "dpet": "dapat", "org": "orang", "orng": "orang", "dlm": "dalam", "pd": "pada",
    "spy": "supaya", "hrs": "harus", "sbg": "sebagai", "tsb": "tersebut", "kpd": "kepada",
    "tgl": "tanggal", "thn": "tahun", "bln": "bulan", "hr": "hari", "jt": "juta",
    "rb": "ribu", "smp": "sampai", "sampe": "sampai", "klo": "kalau", "kalo": "kalau",
    "kl": "kalau", "lg": "lagi", "lgi": "lagi", "sy": "saya", "gw": "saya", "gue": "saya",
    "mhn": "mohon", "tlg": "tolong", "tolg": "tolong", "pke": "pakai", "pake": "pakai",
    "pakek": "pakai", "skrg": "sekarang", "skrng": "sekarang", "sdg": "sedang",
    "kmrn": "kemarin", "bsk": "besok", "hub": "hubungi", "krm": "kirim",
    "wa": "whatsapp", "fb": "facebook", "ig": "instagram",
    "rs": "rumah sakit", "pkm": "puskesmas", "covid19": "covid",
    "cm": "cuma", "cuman": "cuma", "kyk": "seperti", "kayak": "seperti", "sm": "sama",
}

_STEMMER = None
STEM_CACHE = {}


def stem_word(word):
    """Stemming Sastrawi dengan cache per kata unik (jauh lebih cepat)."""
    global _STEMMER
    s = STEM_CACHE.get(word)
    if s is None:
        if _STEMMER is None:
            _STEMMER = StemmerFactory().create_stemmer()
        s = _STEMMER.stem(word)
        STEM_CACHE[word] = s
    return s


class Preprocessor:
    """
    Pipeline: case folding -> hapus URL/emoji/tanda baca -> tokenizing ->
    (opsional normalisasi kata tidak baku) -> stopword removal -> stemming.
    """

    def __init__(self, chain_stop=False, slang_norm=False, stem=True):
        self.chain_stop = chain_stop
        self.slang_norm = slang_norm
        self.stem = stem
        self.stopwords = set(BASE_STOPWORDS) | (set(CHAIN_STOPWORDS) if chain_stop else set())
        self._memo = {}

    # tahap 1: pembersihan teks
    @staticmethod
    def clean(text):
        text = str(text).lower()
        text = URL_RE.sub(" ", text)
        text = SHORTCODE_RE.sub(" ", text)
        text = EMOJI_RE.sub(" ", text)
        text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    # tahap 2: tokenizing
    @staticmethod
    def tokenize(clean_text):
        return clean_text.split()

    def raw_tokens(self, text):
        """Hasil tahap pembersihan dan tokenizing saja (belum disaring)."""
        return self.tokenize(self.clean(text))

    # tahap 3 sampai 5: normalisasi, stopword, stemming (dimemo per token unik)
    def token_terms(self, tok):
        r = self._memo.get(tok)
        if r is None:
            r = self._compute(tok)
            self._memo[tok] = r
        return r

    def _compute(self, tok):
        parts = [tok]
        if self.slang_norm:
            t = REDUP_RE.sub(r"\1", tok)
            parts = SLANG.get(t, t).split()
        out = []
        for t in parts:
            if len(t) < 2 or t in self.stopwords:
                continue
            out.append(stem_word(t) if self.stem else t)
        return tuple(out)

    def terms_from_tokens(self, tokens):
        out = []
        for tok in tokens:
            out.extend(self.token_terms(tok))
        return out

    def process(self, text):
        return self.terms_from_tokens(self.raw_tokens(text))

    def explain(self, text):
        """Menampilkan hasil tiap tahap untuk keperluan demo di laporan."""
        c = self.clean(text)
        toks = self.tokenize(c)
        no_stop = [t for t in toks if len(t) >= 2 and t not in self.stopwords]
        return {
            "1_asli": text,
            "2_bersih": c,
            "3_token": toks,
            "4_tanpa_stopword": no_stop,
            "5_stem": self.process(text),
        }


# ----------------------------------------------------------------------------
# 2. Inverted index dengan TF-IDF cosine dan BM25
# ----------------------------------------------------------------------------
class InvertedIndex:
    """Inverted index: term -> (array id dokumen, array frekuensi term)."""

    def __init__(self, docs_terms):
        self.N = len(docs_terms)
        self.doc_len = np.array([len(t) for t in docs_terms], dtype=np.float64)
        self.avgdl = float(self.doc_len.mean()) if self.N else 0.0
        tmp = defaultdict(lambda: ([], []))
        for d, terms in enumerate(docs_terms):
            for term, tf in Counter(terms).items():
                p = tmp[term]
                p[0].append(d)
                p[1].append(tf)
        self.post_docs = {t: np.asarray(v[0], dtype=np.int32) for t, v in tmp.items()}
        self.post_tf = {t: np.asarray(v[1], dtype=np.float64) for t, v in tmp.items()}
        self.df = {t: len(v[0]) for t, v in tmp.items()}
        N = self.N
        # idf BM25 gaya Lucene (selalu positif) dan idf TF-IDF ala scikit-learn (smooth)
        self.idf_bm25 = {t: math.log(1 + (N - n + 0.5) / (n + 0.5)) for t, n in self.df.items()}
        self.idf_tfidf = {t: math.log((N + 1) / (n + 1)) + 1 for t, n in self.df.items()}
        sq = np.zeros(N)
        for t, docs in self.post_docs.items():
            w = (1 + np.log(self.post_tf[t])) * self.idf_tfidf[t]
            sq[docs] += w * w
        self.norm = np.sqrt(sq)
        self.norm[self.norm == 0] = 1.0

    @property
    def vocab_size(self):
        return len(self.df)

    def score_bm25(self, qterms, k1=1.5, b=0.75):
        s = np.zeros(self.N)
        for t in set(qterms):
            if t not in self.post_docs:
                continue
            d, tf = self.post_docs[t], self.post_tf[t]
            denom = tf + k1 * (1 - b + b * self.doc_len[d] / self.avgdl)
            s[d] += self.idf_bm25[t] * tf * (k1 + 1) / denom
        return s

    def score_tfidf(self, qterms):
        s = np.zeros(self.N)
        qn = 0.0
        for t, c in Counter(qterms).items():
            if t not in self.post_docs:
                continue
            idf = self.idf_tfidf[t]
            wq = (1 + math.log(c)) * idf
            qn += wq * wq
            d, tf = self.post_docs[t], self.post_tf[t]
            s[d] += wq * (1 + np.log(tf)) * idf
        if qn == 0:
            return s
        return s / (self.norm * math.sqrt(qn))


# ----------------------------------------------------------------------------
# 3. Mesin pencari dua field (judul dan isi)
# ----------------------------------------------------------------------------
class HuntFactsEngine:
    def __init__(self, docs, pre, title_index, content_index):
        self.docs = docs.reset_index(drop=True)
        self.pre = pre
        self.title = title_index
        self.content = content_index

    @classmethod
    def build(cls, docs, pre, raw_title, raw_content):
        t_terms = [pre.terms_from_tokens(x) for x in raw_title]
        c_terms = [pre.terms_from_tokens(x) for x in raw_content]
        return cls(docs, pre, InvertedIndex(t_terms), InvertedIndex(c_terms))

    @classmethod
    def from_docs(cls, docs, chain_stop=True, slang_norm=True):
        """Membangun engine langsung dari tabel dokumen (kolom title dan content_display)."""
        pre = Preprocessor(chain_stop=chain_stop, slang_norm=slang_norm)
        docs = docs.reset_index(drop=True)
        raw_t = [pre.raw_tokens(x) for x in docs["title"]]
        raw_c = [pre.raw_tokens(x) for x in docs["content_display"]]
        return cls.build(docs, pre, raw_t, raw_c)

    # ---- query ----
    def query_terms(self, text, reduce_k=None, reduce_by="idf"):
        terms = self.pre.process(text)
        if reduce_k:
            terms = self.reduce_terms(terms, reduce_k, reduce_by)
        return terms

    def reduce_terms(self, terms, k, by="idf"):
        """Memilih k term terpenting dari query panjang berdasarkan bobot IDF."""
        cnt = Counter(terms)
        known = [t for t in cnt if t in self.content.df]

        def weight(t):
            w = self.content.idf_bm25[t]
            return w * (1 + math.log(cnt[t])) if by == "tfidf" else w

        known.sort(key=weight, reverse=True)
        return known[:k]

    # ---- skor ----
    def score(self, qterms, method="bm25", weights=(1.0, 0.0), k1=1.5, b=0.75):
        wc, wt = weights
        total = np.zeros(self.content.N)
        for w, idx in ((wc, self.content), (wt, self.title)):
            if w == 0:
                continue
            if method == "bm25":
                total += w * idx.score_bm25(qterms, k1, b)
            elif method == "tfidf":
                total += w * idx.score_tfidf(qterms)
            else:
                raise ValueError("method harus 'bm25' atau 'tfidf'")
        return total

    def rank(self, qterms, method="bm25", top_k=100, **kw):
        s = self.score(qterms, method, **kw)
        order = np.argsort(-s, kind="stable")[:top_k]
        order = order[s[order] > 0]
        return order, s[order]

    # ---- hasil untuk antarmuka ----
    def highlight(self, text, qterms, width=None):
        """Mengembalikan HTML aman dengan kata yang cocok diberi <mark>."""
        qs = set(qterms)
        words = [m for m in re.finditer(r"\S+", text)]
        hits = []
        for m in words:
            toks = self.pre.raw_tokens(m.group())
            hits.append(any(t in qs for tok in toks for t in self.pre.token_terms(tok)))
        lo, hi = 0, len(words)
        if width and len(words) > width:
            cs = np.concatenate([[0], np.cumsum(hits)])
            gains = cs[width:] - cs[:-width]
            lo = int(np.argmax(gains))
            hi = lo + width
        parts = []
        for i in range(lo, hi):
            w = html.escape(words[i].group())
            parts.append(f"<mark>{w}</mark>" if hits[i] else w)
        out = " ".join(parts)
        return ("... " if lo > 0 else "") + out + (" ..." if hi < len(words) else "")

    def search(self, text, method="bm25", top_k=10, weights=(1.0, 0.0),
               reduce_k=None, snippet_words=45, k1=1.5, b=0.75):
        qterms = self.query_terms(text, reduce_k)
        order, scores = self.rank(qterms, method, top_k, weights=weights, k1=k1, b=b)
        rows = []
        for i, sc in zip(order, scores):
            r = self.docs.iloc[i]
            rows.append({
                "doc_id": int(r["doc_id"]),
                "title": r["title"],
                "score": float(sc),
                "link": r["link"],
                "title_html": self.highlight(r["title"], qterms),
                "snippet_html": self.highlight(r["content_display"], qterms, snippet_words),
            })
        return qterms, rows

    # ---- simpan dan muat ----
    def save(self, path):
        with open(path, "wb") as f:
            pickle.dump(self, f, protocol=pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load(path):
        with open(path, "rb") as f:
            return pickle.load(f)
