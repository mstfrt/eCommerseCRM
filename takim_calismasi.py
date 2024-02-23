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
pd.set_option('display.width', 500)
pd.set_option('display.float_format', lambda x: '%.3f' % x)

#######################################################################################################################
# VERİ ÖN HAZIRLIĞI
#######################################################################################################################

df_ = pd.read_excel(r"C:\Users\mstfr\PycharmProjects\eCommerseCRM\datasets\marketing_campaign.xlsx", sheet_name="Sheet1")
df = df_.copy()

df.isnull().sum()
df.info()
df["Dt_Customer"] = df["Dt_Customer"].apply(pd.to_datetime)

rfm = pd.DataFrame()
rfm["ID"] = df["ID"]
rfm["recency"] = df["Recency"]
rfm["frequency"] = df["NumWebPurchases"] + df["NumCatalogPurchases"] + df["NumStorePurchases"]
rfm["monetary"] = df["MntWines"] + df["MntFruits"] + df["MntMeatProducts"] + df["MntFishProducts"] + \
                  df["MntSweetProducts"] + df["MntGoldProds"]

rfm[rfm["frequency"] == 0]
df.loc[655]
rfm = rfm[rfm["frequency"] > 0]
rfm.describe().T

rfm["recency_score"] = pd.qcut(rfm["recency"], 5, labels=[5, 4, 3, 2, 1])
rfm["frequency_score"] = pd.qcut(rfm["frequency"], 5, labels=[1, 2, 3, 4, 5])
rfm["monetary_score"] = pd.qcut(rfm["monetary"], 5, labels=[1, 2, 3, 4, 5])

rfm["rfm_score"] = rfm["recency_score"].astype(str) + rfm["frequency_score"].astype(str)

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

rfm["segment"] = rfm["rfm_score"].replace(seg_map, regex=True)
list = rfm[rfm["segment"] == "potential_loyalists"]["ID"].values.tolist()
new_df = df.merge(rfm, on="ID", how="left")
new_df = new_df[new_df["ID"].isin(list)]
df[df["Income"] == 666666]
new_df["Income"].min()
df["Income"].min()
rfm[rfm["ID"] == 9432]
new_df[new_df["Income"] == 666666]
rfm.groupby("segment").agg({"count", "mean", "sum"})


#######################################################################################################################
# CLTV
#######################################################################################################################
import pandas as pd
pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)
pd.set_option("display.width", 500)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

df_ = pd.read_excel(r"C:\Users\mstfr\PycharmProjects\eCommerseCRM\datasets\marketing_campaign.xlsx", sheet_name="Sheet1")
df = df_.copy()

# Average order value

df["total_transaction"] = df["NumWebPurchases"] + df["NumCatalogPurchases"] + df["NumStorePurchases"]
df["total_price"] = df["MntWines"] + df["MntFruits"] + df["MntMeatProducts"] + df["MntFishProducts"] + \
                  df["MntSweetProducts"] + df["MntGoldProds"]

cltv_c = df[["ID", "total_transaction", "total_price"]]
cltv_c["average_order_value"] = cltv_c["total_price"] / cltv_c["total_transaction"]

# Purchase Frequency
cltv_c["purchase_frequency"] = cltv_c["total_transaction"] / cltv_c.shape[0]

# Customer Value
cltv_c["customer_value"] = cltv_c["average_order_value"] * cltv_c["purchase_frequency"]

# Churn Rate
repeat_rate = cltv_c[cltv_c["total_transaction"] > 1].shape[0] / cltv_c.shape[0]
churn_rate = 1 - repeat_rate

# profit margin

cltv_c["profit_margin"] = cltv_c["total_price"] * 0.10

# CLTV
cltv_c["cltv"] = (cltv_c["customer_value"] / churn_rate) * cltv_c["profit_margin"]

# Segmentleme
cltv_c["segment"] = pd.qcut(cltv_c["cltv"], 5, labels=["E", "D", "C", "B", "A"])
cltv_c.groupby("segment").agg({"count", "mean", "sum"})


