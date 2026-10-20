# HuntFacts (proyek STKI)

Sistem temu kembali klarifikasi hoaks berbahasa Indonesia untuk pesan berantai, memakai TF-IDF dan BM25.
Sistem hanya menampilkan artikel klarifikasi yang terkait. Sistem tidak memvonis benar atau salah.

## Isi folder
| Berkas | Fungsi |
|---|---|
| `HuntFacts_STKI.ipynb` | Notebook utama (data, preprocessing, indexing, evaluasi, analisis) |
| `huntfacts_core.py` | Modul preprocessing, inverted index, TF-IDF, BM25 (dipakai notebook dan app) |
| `app.py` | Antarmuka Streamlit |
| `data/Meta Data.xlsx` | Dataset (sheet "Hasil Scrapping"), sumber: JibranFawaid/turnbackhoax-dataset |
| `data/eval/queries_draft.csv` | 44 klaim uji DRAF (perlu kamu tulis ulang dan lengkapi) |
| `data/eval/pool_for_annotation.csv` | Berkas penilaian relevansi (dibuat notebook) |
| `artifacts/` | Koleksi bersih dan cache stemming (dibuat notebook) |

## Cara menjalankan
1. `pip install -r requirements.txt`
2. Buka `HuntFacts_STKI.ipynb`, lalu Run All (3 sampai 6 menit pada run pertama).
3. Aplikasi: `streamlit run app.py`

## Alur kunci jawaban (wajib untuk hasil yang sah)
1. Baca dan tulis ulang `data/eval/queries_draft.csv` dengan gayamu, simpan sebagai `data/eval/queries_final.csv`.
2. Jalankan notebook sampai bagian 6.3 supaya `pool_for_annotation.csv` terbentuk.
3. Isi kolom `relevan` (1 atau 0), simpan sebagai `data/eval/annotator_A.csv`.
4. Minta satu teman menilai tanpa melihat jawabanmu, simpan sebagai `data/eval/annotator_B.csv`.
5. Run All ulang. Cohen's kappa dan hasil evaluasi akan dihitung otomatis.

## Catatan data
Tidak ada berkas lisensi pada salinan dataset. Periksa halaman repositori GitHub dan ketentuan turnbackhoax.id sebelum menyebarluaskan.
