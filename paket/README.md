# Paket güvenliği kontrol listesi: npm ve pip

> Videodaki vaat: *"Paket güvenliği için kullandığım kontrol listesini paylaşıyorum."*
> Videodaki kural: *"Tanımadığın birinden gelen kodu okumadan birleştirme."*

Videoda anlattığım test (İngiltere Yapay Zekâ Güvenlik Enstitüsü, modelin açık kaynak projelere zararlı kod sokma
denemeleri) videodan alıntıdır ve videoda da söylediğim gibi bir simülasyondu. Bu sayfa olayın ayrıntısına girmez.
Ders aynı: bir pakete giren tek satır, o paketi kullanan her projeye taşınır. Liste o tek satırın senin projene
**girdiği dört anı** sırayla kapatıyor: eklerken · kurarken · kurduktan sonra · birleştirirken.

Komutlar npm 11 ve pip için. pnpm/yarn/uv kullanıyorsan aynı maddelerin karşılığı onların belgesinde var.

---

## 1 · Yeni bir paket eklerken

- [ ] **Gerçekten gerekiyor mu?** Beş satırlık bir iş için bağımlılık eklemek, o paketin bütün gelecek sürümlerine güvenmek demek.
- [ ] **Adı harf harf kontrol et.** Popüler paketlere bir harf farkla benzeyen adlar (typosquatting) en eski hiledir. Kurmadan önce
  kime ait olduğuna bak:

  ```bash
  npm view <PAKET> repository.url maintainers time.modified
  ```

  Depo adresi beklediğin yer mi, bakımcılar tanıdık mı, son güncelleme makul mü? PyPI'da aynı bilgi paketin pypi.org sayfasında.
- [ ] **Yeni çıkmış sürümü hemen kurma.** Bekleme süresi, ele geçirilmiş bir hesaptan yayımlanan sürümün başkaları tarafından fark
  edilmesine zaman tanır. npm 11.10 ve üstünde (birim **gün**):

  ```bash
  npm config set min-release-age=7 --location=project
  ```

  pnpm'de karşılığı `minimumReleaseAge` (birim **dakika**, pnpm 10.16 ve üstü).

## 2 · Kurarken

- [ ] **Kurulum betiklerini kapat.** Bir paketin `preinstall` / `install` / `postinstall` betiği, sen daha tek satır kod yazmadan
  makinende çalışır. Proje klasöründeki `.npmrc` dosyasına:

  ```ini
  ignore-scripts=true
  ```

  Betiği gerçekten gereken bir paket varsa (yerel derleme yapanlar gibi) önce betiğin ne yaptığını oku, sonra yalnız o kurulum için aç:
  `npm install <PAKET> --ignore-scripts=false`.
- [ ] **Hangi paketin betiği var, bil:**

  ```bash
  npm query ":attr(scripts, [postinstall])"
  ```

- [ ] **Sürümü sabitle.** `.npmrc`'ye `save-exact=true` ekle; `npm install` `^1.2.3` yerine `1.2.3` yazsın.
- [ ] **Kilit dosyasını depoya koy** (`package-lock.json`) ve CI'da `npm install` değil **`npm ci`** kullan. `npm ci` kilit dosyası
  `package.json` ile uyuşmazsa hata verip durur, kilit dosyasını hiç değiştirmez.
- [ ] **Python'da hash'i kilitle.** Her paketin hash'i requirements dosyasında olunca pip, indirdiği dosya hash'le uyuşmazsa kurmayı reddeder:

  ```text
  six==1.17.0 \
      --hash=sha256:4721f391ed90541fddacab5acf947aa0d3dc7d27b2e1e8eda2be8970586c3274
  ```

  ```bash
  pip install --require-hashes --only-binary :all: -r requirements.txt
  ```

  - Hash'i elle yazma: `pip-compile --generate-hashes requirements.in` (pip-tools) üretir, tek dosya için `pip hash <dosya>`.
  - Hash modu ya hep ya hiç: bir pakete hash yazarsan **bütün** paketler (alt bağımlılıklar dahil) hash'li ve `==` ile sabit olmak zorunda.
  - `--only-binary :all:` kaynak paketleri (sdist) reddeder; kaynak paketi kurmak kurulum sırasında kod çalıştırmak demektir.
  - Kendi projeni kurarken `python -m pip install --no-deps .` kullan; `python setup.py install` hash kontrolünü boşa çıkarır.
