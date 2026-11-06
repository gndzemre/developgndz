# Ajanın her adımını kaydeden kurulum (Claude Code)

> Videodaki vaat: *"Ajanlarımın her adımını kaydeden kurulumumu paylaşıyorum."*
> Videodaki dert: *"Sen ajanına iş verdiğinde sonuca bakıyorsun. Arada ne yaptığına bakmıyorsun."*

Videodaki olay (test ajanlarının terk edilmiş bir wikide kendilerine kalıcı bir not alanı kurması) videodan alıntıdır;
bu sayfa olayın ayrıntısına girmez. Oradan alınacak ders şu: ajanın dışarıda bir yere yazması **sonuçta görünmez**,
ancak adım kaydında görünür.

Kurulum üç katman. Birincisi zaten sende var, ikincisi asıl kurulum, üçüncüsü isteğe bağlı.

---

## 1 · Zaten var olan: oturum dökümleri

Claude Code her oturumu yerelde `~/.claude/projects/` altında **düz metin** olarak saklar, varsayılan **30 gün**.
Süreyi ayar dosyasındaki `cleanupPeriodDays` ile değiştirirsin.

Eksiği: her oturum ayrı bir dosya, okuması zor ve 30 gün sonra silinir. "Bu hafta ajanlarım hangi komutları çalıştırdı,
hangisi hata verdi?" sorusuna tek bakışta cevap vermez. İkinci katman bunun için.

## 2 · Asıl kurulum: her adımı tek dosyaya yazan kanca

Claude Code'un **kancaları** (hooks) belirli anlarda senin komutunu çalıştırır ve o anın bilgisini komutun girdisine
JSON olarak verir. Bu kurulum yedi anı yakalayıp tek bir dosyaya satır satır yazar:

| An | Ne zaman | Kayda ne düşer |
|---|---|---|
| `SessionStart` | oturum açılınca | oturum kimliği |
| `UserPromptSubmit` | sen bir istek gönderince | isteğin ilk 300 karakteri |
| `PostToolUse` | bir araç başarıyla çalışınca | araç adı + ne ile çağrıldığı (komut, dosya yolu, adres) + süre |
| `PostToolUseFailure` | bir araç hata verince | araç adı + ne ile çağrıldığı + hatanın ilk satırı |
| `SubagentStop` | bir alt ajan bitince | alt ajanın türü |
| `Stop` | Claude cevabını bitirince | — |
| `SessionEnd` | oturum kapanınca | kapanma nedeni |

Alt ajanların araç çağrıları da kayda düşer; o satırlarda `ajan` alanı alt ajanın türünü gösterir.

### Kurulum (3 adım)

1. Projende `.claude/hooks/` klasörünü aç, aşağıdaki betiği `adim_kaydi.py` adıyla kaydet.
2. Aşağıdaki ayarı projenin `.claude/settings.json` dosyasına koy (dosyada başka ayar varsa `hooks` bloğunu ekle).
3. Kayıt dosyasını depoya gönderme. `.gitignore`'a ekle:

   ```text
   .claude/kayit/
   ```

macOS/Linux'ta `python` yerine `python3` yazman gerekebilir. Ayar **exec biçiminde** yazıldı (`command` + `args`): komut bir kabuktan
geçmeden doğrudan çalışır, Windows'ta Git Bash / PowerShell farkına takılmaz.

Bütün projelerinde açık olsun istiyorsan aynı `hooks` bloğunu `~/.claude/settings.json`'a koy; o zaman betiğin yolunu da
sabit bir yere taşı.

### `.claude/settings.json`

