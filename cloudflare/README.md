# CF'yi Claude Code'a bağlama adımları

> Videodaki vaat: *"CF ile Claude Code'u bağlama adımlarını paylaşıyorum."*
> (caption: *"Cloudflare'ı Claude Code'a bağlama adımlarını yazıya çıkardım."*)

**CF** (`cf`), Cloudflare'ın ajanlar düşünülerek yazdığı yeni komut satırı aracı. Cloudflare API'sinin tamamından
üretiliyor, çıktısı varsayılan olarak JSON. 2026-09-28'de **açık beta** olarak duyuruldu.
Bu sayfa yazılırken npm'deki sürüm `1.0.0-beta.28`. Beta olduğu için komutlar değişebilir.

Bağlantı iki parçadan oluşuyor:

1. **CF'yi kur ve giriş yap** → Claude Code terminalde `cf` komutlarını çalıştırabilir.
2. **Claude Code'a CF'yi tanıt** → bir satırlık talimat + Cloudflare'ın resmî skill paketi (içinde CF skill'i ve Cloudflare'ın MCP sunucusu var).

---

## 1 · CF'yi kur

```bash
npm install --global cf
```

```bash
cf --version
```

- **Node.js:** paketin bildirdiği sürümler `^22.23.0 || ^24.22.0 || ^26.12.0` (Cloudflare belgesi "22.18 ve üstü" diyor;
  paket dosyası daha dar). Bunlardan birini kullan. Ben Node 25'te denedim: `EBADENGINE` uyarısı verdi ama çalıştı.
- yarn / pnpm ile de kurulur: `yarn global add cf` · `pnpm add --global cf`.

## 2 · Giriş yap (bu adımı sen yaparsın, ajan değil)

```bash
cf auth login
```

Tarayıcıda Cloudflare onay ekranı açılır; onayı bir insan vermek zorunda. Uzak makinede ya da SSH'te:
`cf auth login --no-browser` (bağlantıyı basar, tarayıcıyı sen açarsın).

Kontrol:

```bash
cf auth whoami
```

- CF kendi girişini tutar, **Wrangler girişini kullanmaz.**
- Hangi yetkilerin verildiğini görmek için: `cf auth scopes`.
- **Birden çok hesap / proje:** `cf auth create <PROFIL_ADI>` ile adlı profil aç, `cf auth activate <PROFIL_ADI>` ile
  bulunduğun klasöre bağla. Böylece Claude Code o klasörde yalnız o hesabı görür.
- **Gözetimsiz çalışan ajan / CI:** giriş yerine `CLOUDFLARE_API_TOKEN` ve `CLOUDFLARE_ACCOUNT_ID` ortam
  değişkenlerini ver. Jetona yalnız işin gerektirdiği izinleri ver. Jeton ayarlıysa kayıtlı girişin önüne geçer.

## 3 · Claude Code'a "Cloudflare işinde CF kullan" de

Cloudflare'ın önerdiği satırı kullanıcı düzeyindeki `CLAUDE.md`'ne (`~/.claude/CLAUDE.md`) ekle:

```markdown
When interacting with Cloudflare, use the `cf` CLI unless the project has a Wrangler configuration file.
```

CF bunu kendisi de destekliyor: ajan `cf --help` çalıştırdığında çıktının başında *"komut ararken önce
`cf cli search` kullan"* diyen bir blok çıkıyor. Yani Claude Code iç içe `--help` gezmek yerine şunu yapar:

```bash
cf cli search "create D1 database"
```

Giriş gerektirmez, yerelde arar, en iyi beş komutu JSON olarak döner.

## 4 · Cloudflare'ın resmî skill paketini kur (önerilen)

Claude Code'un içinde, birer birer (ilki bitmeden ikincisini yazma):

```text
/plugin marketplace add cloudflare/skills
```

```text
/plugin install cloudflare@cloudflare
```

Kurulumdan sonra gerekirse `/reload-plugins`.

