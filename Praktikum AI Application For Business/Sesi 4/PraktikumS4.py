# ==============================================================================
# PRAKTIKUM AI APPLICATION FOR BUSINESS - SESI 4
# TOPIK: INTENT & ENTITIES + SMART KEYWORD EXTRACTION & ACTIVE LEARNING
# File: PraktikumS4.py (Siap Dijalankan di Google Colab)
# ==============================================================================

import json
import os
import random
import re
import sys

# Menjaga kompatibilitas output encoding di Windows Terminal & Google Colab
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# File penyimpanan memori intent di Google Colab / Local
JSON_FILE = os.path.join(os.path.dirname(__file__), 'kamus_intent.json') if '__file__' in globals() else 'kamus_intent.json'

# Daftar kata umum / kata sambung (Stopwords) yang diabaikan saat ekstraksi kata kunci
STOPWORDS = {
    'apakah', 'disini', 'di', 'sini', 'ada', 'yang', 'ini', 'itu', 'ke', 'dari',
    'saya', 'aku', 'kamu', 'anda', 'kami', 'toko', 'kak', 'min', 'admin',
    'dong', 'ya', 'nih', 'sih', 'deh', 'gan', 'bro', 'bisa', 'mau', 'ingin',
    'tolong', 'mohon', 'sangat', 'banget', 'bgt', 'kah', 'pun'
}

