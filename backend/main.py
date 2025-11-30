import json
import os
from datetime import datetime
from abc import ABC, abstractmethod

# ==========================================
# 1. VERİ MODELLERİ (MODELS)
# Veriler protected/private tutulur, dışarıya kontrollü açılır.
# ==========================================

class Islem:
    def __init__(self, aciklama, miktar):
        # İşlem oluştuktan sonra değiştirilemez, o yüzden private/protected
        self._tarih = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        self._aciklama = aciklama
        self._tutar = miktar

    def to_dict(self):
        """Veriyi dışarıya güvenli bir sözlük olarak verir."""
        return {
            "tarih": self._tarih,
            "aciklama": self._aciklama,
            "tutar": self._tutar
        }

class Hesap:
    def __init__(self, iban, hesap_adi, bakiye=0.0, borc=0.0, islemler=None):
        self._iban = iban            # Protected: Değişmemeli ama okunabilir
        self._hesap_adi = hesap_adi
        self._bakiye = bakiye        # Protected: Sadece servisler değiştirmeli
        self._borc = borc
        self._islemler = islemler if islemler else []

    # --- Property'ler (Read-Only Erişim) ---
    @property
    def iban(self):
        return self._iban

    @property
    def bakiye(self):
        return self._bakiye

    @property
    def borc(self):
        return self._borc

    @property
    def hesap_adi(self):
        return self._hesap_adi

    # --- Yetkili Erişim Metotları ---

    # Bakiye ve Borç set edilmesini sadece servisler yapsın diye
    # setter (@bakiye.setter) yazmıyoruz, serviste _bakiye kullanacağız.

    def islem_ekle(self, islem: Islem):
        """Listeye doğrudan erişimi engellemek için metot kullanıyoruz."""
        self._islemler.append(islem.to_dict())

    def to_dict(self):
        return {
            "iban": self._iban,
            "hesap_adi": self._hesap_adi,
            "bakiye": self._bakiye,
            "borc": self._borc,
            "islemler": self._islemler
        }

class Kisi(ABC):
    def __init__(self, tc, ad, soyad):
        self._tc = tc
        self._ad = ad
        self._soyad = soyad

    @property
    def tc(self): return self._tc

    @property
    def ad(self): return self._ad

    @property
    def soyad(self): return self._soyad

class Musteri(Kisi):
    def __init__(self, tc, ad, soyad, sifre, hesaplar=None):
        super().__init__(tc, ad, soyad)
        self.__sifre = sifre      # Private: Asla dışarı sızmamalı!
        self._hesaplar = hesaplar if hesaplar else [] # Protected

    def sifre_dogrula(self, girilen_sifre):
        """Şifreyi dışarı vermez, sadece doğruluğunu kontrol eder."""
        return self.__sifre == girilen_sifre

    def hesap_bul(self, iban):
        for h in self._hesaplar:
            if h.iban == iban:
                return h
        return None

    def hesap_ekle(self, hesap: Hesap):
        self._hesaplar.append(hesap)

    # Property: Hesapları sadece okumak için dışarı açar
    @property
    def hesaplar(self):
        return self._hesaplar

    def to_dict(self):
        return {
            "tc": self._tc,
            "ad": self._ad,
            "soyad": self._soyad,
            "sifre": self.__sifre, # Kayıt ederken mecburen yazıyoruz
            "hesaplar": [h.to_dict() for h in self._hesaplar]
        }

# ==========================================
# 2. VERİ ERİŞİM (DAL)
# ==========================================

class VeriTabaniArayuzu(ABC):
    @abstractmethod
    def verileri_yukle(self): pass
    @abstractmethod
    def verileri_kaydet(self, veri): pass

