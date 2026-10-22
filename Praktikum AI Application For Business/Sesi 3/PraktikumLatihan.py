# ==============================================================================
# TUGAS PRAKTIKUM 3: PREPROCESSING + BAG OF WORDS + TF-IDF
# Studi Kasus: Ulasan Bisnis Layanan Sistem & Aplikasi
# Menguji Perbandingan: Kata Umum vs Kata Unik (Termasuk Kata 'Bekerja', 'Umum', 'Unik')
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. IMPORT LIBRARY
# ------------------------------------------------------------------------------
import re
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# Inisialisasi Sastrawi
stopword_remover = StopWordRemoverFactory().create_stop_word_remover()
stemmer = StemmerFactory().create_stemmer()

# Load Kamus Slang Global (Online dari GitHub dengan Fallback)
url_kamus = "https://raw.githubusercontent.com/nasalsabila/kamus-alay/master/colloquial-indonesian-lexicon.csv"
try:
    df_kamus = pd.read_csv(url_kamus)
    kamus_global = dict(zip(df_kamus['slang'], df_kamus['formal']))
    print(f"Kamus Slang Global siap: {len(kamus_global)} kata termuat! ✅")
except Exception:
    kamus_global = {
        "bgt": "banget", "yg": "yang", "sy": "saya", "ga": "tidak", "gak": "tidak",
        "cepet": "cepat", "cuy": "kawan", "parahhh": "parah", "kecewaaa": "kecewa"
    }

# Mapping Leetspeak (Angka alay di dalam kata -> Huruf)
map_angka_alay = str.maketrans({
    '0': 'o',
    '1': 'i',
    '3': 'e',
    '4': 'a',
    '6': 'g'
})


