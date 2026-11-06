# Hangi iş Cursor'a, hangisi Claude Code'a: iş dağılımı listem

> Videodaki vaat: *"Hangi işi hangisine verdiğimin listesini çıkardım."*
> Kural videodakiyle aynı: **küçük işler Cursor'da, büyük işler Claude Code'da.**

Ayrım araçların ne yapabildiğine göre değil, **işin kaç adım sürdüğüne** ve **her adımı görmek isteyip istemediğine** göre.
(Cursor'ın Agent'ı da terminal komutu çalıştırabiliyor; Claude Code da editörün içinde çalışabiliyor. Bu liste benim iş bölümüm.)

---

## İki sütun

| Cursor'a verdiğim işler (imleç orada, kontrol bende) | Claude Code'a verdiğim işler (birden çok adım, ben izlemem) |
|---|---|
| Tek satırlık düzeltme: yazım hatası, yanlış koşul, eksik `await` | **Testleri çalıştır → patlayanı bul → düzelt → yeniden çalıştır** döngüsü |
| Yazarken tamamlama: Tab önerisini kabul edip devam etmek | Birden çok dosyaya yayılan değişiklik: bir fonksiyonun imzasını değiştirip tüm çağrıları güncellemek |
| Seçili birkaç satırı yeniden yazdırmak (seç → `Ctrl+K` / `Cmd+K`) | Hata kaydından kök sebebi bulmak: log'u ver, kodda izini sürsün |
| Bir fonksiyonun içini okuyup anlamak, küçük bir yeniden adlandırma | Bağımlılık güncelleme + testleri koşup kırılanı onarmak |
| CSS / arayüz ince ayarı: sonucu her değişiklikte gözle görmek istediğim işler | Yeni bir kod tabanını tanımak: "bu proje nasıl çalışıyor, giriş noktası nerede" |
| Kodu öğrenmek istediğim yerler: her satırı ben görmeliyim | Commit mesajı yazmak, dal açmak, PR hazırlamak |
| Tek dosyada, sonucu hemen belli olan her şey | Tekrar eden toplu işler: lint hatalarını projede temizlemek, eksik testleri yazmak |
| | Komut satırından, betikle ya da CI'da çalışacak işler (`claude -p "..."`) |

## Karar kuralı (üç soru)

1. **Kaç adım?** Tek adım → Cursor. Komut çalıştırıp sonucuna göre devam etmesi gereken iş → Claude Code.
2. **Her adımı görmem gerekiyor mu?** Evet → Cursor. Hayır, sonunda farkı incelerim → Claude Code.
3. **Kaç dosya?** Bir dosya → Cursor. Birden çok dosya ve komut → Claude Code.

İkisi farklı cevap veriyorsa, işi böl: planı Claude Code'a çıkart, ince ayarı Cursor'da yap.

---

## Bu dağılımı işleten ayarlar

**Cursor tarafı**

- **Tab:** yazarken öneri getirir; birden çok satırı değiştirebilir, sıradaki düzenleme yerine atlar.
  `Tab` kabul eder, `Ctrl+→` / `Cmd+→` kelime kelime kabul eder, `Esc` reddeder.
- **Seçili kod → Agent:** kodu seç, `Ctrl+K` / `Cmd+K`. (Eskiden bu kısayol satır içi düzenlemeyi açıyordu; Cursor
  belgesine göre artık seçimi Agent'a gönderiyor.)
- **Agent:** yan panelde açılır (Mac'te `Cmd+I`). Agent oturumunda Cursor kontrol noktaları (checkpoint) tutar, dosyaları geri alabilirsin.

**Claude Code tarafı**

- **Önce plan:** büyük işe başlamadan `Shift+Tab` ile **plan** moduna geç. Claude dosyaları okur, plan yazar,
  sen onaylayana kadar kaynak dosyaya dokunmaz.
- **Örnek komut** (Claude Code belgesindeki):

  ```bash
  claude "write tests for the auth module, run them, and fix any failures"
  ```

- **Geri alma:** `/rewind` (ya da boş istemde iki kez `Esc`). Dikkat: yalnız Claude'un dosya düzenleme araçlarıyla
  yaptığı değişiklikler izlenir; **yalnız bir kabuk komutunun değiştirdiği dosya geri alınmaz.** O yüzden işe başlamadan
  git'te temiz bir noktada ol.
- **Kalıcı talimat:** proje kökündeki `CLAUDE.md`'ye test komutunu ve kod kurallarını yaz; her oturumda okur.
- **Betik/CI:** `claude -p "..."` tek sefer çalışır, çıktıyı basar, çıkar.

**İkisi bir arada**

- Claude Code'un VS Code eklentisi **Cursor'a da kuruluyor** (resmî kurulum sayfasında "Install for Cursor" bağlantısı var).
  Ya da Cursor'ın kendi terminalinde `claude` yaz. Büyük işi Claude Code yürütürken, farkı Cursor'da açıp incelersin.

---

## Kaynaklar

- Claude Code genel bakış (ne yapar, `claude "..."` örneği, `claude -p`, `CLAUDE.md`, Cursor'a eklenti): [code.claude.com/docs/en/overview](https://code.claude.com/docs/en/overview)
- Claude Code izin modları (`plan`, `Shift+Tab`): [code.claude.com/docs/en/permission-modes](https://code.claude.com/docs/en/permission-modes)
- Claude Code kontrol noktaları (`/rewind`, sınırlar): [code.claude.com/docs/en/checkpointing](https://code.claude.com/docs/en/checkpointing)
- Cursor Tab: [cursor.com/docs/tab](https://cursor.com/docs/tab)
- Cursor `Ctrl+K` / `Cmd+K` (satır içi düzenlemenin yerini alan akış): [cursor.com/docs/inline-edit](https://cursor.com/docs/inline-edit)
- Cursor Agent (`Cmd+I`, kontrol noktaları): [cursor.com/docs/agent/overview](https://cursor.com/docs/agent/overview)
- Cursor Agent'ın terminal aracı: [cursor.com/docs/agent/tools/terminal](https://cursor.com/docs/agent/tools/terminal)

## Sınama

2026-11-05:

- **Denendi:** Claude Code 2.1.191'de `claude --help` çıktısında `-p, --print` ve `--permission-mode` bayrakları var.
- **Denenmedi:** Cursor'daki kısayollar ve özellikler bu makinede açılıp denenmedi; resmî Cursor belgelerinden alındı.
  Cursor sık güncelleniyor, kısayollar değişebilir.
- Liste bir kullanım tercihi; çalıştırılacak bir komut seti değil. Fiyat ve plan bilgisi bilerek yazılmadı.
