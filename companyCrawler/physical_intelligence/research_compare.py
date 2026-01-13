import json
from pathlib import Path

DATA_PATH = Path("data/physical_intelligence/research.json")


def researchCompare(curr_items):
    if not DATA_PATH.exists():
        _save(curr_items)
        return []

    prev_items = json.loads(DATA_PATH.read_text(encoding="utf-8"))

    prev_ids = {item["id"] for item in prev_items}
    curr_ids = {item["id"] for item in curr_items}

    new_ids = curr_ids - prev_ids

    new_items = [
        item for item in curr_items
        if item["id"] in new_ids
    ]

    _save(curr_items)
    return new_items


def _save(items):
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_text(
        json.dumps(items, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
