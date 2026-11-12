# ==============================================================================
# PRAKTIKUM KECERDASAN BUATAN - SESI 7 (POST-TEST CHALLENGE)
# STUDI KASUS : SISTEM PAKAR SELEKSI BEASISWA KELAYAKAN MAHASISWA IDE LPKIA
# FITUR       : 1. Dataset CSV Real Mahasiswa (Auto-Generate & Load di Colab)
#               2. Mesin Inferensi Forward Chaining + Jejak Inferensi (R1, R2, R3)
#               3. Mesin Inferensi Backward Chaining + Pembuktian Hipotesis
#               4. Pengujian 3 Profil Mahasiswa Berbeda
#               5. Visualisasi Interaktif Neubrutalism HTML di Google Colab
# ==============================================================================

import csv
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CSV_FILENAME = (
    os.path.join(os.path.dirname(__file__), "dataset_beasiswa_lpkia.csv")
    if "__file__" in globals()
    else "dataset_beasiswa_lpkia.csv"
)

DEFAULT_CSV_DATA = [
    ["nim", "nama", "prodi", "ipk", "penghasilan_ortu", "prestasi_akademik", "organisasi_aktif"],
    ["250414001", "Rizky Pratama", "Teknik Informatika", "3.78", "2400000", "Tidak", "Tidak"],
    ["250414002", "Nadia Maharani", "Sistem Informasi", "3.65", "5500000", "Ya", "Ya"],
    ["250414003", "Dimas Anggara", "Teknik Informatika", "3.25", "2200000", "Tidak", "Ya"],
    ["250414004", "Siti Nurhaliza", "Sistem Informasi", "3.85", "2800000", "Ya", "Ya"],
]


