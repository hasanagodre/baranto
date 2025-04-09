import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime


# HE Parameters
ticker = "AAPL"  # [frontend parametre]
start_date = "2020-01-01"  # [frontend parametre]
end_date = datetime.today().strftime('%Y-%m-%d')  # [otomatik: bugün]
interval = "1d"  # [frontend parametre] seçenekler: 1m, 15m, 1h, 4h, 1d, 1wk, 1mo, 1y
decimal_places = 2  # [frontend parametre]
atr_window = 30  # ATR hesaplama penceresi
atr_type = "SMA"  # [frontend parametre] seçenekler: SMA, EMA, WMA, RMA
step_percentage = 0.01 # Min_Max fiyat arası dikey fiyat artışlarını neye göre yapıyoruz
step_integer = 1 # Min_Max fiyat arası dikey fiyat artışlarını neye göre yapıyoruz
rect_min_duration = 40 # Bar sayısı olarak en az neye bakacağız
#rect_max_duration = len(Yahoo_OHLCV)
rect_bottom_up_flex = 0.02
rect_bottom_down_flex = 0.02
rect_top_up_flex = 0.02
rect_top_down_flex = 0.02

# Veriyi indir
Yahoo_OHLCV = yf.download(ticker, start=start_date, end=end_date, interval=interval)

# Veri çerçevesinin sütun adlarını yazdırarak kontrol edelim
#print("Data columns after downloading STLA:")
#print(Yahoo_OHLCV.columns)  # Sütun adlarını yazdırın

# Verinin ilk birkaç satırını görelim
#print("First few rows of data:")
#print(Yahoo_OHLCV.head())

# Minimum 'Low' ve maksimum 'High' değerlerini hesaplayalım
min_low = Yahoo_OHLCV['Low'].min().item()  # En düşük 'Low' değeri
max_high = Yahoo_OHLCV['High'].max().item()  # En yüksek 'High' değeri
specific_value = Yahoo_OHLCV.iloc[30]['High'].item()
specific_ortalama = Yahoo_OHLCV.iloc[10:20]['High'].mean().item()
#volume = df['Volume'].info()

#-------------------------------------------------------------
# Dikey Rectangle Parçaları : Baktığımız fiyat seviyeleri
current_value = min_low

# Aralıkları depolamak için bir liste oluşturuyoruz
step_values = []

# %1 artış ve 1 birimlik artışı karşılaştırarak ilerliyoruz
while current_value <= max_high:
    # %1 artış ve 1 birimlik artış
    step_percent = current_value * (1+step_percentage)
    step_unit = current_value + step_integer

    # Hangisi daha küçükse, onu seçiyoruz
    next_value = min(step_percent, step_unit)

    # Sonuçları kaydediyoruz
    step_values.append(next_value)

    # current_value'yi yeni değere eşitliyoruz
    current_value = next_value

#--------------------------------------------------------
# ATR hesaplama fonksiyonu
def calculate_atr(Yahoo_OHLCV, window, atr_type):
    Yahoo_OHLCV = Yahoo_OHLCV.copy()

    # True Range hesaplama
    Yahoo_OHLCV['previous_close',ticker] = Yahoo_OHLCV['Close',ticker].shift(1)
#   print("Previous Close:\n", Yahoo_OHLCV['previous_close'].head())
    Yahoo_OHLCV['tr1'] = Yahoo_OHLCV['High',ticker] - Yahoo_OHLCV['Low',ticker]
#   print("TR1 (High - Low):\n", Yahoo_OHLCV['tr1'].head())
#   print("TR1:\n", Yahoo_OHLCV['tr1'].head())
    Yahoo_OHLCV['tr2'] = abs(Yahoo_OHLCV['High',ticker] - Yahoo_OHLCV['previous_close',ticker])
