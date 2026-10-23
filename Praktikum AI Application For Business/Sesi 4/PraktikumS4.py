# ==========================================
# 1. STRUKTUR DATASET KAMUS INTENT BISNIS
# ==========================================
dataset_intent_bisnis = {
    "intents": [
        {
            "tag": "sapaan",
            "patterns": ["halo", "hai", "selamat pagi", "permisi admin", "halo min"],
            "responses": ["Halo Kak! Ada yang bisa kami bantu hari ini?", "Hai! Selamat datang di Toko Kami."]
        },
        {
            "tag": "tanya_produk",
            "patterns": ["apa saja produk unggulan", "jual apa saja", "lihat katalog produk", "ready produk apa"],
            "responses": ["Kami menjual berbagai pilihan Sepatu Sneaker, Sepatu Running, dan Aksesoris Original."]
        },
        {
            "tag": "cek_lokasi",
            "patterns": ["dimana alamat toko", "lokasi toko dimana", "bisa datang langsung ke toko", "alamat offline"],
            "responses": ["Toko offline kami beralamat di Jl. Soekarno-Hatta No. 456, Bandung."]
        },
        {
            "tag": "komplain_pesanan",
            "patterns": ["barang belum sampai", "pesanan rusak", "paket nyangkut", "retur barang"],
            "responses": ["Mohon maaf atas ketidaknyamanannya Kak. Silakan kirimkan Nomor Resi Anda untuk kami cek segera."]
        }
    ]
}

# Menampilkan jumlah kategori intent yang berhasil dibuat
# ==========================================
# 1. IMPORT LIBRARY RANDOM & MEMBUAT FUNGSI CHATBOT
# ==========================================
import random

def deteksi_dan_jawab_intent(pesan_pelanggan, dataset):
    pesan_clean = pesan_pelanggan.lower().strip()

    # Iterasi melalui setiap intent dalam kamus
    for intent in dataset['intents']:
        for pattern in intent['patterns']:
            # Cek apakah kata pola terdapat di dalam pesan pelanggan
            if pattern in pesan_clean:
                # Pilih jawaban secara acak jika ada lebih dari satu pilihan
                jawaban = random.choice(intent['responses'])
                return intent['tag'], jawaban

    # Respon default jika intent tidak terdeteksi
    return 'unknown', 'Maaf Kak, saya belum memahami pertanyaan tersebut. Bisa diulangi?'

# ==========================================
# 2. SIMULASI PENGUJIAN CHATBOT
# ==========================================
pertanyaan_uji = 'dimana alamat toko ini berada'
tag_terdeteksi, balasan_chatbot = deteksi_dan_jawab_intent(pertanyaan_uji, dataset_intent_bisnis)

print('Pertanyaan Pelanggan :', pertanyaan_uji)
print('Intent Terdeteksi    :', tag_terdeteksi)
print('Balasan Chatbot      :', balasan_chatbot)

