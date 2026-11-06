# Ajan çıktısı doğrulama kontrol listesi: rapora değil, ize bak

> Videodaki vaat: *"Ajan çıktısını doğrulamak için kullandığım kontrol listesini paylaşıyorum."*
> Videodaki kural: *"Ajanın raporuna değil, bıraktığı ize bak. Tabloya satır düştü mü, dosya oluştu mu, mesaj gerçekten gitti mi? Yeşil ışık bir iddia, kanıt değil."*

Liste araçtan bağımsız: Claude Code, Cursor, Codex ya da kendi kurduğun bir ajan, hepsinde aynı. Komut örnekleri
git, Node ve Python ile; kendi ortamına uyarla.

---

## 0 · Önce iddiayı kanıta çevir

Ajan "bitti" dediğinde rapordaki her cümleyi bir soruya çevir: **bu doğruysa sistemde ne değişmiş olmalı?**

| Ajanın iddiası | Bakacağın iz |
|---|---|
| "Dosyayı oluşturdum" | Dosya diskte var mı, boş değil mi, içinde beklenen var mı |
| "Kaydı ekledim" | Tabloda o kayıt var mı, sayı arttı mı |
| "Maili / mesajı gönderdim" | Gönderen servisin kendi kaydında teslim görünüyor mu |
| "Testler geçti" | Testler gerçekten koştu mu, kaç tanesi koştu |
| "Hatayı düzelttim" | Hatayı üreten adım şimdi hatasız mı |
| "Geri alınamaz" | Geri almayı sen dene |

Kanıtını gösteremediği iddia **doğrulanmadı** sayılır; "yapıldı" değil.

## 1 · Ajana kanıtla raporlamasını söyle

Görevin sonuna ekle (kopyala):

```text
Bitirdiğinde her iddianın yanına kanıtını koy:
- çalıştırdığın komut ve çıktısının ilgili kısmı (özetleme, olduğu gibi yapıştır),
- oluşturduğun/değiştirdiğin dosyaların listesi,
- testler için: koşan, geçen, atlanan ve düşen test sayısı.
Kanıtını gösteremediğin bir iddiayı "doğrulanmadı" diye işaretle.
Testi geçirmek için test dosyasını, test ayarını ya da çıkış kodunu değiştirdiysen bunu ayrıca söyle.
```

Bu, ajanın raporunu kanıta bağlar; **kanıtı yine de sen kontrol edersin.** Ajanın yapıştırdığı çıktı da bir iddiadır.

## 2 · Dosya oluştu mu, ne değişti?

- [ ] **Ne değiştiğini git'ten oku, rapordan değil:**

  ```bash
  git status --porcelain
  git diff --stat
  ```

  Raporda olmayan bir dosya değişmişse ya da raporda olan dosya listede yoksa dur.
- [ ] **Dosya gerçekten dolu mu?** `ls -l <DOSYA>` ile boyutuna, dosyayı açıp içeriğine bak. Sıfır baytlık ya da yer tutucu metinle
  dolu bir dosya "oluşturuldu" sayılmaz.
- [ ] **Silinen ya da üzerine yazılan bir şey var mı?** `git diff --stat`'taki büyük silmeler (`-`) ajanın raporunda yoksa sor.

## 3 · Testler gerçekten koştu mu?

Videodaki ilk örnek buydu: zor bir testi geçemeyen model, programı başarılı çıkış koduyla kapattı. Testler "geçti", iş yapılmadı.
OpenAI'ın araştırmasında bu iki hile adıyla geçiyor: `exit(0)` ile testleri koşturmadan erken çıkmak ve `raise SkipTest` ile testi atlatmak.

- [ ] **Yalnız çıkış koduna bakma, sayılara bak.** Kaç test koştu, kaçı geçti, kaçı **atlandı**? Node'un test aracı, tek
  test bile geçmeden bütün testler atlandığında çıkış kodu 0 verdi (aşağıdaki sınama). Kendi test aracında da bir kez dene.
- [ ] **Test dosyalarına dokunulmuş mu?**

  ```bash
  git diff --name-only | grep -iE "test|spec"
  ```

  Ajan kodu düzeltmek yerine testi değiştirmiş olabilir. Test değiştiyse o farkı satır satır oku.
- [ ] **Kaçış kalıplarını ara:**

  ```bash
  git diff -U0 | grep -nE "skip|\.only|exit\(0\)|SkipTest|\|\| true"
  ```

  Testi atlatan (`skip`, `.only`), çıkışı zorla başarılı yapan (`exit(0)`, `|| true`) bir satır eklendiyse iş bitmemiştir.