- [ ] **Her projeye ayrı sanal ortam** (`python -m venv .venv`). Sistem Python'una paket kurma.

## 3 · Kurduktan sonra: denetle

- [ ] **Bilinen açıkları tara:**

  ```bash
  npm audit --audit-level=high
  pip-audit -r requirements.txt
  ```

  İkisi de açık bulunca sıfırdan farklı bir çıkış koduyla döner; CI'da adım olarak koyarsan açıklı paket birleştirmeyi durdurur.
  `pip-audit`'i projenin sanal ortamına kur: `python -m pip install pip-audit`.
- [ ] **İmzayı doğrula:**

  ```bash
  npm audit signatures
  ```

  İndirdiğin paketlerin kayıt defteri imzasıyla ve varsa köken (provenance) belgesiyle eşleştiğini kontrol eder.
- [ ] **"Sıfır açık" temiz demek değildir.** `audit` yalnız **bilinen** açıkları bilir. Dün yayımlanan zararlı bir sürüm henüz veritabanında
  yoktur; ona karşı koruma 1. ve 2. bölüm.

## 4 · Birleştirmeden önce: başkasından gelen katkı

Videodaki kuralın uygulaması bu bölüm.

- [ ] **Bağımlılık değişikliğini ayrı oku.** Bir pull request `package.json` / `package-lock.json` / `requirements.txt` değiştiriyorsa
  kod değişikliğinden ayrı incele. Yeni paket mi eklenmiş, `scripts` alanı mı değişmiş?
- [ ] **Kilit dosyasında paketler nereden geliyor?** Her `"resolved"` adresi resmî kayıt defterini göstermeli:

  ```bash
  git diff main -- package-lock.json | grep '"resolved"'
  ```

  `https://registry.npmjs.org/...` dışında bir adres (bir git deposu, bir dosya, tanımadığın bir sunucu) gördüysen dur.
  Git'ten bağımlılık çekilmesini npm ayarıyla da sınırlayabilirsin: `allow-git` (`all` / `root` / `none`).
- [ ] **Sürüm yükseltmesinin farkını oku:**

  ```bash
  npm diff --diff=<PAKET>@<ESKI_SURUM> --diff=<PAKET>@<YENI_SURUM>
  ```

  Önce `--diff-name-only` ile hangi dosyaların değiştiğine bak. Okunamayan (karıştırılmış) kod, uzun base64 blokları, kurulum anında
  ağa çıkan satırlar dur işaretidir.
- [ ] **Katkıyı yapanın geçmişine bak.** Yeni açılmış hesap, tek katkı, katkıyı öven ama başka hiçbir şey yapmamış hesaplar
  (videodaki testte modelin yaptığı buydu) sinyaldir. Sinyal kanıt değil; ama okumadan birleştirmek için de sebep değil.
- [ ] **Birleştirmeyi onaya bağla.** Ana dalı korumaya al, birleştirme için en az bir inceleme şartı koy.
- [ ] **GitHub'da bağımlılık incelemesini aç.** Dependency review, pull request'te eklenen/kaldırılan/güncellenen bağımlılıkları ve
  bilinen açıklarını gösterir; dependency review action açıklı paket bulunca kontrolü düşürür. Herkese açık depolarda kullanılabilir.

## 5 · Kendi paketini yayımlıyorsan

- [ ] **npm hesabında iki aşamalı doğrulamayı aç.**
- [ ] **Köken belgesiyle yayımla.** GitHub Actions ya da GitLab CI/CD'den `npm publish --provenance` (iş akışında `id-token: write` izni
  gerekir). Trusted publishing kullanıyorsan köken belgesi kendiliğinden üretilir ve CI'da erişim jetonu tutman gerekmez.

---

## Kopyala: proje `.npmrc`

