"""Metinden dijital ikiz videosu: ElevenLabs ses -> HeyGen'e yükle -> video üret -> indir.

Kullanım:
  python ikiz_video.py metin.txt video_adi --sadece-ses   # önce sesi üret, dinle
  python ikiz_video.py metin.txt video_adi --ses video_adi.mp3   # onayladığın sesle videoyu üret
  python ikiz_video.py metin.txt video_adi                 # ikisi birden

Ortam değişkenleri (değerleri koda ve sohbete yazma, .env dosyasında tut):
  ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID, HEYGEN_API_KEY, HEYGEN_AVATAR_ID
Yalnız Python standart kütüphanesi kullanır.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid

EL = os.environ.get("ELEVENLABS_BASE", "https://api.elevenlabs.io")
HG = os.environ.get("HEYGEN_BASE", "https://api.heygen.com")
BEKLEME_SN = int(os.environ.get("BEKLEME_SN", "15"))


def gerekli(ad):
    deger = os.environ.get(ad)
    if not deger:
        sys.exit(f"Eksik ortam değişkeni: {ad}")
    return deger


def istek(url, veri=None, basliklar=None, yontem=None):
    req = urllib.request.Request(url, data=veri, headers=basliklar or {}, method=yontem)
    try:
        with urllib.request.urlopen(req, timeout=300) as yanit:
            return yanit.read()
    except urllib.error.HTTPError as hata:
        govde = hata.read().decode("utf-8", "replace")[:500]
        sys.exit(f"HTTP {hata.code} {url.split('?')[0]}\n{govde}")


def ses_uret(metin, cikti):
    ses = gerekli("ELEVENLABS_VOICE_ID")
    url = f"{EL}/v1/text-to-speech/{ses}?output_format=mp3_44100_128"
    govde = json.dumps({"text": metin, "model_id": "eleven_multilingual_v2"}).encode("utf-8")
    mp3 = istek(url, govde, {"xi-api-key": gerekli("ELEVENLABS_API_KEY"),
                             "Content-Type": "application/json"}, "POST")
    with open(cikti, "wb") as f:
        f.write(mp3)
    print(f"Ses hazır: {cikti} ({len(mp3)} bayt)")


def yukle(dosya):
    sinir = uuid.uuid4().hex
    with open(dosya, "rb") as f:
        icerik = f.read()
    govde = (f"--{sinir}\r\nContent-Disposition: form-data; name=\"file\"; "
             f"filename=\"{os.path.basename(dosya)}\"\r\nContent-Type: audio/mpeg\r\n\r\n").encode()
    govde += icerik + f"\r\n--{sinir}--\r\n".encode()
    yanit = istek(f"{HG}/v3/assets", govde,
                  {"X-Api-Key": gerekli("HEYGEN_API_KEY"),
                   "Content-Type": f"multipart/form-data; boundary={sinir}"}, "POST")
    asset_id = json.loads(yanit)["data"]["asset_id"]
    print(f"Ses yüklendi: {asset_id}")
    return asset_id


def video_baslat(asset_id, baslik):
    govde = json.dumps({
        "type": "avatar",
        "avatar_id": gerekli("HEYGEN_AVATAR_ID"),
        "audio_asset_id": asset_id,
        "title": baslik,
        "aspect_ratio": "auto",
        "resolution": "1080p",
    }).encode("utf-8")
    yanit = istek(f"{HG}/v3/videos", govde,
                  {"X-Api-Key": gerekli("HEYGEN_API_KEY"), "Content-Type": "application/json"}, "POST")
    video_id = json.loads(yanit)["data"]["video_id"]
    print(f"Video başladı: {video_id}")
    return video_id


def bekle(video_id, en_cok_dk=60):
    bitis = time.time() + en_cok_dk * 60
    while time.time() < bitis:
        veri = json.loads(istek(f"{HG}/v3/videos/{video_id}",
                                basliklar={"X-Api-Key": gerekli("HEYGEN_API_KEY")}))["data"]
        durum = veri.get("status")
        print(f"  durum: {durum}")
        if durum == "completed":
            return veri["video_url"]
        if durum == "failed":
            sys.exit(f"Video üretilemedi: {veri.get('failure_message') or veri.get('failure_code')}")
        time.sleep(BEKLEME_SN)
    sys.exit("Süre doldu; videoyu HeyGen panelinden kontrol et.")


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    metin_dosyasi, ad = sys.argv[1], sys.argv[2]
    sadece_ses = "--sadece-ses" in sys.argv
    hazir_ses = sys.argv[sys.argv.index("--ses") + 1] if "--ses" in sys.argv else None

    lazim = [] if hazir_ses else ["ELEVENLABS_API_KEY", "ELEVENLABS_VOICE_ID"]
    if not sadece_ses:
        lazim += ["HEYGEN_API_KEY", "HEYGEN_AVATAR_ID"]
    for degisken in lazim:
        gerekli(degisken)

    mp3 = hazir_ses or f"{ad}.mp3"
    if not hazir_ses:
        with open(metin_dosyasi, encoding="utf-8") as f:
            ses_uret(f.read().strip(), mp3)
    if sadece_ses:
        print("Sesi dinle. Beğendiysen: --ses ile video adımını çalıştır.")
        return
    video_url = bekle(video_baslat(yukle(mp3), ad))
    with open(f"{ad}.mp4", "wb") as f:
        f.write(istek(video_url))
    print(f"Video hazır: {ad}.mp4")


if __name__ == "__main__":
    main()
