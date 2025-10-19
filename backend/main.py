import json
from datetime import datetime
import os

DATA_FILE = "data.json"

class Islem:
    def __init__(self, aciklama, miktar):
        self.tarih = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        self.aciklama = aciklama
        self.tutar = miktar

    def to_dict(self):
        return {
            "tarih": self.tarih,
            "aciklama": self.aciklama,
            "tutar": self.tutar
        }

class Hesap:
    def __init__(self, iban, hesap_adi, bakiye=0.0, borc=0.0, islemler=None):
        self.iban = iban
        self.hesap_adi = hesap_adi
        self.bakiye = bakiye
        self.borc = borc
        self.islemler = islemler if islemler else []

    def para_yatir(self, miktar):
        if miktar > 0:
            self.bakiye += miktar
            self.islemler.append(Islem("Para yatırma", miktar).to_dict())
            return True
        return False

    def para_cek(self, miktar):
        if 0 < miktar <= self.bakiye:
            self.bakiye -= miktar
            self.islemler.append(Islem("Para çekme", -miktar).to_dict())
            return True
        return False

    def borc_ode(self, miktar):
        if 0 < miktar <= self.borc and miktar <= self.bakiye:
            self.bakiye -= miktar
            self.borc -= miktar
            self.islemler.append(Islem("Borç ödeme", -miktar).to_dict())
            return True
        return False

    def to_dict(self):
        return {
            "iban": self.iban,
            "hesap_adi": self.hesap_adi,
            "bakiye": self.bakiye,
            "borc": self.borc,
            "islemler": self.islemler
        }

class Musteri:
    def __init__(self, tc, ad, soyad, sifre, hesaplar=None):
        self.tc = tc
        self.ad = ad
        self.soyad = soyad
        self.sifre = sifre
        self.hesaplar = hesaplar if hesaplar else []

    def add_hesap(self, hesap):
        self.hesaplar.append(hesap)

    def get_hesap_by_iban(self, iban):
        for hesap in self.hesaplar:
            if hesap.iban == iban:
                return hesap
        return None

    def to_dict(self):
        return {
            "tc": self.tc,
            "ad": self.ad,
            "soyad": self.soyad,
            "sifre": self.sifre,
            "hesaplar": [h.to_dict() for h in self.hesaplar]
        }


class Banka:
    def __init__(self, dosya_ad="data.json"):
        self.data_file = dosya_ad
        self.musteriler = []
        self.load()

    def load(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.musteriler = []
            for m in data.get("musteriler", []):
                hesaplar = []
                for h in m.get("hesaplar", []):
                    hesaplar.append(Hesap(
                        h["iban"], h["hesap_adi"], h["bakiye"], h["borc"], h.get("islemler", [])
                    ))
                self.musteriler.append(
                    Musteri(m["tc"], m["ad"], m["soyad"], m["sifre"], hesaplar)
                )
        else:
            self.musteriler = []
    
    def save(self):
        data = {
            "musteriler": [m.to_dict() for m in self.musteriler]
        }
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_musteri(self, tc):
        for m in self.musteriler:
            if m.tc == tc:
                return m
        return None

    def verify_login(self, tc, sifre):
        m = self.get_musteri(tc)
        return bool(m and m.sifre == sifre)

    def add_hesap(self, tc, hesap):
        m = self.get_musteri(tc)
        if m:
            m.add_hesap(hesap)
            self.save()
            return True
        return False

    def get_all_hesaplar(self, tc):
        m = self.get_musteri(tc)
        return [h.to_dict() for h in m.hesaplar] if m else []

    def get_hesap_by_iban(self, tc, iban):
        m = self.get_musteri(tc)
        if m:
            h = m.get_hesap_by_iban(iban)
            return h
        return None

    def update_hesap(self, tc, iban, attr, value):
        h = self.get_hesap_by_iban(tc, iban)
        if h:
            setattr(h, attr, value)
            self.save()
            return True
        return False

    def add_islem(self, tc, iban, aciklama, miktar):
        h = self.get_hesap_by_iban(tc, iban)
        if h:
            h.islemler.append(Islem(aciklama, miktar).to_dict())
            self.save()
            return True
        return False

    def get_islemler(self, tc, iban):
        h = self.get_hesap_by_iban(tc, iban)
        if h:
            return h.islemler
        return []

# Kullanım Örneği:
if __name__ == "__main__":
    banka = Banka()
    # Örnek: Yeni müşteri/hesap ekleme, veri görüntüleme, güncelleme vs.
    print("--- Tüm müşteriler ve hesapları ---")
    for musteri in banka.musteriler:
        print(musteri.tc, musteri.ad, musteri.soyad)
        for h in musteri.hesaplar:
            print("   ", h.iban, h.hesap_adi, h.bakiye, h.borc)
