from mlxtend.frequent_patterns import apriori, association_rules
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 500)
pd.set_option('display.expand_frame_repr', False)

df_ = pd.read_excel(r"path\online_retail_II.xlsx",
                    sheet_name="Year 2010-2011")
df = df_.copy()


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


def retail_data_prep(dataframe):
    dataframe.dropna(inplace=True)
    dataframe = dataframe[~dataframe["Invoice"].str.contains("C", na=False)]
    dataframe = dataframe[dataframe["Quantity"] > 0]
    dataframe = dataframe[dataframe["Price"] > 0]
    replace_with_thresholds(dataframe, "Quantity")
    replace_with_thresholds(dataframe, "Price")
    return dataframe


df = retail_data_prep(df)

df_gr = df[df['Country'] == "Germany"]

df_gr.groupby(['Invoice', 'Description']). \
    agg({"Quantity": "sum"}). \
    unstack(). \
    fillna(0). \
    applymap(lambda x: 1 if x > 0 else 0)


def create_invoice_product_df(dataframe, id=False):
    if id:
        return dataframe.groupby(['Invoice', "StockCode"])['Quantity'].sum().unstack().fillna(0). \
            applymap(lambda x: 1 if x > 0 else 0)
    else:
        return dataframe.groupby(['Invoice', 'Description'])['Quantity'].sum().unstack().fillna(0). \
            applymap(lambda x: 1 if x > 0 else 0)


gr_inv_pro_df = create_invoice_product_df(df_gr, id=True)


def check_id(dataframe, stock_code):
    product_name = dataframe[dataframe["StockCode"] == stock_code][["Description"]].values[0].tolist()
    print(product_name)


frequent_itemsets = apriori(gr_inv_pro_df, min_support=0.01, use_colnames=True)
frequent_itemsets.sort_values("support", ascending=False)

rules = association_rules(frequent_itemsets, metric="support", min_threshold=0.01)
sorted_rules = rules.sort_values("lift", ascending=False)

check_id(df_gr, 21987)
# ['PACK OF 6 SKULL PAPER CUPS']
check_id(df_gr, 23235)
# ['STORAGE TIN VINTAGE LEAF']
check_id(df_gr, 22747)
# ["POPPY'S PLAYHOUSE BATHROOM"]

recommendation_list = []

for i, product in enumerate(sorted_rules["antecedents"]):
    for j in list(product):
        if j == 21987:
            recommendation_list.append(list(sorted_rules.iloc[i]["consequents"])[0])

recommendation_list[0:1]
# [21086]
check_id(df, recommendation_list[0])
# ['SET/6 RED SPOTTY PAPER CUPS']

recommendation_list = []

for i, product in enumerate(sorted_rules["antecedents"]):
    for j in list(product):
        if j == 23235:
            recommendation_list.append(list(sorted_rules.iloc[i]["consequents"])[0])

recommendation_list[0:1]
# [23244]
check_id(df, recommendation_list[0])
# ['ROUND STORAGE TIN VINTAGE LEAF']

recommendation_list = []

for i, product in enumerate(sorted_rules["antecedents"]):
    for j in list(product):
        if j == 22747:
            recommendation_list.append(list(sorted_rules.iloc[i]["consequents"])[0])

recommendation_list[0:1]
# [22745]
check_id(df, recommendation_list[0])
# ["POPPY'S PLAYHOUSE BEDROOM "]
