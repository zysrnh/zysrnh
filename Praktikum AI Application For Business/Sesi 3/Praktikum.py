# ==========================================
# 1. IMPORT LIBRARY SCIKIT-LEARN & PANDAS
# ==========================================
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd

# Dataset pertanyaan pelanggan bisnis toko online
dataset_pertanyaan = [
    "apakah produk ini ready stok",
    "apakah produk ini ada garansi resmi",
    "berapa harga produk ini dan ongkos kirim"
]

# ==========================================
# 2. EKSEKUSI BAG OF WORDS (COUNTVECTORIZER)
# ==========================================
vectorizer_bow = CountVectorizer()
matrix_bow = vectorizer_bow.fit_transform(dataset_pertanyaan)

# Mengambil daftar kata unik (Fitur/Vocabulary)
fitur_kata = vectorizer_bow.get_feature_names_out()

# Mengubah matriks sparse menjadi DataFrame Pandas agar rapi
df_bow = pd.DataFrame(matrix_bow.toarray(), columns=fitur_kata)
print('=== MATRIKS BAG OF WORDS (FREKUENSI KATA) ===')
print(df_bow)
