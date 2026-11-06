# Erdős problemleri: kaynak listesi ve çözülen iki problem

> Videodaki vaat: *"Listenin kaynaklarını ve çözülen iki problemi tek dosyada topladım."*
> Bu dosya o: önce videodaki iddiaların kaynağı, sonra çözülen iki problemin metni.

## Videodaki iddialar ve kaynakları

| Videoda | Kaynakta | Kaynak |
|---|---|---|
| Kimsenin çözemediği 68 problem | 68 problem, hepsi **Ağustos 2026 itibarıyla açık**. Problemleri erdosproblems.com'u yürüten matematikçi Thomas Bloom, sitedeki 652 açık problemin içinden seçti. | Epoch duyurusu · makale |
| Epoch AI, Eylül'de sınava çevirdi | Benchmark'ın adı **FrontierMath: Erdős**; duyuru 1 Eylül 2026, makale 6 Eylül 2026 (arXiv:2609.25050, Tom Adamczewski ve Thomas F. Bloom). | Epoch duyurusu · makale |
| GPT 6 resmî denemede ikisini çözdü | Modelin tam adı **GPT-6 Astra**. Resmî koşuda %3: **#74**'ü çürüttü (disproof), **#126**'yı ispatladı. Her model problem başına bir deneme hakkı, 300 dolar bütçe ve 72 saat çalışma süresi aldı. | Epoch duyurusu · benchmark sayfası |
| Diğer modellerin hepsi sıfır aldı | İlk koşuda doğru: GPT-5.6 Sol, GPT-5.5, Claude Fable 5.1, Claude Fable 5 → %0. | Epoch duyurusu |
| Çözümler makineyle doğrulanıyor | Bir çözüm ancak **Lean** ile yazılmış bir ispat ya da çürütme olarak, Lean FRO'nun **Comparator** denetleyicisinden geçerse sayılıyor. Comparator, hile yapmaya çalışan bir gönderime karşı dayanıklı olacak şekilde tasarlanmış. | Epoch duyurusu · LeanOpenProblems deposu |
| Oran yüzde 3, 66 problem hâlâ açık | Duyuru günü için doğru (2/68). **Bugün artık geçerli değil**, aşağıdaki "Videodan sonra" bölümüne bak. | Benchmark sayfası |
| İddia edilen maliyet 220 bin doların üstünde | Rakam Epoch'un kendi açıklaması ve **iki resmî çözümün değil, bütün denemelerin toplamı**: beş çözüme ulaşmak için bütün denemelerde 220.000 doların üstünde işlem gücü harcandı; resmî koşunun kendisi yaklaşık 20.000 dolar. Resmî koşudaki iki çözümün maliyeti: #74 için 222 dolar, #126 için 172 dolar (ikisi de yaklaşık 10 saat). Rakamı bağımsız bir kaynağın doğruladığını bulmadım. | Epoch duyurusu |

**Neden ezber olamaz:** Epoch'un sayfasına göre, değerlendirilen modellerin yayımlanmış en geç bilgi kesim tarihi
Haziran 2026; bu, problemlerin herhangi bir çözümünden daha eski. Cevabı hiçbir yerde yazılı olmayan bir soruda
model "hatırlayamaz".

## Çözülen iki problem

Metinler erdosproblems.com'dan olduğu gibi alındı (İngilizce, LaTeX), altında Türkçesi var.

### #74 — Kromatik sayısı sonsuz, ama "neredeyse iki parçalı" grafik

> Let $f(n)\to \infty$ (possibly very slowly). Is there a graph of infinite chromatic number such that every finite
> subgraph on $n$ vertices can be made bipartite by deleting at most $f(n)$ edges?

**Türkçesi:** f(n) sonsuza gitsin (istediği kadar yavaş). Kromatik sayısı sonsuz olan öyle bir grafik var mı ki,
n köşeli her sonlu alt grafiği en fazla f(n) kenar silinerek iki parçalı (bipartite) hâle getirilebilsin?

