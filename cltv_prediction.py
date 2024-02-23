# ID :                  Müşteri id'si
# Year_Birth :          Müşterinin doğum yılı
# Education :           Müşterinin eğitim düzeyi
# Marital_Status :      Müşterinin medeni durumu
# Income :              Müşterinin yıllık hane geliri
# Kidhome :             Müşterinin evindeki küçük çocukların sayısı
# Teenhome :            Number of teenagers in customer’s household
# Dt_Customer :         Müşterinin şirkete kayıt tarihi
# Recency :             Son satın alma işleminden bu yana geçen gün sayısı
# MntWines :            Son 2 yılda şarap ürünlerine harcanan miktar
# MntFruits :           Son 2 yılda meyve ürünlerine harcanan miktar
# MntMeatProducts :     Son 2 yılda et ürünlerine harcanan miktar
# MntFishProducts :     Son 2 yılda balık ürünlerine harcanan miktar
# MntSweetProducts :    Son 2 yılda tatlı ürünlere harcanan miktar
# MntGoldProds :        Son 2 yılda altın ürünlerine harcanan miktar
# NumDealsPurchases :   İndirimli satın alma sayısı
# NumWebPurchases :     Şirketin web sitesi üzerinden yapılan satın alma sayısı
# NumCatalogPurchases : Katalog kullanılarak yapılan satın alma sayısı
# NumStorePurchases :   Doğrudan mağazalarda yapılan satın alma sayısı
# NumWebVisitsMonth :   Şirketin web sitesini ziyaret eden müşteri sayısı
# AcceptedCmp3 :        3. kampanyada müşteri teklifi kabul ederse 1, aksi halde 0
# AcceptedCmp4 :        4. kampanyada müşteri teklifi kabul ederse 1, aksi halde 0
# AcceptedCmp5 :        5. kampanyada müşteri teklifi kabul ederse 1, aksi halde 0
# AcceptedCmp1 :        1. kampanyada müşteri teklifi kabul ederse 1, aksi halde 0
# AcceptedCmp2 :        2. kampanyada müşteri teklifi kabul ederse 1, aksi halde 0
# Complain :            1 müşteri son 2 yılda şikayette bulunduysa
# Z_CostContact :       Bir müşteriyle iletişim kurmanın maliyeti
# Z_Revenue :           Müşteri kabul kampanyası sonrası gelir
# Response :            Müşteri son kampanyada teklifi kabul ettiyse 1, aksi takdirde 0

import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
from lifetimes import BetaGeoFitter
from lifetimes import GammaGammaFitter
from lifetimes.plotting import plot_period_transactions

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 500)
pd.set_option('display.float_format', lambda x: '%.4f' % x)

#######################################################################################################################
# VERİ ÖN İŞLEME
#######################################################################################################################

df_ = pd.read_excel(r"C:\Users\mstfr\PycharmProjects\eCommerseCRM\datasets\marketing_campaign.xlsx", sheet_name="Sheet1")
df = df_.copy()

df["Dt_Customer"] = df["Dt_Customer"].apply(pd.to_datetime)
df["total_transaction"] = df["NumCatalogPurchases"] + df["NumStorePurchases"] + df["NumWebPurchases"]
df["total_price"] = df["MntWines"] + df["MntFruits"] + df["MntMeatProducts"] + df["MntFishProducts"] + \
                 df["MntSweetProducts"] + df["MntGoldProds"]

df[["total_transaction", "total_price"]].describe().T


def outlier_thresholds(dataframe, variable):
    quartile1 = dataframe[variable].quantile(0.01)
    quartile3 = dataframe[variable].quantile(0.99)
    interquantile_range = quartile3 - quartile1
    up_limit = quartile3 + 1.5 * interquantile_range
    low_limit = quartile1 - 1.5 * interquantile_range
    return low_limit, up_limit


