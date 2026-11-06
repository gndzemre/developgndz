# Abonelik takip akışı: n8n şablonu

> Videodaki vaat: *"Bu akışın hazır şablonunu paylaşıyorum."*
> Videodaki mantıkla aynı: mail kutunu tarayan bir akış, abonelik yenileme maillerini ayırıyor, her ay tekrar eden
> tutarları tabloya döküyor. Tablo üç soruya cevap veriyor: hangi servis, ayda kaç lira, en son ne zaman kullandın.

Dosya: `abonelik_takibi.json` (n8n'de Workflow menüsü → **Import from File**).

## Akış

Her pazartesi 09:00 → Gmail'de son 13 ayın ödeme/yenileme maillerini ara (en fazla 150) → maili kısa metne indir
→ Claude her mail için karar verir: abonelik mi, hangi servis, tutar, para birimi, dönem → aynı servisin maillerini
birleştir → `Abonelikler` sayfasına yaz (servis zaten varsa satırını günceller).

Gmail araması:

```text
newer_than:13m (abonelik OR yenileme OR üyelik OR fatura OR makbuz OR subscription OR renewal OR receipt OR invoice OR "your plan")
```

Senin servislerin farklı kelimeler kullanıyorsa bu satırı `Ödeme mailleri (son 13 ay)` düğümünde genişlet.

## Kurulum

1. Google Sheets'te bir dosya aç, `Abonelikler` adında bir sayfa oluştur. İlk satıra şu başlıkları bu yazımla gir:

   `servis` · `aylik_tutar` · `para_birimi` · `donem` · `son_odeme_maili` · `kac_ayda_goruldu` · `tekrar_ediyor` · `son_kullanim` · `karar`

2. Workflow'u içe aktar. Şablonda kimlik bilgisi yok: Gmail (OAuth2), Anthropic (API anahtarı) ve Google Sheets
   (OAuth2) düğümlerinde kendi bağlantını oluştur ya da seç.
3. `<GOOGLE_SHEETS_ADRESIN>` yerine dosyanın adresini yaz.
4. Önce elle çalıştır, tabloya bak, sonra workflow'u yayınla (Publish); pazartesi zamanlayıcısı ancak o zaman çalışır.

## Tablo nasıl okunur

| Sütun | Kim doldurur | Ne anlama gelir |
|---|---|---|
| `servis` | akış | Servisin adı. Satırı bulmak için anahtar. |
| `aylik_tutar` | akış | Son maildeki tutarın aylık karşılığı. Yıllık plan ise tutar ÷ 12. |
| `para_birimi` · `donem` | akış | TRY / USD / EUR … · aylik / yillik / haftalik / bilinmiyor |
| `son_odeme_maili` | akış | O servisten gelen en son ödeme mailinin tarihi. |
| `kac_ayda_goruldu` | akış | Son 13 ayda kaç farklı ayda ödeme maili geldi. |
| `tekrar_ediyor` | akış | İki ya da daha fazla ayda görüldüyse ya da yıllık plansa `evet`, değilse `belirsiz`. |
| `son_kullanim` | **sen** | Servisi en son ne zaman açtın. |
| `karar` | **sen** | `kalsın` / `iptal` / `düşür` |

**"En son ne zaman kullandın?" sorusunu mail cevaplayamaz.** Ödeme maili servisi kullandığını göstermez. Bu yüzden
`son_kullanim` sütunu sana bırakıldı: tabloyu ilk açtığında her satıra bir kez bak, aylardır açmadığın servis
hemen öne çıkar. Akış bu iki sütuna hiç yazmıyor; ilk güncellemeden sonra senin girdiğin değerlerin yerinde
kaldığını bir kez kontrol et.

**İptali akış yapmaz.** Videodaki Muse iptal yazışmasını da yürütüyor; bu şablon yalnız bulur ve tabloya döker.
İptal kararı ve işlemi sende.

## Bilmen gerekenler

- **Mail içeriği model sağlayıcısına gidiyor.** Her mailin ilk 4000 karakteri Claude'a (Anthropic API) gönderiliyor
  ve bunlar ödeme mailleri. Bunu istemiyorsan `Claude (çıkarıcı)` düğümünü sil, yerine n8n'in **Ollama Chat Model**
  düğümünü bağlayıp kendi makinende çalışan bir model kullan (çıkarım kalitesi seçtiğin modele bağlı, denenmedi).
- Model aynı servise farklı ad verebilir ("X" ve "X Premium" gibi). Akış adları küçük harfe çevirip birleştiriyor
  ama farklı yazımlar ayrı satır olur; tabloda ikiz satır görürsen birini sil.
- Farklı para birimlerini toplamıyor; her satır kendi para biriminde.
- 150 mail sınırı her çalıştırmada geçerli. Gelen kutun kalabalıksa sınırı artırmak yerine aramayı daralt.
- Her mail bir model çağrısı demek (haftada en fazla 150). Güncel fiyatı sağlayıcının fiyat sayfasından kontrol et.

## Sınama

- n8n-mcp `validate_workflow` doğrulayıcısından geçti: **hata 0, uyarı 0**. Doğrulayıcının genel önerisi: hata
  yakalama ekle. Düğüm tipleri ve sürümleri n8n-mcp düğüm kaydından alındı.
- Code düğümlerinin mantığı Node.js 25'te sahte veriyle çalıştırıldı: aynı servisin iki ayrı aydaki maili tek satıra
  indi (`kac_ayda_goruldu: 2`, son tutar alındı), yıllık 1200 TL'lik plan aylık 100 olarak yazıldı, abonelik
  olmayan mail elendi. Sonuç beklenenle aynı.
- **n8n'e içe aktarma, gerçek Gmail ve Sheets ile çalıştırma ve modelin gerçek maillerdeki çıkarım doğruluğu
  denenmedi.**

## Kaynaklar

- n8n, içe/dışa aktarma: https://docs.n8n.io/workflows/export-import/
- Gmail arama işleçleri (`newer_than:` d/m/y, `OR`): https://support.google.com/mail/answer/7190
- Anthropic model listesi (`claude-haiku-5-5`): https://platform.claude.com/docs/en/about-claude/models/overview
