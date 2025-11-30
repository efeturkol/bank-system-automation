from flask import Flask, jsonify, request
from flask_cors import CORS

# main.py dosyasından BankaSistemi ve Hesap sınıflarını dahil ediyoruz
# (Dosya adının main.py olduğunu varsayıyorum)
from main import BankaSistemi, Hesap

app = Flask(__name__)
CORS(app)

# Sistemi başlat (Veritabanını otomatik yükler)
banka = BankaSistemi()

@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        tc = data.get("tc")
        sifre = data.get("sifre")

        # Facade üzerinden giriş yapıyoruz (Private şifreye dokunmuyoruz)
        musteri = banka.giris(tc, sifre)

        if musteri:
            return jsonify({
                "success": True,
                "message": "Giriş başarılı",
                "musteri": {
                    "tc": musteri.tc,
                    "ad": musteri.ad,
                    "soyad": musteri.soyad
                }
            })
        else:
            return jsonify({
                "success": False,
                "message": "Geçersiz TC veya şifre"
            }), 401
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/hesaplar/<tc>", methods=["GET"])
def hesaplar(tc):
    try:
        musteri = banka.musteri_bul(tc)
        if musteri:
            # Musteri içindeki 'hesaplar' property'sini kullanıyoruz
            # Her hesap nesnesinin kendi 'to_dict' metodunu çağırıyoruz
            return jsonify({
                "success": True,
                "hesaplar": [h.to_dict() for h in musteri.hesaplar]
            })
        return jsonify({"success": False, "message": "Müşteri bulunamadı"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/hesap/<tc>/<iban>", methods=["GET"])
def hesap_detay(tc, iban):
    try:
        musteri = banka.musteri_bul(tc)
        if musteri:
            hesap = musteri.hesap_bul(iban)
            if hesap:
                return jsonify({
                    "success": True,
                    "hesap": hesap.to_dict()
                })
        return jsonify({"success": False, "message": "Hesap bulunamadı"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/yatir", methods=["POST"])
def yatir():
    try:
        data = request.get_json()
        tc = data.get("tc")
        iban = data.get("iban")
        miktar = float(data.get("miktar", 0))

        # BankaSistemi (Facade) üzerindeki metodu kullanıyoruz
        # Bu metot arka planda kaydetme işlemini de yapıyor
        if banka.islem_para_yatir(tc, iban, miktar):
            # Güncel bakiyeyi döndürmek için hesabı tekrar çekiyoruz
            hesap = banka.musteri_bul(tc).hesap_bul(iban)
            return jsonify({
                "success": True,
                "message": f"{miktar}₺ yatırıldı",
                "bakiye": hesap.bakiye
            })

        return jsonify({"success": False, "message": "İşlem başarısız (Müşteri yok veya miktar hatalı)"}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/cek", methods=["POST"])
def cek():
    try:
        data = request.get_json()
        tc = data.get("tc")
        iban = data.get("iban")
        miktar = float(data.get("miktar", 0))

        if banka.islem_para_cek(tc, iban, miktar):
            hesap = banka.musteri_bul(tc).hesap_bul(iban)
            return jsonify({
                "success": True,
                "message": f"{miktar}₺ çekildi",
                "bakiye": hesap.bakiye
            })

        return jsonify({"success": False, "message": "Yetersiz bakiye veya hatalı işlem"}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/borc-ode", methods=["POST"])
def borc_ode():
    try:
        data = request.get_json()
        tc = data.get("tc")
        iban = data.get("iban")
        miktar = float(data.get("miktar", 0))

        # Borç ödeme için ana sınıfımızda bir wrapper yoktu,
        # ancak 'hesap_servisi' property'si üzerinden servise ulaşabiliriz.
        musteri = banka.musteri_bul(tc)
        if musteri:
            hesap = musteri.hesap_bul(iban)
            if hesap:
                # Servis üzerinden işlem yap
                if banka.hesap_servisi.borc_ode(hesap, miktar):
                    banka.kaydet() # Değişikliği manuel kaydediyoruz
                    return jsonify({
                        "success": True,
                        "message": f"{miktar}₺ borç ödendi",
                        "bakiye": hesap.bakiye,
                        "borc": hesap.borc
                    })

        return jsonify({"success": False, "message": "Borç ödeme başarısız"}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/islemler/<tc>/<iban>", methods=["GET"])
def islemler(tc, iban):
    try:
        musteri = banka.musteri_bul(tc)
        if musteri:
            hesap = musteri.hesap_bul(iban)
            if hesap:
                # Hesap nesnesinin to_dict çıktısındaki islemler listesini alıyoruz
                return jsonify({"success": True, "islemler": hesap.to_dict()["islemler"]})

        return jsonify({"success": False, "message": "Hesap bulunamadı"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/hesap-ekle", methods=["POST"])
def hesap_ekle():
    try:
        data = request.get_json()
        tc = data.get("tc")

        musteri = banka.musteri_bul(tc)
        if not musteri:
            return jsonify({"success": False, "message": "Müşteri bulunamadı."}), 404

        # Yeni Hesap Nesnesi Oluşturuyoruz (Modeli Kullanarak)
        yeni_hesap = Hesap(
            iban=data.get("iban"),
            hesap_adi=data.get("hesap_adi"),
            bakiye=float(data.get("bakiye", 0)),
            borc=float(data.get("borc", 0))
        )

        # Nesneyi müşteriye ekliyoruz
        musteri.hesap_ekle(yeni_hesap)
        banka.kaydet()

        return jsonify({"success": True, "message": "Hesap başarıyla eklendi!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)
