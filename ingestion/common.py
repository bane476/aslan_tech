import json
import re
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def fetch_text(url: str, params: dict | None = None) -> str:
    target_url = url
    if params:
        target_url = f"{url}?{urlencode(params, doseq=True)}"
    request = Request(
        target_url,
        headers={
            "User-Agent": "AslanEnergyRisk/0.1",
            "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
        },
    )
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="ignore")


def fetch_json(url: str, params: dict | None = None) -> dict:
    return json.loads(fetch_text(url, params=params))


def post_json(url: str, data: dict) -> dict:
    payload = urlencode(data, doseq=True).encode()
    request = Request(
        url,
        data=payload,
        headers={
            "User-Agent": "AslanEnergyRisk/0.1",
            "Accept": "application/json,text/plain;q=0.9,*/*;q=0.8",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        },
    )
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8", errors="ignore"))


def parse_number(value: str) -> float | None:
    cleaned = value.replace(",", "").replace("%", "").strip()
    cleaned = re.sub(r"<[^>]+>", "", cleaned)
    cleaned = re.sub(r"[^0-9.\-]", "", cleaned)
    if not cleaned or cleaned in {"-", ".", "-."}:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def strip_tags(value: str) -> str:
    return " ".join(re.sub(r"<[^>]+>", " ", value).split())


def load_json_file(path: str) -> dict | list:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))
