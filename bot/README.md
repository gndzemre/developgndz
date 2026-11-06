# Sen uyurken satış yapan bot: mimari şeması

> Videodaki vaat: *"Mimarinin şemasını paylaşıyorum."*
> Parçalar videodakiyle aynı: Flowise · Supabase · WhatsApp. Akış da aynı: gece 3 buçukta mesaj geliyor, bot soruyu
> çözüyor, stoğa bakıyor, fiyatı söylüyor, sipariş linkini atıyor.

Şema: `sema.svg` (tarayıcıda açılır, istediğin boyda büyütülür).

## Parçalar

**WhatsApp Cloud API (Meta).** Müşteri zaten orada; uygulama indirmek ya da üye olmak yok. Gelen her mesaj
`messages` webhook'u ile senin adresine POST edilir. Cevabı `POST /<WHATSAPP_BUSINESS_PHONE_NUMBER_ID>/messages`
ile gönderirsin. Serbest metin cevap, müşterinin son mesajından sonraki 24 saat içinde gönderilebilir; pencere
kapanınca yalnız onaylı şablon mesaj gider. Gece gelen soruya hemen cevap verdiğin için bot bu pencerenin içinde
kalır.

**Köprü.** Videoda üç parça var; şemada arada ince bir dördüncü katman duruyor, çünkü Meta ile Flowise doğrudan
konuşamıyor:

- Meta, webhook adresini önce bir **GET** isteğiyle doğrular: `hub.verify_token` senin belirlediğin değerle
  eşleşmeli, cevap olarak `hub.challenge` geri dönmeli.
- Sonraki her bildirim `X-Hub-Signature-256` başlığıyla imzalı gelir; imzayı uygulamanın gizli anahtarıyla
  (App Secret) kontrol et, tutmayanı at.
- 200 dönmezsen Meta aynı bildirimi 7 güne kadar tekrar gönderir; aynı mesaj iki kez gelebilir. Önce 200 dön,
  mesaj kimliğiyle tekrarı ayıkla.
- Adres HTTPS ve sertifikası geçerli olmalı; self-signed kabul edilmez.
- Flowise ise kendi biçimini bekler: `POST /api/v1/prediction/{id}`, gövdede `question`.

Bu işi bir n8n Webhook akışı ya da küçük bir sunucu fonksiyonu yapar.

**Flowise (AgentFlow V2).** Müşterinin ne demek istediğini çözer. "2500'lük olan hâlâ var mı" yazan kişinin hangi
ürünü sorduğunu bulan katman bu.

- *Condition Agent* mesajı niyete göre ayırır: ürün sorusu / sipariş / başka bir şey.
- *Agent* düğümü yalnız izin verdiğin araçları kullanır; burada tek araç var: `stok_sorgula`.
- Konuşmanın devamlılığı için köprü her istekte `overrideConfig.sessionId` gönderir. Flowise bu alanı ancak
  *Settings → Configuration → Security*'den override izni açılınca kabul eder. Telefon numarasını açık yazmak yerine
  özetini (hash) kullan; Flowise kayıtlarında kişisel veri birikmesin.
- Flowise'ı API anahtarıyla koru; köprü `Authorization: Bearer <FLOWISE_API_ANAHTARIN>` gönderir.

**Supabase.** Stok ve fiyat burada durur. Supabase tabloyu kendiliğinden REST API olarak açar
(`https://<PROJE_KIMLIGIN>.supabase.co/rest/v1/`).

## İşin püf noktası: bot cevabı uydurmaz

Her soruda bu tabloya bakar. Ürün bittiyse "var" demez. Bunu modelin iyi niyetine değil yapıya bağlarsın:

1. Fiyat ve stok bilgisi **yalnız araçtan dönen satırdan** gelir; Agent'ın sistem promptuna bu kural yazılır.
2. Araç boş dönerse bot "bilmiyorum, sabah dönüş yapılacak" der.
3. `stok = 0` olan ürün için "var" denmez.
4. Bot ödeme almaz: `siparis_linki`'ni atar, sipariş senin satış sayfanda oluşur, sabah seni bekler.

