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

import pandas as pd
pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)
pd.set_option("display.width", 500)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

#######################################################################################################################
# VERİ ÖN HAZIRLIĞI
#######################################################################################################################

df_ = pd.read_excel(r"C:\Users\mstfr\PycharmProjects\eCommerseCRM\datasets\marketing_campaign.xlsx", sheet_name="Sheet1")
df = df_.copy()

df.isnull().sum()

#######################################################################################################################
# TARİH BİLGİSİ TAŞIYAN DEĞİŞKENLERİN TİP AYARLAMASI
#######################################################################################################################

df["Dt_Customer"] = df["Dt_Customer"].apply(pd.to_datetime)

#######################################################################################################################
# AVERAGE ORDER VALUE
#######################################################################################################################

df["total_transaction"] = df["NumCatalogPurchases"] + df["NumStorePurchases"] + df["NumWebPurchases"]
df["total_price"] = df["MntWines"] + df["MntFruits"] + df["MntMeatProducts"] + df["MntFishProducts"] + \
                 df["MntSweetProducts"] + df["MntGoldProds"]

cltv_c = df[["ID", "Dt_Customer", "total_transaction", "TotalPrice"]]
cltv_c["ID"].nunique()
cltv_c["average_order_value"] = cltv_c["TotalPrice"] / cltv_c["total_transaction"]

#######################################################################################################################
# PURCHASE FREQUENCY
#######################################################################################################################

cltv_c["purchase_frequency"] = cltv_c["total_transaction"] / cltv_c.shape[0]

#######################################################################################################################
# REPEAT RATE VE CHURN RATE
#######################################################################################################################

repeat_rate = cltv_c[cltv_c["total_transaction"] > 1].shape[0] / cltv_c.shape[0]
churn_rate = 1 - repeat_rate

#######################################################################################################################
# PROFIT MARGIN
#######################################################################################################################

cltv_c["profit_margin"] = cltv_c["TotalPrice"] * 0.10

#######################################################################################################################
# CUSTOMER VALUE
#######################################################################################################################

cltv_c["customer_value"] = cltv_c["average_order_value"] * cltv_c["purchase_frequency"]

#######################################################################################################################
# CLTV (CUSTOMER LİFETİME VALUE)
#######################################################################################################################

cltv_c["cltv"] = (cltv_c["customer_value"] / churn_rate) * cltv_c["profit_margin"]
cltv_c.sort_values("cltv", ascending=False).head(20)

#######################################################################################################################
# SEGMENTLERİN OLUŞTURULMASI
#######################################################################################################################

cltv_c["segment"] = pd.qcut(cltv_c["cltv"], 4, labels=["D", "C", "B", "A"])

cltv_c.groupby("segment").agg({"count", "mean", "sum"})
