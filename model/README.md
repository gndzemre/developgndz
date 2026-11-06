# Açık modelleri yedekleme: yöntemler + alternatif kaynaklar

> Videodaki vaat: *"Modelleri yedeklemenin yolunu ve alternatif kaynakları tek listede topladım."*
> (caption: *"Yedekleme yöntemlerini ve alternatif kaynakları tek listeye koydum."*)

Raf bugün yerinde; modeller iniyor. Bu sayfa "yarın bir şey değişirse elimde ne kalır" sorusu için.
Kullandığın modelin **kendi kopyası** senin diskinde dursun, ve aynı modeli başka bir yerden de bulabil.

---

## 0 · Neyi yedekliyorsun?

Bir modelin çalışan kopyası tek dosya değildir. Klasörde şunlar birlikte durmalı:

| Ne | Örnek dosya | Neden |
|---|---|---|
| Ağırlıklar | `*.safetensors` · `*.gguf` | Modelin kendisi |
| Yapılandırma | `config.json` · `generation_config.json` | Yükleyici modelin yapısını buradan okur |
| Tokenizer | `tokenizer.json` · `tokenizer_config.json` · `vocab.json` / `merges.txt` | Metni modele çevirir; yoksa ağırlıklar işe yaramaz |
| Lisans + model kartı | `LICENSE` · `README.md` | Kullanım şartları dosyayla birlikte gitsin |
| **Sürüm kimliği** | commit hash (aşağıda) | Hangi sürümü sakladığını bilmek için |

---

## Yedekleme yöntemleri

### 1 · `hf download` ile kendi klasörüne indir (önerilen)

`hf`, Hugging Face'in resmî komut satırı aracı.

```bash
pip install -U huggingface_hub
```

**a) Önce boyuta bak** (hiçbir şey indirmez):

```bash
hf download Qwen/Qwen2.5-0.5B-Instruct --dry-run
```

**b) Sürümü sabitle.** Model sayfası sonradan güncellenebilir. Şu an indirdiğin sürümün kimliğini al:

```bash
hf models info Qwen/Qwen2.5-0.5B-Instruct --json
```

Çıktıdaki `"sha"` alanı commit kimliğidir. Bunu bir yere not et.

**c) O sürümü önbelleğe değil, kendi klasörüne indir:**

```bash
hf download Qwen/Qwen2.5-0.5B-Instruct --revision <COMMIT_KIMLIGI> --local-dir ./model_yedekleri/qwen2.5-0.5b-instruct
```

`--local-dir` dosyaları özgün klasör yapısıyla, düz dosya olarak yazar. Klasörü olduğu gibi harici diske taşıyabilirsin.
Kökte oluşan `.cache/huggingface/` yalnız indirme kaydıdır; Hugging Face belgesine göre indirme bittikten sonra silinebilir.

