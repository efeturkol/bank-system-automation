from flask import Flask, jsonify, request
from flask_cors import CORS
import main as data_manager

app = Flask(__name__)
CORS(app)

@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        tc = data.get("tc")
        sifre = data.get("sifre")
        if data_manager.verify_login(tc, sifre):
            musteri = data_manager.get_musteri_by_tc(tc)
            return jsonify({
                "success": True,
                "message": "Giriş başarılı",
                "musteri": {
                    "tc": musteri["tc"],
                    "ad": musteri["ad"],
                    "soyad": musteri["soyad"]
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
        hesaplar = data_manager.get_all_hesaplar(tc)
        if hesaplar:
            return jsonify({
                "success": True,
                "hesaplar": [
                    {
                        "iban": h["iban"],
                        "hesap_adi": h["hesap_adi"],
                        "bakiye": h["bakiye"],
                        "borc": h["borc"]
                    } for h in hesaplar
                ]
            })
        return jsonify({"success": False, "message": "Hesap bulunamadı"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/hesap/<tc>/<iban>", methods=["GET"])
def hesap_detay(tc, iban):
    try:
        hesap = data_manager.get_hesap_by_iban(tc, iban)
        if hesap:
            return jsonify({
                "success": True,
                "hesap": {
                    "iban": hesap["iban"],
                    "hesap_adi": hesap["hesap_adi"],
                    "bakiye": hesap["bakiye"],
                    "borc": hesap["borc"]
                }
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
        if miktar <= 0:
            return jsonify({"success": False, "message": "Geçersiz miktar!"}), 400
        hesap = data_manager.get_hesap_by_iban(tc, iban)
        if not hesap:
            return jsonify({"success": False, "message": "Hesap bulunamadı!"}), 404
        yeni_bakiye = hesap["bakiye"] + miktar
        data_manager.update_bakiye(tc, iban, yeni_bakiye)
        data_manager.add_islem(tc, iban, "Para yatırma", miktar)
        return jsonify({"success": True, "message": f"{miktar}₺ yatırıldı", "bakiye": yeni_bakiye})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/cek", methods=["POST"])
def cek():
    try:
        data = request.get_json()
        tc = data.get("tc")
        iban = data.get("iban")
        miktar = float(data.get("miktar", 0))
        hesap = data_manager.get_hesap_by_iban(tc, iban)
        if not hesap:
            return jsonify({"success": False, "message": "Hesap bulunamadı!"}), 404
        if miktar <= 0:
            return jsonify({"success": False, "message": "Geçersiz miktar!"}), 400
        if miktar > hesap["bakiye"]:
            return jsonify({"success": False, "message": "Yetersiz bakiye!"}), 400
        yeni_bakiye = hesap["bakiye"] - miktar
        data_manager.update_bakiye(tc, iban, yeni_bakiye)
        data_manager.add_islem(tc, iban, "Para çekme", -miktar)
        return jsonify({"success": True, "message": f"{miktar}₺ çekildi", "bakiye": yeni_bakiye})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/borc-ode", methods=["POST"])
def borc_ode():
    try:
        data = request.get_json()
        tc = data.get("tc")
        iban = data.get("iban")
        miktar = float(data.get("miktar", 0))
        hesap = data_manager.get_hesap_by_iban(tc, iban)
        if not hesap:
            return jsonify({"success": False, "message": "Hesap bulunamadı!"}), 404
        if miktar <= 0 or miktar > hesap["borc"] or miktar > hesap["bakiye"]:
            return jsonify({"success": False, "message": "Geçersiz borç ödeme!"}), 400
        yeni_bakiye = hesap["bakiye"] - miktar
        yeni_borc = hesap["borc"] - miktar
        data_manager.update_bakiye(tc, iban, yeni_bakiye)
        data_manager.update_borc(tc, iban, yeni_borc)
        data_manager.add_islem(tc, iban, "Borç ödeme", -miktar)
        return jsonify({"success": True, "message": f"{miktar}₺ borç ödendi", "bakiye": yeni_bakiye, "borc": yeni_borc})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/islemler/<tc>/<iban>", methods=["GET"])
def islemler(tc, iban):
    try:
        islem_listesi = data_manager.get_islemler(tc, iban)
        return jsonify({"success": True, "islemler": islem_listesi})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/hesap-ekle", methods=["POST"])
def hesap_ekle():
    try:
        data = request.get_json()
        tc = data.get("tc")
        yeni_hesap = {
            "iban": data.get("iban"),
            "hesap_adi": data.get("hesap_adi"),
            "bakiye": float(data.get("bakiye", 0)),
            "borc": float(data.get("borc", 0)),
            "islemler": []
        }
        ok = data_manager.add_hesap(tc, yeni_hesap)
        if ok:
            return jsonify({"success": True, "message": "Hesap eklendi!"})
        return jsonify({"success": False, "message": "Müşteri bulunamadı."}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)
