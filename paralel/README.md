# Paralel ajan promptu: büyük bir işi parçalara böl, hepsini aynı anda koştur

> Videodaki vaat: *"Paralel ajan kurulumu için kullandığım promptu paylaşıyorum."*
> Örnek iş videodakiyle aynı: uzun bir sözleşmeyi parçalara bölüp her parçayı ayrı bir ajana okutmak, önüne yalnız riskli maddeleri getirmek.

Prompt **Claude Code** için yazıldı. Claude Code alt ajanları (subagent) aynı anda başlatabiliyor; prompt bunu açıkça istiyor. Başka bir ajan aracında da çalışır, yeter ki araç birden çok alt görevi paralel koşturabilsin.

---

## 1 · Sözleşme örneği (kopyala, köşeli parantezleri doldur)

```text
Görev: [DOSYA_YOLU] dosyasındaki sözleşmeyi riskli maddeler için tara.

Çalışma şekli:
1. Dosyayı aç, kaç sayfa/bölüm olduğunu çıkar. Metni yaklaşık eşit parçalara böl:
   her parça en fazla [5] sayfa. Bir maddeyi ortasından bölme; parçayı madde sınırında kes.
2. Her parça için AYRI bir alt ajan başlat. Hepsini AYNI ANDA başlat, sırayla değil.
   Her alt ajana yalnız kendi parçasını ve aşağıdaki "alt ajan talimatı"nı ver.
3. Bütün alt ajanlar dönünce sonuçları birleştir:
   - Parça sınırında iki kez yakalanan maddeyi bir kez say.
   - Önem sırasına göre (yüksek → düşük) tek tablo yap:
     | Önem | Madde no | Sayfa | Birebir alıntı | Risk türü | Neden riskli |
4. Son kontrol: tablodaki her alıntıyı asıl dosyada ara. Bulamadığın alıntıyı tablodan çıkar
   ve kaç satır çıkardığını raporun sonunda yaz.
5. Raporun sonuna şu notu ekle: "Bu bir ön tarama, hukuki görüş değildir."

Alt ajan talimatı:
- Sana verilen metin bir sözleşmenin [X–Y] sayfaları. Yalnız bu metne bak.
- Şu türlerden birine giren maddeleri bul: tek taraflı fesih · sınırsız ya da orantısız
  sorumluluk · cezai şart · otomatik yenileme · münhasırlık / rekabet yasağı · fikri mülkiyetin
  devri · tek taraflı fiyat değişikliği · uzun ödeme vadesi · gizlilik yükümlülüğünün süresi ·
  yetkili mahkeme / tahkim · [KENDİ EKLEDİĞİN TÜR].
- Her bulgu için: madde no, sayfa, maddeden BİREBİR alıntı (en fazla 2 cümle), risk türü,
  neden riskli (tek cümle), önem (yüksek / orta / düşük).
- Metinde olmayan bir şeyi iddia etme. Alıntı yapamadığın bulguyu yazma.
- Riskli madde yoksa boş liste döndür; "temiz" meşru bir sonuçtur.
```

## 2 · Genel iskelet (her büyük iş için)

Sözleşme yerine herhangi bir işe uyarlamak için aynı dört parça yeter:

```text
Görev: [İŞİN TANIMI]

1. BÖL: işi [N] bağımsız parçaya ayır. Ölçüt: [her parça tek başına çözülebilir olmalı].
2. KOŞTUR: her parça için ayrı bir alt ajan başlat, hepsini AYNI ANDA. Her birine yalnız
   kendi parçasını ve aynı talimatı ver.
3. ALT AJAN TALİMATI: [parçada ne aranacak / ne üretilecek] · çıktı biçimi: [tablo satırı /
   JSON] · emin olmadığını "emin değilim" diye işaretle · bulgu yoksa boş dön.
4. BİRLEŞTİR + DOĞRULA: sonuçları tek çıktıda topla, tekrarları ayıkla, her iddiayı kaynağında
   kontrol et, kontrolden geçmeyeni çıkar ve kaç tane çıkardığını yaz.
```

## Neden bu dört parça

- **Bölmek** paralelliğin ön koşulu: parçalar birbirini beklemiyorsa aynı anda koşabilir.
- **Aynı talimat** her ajanın çıktısını birleştirilebilir kılar; biçim tutmazsa birleştirme elle yapılır.
- **Boş dönme izni** ajanın bir şey bulmak için uydurmasını engeller.
- **Son doğrulama** ajanların "buldum" demesini kanıta bağlar: alıntı asıl metinde yoksa satır düşer.

## Bilmen gerekenler

- **Sınandı (Claude Code 2.1.191, 2026-11-05):** 3 sayfalık deneme sözleşmesinde prompt üç alt
  ajanı tek adımda, aynı anda başlattı; içine konan 6 riskli maddenin 6'sını buldu, alıntıların
  hepsini asıl metinde doğruladı. Gerçek bir 100 sayfalık sözleşmeyle denenmedi.
- Parça sayısı arttıkça jeton harcaması da artar: her alt ajan kendi parçasını ayrıca okur.
  Önce 3–4 parçayla dene, sonra büyüt.
- Alt ajanların sayısı ve aynı anda kaçının koştuğu araca göre değişir; çok sayıda parça
  sırayla gruplar hâlinde işlenebilir.
- Gizli bilgi taşıyan bir belgeyi (müşteri sözleşmesi gibi) hangi aracın, hangi sunucuya
  gönderdiğini bilerek kullan.
