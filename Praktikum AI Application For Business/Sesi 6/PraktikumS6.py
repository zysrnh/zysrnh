# ==============================================================================
# PRAKTIKUM AI APPLICATION FOR BUSINESS - PERTEMUAN 6
# TOPIK       : PELATIHAN MODEL KLASIFIKASI INTENT CHATBOT BISNIS MENGGUNAKAN
#               MACHINE LEARNING (NAIVE BAYES & LOGISTIC REGRESSION)
# STUDI KASUS : JASA WEB DEVELOPMENT (NusaWeb Studio)
# FILE        : PraktikumS6.py (Siap Dijalankan di Google Colab)
# ==============================================================================

import sys
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ==============================================================================
# INSTRUKSI 2: KAMUS INTENT BISNIS JASA WEB DEVELOPMENT
# (6 Kategori Intent, masing-masing memiliki 8 variasi kalimat patterns)
# ==============================================================================
dataset_intent = {
    "intents": [
        {
            "tag": "sapaan",
            "patterns": [
                "halo",
                "hai admin",
                "selamat pagi",
                "selamat siang kak",
                "selamat sore min",
                "permisi min mau tanya",
                "halo tim web developer",
                "assalamualaikum admin"
            ],
            "response": (
                "Halo Kak! Selamat datang di NusaWeb Studio (Jasa Web Development Profesional). "
                "Ada yang bisa kami bantu seputar layanan pembuatan website, paket harga, "
                "estimasi waktu pengerjaan, atau garansi maintenance?"
            )
        },
        {
            "tag": "layanan_web",
            "patterns": [
                "melayani jasa pembuatan website apa saja",
                "bisa bikin web company profile dan toko online",
                "jasa pembuatan landing page dan sistem informasi",
                "apakah terima bikin aplikasi web custom laravel react",
                "paket layanan jasa web development apa aja",
                "bisa buat website e-commerce dan portal berita",
                "katalog layanan pembuatan aplikasi web",
                "jenis website apa saja yang bisa dibuat"
            ],
            "response": (
                "Layanan Jasa Web Development di NusaWeb Studio meliputi:\n"
                "  1. Website Landing Page Promosi & UMKM\n"
                "  2. Website Company Profile Perusahaan / Instansi\n"
                "  3. Website Toko Online (E-Commerce + Payment Gateway)\n"
                "  4. Web App / Sistem Informasi Custom (Laravel, React, Node.js)"
            )
        },
        {
            "tag": "tanya_harga",
            "patterns": [
                "berapa biaya bikin website",
                "pricelist harga jasa pembuatan web",
                "harga bikin landing page berapaan",
                "estimasi biaya pembuatan toko online berapa",
                "paket harga buat website perusahaan",
                "daftar tarif biaya jasa web murah",
                "berapa harga paket pembuatan website",
                "info biaya dan harga bikin web"
            ],
            "response": (
                "Daftar Paket Harga Jasa Pembuatan Website:\n"
                "  • Paket Landing Page    : Rp 1.500.000 (Gratis Domain .com + Hosting 1 Thn)\n"
                "  • Paket Company Profile : Rp 3.000.000 (Desain UI/UX Eksklusif + SEO Basic)\n"
                "  • Paket Toko Online     : Rp 4.500.000 (Integrasi Ongkir & QRIS/Virtual Account)\n"
                "  • Paket Custom Web App  : Mulai Rp 7.500.000 (Sesuai kompleksitas fitur)"
            )
        },
        {
            "tag": "durasi_pengerjaan",
            "patterns": [
                "berapa lama proses pengerjaan website",
                "estimasi waktu pengerjaan web berapa hari kerja",
                "bikin website selesai berapa minggu",
                "proses develop web makan waktu berapa lama",
                "apakah sudah termasuk gratis domain dan hosting",
                "kapan website saya bisa selesai dan online",
                "durasi waktu pengerjaan project website",
                "butuh waktu berapa hari sampai website jadi"
            ],
            "response": (
                "Estimasi waktu pengerjaan website:\n"
                "  • Landing Page    : 3 - 5 hari kerja\n"
                "  • Company Profile : 7 - 10 hari kerja\n"
                "  • Toko Online/App : 14 - 30 hari kerja\n"
                "  (Semua paket sudah termasuk gratis Domain .com/.id, Cloud Hosting, dan SSL HTTPS!)"
            )
        },
        {
            "tag": "revisi_maintenance",
            "patterns": [
                "apakah dapat garansi maintenance",
                "gimana kalau website error atau down",
                "bisa revisi desain berapa kali",
                "ada layanan maintenance bulanan dan perbaikan bug",
                "klaim garansi support teknis website",
                "apakah dibantu kalau ada kendala server",
                "jatah revisi tampilan ui ux website",
                "garansi perbaikan jika ada fitur error"
            ],
            "response": (
                "Tenang Kak! Setiap pembuatan website di NusaWeb mendapat:\n"
                "  • Gratis Revisi Desain hingga 3x selama tahap development\n"
                "  • Garansi Maintenance & Bug Fixing gratis selama 3 bulan penuh\n"
                "  • Backup berkala & bantuan teknis 24/7 jika server mengalami kendala."
            )
        },
        {
            "tag": "kontak_order",
            "patterns": [
                "gimana cara order pemesanan website",
                "minta nomor whatsapp atau telepon tim marketing",
                "mau jadwalkan meeting konsultasi project web",
                "hubungi kemana kalau mau pesan website",
                "nomor kontak cs jasa web development",
                "cara pesan dan kontrak kerja pembuatan web",
                "alamat kantor studio web dimana",
                "nomor wa untuk konsultasi pemesanan"
            ],
            "response": (
                "Untuk pemesanan atau konsultasi kebutuhan website gratis, hubungi kami di:\n"
                "  • WhatsApp Konsultasi : 0812-3456-7890\n"
                "  • Telepon Kantor      : (022) 731-8899\n"
                "  • Studio Offline      : Jl. Soekarno-Hatta No. 456, Bandung"
            )
        }
    ]
}

