# 4 GB'lık ekran kartında 70 milyarlık model: AirLLM kurulum adımları

> Videodaki vaat: *"Kurulum adımlarını tek sayfada topladım."*
> Araç: **AirLLM** (açık kaynak, Apache 2.0). Modeli tek parça yüklemez, katman katman yükler: ekran kartında aynı anda tek katman durur.

🔴 **Dürüst not:** "70B modeli 4 GB'ta çalıştırır" iddiası **AirLLM'in kendi README'sine** dayanıyor. Bu sayfada 70B model
çalıştırılmadı, hız ölçülmedi. Ne denendiği en altta, **Sınama** bölümünde.

---

## 0 · Başlamadan önce: üç şeyi kontrol et

| Ne | Neden | Nasıl |
|---|---|---|
| **Ekran kartı belleği** | README tablosu: Llama 3.x 70B (tam hassasiyet) için ~4 GB | `nvidia-smi` (NVIDIA kartlarda) |
| **Disk alanı** | Asıl darboğaz disk. Model önce indirilir, sonra katmanlara bölünüp **ayrıca** kaydedilir | Aşağıdaki hesap |
| **İnternet** | Model ilk seferde indirilir; sonrası makinende | — |

**Disk hesabı (2026-11-05'te Hugging Face'ten ölçüldü):**

- `meta-llama/Llama-3.3-70B-Instruct`: model dosyaları toplam **141,1 GB**
- `Qwen/Qwen2.5-72B-Instruct`: toplam **145,4 GB**

İndirilen orijinal + bölünmüş kopya birlikte durduğu için **yaklaşık iki katı boş alan** ayır. `delete_original=True`
verirsen README'ye göre orijinal silinir ve yerin yarısı geri gelir (adım 6). AirLLM bölmeye başlamadan boş alanı
kendisi kontrol eder; yetmezse `NotEnoughSpaceException` verir.

Model dosyalarını **SSD'ye** koy. README'ye göre hızı belirleyen şey diskten yükleme.

## 1 · Sanal ortam aç

```bash
python -m venv airllm-env
```

```powershell
# Windows
airllm-env\Scripts\activate
```

```bash
# macOS / Linux
source airllm-env/bin/activate
```

## 2 · Önce CUDA'lı PyTorch'u kur (sıra önemli)

AirLLM varsayılan olarak ekran kartını (`cuda:0`) kullanır. PyTorch'u **AirLLM'den önce**, kendi CUDA sürümüne uygun
olarak kur. Komutu [pytorch.org/get-started/locally](https://pytorch.org/get-started/locally/) seçicisinden al
(işletim sistemi · pip · CUDA sürümü). Biçimi şuna benzer:

```bash
pip install torch --index-url https://download.pytorch.org/whl/cu132
```

Sonra kontrol et:

```bash
python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
```

Sonuç `True` olmalı. `False` çıkarsa ekran kartı görülmüyordur: kurulan torch CUDA'sız olabilir. Seçicideki
CUDA'lı komutla yeniden kur. AirLLM'i önce kurarsan pip torch'u kendisi seçer, ve bu kontrol `False` çıkabilir.

## 3 · AirLLM'i kur

```bash
pip install airllm
```

Bu sayfa yazılırken PyPI'deki sürüm **4.0.0** (2026-09-05). Paket bir Python sürüm sınırı bildirmiyor;
Python 3.14'te bağımlılıklar sorunsuz çözüldü. Bağımlılıkları (transformers, accelerate, safetensors,
huggingface_hub…) kendisi getirir.

## 4 · Model erişimini hazırla

**Llama modelleri izin istiyor.** `meta-llama/Llama-3.3-70B-Instruct` Hugging Face'te erişim onaylı (gated) bir model:

