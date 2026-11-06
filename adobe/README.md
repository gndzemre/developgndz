# ArtCraft: projenin bağlantısı ve 8 ajanı paralel çalıştırma notları

> Videodaki vaat: *"Projenin linkini ve 8 ajanı nasıl paralel çalıştırdığını anlatan notları paylaşıyorum."*

---

## 1 · Projenin bağlantısı

**ArtCraft Crafting Apps:** https://getartcraft.com/apps
**GitHub:** https://github.com/storytold

Adobe karşılığı olan yedi uygulama, her biri ayrı bir depo, hepsi Rust:

| Uygulama | Hedeflediği Adobe uygulaması | Depo | Depo açılışı |
|---|---|---|---|
| PhotoCraft | Photoshop | https://github.com/storytold/photocraft | 30 Eylül 2026 |
| VectorCraft | Illustrator | https://github.com/storytold/vectorcraft | 30 Eylül 2026 |
| FilmCraft | Premiere | https://github.com/storytold/filmcraft | 30 Eylül 2026 |
| LightCraft | Lightroom | https://github.com/storytold/lightcraft | 30 Eylül 2026 |
| PdfCraft | Acrobat | https://github.com/storytold/pdfcraft | 30 Eylül 2026 |
| EffectCraft | After Effects | https://github.com/storytold/effectcraft | 1 Ekim 2026 |
| DesignCraft | InDesign | https://github.com/storytold/designcraft | 1 Ekim 2026 |

Hedef uygulamalar her deponun kendi `AGENTS.md` dosyasından, açılış tarihleri GitHub'dan alındı.
PhotoCraft'ın README'si Adobe ile bağlantısı olmadığını açıkça yazıyor; katkı kuralları "clean-room"
çalışmayı, yani Adobe'nin kodunu görmeden yazmayı şart koşuyor.

### Videodaki rakamların kaynağı

İlk okuman gereken dosya PhotoCraft'ın parite değerlendirmesi:
https://github.com/storytold/photocraft/blob/main/docs/target-app-parity.md

| Videoda | Projenin kendi kaydında |
|---|---|
| Claude Opus 5.5, 8 ajan, tek oturumda ~70 menü öğesi | Parite dosyasının 3 Ekim tahmini (kayıt için saklanan bölüm): *"This session landed ~70 menu items + major subsystems in a handful of wall-clock hours using 8 parallel agents"* |
| Günlük profesyonel işe hazırlık %25–35 | `ROADMAP.md` ilerleme günlüğü, 5 Ekim: *"Honest assessment: ready for real work 25–35%"* |
| Depolar 30 Eylül'de açıldı | `ROADMAP.md`: *"2026-09-30 · First commit"* |

Proje o günden beri ilerledi: 10 Ekim'deki yeniden ölçümde PhotoCraft için "gerçek işe hazır" oranı
**~%45**, hâlâ **alpha** aşamasında. Ayrıca 3 Ekim'deki "95%'e 140–220 ajan-saat" tahmininin çok iyimser
çıktığını kendileri yazıyor; yeni tahmin beta için 1.100–1.800 ajan-saat. Proje bugün kendini
"ArtCraft ekibi ve topluluğu" olarak tanıtıyor ve depolarda çok sayıda katkıcı görünüyor.

---

## 2 · 8 ajanı paralel çalıştırma notları

### Projenin kendi kuralları

PhotoCraft'ın `AGENTS.md` dosyasında "Parallel agents" başlıklı bir bölüm var. Özeti:

1. **Her ajan kendi derleme klasörünü kullanır** (`CARGO_TARGET_DIR=target/agent-<ad>`). Aynı klasörü
   paylaşan ajanlar birbirinin derleme kilidini bekler.
2. **Her ajan yalnız sahibi olduğu dosyaları düzenler.** Ortak dosyalarda (giriş noktası, komut kayıt
   listesi, menü) yalnız küçük, cerrahi eklemeler yapılır ve düzenlemeden önce dosya yeniden okunur.