#######################################################################################################################
# CLTV Prediction
#######################################################################################################################
import datetime as dt
import pandas as pd
from lifetimes import BetaGeoFitter
from lifetimes import GammaGammaFitter

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 500)
pd.set_option('display.float_format', lambda x: '%.4f' % x)

df_ = pd.read_excel(r"C:\Users\mstfr\PycharmProjects\eCommerseCRM\datasets\marketing_campaign.xlsx", sheet_name="Sheet1")
df = df_.copy()

# recency: son satın alma tarihi ile ilk satın alma tarihi arasındaki zaman farkı. Haftalık. (kullanıcı özelinde)
# frequency: tekrar eden toplam satın alma sayısı (frequency>1)
# T: Müşterinin yaşı. Haftalık. (analiz tarihinden ne kadar süre önce ilk satın alma yapılmış)
# monetary: satın alma başına ortalama kazanç

today_date = dt.datetime(2014, 12, 1)

for i, val in enumerate(df["Recency"].values):
    df["last_order_date"][i] = today_date - dt.timedelta(days=int(val))

# Alternatif:
df["last_order_date"] = today_date - df["Recency"].apply(lambda x: dt.timedelta(days=int(x)))

df["Dt_Customer"] = df["Dt_Customer"].apply(pd.to_datetime)

df["total_transaction"] = df["NumCatalogPurchases"] + df["NumStorePurchases"] + df["NumWebPurchases"]
df["total_price"] = df["MntWines"] + df["MntFruits"] + df["MntMeatProducts"] + df["MntFishProducts"] + \
                 df["MntSweetProducts"] + df["MntGoldProds"]

df = df[df["total_transaction"] > 1]

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
    dataframe.loc[(dataframe[variable] < low_limit), variable] = low_limit
    dataframe.loc[(dataframe[variable] > up_limit), variable] = up_limit


replace_with_thresholds(df, "total_transaction")
replace_with_thresholds(df, "total_price")

cltv_df = pd.DataFrame()

# recency: son satın alma tarihi ile ilk satın alma tarihi arasındaki zaman farkı. Haftalık. (kullanıcı özelinde)
# frequency: tekrar eden toplam satın alma sayısı (frequency>1)
# T: Müşterinin yaşı. Haftalık. (analiz tarihinden ne kadar süre önce ilk satın alma yapılmış)
# monetary: satın alma başına ortalama kazanç

cltv_df["ID"] = df["ID"]
cltv_df["recency"] = (df["last_order_date"] - df["Dt_Customer"]) / dt.timedelta(weeks=1)
cltv_df["frequency"] = df["total_transaction"]
cltv_df["T"] = (today_date - df["Dt_Customer"]) / dt.timedelta(weeks=1)
cltv_df["monetary"] = df["total_price"] / df["total_transaction"]


bgf = BetaGeoFitter(penalizer_coef=0.001)

bgf.fit(recency=cltv_df["recency"],
        frequency=cltv_df["frequency"],
        T=cltv_df["T"])

# 3 ayda en fazla işllem yapacak ilk 5 kişi

cltv_df["3_m_transaction_predict"] = bgf.predict(12,
                                                cltv_df["frequency"],
                                                cltv_df["recency"],
                                                cltv_df["T"])

cltv_df.sort_values("3_m_transaction_predict", ascending=False)

ggf = GammaGammaFitter(penalizer_coef=0.01)

ggf.fit(frequency=cltv_df["frequency"], monetary_value=cltv_df["monetary"])

cltv_df["con_exp_ave_pro"] = ggf.conditional_expected_average_profit(cltv_df["frequency"],
                                                                    cltv_df["monetary"])

cltv_df["cltv"] = ggf.customer_lifetime_value(bgf,
                                              cltv_df["frequency"],
                                              cltv_df["recency"],
                                              cltv_df["T"],
                                              cltv_df["monetary"],
                                              time=1,
                                              freq="W",
                                              discount_rate=0.01)

cltv_df.sort_values("cltv", ascending=False).head(10)


cltv_df["segment"] = pd.qcut(cltv_df["cltv"], 5, labels=["E", "D", "C", "B", "A"])

cltv_df.groupby("segment").agg({"count", "mean", "sum"})
