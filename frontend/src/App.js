import React, { useState } from "react";
import axios from "axios";

function App() {
  const [tc, setTc] = useState("");
  const [sifre, setSifre] = useState("");
  const [giris, setGiris] = useState(false);
  const [musteri, setMusteri] = useState({});
  const [hesaplar, setHesaplar] = useState([]);
  const [seciliIban, setSeciliIban] = useState("");
  const [hesapDetay, setHesapDetay] = useState(null);
  const [miktar, setMiktar] = useState("");
  const [mesaj, setMesaj] = useState("");
  const [islemler, setIslemler] = useState([]);

  // Giriş işlemi
  const login = async () => {
    try {
      const res = await axios.post("/login", { tc, sifre });
      if (res.data.success) {
        setGiris(true);
        setMusteri(res.data.musteri);
        fetchHesaplar(res.data.musteri.tc);
        setMesaj("");
      } else {
        setMesaj(res.data.message);
      }
    } catch (err) {
      setMesaj("Sunucu hatası veya bağlantı yok!");
    }
  };

  // Hesapları getir
  const fetchHesaplar = async (gelenTc) => {
    try {
      const res = await axios.get(`/hesaplar/${gelenTc}`);
      if (res.data.success) {
        setHesaplar(res.data.hesaplar);
      }
    } catch (err) {
      setMesaj("Hesaplar yüklenemedi.");
    }
  };

  // Hesap detay ve işlemleri
  const selectHesap = async (iban) => {
    setSeciliIban(iban);
    setMesaj("Yükleniyor...");
    try {
      const res = await axios.get(`/hesap/${tc}/${iban}`);
      if (res.data.success) setHesapDetay(res.data.hesap);

      const res2 = await axios.get(`/islemler/${tc}/${iban}`);
      if (res2.data.success) setIslemler(res2.data.islemler);

      setMesaj("");
    } catch (err) {
      setMesaj("Hesap detayları veya işlemler yüklenemedi.");
    }
  };

  // Para Yatır
  const paraYatir = async () => {
    if (!miktar || isNaN(miktar) || Number(miktar) <= 0) {
      setMesaj("Lütfen geçerli bir miktar giriniz!");
      return;
    }
    try {
      const res = await axios.post("/yatir", {
        tc,
        iban: seciliIban,
        miktar: parseFloat(miktar)
      });
      setMesaj(res.data.message);
      selectHesap(seciliIban);
      setMiktar("");
    } catch (err) {
      setMesaj(err.response?.data?.message || "Para yatırılırken hata oluştu!");
    }
  };

  // Para Çek
  const paraCek = async () => {
    if (!miktar || isNaN(miktar) || Number(miktar) <= 0) {
      setMesaj("Lütfen geçerli bir miktar giriniz!");
      return;
    }
    try {
      const res = await axios.post("/cek", {
        tc,
        iban: seciliIban,
        miktar: parseFloat(miktar)
      });
      setMesaj(res.data.message);
      selectHesap(seciliIban);
      setMiktar("");
    } catch (err) {
      setMesaj(err.response?.data?.message || "Para çekilirken hata oluştu!");
    }
  };

  // Borç Öde
  const borcOde = async () => {
    if (!miktar || isNaN(miktar) || Number(miktar) <= 0) {
      setMesaj("Lütfen geçerli bir miktar giriniz!");
      return;
    }
    try {
      const res = await axios.post("/borc-ode", {
        tc,
        iban: seciliIban,
        miktar: parseFloat(miktar)
      });
      setMesaj(res.data.message);
      selectHesap(seciliIban);
      setMiktar("");
    } catch (err) {
      setMesaj(err.response?.data?.message || "Borç ödenirken hata oluştu!");
    }
  };

  // Giriş sayfası
  if (!giris) {
    return (
      <div style={{ maxWidth: 400, margin: "80px auto", textAlign: "center" }}>
        <h2>Banka Sistemi | Giriş</h2>
        <input
          type="text"
          placeholder="TC Kimlik No"
          value={tc}
          onChange={(e) => setTc(e.target.value)}
          style={{ width: "90%", padding: "10px", margin: "12px" }}
        />
        <input
          type="password"
          placeholder="Şifre"
          value={sifre}
          onChange={(e) => setSifre(e.target.value)}
          style={{ width: "90%", padding: "10px", margin: "12px" }}
        />
        <button onClick={login} style={{ padding: "10px 30px" }}>
          Giriş Yap
        </button>
        {mesaj && <p style={{ marginTop: "16px", color: "#b00" }}>{mesaj}</p>}
      </div>
    );
  }

  // Vadeli/Vadesiz kontrolü -> vadeli hesapta borç yok
  const isVadesiz = hesapDetay && hesapDetay.hesap_adi?.toLowerCase().includes("vadesiz");

  return (
    <div style={{ maxWidth: 700, margin: "60px auto", padding: "32px", background: "white", borderRadius: 16 }}>
      <h2>Hoş geldin, {musteri.ad} {musteri.soyad}</h2>
      <h4>Hesaplarını Seç:</h4>
      <div style={{ display: "flex", gap: "16px", marginBottom: "24px", flexWrap: "wrap" }}>
        {hesaplar.map((h) => (
          <button
            key={h.iban}
            onClick={() => selectHesap(h.iban)}
            style={{
              padding: "18px 24px",
              minWidth: "150px",
              borderRadius: "8px",
              background: seciliIban === h.iban ? "#9060f7" : "#eee",
              color: seciliIban === h.iban ? "white" : "#333",
              border: seciliIban === h.iban ? "2px solid #9060f7" : "1px solid #888",
              fontWeight: "bold",
              fontSize: 16
            }}
          >
            {h.hesap_adi} <br />
            <span style={{ fontSize: 12, color: "#333" }}>{h.iban}</span>
          </button>
        ))}
      </div>

      {hesapDetay && (
        <>
          <div style={{ marginBottom: 24, background: "#f9f9ff", padding: 20, borderRadius: 12 }}>
            <h3 style={{ margin: 0, color: "#1a2257" }}>
              {hesapDetay.hesap_adi} ({hesapDetay.iban})
            </h3>
            <p>
              <strong>Bakiye:</strong> {hesapDetay.bakiye}₺
              {isVadesiz && (
                <>
                  &nbsp; |&nbsp; <strong>Borç:</strong> {hesapDetay.borc}₺
                </>
              )}
            </p>
          </div>

          <div style={{ display: "flex", alignItems: "center", marginBottom: "22px", gap: "16px" }}>
            <input
              type="number"
              placeholder="Miktar"
              value={miktar}
              onChange={(e) => setMiktar(e.target.value)}
              style={{ width: 120, padding: "10px", borderRadius: 6, border: "1px solid #bbb" }}
            />
            <button
              onClick={paraYatir}
              style={{ padding: "10px", background: "#2fd643", color: "white", border: "none", borderRadius: 6 }}
            >Para Yatır</button>
            <button
              onClick={paraCek}
              style={{ padding: "10px", background: "#ff3b3f", color: "white", border: "none", borderRadius: 6 }}
            >Para Çek</button>
            {isVadesiz && (
              <button
                onClick={borcOde}
                style={{ padding: "10px", background: "#ffd700", color: "#333", border: "none", borderRadius: 6 }}
              >Borç Öde</button>
            )}
          </div>

          {mesaj && (
            <div style={{ marginBottom: 16, padding: 10, color: "#014421", background: "#e6ffe6", borderRadius: 7, border: "1px solid #bdd4bc" }}>
              {mesaj}
            </div>
          )}

          <div>
            <h4>Son İşlemler</h4>
            <table style={{ width: "100%", background: "#fafae7", borderRadius: 8 }}>
              <thead>
                <tr style={{ background: "#e0e0e7" }}>
                  <th style={{ padding: "8px" }}>Tarih</th>
                  <th style={{ padding: "8px" }}>Açıklama</th>
                  <th style={{ padding: "8px" }}>Tutar</th>
                </tr>
              </thead>
              <tbody>
                {islemler.length === 0 && (
                  <tr>
                    <td colSpan={3} style={{ padding: "12px", textAlign: "center" }}>Henüz işlem yok.</td>
                  </tr>
                )}
                {islemler.slice(-5).reverse().map((islem, i) => (
                  <tr key={i}>
                    <td style={{ padding: "6px" }}>{islem.tarih}</td>
                    <td style={{ padding: "6px" }}>{islem.aciklama}</td>
                    <td style={{ padding: "6px" }}>{islem.tutar}₺</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}

export default App;