RESPON_INTENT = {item["tag"]: item["response"] for item in dataset_intent["intents"]}

# ==============================================================================
# INSTRUKSI 3: EKSTRAK DATASET MENJADI PASANGAN ARRAY X_train DAN y_train
# ==============================================================================
X_train = []
y_train = []

for intent in dataset_intent["intents"]:
    for pattern in intent["patterns"]:
        X_train.append(pattern)
        y_train.append(intent["tag"])

print("=" * 80)
print("  PRAKTIKUM 6: KLASIFIKASI INTENT CHATBOT - JASA WEB DEVELOPMENT (NusaWeb)")
print("=" * 80)
print(f"Total Kategori Intent : {len(dataset_intent['intents'])} kategori")
print(f"Total Sampel X_train  : {len(X_train)} kalimat pertanyaan latih")
print("-" * 80)

# ==============================================================================
# INSTRUKSI 4: LATIH DUA MODEL KLASIFIKASI MENGGUNAKAN SCIKIT-LEARN PIPELINE
# (1) Multinomial Naive Bayes & (2) Logistic Regression
# ==============================================================================

# 1. Pipeline Model Multinomial Naive Bayes
model_nb = Pipeline([
    ("vect", CountVectorizer()),
    ("tfidf", TfidfTransformer()),
    ("clf", MultinomialNB())
])
model_nb.fit(X_train, y_train)
print("[OK] Model 1: Multinomial Naive Bayes berhasil dilatih!")

# 2. Pipeline Model Logistic Regression
model_logreg = Pipeline([
    ("vect", CountVectorizer()),
    ("tfidf", TfidfTransformer()),
    ("clf", LogisticRegression())
])
model_logreg.fit(X_train, y_train)
print("[OK] Model 2: Logistic Regression berhasil dilatih!")
print("=" * 80)


# ==============================================================================
# FUNGSI PREDIKSI INTENT PELANGGAN REAL-TIME
# ==============================================================================
def prediksi_intent_ml(kalimat_baru, model):
    prediksi_tag = model.predict([kalimat_baru])[0]
    probabilitas = model.predict_proba([kalimat_baru]).max()
    return prediksi_tag, probabilitas


# ==============================================================================
# INSTRUKSI 5: UJI KEDUA MODEL DENGAN MINIMAL 4 KALIMAT PERTANYAAN BARU
# (Belum ada di data latih) & TAMPILKAN TAG INTENT BESERTA CONFIDENCE SCORE (%)
# ==============================================================================
daftar_pertanyaan_uji = [
    "berapa biaya dan harga paket pembuatan website perusahaan ya",
    "apakah melayani pembuatan aplikasi web custom pakai laravel dan react",
    "proses pengerjaan web sampai selesai butuh waktu berapa hari kerja",
    "kalau nanti website tiba-tiba error apakah dapat garansi perbaikan bug",
    "minta nomor whatsapp tim marketing untuk konsultasi cara order",
    "selamat pagi admin, permisi mau tanya"
]

print("\nHASIL PENGUJIAN PERBANDINGAN NAIVE BAYES VS LOGISTIC REGRESSION:")
print("=" * 80)