3. **Yeni iş yeni modüle gider.** Yeni komutlar ortak dosyayı büyütmek yerine yeni bir modüle yazılır.
   Çakışmayı azaltan asıl kural bu.
4. **Başkasının yarım işini düzeltme.** Başka bir ajanın değişikliği derlemeyi bozduysa bekle, tekrar dene.
5. **Ortak yapılandırma dosyası her an geçerli kalır.** Bir bozuk manifest herkesin derlemesini kırdığı için
   yeni manifest önce geçici bir yere yazılıp sonra tek hamlede yerine taşınır.
6. **Disk temizliği.** Her ajanın derleme klasörü yaklaşık 10 GB; biten ajanın klasörü silinir.

Bitirmeden önce her ajan dokunduğu parçanın testlerini ve denetimlerini çalıştırır, sonra geliştirme
günlüğüne bir satır yazar. Parite dosyası işin yaklaşık **%80'inin paralelleşebildiğini** söylüyor:
alanlar bağımsız modüller. Paralelleşmeyen kısımlar GPU birleştiricisi, performans mimarisi ve PSD yazıcısı.
Depo bugüne kadar aynı anda **10–20 ajanı** kaldırmış.

Çıkarılacak ders: paralellik ajan sayısından değil **işin bölünebilirliğinden** geliyor. Projenin
3 Ekim kaydında 8 ajan yaklaşık **6–8 kat** paralellik vermiş, çünkü alanlar birbirinin dosyasına
dokunmuyordu. Dokunsalardı birbirlerini beklerlerdi.

### Claude Code'da kurmak: iki yol

**Yol 1 · Ayrı oturumlar, ayrı worktree'ler.** Her terminalde bir alan:

```bash
claude --worktree vektor-araclari
claude --worktree dosya-bicimleri
claude --worktree menu-komutlari
# ... sekiz terminal, sekiz ad
```

Her biri `.claude/worktrees/<ad>/` altında kendi kopyasında, `worktree-<ad>` dalında çalışır. Depoda en az
bir commit olmalı.

**Yol 2 · Tek oturum, worktree'li alt ajanlar.** Ana oturum işi böler, alt ajanları aynı anda başlatır.
Alt ajanın her seferinde kendi worktree'sinde çalışması için `.claude/agents/alan-gelistirici.md`:

```markdown
---
name: alan-gelistirici
description: Kendisine verilen tek bir alanı (modül/klasör) kendi git worktree'sinde geliştirir. Paralel işlerde her alan için ayrı başlatılır.
tools: Read, Write, Edit, Glob, Grep, Bash
isolation: worktree
---

Sen tek bir alanın sahibisin. Görevde verilen alan dışında hiçbir dosyaya dokunma.
Ortak dosyalarda (giriş noktası, kayıt listeleri) yalnız küçük, cerrahi eklemeler yap.
İşin bitince testleri çalıştır, değişikliği kendi dalında tek commit olarak kaydet
ve şu biçimde dön: dal adı · değişen dosyalar · test sonucu · bilinen eksik.
```

Ana oturuma verilecek prompt:

```text
Bu depoda şu [8] bağımsız alan var: [ALAN_1], [ALAN_2], ... [ALAN_8].
Her alan için ayrı bir alan-gelistirici alt ajanı başlat; hepsini AYNI ANDA, tek adımda başlat.
Her ajana yalnız kendi alanını ve şu işi ver: [İŞİN TANIMI]. Ortak dosyalara yalnız kayıt satırı eklesin.
Hepsi dönünce tek tablo ver: alan · dal adı · test sonucu · bilinen eksik. Dalları birleştirme.
```

Birleştirmeyi sen yap: dalları tek tek al, her birleştirmeden sonra testleri çalıştır.

### Bilmen gerekenler

- **Aynı anda kaç alt ajan:** Claude Code bir oturumda varsayılan olarak **20** alt ajana kadar izin
  veriyor; sınırı `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` ile değiştirebilirsin. 8 ajan bu sınırın içinde.