- Erdős, Hajnal ve Szemerédi'nin sorusu [EHS82]. Erdős ispat için 500 dolar, karşı örnek için 250 dolar ödül koymuş.
- Daha önce f(n) = √n için bile açıktı.
- **GPT-6 Astra cevabı olumsuz buldu:** f(n) ≍ log n / log log n için böyle bir grafik yok; hatta bu koşulu
  sağlayan bir grafiğin kromatik sayısı en fazla 3 olmak zorunda. (Erdős Problems sayfasının notu ve Thomas Bloom'un
  ispat özeti.)
- Sayfa: https://www.erdosproblems.com/74

### #126 — Bir kümenin ikili toplamlarının asal çarpanları

> Let $f(n)$ be maximal such that if $A\subseteq\mathbb{N}$ has $\lvert A\rvert=n$ then $\prod_{a\neq b\in A}(a+b)$
> has at least $f(n)$ distinct prime factors. Is it true that $f(n)/\log n\to\infty$?

**Türkçesi:** n elemanlı her A ⊆ ℕ kümesi için, farklı a, b ∈ A elemanlarının a + b toplamlarının çarpımı en az
f(n) farklı asal çarpana sahip olsun; f(n) bunu sağlayan en büyük sayı. f(n) / log n sonsuza gider mi?

- Erdős ve Turán'ın ilk ortak makalesinden [ErTu34]; orada log n ≪ f(n) ≪ n / log n gösterilmişti. Ödül 250 dolar.
- **GPT-6 Astra ispatladı:** cevap evet; hatta f(n) ≫ n^(1/2). (Erdős Problems sayfasının notu.)
- Sayfa: https://www.erdosproblems.com/126

## Videodan sonra: tablo değişti

Epoch'un benchmark sayfası (çözüm listesi en son **29 Ekim 2026**'da güncellenmiş) bugün şunu gösteriyor:

- #74 ve #126'yı resmî koşularda sonradan başka modeller de çözdü: Claude Opus 5.5 (22–23 Eylül 2026),
  Claude Sonnet 5.5 (2 Ekim 2026), GPT-6.1 Sol (3 Ekim 2026). "Diğer modellerin hepsi sıfır aldı" yalnız ilk koşu
  için doğru.
- GPT-6 Astra, resmî skora sayılmayan ek denemelerde (daha büyük bütçe, farklı ajan ayarı) #1, #548 ve #571'i de
  çözdü; bunlar skora girmiyor.
- Epoch dışında da çözümler geldi; sayfa bunlar arasında OpenAI'ın Ekim 2026'da yayımladığı 700'ü aşkın ispatı
  ayrıca anıyor.
- Sayfadaki çözüm listesinde 29 Ekim itibarıyla **68 problemin 17'si** var (resmî koşu, Epoch'un ek denemeleri ve
  Epoch dışı çözümler birlikte). Yani "66 problem hâlâ açık" artık doğru değil. Güncel sayıyı sayfanın kendisinden oku.

## Kaynaklar

- Epoch AI, FrontierMath: Erdős duyurusu (1 Eylül 2026): https://epoch.ai/latest/announcing-frontiermath-erdos
- Epoch AI, FrontierMath: Erdős benchmark sayfası (çözüm listesi, Lean ispatları, transkriptler): https://epoch.ai/benchmarks/frontiermath-erdos
- Makale: Adamczewski & Bloom, *FrontierMath Erdős*, arXiv:2609.25050: https://arxiv.org/abs/2609.25050
- Değerlendirme kodu ve veri: https://github.com/epoch-research/LeanOpenProblems
- Lean FRO Comparator (ispat denetleyicisi): https://github.com/leanprover/comparator
- Erdős Problems, #74: https://www.erdosproblems.com/74
- Erdős Problems, #126: https://www.erdosproblems.com/126
- Videodaki fotoğraf: Kmhkmh, CC BY 3.0, Wikimedia Commons (kırpılmış): https://commons.wikimedia.org/wiki/File:Erdos_budapest_fall_1992_(cropped).jpg

## Sınama

Her satır birincil kaynaktan 2026-11-05'te okundu: Epoch duyurusu ve benchmark sayfası, arXiv özeti,
erdosproblems.com'daki iki problem sayfası, Commons dosya sayfası. "17 problem" sayısı benchmark sayfasındaki
problem bağlantıları sayılarak çıkarıldı. Lean ispatları ve makalenin tam metni okunmadı.