class JsonVeriYoneticisi(VeriTabaniArayuzu):
    def __init__(self, dosya_yolu="data.json"):
        self.__dosya_yolu = dosya_yolu # Private: Dışarıdan değiştirilememeli

    def verileri_yukle(self):
        if os.path.exists(self.__dosya_yolu):
            with open(self.__dosya_yolu, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"musteriler": []}

    def verileri_kaydet(self, veri_listesi):
        data = {"musteriler": [m.to_dict() for m in veri_listesi]}
        with open(self.__dosya_yolu, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

# ==========================================
# 3. SERVİSLER (SERVICES)
# Servisler modellerin protected (_) alanlarına erişebilir (Python convention)
# ==========================================

class HesapHizmeti:

    def para_yatir(self, hesap: Hesap, miktar: float):
        if miktar <= 0:
            return False

        # Protected değişkenlere erişim (Module-Level Access)
        hesap._bakiye += miktar
        hesap.islem_ekle(Islem("Para Yatırma", miktar))
        return True

    def para_cek(self, hesap: Hesap, miktar: float):
        if miktar <= 0 or miktar > hesap.bakiye:
            return False

        hesap._bakiye -= miktar
        hesap.islem_ekle(Islem("Para Çekme", -miktar))
        return True

    def borc_ode(self, hesap: Hesap, miktar: float):
        if miktar <= 0 or miktar > hesap.borc or miktar > hesap.bakiye:
            return False

        hesap._bakiye -= miktar
        hesap._borc -= miktar
        hesap.islem_ekle(Islem("Borç Ödeme", -miktar))
        return True

class TransferHizmeti:

    def transfer_yap(self, gonderen: Hesap, alici: Hesap, miktar: float, g_ad, a_ad):
        if miktar <= 0 or gonderen.bakiye < miktar:
            return False

        # Gönderenden düş
        gonderen._bakiye -= miktar
        gonderen.islem_ekle(Islem(f"Transfer: {a_ad}", -miktar))

        # Alıcıya ekle
        alici._bakiye += miktar
        alici.islem_ekle(Islem(f"Transfer Alınan: {g_ad}", miktar))
        return True

class AuthHizmeti:
    def giris_yap(self, musteriler, tc, sifre):
        for m in musteriler:
            # Şifreye doğrudan erişmek yerine doğrulama metodunu kullanıyoruz
            if m.tc == tc and m.sifre_dogrula(sifre):
                return m
        return None

# ==========================================
# 4. FACADE (SİSTEM YÖNETİCİSİ)
# ==========================================

class BankaSistemi:
    def __init__(self):
        # Alt bileşenler private tutulmalı, dışarıdan kurcalanmamalı
        self.__db = JsonVeriYoneticisi()
        self.__hesap_servisi = HesapHizmeti()
        self.__transfer_servisi = TransferHizmeti()
        self.__auth_servisi = AuthHizmeti()
        self._musteriler = [] # Protected
        self.__verileri_yukle() # Private metod

    def __verileri_yukle(self):
        """Sadece sınıf ilk açıldığında çalışır, dışarıdan çağrılamaz."""
        raw_data = self.__db.verileri_yukle()
        self._musteriler = []
        for m_data in raw_data.get("musteriler", []):
            hesap_nesneleri = []
            for h_data in m_data.get("hesaplar", []):
                h = Hesap(h_data["iban"], h_data["hesap_adi"], h_data["bakiye"], h_data["borc"], h_data.get("islemler"))
                hesap_nesneleri.append(h)

            musteri = Musteri(m_data["tc"], m_data["ad"], m_data["soyad"], m_data["sifre"], hesap_nesneleri)
            self._musteriler.append(musteri)

    def kaydet(self):
        self.__db.verileri_kaydet(self._musteriler)

    def musteri_bul(self, tc):
        for m in self._musteriler:
            if m.tc == tc: return m
        return None

    # --- Public API Metotları ---

    # Servisler private olduğu için property ile dışarıya sadece okunabilir referans verebiliriz
    # veya wrapper metot yazarız (Tercih edilen: Wrapper).

    @property
    def hesap_servisi(self):
        return self.__hesap_servisi

    def giris(self, tc, sifre):
        return self.__auth_servisi.giris_yap(self._musteriler, tc, sifre)

    def islem_para_yatir(self, tc, iban, miktar):
        m = self.musteri_bul(tc)
        if m:
            h = m.hesap_bul(iban)
            if h and self.__hesap_servisi.para_yatir(h, miktar):
                self.kaydet()
                return True
        return False

    def islem_para_cek(self, tc, iban, miktar):
        m = self.musteri_bul(tc)
        if m:
            h = m.hesap_bul(iban)
            if h and self.__hesap_servisi.para_cek(h, miktar):
                self.kaydet()
                return True
        return False

    def islem_transfer(self, g_tc, g_iban, a_tc, a_iban, miktar):
        g_mus = self.musteri_bul(g_tc)
        a_mus = self.musteri_bul(a_tc)

        if g_mus and a_mus:
            g_hesap = g_mus.hesap_bul(g_iban)
            a_hesap = a_mus.hesap_bul(a_iban)

            if g_hesap and a_hesap:
                if self.__transfer_servisi.transfer_yap(g_hesap, a_hesap, miktar, g_mus.ad, a_mus.ad):
                    self.kaydet()
                    return True
        return False
