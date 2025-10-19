import json
import os
from datetime import datetime

DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        default_data = {
            "musteriler": [
                {
                    "tc": "11111111111",
                    "ad": "Ali",
                    "soyad": "Vural",
                    "sifre": "1234",
                    "hesaplar": [
                        {
                            "iban": "TR001",
                            "hesap_adi": "Vadesiz Hesap",
                            "bakiye": 5000.0,
                            "borc": 1000.0,
                            "islemler": []
                        },
                        {
                            "iban": "TR002",
                            "hesap_adi": "Vadeli Hesap",
                            "bakiye": 10000.0,
                            "borc": 0.0,
                            "islemler": []
                        }
                    ]
                }
            ]
        }
        save_data(default_data)
        return default_data
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_musteri_by_tc(tc):
    data = load_data()
    for musteri in data["musteriler"]:
        if musteri["tc"] == tc:
            return musteri
    return None

def get_hesap_by_iban(tc, iban):
    musteri = get_musteri_by_tc(tc)
    if musteri:
        for hesap in musteri["hesaplar"]:
            if hesap["iban"] == iban:
                return hesap
    return None

def get_all_hesaplar(tc):
    musteri = get_musteri_by_tc(tc)
    if musteri:
        return musteri["hesaplar"]
    return []

def update_bakiye(tc, iban, yeni_bakiye):
    data = load_data()
    for musteri in data["musteriler"]:
        if musteri["tc"] == tc:
            for hesap in musteri["hesaplar"]:
                if hesap["iban"] == iban:
                    hesap["bakiye"] = yeni_bakiye
                    save_data(data)
                    return True
    return False

def update_borc(tc, iban, yeni_borc):
    data = load_data()
    for musteri in data["musteriler"]:
        if musteri["tc"] == tc:
            for hesap in musteri["hesaplar"]:
                if hesap["iban"] == iban:
                    hesap["borc"] = yeni_borc
                    save_data(data)
                    return True
    return False

def add_islem(tc, iban, aciklama, miktar):
    data = load_data()
    for musteri in data["musteriler"]:
        if musteri["tc"] == tc:
            for hesap in musteri["hesaplar"]:
                if hesap["iban"] == iban:
                    islem = {
                        "tarih": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                        "aciklama": aciklama,
                        "tutar": miktar
                    }
                    hesap["islemler"].append(islem)
                    save_data(data)
                    return True
    return False

def get_islemler(tc, iban):
    hesap = get_hesap_by_iban(tc, iban)
    if hesap:
        return hesap["islemler"]
    return []

def verify_login(tc, sifre):
    musteri = get_musteri_by_tc(tc)
    if musteri and musteri["sifre"] == sifre:
        return True
    return False

def add_hesap(tc, yeni_hesap):
    data = load_data()
    for musteri in data["musteriler"]:
        if musteri["tc"] == tc:
            musteri["hesaplar"].append(yeni_hesap)
            save_data(data)
            return True
    return False