# ==============================================================================
# 1. STRUKTUR DATASET AWAL (5 KATEGORI INTENT + KATA KUNCI LENGKAP)
# ==============================================================================
default_dataset_intent = {
    "intents": [
        {
            "tag": "sapaan",
            "patterns": [
                "halo", "hai", "selamat pagi", "permisi admin", "halo min",
                "pagi", "assalamualaikum", "halo kak", "hai admin"
            ],
            "responses": [
                "Halo Kak! Ada yang bisa kami bantu hari ini?",
                "Hai! Selamat datang di Toko Kami, silakan tanyakan apa saja ya."
            ]
        },
        {
            "tag": "tanya_produk",
            "patterns": [
                "apa saja produk unggulan", "jual apa saja", "lihat katalog produk",
                "ready produk apa", "ada sepatu apa", "katalog", "daftar barang",
                "jual apa", "stok barang"
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
                "alamat offline", "toko di mana", "cabang toko", "buka jam berapa"
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
                "cacat", "rusak", "mengecewakan"
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
                "ada diskon ga", "berapaan min", "daftar harga", "potongan harga"
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
# 3. FUNGSI EKSTRAKSI KATA KUNCI (MENGATASI KALIMAT PANJANG)
# ==============================================================================
def ekstrak_kata_kunci(kalimat):
    """
    Menyaring kata sambung (stopwords) dan mengekstrak kata kunci inti
    agar bot mengenali kalimat panjang maupun kata tunggal.
    """
    clean = re.sub(r'[^a-zA-Z0-9\s]', ' ', kalimat.lower())
    words = clean.split()
    kata_kunci = [w for w in words if w not in STOPWORDS and len(w) > 1]
    return kata_kunci


# ==============================================================================
# 4. FUNGSI LOAD & SAVE MEMORI JSON KE SISTEM
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
# 5. FUNGSI PENCOCOKAN INTENT CERDAS (TOKEN & OVERLAP MATCHING)
# ==============================================================================
def deteksi_intent(pesan_pelanggan, dataset):
    """
    Mendeteksi intent dengan 2 tingkatan:
    1. Exact / Substring Match langsung pada pattern.
    2. Token Overlap Matching pada kata kunci penting (mengatasi kalimat panjang & pendek).
    """
    pesan_clean = pesan_pelanggan.lower().strip()
    pesan_no_punct = re.sub(r'[^a-zA-Z0-9\s]', ' ', pesan_clean)
    words = pesan_no_punct.split()
    kata_kunci_user = ekstrak_kata_kunci(pesan_clean)

    # Tingkat 1: Exact Match atau Substring Match pada pola
    for intent in dataset['intents']:
        for pattern in intent['patterns']:
            pattern_clean = pattern.lower().strip()
            if pattern_clean == pesan_clean or pattern_clean in pesan_clean or pattern_clean in words:
                return intent['tag'], random.choice(intent['responses'])

    # Tingkat 2: Pencocokan Berbasis Kata Kunci Inti (Token Overlap)
    if kata_kunci_user:
        best_intent = None
        best_score = 0
        for intent in dataset['intents']:
            score = 0
            for pattern in intent['patterns']:
                p_clean = pattern.lower().strip()
                p_words = set(re.sub(r'[^a-zA-Z0-9\s]', ' ', p_clean).split())
                # Hitung berapa kata kunci user yang cocok dengan pola dalam intent
                overlap = sum(1 for kw in kata_kunci_user if kw in p_words or kw in p_clean)
                if overlap > score:
                    score = overlap
            if score > best_score:
                best_score = score
                best_intent = intent

        # Jika ada minimal 1 kata kunci penting yang cocok, tentukan intent tersebut
        if best_intent and best_score >= 1:
            return best_intent['tag'], random.choice(best_intent['responses'])

    return 'unknown', None


# ==============================================================================
# 6. MEKANISME SELF-LEARNING CERDAS (MENYIMPAN KALIMAT & KATA KUNCI)
# ==============================================================================
def pelajari_kata_baru(pesan_baru, dataset):
    """
    Fitur Pintar: Ketika ada kalimat panjang atau kata baru, sistem mengekstrak
    kata kuncinya, meminta konfirmasi kategori, lalu menyimpan kalimat dan kata kunci
    ke memori JSON agar langsung dikenali baik dalam bentuk panjang maupun pendek.
    """
    pesan_clean = pesan_baru.lower().strip()
    kata_kunci = ekstrak_kata_kunci(pesan_clean)

    print("\n" + "=" * 65)
    print(f"[AI LEARNING]: Kalimat/kata '{pesan_clean}' belum ada di memoriku!")
    if kata_kunci:
        print(f"Kata kunci terdeteksi: {kata_kunci}")
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
            # Tambahkan kalimat lengkap ke pola
            for intent in dataset['intents']:
                if intent['tag'] == tag_terpilih:
                    if pesan_clean not in intent['patterns']:
                        intent['patterns'].append(pesan_clean)
                    # Tambahkan juga setiap kata kunci penting secara individual
                    for kw in kata_kunci:
                        if kw not in intent['patterns']:
                            intent['patterns'].append(kw)

                    # Simpan memori terbaru ke file JSON di Colab
                    simpan_kamus_intent(dataset)
                    print(f"[SUKSES TERSIMPAN]: Pola '{pesan_clean}' dan kata kunci {kata_kunci} berhasil disimpan ke intent '{tag_terpilih}'!")
                    print("=" * 65 + "\n")
                    return tag_terpilih, random.choice(intent['responses'])
    except ValueError:
        pass

    print("[PERINGATAN]: Kata dilewati tanpa disimpan ke memori.")
    print("=" * 65 + "\n")
    return 'unknown', "Maaf Kak, saya belum memahami pertanyaan tersebut. Ada yang bisa dibantu lainnya?"


# ==============================================================================
# 7. MODE CHAT INTERAKTIF (GOOGLE COLAB)
# ==============================================================================
def jalankan_chatbot():
    dataset = load_kamus_intent()
    print("=" * 70)
    print("[CHATBOT BISNIS INTERAKTIF - FITUR SELF-LEARNING CERDAS]")
    print("Status Memori: 5 Kategori Intent Siap Digunakan.")
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

        # B. Deteksi Intent (Cerdas: Kalimat Panjang, Kata Singkat, dan Bad Review)
        tag, balasan = deteksi_intent(pesan, dataset)

        # C. Jika Belum Dikenali -> Aktifkan Mekanisme Belajar Otomatis
        if tag == 'unknown':
            tag, balasan = pelajari_kata_baru(pesan, dataset)

        # D. Tampilkan Respon Chatbot
        print(f"[Chatbot] ({tag}): {balasan}")
        if entitas:
            print(f"  [Entitas Ditemukan]: {entitas}")


# ==============================================================================
# ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    jalankan_chatbot()
