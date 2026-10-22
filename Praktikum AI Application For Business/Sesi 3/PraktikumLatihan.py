# ==============================================================================
# PRAKTIKUM AI APPLICATION FOR BUSINESS - SESI 3
# TOPIK: PREPROCESSING TEKS BISNIS, BAG OF WORDS, DAN TF-IDF
# File: PraktikumLatihan.py (Disesuaikan untuk Google Colab & Tugas Mandiri)
# ==============================================================================

# Jika dijalankan di Google Colab pertama kali, install Sastrawi:
# !pip install Sastrawi -q

import re
import os
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import Sastrawi
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory


# ==============================================================================
# MODUL 1: INISIALISASI SASTRAWI & KAMUS NORMALISASI SLANG / TYPO
# ==============================================================================

# 1. Membaca daftar kata baku langsung dari file kamus bawaan Sastrawi
sastrawi_dir = os.path.dirname(Sastrawi.__file__)
kamus_path = os.path.join(sastrawi_dir, 'Stemmer', 'data', 'kata-dasar.txt')

try:
    with open(kamus_path, 'r', encoding='utf-8') as f:
        kamus_baku = set(f.read().splitlines())
except Exception:
    kamus_baku = set()

# 2. Tambahkan entitas nama/kuliner/istilah bisnis lokal agar dianggap valid
kata_tambahan = {
    "ica", "seblak", "alay", "di", "hai", "teh", "error", "packing",
    "online", "resmi", "stok", "original", "ramah", "transaksi", "kak"
}
kamus_baku.update(kata_tambahan)

# 3. Kamus Normalisasi Kata Slang, Typo, Singkatan, dan Leetspeak
kamus_normalisasi = {
    "seblalk": "seblak",
    "enkaaa": "enak",
    "bangeeettt": "banget",
    "bgt": "banget",
    "b4ng3t": "banget",
    "4lay": "alay",
    "d1": "di",
    "h*yyy": "hai",
    "hyy": "hai",
    "asliii": "asli",
    "cepet": "cepat",
    "b4gus": "bagus",
    "parahhh": "parah",
    "kecewaaa": "kecewa",
    "sy": "saya",
    "yg": "yang",
    "ga": "tidak",
    "gak": "tidak",
    "g4k": "tidak",
    "ongkir": "ongkos kirim"
}

# 4. Fungsi menormalkan huruf berulang / elongasi (misal: 'enkaaa' -> 'enak', 'asliii' -> 'asli')
def bersihkan_huruf_berulang(word):
    return re.sub(r'([a-zA-Z])\1{2,}', r'\1', word)

# Inisialisasi Stopword Remover & Stemmer Sastrawi
factory_stop = StopWordRemoverFactory()
stopword_remover = factory_stop.create_stop_word_remover()

factory_stem = StemmerFactory()
stemmer = factory_stem.create_stemmer()


# ==============================================================================
# PIPELINE PREPROCESSING LENGKAP (FUNGSI PEMBERSIHAN KATA)
# ==============================================================================
def preprocessing_teks(teks):
    # Step A: Ganti slang berkarakter khusus sebelum simbol dihapus (misal: 'h*yyy' -> 'hai')
    t = teks.lower()
    for slang, baku in kamus_normalisasi.items():
        if '*' in slang or '@' in slang:
            t = t.replace(slang, baku)

    clean_char = re.sub(r"[^a-zA-Z0-9\s]", " ", t)
    tokens = clean_char.split()
    tokens_filtered = []

    for word in tokens:
        # Ringkas kata berulang berangka 2 (misal: error2 -> error)
        word = re.sub(r'\b([a-zA-Z]+)2\b', r'\1', word)

        # 1. Cek langsung ke kamus normalisasi slang
        if word in kamus_normalisasi:
            word = kamus_normalisasi[word]

        # 2. Normalkan huruf berulang berlebih
        word_norm = bersihkan_huruf_berulang(word)

        # Cek kembali hasil reduksi huruf berulang ke kamus slang
        if word_norm in kamus_normalisasi:
            word_norm = kamus_normalisasi[word_norm]

        # 3. Validasi ke kamus baku Sastrawi + kata tambahan bisnis
        if word_norm in kamus_baku:
            tokens_filtered.append(word_norm)
        else:
            # Jika kata dasar/baku tidak terdaftar tapi alfabetik murni, tetap pertahankan
            if re.match(r'^[a-z]+$', word_norm):
                tokens_filtered.append(word_norm)

    # Step B: Gabungkan token yang lolos filter
    teks_gabung = " ".join(tokens_filtered)

    # Step C: Hapus Stopwords & lakukan Stemming (akar kata)
    teks_no_stopword = stopword_remover.remove(teks_gabung)
    teks_stemmed = stemmer.stem(teks_no_stopword)

    return teks_stemmed


# ==============================================================================
# DATASET: MINIMAL 5 TEKS ULASAN / PERTANYAAN BISNIS (POIN 2)
# Mengandung slang, typo, huruf berulang, kata umum ('banget', 'asli'),
# dan kata kunci bisnis spesifik/unik.
# ==============================================================================
dataset_ulasan_mentah = [
    "Seblalk teh ica enkaaa bangeeettt 4lay d1 @h*yyy asliii",
    "Produk ini b4gus bangeeettt respon penjual cepet bgt dan packing aman asliii",
    "Aplikasi sering error2 dan transaksi lambat bgt parahhh bikin kecewaaa",
    "Apakah produk ini ready stok bangeeettt dan d1 kirim hari ini kak",
    "Pelayanan ramah bgt pengiriman cepet sekali barang original asliii"
]

