# ==============================================================================
# PRAKTIKUM AI APPLICATION FOR BUSINESS - SESI 4
# TOPIK: INTENT & ENTITIES CHATBOT BISNIS (ALUR PROFESIONAL & RESPON SEMANTIK)
# File: PraktikumS4.py (Siap Dijalankan di Google Colab)
# ==============================================================================

import json
import os
import random
import re
import sys
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Menjaga kompatibilitas output encoding di Windows Terminal & Google Colab
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# File penyimpanan memori intent di Google Colab / Local
JSON_FILE = os.path.join(os.path.dirname(__file__), 'kamus_intent.json') if '__file__' in globals() else 'kamus_intent.json'

# ==============================================================================
# 1. STRUKTUR DATASET KAMUS INTENT BISNIS (5 KATEGORI LENGKAP & ALUR NATURAL)
# ==============================================================================
default_dataset_intent = {
    "intents": [
        {
            "tag": "sapaan",
            "patterns": [
                "halo", "hai", "selamat pagi", "permisi admin", "halo min",
                "pagi", "assalamualaikum", "halo kak", "hai admin",
                "aku mau minta tolong", "bisa tolong saya", "mau tanya dong",
                "bisa bantu saya ga", "butuh bantuan", "mau tanya min",
                "tolong bantu", "bisakah kamu bantu aku", "bisa bantu aku",
                "mau nanya", "permisi", "help"
            ],
            "responses": [
                "Halo Kak! Tentu, kami siap bantu dengan senang hati. Mau tanya info katalog produk, harga, alamat toko, atau kendala pesanan Kak?",
                "Hai Kak! Selamat datang di Toko Sepatu Official. Ada yang bisa kami bantu seputar produk atau pesanan Kakak hari ini?"
            ]
        },
        {
            "tag": "tanya_produk",
            "patterns": [
                "apa saja produk unggulan", "jual apa saja", "lihat katalog produk",
                "ready produk apa", "ada sepatu apa", "katalog sepatu", "daftar barang",
                "jual apa", "stok barang", "apakah ada sepatu sneaker", "rekomendasi produk",
                "sepatu running", "sneaker casual", "produk sepatu", "ada model apa aja"
            ],
            "responses": [
                "Kami menjual berbagai pilihan Sepatu Sneaker, Sepatu Running, dan Aksesoris Original dengan kualitas terbaik Kak!",
                "Katalog produk kami mencakup Sneaker Casual, Running Shoes dengan bantalan empuk, dan Kaos Kaki Premium Kak!"
            ]
        },
        {
            "tag": "cek_lokasi",
            "patterns": [
                "dimana alamat toko", "lokasi toko dimana", "bisa datang langsung ke toko",
                "alamat offline", "toko di mana", "cabang bandung", "dimana sih toko kalian",
                "posisi toko di mana", "buka jam berapa", "jam operasional", "alamat toko"
            ],
            "responses": [
                "Toko offline kami beralamat di Jl. Soekarno-Hatta No. 456, Bandung. Buka setiap hari pukul 09.00 - 21.00 WIB.",
                "Silakan mampir langsung ke outlet kami di Jl. Soekarno-Hatta No. 456, Bandung untuk fitting ukuran ya Kak!"
            ]
        },
        {
            "tag": "komplain_pesanan",
            "patterns": [
                "barang belum sampai", "pesanan rusak", "paket nyangkut", "retur barang",
                "salah kirim barang", "produk jelek", "sangat jelek", "jelek", "buruk",
                "kualitas buruk", "kecewa", "sangat kecewa", "parah", "tidak sesuai",
                "cacat", "rusak", "mengecewakan", "kualitas jelek banget bikin kecewa",
                "kecewa banget", "komplain"
            ],
            "responses": [
                "Mohon maaf sebesar-besarnya atas ketidaknyamanan Kakak. Produk kami bergaransi 100% Ganti Baru atau Uang Kembali. Silakan infokan nomor pesanan dan foto kendala produk agar tim kami proses penukaran segera ya Kak.",
                "Kami sangat menyesal mendengar kendala tersebut Kak. Kepuasan Kakak adalah prioritas kami. Mohon kirimkan Nomor Resi dan foto bukti kendala untuk kami ganti dengan produk baru hari ini juga."
            ]
        },
        {
            "tag": "tanya_harga",
            "patterns": [
                "berapa harganya", "pricelist sepatu", "harga produk ini berapa",
                "ada diskon ga", "berapaan min", "daftar harga", "potongan harga",
                "harganya berapaan kak", "ada promo apa", "harga sepatu"
            ],
            "responses": [
                "Harga sepatu kami mulai dari Rp 250.000 hingga Rp 750.000 tergantung model dan brand Kak. Saat ini ada diskon 10% untuk seri Running!",
                "Untuk pricelist lengkap mulai dari Rp 250.000 Kak. Kakak tertarik dengan model Sneaker Casual atau Sepatu Running?"
            ]
        }
    ]
}

