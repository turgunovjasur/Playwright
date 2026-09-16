"""Test va flowlar uchun JSON faylga saqlash va undan o'qish funksiyalari."""

import json
from pathlib import Path


DATA_DIR = Path("test-results/data")


# ----------------------------------------------------------------------------------------------------------------------


def data_file(file_name="data_store"):
    """test-results/data/<file_name>.json yo'lini qaytaradi.

    file_name: .json kengaytmasisiz fayl nomi; standart — "data_store".
    """
    return DATA_DIR / f"{file_name}.json"


# ----------------------------------------------------------------------------------------------------------------------


def load_data_file(file_name="data_store"):
    """JSONni dict sifatida o'qiydi; yo'q/bo'sh fayl uchun {}, noto'g'ri JSONda xato.

    file_name: .json kengaytmasisiz fayl nomi; standart — "data_store".
    """
    path = data_file(file_name)
    if not path.exists():
        return {}

    raw = path.read_text(encoding="utf-8")
    if not raw.strip():
        return {}

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"{path} buzilgan JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise AssertionError(f"{path} ichida JSON object bo'lishi kerak")
    return data


# ----------------------------------------------------------------------------------------------------------------------


def write_data_file(data, file_name="data_store"):
    """Vaqtinchalik fayl orqali JSON faylni to'liq almashtiradi.

    data: JSONga mos qiymatlardan iborat dict.
    file_name: .json kengaytmasisiz fayl nomi; standart — "data_store".
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = data_file(file_name)
    temporary_path = path.with_suffix(".json.tmp")
    with temporary_path.open("w", encoding="utf-8") as data_output:
        json.dump(data, data_output, indent=4, ensure_ascii=False)
    temporary_path.replace(path)


# ----------------------------------------------------------------------------------------------------------------------


def save_data(key, value, file_name="data_store"):
    """Bitta kalitni qo'shadi/yangilaydi; qolgan kalitlar saqlanadi.

    key: Kalit nomi, masalan, "product_id".
    value: Saqlanadigan JSONga mos qiymat.
    file_name: .json kengaytmasisiz fayl nomi; standart — "data_store".
    """
    data = load_data_file(file_name)
    data[key] = value
    write_data_file(data, file_name)


# ----------------------------------------------------------------------------------------------------------------------


def load_data(key, file_name="data_store", *, allow_missing=False):
    """Bitta kalitning saqlangan qiymatini qaytaradi.

    key: O'qiladigan kalit nomi, masalan, "product_id".
    file_name: .json kengaytmasisiz fayl nomi; standart — "data_store".
    allow_missing: True bo'lsa yo'q/None/"" qiymat uchun None, aks holda xato.
    """
    value = load_data_file(file_name).get(key)
    if value in (None, ""):
        if allow_missing:
            return None
        raise AssertionError(
            f"{file_name}.json ichida majburiy key topilmadi: {key}"
        )
    return value
