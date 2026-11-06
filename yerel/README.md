# Kendi bilgisayarında yapay zekâ sohbeti: üç aracı hangi sırayla kuracağın

> Videodaki vaat: *"Kurulum adımlarını tek sayfada topladım."* (caption: *"Üç aracı hangi sırayla kuracağını adım adım yazdım."*)
> Sıra: **Ollama** (modeli çalıştırır) → **LM Studio** (makinene hangi modelin sığacağını gösterir) → **Open WebUI** (sohbet ekranı).

**Önce bil:** model ilk seferde internetten indirilir. İndirdikten sonra sohbet internetsiz çalışır.
Hız bilgisayarının gücü kadardır; buluttaki hızı bekleme.

---

## 1 · Ollama: modeli indirip arka planda çalıştırır

**Kur**

```powershell
# Windows (PowerShell) — ya da ollama.com/download'dan OllamaSetup.exe
irm https://ollama.com/install.ps1 | iex
```

```bash
# macOS / Linux — macOS'ta ollama.com/download'dan Ollama.dmg de olur
curl -fsSL https://ollama.com/install.sh | sh
```

**İlk modeli çalıştır** (küçük bir modelle başla, yaklaşık 1,3 GB):

```bash
ollama run llama3.2:1b
```

- Ollama arka planda `127.0.0.1:11434` adresinde bekler; diğer araçlar onu buradan bulur.
- Gereksinim: Windows 10 22H2 ve üstü, macOS 14 (Sonoma) ve üstü.
- Kaynak: [ollama.com/download](https://ollama.com/download) · [docs.ollama.com](https://docs.ollama.com/faq) · [llama3.2 modeli](https://ollama.com/library/llama3.2)

## 2 · LM Studio: hangi modeli seçeceğini tahmine bırakmaz

[lmstudio.ai/download](https://lmstudio.ai/download)'dan uygulamayı kur. Bir modeli yüklemeden önce
LM Studio **bellek tahmini** gösterir ve makinene sığmayacaksa uyarır. Modeli seçerken bunu kullan:
sığan en büyük modeli bul, sonra Ollama'da aynı modelin sürümünü indir (`ollama run <model>`) ya da
doğrudan LM Studio'da kullan.

- Komut satırından da bakılabilir: `lms load <model> --estimate-only` (modeli yüklemeden tahmin basar).
- Resmî donanım önerisi: Windows'ta en az 16 GB RAM ve AVX2 destekli işlemci; Mac'te Apple Silicon
  (Intel desteklenmiyor), macOS 14 ve üstü, 16 GB+ RAM önerilir.
- LM Studio kendi başına da bir model çalıştırıcı. Ollama'yla aynı işi yapabildiği için ikisini aynı
  anda çalıştırmak zorunda değilsin; bu kurulumda LM Studio'yu model seçmek için kullanıyoruz.
- Kaynak: [sistem gereksinimleri](https://lmstudio.ai/docs/app/system-requirements) · [lms load](https://lmstudio.ai/docs/cli/local-models/load) · [bellek tahmini (0.3.27)](https://lmstudio.ai/blog/lmstudio-v0.3.27)

## 3 · Open WebUI: alıştığın sohbet ekranı, konuşmalar senin diskinde

**Docker ile** (Ollama aynı bilgisayarda):

```bash
docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data -e WEBUI_SECRET_KEY=<RASTGELE_UZUN_BIR_METIN> --name open-webui --restart always ghcr.io/open-webui/open-webui:main
```

Tarayıcıda `http://localhost:3000` aç, hesabını oluştur, model listesinde Ollama'daki modeli seç.

**Docker yoksa Python ile** (Python 3.12 kullan):

```bash
pip install open-webui
open-webui serve
```

Bu durumda adres `http://localhost:8080`.

- Open WebUI Ollama'yı kendisi arar. Bulamazsa: Settings → Admin → Connections'tan Ollama adresini
  (`http://localhost:11434`) elle gir.
- Kaynak: [Open WebUI hızlı başlangıç](https://docs.openwebui.com/getting-started/quick-start/) · [Ollama bağlantısı](https://docs.openwebui.com/getting-started/quick-start/connect-a-provider/starting-with-ollama)

---

## Kontrol: gerçekten yerelde mi?

1. Model indikten sonra interneti kapat.
2. Open WebUI'de bir soru sor. Cevap geliyorsa sohbet tamamen kendi bilgisayarında dönüyor.

## Bilmen gerekenler

- Bulutta iki saniyede gelen cevap burada yarım dakika sürebilir; küçük modeller daha hızlıdır.
- Konuşmalar Open WebUI'nin veri klasöründe (Docker'da `open-webui` biriminde) durur. Yedeğini sen alırsın.
- Komutlar resmî belgelerden alındı. Bu sayfa Windows'ta uçtan uca kurulup denenmedi.
