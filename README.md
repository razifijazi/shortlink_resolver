# shortlink_resolver

Resolver HTTP sederhana untuk shortlink model interstitial + form submit, dengan dashboard web untuk resolve banyak link sekaligus.

## Fitur
- Resolve shortlink model interstitial + countdown + form submit
- Support multi-link input (satu link per baris)
- Tombol per item:
  - Copy link hasil
  - Open in new tab
- Kolom **Final Links Only** di sisi kanan
- Tombol **Copy All Results**
- Dashboard/web UI di port `4050`

## Flow yang saat ini didukung
Contoh domain seperti `link.com`:
1. GET halaman shortlink
2. Parse form `go-popup` dan `go-link`
3. Submit `go-popup` (`/links/popad`)
4. Tunggu countdown
5. Submit `go-link` (`/links/go`)
6. Ambil final URL dari response JSON

## Requirements
- Python 3.10+ (tested on Python 3.12)
- Package Python:
  - `requests`

Install dependency jika belum ada:
```bash
pip install requests
```

## Struktur file
```text
shortlink_resolver/
├── README.md
├── app.py
├── resolve.py
└── .gitignore
```

## Menjalankan via CLI
Resolve satu shortlink:
```bash
cd shortlink_resolver
python3 resolve.py 'https://link.com/u4O54dM'
```

Contoh output:
```text
https://link.com/download/8w0j3fms815x
```

## Menjalankan dashboard web
Masuk ke folder project:
```bash
cd shortlink_resolver
```

Lalu jalankan:
```bash
python3 app.py
```

Secara default dashboard aktif di:
```text
http://127.0.0.1:4050
```

Kalau server punya IP publik dan port dibuka, bisa diakses dari browser lain lewat:
```text
http://IP-VPS:4050
```

## Deploy sebagai website biasa di aaPanel (tanpa port di URL)
App ini sekarang kompatibel dengan **WSGI**, jadi bisa dijalankan sebagai website biasa lewat domain/subdomain di aaPanel tanpa mengubah fungsi.

### Opsi 1 — Python Project / WSGI di aaPanel
Kalau aaPanel kamu punya menu **Python Project**:

- **Project path:** folder repo `shortlink_resolver`
- **Startup file / module:** `app`
- **Application callable:** `application`
- **Python version:** 3.x
- **Requirements:** install package `requests`

Konsepnya: aaPanel akan menjalankan WSGI app `app:application`, lalu domain diarahkan langsung ke app ini. Jadi user akses lewat:

```text
https://subdomain-kamu.com
```

bukan `:4050`.

### Opsi 2 — Tetap pakai mode lama
Kalau tidak pakai WSGI, mode lama masih tetap bisa dipakai:

```bash
python3 app.py
```

Jadi perubahan ini **tidak mengubah fungsi resolver**, hanya menambah mode deploy yang lebih enak buat hosting panel.

## Menjalankan di background
Cara sederhana:
```bash
nohup python3 app.py >/tmp/shortlink_resolver_4050.log 2>&1 &
```

Cek apakah port aktif:
```bash
ss -ltnp | grep 4050
```

Lihat log:
```bash
tail -f /tmp/shortlink_resolver_4050.log
```

Matikan proses di port 4050:
```bash
fuser -k 4050/tcp
```

## Membuka akses dashboard dari luar VPS
Kalau dashboard tidak bisa diakses dari browser luar, cek firewall.

### Uji lokal di VPS
```bash
curl http://127.0.0.1:4050
```

### Kalau pakai UFW
Buka port 4050:
```bash
sudo ufw allow 4050/tcp
sudo ufw reload
sudo ufw status
```

### Kalau pakai firewall provider / security group
Pastikan rule inbound TCP `4050` dibuka juga di panel provider VPS.

## Cara pakai dashboard
1. Buka dashboard
2. Paste satu atau banyak shortlink, satu per baris
3. Klik **Submit**
4. Hasil akan muncul:
   - panel kiri: hasil detail per item
   - panel kanan: **Final Links Only**
5. Gunakan:
   - **Copy link #N** untuk copy satu hasil
   - **Open in new tab** untuk buka satu hasil
   - **Copy All Results** untuk copy semua final link sekaligus

## Catatan penting
- Resolver ini saat ini dituning untuk flow seperti `link.com`
- Tidak semua shortlink service punya flow yang sama
- Beberapa domain mungkin butuh penyesuaian tambahan
- Countdown saat ini mengikuti nilai timer halaman (maksimal 10 detik)

## Deploy cepat di VPS baru
```bash
git clone https://github.com/razifijazi/shortlink_resolver.git
cd shortlink_resolver
pip install requests
nohup python3 app.py >/tmp/shortlink_resolver_4050.log 2>&1 &
ss -ltnp | grep 4050
```

Lalu buka:
```text
http://IP-VPS:4050
```

## Troubleshooting
### Dashboard kebuka tapi submit gagal
Cek log:
```bash
tail -100 /tmp/shortlink_resolver_4050.log
```

### Port tidak bisa diakses dari luar
- cek `curl http://127.0.0.1:4050`
- cek firewall UFW / firewall provider

### Hasil tidak keluar link final
Berarti kemungkinan flow domain target berbeda dari flow yang saat ini sudah di-handle.