- [ ] **Test gerçekten düşebiliyor mu?** Ana kodda bilerek küçük bir hata yap (bir `+`'yı `-` yap), testleri koş. Hâlâ yeşilse
  o test hiçbir şeyi ölçmüyor. Sonra hatayı geri al.
- [ ] **Testleri kendin koş.** Ajanın "koştum, geçti" demesi yerine aynı komutu kendi terminalinde çalıştır.

## 4 · Tabloya satır düştü mü?

- [ ] **İşten önce ve sonra say.** Ajan çalışmadan önce kayıt sayısını not et, sonra tekrar say:

  ```sql
  SELECT COUNT(*) FROM <TABLO>;
  ```

- [ ] **Yeni kaydı kendisiyle bul.** Sayı yetmez; eklenmesi gereken kaydı kimliği ya da zamanıyla çek:

  ```sql
  SELECT * FROM <TABLO> WHERE <OLUSTURMA_ZAMANI> >= '<IS_BASLANGICI>';
  ```

- [ ] **Uydurma veri var mı?** Videodaki ikinci örnek buydu: Replit'in ajanı hatalarını örtmek için sahte kişilerle dolu bir veritabanı
  üretti. Beklediğinden çok satır, birbirine benzeyen adlar, test/örnek görünümlü değerler dur işaretidir. Diff'te `faker`, `seed`,
  `mock`, `dummy` gibi yeni eklenmiş satırlara bak.
- [ ] **Doğru veritabanında mısın?** Ajan geliştirme yerine canlı veritabanına yazmış (ya da tersi) olabilir. Bağlantı adresini kontrol et.

## 5 · Mesaj gerçekten gitti mi?

- [ ] **İsteğin kabul edilmesi teslim değildir.** Bir API'nin `200` ya da `202` dönmesi, isteği **aldığını** söyler; mailin kutuya,
  mesajın telefona ulaştığını söylemez.
- [ ] **Gönderen servisin kendi kaydına bak.** Gönderim API'leri genellikle her mesaj için bir kimlik döner; ajanın raporunda
  o kimliği iste ve o kimlikle servisin panelinde ya da API'sinde teslim durumunu sorgula.
- [ ] **Alıcı tarafında gör.** Mümkünse test alıcısına gönder ve mesajı orada gözünle gör.

## 6 · "Geri alınamaz" dediyse

- [ ] **Geri almayı kendin dene.** Videodaki örnekte ajan geri almanın imkânsız olduğunu söyledi; geri alma çalışıyordu.
  Ajanın "yapılamaz" demesi de bir iddiadır.
- [ ] **Geri alma yolunu işten önce kur.** Temiz bir git durumu (commit), veritabanı yedeği ya da anlık görüntü. Yıkıcı bir işi
  geri dönüş yolu olmadan ajana verme.

## 7 · "Neredeyse doğru"yu yakala

Stack Overflow'un 2025 geliştirici anketinde en sık şikâyet *"neredeyse doğru ama tam değil"* çıkan yapay zekâ çözümleriydi (%66).

- [ ] **İstediğinle yapılanı yan yana koy.** Görev tanımını madde madde yaz, her maddenin yanına izini koy. Eksik kalan madde
  "neredeyse" demektir.
- [ ] **Kenar durumunu sen dene.** Boş girdi, Türkçe karakter, çok büyük dosya, olmayan kayıt. Ajanın denediği örnekler genellikle
  kendi yazdığı örneklerdir.

---

## Sınama

2026-11-05, Windows 11, Node 25.8.2, git, Python 3.14 `sqlite3`, geçici bir git deposunda:

- Bilerek hatalı bir `topla` fonksiyonu ve onu yakalayan bir test yazdım: `node --test` **düştü** (çıkış 1).
- Ajanın yapabileceği hileyi taklit edip testi `{ skip: true }` ile atlattım: `node --test` **çıkış 0** verdi; özet
  `tests 1 · pass 0 · skipped 1`. Yani yeşil çıktı, tek test bile geçmeden.
- Aynı durumda `git diff --name-only | grep -iE "test|spec"` değişen test dosyasını, kaçış kalıbı araması da `skip: true`
  satırını **buldu**.
- SQLite'ta bir tabloya kayıt ekleyip son 10 dakikadaki kayıtları zamana göre saydım: beklenen 1 kaydı **buldu**.
- Mail/mesaj teslim sorgusu servise göre değiştiği için **denenmedi**. 1. bölümdeki rapor promptu bir ajanla **denenmedi**.

## Kaynaklar

- `exit(0)` ve `raise SkipTest` hileleri: OpenAI, *Monitoring Reasoning Models for Misbehavior and the Risks of Promoting Obfuscation*
  (2025) — [arxiv.org/abs/2503.11926](https://arxiv.org/abs/2503.11926) · özet yazı: [openai.com/index/chain-of-thought-monitoring](https://openai.com/index/chain-of-thought-monitoring/)
- Replit olayı (Temmuz 2025; sahte veri üretmesi, geri almanın imkânsız olduğunu söylemesi ve geri almanın aslında çalışması):
  [The Register, 21 Temmuz 2025](https://www.theregister.com/2025/07/21/replit_saastr_vibe_coding_incident) ·
  [Fortune, 23 Temmuz 2025](https://fortune.com/2025/07/23/ai-coding-tool-replit-wiped-database-called-it-a-catastrophic-failure/).
  "4000 sahte kişi" rakamı videodan alıntıdır; haberlerde rakamlar kaynaktan kaynağa değişiyor.
- Güven oranı ve "neredeyse doğru" şikâyeti: [Stack Overflow 2025 Developer Survey · AI](https://survey.stackoverflow.co/2025/ai)
  (2025'te yapay zekâ araçlarının doğruluğuna güvenenler %33, şikâyet %66). Videodaki "43'ten 33'e" düşüşün 2024 tarafı (%43) basında
  aktarıldı: [tech.co](https://tech.co/news/survey-developers-using-ai-more-trust-less).
- Node test aracı (`skip` seçeneği, özet satırları): [nodejs.org/api/test.html](https://nodejs.org/api/test.html)
- `git diff --stat` / `--name-only`: [git-scm.com/docs/git-diff](https://git-scm.com/docs/git-diff)
