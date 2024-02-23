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
import datetime as dt
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 500)
pd.set_option('display.float_format', lambda x: '%.3f' % x)

#######################################################################################################################
# VERİ ÖN HAZIRLIĞI
#######################################################################################################################

df_ = pd.read_excel(r"C:\Users\mstfr\PycharmProjects\eCommerseCRM\datasets\marketing_campaign.xlsx", sheet_name="Sheet1")
df = df_.copy()

df.head()
df.isnull().sum()
df.info()
df["ID"].nunique()
df.shape

#######################################################################################################################
# TARİH BİLGİSİ TAŞIYAN DEĞİŞKENLERİN TİP AYARLAMASI
#######################################################################################################################

df["Dt_Customer"] = df["Dt_Customer"].apply(pd.to_datetime)

#######################################################################################################################
# RECENCY, FREQUENCY VE MONATERY METRİKLERİNİN OLUŞTURULMASI
#######################################################################################################################

df["frequency"] = df["NumCatalogPurchases"] + df["NumStorePurchases"] + df["NumWebPurchases"]
df["monatery"] = df["MntWines"] + df["MntFruits"] + df["MntMeatProducts"] + df["MntFishProducts"] + \
                 df["MntSweetProducts"] + df["MntGoldProds"]

df[["Recency", "frequency", "monatery"]].describe().T
df1 = df.copy()
df = df1

df = df[df["frequency"] > 0]
df["frequency"] = df["frequency"].apply(lambda x: 1 if x == 0 else x)

#######################################################################################################################
# RECENCY, FREQUENCY VE MONATERY SKORLARININ OLUŞTURULMASI
#######################################################################################################################

rfm_df = df[["ID", "Recency", "frequency", "monatery"]]
rfm_df["recency_score"] = pd.qcut(df["Recency"], 5, labels=[5, 4, 3, 2, 1])
rfm_df["frequency_score"] = pd.qcut(df["frequency"], 5, labels=[1, 2, 3, 4, 5])
rfm_df["monetary_score"] = pd.qcut(df["monatery"], 5, labels=[1, 2, 3, 4, 5])

#######################################################################################################################
# RECENCY VE FREQUENCY SKORLARININ BİRLEŞTİRİLMESİ
#######################################################################################################################

rfm_df["rfm_score"] = rfm_df["recency_score"].astype(str) + rfm_df["frequency_score"].astype(str)

#######################################################################################################################
# RFM TABLOSUNA GÖRE SEGMENTLERE AYRILMASI
#######################################################################################################################

seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

rfm_df["segment"] = rfm_df["rfm_score"].replace(seg_map, regex=True)

rfm_df.loc[[655, 981, 1245, 1524, 1846, 2132]]