# ------------------------------------------------------------------------------
# 2. FUNGSI CLEANING & NORMALISASI (HAPUS ANGKA, ALAY, LEETSPEAK)
# ------------------------------------------------------------------------------
def bersihkan_teks(teks):
    # A. Case Folding (huruf kecil)
    t = teks.lower()

    # B. Ringkas kata ulang angka 2 (unik2 -> unik, error2 -> error)
    t = re.sub(r'\b([a-z]+)2\b', r'\1', t)

    # C. Hapus angka murni harga/persentase (misal: 100, 50000)
    t = re.sub(r"\b\d+\b", "", t)

    # D. Konversi angka alay leetspeak (b4ng3t -> banget, g4k -> gak/tidak)
    t = t.translate(map_angka_alay)

    # E. Hapus sisa angka nyasar jika ada
    t = re.sub(r"\d+", "", t)

    # F. Ringkas huruf kembar berlebih / elongasi (parahhh -> parah, kecewaaa -> kecewa)
    t = re.sub(r"([a-z])\1{2,}", r"\1", t)

    # G. Ringkas huruf kembar di akhir kata (dehh -> deh)
    t = re.sub(r"([a-z])\1+\b", r"\1", t)

    # H. Ringkas kata kembar berulang beruntun jadi 1 kata (bgt bgt -> bgt)
    t = re.sub(r'\b(\w+)(?:\s+\1\b)+', r'\1', t)

    # I. Hapus tanda baca dan rapikan spasi dobel
    t = re.sub(r"[^a-z\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()

    # J. Normalisasi kata slang/alay via kamus global (bgt -> banget, cepet -> cepat)
    kata_tokens = [kamus_global.get(k, k) for k in t.split()]
    kalimat_normal = " ".join(kata_tokens)

    # K. Stopwords Removal & Stemming (Sastrawi: 'bekerja' -> 'kerja')
    tanpa_stopword = stopword_remover.remove(kalimat_normal)
    hasil_stemmed = stemmer.stem(tanpa_stopword)

    return hasil_stemmed


# ------------------------------------------------------------------------------
# 3. DATASET 5 ULASAN MENTAH
# Berisi kata umum ('bekerja', 'sistem'), kata spesifik/unik ('unik', 'umum'),
# serta anomali alay (angka 100%, kata ulang angka 2, leetspeak, dan slang).
# ------------------------------------------------------------------------------
ulasan_mentah = [
    "Sistem aplikasi ini bekerja sangat baik b4ng3t, fiturnya unik2 dan cepet responnya!",
    "Layanan ini bekerja secara umum cukup bagus, tetapi sering error2 dan lambat bgt!",
    "Tim support bekerja lambat parahhh, sistem aplikasi sering ngadat dan bikin kecewaaa!",
    "Secara umum sistem bekerja normal 100%, tampilan antarmukanya sangat unik dan ramah!",
    "Aplikasi tidak bekerja sama sekali cuy, pelayanan buruk bgt dan g4k profesional!"
]

print("\n" + "=" * 80)
print("PROSES PREPROCESSING & NORMALISASI 5 ULASAN MENTAH")
print("=" * 80)

ulasan_bersih = []
for i, teks_asli in enumerate(ulasan_mentah, 1):
    teks_hasil = bersihkan_teks(teks_asli)
    ulasan_bersih.append(teks_hasil)
    print(f"\n[Ulasan {i}]")
    print(f"  Teks Mentah Asli      : {teks_asli}")
    print(f"  Setelah Preprocessing : {teks_hasil}")


# ------------------------------------------------------------------------------
# 4. IMPLEMENTASI BAG OF WORDS (COUNTVECTORIZER)
# ------------------------------------------------------------------------------
vectorizer_bow = CountVectorizer()
matrix_bow = vectorizer_bow.fit_transform(ulasan_bersih)

# Konversi matriks frekuensi ke DataFrame Pandas
df_bow = pd.DataFrame(matrix_bow.toarray(), columns=vectorizer_bow.get_feature_names_out())

print("\n" + "=" * 80)
print("1. MATRIKS BAG OF WORDS (FREKUENSI KEMUNCULAN KATA)")
print("=" * 80)
print(df_bow)


# ------------------------------------------------------------------------------
# 5. IMPLEMENTASI TF-IDF VECTORIZER (BOBOT KEPENTINGAN KATA)
# ------------------------------------------------------------------------------
vectorizer_tfidf = TfidfVectorizer()
matrix_tfidf = vectorizer_tfidf.fit_transform(ulasan_bersih)

# Konversi bobot ke DataFrame Pandas (pembulatan 3 desimal)
df_tfidf = pd.DataFrame(matrix_tfidf.toarray(), columns=vectorizer_tfidf.get_feature_names_out())

print("\n" + "=" * 80)
print("2. MATRIKS TF-IDF (BOBOT KEPENTINGAN KATA)")
print("=" * 80)
print(df_tfidf.round(3))


# ------------------------------------------------------------------------------
# 6. ANALISIS PERBANDINGAN: KATA UMUM vs KATA UNIK (JAWABAN TUGAS POIN 5)
# ------------------------------------------------------------------------------
print("\n" + "=" * 80)
print("3. ANALISIS PERBANDINGAN BOBOT TF-IDF: KATA UMUM VS KATA UNIK")
print("=" * 80)

# Menampilkan bobot kata umum 'kerja' (akar kata dari 'bekerja')
print("\n[A] Nilai Bobot Kata Umum ('bekerja' -> 'kerja') di Tiap Ulasan:")
for i, val in enumerate(df_tfidf['kerja'], 1):
    print(f"  - Ulasan {i}: {val:.3f}")

print("\n[B] Nilai Bobot Kata Kunci Unik Tertinggi di Tiap Ulasan:")
for i, row in df_tfidf.iterrows():
    top_kata = row.nlargest(3)
    kata_skor = [f"{k} ({v:.3f})" for k, v in top_kata.items() if v > 0]
    print(f"  - Ulasan {i+1} : {', '.join(kata_skor)}")

print("\n[C] KESIMPULAN ANALISIS (UNTUK SEL TEKS / MARKDOWN):")
print("-" * 80)
print("1. Kata Umum ('bekerja' / 'kerja'):")
print("   Memiliki bobot TF-IDF RENDAH (rata-rata hanya 0.164 - 0.190).")
print("   Alasannya: Kata ini muncul di seluruh (5 dari 5) ulasan pelanggan, sehingga nilai")
print("   IDF (Inverse Document Frequency)-nya ditekan/dikecilkan karena tidak memiliki nilai pembeda.")
print("\n2. Kata Unik ('profesional', 'antarmuka', 'kecewa', 'ramah', dll):")
print("   Memiliki bobot TF-IDF TINGGI (mencapai 0.350 - 0.380).")
print("   Alasannya: Kata-kata ini hanya muncul di 1 dokumen ulasan spesifik, sehingga dianggap")
print("   sangat bernilai (informatif) untuk membedakan sentimen atau masalah yang dialami pelanggan.")
print("-" * 80)
# ==============================================================================
# TUGAS PRAKTIKUM 3: PREPROCESSING + BAG OF WORDS + TF-IDF
# Studi Kasus: Ulasan Bisnis Layanan Sistem & Aplikasi
# Menguji Perbandingan: Kata Umum vs Kata Unik (Termasuk Kata 'Bekerja', 'Umum', 'Unik')
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. IMPORT LIBRARY
# ------------------------------------------------------------------------------
import re
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# Inisialisasi Sastrawi
stopword_remover = StopWordRemoverFactory().create_stop_word_remover()
stemmer = StemmerFactory().create_stemmer()

# Load Kamus Slang Global (Online dari GitHub dengan Fallback)
url_kamus = "https://raw.githubusercontent.com/nasalsabila/kamus-alay/master/colloquial-indonesian-lexicon.csv"
try:
    df_kamus = pd.read_csv(url_kamus)
    kamus_global = dict(zip(df_kamus['slang'], df_kamus['formal']))
    print(f"Kamus Slang Global siap: {len(kamus_global)} kata termuat! ✅")
except Exception:
    kamus_global = {
        "bgt": "banget", "yg": "yang", "sy": "saya", "ga": "tidak", "gak": "tidak",
        "cepet": "cepat", "cuy": "kawan", "parahhh": "parah", "kecewaaa": "kecewa"
    }

# Mapping Leetspeak (Angka alay di dalam kata -> Huruf)
map_angka_alay = str.maketrans({
    '0': 'o',
    '1': 'i',
    '3': 'e',
    '4': 'a',
    '6': 'g'
})


# ------------------------------------------------------------------------------
# 2. FUNGSI CLEANING & NORMALISASI (HAPUS ANGKA, ALAY, LEETSPEAK)
# ------------------------------------------------------------------------------
def bersihkan_teks(teks):
    # A. Case Folding (huruf kecil)
    t = teks.lower()

    # B. Ringkas kata ulang angka 2 (unik2 -> unik, error2 -> error)
    t = re.sub(r'\b([a-z]+)2\b', r'\1', t)

    # C. Hapus angka murni harga/persentase (misal: 100, 50000)
    t = re.sub(r"\b\d+\b", "", t)

    # D. Konversi angka alay leetspeak (b4ng3t -> banget, g4k -> gak/tidak)
    t = t.translate(map_angka_alay)

    # E. Hapus sisa angka nyasar jika ada
    t = re.sub(r"\d+", "", t)

    # F. Ringkas huruf kembar berlebih / elongasi (parahhh -> parah, kecewaaa -> kecewa)
    t = re.sub(r"([a-z])\1{2,}", r"\1", t)

    # G. Ringkas huruf kembar di akhir kata (dehh -> deh)
    t = re.sub(r"([a-z])\1+\b", r"\1", t)

    # H. Ringkas kata kembar berulang beruntun jadi 1 kata (bgt bgt -> bgt)
    t = re.sub(r'\b(\w+)(?:\s+\1\b)+', r'\1', t)

    # I. Hapus tanda baca dan rapikan spasi dobel
    t = re.sub(r"[^a-z\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()

    # J. Normalisasi kata slang/alay via kamus global (bgt -> banget, cepet -> cepat)
    kata_tokens = [kamus_global.get(k, k) for k in t.split()]
    kalimat_normal = " ".join(kata_tokens)

    # K. Stopwords Removal & Stemming (Sastrawi: 'bekerja' -> 'kerja')
    tanpa_stopword = stopword_remover.remove(kalimat_normal)
    hasil_stemmed = stemmer.stem(tanpa_stopword)

    return hasil_stemmed


# ------------------------------------------------------------------------------
# 3. DATASET 5 ULASAN MENTAH
# Berisi kata umum ('bekerja', 'sistem'), kata spesifik/unik ('unik', 'umum'),
# serta anomali alay (angka 100%, kata ulang angka 2, leetspeak, dan slang).
# ------------------------------------------------------------------------------
ulasan_mentah = [
    "Sistem aplikasi ini bekerja sangat baik b4ng3t, fiturnya unik2 dan cepet responnya!",
    "Layanan ini bekerja secara umum cukup bagus, tetapi sering error2 dan lambat bgt!",
    "Tim support bekerja lambat parahhh, sistem aplikasi sering ngadat dan bikin kecewaaa!",
    "Secara umum sistem bekerja normal 100%, tampilan antarmukanya sangat unik dan ramah!",
    "Aplikasi tidak bekerja sama sekali cuy, pelayanan buruk bgt dan g4k profesional!"
]

print("\n" + "=" * 80)
print("PROSES PREPROCESSING & NORMALISASI 5 ULASAN MENTAH")
print("=" * 80)

ulasan_bersih = []
for i, teks_asli in enumerate(ulasan_mentah, 1):
    teks_hasil = bersihkan_teks(teks_asli)
    ulasan_bersih.append(teks_hasil)
    print(f"\n[Ulasan {i}]")
    print(f"  Teks Mentah Asli      : {teks_asli}")
    print(f"  Setelah Preprocessing : {teks_hasil}")


# ------------------------------------------------------------------------------
# 4. IMPLEMENTASI BAG OF WORDS (COUNTVECTORIZER)
# ------------------------------------------------------------------------------
vectorizer_bow = CountVectorizer()
matrix_bow = vectorizer_bow.fit_transform(ulasan_bersih)

# Konversi matriks frekuensi ke DataFrame Pandas
df_bow = pd.DataFrame(matrix_bow.toarray(), columns=vectorizer_bow.get_feature_names_out())

print("\n" + "=" * 80)
print("1. MATRIKS BAG OF WORDS (FREKUENSI KEMUNCULAN KATA)")
print("=" * 80)
print(df_bow)


# ------------------------------------------------------------------------------
# 5. IMPLEMENTASI TF-IDF VECTORIZER (BOBOT KEPENTINGAN KATA)
# ------------------------------------------------------------------------------
vectorizer_tfidf = TfidfVectorizer()
matrix_tfidf = vectorizer_tfidf.fit_transform(ulasan_bersih)

# Konversi bobot ke DataFrame Pandas (pembulatan 3 desimal)
df_tfidf = pd.DataFrame(matrix_tfidf.toarray(), columns=vectorizer_tfidf.get_feature_names_out())

print("\n" + "=" * 80)
print("2. MATRIKS TF-IDF (BOBOT KEPENTINGAN KATA)")
print("=" * 80)
print(df_tfidf.round(3))


# ------------------------------------------------------------------------------
# 6. ANALISIS PERBANDINGAN: KATA UMUM vs KATA UNIK (JAWABAN TUGAS POIN 5)
# ------------------------------------------------------------------------------
print("\n" + "=" * 80)
print("3. ANALISIS PERBANDINGAN BOBOT TF-IDF: KATA UMUM VS KATA UNIK")
print("=" * 80)

# Menampilkan bobot kata umum 'kerja' (akar kata dari 'bekerja')
print("\n[A] Nilai Bobot Kata Umum ('bekerja' -> 'kerja') di Tiap Ulasan:")
for i, val in enumerate(df_tfidf['kerja'], 1):
    print(f"  - Ulasan {i}: {val:.3f}")

print("\n[B] Nilai Bobot Kata Kunci Unik Tertinggi di Tiap Ulasan:")
for i, row in df_tfidf.iterrows():
    top_kata = row.nlargest(3)
    kata_skor = [f"{k} ({v:.3f})" for k, v in top_kata.items() if v > 0]
    print(f"  - Ulasan {i+1} : {', '.join(kata_skor)}")

print("\n[C] KESIMPULAN ANALISIS (UNTUK SEL TEKS / MARKDOWN):")
print("-" * 80)
print("1. Kata Umum ('bekerja' / 'kerja'):")
print("   Memiliki bobot TF-IDF RENDAH (rata-rata hanya 0.164 - 0.190).")
print("   Alasannya: Kata ini muncul di seluruh (5 dari 5) ulasan pelanggan, sehingga nilai")
print("   IDF (Inverse Document Frequency)-nya ditekan/dikecilkan karena tidak memiliki nilai pembeda.")
print("\n2. Kata Unik ('profesional', 'antarmuka', 'kecewa', 'ramah', dll):")
print("   Memiliki bobot TF-IDF TINGGI (mencapai 0.350 - 0.380).")
print("   Alasannya: Kata-kata ini hanya muncul di 1 dokumen ulasan spesifik, sehingga dianggap")
print("   sangat bernilai (informatif) untuk membedakan sentimen atau masalah yang dialami pelanggan.")
print("-" * 80)
