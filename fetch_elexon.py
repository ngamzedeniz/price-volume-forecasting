# fetch_elexon.py
import requests
import pandas as pd
from datetime import datetime, timedelta
import io

# 🔑 Elexon API key
api_key = '0fad4fex2qqke42'

# --- 1. Price verisi (B1770) ---
url_price = f'https://api.bmreports.com/BMRS/B1770/v1?APIKey={api_key}&SettlementDate=*&Period=*&ServiceType=csv'
r_price = requests.get(url_price)
r_price.raise_for_status()
df_price = pd.read_csv(io.StringIO(r_price.text), skiprows=4)

if 'ImbalancePriceAmount' in df_price.columns:
    df_price.rename(columns={'ImbalancePriceAmount': 'Price'}, inplace=True)

# --- 2. Volume verisi (B1780) ---
url_volume = f'https://api.bmreports.com/BMRS/B1780/v1?APIKey={api_key}&SettlementDate=*&Period=*&ServiceType=csv'
r_volume = requests.get(url_volume)
r_volume.raise_for_status()
df_volume = pd.read_csv(io.StringIO(r_volume.text), skiprows=4)

if 'ImbalanceQuantity' in df_volume.columns:
    df_volume.rename(columns={'ImbalanceQuantity': 'Volume'}, inplace=True)

# --- 3. SettlementPeriod → datetime ---
def settlement_to_time(date_str, period):
    base = datetime.strptime(date_str, "%Y-%m-%d")
    minutes = (int(period) - 1) * 30
    return base + timedelta(minutes=minutes)

df_price['datetime'] = df_price.apply(lambda row: settlement_to_time(row['SettlementDate'], row['SettlementPeriod']), axis=1)
df_volume['datetime'] = df_volume.apply(lambda row: settlement_to_time(row['SettlementDate'], row['SettlementPeriod']), axis=1)

# --- 4. Birleştir (datetime + Price + Volume) ---
df = pd.merge(df_price[['datetime', 'Price']], df_volume[['datetime', 'Volume']], on='datetime', how='inner')

# --- 5. JSON olarak kaydet ---
df.to_json('forecast_price_volume.json', orient='records', date_format='iso')

print("✅ forecast_price_volume.json başarıyla oluşturuldu")
