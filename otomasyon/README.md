# n8n: videodaki 3 akışın hazır şablonları

> Videodaki vaat: *"Bu 3 akışın hazır şablonlarını paylaşıyorum."*
> Sıra videodakiyle aynı: mail ayıklama · sipariş + stok bildirimi · akşam özeti.

| Dosya | Ne yapar |
|---|---|
| `1_mail_ayiklama.json` | Gelen kutusunu okur, acil olanı ayırıp telefonuna (Telegram) atar. |
| `2_siparis_stok.json` | Siteden düşen siparişi tabloya yazar, stok eşiğin altına inince Telegram'dan haber verir. |
| `3_aksam_ozeti.json` | Her akşam 18:00'de günün rakamlarını ekip kanalına (Slack) yollar. |

## Başlamadan

- **İçe aktarma:** n8n'de yeni bir workflow aç → üstteki Workflow menüsü → **Import from File** → `.json` dosyasını seç.
- **Kimlik bilgisi yok.** Şablonlarda hiçbir bağlantı kayıtlı değil. İçe aktardıktan sonra kırmızı uyarı veren
  her düğümü aç, kendi bağlantını oluştur ya da seç: Gmail (OAuth2), Anthropic (API anahtarı), Telegram (bot jetonu),
  Google Sheets (OAuth2), Slack (OAuth2).
- **Yer tutucuları değiştir:** `<TELEGRAM_CHAT_ID>`, `<GOOGLE_SHEETS_ADRESIN>`, `<SLACK_KANAL_ID>`.
- **Saat dilimi** şablonlarda `Europe/Istanbul`. Başka yerdeysen workflow ayarlarından değiştir.
- **Sürüm:** düğümler n8n'in güncel düğüm sürümleriyle yazıldı. Eski bir n8n kurulumunda içe aktarırken bir düğüm
  tanınmazsa önce n8n'i güncelle.
- Akışlar yayınlanmadan (Publish) zamanlayıcı ve webhook kendiliğinden çalışmaz; denerken düğümü elle çalıştır.

### Telegram bilgileri

1. Telegram'da **@BotFather** ile sohbet aç, `/newbot` yaz, adını ver. Verdiği jeton n8n'deki Telegram
   bağlantısının *Access Token* alanına gider.
2. Botuna bir mesaj yaz. Sonra tarayıcıda `https://api.telegram.org/bot<BOT_JETONUN>/getUpdates` adresini aç;
   cevaptaki `message.chat.id` değeri senin `<TELEGRAM_CHAT_ID>`'n. Jetonu kimseyle paylaşma; bu adres tarayıcı
   geçmişinde kalır, işin bitince geçmişten sil.

---

## 1 · Mail ayıklama: acil olanı telefonuna at

**Akış:** Gmail Trigger (5 dakikada bir, okunmamış, reklam ve sosyal sekmeleri hariç) → Text Classifier
(`acil` / `acil_degil`) → `acil` ise Telegram mesajı.

- Sınıflandırmayı Claude Haiku 5.5 (`claude-haiku-5-5`) yapıyor. Anthropic bu modeli sınıflandırma, bilgi çıkarma
  ve yönlendirme gibi yoğun ve hızlı işler için öneriyor. İstersen Anthropic düğümünü başka bir sohbet modeli
  düğümüyle değiştir.
- **"Acil" tanımı senin.** `Acil mi?` düğümündeki iki kategorinin açıklamasını kendi işine göre yaz. Model kararını
  bu açıklamalara göre veriyor; ilk hafta yanlış ayrılanlara bakıp açıklamayı düzelt.
- Modele yalnız gönderen, konu ve Gmail'in kısa özeti (`snippet`) gidiyor, mailin tamamı gitmiyor. Yine de bu
  bilgiler model sağlayıcısının sunucusundan geçiyor; buna göre karar ver.
- Her mail bir model çağrısı demek. Günde yüzlerce mail alıyorsan Gmail Trigger'a etiket ya da gönderen filtresi ekle.

## 2 · Sipariş tabloya, stok azalınca Telegram

**Akış:** Webhook (POST `/siparis`) → siparişi ürün satırlarına böl → `Siparisler` sayfasına ekle → `Stok`
sayfasını oku → adetleri düş → yeni stoğu yaz + eşiğin altındaysa Telegram uyarısı.

**Google Sheets'te bir dosya aç, iki sayfa oluştur.** İlk satırlar başlık olsun:

| Sayfa | Başlıklar (ilk satır, bu yazımla) |
|---|---|
| `Siparisler` | `gun` · `saat` · `siparis_no` · `urun_kodu` · `urun_adi` · `adet` · `birim_fiyat` · `tutar` |
| `Stok` | `urun_kodu` · `urun_adi` · `stok` · `esik` |

`Stok` sayfasına ürünlerini ve uyarı eşiğini elle gir (ör. `A1 · Ürün A · 40 · 5`).

**Webhook'u koru.** Düğüm *Header Auth* ile geliyor; korumasız bir webhook'a herkes sahte sipariş gönderebilir.
Webhook düğümünde yeni bir Header Auth bağlantısı oluştur: başlık adı ör. `X-Siparis-Anahtari`, değeri uzun ve
rastgele bir dize. Siten aynı başlığı her istekte göndermeli.

**Sitenin göndermesi gereken gövde:**

