import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(
    page_title="Vergi Hesaplayıcı",
    page_icon="static/icon.png",
    layout="wide"
)

# Ekran genişliğini al via JS
width = streamlit_js_eval(js_expressions='screen.width', key="SCR_WIDTH")
# Eğer None gelirse, varsayılan bir değer ata
if width is None:
    width = 1000

# Mobil kontrolü
is_mobile = width < 600

# İkon kontrolü
if not os.path.exists("static/icon.png"):
    st.warning("⚠️ İkon dosyası bulunamadı. Lütfen 'static/icon.png' dosyasını yükleyin.")

st.title("📦 Şahıs Firması Vergi Hesaplayıcı (2025)")
st.markdown("KDV dahil gelir girerek 3 aylık geçici vergi, yıllık gelir vergisi ve mahsup sonrası kalan tutarı hesaplayın.")

# Girdi alanları
gelir_brut = st.number_input("Aylık Gelir (KDV Dahil) (₺)", min_value=0.0)
gider = st.number_input("Aylık Gider (₺)", min_value=0.0)
kdv_orani = st.selectbox("KDV Oranı", [0.01, 0.10, 0.20], index=2)

# Hesaplamalar
gelir_kdv_haric = gelir_brut / (1 + kdv_orani)
kdv = gelir_brut - gelir_kdv_haric
net_kazanc = gelir_kdv_haric - gider

def kademeli_gelir_vergisi(matrah):
    vergi = 0
    dilimler = [
        (0, 110000, 0.15),
        (110000, 230000, 0.20),
        (230000, 870000, 0.27),
        (870000, 3000000, 0.35),
        (3000000, float('inf'), 0.40)
    ]
    for alt, ust, oran in dilimler:
        if matrah > alt:
            vergilendirilen = min(matrah, ust) - alt
            vergi += vergilendirilen * oran
    return vergi

gecici_matrah = net_kazanc * 3
gecici_vergi = kademeli_gelir_vergisi(gecici_matrah)
yillik_matrah = net_kazanc * 12
yillik_vergi = kademeli_gelir_vergisi(yillik_matrah)
gecici_vergi_toplam = gecici_vergi * 4
kalan_vergi = max(yillik_vergi - gecici_vergi_toplam, 0)
taksit_sayisi = 2
taksit_tutari = kalan_vergi / taksit_sayisi if taksit_sayisi != 0 else 0

# Sonuçları göster
st.subheader("📊 Hesaplama Sonuçları")

if is_mobile:
    # Mobil görünüm — sade stil
    st.write(f"KDV Hariç Gelir: ₺{gelir_kdv_haric:,.2f}")
    st.write(f"KDV Tutarı ({kdv_orani*100:.0f}%): ₺{kdv:,.2f}")
    st.write(f"Net Kazanç (Aylık): ₺{net_kazanc:,.2f}")
    st.write(f"Geçici Vergi (3 Aylık): ₺{gecici_vergi:,.2f}")
    st.write(f"Yıllık Vergi (12 Ay): ₺{yillik_vergi:,.2f}")
else:
    # Masaüstü stil
    st.write(f"**KDV Hariç Gelir:** ₺{gelir_kdv_haric:,.2f}")
    st.write(f"**KDV Tutarı ({kdv_orani*100:.0f}%):** ₺{kdv:,.2f}")
    st.write(f"**Net Kazanç (Aylık):** ₺{net_kazanc:,.2f}")
    st.write(f"**Geçici Vergi (3 Aylık):** ₺{gecici_vergi:,.2f}")
    st.write(f"**Yıllık Vergi (12 Ay):** ₺{yillik_vergi:,.2f}")

# Mahsup & taksit planı
st.subheader("📆 Yıl Sonu Mahsup ve Taksit Planı")
st.write(f"**Ödenmiş Geçici Vergi (Yıl Boyunca):** ₺{gecici_vergi_toplam:,.2f}")
st.write(f"**Mahsup Sonrası Kalan Tutar:** ₺{kalan_vergi:,.2f}")

if kalan_vergi > 0:
    st.write(f"**1. Taksit (Mart):** ₺{taksit_tutari:,.2f}")
    st.write(f"**2. Taksit (Temmuz):** ₺{taksit_tutari:,.2f}")
else:
    st.success("Yıl boyunca ödediğiniz geçici vergiler, yıllık vergiyi tamamen karşılıyor. Ek ödeme yok.")

# Grafik
if gelir_brut > 0:
    st.subheader("📈 3 Aylık Dağılım Grafiği")
    labels = ['Gider (3 Ay)', 'KDV (3 Ay)', 'Geçici Vergi']
    values = [gider * 3, kdv * 3, gecici_vergi]
    if is_mobile:
        fig, ax = plt.subplots(figsize=(3, 3))
    else:
        fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    st.pyplot(fig)

# Tablo
st.subheader("📅 Dönemsel Kayıt (Örnek)")
veri = {
    "Dönem": ["Ocak–Mart", "Nisan–Haziran", "Temmuz–Eylül", "Ekim–Aralık"],
    "Gelir (KDV Dahil)": [gelir_brut * 3] * 4,
    "Gider": [gider * 3] * 4,
    "Net Kazanç": [net_kazanc * 3] * 4,
    "KDV": [kdv * 3] * 4,
    "Geçici Vergi": [gecici_vergi] * 4
}
df = pd.DataFrame(veri)
st.dataframe(df)

st.markdown("---")
st.caption("🧮 Vergi dilimleri 2025 tarifesine göre kademeli uygulanır. Geçici vergi 3 ayda bir beyan edilir. Yıllık vergi Mart ayında beyan edilir. Geçici vergiler yıl sonu vergiden düşülür.")