```json
{
  "hooks": {
    "SessionStart":       [{ "hooks": [{ "type": "command", "command": "python", "args": ["${CLAUDE_PROJECT_DIR}/.claude/hooks/adim_kaydi.py"] }] }],
    "UserPromptSubmit":   [{ "hooks": [{ "type": "command", "command": "python", "args": ["${CLAUDE_PROJECT_DIR}/.claude/hooks/adim_kaydi.py"] }] }],
    "PostToolUse":        [{ "matcher": "*", "hooks": [{ "type": "command", "command": "python", "args": ["${CLAUDE_PROJECT_DIR}/.claude/hooks/adim_kaydi.py"] }] }],
    "PostToolUseFailure": [{ "matcher": "*", "hooks": [{ "type": "command", "command": "python", "args": ["${CLAUDE_PROJECT_DIR}/.claude/hooks/adim_kaydi.py"] }] }],
    "SubagentStop":       [{ "hooks": [{ "type": "command", "command": "python", "args": ["${CLAUDE_PROJECT_DIR}/.claude/hooks/adim_kaydi.py"] }] }],
    "Stop":               [{ "hooks": [{ "type": "command", "command": "python", "args": ["${CLAUDE_PROJECT_DIR}/.claude/hooks/adim_kaydi.py"] }] }],
    "SessionEnd":         [{ "hooks": [{ "type": "command", "command": "python", "args": ["${CLAUDE_PROJECT_DIR}/.claude/hooks/adim_kaydi.py"] }] }]
  }
}
```

### `.claude/hooks/adim_kaydi.py`

```python
#!/usr/bin/env python3
"""Claude Code adım kaydı: her kanca olayını tek satır JSON olarak dosyaya ekler.

Kullanım (kanca):   python .claude/hooks/adim_kaydi.py          (girdi stdin'den gelir)
Kullanım (okuma):   python .claude/hooks/adim_kaydi.py --son 20
Kayıt dosyası:      <proje>/.claude/kayit/adimlar.jsonl
"""
import datetime
import json
import os
import re
import sys

KAYIT_KLASORU = os.path.join(
    os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd(), ".claude", "kayit"
)
KAYIT_DOSYASI = os.path.join(KAYIT_KLASORU, "adimlar.jsonl")
OZET_SINIRI = 300

# Komutlara karışmış gizli değerleri kayda geçirmeden önce maskele.
GIZLI_DESENLER = [
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._~+/=-]+"),
    re.compile(r"(?i)(api[_-]?key|token|secret|password|passwd|authorization)(\s*[:=]\s*|\s+)\S+"),
    re.compile(r"sk-[A-Za-z0-9_-]{10,}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
]


def maskele(metin):
    for desen in GIZLI_DESENLER:
        metin = desen.sub("<MASKELENDI>", metin)
    return metin


def kisalt(metin):
    metin = maskele(str(metin)).replace("\n", " ")
    return metin if len(metin) <= OZET_SINIRI else metin[:OZET_SINIRI] + "..."


def arac_ozeti(girdi):
    """Aracın ne yaptığını tek satırda anlatan alanı seç."""
    if not isinstance(girdi, dict):
        return kisalt(girdi)
    for alan in ("command", "file_path", "url", "pattern", "query", "prompt", "description"):
        if girdi.get(alan):
            return f"{alan}: {kisalt(girdi[alan])}"
    return kisalt(json.dumps(girdi, ensure_ascii=False))


def kaydet():
    try:
        # Windows'ta varsayılan kodlama UTF-8 olmayabilir; girdiyi bayt olarak oku.
        olay = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except Exception as hata:  # Kanca asla oturumu bozmasın.
        olay = {"hook_event_name": "OKUNAMADI", "hata": str(hata)}

    satir = {
        "zaman": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "olay": olay.get("hook_event_name"),
        "oturum": olay.get("session_id"),
    }
    if olay.get("agent_type"):
        satir["ajan"] = olay.get("agent_type")
    if olay.get("tool_name"):
        satir["arac"] = olay["tool_name"]
        satir["ne"] = arac_ozeti(olay.get("tool_input"))
    if olay.get("hook_event_name") == "PostToolUse":
        satir["sonuc"] = "basarili"
    if olay.get("error"):
        satir["sonuc"] = "hata"
        satir["hata"] = kisalt(str(olay["error"]).splitlines()[0])
    if olay.get("duration_ms") is not None:
        satir["sure_ms"] = olay["duration_ms"]
    if olay.get("hook_event_name") == "UserPromptSubmit":
        satir["istek"] = kisalt(olay.get("prompt", ""))
    if olay.get("reason"):
        satir["neden"] = olay["reason"]

    os.makedirs(KAYIT_KLASORU, exist_ok=True)
    with open(KAYIT_DOSYASI, "a", encoding="utf-8") as dosya:
        dosya.write(json.dumps(satir, ensure_ascii=False) + "\n")
    return 0


def son_satirlar(adet):
    if not os.path.exists(KAYIT_DOSYASI):
        print("Kayıt yok:", KAYIT_DOSYASI)
        return 0
    with open(KAYIT_DOSYASI, encoding="utf-8") as dosya:
        satirlar = dosya.readlines()[-adet:]
    sys.stdout.reconfigure(encoding="utf-8")
    for ham in satirlar:
        s = json.loads(ham)
        print(" | ".join(str(s.get(k, "")) for k in ("zaman", "olay", "ajan", "arac", "sonuc", "ne", "hata")))
    return 0


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "--son":
        sys.exit(son_satirlar(int(sys.argv[2])))
    sys.exit(kaydet())
```

