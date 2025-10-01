import requests
import pandas as pd
from datetime import datetime

# 🔑 Senin Elexon API key
api_key = '0fad4fex2qqke42'

# B1770 raporu: Imbalance Price (GB / Scotland dahil)
url = f'https://api.bmreports.com/BMRS/B1770/v1?APIKey={api_key}&Period=*&SettlementDate=*&ServiceType=csv'

try:
    # Veriyi çek
    response = requests.get(url)
    response.raise_for_status()  # HTTP hatası varsa hata ver

    # CSV dosyasına yaz
    with open('elexon_data.csv', 'wb') as f:
        f.write(response.content)

    # CSV'yi oku
    df = pd.read_csv('elexon_data.csv', skiprows=4)

    # datetime sütunu oluştur (SettlementDate + SettlementPeriod)
    df['datetime'] = pd.to_datetime(
        df['SettlementDate'] + ' ' + df['SettlementPeriod'].astype(str) + ':00',
        format='%Y-%m-%d %H:%M'
    )

    # Sadece gerekli sütunlar
    df = df[['datetime', 'Price']]

    # JSON olarak kaydet
    df.to_json('forecast_price.json', orient='records', date_format='iso')

    print("forecast_price.json başarıyla oluşturuldu ✅")

except Exception as e:
    print("Hata oluştu:", e)
