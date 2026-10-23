# ==============================================================================
# PRAKTIKUM AI APPLICATION FOR BUSINESS - SESI 4
# TOPIK: INTENT & ENTITIES DENGAN ENGINE TF-IDF COSINE SIMILARITY (AI SEMANTIK)
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
# 1. STRUKTUR DATASET AWAL (5 KATEGORI INTENT BISNIS LENGKAP)
# ==============================================================================
default_dataset_intent = {
    "intents": [
        {
            "tag": "sapaan",
            "patterns": [
                "halo", "hai", "selamat pagi", "permisi admin", "halo min",
                "pagi", "assalamualaikum", "halo kak", "hai admin",
                "aku mau minta tolong", "bisa tolong saya", "mau tanya dong",
                "bisa bantu saya ga", "butuh bantuan", "mau tanya min", "tolong bantu"
            ],
            "responses": [
                "Halo Kak! Dengan senang hati kami siap membantu. Ada yang bisa kami bantu hari ini?",
                "Hai! Selamat datang di Toko Kami. Silakan tanyakan apa saja, kami siap melayani Kakak."
            ]
        },
        {
            "tag": "tanya_produk",
            "patterns": [
                "apa saja produk unggulan", "jual apa saja", "lihat katalog produk",
                "ready produk apa", "ada sepatu apa", "katalog sepatu", "daftar barang",
                "jual apa", "stok barang", "apakah ada sepatu sneaker", "rekomendasi produk"
            ],
            "responses": [
                "Kami menjual berbagai pilihan Sepatu Sneaker, Sepatu Running, dan Aksesoris Original.",
                "Katalog produk kami mencakup Sneaker Casual, Running Shoes, dan Kaos Kaki Premium Kak!"
            ]
        },
        {
            "tag": "cek_lokasi",
            "patterns": [
                "dimana alamat toko", "lokasi toko dimana", "bisa datang langsung ke toko",
                "alamat offline", "toko di mana", "cabang bandung", "dimana sih toko kalian",
                "posisi toko di mana", "buka jam berapa"
            ],
            "responses": [
                "Toko offline kami beralamat di Jl. Soekarno-Hatta No. 456, Bandung.",
                "Silakan mampir ke outlet kami di Jl. Soekarno-Hatta No. 456, Bandung. Buka setiap hari pukul 09.00 - 21.00 WIB."
            ]
        },
        {
            "tag": "komplain_pesanan",
            "patterns": [
                "barang belum sampai", "pesanan rusak", "paket nyangkut", "retur barang",
                "salah kirim barang", "produk jelek", "sangat jelek", "jelek", "buruk",
                "kualitas buruk", "kecewa", "sangat kecewa", "parah", "tidak sesuai",
                "cacat", "rusak", "mengecewakan", "kualitas jelek banget bikin kecewa"
            ],
            "responses": [
                "Mohon maaf sebesar-besarnya atas ketidaknyamanan Kakak. Produk kami bergaransi 100% Ganti Baru atau Uang Kembali. Silakan infokan nomor pesanan dan foto/video kendala produk agar tim kami proses ganti rugi segera.",
                "Kami sangat menyesal mendengar kendala ini Kak. Kepuasan Kakak adalah prioritas kami. Mohon kirimkan Nomor Resi / Bukti kendala untuk kami ganti dengan produk baru hari ini juga."
            ]
        },
        {
            "tag": "tanya_harga",
            "patterns": [
                "berapa harganya", "pricelist sepatu", "harga produk ini berapa",
                "ada diskon ga", "berapaan min", "daftar harga", "potongan harga",
                "harganya berapaan kak", "ada promo apa"
            ],
            "responses": [
                "Harga sepatu kami mulai dari Rp 250.000 hingga Rp 750.000 tergantung model dan brand Kak.",
                "Untuk pricelist lengkap dan promo diskon 10%, silakan cek katalog promo mingguan kami ya!"
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
# 3. FUNGSI LOAD & SAVE MEMORI JSON KE SISTEM
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
    """Menyimpan seluruh memori intent yang sudah dipelajari ke file JSON."""
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=4, ensure_ascii=False)


# ==============================================================================
# 4. ENGINE TF-IDF & COSINE SIMILARITY (OTOMATIS MEMAHAMI MAKNA KALIMAT)
# ==============================================================================
class IntentSimilarityEngine:
    """
    Engine AI cerdas berbasis TF-IDF & Cosine Similarity:
    Menghitung sudut kemiripan vektor antara kalimat pelanggan dengan seluruh
    pola intent di kamus, sehingga variasi kalimat panjang, typo, atau kalimat umum
    langsung dipahami otomatis tanpa perlu didaftarkan satu per satu.
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

        # Menggunakan kombinasi Unigram & Bigram agar frasa 2 kata terbobot sempurna
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2))
        self.pattern_vectors = self.vectorizer.fit_transform(self.corpus_patterns)

    def predict(self, user_message, threshold=0.25):
        clean_msg = user_message.lower().strip()
        # Jika kosong
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

        # Jika skor kemiripan >= threshold (misal 25%), AI langsung mengenali maksudnya
        if best_score >= threshold:
            for item in self.dataset["intents"]:
                if item["tag"] == best_tag:
                    return best_tag, best_score, random.choice(item["responses"])

        return "unknown", best_score, None


# ==============================================================================
# 5. MEKANISME SELF-LEARNING CERDAS (ACTIVE LEARNING)
# ==============================================================================
def pelajari_kata_baru(pesan_baru, dataset, engine):
    """
    Fitur Belajar: Hanya aktif jika skor kemiripan sangat rendah (< 25%),
    menanyakan kategori ke pengguna lalu menyimpan dan mere-train engine otomatis.
    """
    pesan_clean = pesan_baru.lower().strip()

    print("\n" + "=" * 65)
    print(f"[AI LEARNING]: Kalimat/kata '{pesan_clean}' belum dikenali sistem!")
    print("Bantu aku ya, maksud kalimat ini tergolong ke kategori apa?")
    print("-" * 65)

    tags = [intent['tag'] for intent in dataset['intents']]
    for i, tag in enumerate(tags, 1):
        print(f"  {i}. {tag}")
    print(f"  {len(tags) + 1}. [Abaikan / Tidak relevan]")

    pilihan = input(f"Pilih kategori intent (1-{len(tags) + 1}): ").strip()

    try:
        idx = int(pilihan) - 1
        if 0 <= idx < len(tags):
            tag_terpilih = tags[idx]
            for intent in dataset['intents']:
                if intent['tag'] == tag_terpilih:
                    if pesan_clean not in intent['patterns']:
                        intent['patterns'].append(pesan_clean)

                    # Simpan memori terbaru ke file JSON
                    simpan_kamus_intent(dataset)
                    # Rebuild TF-IDF engine agar langsung paham detik ini juga
                    engine.build_engine()

                    print(f"[SUKSES TERSIMPAN]: Pola '{pesan_clean}' berhasil dipelajari ke intent '{tag_terpilih}'!")
                    print("=" * 65 + "\n")
                    return tag_terpilih, random.choice(intent['responses'])
    except ValueError:
        pass

    print("[PERINGATAN]: Kata dilewati tanpa disimpan ke memori.")
    print("=" * 65 + "\n")
    return 'unknown', "Maaf Kak, saya belum memahami pertanyaan tersebut. Ada yang bisa kami bantu terkait katalog produk, harga, atau lokasi toko kami?"


# ==============================================================================
# 6. MODE CHAT INTERAKTIF DENGAN AI KEMIRIPAN SEMANTIK (GOOGLE COLAB)
# ==============================================================================
def jalankan_chatbot():
    dataset = load_kamus_intent()
    engine = IntentSimilarityEngine(dataset)

    print("=" * 70)
    print("[CHATBOT BISNIS CERDAS - ENGINE TF-IDF & COSINE SIMILARITY]")
    print(f"Status Memori: {len(dataset['intents'])} Kategori Intent | Model AI Siap.")
    print("Ketik pesan Anda di bawah. Ketik 'exit' atau 'keluar' untuk mengakhiri.")
    print("=" * 70)

    while True:
        try:
            pesan = input("\nPelanggan: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[Chatbot]: Terima kasih! Sampai jumpa kembali Kak.")
            break

        if not pesan:
            continue

        if pesan.lower() in ['exit', 'keluar', 'quit', 'selesai', 'bye']:
            print("[Chatbot]: Terima kasih telah menghubungi toko kami. Semoga harimu menyenangkan!")
            break

        # A. Ekstraksi Entitas
        entitas = ekstrak_entitas(pesan)

        # B. Prediksi Intent Menggunakan Cosine Similarity TF-IDF
        tag, skor, balasan = engine.predict(pesan)

        # C. Jika Kemiripan di Bawah Batas Ambang -> Aktifkan Belajar Otomatis
        if tag == 'unknown':
            tag, balasan = pelajari_kata_baru(pesan, dataset, engine)

        # D. Tampilkan Respon Chatbot beserta Confidence Score
        confidence_info = f" (Akurasi: {skor:.1%})" if tag != 'unknown' and skor > 0 else ""
        print(f"[Chatbot] ({tag}){confidence_info}: {balasan}")
        if entitas:
            print(f"  [Entitas Ditemukan]: {entitas}")


# ==============================================================================
# ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    jalankan_chatbot()
