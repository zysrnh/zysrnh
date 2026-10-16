# ==========================================
# 1. IMPORT TFIDFVECTORIZER & PANDAS
# ==========================================
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd

# Dataset ulasan pelanggan bisnis toko online
dataset_ulasan = [
    "apakah produk ini ready stok",
    "apakah produk ini ada garansi resmi",
    "berapa harga produk ini dan ongkos kirim"
]

# ==========================================
# 2. EKSEKUSI TF-IDF VECTORIZER
# ==========================================
vectorizer_tfidf = TfidfVectorizer()
matrix_tfidf = vectorizer_tfidf.fit_transform(dataset_ulasan)

# Mengambil nama fitur kata unik (Vocabulary)
nama_kata = vectorizer_tfidf.get_feature_names_out()

# Menampilkan hasil bobot TF-IDF dalam bentuk DataFrame (pembulatan 3 desimal)
df_tfidf = pd.DataFrame(matrix_tfidf.toarray(), columns=nama_kata)

print('=== MATRIKS TF-IDF (BOBOT KEUNIKAN KATA) ===')
print(df_tfidf.round(3))