def siapkan_dataset_csv():
    """Memastikan file CSV dataset mahasiswa tersedia di lokal maupun Google Colab."""
    if not os.path.exists(CSV_FILENAME):
        with open(CSV_FILENAME, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(DEFAULT_CSV_DATA)

    profil_list = []
    with open(CSV_FILENAME, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            profil_list.append({
                "nim": row["nim"],
                "nama": row["nama"],
                "prodi": row["prodi"],
                "ipk": float(row["ipk"]),
                "penghasilan_ortu": int(row["penghasilan_ortu"]),
                "prestasi_akademik": row["prestasi_akademik"].strip().lower() == "ya",
                "organisasi_aktif": row["organisasi_aktif"].strip().lower() == "ya",
            })
    return profil_list


# ==============================================================================
# 1. EKSTRAKSI FAKTA AWAL & BASIS ATURAN PRODUKSI (R1, R2, R3)
# ==============================================================================
def ekstrak_fakta_awal(mhs):
    """
    Mengubah atribut profil mahasiswa menjadi himpunan fakta awal:
    - IPK >= 3.5
    - OrangTua_KurangMampu (Penghasilan Orang Tua < Rp 3.000.000)
    - Prestasi_Akademik
    - Organisasi_Aktif
    """
    fakta = []
    if mhs["ipk"] >= 3.5:
        fakta.append("IPK >= 3.5")
    if mhs["penghasilan_ortu"] < 3000000:
        fakta.append("OrangTua_KurangMampu")
    if mhs["prestasi_akademik"]:
        fakta.append("Prestasi_Akademik")
    if mhs["organisasi_aktif"]:
        fakta.append("Organisasi_Aktif")
    return fakta


# ==============================================================================
# 2. MESIN INFERENSI FORWARD CHAINING (DATA-DRIVEN)
# ==============================================================================
def forward_chaining_beasiswa(fakta_awal):
    """
    Mengevaluasi status beasiswa mahasiswa secara Forward Chaining:
    - R1: IF IPK >= 3.5 AND OrangTua_KurangMampu THEN Layak_Ekonomi
    - R2: IF IPK >= 3.5 AND (Prestasi_Akademik OR Organisasi_Aktif) THEN Layak_Prestasi
    - R3: IF Layak_Ekonomi OR Layak_Prestasi THEN BEASISWA_DISETUJUI
    """
    known_facts = set(fakta_awal)
    jejak_inferensi = []
    iterasi = 1
    ada_fakta_baru = True

    print(f"  [START] Fakta Awal : {sorted(list(known_facts))}")

    while ada_fakta_baru:
        ada_fakta_baru = False
        print(f"  --- Iterasi ke-{iterasi} ---")

        # Evaluasi R1: IF IPK >= 3.5 AND OrangTua_KurangMampu THEN Layak_Ekonomi
        syarat_r1 = ("IPK >= 3.5" in known_facts) and ("OrangTua_KurangMampu" in known_facts)
        if syarat_r1 and ("Layak_Ekonomi" not in known_facts):
            known_facts.add("Layak_Ekonomi")
            pesan = "R1 Terpemicu: IF IPK >= 3.5 AND OrangTua_KurangMampu THEN Layak_Ekonomi"
            jejak_inferensi.append(pesan)
            print(f"    [+] {pesan}")
            ada_fakta_baru = True
            iterasi += 1
            continue
        else:
            alasan = "Sudah diketahui" if "Layak_Ekonomi" in known_facts else "Syarat belum terpenuhi"
            print(f"    [-] R1 Dilewati ({alasan})")

        # Evaluasi R2: IF IPK >= 3.5 AND (Prestasi_Akademik OR Organisasi_Aktif) THEN Layak_Prestasi
        syarat_r2 = ("IPK >= 3.5" in known_facts) and (
            ("Prestasi_Akademik" in known_facts) or ("Organisasi_Aktif" in known_facts)
        )
        if syarat_r2 and ("Layak_Prestasi" not in known_facts):
            known_facts.add("Layak_Prestasi")
            pesan = "R2 Terpemicu: IF IPK >= 3.5 AND (Prestasi_Akademik OR Organisasi_Aktif) THEN Layak_Prestasi"
            jejak_inferensi.append(pesan)
            print(f"    [+] {pesan}")
            ada_fakta_baru = True
            iterasi += 1
            continue
        else:
            alasan = "Sudah diketahui" if "Layak_Prestasi" in known_facts else "Syarat belum terpenuhi"
            print(f"    [-] R2 Dilewati ({alasan})")

        # Evaluasi R3: IF Layak_Ekonomi OR Layak_Prestasi THEN BEASISWA_DISETUJUI
        syarat_r3 = ("Layak_Ekonomi" in known_facts) or ("Layak_Prestasi" in known_facts)
        if syarat_r3 and ("BEASISWA_DISETUJUI" not in known_facts):
            known_facts.add("BEASISWA_DISETUJUI")
            pesan = "R3 Terpemicu: IF Layak_Ekonomi OR Layak_Prestasi THEN BEASISWA_DISETUJUI"
            jejak_inferensi.append(pesan)
            print(f"    [+] {pesan}")
            ada_fakta_baru = True
            iterasi += 1
            continue
        else:
            alasan = "Sudah diketahui" if "BEASISWA_DISETUJUI" in known_facts else "Syarat belum terpenuhi"
            print(f"    [-] R3 Dilewati ({alasan})")

    disetujui = "BEASISWA_DISETUJUI" in known_facts
    print(f"  [FAKTA AKHIR]      : {sorted(list(known_facts))}")
    print(f"  [KEPUTUSAN FC]     : {'BEASISWA_DISETUJUI (LOLOS)' if disetujui else 'BEASISWA_DITOLAK (TIDAK LOLOS)'}")
    return disetujui, known_facts, jejak_inferensi


# ==============================================================================
# 3. MESIN INFERENSI BACKWARD CHAINING (GOAL-DRIVEN)
# ==============================================================================
# Representasi klausa Horn (Disjungsi OR dipecah menjadi cabang sub-goal konjungtif)
ATURAN_BACKWARD = {
    "BEASISWA_DISETUJUI": [
        ("R3 [Jalur Ekonomi]", ["Layak_Ekonomi"]),
        ("R3 [Jalur Prestasi]", ["Layak_Prestasi"]),
    ],
    "Layak_Ekonomi": [
        ("R1", ["IPK >= 3.5", "OrangTua_KurangMampu"]),
    ],
    "Layak_Prestasi": [
        ("R2 [Prestasi Akademik]", ["IPK >= 3.5", "Prestasi_Akademik"]),
        ("R2 [Organisasi Aktif]", ["IPK >= 3.5", "Organisasi_Aktif"]),
    ],
}


def backward_chaining_beasiswa(goal, known_facts, depth=0):
    """
    Membuktikan hipotesis 'BEASISWA_DISETUJUI' secara rekursif (Backward Chaining).
    """
    indent = "    " + ("  " * depth)

    # 1. Jika goal sudah ada di dalam fakta yang diketahui
    if goal in known_facts:
        print(f"{indent}[VALID] Fakta '{goal}' ditemukan pada data mahasiswa.")
        return True

    # 2. Jika goal tidak punya aturan pembentuk (fakta dasar tidak terpenuhi)
    if goal not in ATURAN_BACKWARD:
        print(f"{indent}[GAGAL] Fakta '{goal}' TIDAK ditemukan pada data mahasiswa.")
        return False

    # 3. Telusuri setiap cabang aturan yang menghasilkan goal
    for nama_aturan, subgoals in ATURAN_BACKWARD[goal]:
        print(f"{indent}[CEK {nama_aturan}] Membuktikan '{goal}' dengan syarat: {subgoals}")
        semua_terpenuhi = True
        for sg in subgoals:
            if not backward_chaining_beasiswa(sg, known_facts, depth + 1):
                semua_terpenuhi = False
                break

        if semua_terpenuhi:
            known_facts.add(goal)
            print(f"{indent}[TERBUKTI] Sub-goal '{goal}' berhasil dibuktikan melalui {nama_aturan}!")
            return True

    print(f"{indent}[TIDAK TERBUKTI] Goal '{goal}' gagal dibuktikan.")
    return False


# ==============================================================================
# 4. EKSEKUSI PENGUJIAN 3 PROFIL MAHASISWA BERBEDA
# ==============================================================================
def jalankan_pengujian_3_profil():
    semua_profil = siapkan_dataset_csv()
    tiga_profil_uji = semua_profil[:3]

    print("=" * 78)
    print("  SISTEM PAKAR SELEKSI BEASISWA KELAYAKAN MAHASISWA IDE LPKIA (SESI 7)")
    print("=" * 78)

    ringkasan = []

    for idx, mhs in enumerate(tiga_profil_uji, 1):
        fakta_awal = ekstrak_fakta_awal(mhs)
        rp_ortu = f"Rp {mhs['penghasilan_ortu']:,}".replace(",", ".")

        print(f"\nPROFIl UJI #{idx}: {mhs['nama']} (NIM: {mhs['nim']} - {mhs['prodi']})")
        print(
            f"  Atribut : IPK = {mhs['ipk']} | Penghasilan Ortu = {rp_ortu} | "
            f"Prestasi = {'Ya' if mhs['prestasi_akademik'] else 'Tidak'} | "
            f"Organisasi = {'Ya' if mhs['organisasi_aktif'] else 'Tidak'}"
        )
        print("-" * 78)

        # A. Forward Chaining
        print("  [A] EVALUASI FORWARD CHAINING:")
        lolos_fc, _, trace_fc = forward_chaining_beasiswa(fakta_awal)

        # B. Backward Chaining
        print("\n  [B] EVALUASI BACKWARD CHAINING (Hipotesis: 'BEASISWA_DISETUJUI'):")
        lolos_bc = backward_chaining_beasiswa("BEASISWA_DISETUJUI", set(fakta_awal))
        print(
            f"  [KEPUTUSAN BC]     : Hipotesis BEASISWA_DISETUJUI -> "
            f"{'TERBUKTI (DISETUJUI)' if lolos_bc else 'TIDAK TERBUKTI (DITOLAK)'}"
        )
        print("=" * 78)

        ringkasan.append({
            "nama": mhs["nama"],
            "ipk": mhs["ipk"],
            "ortu": rp_ortu,
            "jejak": " -> ".join([t.split(":")[0] for t in trace_fc]) if trace_fc else "Tidak ada aturan aktif",
            "status": "BEASISWA_DISETUJUI" if (lolos_fc and lolos_bc) else "DITOLAK",
        })

    print("\nRINGKASAN HASIL UJI 3 PROFIL MAHASISWA:")
    print("-" * 78)
    print(f"{'No':<4} {'Nama Mahasiswa':<18} {'IPK':<6} {'Penghasilan Ortu':<16} {'Jejak Aturan':<18} {'Hasil Akhir'}")
    print("-" * 78)
    for i, r in enumerate(ringkasan, 1):
        print(f"{i:<4} {r['nama']:<18} {r['ipk']:<6.2f} {r['ortu']:<16} {r['jejak']:<18} {r['status']}")
    print("=" * 78)


# ==============================================================================
# 5. RENDER VISUALISASI HTML NEUBRUTALISM DI GOOGLE COLAB
# ==============================================================================
HTML_NEUBRUTALISM = """<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    .nb-wrap {
      display: flex; flex-direction: row; gap: 18px; width: 100%; max-width: 960px;
      background: #ffffff; border: 4px solid #000000; border-radius: 6px;
      padding: 18px; box-shadow: 6px 6px 0px #000000; color: #000000;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
      margin: 12px 0;
    }
    .nb-left { flex: 1.05; display: flex; flex-direction: column; gap: 12px; }
    .nb-right { flex: 0.95; display: flex; flex-direction: column; gap: 12px; border-left: 3px solid #000000; padding-left: 18px; }
    .nb-header { border-bottom: 3px solid #000000; padding-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }
    .nb-title { font-size: 17px; font-weight: 900; text-transform: uppercase; letter-spacing: -0.4px; }
    .nb-pill { font-size: 11px; font-weight: 900; padding: 5px 10px; border: 3px solid #000000; box-shadow: 2px 2px 0px #000000; text-transform: uppercase; }
    .nb-ok { background: #22c55e; color: #000000; }
    .nb-no { background: #ef4444; color: #ffffff; }
    .nb-seg { display: flex; background: #ffffff; border: 3px solid #000000; box-shadow: 3px 3px 0px #000000; }
    .nb-btn { flex: 1; background: #ffffff; color: #000000; border: none; border-right: 3px solid #000000; padding: 7px 5px; font-size: 11px; font-weight: 900; cursor: pointer; text-transform: uppercase; }
    .nb-btn:last-child { border-right: none; }
    .nb-btn.active { background: #fde047; color: #000000; }
    .nb-btn.active-mode { background: #38bdf8; color: #000000; }
    .nb-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    .nb-card { background: #f8fafc; border: 3px solid #000000; padding: 9px; box-shadow: 3px 3px 0px #000000; display: flex; flex-direction: column; gap: 5px; }
    .nb-top { display: flex; justify-content: space-between; align-items: center; font-size: 11px; font-weight: 900; text-transform: uppercase; }
    .nb-badge { font-size: 10px; font-weight: 900; padding: 2px 6px; border: 2px solid #000000; }
    .nb-b-on { background: #22c55e; color: #000000; }
    .nb-b-off { background: #e2e8f0; color: #475569; }
    .nb-input { width: 100%; padding: 5px 8px; font-size: 13px; font-weight: 900; border: 2px solid #000000; background: #ffffff; color: #000000; }
    .nb-trow { display: flex; border: 2px solid #000000; }
    .nb-tbtn { flex: 1; padding: 4px 0; font-size: 11px; font-weight: 900; border: none; border-right: 2px solid #000000; background: #ffffff; color: #000000; cursor: pointer; }
    .nb-tbtn:last-child { border-right: none; }
    .nb-tbtn.on { background: #22c55e; color: #000000; }
    .nb-tbtn.off { background: #000000; color: #ffffff; }
    .nb-rules { display: flex; flex-direction: column; gap: 8px; }
    .nb-rule { border: 3px solid #000000; padding: 9px 11px; background: #f8fafc; box-shadow: 3px 3px 0px #000000; display: flex; justify-content: space-between; align-items: center; gap: 8px; }
    .nb-rule.fired { background: #fde047; }
    .nb-rcode { font-size: 11.5px; font-weight: 900; line-height: 1.35; }
    .nb-rtag { font-size: 10px; font-weight: 900; padding: 3px 7px; border: 2px solid #000000; background: #ffffff; text-transform: uppercase; }
    .nb-rule.fired .nb-rtag { background: #000000; color: #fde047; }
    .nb-box { background: #f8fafc; border: 3px solid #000000; padding: 10px; box-shadow: 3px 3px 0px #000000; }
    .nb-phead { font-size: 11px; font-weight: 900; text-transform: uppercase; border-bottom: 2px solid #000000; padding-bottom: 5px; margin-bottom: 7px; display: flex; justify-content: space-between; }
    .nb-fwrap { display: flex; flex-wrap: wrap; gap: 6px; }
    .nb-chip { font-size: 11px; font-weight: 900; padding: 3px 8px; border: 2px solid #000000; background: #38bdf8; color: #000000; }
    .nb-chip.goal { background: #22c55e; }
    .nb-trace { font-family: Consolas, monospace; font-size: 11px; font-weight: 700; line-height: 1.45; background: #ffffff; border: 2px solid #000000; padding: 8px; max-height: 180px; overflow-y: auto; white-space: pre-wrap; }
    .nb-tbl { width: 100%; border-collapse: collapse; font-size: 11px; background: #ffffff; border: 2px solid #000000; }
    .nb-tbl th { background: #000000; color: #ffffff; padding: 5px; text-align: left; font-weight: 900; text-transform: uppercase; }
    .nb-tbl td { padding: 5px; border-bottom: 2px solid #000000; font-weight: 800; cursor: pointer; color: #000000; }
    .nb-tbl tr:hover td { background: #fef9c3; }
    .nb-tok { color: #15803d !important; font-weight: 900; }
    .nb-tno { color: #b91c1c !important; font-weight: 900; }
  </style>
</head>
<body>
<div class="nb-wrap">
  <div class="nb-left">
    <div class="nb-header">
      <div class="nb-title">SELEKSI BEASISWA IDE LPKIA</div>
      <div id="nb-pill" class="nb-pill nb-ok">BEASISWA DISETUJUI</div>
    </div>
    <div class="nb-seg" id="nb-ptabs">
      <button class="nb-btn active" onclick="nbSelect(0)">Mhs 1: Rizky</button>
      <button class="nb-btn" onclick="nbSelect(1)">Mhs 2: Nadia</button>
      <button class="nb-btn" onclick="nbSelect(2)">Mhs 3: Dimas</button>
      <button class="nb-btn" onclick="nbSelect(3)">Mhs 4: Siti</button>
    </div>
    <div class="nb-seg">
      <button class="nb-btn active-mode" id="nb-fc" onclick="nbMode('forward')">Forward Chaining</button>
      <button class="nb-btn" id="nb-bc" onclick="nbMode('backward')">Backward Chaining</button>
    </div>
    <div class="nb-grid">
      <div class="nb-card">
        <div class="nb-top"><span>IPK (>= 3.5)</span><span id="nb-bipk" class="nb-badge nb-b-on">VALID</span></div>
        <input type="number" id="nb-ipk" class="nb-input" step="0.01" min="0" max="4" value="3.78" oninput="nbCustom()">
      </div>
      <div class="nb-card">
        <div class="nb-top"><span>Ortu (< 3.000.000)</span><span id="nb-bortu" class="nb-badge nb-b-on">VALID</span></div>
        <input type="number" id="nb-ortu" class="nb-input" step="100000" min="0" value="2400000" oninput="nbCustom()">
      </div>
      <div class="nb-card">
        <div class="nb-top"><span>Prestasi Akademik</span><span id="nb-bpres" class="nb-badge nb-b-off">TIDAK</span></div>
        <div class="nb-trow">
          <button type="button" id="nb-pya" class="nb-tbtn" onclick="nbTog('prestasi', true)">YA</button>
          <button type="button" id="nb-pno" class="nb-tbtn off" onclick="nbTog('prestasi', false)">TIDAK</button>
        </div>
      </div>
      <div class="nb-card">
        <div class="nb-top"><span>Organisasi Aktif</span><span id="nb-borg" class="nb-badge nb-b-off">TIDAK</span></div>
        <div class="nb-trow">
          <button type="button" id="nb-oya" class="nb-tbtn" onclick="nbTog('org', true)">YA</button>
          <button type="button" id="nb-ono" class="nb-tbtn off" onclick="nbTog('org', false)">TIDAK</button>
        </div>
      </div>
    </div>
    <div class="nb-rules">
      <div class="nb-rule" id="nb-cr1">
        <div class="nb-rcode">R1: IF IPK >= 3.5 AND OrangTua_KurangMampu<br>THEN Layak_Ekonomi</div>
        <div class="nb-rtag" id="nb-tr1">TERPEMICU</div>
      </div>
      <div class="nb-rule" id="nb-cr2">
        <div class="nb-rcode">R2: IF IPK >= 3.5 AND (Prestasi_Akademik OR Organisasi_Aktif)<br>THEN Layak_Prestasi</div>
        <div class="nb-rtag" id="nb-tr2">LEWAT</div>
      </div>
      <div class="nb-rule" id="nb-cr3">
        <div class="nb-rcode">R3: IF Layak_Ekonomi OR Layak_Prestasi<br>THEN BEASISWA_DISETUJUI</div>
        <div class="nb-rtag" id="nb-tr3">TERPEMICU</div>
      </div>
    </div>
  </div>
  <div class="nb-right">
    <div class="nb-box">
      <div class="nb-phead"><span>Working Memory</span><span id="nb-fcount">3 Fakta</span></div>
      <div class="nb-fwrap" id="nb-fwrap"></div>
    </div>
    <div class="nb-box">
      <div class="nb-phead"><span id="nb-ttitle">Inference Trace (Forward Chaining)</span></div>
      <div class="nb-trace" id="nb-trace"></div>
    </div>
    <div class="nb-box">
      <div class="nb-phead"><span>Dataset Uji Mahasiswa</span></div>
      <table class="nb-tbl">
        <thead><tr><th>Nama</th><th>IPK</th><th>Ortu</th><th>Pres/Org</th><th>Status</th></tr></thead>
        <tbody id="nb-tbody"></tbody>
      </table>
    </div>
  </div>
</div>
<script>
(function() {
  const profs = [
    { nama: "Rizky Pratama", ipk: 3.78, ortu: 2400000, prestasi: false, org: false },
    { nama: "Nadia Maharani", ipk: 3.65, ortu: 5500000, prestasi: true, org: true },
    { nama: "Dimas Anggara", ipk: 3.25, ortu: 2200000, prestasi: false, org: true },
    { nama: "Siti Nurhaliza", ipk: 3.85, ortu: 2800000, prestasi: true, org: true }
  ];
  let mode = "forward";
  let st = { ...profs[0] };

  function getFacts(s) {
    const f = [];
    if (s.ipk >= 3.5) f.push("IPK >= 3.5");
    if (s.ortu < 3000000) f.push("OrangTua_KurangMampu");
    if (s.prestasi) f.push("Prestasi_Akademik");
    if (s.org) f.push("Organisasi_Aktif");
    return f;
  }

  function evalFC(init) {
    const k = new Set(init);
    const tr = [`[AWAL] Fakta: ${JSON.stringify(Array.from(k))}`];
    const fired = { R1: false, R2: false, R3: false };
    let step = 1, chg = true;
    while (chg) {
      chg = false;
      tr.push(`\\n--- ITERASI ${step} ---`);
      if (k.has("IPK >= 3.5") && k.has("OrangTua_KurangMampu") && !k.has("Layak_Ekonomi")) {
        k.add("Layak_Ekonomi"); fired.R1 = true; chg = true;
        tr.push("[R1 AKTIF] IF IPK >= 3.5 AND OrangTua_KurangMampu -> +Layak_Ekonomi");
        step++; continue;
      } else tr.push(`[R1 LEWAT] ${k.has("Layak_Ekonomi") ? "Sudah ada" : "Syarat belum terpenuhi"}`);

      if (k.has("IPK >= 3.5") && (k.has("Prestasi_Akademik") || k.has("Organisasi_Aktif")) && !k.has("Layak_Prestasi")) {
        k.add("Layak_Prestasi"); fired.R2 = true; chg = true;
        tr.push("[R2 AKTIF] IF IPK >= 3.5 AND (Prestasi/Organisasi) -> +Layak_Prestasi");
        step++; continue;
      } else tr.push(`[R2 LEWAT] ${k.has("Layak_Prestasi") ? "Sudah ada" : "Syarat belum terpenuhi"}`);

      if ((k.has("Layak_Ekonomi") || k.has("Layak_Prestasi")) && !k.has("BEASISWA_DISETUJUI")) {
        k.add("BEASISWA_DISETUJUI"); fired.R3 = true; chg = true;
        tr.push("[R3 AKTIF] IF Layak_Ekonomi OR Layak_Prestasi -> +BEASISWA_DISETUJUI");
        step++; continue;
      } else tr.push(`[R3 LEWAT] ${k.has("BEASISWA_DISETUJUI") ? "Sudah ada" : "Syarat belum terpenuhi"}`);
    }
    const ok = k.has("BEASISWA_DISETUJUI");
    tr.push(`\\n[HASIL] ${ok ? "BEASISWA_DISETUJUI (LOLOS)" : "BEASISWA_DITOLAK (TIDAK LOLOS)"}`);
    return { known: Array.from(k), trace: tr.join("\\n"), fired, ok };
  }

  function evalBC(init) {
    const k = new Set(init);
    const tr = ["[HIPOTESIS AWAL] Membuktikan Goal: 'BEASISWA_DISETUJUI'\\n"];
    const fired = { R1: false, R2: false, R3: false };
    const rmap = {
      "BEASISWA_DISETUJUI": [
        { id: "R3 (Jalur Ekonomi)", req: ["Layak_Ekonomi"], c: "R3" },
        { id: "R3 (Jalur Prestasi)", req: ["Layak_Prestasi"], c: "R3" }
      ],
      "Layak_Ekonomi": [{ id: "R1", req: ["IPK >= 3.5", "OrangTua_KurangMampu"], c: "R1" }],
      "Layak_Prestasi": [
        { id: "R2 (Prestasi)", req: ["IPK >= 3.5", "Prestasi_Akademik"], c: "R2" },
        { id: "R2 (Organisasi)", req: ["IPK >= 3.5", "Organisasi_Aktif"], c: "R2" }
      ]
    };
    function prove(g, d) {
      const pad = "  ".repeat(d);
      if (k.has(g)) { tr.push(`${pad}[FAKTA VALID] '${g}' ditemukan`); return true; }
      if (!rmap[g]) { tr.push(`${pad}[GAGAL] '${g}' tidak ditemukan`); return false; }
      for (const b of rmap[g]) {
        tr.push(`${pad}[CEK ${b.id}] Buktikan '${g}' <- ${JSON.stringify(b.req)}`);
        let m = true;
        for (const s of b.req) { if (!prove(s, d + 1)) { m = false; break; } }
        if (m) { k.add(g); fired[b.c] = true; tr.push(`${pad}[TERBUKTI] '${g}' VALID via ${b.id}`); return true; }
      }
      tr.push(`${pad}[TIDAK TERBUKTI] '${g}' gagal dibuktikan`);
      return false;
    }
    const ok = prove("BEASISWA_DISETUJUI", 0);
    tr.push(`\\n[KESIMPULAN] Hipotesis BEASISWA_DISETUJUI = ${ok ? "TERBUKTI (DISETUJUI)" : "TIDAK TERBUKTI (DITOLAK)"}`);
    return { known: Array.from(k), trace: tr.join("\\n"), fired, ok };
  }

  function render() {
    const iv = st.ipk >= 3.5, ov = st.ortu < 3000000;
    const bi = document.getElementById("nb-bipk"); bi.textContent = iv ? "VALID" : "TIDAK"; bi.className = "nb-badge " + (iv ? "nb-b-on" : "nb-b-off");
    const bo = document.getElementById("nb-bortu"); bo.textContent = ov ? "VALID" : "TIDAK"; bo.className = "nb-badge " + (ov ? "nb-b-on" : "nb-b-off");
    const bp = document.getElementById("nb-bpres"); bp.textContent = st.prestasi ? "YA" : "TIDAK"; bp.className = "nb-badge " + (st.prestasi ? "nb-b-on" : "nb-b-off");
    const bg = document.getElementById("nb-borg"); bg.textContent = st.org ? "YA" : "TIDAK"; bg.className = "nb-badge " + (st.org ? "nb-b-on" : "nb-b-off");

    document.getElementById("nb-pya").className = "nb-tbtn " + (st.prestasi ? "on" : "");
    document.getElementById("nb-pno").className = "nb-tbtn " + (!st.prestasi ? "off" : "");
    document.getElementById("nb-oya").className = "nb-tbtn " + (st.org ? "on" : "");
    document.getElementById("nb-ono").className = "nb-tbtn " + (!st.org ? "off" : "");

    const f = getFacts(st);
    const res = mode === "forward" ? evalFC(f) : evalBC(f);
    const pill = document.getElementById("nb-pill");
    pill.textContent = res.ok ? "BEASISWA DISETUJUI" : "BEASISWA DITOLAK";
    pill.className = "nb-pill " + (res.ok ? "nb-ok" : "nb-no");

    ["R1", "R2", "R3"].forEach(r => {
      const c = document.getElementById("nb-c" + r.toLowerCase());
      const t = document.getElementById("nb-t" + r.toLowerCase());
      if (res.fired[r]) { c.classList.add("fired"); t.textContent = "TERPEMICU"; }
      else { c.classList.remove("fired"); t.textContent = "LEWAT"; }
    });

    document.getElementById("nb-fcount").textContent = `${res.known.length} Fakta`;
    document.getElementById("nb-fwrap").innerHTML = res.known.length
      ? res.known.map(x => `<span class="nb-chip ${x === 'BEASISWA_DISETUJUI' ? 'goal' : ''}">${x}</span>`).join("")
      : `<span class="nb-chip" style="background:#e2e8f0;">Tidak ada fakta memenuhi syarat</span>`;

    document.getElementById("nb-ttitle").textContent = `Inference Trace (${mode === "forward" ? "Forward Chaining" : "Backward Chaining"})`;
    document.getElementById("nb-trace").textContent = res.trace;

    document.getElementById("nb-tbody").innerHTML = profs.map((p, i) => {
      const r = evalFC(getFacts(p));
      return `<tr onclick="nbSelect(${i})">
        <td>${p.nama}</td><td>${p.ipk.toFixed(2)}</td><td>Rp ${(p.ortu/1000000).toFixed(1)} Jt</td>
        <td>${p.prestasi ? "Ya" : "-"}/${p.org ? "Ya" : "-"}</td>
        <td class="${r.ok ? 'nb-tok' : 'nb-tno'}">${r.ok ? "DISETUJUI" : "DITOLAK"}</td>
      </tr>`;
    }).join("");
  }

  window.nbSelect = function(i) {
    st = { ...profs[i] };
    document.getElementById("nb-ipk").value = st.ipk;
    document.getElementById("nb-ortu").value = st.ortu;
    document.querySelectorAll("#nb-ptabs .nb-btn").forEach((b, idx) => b.classList.toggle("active", idx === i));
    render();
  };
  window.nbMode = function(m) {
    mode = m;
    document.getElementById("nb-fc").classList.toggle("active-mode", m === "forward");
    document.getElementById("nb-bc").classList.toggle("active-mode", m === "backward");
    render();
  };
  window.nbTog = function(k, v) {
    st[k] = v;
    document.querySelectorAll("#nb-ptabs .nb-btn").forEach(b => b.classList.remove("active"));
    render();
  };
  window.nbCustom = function() {
    st.ipk = parseFloat(document.getElementById("nb-ipk").value) || 0;
    st.ortu = parseFloat(document.getElementById("nb-ortu").value) || 0;
    document.querySelectorAll("#nb-ptabs .nb-btn").forEach(b => b.classList.remove("active"));
    render();
  };
  render();
})();
</script>
</body>
</html>"""


def tampilkan_visualisasi_colab():
    """Menampilkan UI HTML Neubrutalism secara otomatis jika dijalankan di Google Colab."""
    try:
        from IPython.display import HTML, display
        if "google.colab" not in sys.modules and "ipykernel" not in sys.modules:
            return
        html_path = (
            os.path.join(os.path.dirname(__file__), "P7C.html")
            if "__file__" in globals()
            else "P7C.html"
        )
        if os.path.exists(html_path):
            with open(html_path, "r", encoding="utf-8") as f:
                display(HTML(f.read()))
        else:
            display(HTML(HTML_NEUBRUTALISM))
    except Exception:
        pass


if __name__ == "__main__":
    jalankan_pengujian_3_profil()
    tampilkan_visualisasi_colab()
