import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Sayfa ayarları (ikon dosyası varsa static/icon.png)
st.set_page_config(
    page_title="Vergi Hesaplayıcı",
    page_icon="static/icon.png",
    layout="centered"
)

st.title("📦 Şahıs Firması Vergi Hesaplayıcı (2025)")

# Girdi alanları
gelir = st.number_input("KDV Dahil Toplam Gelir (₺)", min_value=0.0, step=100.0)
gider = st.number_input("Toplam Gider (₺)", min_value=0.0, step=100.0)
kdv_orani = st.slider("KDV Oranı (%)", min_value=1, max_value=20, value=20)

if gelir > 0:
    # KDV ayrıştırma
    kdv_tutari = gelir * kdv_orani / (100 + kdv_orani)
    net_gelir = gelir - kdv_tutari
    net_kazanc = net_gelir - gider

    st.subheader("📊 Hesaplama Sonuçları")
    st.write(f"**KDV Tutarı:** ₺{kdv_tutari:,.2f}")
    st.write(f"**Net Gelir (KDV Hariç):** ₺{net_gelir:,.2f}")
    st.write(f"**Net Kazanç:** ₺{net_kazanc:,.2f}")

    # Geçici vergi (3 ayda bir)
    gecici_vergi_orani = 0.15
    gecici_vergi_toplam = net_kazanc * gecici_vergi_orani
    gecici_vergi_taksit = gecici_vergi_toplam / 4

    # Yıllık gelir vergisi (kademeli)
    def gelir_vergisi_hesapla(kazanc):
        kalan = kazanc
        vergi = 0
        dilimler = [
            (110000, 0.15),
            (230000, 0.20),
            (870000, 0.27),
            (3000000, 0.35),
            (float("inf"), 0.40)
        ]
        onceki_limit = 0
        for limit, oran in dilimler:
            fark = min(kalan, limit - onceki_limit)
            vergi += fark * oran
            kalan -= fark
            onceki_limit = limit
            if kalan <= 0:
                break
        return vergi

    gelir_vergisi = gelir_vergisi_hesapla(net_kazanc)
    mahsup = gecici_vergi_toplam
    kalan_vergi = max(gelir_vergisi - mahsup, 0)
    taksit = kalan_vergi / 2

    st.write(f"**Yıllık Gelir Vergisi:** ₺{gelir_vergisi:,.2f}")
    st.write(f"**Mahsup Edilen Geçici Vergi:** ₺{mahsup:,.2f}")
    st.write(f"**Kalan Vergi:** ₺{kalan_vergi:,.2f}")
    st.write(f"**2 Taksit (Haziran-Aralık):** ₺{taksit:,.2f} x2")

    # Grafik
    fig, ax = plt.subplots()
    labels = ['Gider', 'KDV', 'Vergi', 'Net']
    values = [gider, kdv_tutari, gelir_vergisi, net_kazanc - gelir_vergisi]
    ax.bar(labels, values, color=['gray', 'orange', 'red', 'green'])
    ax.set_ylabel("₺")
    ax.set_title("Kazanç Dağılımı")
    st.pyplot(fig)

    # Tablo
    st.subheader("📅 Dönemsel Özet")
    df = pd.DataFrame({
        "Dönem": ["1. Geçici", "2. Geçici", "3. Geçici", "4. Geçici"],
        "Gelir": [gelir/4]*4,
        "Gider": [gider/4]*4,
        "Vergi": [gecici_vergi_taksit]*4
    })
    st.dataframe(df.style.format({"Gelir": "₺{:.2f}", "Gider": "₺{:.2f}", "Vergi": "₺{:.2f}"}))
