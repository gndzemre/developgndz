# Dijital ikiz kurulumu: görüntü, ses, yönetim

> Videodaki vaat: *"Kurulumu adım adım anlattığım rehberi hazırladım."*
> Sıra videodakiyle aynı, üç parça ve üçü de bir kerelik: **görüntü** (HeyGen'e tek çekim) ·
> **ses** (ElevenLabs'e uzun kayıt) · **yönetim** (senaryoyu yazan, sesi üreten, ikize gönderen Claude Code).

Kurulum bitince her video için yaptığın iş: konuyu söylemek, metni okuyup onaylamak, sesi dinlemek,
çıkan videoya bakmak. Kamera, ışık, makyaj yok.

---

## 1 · Görüntü: HeyGen'e tek çekim

HeyGen'de bunun adı **Digital Twin** (video avatar). Bir kez çekiyorsun, sonra her metni o görüntüyle
söyletebiliyorsun.

### Çekim

| | HeyGen'in istediği |
|---|---|
| Süre | En az 2 dakika, önerilen 5 dakikaya kadar. Yükleme sınırı 30 saniye – 5 dakika. |
| Kalite | En az 1080p, 30 fps. 4K / 60 fps daha iyi. Telefon, web kamerası, profesyonel kamera olur. |
| Bütünlük | **Tek parça kesintisiz kayıt.** Kesme, geçiş, birleştirme yok. |
| Bakış | Doğrudan objektife. Yüz baştan sona kameraya dönük. |
| Işık ve fon | Parlak, eşit ışık, sert gölge yok. Sade, sabit fon. |
| Ses | Sessiz oda ve **çekimde kendi sesin olmalı.** Sonra başka bir sesle konuşturacak olsan bile HeyGen dudak senkronu için bunu istiyor. |
| Eller | Hareket serbest ama kadrajda kalsın, yüzü ve ağzı kapatmasın. |
| Duraklar | Susarken de yüzün canlı kalsın (hafif gülümseme, tepki); avatarın "boşta" hâli buradan çıkıyor. |

Pratik notlar:

- **Videolarını dikey (Reels/Shorts) yayınlayacaksan dikey çek.** Yatay çekip sonradan dikeye kırparsan
  yüzün etrafındaki dar alan büyütülür, keskinlik düşer.
- **Kıyafeti ve ortamı çekimde seç.** HeyGen'in yardım sayfasına göre video avatarlarda üretken kıyafet
  değiştirme yok. Başka kıyafet istiyorsan aynı avatara o kıyafetle ayrı bir çekim ekle.
- Çekimi yüklemeden önce kendin kontrol et (süre, çözünürlük, kare hızı, ses kanalı var mı):

```bash
ffprobe -v error -show_entries format=duration:stream=codec_type,width,height,avg_frame_rate -of compact=p=0 cekim.mp4
```

Çıktıda bir `codec_type=video` ve bir `codec_type=audio` satırı görmelisin. `audio` satırı yoksa
HeyGen çekimi "ses yok" diye reddeder.

### HeyGen'de oluşturma

1. **Avatars** → **New Avatar** → **Clone a Real Person**.
2. Çekimi yükle (ya da orada canlı çek).
3. **Onay videosu (consent):** kameraya bakıp ekranda çıkan kodu okursun. Onay videosundaki kişi ile
   çekimdeki kişi aynı olmalı; başkasının görüntüsüyle ikiz kurulmuyor.
4. İşlem bitince avatarın hazır. Ret gelirse HeyGen sebebini açık hata koduyla söylüyor
   (yüz bulunamadı, ses yok, birden fazla sahne, yüz açısı büyük…).

🔴 HeyGen üst üste **3 başarısız denemenin** avatar yasağıyla sonuçlanabileceğini yazıyor. Yüklemeden önce
tablodaki maddeleri gerçekten kontrol et.

---

## 2 · Ses: ElevenLabs'e uzun kayıt

ElevenLabs'te bunun adı **Professional Voice Clone (PVC)**. Kısa örnekten yapılan hızlı klondan farkı:
nefesini, duraklarını, vurgularını öğrenmesi.

### Kayıt

| | ElevenLabs'in önerisi |
|---|---|
| Süre | Alt sınır olarak önerilen **30 dakika**; en iyi sonuç için **2–3 saate** yakın. Yükleme adımı en az 1 saat öneriyor. |
| Konuşmacı | Baştan sona **tek ses**. Başka kişi, müzik, arka plan gürültüsü yok. |
| Üslup | Tek tarz. Videolarda nasıl konuşacaksan kayıtta da öyle konuş. |
| Ortam | Mümkünse akustiği düzenlenmiş oda; ses kartına bağlı XLR mikrofon öneriliyor ama her mikrofon çalışır. |
| Biçim | MP3, **192 kbps veya üstü**. |

Kayıt toplamını yüklemeden önce ölç:

```bash
for f in kayit/*.mp3; do ffprobe -v error -show_entries format=duration -of csv=p=0 "$f"; done | awk '{s+=$1} END {printf "%.1f dakika\n", s/60}'
```

### ElevenLabs'te oluşturma

1. Voices → yeni ses → **Professional Voice Clone**. PVC, **Creator ve üstü** planlarda var
   (Creator ve Pro'da 1 PVC hakkı). Free ve Starter'da yok.
2. Kayıtları yükle.
3. **Ses doğrulaması:** sesin sahibi olduğunu kanıtlamak için ekranda çıkan satırları okursun.
   Aynı mikrofon ve aynı tonla oku.
4. Eğitim birkaç saat sürer (ElevenLabs 3–6 saat, sıra yoğunsa daha uzun diyor).
5. Klon **Flash v2.5, Turbo v2.5 ve Multilingual v2** modelleri için eğitilir. Türkçe ya da İngilizce dışı
   içerik için Multilingual v2 kullan (HeyGen'in ses rehberi de aksanı korumak için bunu öneriyor).

🔴 Ham kayıtlarını sakla. Klonu yeniden eğitmen ya da başka bir yere kurman gerekirse elindeki tek
kaynak onlar. Ayrıca planı Creator'ın altına düşürürsen klon hesapta kalır ama kullanılamaz.

### Sesi HeyGen'e bağlamak (panelden çalışacaksan)

HeyGen'in AI Studio'sunda: avatar → Voice → **+ New Voice** → **Integrate 3rd Party Voice** →
**Import Voice** → ElevenLabs → API anahtarını yapıştır → **Confirm**. ElevenLabs sesin artık HeyGen
içinde seçilebilir. "Invalid API key" alırsan ElevenLabs anahtarında şu izinleri aç: Text to Speech,
Voices, Voice Generation, Models, History, User.

HeyGen'in SSS'ine göre her video avatar kendi ses klonuyla geliyor; benim hesabımda avatarın varsayılan
sesi bu klondu, ElevenLabs sesi değil. Panelden video üretmeden önce hangi sesin seçili olduğuna bak.

---

## 3 · Yönetim: Claude Code

Videodaki "senaryoyu yazan, sesi üreten, ikizime gönderen" kısım. İki yol var.

### Yol A · MCP: anahtarsız, tarayıcıdan giriş

HeyGen'in resmî MCP sunucusu:

```bash
claude mcp add --transport http heygen https://mcp.heygen.com/mcp/v1/
```

Claude Code'da `/mcp` → `heygen` → tarayıcıda onay. Sonra doğal dille iste. HeyGen'e göre bu yol
**abonelik kredini** kullanır ve küçük denemeler için uygun; seri üretim için API anahtarını öneriyor.

ElevenLabs'in de barındırılan (hosted) MCP sunucusu var: `https://api.elevenlabs.io/v1/mcp`, OAuth ile
giriş, içinde metinden ses üretme aracı da bulunuyor. Eski yerel ElevenLabs MCP sunucusu kullanımdan
kaldırıldı.

### Yol B · API: tekrarlanabilir hat (önerdiğim)

Her video aynı adımlardan geçiyorsa bunu bir betiğe bağla, Claude Code betiği çalıştırsın. Bu sayfanın
yanındaki **`ikiz_video.py`** tam olarak bunu yapıyor (yalnız Python standart kütüphanesi):

1. Metni ElevenLabs'e gönderir, kendi sesinle MP3 üretir
   (`POST /v1/text-to-speech/{voice_id}`, model `eleven_multilingual_v2`).
2. MP3'ü HeyGen'e yükler (`POST /v3/assets`).
3. İkizinle videoyu başlatır (`POST /v3/videos`, `type: avatar`, `audio_asset_id`).
4. Bitene kadar durumu sorar (`GET /v3/videos/{video_id}`), sonra MP4'ü indirir.

Anahtarları proje klasöründe bir `.env` dosyasına koy ve `.gitignore`'a ekle:

```bash
ELEVENLABS_API_KEY=<ELEVENLABS_ANAHTARIN>
ELEVENLABS_VOICE_ID=<PVC_SES_KIMLIGIN>
HEYGEN_API_KEY=<HEYGEN_ANAHTARIN>
HEYGEN_AVATAR_ID=<IKIZ_LOOK_KIMLIGIN>
```

`HEYGEN_AVATAR_ID`, avatarın look kimliği (HeyGen'de `GET /v3/avatars/looks` ile listelenir).
🔴 HeyGen'e göre API anahtarıyla yapılan üretim **API faturasına** yazılır, web aboneliğinin kredisinden
düşmez. Başlamadan önce hesabındaki API bakiyesini ve ücret sayfasını kontrol et.

Kullanım (Bash; `.env`'i ortama yükleyip çalıştırır):

```bash
set -a; source .env; set +a
python ikiz_video.py metin.txt bolum_01 --sadece-ses   # önce sesi üret, dinle
python ikiz_video.py metin.txt bolum_01 --ses bolum_01.mp3   # beğendiysen videoyu üret
```

Sesi videodan önce ayrı dinlemek bilinçli: ses beğenilmezse video kredisi harcanmamış olur.

### Claude Code'a verilecek çalışma talimatı

Proje klasörüne `CLAUDE.md` olarak koy, Claude Code her oturumda okusun:

```markdown
# Dijital ikiz video hattı

Ben yalnız konuyu söylerim. Sen sırayla:
1. Metni yaz: 60 saniye için Türkçede yaklaşık 130–150 kelime. Konuşur gibi, kısa cümleler.
   Sayıları yazıyla yaz ("3" değil "üç"); okunuşu karışabilecek kısaltmaları açık yaz.
   Metni metinler/<tarih>_<konu>.txt dosyasına kaydet ve bana göster. ONAYIMI BEKLE.
2. Onaylarsam: `python ikiz_video.py <metin> <ad> --sadece-ses` çalıştır. Sesi dinlememi iste. ONAYIMI BEKLE.
3. Onaylarsam: `python ikiz_video.py <metin> <ad> --ses <ad>.mp3` çalıştır, videonun yolunu söyle.

Kurallar:
- .env dosyasını okuma, içindeki değerleri hiçbir yere yazma.
- Onayım olmadan ses veya video üretme; her üretim kredi harcar.
- Hata alırsan aynı isteği körlemesine tekrarlama, hatayı bana göster.
```

Metin kalitesi için kendi tarzını öğret: daha önce yazdığın ya da konuştuğun 10–20 metni bir klasöre
koy ve CLAUDE.md'ye "metni bu örneklerin üslubuyla yaz, benim kullanmayacağım kelimeleri kullanma" ekle.

---

## Bilmen gerekenler

- **Yapay zekâ etiketi.** Instagram, gerçekçi görünen yapay zekâ videosu ya da gerçekçi sesli içerik
  paylaşırken "AI info" etiketini senin eklemeni istiyor. Paylaşmadan önce Instagram'ın yardım sayfasını kontrol et.
- **Ağız bölgesi sentez.** Benim denemelerimde ağız çevresindeki detay gerçek çekimden belirgin biçimde
  düşüktü; yakın planda fark edilebiliyor. Ham çıktıyı tek başına yayınlamak yerine araya ekran görüntüsü
  ve görsel kesmeler koymak bunu örtüyor.
- **Kayıt, klonun tavanı.** Gürültülü, tek düze ya da kısa kayıttan iyi klon çıkmıyor; sonradan ayarla düzelmiyor.
- **Başkasının yüzü ve sesi yok.** İkiz yalnız kendi onayınla kendin için kurulur.
- Planlar ve kredi tarifeleri sık değişiyor; bu sayfada bilerek fiyat yazmadım.

## Sınama

2026-11-05, Windows, Python 3.14, ffmpeg 8.1.1, geçici bir klasörde:

- **Çekim kontrol komutu:** sesli ve sessiz iki deneme videosu üretildi; komut sesli olanda `video` +
  `audio`, sessiz olanda yalnız `video` satırı gösterdi. ✅
- **Kayıt süresi komutu:** 3 × 90 saniyelik MP3 için "4.5 dakika" verdi. ✅
- **`ikiz_video.py`:** gerçek API yerine yerel bir sahte sunucuya karşı uçtan uca koşuldu. Sahte sunucu
  istekleri belgelerdeki şekle göre denetledi: ses isteği, çok parçalı yükleme, `POST /v3/videos` alanları
  (`type`, `avatar_id`, `audio_asset_id`, `aspect_ratio`, `resolution`, `title`), üç durum sorgusu ve
  indirme geçti. Eksik ortam değişkeninde betik hiçbir istek atmadan durdu. ✅
- Gerçek uçlar anahtarsız çağrıldığında ikisi de `401` döndü (uç adresleri doğru, kimlik istiyor).
- **Denenmedi:** gerçek ElevenLabs ses üretimi, gerçek HeyGen yükleme ve render, HeyGen MCP girişi,
  ikiz/PVC oluşturma. Bunlar hesap ve kredi ister; bu sınamada bilerek ücretli çağrı yapılmadı.

## Kaynaklar

- HeyGen, ilk Digital Twin (çekim kuralları, oluşturma adımları): https://help.heygen.com/en/articles/12089286-create-your-first-digital-twin-video-avatar-with-avatar-iv
- HeyGen, Digital Twin hata kodları (30 sn – 5 dk, tek sahne, ses, onay, 3 deneme): https://help.heygen.com/en/articles/9824740-digital-twin-creation-error-codes
- HeyGen, Digital Twin SSS (slot, onay, kıyafet): https://help.heygen.com/en/articles/9380615-digital-twin-faq
- HeyGen, ElevenLabs sesini bağlamak: https://help.heygen.com/en/articles/8310663-how-to-integrate-elevenlabs-other-third-party-voices
- HeyGen, ses rehberi (PVC ve Multilingual v2 önerisi): https://help.heygen.com/en/articles/9834925-ai-voice-101-the-comprehensive-guide
- HeyGen, Audio to Video (`POST /v3/videos` + `audio_asset_id`): https://developers.heygen.com/audio-to-video
- HeyGen, dosya yükleme (`POST /v3/assets`): https://developers.heygen.com/docs/upload-assets
- HeyGen, video durumu (`GET /v3/videos/{video_id}`): https://developers.heygen.com/reference/get-video
- HeyGen, MCP ile Claude Code: https://developers.heygen.com/mcp/claude-code
- HeyGen, geliştirici dizini (OAuth = abonelik kredisi, API anahtarı = API faturası): https://developers.heygen.com/llms.txt
- ElevenLabs, Professional Voice Cloning: https://elevenlabs.io/docs/eleven-creative/voices/voice-cloning/professional-voice-cloning
- ElevenLabs, metinden ses API'si: https://elevenlabs.io/docs/api-reference/text-to-speech/convert
- ElevenLabs, barındırılan MCP sunucusu: https://elevenlabs.io/docs/eleven-agents/operate/hosted-mcp
- Instagram, yapay zekâ etiketi: https://help.instagram.com/761121959519495