Paket 19 skill içeriyor. Bu iş için önemlisi **`cf-cli`**: *"CF komutlarını bulmak ve çalıştırmak, CF ile Wrangler
arasında seçim yapmak."* Paket ayrıca Cloudflare'ın **API MCP sunucusunu** (Code Mode) getiriyor. Claude bir Cloudflare
aracını ilk çağırdığında tarayıcıda OAuth onayı açılır; hangi izinleri vereceğini orada seçersin.

### Paket yerine yalnız MCP istiyorsan

Skill paketini kurmak istemiyorsan, Cloudflare'ın MCP sunucularını doğrudan ekleyebilirsin:

```bash
claude mcp add --transport http cloudflare-api https://mcp.cloudflare.com/mcp
claude mcp add --transport http cloudflare-docs https://docs.mcp.cloudflare.com/mcp
```

- `cloudflare-api`: Cloudflare API'sinin tamamı, iki araçla (`search()` ve `execute()`). İlk kullanımda Claude Code'da
  `/mcp` → `cloudflare-api` → kimlik doğrula.
- `cloudflare-docs`: güncel Cloudflare belgeleri. Giriş istemiyor.
- Paketi kurduysan `cloudflare-api`'yi ayrıca ekleme; paket zaten getiriyor.
- Komutlar varsayılan olarak yalnız o proje klasöründe geçerli. Her yerde istiyorsan `--scope user` ekle.

## 5 · İzinleri ayarla

Arama ve belge komutları zararsız; her seferinde onay sormasın. Proje kökünde `.claude/settings.json`:

```json
{
  "permissions": {
    "allow": [
      "Bash(cf cli search *)",
      "Bash(cf docs search *)",
      "Bash(cf schema *)",
      "Bash(cf auth whoami)"
    ],
    "ask": [
      "Bash(cf deploy *)"
    ]
  }
}
```

`deploy`, `delete` ve listede olmayan her şey varsayılan olarak onay sormaya devam eder. `ask` kuralı, ileride
`allow` listesine daha geniş bir `cf` kuralı eklesen bile yayına almayı sana sordurur (Claude Code kuralları
önce `deny`, sonra `ask`, sonra `allow` sırasıyla değerlendirir).

## 6 · İlk deneme

Claude Code'da:

```text
Cloudflare hesabımdaki zone'ları listele. Önce cf cli search ile doğru komutu bul.
```

Claude `cf zones list` çalıştırır; sonuç JSON gelir. İstersen önce `--dry-run` ile ne gönderileceğini gösterir:

```bash
cf zones list --dry-run
```

Çıktı: hangi adrese hangi yöntemle istek gideceği. Kimlik bilgisi gerekmez, hiçbir şey göndermez.

---

## Güvenlik notları (Cloudflare'ın ajan belgesinden)

- **`--dry-run` kullan.** İsteği göndermeden gösterir.
- 🔴 **"Başarılı" çıkış kodu silindi demek değil.** Etkileşimsiz oturumda `--force` olmadan çalışan yıkıcı bir komut
  `Aborted.` yazar ve **yine 0 ile çıkar.** Ajanın "sildim" demesini çıktıya bakarak doğrula.
- **`--force`'u gözden geçir.** Bazı komutlarda API parametresi de; örneğin `cf workers delete --force`, başka
  Worker'ların bağlı olduğu bir Worker'ı da siler.
- **Wrangler projesinde dikkat:** Wrangler yapılandırması olup `cloudflare.config.ts` olmayan projede `cf dev`,
  `cf build`, `cf deploy` çalıştırma. Önce `cf migrate --dry-run`, sonra `cf migrate`.
- **Aramalar anonim kalsın.** `cf cli search` ve `cf docs search` sorgularına hesap kimliği, alan adı, e-posta, jeton yazma.
  CF'nin kendi yardım çıktısı da bunu söylüyor.
- **Telemetri:** CF anonim kullanım verisi toplar. Kapatmak için `cf cli telemetry disable`, durumu görmek için
  `cf cli telemetry status`.

---