def replace_with_thresholds(dataframe, variable):
    low_limit, up_limit = outlier_thresholds(dataframe, variable)
    # dataframe.loc[(dataframe[variable] < low_limit), variable] = low_limit
    dataframe.loc[(dataframe[variable] > up_limit), variable] = up_limit



replace_with_thresholds(df, "total_transaction")
replace_with_thresholds(df, "total_price")

#######################################################################################################################
# RECENCY, FREQUENCY, T VE MONATERY METRİKLERİNİN OLUŞTURULMASI
#######################################################################################################################

# recency: son satın alma tarihi ile ilk satın alma tarihi arasındaki zaman farkı. Haftalık. (kullanıcı özelinde)
# frequency: tekrar eden toplam satın alma sayısı (frequency>1)
# T: Müşterinin yaşı. Haftalık. (analiz tarihinden ne kadar süre önce ilk satın alma yapılmış)
# monetary: satın alma başına ortalama kazanç

cltv_df = pd.DataFrame()

today_date = dt.datetime(2014, 12, 1)
df["last_transaction_date"] = ""


for i, val in enumerate(df["Recency"].values):
    df["last_transaction_date"][i] = today_date - dt.timedelta(days=int(val))
# Alternatif Yöntem:
df["last_order_date"] = today_date - df["Recency"].apply(lambda x: dt.timedelta(days=int(x)))
#######################################################################################################################

df["last_transaction_date"] = df["last_transaction_date"].astype("datetime64")

df = df[df["total_transaction"] > 1]

cltv_df["ID"] = df["ID"]
cltv_df["recency"] = (df["last_transaction_date"] - df["Dt_Customer"]) / dt.timedelta(weeks=1)
cltv_df["frequency"] = df["total_transaction"]
cltv_df.describe().T
cltv_df["T"] = (today_date - df["Dt_Customer"]) / dt.timedelta(weeks=1)
cltv_df["monetary"] = df["total_price"] / df["total_transaction"]

#######################################################################################################################
# BG-NBD MODELİNİN KURULMASI
#######################################################################################################################

bgf = BetaGeoFitter(penalizer_coef=0.001)

bgf.fit(frequency=cltv_df['frequency'],
        recency=cltv_df['recency'],
        T=cltv_df['T'])

# 1 hafta içinde en çok satın alma beklediğimiz 10 müşteri kimdir?

bgf.predict(1,
            cltv_df['frequency'],
            cltv_df['recency'],
            cltv_df['T']).sort_values(ascending=False).head(10)

cltv_df.loc[1898]

#######################################################################################################################
# GAMMA-GAMMA MODELİNİN KURULMASI
#######################################################################################################################

ggf = GammaGammaFitter(penalizer_coef=0.01)

ggf.fit(cltv_df['frequency'], cltv_df['monetary'])

ggf.conditional_expected_average_profit(cltv_df['frequency'],
                                        cltv_df['monetary']).sort_values(ascending=False).head(10)

cltv_df.loc[1328]

#######################################################################################################################
# BG-NBD VE GAMMA-GAMMA MODELLERİ İLE CLTV'NİN HESAPLANMASI
#######################################################################################################################

cltv_df["cltv"] = ggf.customer_lifetime_value(bgf,
                                              cltv_df['frequency'],
                                              cltv_df['recency'],
                                              cltv_df['T'],
                                              cltv_df['monetary'],
                                              time=3,  # 3 aylık
                                              freq="W",  # T'nin frekans bilgisi.
                                              discount_rate=0.01)


cltv_final = df.merge(cltv_df, on="ID", how="left")
cltv_final.sort_values(by="cltv", ascending=False).head(10)

#######################################################################################################################
# CLTV'YE GÖRE SEGMENTLERİN OLUŞTURULMASI
#######################################################################################################################

cltv_final

cltv_final["segment"] = pd.qcut(cltv_final["cltv"], 4, labels=["D", "C", "B", "A"])

cltv_final.sort_values(by="cltv", ascending=False).head(50)

cltv_final.groupby("segment").agg(
    {"count", "mean", "sum"})
