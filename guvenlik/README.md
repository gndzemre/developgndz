# Ajan güvenlik kontrol listesi: her bağlantı bir yetki

> Videodaki vaat: *"Ajan güvenlik kontrol listemi hazırladım."*
> Videodaki üç kural bu listenin iskeleti: **ajan sadece o işin klasörünü görür · deneme izole ortamda yapılır · her adım kayda geçer.**
> Başa bir bölüm daha ekledim, çünkü videonun asıl uyarısı oydu: *"Her bağlantı bir yetki demek."*

Örnekler Claude Code için yazıldı; mantık her ajan aracında aynı. Ayarlar projenin
`.claude/settings.json` dosyasına girer (yalnız sende geçerli olsun istiyorsan `.claude/settings.local.json`).
Hangi dosyaların yüklendiğini Claude Code içinde `/status` gösterir.

Videodaki olay (OpenAI'ın test ajanlarının kapalı ortamdan çıkması) videodan alıntıdır; bu sayfa olayın
ayrıntısına girmez, yalnız senin kurulumunda ne yapacağını listeler.

---

## 0 · Bağlantılar: mail, takvim, dosya

- [ ] **Bağlı olan her şeyi say.** `claude mcp list` ile listele, kullanmadığını kaldır: `claude mcp remove <ad>`.
- [ ] **En dar izinle bağla.** Salt-okunur seçeneği olanı salt-okunur kur. Jetonu proje başına ayrı üret, yalnız gereken izni ver.
- [ ] **Geri alınamayan araçları onaya bağla.** Mail gönderme, davet atma, dosya silme gibi araçlar için `ask` kuralı yaz.
  MCP araç adları `mcp__<sunucu>__<araç>` biçimindedir:

  ```json
  { "permissions": { "ask": ["mcp__<SUNUCU>__<GONDERME_ARACI>"] } }
  ```

- [ ] **Hiç kullanmayacağın aracı kapat.** `deny` listesine yaz. Bütün MCP araçlarını kapatmak için `"deny": ["mcp__*"]`.
- [ ] **Dışarıdan içerik getiren her bağlantı bir giriş kapısıdır.** Gelen bir mailin, web sayfasının ya da issue'nun içindeki
  "şunu yap" cümlesi senin talimatın değildir (prompt injection). Bu tür içeriği işleyen oturumda yazma/gönderme yetkisini
  açık bırakma.
- [ ] **Bağlantıyı kimin yazdığına bak.** Anthropic, dizine aldığı bağlayıcıları kendi listeleme ölçütlerine göre inceliyor ama
  hiçbir MCP sunucusunun güvenlik denetimini yapmıyor ya da yönetmiyor. Kendi yazdığın ya da güvendiğin sağlayıcının sunucusunu kullan.

## 1 · Kural 1: Ajan sadece o işin klasörünü görür

- [ ] **Claude Code'u işin klasöründe başlat**, ev dizininde değil. Manual modda dosya araçları başlatıldığı klasörün dışını
  okumadan/yazmadan önce sorar. Dikkat: bu sınır bir onay sorusudur; **onayladığın bir Bash komutu hesabının yazabildiği her yere yazabilir.**
- [ ] **Gizli dosyaları okumaya kapat:**

  ```json
  {
    "permissions": {
      "deny": ["Read(./.env)", "Read(./.env.*)", "Read(./secrets/**)"]
    }
  }
  ```

  `Read` yasağı aynı yolda `Edit` ve `Write`'ı da durdurur; Claude Code'un tanıdığı `cat`, `head`, `tail`, `sed` gibi
  kabuk komutlarına da uygulanır.
- [ ] **Bu yasağın sınırını bil.** Dosyayı kendisi açan bir Python/Node betiğini durdurmaz. İşletim sistemi düzeyinde
  engel istiyorsan sandbox gerekir (bölüm 2). Bunu aşağıdaki sınamada gördüm.
- [ ] **Ek klasörü yalnız gerektiğinde aç** (`/add-dir` ya da `permissions.additionalDirectories`). Her ek klasör ajanın görüş alanını büyütür.
- [ ] **Ayarları ara ara gözden geçir:** `/permissions`. "Yes, and don't ask again" dediğin her şey kalıcı bir `allow` kuralı olarak
  `.claude/settings.local.json`'a yazılır.

## 2 · Kural 2: Deneme izole ortamda yapılır

- [ ] **Sandbox'ı aç.** Oturumda `/sandbox` ya da ayar dosyasında `"sandbox": { "enabled": true }`. Varsayılan olarak kapalı.
- [ ] **İşletim sistemine bak.** Sandbox macOS, Linux ve WSL2'de çalışır. **Windows'ta doğrudan çalıştırırsan komutlar sandbox'sız koşar**;
  Windows'taysan Claude Code'u WSL2 içinde çalıştır. Linux/WSL2'de `bubblewrap` ve `socat` paketleri gerekir.
- [ ] **Ağı daralt.** Sandbox'ta dışarı doğrudan yol yoktur; izin verilen alan adları listesi boş başlar. Yalnız gerekenleri ekle
  (`sandbox.network.allowedDomains`).
- [ ] **Sandbox dışına kaçışı kapat.** Claude başarısız bir komutu sandbox dışında yeniden denemek isteyebilir;
  `"allowUnsandboxedCommands": false` bunu kapatır. Sandbox kurulamıyorsa sessizce sandbox'sız devam etmesin istiyorsan
  `"failIfUnavailable": true`.
- [ ] **Okuma da açık, bunu kapat.** Varsayılan sandbox makinenin çoğunu okuyabilir, `~/.ssh` ve `~/.aws/credentials` dahil.
  `sandbox.filesystem.denyRead` ile kapat.
- [ ] **Sandbox yalnız kabuk komutlarını kapsar.** Claude'un dosya araçları, MCP sunucuları ve kancalar sandbox dışında koşar;
  onlar için bölüm 1'deki izin kuralları gerekir.
- [ ] **Bütün kontrolleri kapatan modu yalnız kapalı kutuda kullan.** `bypassPermissions` modunu belgeler yalnız konteyner ya da sanal
  makine gibi yalıtılmış ortamlar için öneriyor. Kendi makinende kilitle: `"permissions": { "disableBypassPermissionsMode": "disable" }`.
- [ ] **Yabancı içerikle çalışan işi sanal makinede yap.** Özellikle dış web servisleriyle konuşan betikler için. Bütün Claude Code'u
  bir dev container'da çalıştırmak da resmî seçeneklerden.
- [ ] **Klonladığın depoda `claude -p` koşmadan önce iki dosyayı oku:** `.claude/settings.json` ve `.mcp.json`. Başsız modda (`-p`)
  güven sorusu çıkmaz; deponun ayar dosyasındaki **kancalar ve `env` bloğu kullanılır**, `.mcp.json`'daki sunucular **sormadan bağlanır**.

## 3 · Kural 3: Her adım kayda geçer

- [ ] **Var olan kaydı bil.** Claude Code oturum dökümlerini yerelde `~/.claude/projects/` altında **düz metin** olarak tutar,
  varsayılan 30 gün. Süreyi `cleanupPeriodDays` ayarıyla değiştirirsin.
- [ ] **Düz metin olduğu için oraya sır düşürme.** Bir anahtar sohbete ya da komut çıktısına düştüyse dökümde de durur:
  anahtarı sağlayıcıda iptal et, yenisini üret.
- [ ] **Araç çağrılarını ayrıca kaydet.** Claude Code'un `PostToolUse` kancası her başarılı araç çağrısından sonra çalışır;
  girdide aracın adı (`tool_name`) ve ne ile çağrıldığı (`tool_input`) gelir. Bunu bir dosyaya yazan küçük bir kanca yeter.
- [ ] **Kaydı oku.** Kimsenin bakmadığı kayıt, olmayan kayıttır. Göremediğin şeyi durduramazsın.

## 4 · Onay

- [ ] **Geri dönüşü olmayan komutlar onaysız geçmesin:**

  ```json
  { "permissions": { "ask": ["Bash(git push *)", "Bash(rm *)"] } }
  ```

  Kurallar şu sırayla değerlendirilir: önce `deny`, sonra `ask`, sonra `allow`. Yani bir `allow` kuralı `ask`'ı ezmez.
- [ ] **Bash kuralı bir güvenlik sınırı değildir.** Kural, Claude'un yazdığı komut metnini eşler. `Bash(git push *)` kuralı
  `git push origin main`'i yakalar ama `git -C . push origin main`'i yakalamaz. Gerçek sınır için sandbox.
- [ ] **CLAUDE.md'ye "şunu yapma" yazmak izin değildir.** Talimatlar Claude'un ne yapmaya çalışacağını etkiler; neye izin verildiğini
  Claude Code'un izin kuralları belirler.

## 5 · Gizli değerler

- [ ] **Sırrı prompta, CLAUDE.md'ye ya da komut satırına yazma.** Değeri kullanacak kod `.env`'i kendisi okusun, ekrana basmasın.
- [ ] **`.env` okumaya kapalı olsun** (bölüm 1'deki `deny` kuralları).
- [ ] **Sandbox'ta korunacak anahtarları bildir.** `sandbox.credentials` ile dosya ve ortam değişkeni korunur, örneğin
  `"envVars": [{ "name": "GITHUB_TOKEN", "mode": "deny" }]`.
- [ ] **Kabuk komutlarını kapıda süz.** `PreToolUse` kancası komut çalışmadan önce koşar; `exit 2` ile dönerse Claude Code komutu durdurur.
  Ben `.env` geçen kabuk komutlarını bu yolla reddediyorum.

---

## Başlangıç ayar dosyası

Yukarıdaki maddelerin çoğunu tek dosyada toplar. `.claude/settings.json` olarak kaydet, alan adlarını kendi işine göre değiştir:

```json
{
  "permissions": {
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)"
    ],
    "ask": [
      "Bash(git push *)",
      "Bash(rm *)"
    ],
    "disableBypassPermissionsMode": "disable"
  },
  "sandbox": {
    "enabled": true,
    "allowUnsandboxedCommands": false,
    "filesystem": {
      "denyRead": ["~/.ssh", "~/.aws"]
    },
    "network": {
      "allowedDomains": ["github.com", "*.npmjs.org"]
    }
  }
}
```

Ayar dosyası katı JSON'dur: yorum satırı ya da sondaki virgül hata verir.

## Sınama

Claude Code 2.1.191, Windows 11, 2026-11-05, boş bir geçici klasörde, başsız modda (`claude -p`):

- `Read(./gizli/**)` yasağı varken Read aracıyla okuma: **engellendi** ("File is in a directory that is denied by your permission settings").
- Aynı dosyayı `cat` ile okuma (Bash'e `cat` için izin verilmişken): **engellendi**.
- Aynı dosyayı `python -c "open(...)"` ile okuma, Manual modda ve Bash'e `python` için izin verilmişken: **okundu.**
  Belgedeki uyarı doğru: `Read` yasağı betiklerin dosya açmasını durdurmuyor. (Auto modda sınıflandırıcı bu dolanmayı yakalayıp engelledi;
  buna güvenme, sınır sandbox.)
- `ask` listesindeki `git push` ve `rm`, `--allowedTools` ile izin verilmiş olsa bile **çalışmadı** (başsız modda onay soran komut reddedilir).
- Yukarıdaki başlangıç ayar dosyası hatasız yüklendi. Windows'ta Claude Code şu uyarıyı bastı: *"Sandbox disabled: ... windows is not
  supported (requires macOS, Linux, or WSL2)"*. **Sandbox bölümü bu yüzden denenmedi** (macOS/Linux/WSL2 gerekir).
- Belgeler 2.1.191'den yeni sürümleri anlatıyor; `claude --version` ile kendi sürümüne bak.

## Kaynaklar

- İzinler, kural sırası, Read/Edit kapsamı, Bash kuralının sınırı, modlar, `disableBypassPermissionsMode`, depo güveni:
  [code.claude.com/docs/en/permissions](https://code.claude.com/docs/en/permissions)
- Sandbox anahtarları, desteklenen sistemler, varsayılan kısıtlar ve sınırlar: [code.claude.com/docs/en/sandboxing](https://code.claude.com/docs/en/sandboxing)
- Prompt injection, MCP güvenliği, sanal makine önerisi, çalışma klasörü sınırı: [code.claude.com/docs/en/security](https://code.claude.com/docs/en/security)
- Ayar dosyaları, `/status`, katı JSON: [code.claude.com/docs/en/settings](https://code.claude.com/docs/en/settings)
- Oturum dökümlerinin yeri ve 30 günlük süre (`cleanupPeriodDays`): [code.claude.com/docs/en/data-usage](https://code.claude.com/docs/en/data-usage)
- `PreToolUse` / `PostToolUse` kancaları, `exit 2`: [code.claude.com/docs/en/hooks](https://code.claude.com/docs/en/hooks)
- MCP komutları: [code.claude.com/docs/en/mcp](https://code.claude.com/docs/en/mcp)