## Kaynaklar

- CF duyurusu (açık beta, 3000+ işlem, JSON varsayılan, `cf cli search`, `cf migrate`): [blog.cloudflare.com/cloudflare-cf-cli-launch](https://blog.cloudflare.com/cloudflare-cf-cli-launch/)
- CF belgeleri: [developers.cloudflare.com/cf](https://developers.cloudflare.com/cf/)
- Kurulum ve giriş (`cf auth login`, `--no-browser`, ortam değişkenleri, Node sürümü): [developers.cloudflare.com/cf/get-started](https://developers.cloudflare.com/cf/get-started/)
- Kodlama ajanlarıyla CF (CLAUDE.md satırı, `cf cli search`, `--dry-run`, `Aborted.` uyarısı): [developers.cloudflare.com/cf/agents](https://developers.cloudflare.com/cf/agents/)
- Claude Code için Cloudflare kurulumu (skill paketi komutları, MCP sunucu adresleri): [developers.cloudflare.com/agent-setup/claude-code](https://developers.cloudflare.com/agent-setup/claude-code/)
- Cloudflare MCP sunucuları (API sunucusu, OAuth / jeton, Code Mode): [developers.cloudflare.com/agents/model-context-protocol/mcp-servers-for-cloudflare](https://developers.cloudflare.com/agents/model-context-protocol/mcp-servers-for-cloudflare/)
- Cloudflare skill paketi: [github.com/cloudflare/skills](https://github.com/cloudflare/skills)
- CF kaynak kodu: [github.com/cloudflare/cf](https://github.com/cloudflare/cf) · npm: [npmjs.com/package/cf](https://www.npmjs.com/package/cf)
- Claude Code MCP: [code.claude.com/docs/en/mcp](https://code.claude.com/docs/en/mcp)
- Claude Code izin kuralları (`allow` / `ask` / `deny`, `Bash(... *)`): [code.claude.com/docs/en/permissions](https://code.claude.com/docs/en/permissions)

## Sınama

2026-11-05, Windows 11, Node 25.8.2, Claude Code 2.1.191, geçici bir klasörde (global kurulum yapılmadı):

- **Denendi:** `npm i cf@1.0.0-beta.28` (yerel) → kuruldu, `EBADENGINE` uyarısı verdi (Node 25 bildirilen aralıkta değil).
  `cf --version` → `1.0.0-beta.28`.
- **Denendi:** `cf --help` → başta ajanlara `cf cli search` kullanmasını söyleyen blok çıktı.
- **Denendi:** `cf cli search "create D1 database"` → girişsiz, beş JSON sonuç (`cf d1 create` ilk sırada).
- **Denendi:** `cf docs search "deploy a worker"` → girişsiz, sıralı JSON sonuç ve belge adresleri.
- **Denendi:** `cf auth whoami` → `"authenticated": false` (beklenen; giriş yapılmadı). `cf auth --help`,
  `cf auth login --help` (`--no-browser`, `--force`), `cf cli telemetry --help` bayrakları sayfadakilerle aynı.
- **Denendi:** `cf zones list --dry-run` → girişsiz, `GET https://api.cloudflare.com/client/v4/zones` isteğini gösterdi.
- **Denendi:** `claude mcp add --transport http --scope local` ile iki sunucu geçici klasöre eklendi. `claude mcp list`:
  `docs.mcp.cloudflare.com` **bağlandı**, `mcp.cloudflare.com` **kimlik doğrulama bekledi** (beklenen; OAuth gerekiyor).
  Sonra `claude mcp remove` ile ikisi de kaldırıldı.
- **Denenmedi:** `npm install --global cf`, `cf auth login` (tarayıcı onayı + gerçek hesap), `/plugin marketplace add` ve
  `/plugin install` (kullanıcı düzeyinde kalıcı değişiklik yaptığı için), OAuth sonrası MCP araç çağrısı,
  `.claude/settings.json` izin kuralları, `cf deploy`, `cf migrate`, `cf cli telemetry disable`.
