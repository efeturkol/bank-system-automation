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
    def __init__(self, iban, hesap_adi, musteri, bakiye=0.0, borc=0.0, islemler=None):
        self.iban = iban
        self.hesap_adi = hesap_adi
        self.musteri = musteri
        self.bakiye = bakiye
        self.borc = borc
        self.islemler = islemler if islemler else []

    def para_yatir(self, miktar):
        if miktar > 0:
            self.bakiye += miktar
            self.islemler.append(Islem("Para yatırma", miktar).to_dict())
            print(f"{miktar}₺ yatırıldı. Yeni bakiye: {self.bakiye}₺")
            return True
        else:
            print("Geçersiz işlem! Lütfen geçerli bir değer giriniz.")
            return False

    def para_cek(self, miktar):
        if miktar <= 0:
            print("Geçersiz işlem! Lütfen geçerli bir değer giriniz.")
            return False
        elif miktar > self.bakiye:
            print("Yetersiz bakiye!")
            return False
        else:
            self.bakiye -= miktar
            self.islemler.append(Islem("Para çekme", -miktar).to_dict())
            print(f"{miktar}₺ çekildi. Kalan bakiye: {self.bakiye}₺")
            return True

    def borc_ode(self, miktar):
        if miktar <= 0:
            print("Geçersiz miktar!")
            return False
        elif miktar > self.borc:
            print("Borç miktarından fazla ödeme yapılamaz.")
            return False
        elif miktar > self.bakiye:
            print("Yetersiz bakiye!")
            return False
        else:
            self.bakiye -= miktar
            self.borc -= miktar
            self.islemler.append(Islem("Borç ödeme", -miktar).to_dict())
            print(f"{miktar}₺ borç ödendi. Kalan borç: {self.borc}₺")
            return True

    def transfer_yap(self, farkli_hesap, miktar):
        if miktar <= 0:
            print("Geçersiz miktar!")
            return False
        elif miktar > self.bakiye:
            print("Yetersiz bakiye!")
            return False
        else:
            self.bakiye -= miktar
            farkli_hesap.bakiye += miktar
            self.islemler.append(Islem(f"{farkli_hesap.musteri.ad} adlı kişiye transfer", -miktar).to_dict())
            farkli_hesap.islemler.append(Islem(f"{self.musteri.ad} adlı kişiden transfer", miktar).to_dict())
            print(f"{farkli_hesap.musteri.ad} adlı kişiye {miktar}₺ gönderildi.")
            return True

    def bilgi_goster(self):
        print(f"\n--- {self.musteri.ad} {self.musteri.soyad} ---")
        print(f"TC: {self.musteri.tc}")
        print(f"Bakiye: {self.bakiye}₺")
        print(f"Borç: {self.borc}₺")
        print("İşlem Geçmişi:")
        for islem in self.islemler:
            print(" ", islem)
        print("-----------------------------\n")

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
                musteri_obj = Musteri(m["tc"], m["ad"], m["soyad"], m["sifre"])
                hesaplar = []
                for h in m.get("hesaplar", []):
                    hesaplar.append(Hesap(
                        h["iban"], h["hesap_adi"], musteri_obj, h["bakiye"], h["borc"], h.get("islemler", [])
                    ))
                musteri_obj.hesaplar = hesaplar
                self.musteriler.append(musteri_obj)
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
            for mm in self.musteriler:
                for hh in mm.hesaplar:
                    if hh.iban == hesap.iban:
                        return False
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
            if attr in {"bakiye", "borc", "hesap_adi"}:
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

    def para_yatir(self, tc, iban, miktar):
        h = self.get_hesap_by_iban(tc, iban)
        if h and h.para_yatir(miktar):
            self.save()
            return True
        return False

    def para_cek(self, tc, iban, miktar):
        h = self.get_hesap_by_iban(tc, iban)
        if h and h.para_cek(miktar):
            self.save()
            return True
        return False

    def borc_ode(self, tc, iban, miktar):
        h = self.get_hesap_by_iban(tc, iban)
        if h and h.borc_ode(miktar):
            self.save()
            return True
        return False

    def transfer(self, gonderen_tc, gonderen_iban, alici_tc, alici_iban, miktar):
        g = self.get_hesap_by_iban(gonderen_tc, gonderen_iban)
        a = self.get_hesap_by_iban(alici_tc, alici_iban)
        if not g or not a:
            return False
        if not g.transfer_yap(a, miktar):
            return False
        self.save()
        return True

if __name__ == "__main__":
    banka = Banka()
    print("--- Tüm müşteriler ve hesapları ---")
    for musteri in banka.musteriler:
        print(musteri.tc, musteri.ad, musteri.soyad)
        for h in musteri.hesaplar:
            print("   ", h.iban, h.hesap_adi, h.bakiye, h.borc)
