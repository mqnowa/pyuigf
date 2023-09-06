
from dataclasses import dataclass
import json
import os
from pathlib import PurePath

ITEM_TYPE = {
    "武器": "weapon",
    "武器": "weapon",
    "weapon": "weapon",
    "キャラクター": "character",
    "角色": "character",
    "character": "character"
}

LANG = {
    "zh-cn": "chs",
    "zh-tw": "cht",
    "ja-jp": "ja",
    "en-us": "en",
    "de-de": "de",
    "es-es": "es",
    "fr-fr": "fr",
    "id-id": "id",
    "ko-kr": "ko",
    "pt-pt": "pt",
    "ru-ru": "ru",
    "th-th": "th",
    "vi-vn": "vi",
}


@dataclass
class UIGF_Info():
    uid: str
    uigf_version: str
    lang: str | None = None
    export_timestamp: int | None = None
    export_time: str | None = None
    export_app: str | None = None
    export_app_version: str | None = None


@dataclass
class UIGF_Item():
    uigf_gacha_type: str
    gacha_type: str
    id: str
    item_id: str
    time: str
    count: str | None = None
    name: str | None = None
    item_type: str | None = None
    rank_type: str | None = None


_list = list


@dataclass
class UIGF():
    info: UIGF_Info
    list: _list[UIGF_Item]

    def __post_init__(self):
        if isinstance(self.info, dict):
            self.info = UIGF_Info(**self.info)
        self.list = list(map(lambda x: UIGF_Item(**x) if isinstance(x, dict) else x, self.list))


def convert_from_official(item: dict, translate: dict):
    return UIGF_Item(
        "301" if item["gacha_type"] == "400" else item["gacha_type"],
        item["gacha_type"],
        item["id"],
        str(translate[item["name"]]),
        item["time"],
        "1",
        item["name"],
        ITEM_TYPE[item["item_type"]],
        item["rank_type"]
    )


def load_from_official(data: dict):
    _l: list[UIGF_Item] = []
    lang = None
    translate = None
    for i in data["data"]["list"]:
        if not i["lang"] == lang:
            lang = i["lang"]
            with open(str(PurePath(__file__).parent) + "/translate/genshin.json") as f:
                translate = json.load(f)[LANG[lang]]
        _l.append(convert_from_official(i, translate))
    return _l


def convert_from_paimonmoe(item: dict, translate: dict):
    item_id: str = item["name"]
    item_id = " ".join(map(lambda x: x[0].upper() + x[1:].lower(), item_id.split("_")))
    return UIGF_Item(
        "301" if item["code"] == "400" else item["code"],
        item["id"],
        "0",
        str(translate[item_id]),
        item["time"],
        "1",
        item["name"],
        ITEM_TYPE[item["type"]],
        item["rank_type"]
    )


def load_from_paimonmoe(data: dict):
    _l: list[UIGF_Item] = []
    translate = None
    for k in ["wish-counter-beginners", "wish-counter-character-event",
              "wish-counter-standard", "wish-counter-weapon-event"]:
        for item in data[k]["pulls"]:
            translate_path  = str(PurePath(__file__).parent) + "/translate/genshin.json"
            with open(translate_path) as f:
                translate = json.load(f)["en"]
            _l.append(convert_from_paimonmoe(item, translate))


def update_tlanslate():
    import requests
    moduletop = str(PurePath(__file__).parent)
    
    for game in ["genshin", "starrail"]:
        if not os.path.exists(moduletop + "/translate"):
            os.mkdir(moduletop + "/translate")
        res = requests.get(f"https://api.uigf.org/dict/{game}/all.json", stream=True)
        if not res.status_code // 100 == 2:
            print(f"faild to fetch 'https://api.uigf.org/dict/{game}/all.json'")
            continue
        with open(f"{moduletop}/translate/{game}.json", "wb") as f:
            for chunk in res.iter_content(1024):
                f.write(chunk)