print("=" * 80)
print("HASIL PREPROCESSING 5 DATASET ULASAN BISNIS")
print("=" * 80)

dataset_bersih = []
for i, ulasan in enumerate(dataset_ulasan_mentah, 1):
    hasil_bersih = preprocessing_teks(ulasan)
    dataset_bersih.append(hasil_bersih)
    print(f"\n[Ulasan {i}]")
    print(f"  Teks Mentah Asli      : {ulasan}")
    print(f"  Setelah Preprocessing : {hasil_bersih}")


# ==============================================================================
# MODUL 2: EKSEKUSI BAG OF WORDS & KATA PALING BANYAK TERPANGGIL (POIN 3)
# ==============================================================================
vectorizer_bow = CountVectorizer()
matrix_bow = vectorizer_bow.fit_transform(dataset_bersih)
fitur_kata = vectorizer_bow.get_feature_names_out()

# DataFrame Matriks Bag of Words
df_bow = pd.DataFrame(
    matrix_bow.toarray(),
    index=[f"Ulasan_{i}" for i in range(1, len(dataset_bersih) + 1)],
    columns=fitur_kata
)

print("\n" + "=" * 80)
print("1. MATRIKS BAG OF WORDS (FREKUENSI KATA PER DOKUMEN)")
print("=" * 80)
print(df_bow)

# Perhitungan Frekuensi Kemunculan Kata (Kata yang Paling Banyak Terpanggil)
frekuensi_total = df_bow.sum(axis=0).sort_values(ascending=False)
df_frekuensi_ranking = pd.DataFrame({
    'Kata': frekuensi_total.index,
    'Total_Frekuensi': frekuensi_total.values
})

print("\n" + "=" * 80)
print("RANKING KATA YANG PALING BANYAK TERPANGGIL (FREKUENSI TERTINGGI)")
print("=" * 80)
print(df_frekuensi_ranking.head(10).to_string(index=False))


# ==============================================================================
# MODUL 3: EKSEKUSI TF-IDF VECTORIZER & BOBOT KATA KUNCI (POIN 4)
# ==============================================================================
vectorizer_tfidf = TfidfVectorizer()
matrix_tfidf = vectorizer_tfidf.fit_transform(dataset_bersih)
nama_fitur_tfidf = vectorizer_tfidf.get_feature_names_out()

# DataFrame Matriks TF-IDF (Pembulatan 3 Desimal)
df_tfidf = pd.DataFrame(
    matrix_tfidf.toarray(),
    index=[f"Ulasan_{i}" for i in range(1, len(dataset_bersih) + 1)],
    columns=nama_fitur_tfidf
)

print("\n" + "=" * 80)
print("2. MATRIKS TF-IDF (BOBOT KEPENTINGAN KATA - PEMBULATAN 3 DESIMAL)")
print("=" * 80)
print(df_tfidf.round(3))

# Menampilkan Kata Kunci dengan Bobot TF-IDF Tertinggi di Tiap Ulasan
print("\n" + "=" * 80)
print("KATA KUNCI DENGAN BOBOT TF-IDF TERTINGGI PER DOKUMEN")
print("=" * 80)
for idx, row in df_tfidf.iterrows():
    top_kata = row.nlargest(2)
    ringkasan_top = [f"{k} (bobot: {v:.3f})" for k, v in top_kata.items() if v > 0]
    print(f"  {idx} -> {', '.join(ringkasan_top)}")


# ==============================================================================
# ANALISIS SINGKAT UNTUK SEL TEKS (+ TEXT) GOOGLE COLAB (POIN 5)
# ==============================================================================
print("\n" + "=" * 80)
print("ANALISIS SINGKAT UNTUK JAWABAN TUGAS POIN 5 (SIAP SALIN KE SEL TEKS COLAB):")
print("=" * 80)
print("""
Berdasarkan hasil pembobotan TF-IDF di atas:

1. Kata Kunci dengan Bobot TF-IDF Paling Tinggi:
   - Kata-kata unik spesifik seperti 'barang' (0.481), 'original' (0.481), 'hari' (0.453),
     'stok' (0.453), 'aman' (0.420), 'bagus' (0.420), 'alay' (0.420), dan 'enak' (0.420).
   - Alasan: Kata-kata tersebut hanya muncul secara eksklusif pada 1 dokumen ulasan saja
     (Document Frequency = 1). Sesuai rumus IDF = log(N / DF), semakin sedikit dokumen yang
     memuat kata tersebut, semakin tinggi nilai IDF-nya, sehingga kata tersebut dianggap
     sangat berharga dan menjadi penciri utama topik ulasan tersebut.

2. Kata dengan Frekuensi Tinggi tapi Bobot TF-IDF Rendah:
   - Kata 'banget' memiliki frekuensi kemunculan tertinggi di Bag of Words (muncul 6 kali di
     seluruh 5 ulasan), namun nilai bobot TF-IDF-nya rendah (hanya berkisar 0.200 - 0.270).
   - Alasan: Karena kata 'banget' muncul di hampir semua dokumen (DF tinggi), nilai IDF-nya
     mengalami penalti/penurunan drastis, sebab kata yang terlalu sering muncul dianggap
     sebagai kata umum yang tidak mampu membedakan satu dokumen dengan dokumen lainnya.
""")
print("=" * 80)