## Başlangıç tablosu

```sql
create table public.urunler (
  id bigint generated always as identity primary key,
  ad text not null,
  fiyat numeric not null,
  stok integer not null default 0,
  siparis_linki text
);

alter table public.urunler enable row level security;

create policy "Ürünler okunabilir"
on public.urunler for select
to anon
using ( true );
```

- RLS açıkken, politika yazılana kadar publishable key ile API'den hiçbir veri gelmez. Yukarıdaki politika yalnız
  **okuma** izni verir; yazma politikası yok, bot tabloyu değiştiremez.
- Bot **publishable key** kullanır. **Secret key RLS'nin tamamını aşar**; bota, Flowise'a ya da istemci koduna koyma.

## `stok_sorgula` aracı (Flowise Custom Tool, taslak)

Girdi şeması: `fiyat` (number, isteğe bağlı).

```js
const fetch = require('node-fetch');
let url = 'https://<PROJE_KIMLIGIN>.supabase.co/rest/v1/urunler?select=ad,fiyat,stok,siparis_linki';
if ($fiyat) url += '&fiyat=eq.' + encodeURIComponent($fiyat);
const r = await fetch(url, { headers: { apikey: '<SUPABASE_PUBLISHABLE_KEY>' } });
return JSON.stringify(await r.json());
```

Fiyat verilmezse bütün katalog döner; Agent ürünü addan kendisi eşleştirir. Katalog büyükse araca bir filtre daha
ekle. (Bu araç kodu denenmedi.)

## Sınama

- `sema.svg` elle yazıldı; XML ayrıştırıcıdan geçti, Chrome'da 1200×1590 boyutunda açılıp bakıldı: taşan ya da
  üst üste binen yazı yok.
- Şemadaki her yetenek aşağıdaki resmî belgelerden doğrulandı: WhatsApp webhook'u ve 7 günlük yeniden deneme,
  GET doğrulaması, `X-Hub-Signature-256`, HTTPS şartı, mesaj gönderme yolu, 24 saatlik pencere; Flowise AgentFlow V2
  düğümleri, Prediction API, `sessionId`, Bearer anahtarı, Custom Tool; Supabase REST API, RLS, publishable/secret
  key ayrımı, `apikey` başlığı; PostgREST `eq.` filtresi.
- **Uçtan uca kurulum (WhatsApp numarası + köprü + Flowise + Supabase) denenmedi.** SQL ve araç kodu da çalıştırılmadı.

## Kaynaklar

- WhatsApp Cloud API, webhook kurulumu (`messages`, 7 gün yeniden deneme): https://developers.facebook.com/docs/whatsapp/cloud-api/guides/set-up-webhooks
- Meta webhook doğrulaması (`hub.challenge`, `X-Hub-Signature-256`, TLS şartı): https://developers.facebook.com/docs/graph-api/webhooks/getting-started
- WhatsApp Cloud API, mesaj gönderme ve 24 saatlik pencere: https://developers.facebook.com/docs/whatsapp/cloud-api/guides/send-messages
- Flowise AgentFlow V2 düğümleri: https://docs.flowiseai.com/using-flowise/agentflowv2
- Flowise Prediction API (`question`, `overrideConfig`, `sessionId`): https://docs.flowiseai.com/using-flowise/prediction
- Flowise akış koruması (Bearer API anahtarı): https://docs.flowiseai.com/configuration/authorization/chatflow-level
- Flowise Custom Tool: https://docs.flowiseai.com/integrations/langchain/tools/custom-tool
- Supabase REST API: https://supabase.com/docs/guides/api
- Supabase API anahtarları (publishable / secret, `apikey` başlığı): https://supabase.com/docs/guides/api/api-keys
- Supabase Row Level Security: https://supabase.com/docs/guides/database/postgres/row-level-security
- PostgREST, tablo filtreleri (`eq.`): https://docs.postgrest.org/en/latest/references/api/tables_views.html