```json
{
  "siparis_no": "1001",
  "urunler": [
    { "urun_kodu": "A1", "urun_adi": "Ürün A", "adet": 2, "birim_fiyat": 250 }
  ]
}
```

Elle denemek için (adresi Webhook düğümündeki *Test URL*'den kopyala, düğümde **Listen for test event**'e bas):

```bash
curl -X POST "<WEBHOOK_TEST_ADRESIN>" -H "Content-Type: application/json" -H "X-Siparis-Anahtari: <ANAHTARIN>" -d '{"siparis_no":"T1","urunler":[{"urun_kodu":"A1","urun_adi":"Ürün A","adet":1,"birim_fiyat":250}]}'
```

**Bilmen gerekenler:**

- E-ticaret altyapın (WooCommerce, Shopify vb.) kendi webhook'unu kendi biçimiyle gönderir. O zaman yalnız
  `Satırlara böl` düğümündeki birkaç satırı o biçime göre değiştir; akışın geri kalanı aynı kalır.
- Müşteri adı ve telefonu tabloya bilerek yazılmıyor: özet için gerekmiyor, gereksiz kişisel veri tutmamış olursun.
- Tablo bir veritabanı değil. Aynı saniyede iki sipariş gelirse ikisi de eski stoğu okuyup birinin düşmesini
  ezebilir. Sipariş hacmin yüksekse stoğu e-ticaret altyapısının kendisinden oku.
- `Stok` sayfasında olmayan bir ürün kodu gelirse sipariş yine `Siparisler`'e yazılır, stok adımı o ürünü atlar.

## 3 · Akşam özeti: günün rakamları ekip kanalına

**Akış:** her gün 18:00 → `Siparisler` sayfasını oku → bugünün satırlarından sipariş sayısı, ciro ve en çok
satan ürünü hesapla → Slack kanalına tek mesaj.

- 2. akışın yazdığı `Siparisler` sayfasını okur; ikisini birlikte kur.
- Slack'te bir uygulama oluştur, *Bot Token Scopes* altına `chat:write` ekle, botu kanala davet et
  (`/invite @botunun_adı`). Davet etmezsen Slack `not_in_channel` hatası döner.
- `<SLACK_KANAL_ID>`: Slack'in resmî yolu `conversations.list` API metodu; kanalları kimlikleriyle listeler.
  Uygulamada kanalın *View channel details* penceresinin altında da görünür (bu, Slack belgesinden değil
  yaygın kullanımdan; arayüz adı sürüme göre değişebilir).
- Ekibin Telegram grubunda konuşuyorsa Slack düğümünü sil, yerine 1. akıştaki Telegram düğümünü koy.
- O gün sipariş yoksa mesaj yine gider: "Bugün sipariş yok."

---

## Videodaki son kısım: akışı Claude'a kurdurmak

Videoda *"n8n'i Claude'a bağlıyorsun, ne istediğini anlatıyorsun, akışı o kuruyor"* deniyor. n8n'in kendi
belgesine göre bu, **Settings → Instance-level MCP**'den açılıyor (yalnız sahip ya da yönetici açabilir);
sunucu adresi `/mcp-server/http` ile biter. Workflow oluşturma ve düzenleme n8n **2.13.0** ve sonrasında var.
Açtığın her workflow, bağladığın her istemciye görünür; yalnız gerçekten gerekenleri aç. (Bu bağlantı bu sayfa
için kurulup denenmedi.)

## Sınama

- Üç JSON dosyası n8n-mcp `validate_workflow` doğrulayıcısından geçti: **hata 0**. Tek uyarı 2. akışta
  `Stok tablosunu oku` düğümündeki `executeOnce`; bilerek açık (stok sayfası sipariş başına bir kez okunsun diye).
  Doğrulayıcının genel önerisi: hata yakalama (Error Trigger) ekle.
- Düğüm tipleri ve sürümleri n8n-mcp düğüm kaydından alındı.
- Code düğümlerinin mantığı Node.js 25'te sahte veriyle çalıştırıldı: aynı üründen iki satır toplanıyor
  (stok 5 → 2, eşik 3 → uyarı), tanımsız ürün atlanıyor, günlük özet yalnız bugünü sayıyor, sipariş yoksa
  "Bugün sipariş yok" çıkıyor. Sonuçlar beklenenle aynı.
- **n8n'e içe aktarma ve gerçek Gmail / Sheets / Telegram / Slack bağlantısıyla çalıştırma denenmedi.**

## Kaynaklar

- n8n, içe/dışa aktarma: https://docs.n8n.io/workflows/export-import/
- n8n, Webhook düğümü (test ve yayın adresi, Header auth): https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/
- n8n, Telegram bağlantısı (BotFather, `/newbot`): https://docs.n8n.io/integrations/builtin/credentials/telegram/
- Telegram Bot API, `getUpdates` ve adres biçimi: https://core.telegram.org/bots/api#getupdates
- n8n, Slack bağlantısı: https://docs.n8n.io/integrations/builtin/credentials/slack/
- Slack, `chat.postMessage` (`chat:write`, `not_in_channel`): https://docs.slack.dev/reference/methods/chat.postMessage
- Gmail arama işleçleri (`category:`, `OR`): https://support.google.com/mail/answer/7190
- Anthropic model listesi (`claude-haiku-5-5`): https://platform.claude.com/docs/en/about-claude/models/overview
- n8n, Instance-level MCP: https://docs.n8n.io/advanced-ai/accessing-n8n-mcp-server/
