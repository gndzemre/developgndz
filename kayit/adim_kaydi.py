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
