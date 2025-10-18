import json
from datetime import datetime


class Musteri:
    def __init__(self,ad,soyad,tc,sifre):
        self.ad = ad
        self.soyad = soyad
        self.__tc = tc
        self.__sifre = sifre
        

class Hesap:
    def __init__(self,iban,musteri,bakiye=0.0,borc=0.0):
        self.iban = iban
        self.musteri = musteri
        self.bakiye = bakiye
        self.borc = borc
        self.islem = []

    def para_yatir(self,miktar):
        if miktar > 0:
            self.bakiye += miktar 
            self.islem.append(f"Para yatırma işlemi: {miktar}₺ | Güncel bakiye: {self.bakiye}₺")
            print(f"{miktar}₺ yatırıldı. Yeni bakiye: {self.bakiye}₺")
        else:
            print("Geçersiz işlem! Lütfen geçerli bir değer giriniz.")
    
    def para_cekme(self,miktar):
        if miktar <= 0:
            print("Geçersiz işlem! Lütfen geçerli bir değer giriniz. ")
        elif miktar > self.bakiye:
            print("Yetersiz bakiye!")
        else:
            self.bakiye -= miktar
            self.islem.append(IslemKaydi("Para çekme",-miktar))
            print(f"{miktar}₺ çekildi. Kalan bakiye: {self.bakiye}₺")

    def borc_yatirma(self,miktar):
        if miktar <= 0:
            print("Geçersiz miktar!")
        elif miktar > self.borc:
            print("Borç miktarından fazla ödeme yapılamaz.")
        elif miktar > self.bakiye:
            print("Yetersiz bakiye!")
        else:
            self.bakiye -= miktar
            self.borc -= miktar
            self.islem.append(IslemKaydi("Borç Ödeme: ", -miktar))
            print(f"{miktar}₺ borç ödendi. Kalan borç: {self.borc}₺")
    
    def transfer_yap(self,farkli_musteri,miktar):
        if miktar <= 0:
            print("Geçersiz miktar!")
        elif miktar > self.bakiye:
            print("Yetersiz bakiye!")
        else:
            self.bakiye -= miktar 
            farkli_musteri.bakiye += miktar
            self.islem.append(IslemKaydi(f"{farkli_musteri.musteri.ad} adlı kişiye transfer", -miktar))
            farkli_musteri.islem.append(IslemKaydi(f"{self.ad} adlı kişiden transfer", miktar))
            print(f"{farkli_musteri.ad} adlı kişiye {miktar}₺ gönderildi.")

    def bilgi_goster(self):
        print(f"\n--- {self.musteri.ad} {self.musteri.soyad} ---")
        print(f"TC: {self.musteri._Musteri__tc}")
        print(f"Bakiye: {self.bakiye}₺")
        print(f"Borç: {self.borc}₺")
        print("İşlem Geçmişi:")
        for islem in self.islem:
            print(" ", islem)
        print("-----------------------------\n")

            

class Banka:
    def __init__(self,ad,**musteriler):
        self.ad = ad
        self.musteriler = musteriler 


class IslemKaydi:
    def __init__(self,aciklama,miktar):
        self.aciklama = aciklama
        self.tutar = miktar 





    

