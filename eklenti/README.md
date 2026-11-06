# Claude Code'a ilk kurman gereken 5 bağlantı: kurulum komutları

> Videodaki vaat: *"Beşinin kurulum komutlarını tek sayfada topladım."*
> Sıra videodakiyle aynı: GitHub · Context7 · Playwright · Supabase · Arama.

Her komut terminalde çalışır. Kurduğunu görmek için:

```bash
claude mcp list
```

Bir bağlantıyı kaldırmak için `claude mcp remove <ad>`.

**Kapsam:** komutlar varsayılan olarak yalnız bulunduğun proje klasöründe geçerli olur.
Her projede açık olsun istiyorsan komuta `--scope user` ekle.

---

## 1 · GitHub: dal aç, pull request gönder, hata kayıtlarını oku

```bash
claude mcp add --transport http github https://api.githubcopilot.com/mcp/ --header "Authorization: Bearer <GITHUB_JETONUN>"
```

- Jetonu GitHub → Settings → Developer settings → Personal access tokens'tan al. Yalnız ihtiyacın
  olan izinleri ver, proje başına ayrı jeton kullan.
- **Önce yalnız okumak istiyorsan** adresin sonuna `readonly` ekle:
  `https://api.githubcopilot.com/mcp/readonly`
- Kaynak: [github/github-mcp-server](https://github.com/github/github-mcp-server) · [Claude Code MCP dokümanı](https://code.claude.com/docs/en/mcp)

## 2 · Context7: kütüphanenin güncel dokümanından yazsın

```bash
claude mcp add --transport http context7 https://mcp.context7.com/mcp
```

- Anahtarsız çalışır. Daha yüksek kota istersen context7.com'dan ücretsiz anahtar alıp şunu ekle:
  `--header "Authorization: Bearer <CONTEXT7_ANAHTARIN>"`
- Kaynak: [upstash/context7](https://github.com/upstash/context7)

## 3 · Playwright: yazdığı sayfayı kendisi açsın, tıklasın, hatayı görsün

```bash
claude mcp add playwright -- npx @playwright/mcp@latest
```

- Node.js 18 veya üstü gerekir.
- Kaynak: [microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp)

## 4 · Supabase: şemayı okusun, sorguyu yazsın, sonucu kontrol etsin

```bash
claude mcp add --transport http supabase "https://mcp.supabase.com/mcp?project_ref=<PROJE_KIMLIGIN>&read_only=true"
```

- `project_ref` bağlantıyı tek projeye kilitler, `read_only=true` sorguları salt-okunur kullanıcıyla
  çalıştırır. **Başlangıçta ikisini de açık tut.** Adresi tırnak içinde yaz (içindeki `&` yüzünden).
- Kurduktan sonra Claude Code'da `/mcp` → supabase → Authenticate: giriş tarayıcıdan yapılır, jeton gerekmez.
- Üretim veritabanına yalnız gerçekten gerekiyorsa bağlan.
- Kaynak: [Supabase MCP dokümanı](https://supabase.com/docs/guides/getting-started/mcp)

## 5 · Arama: cevabı o anki internetten getirsin

Claude Code'un kendi arama aracı zaten var. Ayrı bir arama bağlantısı, farklı bir arama sağlayıcısı
istediğinde ya da sayfa içeriğini de çekmek istediğinde işe yarar. Üç seçenekten birini seç:

```bash
# Exa: anahtarsız da çalışır (sınırlı hızla)
claude mcp add --transport http exa https://mcp.exa.ai/mcp

# Tavily: ücretsiz anahtar tavily.com'dan
claude mcp add --transport http tavily "https://mcp.tavily.com/mcp/?tavilyApiKey=<TAVILY_ANAHTARIN>"

# Brave Search: anahtar brave.com/search/api'den
claude mcp add --transport stdio brave-search --env BRAVE_API_KEY=<BRAVE_ANAHTARIN> -- npx -y @brave/brave-search-mcp-server
```

- Üçünün de ücretsiz kullanım katmanı var; güncel kotayı sağlayıcının fiyat sayfasından kontrol et.
- Kaynak: [exa-labs/exa-mcp-server](https://github.com/exa-labs/exa-mcp-server) · [tavily-ai/tavily-mcp](https://github.com/tavily-ai/tavily-mcp) · [brave/brave-search-mcp-server](https://github.com/brave/brave-search-mcp-server) · [Claude Code araçları](https://code.claude.com/docs/en/tools-reference)

---

## Her bağlantı bir yetki

Videodaki uyarının uzun hâli:

- **Sadece gerçekten kullandığını kur.** Her bağlantı Claude'a yeni bir kapı açar.
- Dışarıdan içerik çeken bağlantılar (tarayıcı, arama, GitHub'daki yabancı bir kayıt) zararlı bir
  metni Claude'un önüne getirebilir. Claude Code'un kendi dokümanı da bunu söylüyor: *"Servers that
  fetch external content can expose you to prompt injection risk."*
- Mümkün olanı **salt-okunur** kur (GitHub `readonly`, Supabase `read_only=true`), ihtiyaç doğunca aç.
- Araç çağrılarını onaylama adımını kapatma.
- Jetonları komut geçmişinde bırakmamak için, kurduktan sonra terminal geçmişini temizlemeyi düşün.

## Sınandı

Claude Code 2.1.191 ile 2026-11-05'te boş bir klasörde kuruldu, `claude mcp list` sonucu:
Playwright · Context7 · Exa · Brave **bağlandı**, Supabase **tarayıcıdan giriş bekledi** (beklenen),
GitHub sahte jetonla **reddedildi** (beklenen; gerçek jetonla bağlanır). Tavily anahtarsız denenmedi.
