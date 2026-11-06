# Figma ⇄ Claude Code: kurulum ve komponent eşleme (Code Connect) rehberi

> Videodaki vaat: *"Kurulum ve eşleme adımlarını tek rehbere döktüm."*
> Sıra videodakiyle aynı: önce bağlantı (Claude Code Figma'yı okusun), sonra Code Connect eşlemesi,
> sonra iki yön: Figma linkinden ekran kurmak ve canlı sayfayı Figma'ya geri yollamak.

Rehber Figma'nın kendi **MCP sunucusunu** kullanıyor. MCP, Claude Code'un dış bir araca bağlanma yolu.
Bağlandıktan sonra Claude Code tasarımı bir resim gibi tahmin etmiyor; katmanları, değişkenleri ve
komponentleri yapılandırılmış veri olarak alıyor. Görsel karşılaştırma için ekran görüntüsü aracı da var,
ama asıl iş yapılandırılmış veriden yürüyor.

---

## 0 · Önce bunlara bak: hangi plan, hangi koltuk

| Özellik | Ne gerekir (Figma'nın belgesine göre) |
|---|---|
| MCP sunucusu (okuma) | Tam verim için **Dev veya Full koltuk**. Starter planda ya da View/Collab koltukta ayda **6 araç çağrısı** sınırı var. |
| Code Connect | **Dev veya Full koltuk**, **Professional, Organization veya Enterprise** plan. Professional'da aynı anda tek kütüphane ve tek framework etkin olabilir. |
| Figma'ya yazma (tasarım sistemi kurmak gibi) | Uzak (remote) MCP sunucusu. Taslaklar (drafts) dışına yazmak için **Full koltuk**. Figma bunu şimdilik beta olarak sunuyor ve ileride kullanım bazlı ücretli olacağını yazıyor. |
| Canlı sayfayı Figma'ya göndermek | Uzak MCP sunucusu + desteklenen istemci (Claude Code listede). Starter dahil planlarda var. |

Plan adları ve sınırlar değişebiliyor, kurmadan önce aşağıdaki kaynaklardan güncelini kontrol et.

---

## 1 · Bağlantı: Claude Code Figma'yı okusun

**Önerilen yol: Figma eklentisi.** MCP ayarını ve Figma'nın hazır iş akışı skill'lerini birlikte kurar
(Code Connect ve tasarım sistemi adımlarında bu skill'ler kullanılıyor).

```bash
claude plugin install figma@claude-plugins-official
```

Kurduktan sonra Claude Code'u yeniden başlat, `/plugin` → **Installed** sekmesinde Figma'yı gör.

**Elle yol: yalnız MCP sunucusu.**

```bash
claude mcp add --transport http figma https://mcp.figma.com/mcp
```

**Giriş:** Claude Code'u aç, `/mcp` yaz, `figma`'yı seç, **Authenticate** de. Giriş tarayıcıda yapılır,
jeton kopyalaman gerekmez. Sonra:

```bash
claude mcp list
```

`figma` satırında bağlı görünmeli.

**İlk deneme.** Figma'da bir çerçeveye sağ tıkla → *Copy link to selection*. Claude Code'a:

```text
Bu Figma çerçevesindeki değişkenleri ve kullanılan komponentleri listele: <FIGMA_LINKI>
```

Uzak sunucuda bağlantıyı (link) mutlaka ver; "seçili olanı oku" demek yalnız masaüstü sunucuda çalışır.

---

## 2 · Eşleme: Code Connect

Code Connect olmadan Claude Code, Figma'daki butonun projende hangi bileşene karşılık geldiğini
**tahmin eder**. Figma'nın kendi rehberi de bunu söylüyor: Code Connect, üretilen kodun projendeki
bileşenleri yeniden kullanmasının en iyi yolu. Eşleme yapıldığında MCP yanıtına "bu Figma komponentinin
koddaki karşılığı şu" bilgisi eklenir.

Ön koşullar: Figma'daki komponentlerin bir takım kütüphanesinde **yayınlanmış** olması ve linkin
`node-id` içermesi.

### 2a · Kısa yol: Claude Code yazsın

Figma eklentisiyle gelen `figma-code-connect` skill'i, verdiğin Figma komponenti için eşleme dosyasını
senin deponda yazar. CLI kurulu ve `figma.config.json` hazır olmalı (2b'deki ilk iki adım).

```text
Bu Figma komponenti için Code Connect eşlemesini yaz, projedeki karşılığını bul: <KOMPONENT_LINKI>
```

Çıkan dosyayı oku, düzelt, sonra 2b'deki gibi yayınla.

### 2b · Elle yol: CLI ve şablon dosyası

**1. CLI'yı kur** (Node.js 18 veya üstü):

```bash
npm install --global @figma/code-connect@latest
```

**2. Proje köküne `figma.config.json` koy:**

```json
{
  "codeConnect": {
    "include": ["**/*.figma.ts"],
    "label": "React",
    "language": "jsx"
  }
}
```

`label` ve `language` kendi framework'üne göre değişir (Figma'nın örneği: SwiftUI için `"Swift"` ve `"swift"`).
TypeScript kullanıyorsan `tsconfig.json`'a şunu ekle, şablonlarda otomatik tamamlama gelsin:

```json
{ "compilerOptions": { "types": ["@figma/code-connect/figma-types"] } }
```

**3. Her komponent için bir şablon dosyası yaz.** Bileşenin yanına, aynı adla: `Button.figma.ts`

```ts
// url=https://www.figma.com/design/<DOSYA_KIMLIGI>/<DOSYA_ADI>?node-id=<NODE_ID>
import figma from 'figma'

const instance = figma.selectedInstance
const label = instance.getString('Label')
const disabled = instance.getBoolean('Disabled')
const size = instance.getEnum('Size', {
  Large: 'large',
  Medium: 'medium',
  Small: 'small',
})

export default {
  example: figma.code`
    <Button size={${size}} disabled={${disabled}}>
      ${label}
    </Button>
  `,
  imports: ['import { Button } from "components/Button"'],
  id: 'button',
}
```

- İlk satırdaki `url`, Figma'daki komponentin linki.
- `getString`, `getBoolean`, `getEnum` Figma'daki özellik adlarını okur; `'Label'`, `'Size'` gibi adlar
  **senin Figma komponentindeki adlarla birebir** aynı olmalı.
- `imports` ve `example`, Figma'da gösterilecek ve Claude Code'a verilecek kod.

**4. Kontrol et, sonra yayınla.** Figma hesabından bir kişisel erişim jetonu (personal access token) üret.
İzinler: **Code Connect: Write**, **File content: Read**. Jetonu komuta yazmak yerine ortam değişkenine koy:

```bash
export FIGMA_ACCESS_TOKEN=<FIGMA_JETONUN>

npx figma connect parse              # şablonları yerelde okur, JSON basar (jeton gerekmez)
npx figma connect publish --dry-run  # yayınlamadan sınar
npx figma connect publish            # yayınlar
```

**5. Gör.** Yayın çıktısındaki linki aç → üst çubukta **Dev Mode** → sağdaki **Inspect** panelinde
kendi kod parçan görünmeli.

Bir eşlemeyi geri almak için:

```bash
npx figma connect unpublish --node=<KOMPONENT_LINKI> --label=React
```

🔴 `--node` vermeden `unpublish` çalıştırırsan klasördeki **bütün** eşlemeler kalkar.

Kod yazmadan bağlamak istersen Figma'nın **Code Connect UI**'ı da var (Figma içinden, GitHub bağlantısıyla).

---

## 3 · Kullanım: üç yön

### Figma linkinden ekran kurmak

```text
Bu ekranı projedeki mevcut bileşenler ve renk/boşluk değişkenleriyle kur.
Yeni bileşen veya sabit renk kodu yazma; karşılığı yoksa listele, ben karar vereyim.
<FIGMA_LINKI>
```

Code Connect eşlemesi varsa yanıtta hangi bileşenin kullanılacağı yazılı gelir; yoksa model tahmin eder.

### Canlı sayfayı Figma'ya geri yollamak

Figma buna **code to canvas** diyor (`generate_figma_design` aracı). Yalnız uzak sunucuda çalışır,
Claude Code destekli istemciler arasında. Figma'nın örnek promptu:

```text
Start a local server for my app and capture the UI in a new Figma file.
```

Ajan uygulamanı yerelde açar, yakalama betiğini ekler ve bir tarayıcı penceresi açar; ilk yakalama
kendiliğinden yapılır. Penceredeki araç çubuğundan *Entire screen* veya *Select element* ile devam edersin.
Yeni dosya taslaklarına (drafts) düşer.

Bilmen gereken: yakalanan katmanlar **düzenlenebilir ama kütüphanene bağlı değil**. Hedef dosyada
değişkenli bir kütüphane varsa eşleşen renk/sayı/metin değişkenleri kendiliğinden bağlanır, komponentler bağlanmaz.
Masaüstü sunucusu da kuruluysa istemci onu seçebilir; Figma bu durumda masaüstü sunucusunu kaldırmayı öneriyor.

### Koddaki bileşenlerden Figma'da tasarım sistemi kurmak

Bu Figma'ya **yazma** işi (`use_figma` aracı). Figma eklentisindeki `figma-generate-library` skill'i
sıralamayı yönetiyor: önce değişkenler (token), sonra bileşenler ve varyantlar.

```text
Projedeki renk, boşluk ve tipografi token'larından ve src/components altındaki bileşenlerden
Figma'da bir tasarım sistemi kur. Önce kapsamı ve kabul listesini göster, onaylamadan yazma.
```

Önce tek bir bileşenle dene. Bütün kütüphane uzun bir iş ve beta bir özellik.

---

## Bilmen gerekenler

- Figma'daki adlandırma ne kadar düzenliyse (komponent özellikleri, değişken adları) sonuç o kadar iyi.
  Code Connect şablonundaki özellik adları Figma'dakilerle birebir aynı olmalı.
- Yazma araçları dosyanı değiştirir. İlk denemeleri bir kopya dosyada ya da taslaklarda yap.
- Jetonu depoya, `figma.config.json`'a ya da komut geçmişine bırakma.
- Figma'nın MCP araçları hızla değişiyor. Güncel araç listesi aşağıdaki "Tools and prompts" sayfasında.

## Sınama

2026-11-05, Windows, Claude Code 2.1.191, Node 25.8.2, geçici bir klasörde:

- `@figma/code-connect` 2.1.0 **yerel** kuruldu; `npx figma connect --help` komutları listeledi
  (`publish`, `unpublish`, `parse`, `create`, `migrate`, `preview`).
- Bu sayfadaki `figma.config.json` + `Button.figma.ts` ile `npx figma connect parse` **çalıştı**:
  şablonu okudu, `label: React`, `language: jsx`, `isParserless: true` olarak JSON üretti.
- `publish --dry-run` sahte jetonla **reddedildi** (`403 Invalid token`), beklenen; gerçek jetonla denenmedi.
- `claude mcp add --transport http figma https://mcp.figma.com/mcp` (proje kapsamında) **eklendi**;
  giriş (OAuth) yapılmadığı için bağlantı açılmadı.
- `figma@claude-plugins-official` eklentisinin resmî eklenti listesinde durduğu kontrol edildi; eklenti kurulmadı.
- **Denenmedi:** gerçek bir Figma dosyasından okuma, Code Connect yayını, canlı sayfayı Figma'ya
  yakalama, Figma'ya tasarım sistemi yazma. Bunlar Figma hesabı ve uygun koltuk ister.

## Kaynaklar

- Figma MCP sunucusu, giriş: https://developers.figma.com/docs/figma-mcp-server/
- Araç listesi (`get_design_context`, `get_variable_defs`, `add_code_connect_map`, `generate_figma_design`, `use_figma`…): https://developers.figma.com/docs/figma-mcp-server/tools-and-prompts/
- Code to canvas (canlı sayfayı Figma'ya): https://developers.figma.com/docs/figma-mcp-server/code-to-canvas/
- Claude Code kurulumu (Figma yardım merkezi): https://help.figma.com/hc/en-us/articles/35281350665623
- Figma'nın MCP rehberi ve skill'leri (`figma-code-connect`, `figma-generate-library`, `figma-generate-design`): https://github.com/figma/mcp-server-guide
- Code Connect, plan ve koltuk: https://developers.figma.com/docs/code-connect/
- Code Connect CLI hızlı başlangıç (kurulum, jeton izinleri, şablon, publish/unpublish): https://developers.figma.com/docs/code-connect/quickstart-guide/
- Claude Code MCP komutları: https://code.claude.com/docs/en/mcp