**d) Bütünlüğü doğrula** (yerel dosyaları Hub'daki sağlama toplamlarıyla karşılaştırır):

```bash
hf cache verify Qwen/Qwen2.5-0.5B-Instruct --local-dir ./model_yedekleri/qwen2.5-0.5b-instruct --fail-on-missing-files
```

**İzin isteyen modeller** (ör. Llama): model sayfasında lisansı kabul et, sonra `hf auth login`.
Jetonu [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)'tan al; komuta düz yazma.

**GGUF depolarında tek nicemleme indir**, hepsini değil:

```bash
hf download <KULLANICI>/<MODEL>-GGUF --include "*Q4_K_M*.gguf" --local-dir ./model_yedekleri/<MODEL>-gguf
```

### 2 · Zaten indirdiklerini bul, ama önbelleği yedek sayma

Daha önce `transformers`, `hf` ya da benzeri bir araçla indirdiğin modeller önbellekte durur:

```bash
hf cache ls
```

Varsayılan yer `~/.cache/huggingface/hub` (`HF_HOME` / `HF_HUB_CACHE` ile değişir).

🔴 **Önbellek bir yedek değildir, iki sebeple:**

- Önbellek dosyaları **sembolik bağlantılarla** tutar (`snapshots/` → `blobs/`). Klasörü düz kopyalamak bağlantıları
  bozabilir. (Windows'ta sembolik bağlantı yoksa dosyalar doğrudan `snapshots/` içine yazılır.)
- `huggingface_hub` önbellek klasörüne bir **`CACHEDIR.TAG`** dosyası koyar. Bu dosya Borg, restic, rsync gibi yedekleme
  araçlarına *"burası yeniden indirilebilir, atlayabilirsin"* der. **Yedek aracın bu klasörü sessizce atlayabilir.**

Önbellekteki bir modeli sakla demek istiyorsan, yöntem 1'deki gibi `--local-dir` ile ayrı bir klasöre indir.

### 3 · Ollama kullanıyorsan

Ollama modelleri kendi klasöründe tutar:

| Sistem | Varsayılan yer |
|---|---|
| macOS | `~/.ollama/models` |
| Linux | `/usr/share/ollama/.ollama/models` |
| Windows | `C:\Users\%username%\.ollama\models` |

Yeri değiştirmek için `OLLAMA_MODELS` ortam değişkenini ayarla (ör. harici bir diske).

Daha taşınabilir yol: modelin **GGUF dosyasını** yöntem 1'le sakla. Gerektiğinde Ollama'ya geri al:

```text
# Modelfile
FROM ./model_yedekleri/<MODEL>.gguf
```

```bash
ollama create <MODEL_ADI> -f Modelfile
```

### 4 · İkinci kopya

Tek diskteki yedek, o disk kadar sağlamdır. Büyük ağırlık klasörlerini ikinci bir yere (harici disk, NAS) kopyala ve
`hf cache verify --local-dir` ile oradaki kopyayı da doğrula.

Kendi Hugging Face hesabına yüklemek (`hf upload`) bir kopya sağlar, ama yine aynı rafta durur. Bu videonun sorusuna
cevap değildir.

---

## Alternatif kaynaklar

Aynı açık modellerin önemli bir kısmı başka depolarda da yayınlanıyor. Her model her yerde yok; aradığın modelin
hangi depoda olduğuna tek tek bak.

| Kaynak | Ne | Nasıl indirilir |
|---|---|---|
| **ModelScope** ([modelscope.cn](https://www.modelscope.cn/models)) | Alibaba'nın model deposu. Qwen gibi birçok model burada da yayınlanıyor | `pip install modelscope` → `modelscope download <SAHIP>/<MODEL> --local-dir ./klasor` |
| **Kaggle Models** ([kaggle.com/models](https://www.kaggle.com/models)) | Google'ın Kaggle'ı üzerindeki model deposu | `pip install kagglehub` → `kagglehub.model_download("<SAHIP>/<MODEL>/<FRAMEWORK>/<VARYANT>", output_dir="./klasor")` |
| **Ollama kütüphanesi** ([ollama.com/library](https://ollama.com/library)) | Ollama'nın kendi model kütüphanesi | `ollama pull <MODEL>` |

**ModelScope örneği** (indirmeyi başlatmadan önce dosya listesine sitede bak):

```bash
modelscope download Qwen/Qwen2.5-0.5B-Instruct --local-dir ./model_yedekleri/qwen2.5-0.5b-ms
```

Belirli dosyalar için adlarını sona ekle (`... config.json tokenizer.json`), ya da `--include "*.safetensors"` kullan.
Windows konsolunda indirme bittikten sonra `'charmap' codec can't encode character` hatası görürsen
`PYTHONIOENCODING=utf-8` ayarla. Sınamada dosya bu hataya rağmen inmişti; hata yalnız ekrana yazdırmadaydı.

**Kaggle örneği** (Python):

```python
import kagglehub

yol = kagglehub.model_download("<SAHIP>/<MODEL>/<FRAMEWORK>/<VARYANT>", output_dir="./model_yedekleri/kaggle")
print(yol)
```

kagglehub belgesine göre giriş yalnız onay isteyen ya da özel modeller için gerekir; diğer herkese açık modeller girişsiz iner.

**Ollama notu:** Adı `hf.co/` ile başlayan Ollama modelleri (`ollama run hf.co/<kullanıcı>/<depo>`) Hugging Face'ten
gelir. Bunlar ayrı bir kaynak sayılmaz.

### Başka kaynaktan inen dosya aynı dosya mı?

Hugging Face'e hâlâ erişebiliyorsan, başka depodan indirdiğin klasörü Hugging Face'teki sürümle karşılaştırabilirsin:

```bash
hf cache verify <SAHIP>/<MODEL> --local-dir ./model_yedekleri/<ModelScope_klasoru>
```

İki yerel kopyayı birbiriyle karşılaştırmak için SHA-256 al. Değerler aynıysa dosya aynıdır:

```bash
# macOS / Linux
sha256sum model.safetensors
```

```powershell
# Windows
certutil -hashfile model.safetensors SHA256
```

---

## Kısa liste: bugün yapılacaklar

1. Kullandığın her model için `hf models info <model> --json` → commit kimliğini not et.
2. `hf download <model> --revision <kimlik> --local-dir <yedek_klasörü>`
3. `hf cache verify <model> --local-dir <yedek_klasörü> --fail-on-missing-files`
4. Klasörü ikinci bir diske kopyala.
5. Aynı modelin ModelScope / Kaggle / Ollama'da olup olmadığına bak, bağlantısını not et.

---

## Kaynaklar

- Hugging Face CLI (`hf download`, `--dry-run`, `--local-dir`, `--revision`, `hf cache`): [huggingface.co/docs/huggingface_hub/guides/cli](https://huggingface.co/docs/huggingface_hub/guides/cli)
- Hugging Face indirme rehberi (`local_dir`, `.cache/huggingface/`): [huggingface.co/docs/huggingface_hub/guides/download](https://huggingface.co/docs/huggingface_hub/guides/download)
- Hugging Face önbellek rehberi (sembolik bağlantılar, Windows, `CACHEDIR.TAG`, `hf cache verify`): [huggingface.co/docs/huggingface_hub/guides/manage-cache](https://huggingface.co/docs/huggingface_hub/guides/manage-cache)
- Ollama model klasörü ve `OLLAMA_MODELS`: [docs.ollama.com/faq](https://docs.ollama.com/faq)
- Ollama'ya GGUF alma (`FROM`, `ollama create`): [docs.ollama.com/import](https://docs.ollama.com/import)
- Ollama'da Hugging Face GGUF'ları: [huggingface.co/docs/hub/ollama](https://huggingface.co/docs/hub/ollama)
- ModelScope Python paketi: [github.com/modelscope/modelscope](https://github.com/modelscope/modelscope)
- kagglehub: [github.com/Kaggle/kagglehub](https://github.com/Kaggle/kagglehub)

## Sınama

2026-11-05, Windows 11, Python 3.14.4, huggingface_hub 2.4.0, modelscope 1.40.2, geçici bir klasörde:

- **Denendi:** `hf download Qwen/Qwen2.5-0.5B-Instruct --dry-run` → 10 dosya, 999,6 MB listelendi, hiçbir şey inmedi.
- **Denendi:** `hf models info ... --json` commit kimliğini (`sha`) verdi. `hf download ... --revision <kimlik> --local-dir`
  dosyayı o sürümden indirdi.
- **Denendi:** `hf download ... --include "*.json" --local-dir` yalnız JSON dosyalarını indirdi. `hf cache verify --local-dir`
  5 dosyayı doğruladı ve eksik dosyalar için uyardı (beklenen; yalnız JSON indirilmişti).
- **Denendi:** `modelscope download Qwen/Qwen2.5-0.5B-Instruct config.json --local-dir` dosyayı indirdi. Dosya
  Hugging Face'ten inenle **bayt bayt aynı** çıktı. İlk denemede Windows konsolunda yazdırma hatası çıktı;
  `PYTHONIOENCODING=utf-8` ile temiz bitti. İki dosyanın `certutil` SHA-256 değerleri aynı çıktı.
- **Denendi:** ModelScope'tan inen klasör `hf cache verify ... --local-dir` ile Hugging Face'teki sağlama toplamına
  karşı doğrulandı (1 dosya kontrol edildi, geçti).
- **Denendi:** `hf cache --help` ve `hf download --help` çıktıları bu sayfadaki bayraklarla örtüşüyor.
- **Denenmedi:** Büyük ağırlık dosyası indirme, GGUF `--include` filtresi, Ollama (bu makinede kurulu değil),
  `ollama create`, kagglehub, `sha256sum` (Linux/macOS), `hf auth login` ve izin isteyen modeller.
