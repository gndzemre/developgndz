# İş başı maliyet ölçüm tablosu

> Videodaki vaat: *"Bu ölçüm için kullandığım tabloyu paylaşıyorum."*
> Ölçtüğü şey videodaki gibi: token fiyatı değil, **bir işi bitirmenin toplam maliyeti.**

Dosya: `is_basi_maliyet_tablosu.xlsx` (Excel ve Google E-Tablolar'da açılır). Üç sayfa:

| Sayfa | Ne yaparsın |
|---|---|
| **Fiyatlar** | Karşılaştıracağın iki modelin adını ve 1 milyon jeton başına girdi/çıktı fiyatını yazarsın. Fiyatı sağlayıcının resmî fiyat sayfasından al, kaynağını ve tarihini yanına not et. |
| **Kayıt** | Her iş bir satır: model, iş, kaç turda bitti, girdi/çıktı jetonu, bitti mi, elle düzeltme gerekti mi. **Maliyet** sütunu kendiliğinden hesaplanır. |
| **Özet** | Model başına toplam maliyet, biten iş sayısı ve **iş başı maliyet = toplam maliyet ÷ biten iş.** |

## Bir haftalık ölçüm

1. İki modeli seç, **Fiyatlar** sayfasına yaz.
2. Bir hafta boyunca iki modele **aynı işleri** ver: aynı hata, aynı özellik, aynı belge.
   İşler gerçek olsun; deneme amaçlı kolay işler sonucu bozar.
3. Her işten sonra **Kayıt**'a bir satır ekle. Jeton sayısını API cevabındaki kullanım
   alanından ya da sağlayıcının kullanım panelinden al.
4. "Bitti mi?" sütununa yalnız iş gerçekten bittiyse **evet** yaz. Yarım kalan iş maliyete
   girer ama bitenlere girmez. Pahalıya patlayan model tam burada görünür.
5. Hafta sonunda **Özet**'e bak: kazanan, iş başı maliyeti düşük olandır.

## Dikkat

- **Biten iş sayısı azsa sonuç gürültülüdür.** Üç işle karar verme.
- Önbellekli girdi ayrı fiyatlanıyorsa tablo bunu ayırmaz; büyük fark yaratıyorsa ayrı bir
  satır gibi düşün.
- Elle düzeltme süresi faturada görünmez ama gerçek bir maliyettir; o sütunu bu yüzden tutuyoruz.
- Tablo örnek veriyle Excel'de sınandı: maliyet ve iş başı sonuçlar elle hesapla aynı çıktı.