- **Worktree'ler nereye düşer:** `.claude/worktrees/`. Bunu `.gitignore`'a ekle, yoksa ana kopyada izlenmeyen
  dosya olarak görünürler.
- **`.env` gibi git dışı dosyalar** worktree'ye kendiliğinden gelmez. Proje köküne `.worktreeinclude`
  koyup içine `.env` yazarsan her yeni worktree'ye kopyalanır.
- **Temizlik:** değişiklik yapmayan alt ajanın worktree'si kendiliğinden silinir; değişiklik yapanınki
  kalır. `claude -p` ile çalıştırdıysan kapanış sorusu olmadığı için worktree'ler yerinde durur;
  işin bitince `git worktree remove <yol>` ile kaldır.
- **Taban dal:** worktree'ler varsayılan olarak deponun ana dalından açılır. Henüz push etmediğin işin
  üstünde çalışmaları gerekiyorsa ayarlarda `worktree.baseRef` değerini `"head"` yap.
- **Jeton:** her ajan kendi bağlamını ayrıca doldurur. Önce 3 ajanla dene, sonra büyüt.

Bölme–koşturma–birleştirme iskeletinin genel hâli (her büyük işe uyan dört parçalı prompt) için
paralel ajan promptumu ayrıca paylaştım: [paralel](../paralel).

## Sınama

2026-11-05, Claude Code 2.1.191, `claude -p` ile, boş bir deneme deposunda, 8 yerine **3 alan** ile:

- Yukarıdaki `alan-gelistirici` dosyası ve ana prompt kullanıldı (alanlar: toplama, çarpma, bölme modülü + testleri).
- Ana oturum üç alt ajanı tek adımda başlattı. Üçü ayrı worktree'de (`.claude/worktrees/agent-…`),
  ayrı dalda çalıştı ve **14 saniye içinde** (19:07:16 · 19:07:18 · 19:07:30) kendi commit'ini attı.
  Hiçbiri başka alanın dosyasına dokunmadı.
- Üç dal geçici bir dalda elle birleştirildi: çakışma yok, **7/7 test geçti**.
- `claude --worktree` / `-w` seçeneği bu sürümün `--help` çıktısında var; ayrı terminallerle (Yol 1) denenmedi.
- **Denenmedi:** 8 ajanla gerçek boyutta bir proje. ArtCraft'ın kendi kurulumu (hangi araçla, nasıl
  orkestre edildiği) depolarda ayrıntılı yazmıyor; yukarıdaki notlar projenin `AGENTS.md` kuralları ile
  Claude Code'un resmî özelliklerinin birleşimi.

## Kaynaklar

- ArtCraft uygulama listesi: https://getartcraft.com/apps
- GitHub organizasyonu: https://github.com/storytold
- PhotoCraft deposu: https://github.com/storytold/photocraft
- PhotoCraft `ROADMAP.md` (ilk commit, %25–35, %45): https://github.com/storytold/photocraft/blob/main/ROADMAP.md
- PhotoCraft parite değerlendirmesi (8 paralel ajan, ~70 menü öğesi, %80 paralelleşme, 10–20 eşzamanlı ajan): https://github.com/storytold/photocraft/blob/main/docs/target-app-parity.md
- PhotoCraft `AGENTS.md` (§6 Parallel agents): https://github.com/storytold/photocraft/blob/main/AGENTS.md
- Diğer depoların hedef uygulaması, her birinin `AGENTS.md`'si: vectorcraft · filmcraft · lightcraft · pdfcraft · effectcraft · designcraft (`https://github.com/storytold/<depo>/blob/main/AGENTS.md`)
- Claude Code alt ajanları (`isolation: worktree`, arka planda çalışma, 20 eşzamanlı sınırı): https://code.claude.com/docs/en/sub-agents
- Claude Code worktree'leri (`--worktree`, `.claude/worktrees/`, `.worktreeinclude`, temizlik, `worktree.baseRef`): https://code.claude.com/docs/en/worktrees