```ini
ignore-scripts=true
save-exact=true
min-release-age=7
```

`min-release-age` npm 11.10 ve üstünde çalışır; `npm --version` ile bak.

## Sınama

2026-11-05, Windows 11, npm 11.11.1 + Node 25.8.2, pip 26.0.1 + Python 3.14, geçici klasörde:

- `postinstall` betiği bir dosya yazan sahte bir yerel paket yaptım. `--ignore-scripts` ile ve `.npmrc`'de `ignore-scripts=true` varken
  `npm ci` ile kurulumda **betik çalışmadı**; normal kurulumda ve `--ignore-scripts=false` ile **çalıştı**.
- `npm query ":attr(scripts, [postinstall])"` o paketi ve betiğini **listeledi**.
- `package.json`'daki sürümü kilit dosyasından farklı yapınca `npm ci` **durdu** (`EUSAGE`, "package.json and package-lock.json ... are in sync").
- `npm install <paket> --min-release-age=7` normal kurdu; `--min-release-age=99999` ile **kurmadı** (`ENOVERSIONS`). Aynısı
  `npm config set min-release-age=... --location=project` ile `.npmrc`'ye yazınca da oldu.
- `npm audit --audit-level=high` 0 açık / çıkış 0; `npm audit signatures` "1 package has a verified registry signature".
- `npm diff --diff-name-only` iki sürüm arasında değişen 4 dosyayı listeledi; kilit dosyasındaki `"resolved"` satırında yerel paketin
  `file:` adresi göründü.
- pip: doğru hash ile kurulum **başarılı**; yanlış hash ile **reddedildi** ("THESE PACKAGES DO NOT MATCH THE HASHES"); hash'siz bir paket
  eklenince **reddedildi** ("Hashes are required in --require-hashes mode").
- `pip-audit` 2.10.1: temiz dosyada "No known vulnerabilities found"; eski bir `urllib3` sürümünde açıkları listeledi, çıkış kodu 1.
- `pip-compile --generate-hashes`, GitHub dependency review ve `npm publish --provenance` **denenmedi**.

## Kaynaklar

- `min-release-age`, `ignore-scripts`, `save-exact`, `allow-git`, `audit-level`: [docs.npmjs.com/cli/v11/using-npm/config](https://docs.npmjs.com/cli/v11/using-npm/config)
- `npm ci`: [docs.npmjs.com/cli/v11/commands/npm-ci](https://docs.npmjs.com/cli/v11/commands/npm-ci)
- `npm audit` ve `npm audit signatures`: [docs.npmjs.com/cli/v11/commands/npm-audit](https://docs.npmjs.com/cli/v11/commands/npm-audit)
- `npm diff`: [docs.npmjs.com/cli/v11/commands/npm-diff](https://docs.npmjs.com/cli/v11/commands/npm-diff)
- `npm query` seçicileri: [docs.npmjs.com/cli/v11/using-npm/dependency-selectors](https://docs.npmjs.com/cli/v11/using-npm/dependency-selectors)
- Köken belgesi ve trusted publishing: [docs.npmjs.com/generating-provenance-statements](https://docs.npmjs.com/generating-provenance-statements)
- npm iki aşamalı doğrulama: [docs.npmjs.com/configuring-two-factor-authentication](https://docs.npmjs.com/configuring-two-factor-authentication)
- pnpm `minimumReleaseAge`: [pnpm.io/settings](https://pnpm.io/settings)
- pip hash modu, `--only-binary`, `--no-deps`: [pip.pypa.io/en/stable/topics/secure-installs](https://pip.pypa.io/en/stable/topics/secure-installs/)
- `pip-audit`: [pypi.org/project/pip-audit](https://pypi.org/project/pip-audit/)
- `pip-compile --generate-hashes`: [github.com/jazzband/pip-tools](https://github.com/jazzband/pip-tools)
- GitHub dependency review: [docs.github.com/.../about-dependency-review](https://docs.github.com/en/code-security/supply-chain-security/understanding-your-software-supply-chain/about-dependency-review)
- Korumalı dallar: [docs.github.com/.../about-protected-branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