### Kurduğunu doğrula

1. Claude Code içinde `/hooks` yaz: yedi anın her birinde betiğin göründüğünü gör.
2. Ona küçük bir iş ver: bir dosya yazsın, bir komut çalıştırsın.
3. Kaydı oku:

   ```bash
   python .claude/hooks/adim_kaydi.py --son 20
   ```

   Çıktı böyle görünür (sınamadan, kısaltılmış):

   ```text
   ... | PostToolUse        |        | Write | basarili | file_path: ...\not.txt |
   ... | PostToolUseFailure |        | Bash  | hata     | command: ls olmayan_klasor | Exit code 2
   ... | PostToolUse        | claude | Bash  | basarili | command: ls |
   ... | SubagentStop       | claude |       |          |  |
   ```

Kanca çalışmıyorsa Claude Code'u `claude --debug` ile başlat; kancanın hata çıktısı orada görünür.

### Kayda neye bakarsın

- **Hatalar:** `--son 200` çıktısında `hata` geçen satırlar. Aynı komut art arda düşüyorsa ajan bir döngüde dönüyordur.
- **Dışarıya çıkan adımlar:** `WebFetch`, `curl`, `wget`, `git push`, `ssh` geçen satırlar. Videodaki gibi "dışarıda bir yere yazma"
  ancak burada görünür.
- **Klasör dışına yazma:** `file_path` alanında projenin dışında bir yol.
- **İstemediğin araç:** görevde olmayan bir MCP aracı (`mcp__...`) ya da alt ajan.

Kayıt ancak okununca işe yarar. Haftada bir `--son 200` yeter.

### Bilmen gerekenler

- **Sırlar:** betik komutlardaki `Bearer ...`, `API_KEY=...`, `token: ...` gibi kalıpları kayda yazmadan önce `<MASKELENDI>` yapar.
  Bu bir süzgeçtir, garanti değil; kayıt dosyasını yine de gizli bilgi gibi koru.
- **İsteklerin metni:** `UserPromptSubmit` satırı isteğinin ilk 300 karakterini yazar. İstemiyorsan settings'ten o bloğu sil.
- **Kanca da koddur.** Kanca, Claude Code'un senin makinende çalıştırdığı bir komuttur. Başkasının deposunu klonladıysan önce `.claude/settings.json`'daki
  kancaları oku: başsız modda (`claude -p`) depo güvenilmemiş olsa bile **kancalar çalışır**.
- **Hız:** betik her araç çağrısında bir kez çalışır ve yalnız dosyaya bir satır ekler; gecikme fark edilmez.

## 3 · İsteğe bağlı: OpenTelemetry ile merkezî izleme

Birden çok makinede ya da ekipte aynı kaydı tek yerde toplamak istiyorsan Claude Code OpenTelemetry olayları da gönderebilir.
Önce ekrana bas, ne geldiğini gör:

```bash
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_LOGS_EXPORTER=console
export OTEL_METRICS_EXPORTER=none
export OTEL_LOGS_EXPORT_INTERVAL=1000
export OTEL_LOG_TOOL_DETAILS=1
claude
```

Her araç çağrısı için `claude_code.tool_result` olayı gelir: araç adı, başarılı mı (`success`), süre (`duration_ms`).
`OTEL_LOG_TOOL_DETAILS=1` olmadan Bash komutlarının metni ve araç girdileri **gönderilmez**. İsteklerin metni varsayılan olarak
gizlidir; `OTEL_LOG_USER_PROMPTS=1` açar.

Kalıcı kurulum için `console` yerine `otlp` seç ve kendi toplayıcının adresini ver:

```bash
export OTEL_LOGS_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_PROTOCOL=grpc
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
```

Dikkat: bu değişkenleri projenin `.claude/settings.json` dosyasındaki `env` bloğuna yazarsan Claude Code onları **yok sayar**.
Kabukta tanımla ya da `~/.claude/settings.json`'a yaz.

---

## Sınama

Claude Code 2.1.191, Windows 11, Python 3.14, 2026-11-05, boş bir geçici klasörde, başsız modda (`claude -p`):

- Yukarıdaki iki dosya olduğu gibi kopyalandı. Claude'a bir dosya yazdırdım, hata veren bir komut çalıştırdım, bir alt ajana `ls`
  koşturdum. Kayda **9 satır** düştü: `SessionStart`, `UserPromptSubmit`, `Write` (başarılı), `ls olmayan_klasor` (hata,
  "Exit code 2"), alt ajanın `ls`'i (`ajan: claude`), `SubagentStop`, `Agent`, `Stop`, `SessionEnd`.
- Maskeleme sahte değerlerle ayrıca denendi: `Authorization: Bearer ...`, `API_KEY=...` ve `sk-...` kalıpları kayıtta `<MASKELENDI>` oldu.
- Türkçe karakterler ilk denemede bozuk yazıldı (Windows kodlaması); betik girdiyi UTF-8 bayt olarak okuyacak şekilde düzeltildi,
  ikinci denemede doğru yazıldı.
- OpenTelemetry: yukarıdaki `console` ayarlarıyla tek bir oturum açıldı; çıktıda `claude_code.tool_result` olayı, `tool_name: "Bash"`,
  `success: "true"` ve `OTEL_LOG_TOOL_DETAILS=1` sayesinde komutun metni göründü. `otlp` ile bir toplayıcıya gönderim **denenmedi**.
- macOS/Linux'ta ve etkileşimli oturumda (`/hooks` görünümü, `claude --debug`) **denenmedi**; bunlar belgelerden.

## Kaynaklar

- Kancalar: olay adları, ayar yapısı, `matcher`, ortak girdi alanları (`session_id`, `hook_event_name`, `agent_type`),
  `PostToolUse` girdisi (`tool_name`, `tool_input`, `tool_response`, `duration_ms`), `PostToolUseFailure` (`error`),
  `SessionEnd` `reason` değerleri, exec biçimi (`command` + `args`), `${CLAUDE_PROJECT_DIR}`, `/hooks`, `claude --debug`:
  [code.claude.com/docs/en/hooks](https://code.claude.com/docs/en/hooks)
- Depo güveni ve başsız modda kancaların çalışması: [code.claude.com/docs/en/permissions](https://code.claude.com/docs/en/permissions)
- Oturum dökümleri, 30 gün, `cleanupPeriodDays`: [code.claude.com/docs/en/data-usage](https://code.claude.com/docs/en/data-usage)
- OpenTelemetry değişkenleri, `claude_code.tool_result` alanları, gizlilik varsayılanları: [code.claude.com/docs/en/monitoring-usage](https://code.claude.com/docs/en/monitoring-usage)
- Proje `env` bloğundaki telemetri değişkenlerinin yok sayılması: [code.claude.com/docs/en/settings](https://code.claude.com/docs/en/settings)