# ==============================================================================
# 2. DEFINISI ENTITAS KHUSUS (ENTITIES) - POIN 4 MODUL
# ==============================================================================
ENTITAS_BISNIS = {
    "PRODUK": ["sneaker", "running", "casual", "aksesoris", "kaos kaki"],
    "METODE_BAYAR": ["transfer bca", "qris", "cod", "mandiri", "gopay"]
}

def ekstrak_entitas(pesan):
    """Mendeteksi entitas khusus (produk/metode bayar) di dalam pesan pelanggan."""
    ditemukan = {}
    pesan_lower = pesan.lower()
    for kategori, daftar_entitas in ENTITAS_BISNIS.items():
        for item in daftar_entitas:
            if item in pesan_lower:
                ditemukan[kategori] = item.upper()
                break
    return ditemukan


# ==============================================================================
# 3. FUNGSI LOAD & SAVE MEMORI JSON
# ==============================================================================
def load_kamus_intent():
    """Membaca memori intent dari file JSON, jika belum ada buat dari default."""
    if os.path.exists(JSON_FILE):
        try:
            with open(JSON_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return default_dataset_intent
    else:
        simpan_kamus_intent(default_dataset_intent)
        return default_dataset_intent

def simpan_kamus_intent(dataset):
    """Menyimpan seluruh memori intent ke file JSON."""
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=4, ensure_ascii=False)


# ==============================================================================
# 4. ENGINE AI KEMIRIPAN SEMANTIK (TF-IDF & COSINE SIMILARITY)
# ==============================================================================
class IntentSimilarityEngine:
    """
    Engine AI cerdas berbasis TF-IDF & Cosine Similarity:
    Memahami variasi kalimat pelanggan secara otomatis berdasarkan kemiripan makna.
    """
    def __init__(self, dataset):
        self.dataset = dataset
        self.build_engine()

    def build_engine(self):
        self.corpus_patterns = []
        self.corpus_tags = []
        for item in self.dataset["intents"]:
            for pat in item["patterns"]:
                self.corpus_patterns.append(pat.lower().strip())
                self.corpus_tags.append(item["tag"])

        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2))
        self.pattern_vectors = self.vectorizer.fit_transform(self.corpus_patterns)

    def predict(self, user_message, threshold=0.22):
        clean_msg = user_message.lower().strip()
        if not clean_msg:
            return "unknown", 0.0, None

        # 1. Cek Exact Match langsung
        for item in self.dataset["intents"]:
            for pat in item["patterns"]:
                if pat.lower().strip() == clean_msg:
                    return item["tag"], 1.0, random.choice(item["responses"])

        # 2. Hitung Cosine Similarity berbasis TF-IDF
        user_vec = self.vectorizer.transform([clean_msg])
        sims = cosine_similarity(user_vec, self.pattern_vectors).flatten()
        best_idx = int(np.argmax(sims))
        best_score = float(sims[best_idx])
        best_tag = self.corpus_tags[best_idx]

        if best_score >= threshold:
            for item in self.dataset["intents"]:
                if item["tag"] == best_tag:
                    return best_tag, best_score, random.choice(item["responses"])

        # 3. Respon Fallback Cerdas & Sopan jika di luar topik toko
        fallback_msg = (
            "Maaf Kak, toko kami khusus menyediakan koleksi sepatu dan aksesoris olahraga original. "
            "Ada yang bisa kami bantu seputar katalog produk, cek harga, lokasi toko, atau kendala pesanan Kak?"
        )
        return "unknown", best_score, fallback_msg


# ==============================================================================
# 5. MODE LIVE CHAT CUSTOMER SERVICE (BERSIH, SEJAJAR, & PROFESIONAL)
# ==============================================================================
def jalankan_chatbot():
    dataset = load_kamus_intent()
    engine = IntentSimilarityEngine(dataset)

    print("=" * 70)
    print("           TOKO SEPATU OFFICIAL - CUSTOMER SERVICE VIRTUAL")
    print("=" * 70)
    print("CS   : Halo Kak! Selamat datang di Toko Sepatu Official.")
    print("       Ada yang bisa kami bantu? (Katalog / Cek Harga / Lokasi / Komplain)")
    print("       (Ketik 'exit' kapan saja untuk mengakhiri chat)")
    print("-" * 70)

    while True:
        try:
            pesan = input("\nAnda : ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nCS   : Terima kasih telah menghubungi Toko Sepatu Official. Sampai jumpa lagi Kak!")
            break

        if not pesan:
            continue

        if pesan.lower() in ['exit', 'keluar', 'quit', 'selesai', 'bye']:
            print("CS   : Terima kasih telah menghubungi Toko Sepatu Official. Semoga harimu menyenangkan Kak!")
            print("=" * 70)
            break

        # A. Prediksi Intent & Respon CS
        tag, skor, balasan = engine.predict(pesan)

        # B. Tampilkan Respon Rapi Sejajar
        print(f"CS   : {balasan}")


# ==============================================================================
# ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    jalankan_chatbot()