1. Model sayfasında lisansı kabul et, onay gelsin.
2. [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)'tan okuma yetkili bir jeton oluştur.
3. Terminalde giriş yap (`hf` komutu AirLLM'le birlikte gelen `huggingface_hub` paketinde):

```bash
hf auth login
```

Giriş yapmak yerine jetonu doğrudan AirLLM'e de verebilirsin: `hf_token="<HF_JETONUN>"` (adım 5). 401 hatası
alırsan bu yolu kullan.

**İzin beklemek istemiyorsan:** `Qwen/Qwen2.5-72B-Instruct` erişim onayı istemiyor. AirLLM README'si Qwen2.5'i
desteklenenler arasında sayıyor.

## 5 · Önce küçük bir modelle zinciri dene

140 GB indirmeden önce her şeyin çalıştığını ~1 GB'lık bir modelle gör. `dene.py` adlı bir dosya aç:

```python
from airllm import AutoModel

MAX_LENGTH = 128

model = AutoModel.from_pretrained(
    "Qwen/Qwen2.5-0.5B-Instruct",                     # ~1 GB; sonra 70B ile değiştir
    layer_shards_saving_path="<GENIS_DISKTEKI_KLASOR>", # bölünmüş katmanlar buraya
    profiling_mode=True,                              # süreleri kendin gör
)

input_text = ["What is the capital of United States?"]

input_tokens = model.tokenizer(
    input_text,
    return_tensors="pt",
    return_attention_mask=False,
    truncation=True,
    max_length=MAX_LENGTH,
    padding=False,
)

generation_output = model.generate(
    input_tokens["input_ids"].to(model.device),
    max_new_tokens=20,
    use_cache=True,
    return_dict_in_generate=True,
)

print(model.tokenizer.decode(generation_output.sequences[0]))
```

```bash
python dene.py
```

Kod, README'deki hızlı başlangıç örneğinin aynısı; yalnız model adı ve iki parametre değişti.

## 6 · 70B'ye geç

`dene.py`'de model satırını değiştir:

```python
model = AutoModel.from_pretrained(
    "meta-llama/Llama-3.3-70B-Instruct",              # ya da "Qwen/Qwen2.5-72B-Instruct"
    layer_shards_saving_path="<GENIS_DISKTEKI_KLASOR>",
    # hf_token="<HF_JETONUN>",                        # hf auth login yapmadıysan
    # delete_original=True,                           # orijinali silip yer aç (yarı yarıya)
    profiling_mode=True,
)
```

**İlk çalıştırma uzun sürer:** önce indirir, sonra modeli katmanlara bölüp diske yazar. Sonraki çalıştırmalar
bölünmüş kopyadan devam eder.

## 7 · İsteğe bağlı: sıkıştırma

README'ye göre katmanları 4 ya da 8 bitlik bloklar hâlinde sıkıştırmak diskten yüklenen veriyi küçültür ve
çıkarımı hızlandırır (README "3 kata kadar" diyor; bu sayfada ölçülmedi).

```bash
pip install -U bitsandbytes
```

```python
model = AutoModel.from_pretrained(
    "meta-llama/Llama-3.3-70B-Instruct",
    compression="4bit",     # ya da "8bit"
)
```

Paket kodunda gördüğüm bir ayrıntı: sıkıştırma açıkken **önceden yükleme (`prefetching`) kendiliğinden kapanıyor.**

## Ayarlar (README + paket kodu)

| Parametre | Ne yapar | Varsayılan |
|---|---|---|
| `layer_shards_saving_path` | Bölünmüş katmanların yazılacağı klasör | model önbelleğinin yanı |
| `compression` | `"4bit"` / `"8bit"` sıkıştırma | `None` |
| `delete_original` | İndirilen orijinali silip yalnız bölünmüş kopyayı tutar | `False` |
| `hf_token` | İzinli modeller için Hugging Face jetonu | `None` |
| `prefetching` | Sonraki katmanı hesap sürerken yükler | `True` |
| `profiling_mode` | Süre ölçümlerini basar | `False` |
| `device` | Hangi kart | `"cuda:0"` |
| `max_seq_len` | En uzun dizi | `512` |

## Mac'te

- Yalnız **Apple Silicon**. `mlx` ve `torch` kurulu olmalı; kod aynı.
- Şimdilik yalnız Llama tarzı modeller (`LlamaForCausalLM`, `MistralForCausalLM`) çalışıyor. Diğerleri indirmeden önce hata verir.

## Sık hatalar (README FAQ)

| Hata | Büyük ihtimalle | Çözüm |
|---|---|---|
| `MetadataIncompleteBuffer` | Disk doldu | Yer aç (Hugging Face önbelleğini temizle), yeniden çalıştır |
| `401 Client Error ... gated` | İzinli model, jeton yok | Lisansı kabul et, `hf_token` ver |
| `ValueError: max() arg is an empty sequence` | Qwen/ChatGLM'i Llama sınıfıyla açtın | `AutoModel` kullan |
| `Asking to pad but the tokenizer does not have a padding token` | Tokenizer'da dolgu yok | `padding=False` |

## Bilmen gerekenler

- **Bedeli hız.** Her katman diskten belleğe taşınır. Bulutta saniyeler süren cevap burada dakikalar sürebilir.
  Ne kadar süreceğini `profiling_mode=True` ile kendi makinende ölç.
- Bu yüzden sohbet için değil; akşam bırakıp sabah sonucuna baktığın işler için (toplu özet, sınıflandırma, uzun metin işleme).
- Karşılığında model senin diskinde durur. İndirme bittikten sonra çalışmak için internet gerekmez, veri dışarı çıkmaz.

---

## Kaynaklar

- AirLLM README (kurulum, örnek kod, tablo, ayarlar, macOS, FAQ): [github.com/lyogavin/airllm](https://github.com/lyogavin/airllm)
- AirLLM PyPI (sürüm 4.0.0): [pypi.org/project/airllm](https://pypi.org/project/airllm/)
- PyTorch kurulum seçicisi: [pytorch.org/get-started/locally](https://pytorch.org/get-started/locally/)
- PyTorch CUDA paket dizini: [download.pytorch.org/whl/cu132/torch](https://download.pytorch.org/whl/cu132/torch/)
- Hugging Face CLI (`hf auth login`): [huggingface.co/docs/huggingface_hub/guides/cli](https://huggingface.co/docs/huggingface_hub/guides/cli)
- Hugging Face jetonları: [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
- Model sayfaları: [meta-llama/Llama-3.3-70B-Instruct](https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct) · [Qwen/Qwen2.5-72B-Instruct](https://huggingface.co/Qwen/Qwen2.5-72B-Instruct) · [Qwen/Qwen2.5-0.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct)

## Sınama

2026-11-05, Windows 11, Python 3.14.4:

- **Denendi:** `pip install --no-deps airllm==4.0.0` temiz bir sanal ortama kuruldu. `AutoModel` ve temel sınıfın
  imzası paket kaynağından okundu: tablodaki parametre adları ve varsayılanlar (`device="cuda:0"`, `max_seq_len=512`,
  sıkıştırmada `prefetching`'in kapanması, disk kontrolü) koddan doğrulandı.
- **Denendi:** `pip install --dry-run airllm==4.0.0` bağımlılıkları sorunsuz çözdü (torch 2.15.0, transformers 5.22.1,
  huggingface_hub 2.4.0 seçildi).
- **Denendi:** Model boyutları Hugging Face API'den ölçüldü (141,1 GB · 145,4 GB · Llama'nın erişim onayı istediği).
  `Qwen/Qwen2.5-0.5B-Instruct` için `hf download --dry-run` toplamı 999,6 MB gösterdi.
- **Denendi:** `download.pytorch.org/whl/cu132` dizininde torch 2.15.0'ın Windows (Python 3.13/3.14) paketleri listelendi.
- **Denenmedi:** CUDA'lı torch kurulumu, herhangi bir modelin indirilip AirLLM'le çalıştırılması, 70B, hız, sıkıştırma,
  macOS. Çok GB'lık indirme gerektirdiği için yapılmadı. 4 GB / 70B iddiası README'nin.
