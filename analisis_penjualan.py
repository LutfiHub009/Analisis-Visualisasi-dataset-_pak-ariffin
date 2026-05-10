import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime as dt
import warnings

warnings.filterwarnings('ignore')

# Konfigurasi Tema Visual
sns.set_theme(style="whitegrid", palette="muted")

def main():
    print("="*50)
    print("Memulai Praktikum Analisis Performa Penjualan")
    print("="*50)

    # ---------------------------------------------------------
    # Langkah 1 & 2: Persiapan Data & Pembersihan (Data Cleaning)
    # ---------------------------------------------------------
    print("\n[1/5] Memproses dan membersihkan data...")
    df = pd.read_csv('data_praktikum_analisis_data.csv')
    df = df.dropna(subset=['Total_Sales'])
    df = df[df['Price_Per_Unit'] > 0]
    df['Order_Date'] = pd.to_datetime(df['Order_Date'])
    print(f"      -> Data bersih tersisa: {df.shape[0]} baris.")

    # ---------------------------------------------------------
    # Langkah 3: Analisis & Visualisasi Dasar
    # ---------------------------------------------------------
    print("[2/5] Membuat visualisasi Tren Bulanan dan Heatmap...")
    
    # Tren Penjualan Bulanan
    df['Month'] = df['Order_Date'].dt.to_period('M').astype(str)
    monthly_sales = df.groupby('Month')['Total_Sales'].sum()

    plt.figure(figsize=(10, 5))
    plt.plot(monthly_sales.index, monthly_sales.values, marker='o', color='b', linewidth=2, markersize=8)
    plt.title('Tren Penjualan Bulanan', fontsize=14, pad=15)
    plt.xlabel('Bulan', fontsize=12)
    plt.ylabel('Total Penjualan (Rp)', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('visualisasi_1_tren_bulanan.png', dpi=300)
    plt.show() # Ditambahkan kembali agar grafik muncul saat di-play
    plt.close()

    # Heatmap Korelasi
    correlation = df[['Total_Sales', 'Ad_Budget', 'Price_Per_Unit', 'Quantity']].corr()
    plt.figure(figsize=(8, 6))
    sns.heatmap(correlation, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
    plt.title('Peta Korelasi Antar Variabel', fontsize=14, pad=15)
    plt.tight_layout()
    plt.savefig('visualisasi_2_heatmap.png', dpi=300)
    plt.show() # Ditambahkan kembali agar grafik muncul saat di-play
    plt.close()

    # ---------------------------------------------------------
    # Tugas Siswa: Optimasi Strategi Pemasaran
    # ---------------------------------------------------------
    print("[3/5] Mengidentifikasi produk underperformer (Scatter Plot)...")
    
    # Tugas 1: Underperformer
    avg_price = df['Price_Per_Unit'].mean()
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='Price_Per_Unit', y='Quantity', hue='Product_Category', s=100, alpha=0.7)
    plt.axvline(avg_price, color='red', linestyle='--', linewidth=2, label='Rata-rata Harga')
    plt.title('Identifikasi Produk Underperformer\n(Harga Tinggi vs Volume Rendah)', fontsize=14, pad=15)
    plt.xlabel('Price Per Unit (Rp)')
    plt.ylabel('Quantity')
    plt.legend()
    plt.tight_layout()
    plt.savefig('tugas1_underperformer.png', dpi=300)
    plt.show() # Ditambahkan kembali agar grafik muncul saat di-play
    plt.close()

    print("[4/5] Melakukan Segmentasi Pelanggan (RFM Analysis)...")
    
    # Tugas 2: RFM Analysis
    snapshot_date = df['Order_Date'].max() + dt.timedelta(days=1)
    rfm = df.groupby('CustomerID').agg({
        'Order_Date': lambda x: (snapshot_date - x.max()).days,
        'Order_ID': 'count',
        'Total_Sales': 'sum'
    })
    rfm.columns = ['Recency', 'Frequency', 'Monetary']
    rfm['R_Score'] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1], duplicates='drop')
    rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
    rfm['M_Score'] = pd.qcut(rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5], duplicates='drop')
    rfm['RFM_Group'] = rfm.R_Score.astype(str) + rfm.F_Score.astype(str) + rfm.M_Score.astype(str)
    rfm.to_csv('hasil_rfm.csv')

    print("[5/5] Menganalisis efisiensi kategori dan menguji hipotesis regresi...")
    
    # Tugas 3: Kontribusi Kategori
    category_analysis = df.groupby('Product_Category')[['Total_Sales', 'Ad_Budget']].sum().reset_index()
    category_analysis['Efficiency_Ratio'] = category_analysis['Total_Sales'] / category_analysis['Ad_Budget']
    category_analysis = category_analysis.sort_values(by='Efficiency_Ratio', ascending=True)

    plt.figure(figsize=(10, 6))
    cat_melted = category_analysis.melt(id_vars='Product_Category', value_vars=['Total_Sales', 'Ad_Budget'], 
                                        var_name='Metrics', value_name='Amount')
    sns.barplot(data=cat_melted, y='Product_Category', x='Amount', hue='Metrics', orient='h')
    plt.title('Kontribusi Kategori: Total Penjualan vs Biaya Iklan', fontsize=14, pad=15)
    plt.xlabel('Jumlah (Rp)')
    plt.ylabel('Kategori Produk')
    plt.tight_layout()
    plt.savefig('tugas3_kontribusi_kategori.png', dpi=300)
    plt.show() # Ditambahkan kembali agar grafik muncul saat di-play
    plt.close()

    # Tugas 4: Uji Hipotesis & Regresi Linear
    X = df['Ad_Budget'].values
    y = df['Total_Sales'].values
    m, c = np.polyfit(X, y, 1)

    plt.figure(figsize=(10, 6))
    sns.regplot(data=df, x='Ad_Budget', y='Total_Sales', scatter_kws={'alpha':0.6, 's':50}, line_kws={'color':'red', 'linewidth':2})
    plt.title('Pengaruh Biaya Iklan terhadap Total Penjualan\n(Regresi Linear)', fontsize=14, pad=15)
    plt.xlabel('Biaya Iklan (Ad Budget)')
    plt.ylabel('Total Penjualan (Total Sales)')
    plt.tight_layout()
    plt.savefig('tugas4_regresi_iklan.png', dpi=300)
    plt.show() # Ditambahkan kembali agar grafik muncul saat di-play
    plt.close()

    print("\n==================================================")
    print("SELESAI! Semua grafik dan laporan telah berhasil dibuat.")
    print("==================================================\n")

if __name__ == "__main__":
    main()