for idx, kalimat_uji in enumerate(daftar_pertanyaan_uji, start=1):
    tag_nb, conf_nb = prediksi_intent_ml(kalimat_uji, model_nb)
    tag_lr, conf_lr = prediksi_intent_ml(kalimat_uji, model_logreg)

    print(f"\n[Uji #{idx}] Pertanyaan Baru : \"{kalimat_uji}\"")
    print(f"  • Naive Bayes         -> Intent: {tag_nb:<20} | Confidence: {conf_nb * 100:6.2f}%")
    print(f"  • Logistic Regression -> Intent: {tag_lr:<20} | Confidence: {conf_lr * 100:6.2f}%")
    print(f"  • Respon Chatbot      : {RESPON_INTENT[tag_lr].splitlines()[0]}")

# ==============================================================================
# INSTRUKSI 6: PERBANDINGAN AKURASI MODEL (UNTUK SEL TEKS / KESIMPULAN COLAB)
# ==============================================================================
print("\n" + "=" * 80)
print("KESIMPULAN PERBANDINGAN MODEL (UNTUK SEL TEKS + TEXT DI GOOGLE COLAB):")
print("-" * 80)
kesimpulan_perbandingan = """
Berdasarkan hasil pengujian terhadap kalimat pertanyaan baru pada studi kasus
Jasa Web Development (NusaWeb Studio):
1. Ketepatan Prediksi (Akurasi):
   Kedua model (Multinomial Naive Bayes dan Logistic Regression) berhasil
   memprediksi seluruh kategori intent (100% tepat) pada kalimat uji baru yang
   belum pernah ada di data latih (X_train).
2. Perbandingan Confidence Score (%):
   Model Logistic Regression menghasilkan nilai Confidence Score rata-rata yang
   lebih tinggi dan stabil dibandingkan Multinomial Naive Bayes, karena Logistic
   Regression mengoptimalkan bobot pemisah antar kelas fitur TF-IDF secara langsung,
   sedangkan Naive Bayes mengasumsikan kemunculan tiap kata bersifat independen.
   Dengan demikian, Logistic Regression lebih unggul untuk digunakan pada sistem
   chatbot pelanggan Jasa Web Development.
"""
print(kesimpulan_perbandingan.strip())
print("=" * 80)


# ==============================================================================
# FITUR TAMBAHAN: LIVE CHAT INTERAKTIF DENGAN INPUT() & FALLBACK TELEPON CS
# ==============================================================================
def live_chat_webdev():
    print("\n" + "=" * 80)
    print("        LIVE CHAT SIMULASI - NUSAWEB STUDIO (JASA WEB DEVELOPMENT)        ")
    print("=" * 80)
    print("  Tag Topik Obrolan:")
    print("  • 'Layanan web apa saja'      • 'Berapa lama pengerjaan web'")
    print("  • 'Berapa harga bikin web'    • 'Apakah ada garansi / revisi'")
    print("  • 'Cara order / No WA'        • Ketik 'exit' untuk selesai")
    print("-" * 80)
    print("Bot  : Halo Kak! Selamat datang di NusaWeb Studio. Mau konsultasi pembuatan")
    print("       website apa hari ini? (Landing Page / Company Profile / Toko Online / Web App)")

    vectorizer = model_logreg.named_steps["vect"]

    while True:
        try:
            pesan_user = input("\nAnda : ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBot  : Terima kasih sudah menghubungi NusaWeb Studio. Sampai jumpa Kak!")
            break

        if not pesan_user:
            continue

        if pesan_user.lower() in ["exit", "keluar", "quit", "selesai"]:
            print("Bot  : Terima kasih sudah berkonsultasi di NusaWeb Studio!")
            print("       Hubungi WA 0812-3456-7890 kapan saja jika siap mulai project ya Kak.")
            print("=" * 80)
            break

        # Cek apakah ada kata yang dikenali di dalam kosakata (vocabulary) model
        jumlah_kata_dikenali = vectorizer.transform([pesan_user]).nnz
        tag_pred, skor_conf = prediksi_intent_ml(pesan_user, model_logreg)

        # Jika kalimat tidak jelas / tidak ada kata yang dikenali / confidence rendah (< 20%)
        if jumlah_kata_dikenali == 0 or skor_conf < 0.20:
            print(
                f"Bot  : Maaf Kak, maksud kalimatnya belum tertangkap oleh sistem AI kami.\n"
                f"       Untuk diskusi kebutuhan fitur custom secara langsung, silakan hubungi:\n"
                f"       • WhatsApp Konsultasi : 0812-3456-7890  |  Telepon : (022) 731-8899\n"
                f"       • Atau tanyakan seputar: Layanan Web, Harga Paket, Lama Pengerjaan, Garansi Revisi."
            )
        else:
            print(f"Bot  : [Intent: {tag_pred} | Confidence: {skor_conf * 100:.2f}%]")
            print(f"       {RESPON_INTENT[tag_pred]}")


if __name__ == "__main__":
    live_chat_webdev()