#   print("TR2 (abs(High - Previous Close)):\n", Yahoo_OHLCV['tr2'].head())
    Yahoo_OHLCV['tr2'] = abs(Yahoo_OHLCV[('High', ticker)] - Yahoo_OHLCV[('previous_close', ticker)])
    Yahoo_OHLCV['tr3'] = abs(Yahoo_OHLCV['Low', ticker] - Yahoo_OHLCV['previous_close',ticker])

    # Gerçek hareket mesafesini hesapla (True Range)
    Yahoo_OHLCV['true_range'] = Yahoo_OHLCV[['tr1', 'tr2', 'tr3']].max(axis=1)

    # ATR hesaplama türüne göre
    if atr_type == "SMA":
        Yahoo_OHLCV['ATR'] = Yahoo_OHLCV['true_range'].rolling(window=window).mean()
    elif atr_type == "EMA":
        Yahoo_OHLCV['ATR'] = Yahoo_OHLCV['true_range'].ewm(span=window, adjust=False).mean()
    elif atr_type == "WMA":
        weights = list(range(1, window + 1))
        def weighted_ma(x): return (x * weights).sum() / sum(weights)
        Yahoo_OHLCV['ATR'] = Yahoo_OHLCV['true_range'].rolling(window=window).apply(weighted_ma, raw=True)
    elif atr_type == "RMA":
        rma = Yahoo_OHLCV['true_range'].copy()
        rma.iloc[:window] = rma.iloc[:window].mean()
        for i in range(window, len(rma)):
            rma.iloc[i] = (rma.iloc[i - 1] * (window - 1) + rma.iloc[i]) / window
        Yahoo_OHLCV['ATR'] = rma
    else:
        raise ValueError(f"Unknown atr_type: {atr_type}")

    return Yahoo_OHLCV

# ATR hesaplamasını uygulayalım
atr_data = calculate_atr(Yahoo_OHLCV, atr_window, atr_type)
latest_atr = atr_data['ATR'].iloc[-1]  # En son ATR değeri
specific_atr = atr_data.iloc[30]['ATR'].item()
#--------------------------------------------------------

bottom_candidates = []

# Step values'ları kullanarak barları tarıyoruz
for step_value in step_values:
    start_bar = 0  # Başlangıç noktası
    for i in range(0, len(Yahoo_OHLCV)):  # Verinin tamamını tarıyoruz
        # Low değeri step_value * (1 - rect_bottom_down_flex) seviyesinin altına inerse
        if Yahoo_OHLCV['Low'].iloc[i].item() < step_value * (1 - rect_bottom_down_flex):
            # Eğer uygun bar bulunduysa, bu noktada işlemi bitiriyoruz
            # ve bu bilgiyi bottom_candidates listesine ekliyoruz.
            bottom_candidates.append({
                'step_value': step_value,
                'start_bar': start_bar,  # Başlangıç noktası 0. bar
                'start_date': Yahoo_OHLCV.index[start_bar],
                'end_bar': i,  # Bulunan barı bitiş noktası olarak kabul ediyoruz
                'end_date': Yahoo_OHLCV.index[i]
              })
            break  # Aramayı durduruyoruz, çünkü bir bottom candidate bulduk

# Bottom candidate'ları B1 tablosuna kaydediyoruz
BC = pd.DataFrame(bottom_candidates)

# BC tablosunu yazdıralım
print(BC)

#---------------------------------------------------------

print("\n")  # Bu satır başında bir boş satır bırakır
print(f"Length: {len(Yahoo_OHLCV)}")

# Sonuçları yazdıralım
print("\n")  # Bu satır başında bir boş satır bırakır
print(f"ATR Calculation for {ticker}:")
print(f"Latest ATR ({atr_type}): {latest_atr:.{decimal_places}f}")
#--------------------------------------------------------

#print("\n")  # Bu satır başında bir boş satır bırakır
#print(atr_data[['ATR']].tail(len(Yahoo_OHLCV)))  # Son 5 ATR değerini gösterir

print("\n")  # Bu satır başında bir boş satır bırakır
print(f"Spesific ATR: {specific_atr:.{decimal_places}f}")

print("\n")  # Bu satır başında bir boş satır bırakır
print(f"Minimum Value: {min_low:.{decimal_places}f}")
print(f"Maximum Value: {max_high:.{decimal_places}f}")
print("\n")  # Bu satır başında bir boş satır bırakır
print(f"Spesific: {specific_value:.{decimal_places}f}")
print(f"Spesific Ortalama: {specific_ortalama:.{decimal_places}f}")

print("\n")  # Bu satır başında bir boş satır bırakır
# Aralıkları yazdıralım
#print("Value Ranges (Minimum Value to Maximum Value):")
#for value in step_values:
#    print(f"{value:.{decimal_places}f}")
