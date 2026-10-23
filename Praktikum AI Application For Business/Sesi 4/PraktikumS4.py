# ==============================================================================
# PRAKTIKUM AI APPLICATION FOR BUSINESS - SESI 4
# TOPIK: INTENT & ENTITIES + SELF-LEARNING CHATBOT (ACTIVE LEARNING)
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

# ==============================================================================
# 1. STRUKTUR DATASET AWAL (5 KATEGORI INTENT SESUAI TUGAS MODUL 4)
# ==============================================================================
default_dataset_intent = {
    "intents": [
        {
            "tag": "sapaan",
            "patterns": ["halo", "hai", "selamat pagi", "permisi admin", "halo min", "pagi", "assalamualaikum"],
            "responses": [
                "Halo Kak! Ada yang bisa kami bantu hari ini?",
                "Hai! Selamat datang di Toko Sepatu Kami, silakan tanyakan apa saja ya."
            ]
        },
        {
            "tag": "tanya_produk",
            "patterns": ["apa saja produk unggulan", "jual apa saja", "lihat katalog produk", "ready produk apa", "ada sepatu apa"],
            "responses": [
                "Kami menjual berbagai pilihan Sepatu Sneaker, Sepatu Running, dan Aksesoris Original.",
                "Katalog produk kami mencakup Sneaker Casual, Running Shoes, dan Kaos Kaki Premium Kak!"
            ]
        },
        {
            "tag": "cek_lokasi",
            "patterns": ["dimana alamat toko", "lokasi toko dimana", "bisa datang langsung ke toko", "alamat offline", "toko di mana"],
            "responses": [
                "Toko offline kami beralamat di Jl. Soekarno-Hatta No. 456, Bandung.",
                "Silakan mampir ke outlet kami di Jl. Soekarno-Hatta No. 456, Bandung. Buka setiap hari pukul 09.00 - 21.00 WIB."
            ]
        },
        {
            "tag": "komplain_pesanan",
            "patterns": ["barang belum sampai", "pesanan rusak", "paket nyangkut", "retur barang", "salah kirim barang"],
            "responses": [
                "Mohon maaf atas ketidaknyamanannya Kak. Silakan kirimkan Nomor Resi Anda untuk kami cek segera.",
                "Kami siap bantu kendalanya Kak. Mohon infokan Nomor Pesanan dan bukti video unboxing ya."
            ]
        },
        {
            "tag": "tanya_harga",
            "patterns": ["berapa harganya", "pricelist sepatu", "harga produk ini berapa", "ada diskon ga", "berapaan min"],
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
# 4. FUNGSI PENCOCOKAN INTENT (PATTERN MATCHING)
# ==============================================================================
def deteksi_intent(pesan_pelanggan, dataset):
    """Mendeteksi apakah pesan pelanggan cocok dengan salah satu pattern yang ada."""
    pesan_clean = pesan_pelanggan.lower().strip()
    pesan_clean_no_punct = re.sub(r'[^a-zA-Z0-9\s]', ' ', pesan_clean)
    words = pesan_clean_no_punct.split()

    for intent in dataset['intents']:
        for pattern in intent['patterns']:
            pattern_clean = pattern.lower().strip()
            # Cek kecocokan kalimat penuh, potongan frasa, atau kata kunci
            if pattern_clean in pesan_clean or pattern_clean in words or pesan_clean == pattern_clean:
                jawaban = random.choice(intent['responses'])
                return intent['tag'], jawaban

    return 'unknown', None


# ==============================================================================
# 5. MEKANISME SELF-LEARNING (ACTIVE LEARNING / MEMPELAJARI POLA BARU)
# ==============================================================================
def pelajari_kata_baru(kata_baru, dataset):
    """
    Fitur Pintar: Ketika ada kata/kalimat asing yang belum ada di pola (seperti 'oy'),
    sistem meminta konfirmasi kategori, lalu otomatis menyimpannya ke memori JSON.
    """
    print("\n" + "=" * 65)
    print(f"[AI LEARNING]: Kata/kalimat '{kata_baru}' belum ada di memoriku!")
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
            # Tambahkan pola kata baru ke intent tersebut
            for intent in dataset['intents']:
                if intent['tag'] == tag_terpilih:
                    if kata_baru not in intent['patterns']:
                        intent['patterns'].append(kata_baru)
                    # Simpan memori terbaru ke file JSON di Colab
                    simpan_kamus_intent(dataset)
                    print(f"[SUKSES TERSIMPAN]: Kata '{kata_baru}' berhasil dipelajari dan disimpan ke intent '{tag_terpilih}'!")
                    print("=" * 65 + "\n")
                    # Langsung jawab dengan respon intent tersebut
                    return tag_terpilih, random.choice(intent['responses'])
    except ValueError:
        pass

    print("[PERINGATAN]: Kata dilewati tanpa disimpan ke memori.")
    print("=" * 65 + "\n")
    return 'unknown', "Maaf Kak, saya belum memahami pertanyaan tersebut. Ada yang bisa dibantu lainnya?"


# ==============================================================================
# 6. MODE CHAT INTERAKTIF (GOOGLE COLAB)
# ==============================================================================
def jalankan_chatbot():
    dataset = load_kamus_intent()
    print("=" * 70)
    print("[CHATBOT BISNIS INTERAKTIF - FITUR SELF-LEARNING]")
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

        # B. Deteksi Intent
        tag, balasan = deteksi_intent(pesan, dataset)

        # C. Jika Belum Dikenali -> Aktifkan Mekanisme Belajar Otomatis
        if tag == 'unknown':
            tag, balasan = pelajari_kata_baru(pesan.lower().strip(), dataset)

        # D. Tampilkan Respon Chatbot
        print(f"[Chatbot] ({tag}): {balasan}")
        if entitas:
            print(f"  [Entitas Ditemukan]: {entitas}")


# ==============================================================================
# 7. SIMULASI PENGUJIAN OTOMATIS (POIN 5 MODUL)
# ==============================================================================
def simulasi_pengujian():
    dataset = load_kamus_intent()
    print("\n" + "=" * 70)
    print("SIMULASI PENGUJIAN 3 KALIMAT PELANGGAN BERBEDA (POIN 5 MODUL 4)")
    print("=" * 70)

    pertanyaan_uji = [
        "Halo min, ada sepatu running diskon ga hari ini?",
        "Dimana alamat toko offline nya ya?",
        "Paket nyangkut nih barang belum sampai sama sekali!"
    ]

    for i, tanya in enumerate(pertanyaan_uji, 1):
        tag, balasan = deteksi_intent(tanya, dataset)
        entitas = ekstrak_entitas(tanya)
        print(f"\n[Uji {i}]")
        print(f"  Pertanyaan        : {tanya}")
        print(f"  Intent Terdeteksi : {tag}")
        print(f"  Entitas Khusus    : {entitas if entitas else 'None'}")
        print(f"  Balasan Chatbot   : {balasan}")


# ==============================================================================
# ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    # 1. Jalankan simulasi pengujian modul
    simulasi_pengujian()

    # 2. Buka sesi chat interaktif
    print("\n")
    jalankan_chatbot()
