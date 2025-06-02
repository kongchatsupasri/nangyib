#%%
import streamlit as st
import pandas as pd
import json
import math
#%%

compenent_d = json.load(open('set_d.json'))
sku_df = pd.read_excel('sku.xlsx', skiprows=2)
# st.dataframe(sku_df)
#%%
wpp_sku = [
    '5283830469-1723047357840-2', 
    '5283830469-1723047357840-1', 
    '5283830469-1723047357840-0', 
    '4586761423-1682154660017-1', 
    '4586761423-1682154660017-4', 
    '4586761423-1682154660017-6', 
    '4586761423-1682154660017-2', 
    '4017398478-1691655142813-0', 
    '4017398478-1667990095194-1', 
    '5528354151-1734959471510-2', 
    '5528354151-1734959471507-1', 
    '5528354151-1734959471504-0', 
    '5260404779-1725279034904-2', 
    '5260404779-1725279034904-3', 
    '5260404779-1721666451156-0', 
    '5260404779-1725279034904-1', 
    '5260404779-1726754533302-4'
]

small_wpp_sku = [
    '4017398478-1741015258370-3', '4017398478-1741015258370-2'
]


st.set_page_config(layout="wide")
#%%
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader('Shopee')
    shopee_file = st.file_uploader(
        label = 'Shopee',
        accept_multiple_files = False, 
        type = 'xlsx', 
        label_visibility = 'hidden'
    )

with col2:
    st.subheader('TikTok')
    tiktok_file = st.file_uploader(
        label = 'TikTok',
        accept_multiple_files = False, 
        type = 'csv', 
        label_visibility = 'hidden'
    )

with col3:
    st.subheader('Lazada')


if 'clicked' not in st.session_state:
    st.session_state.clicked = False

def click_button():
    st.session_state.clicked = True

st.button('Click me', on_click=click_button)

if st.session_state.clicked:
    d = {}


    df = pd.DataFrame()

    if tiktok_file:
        tiktok_df = pd.read_csv(tiktok_file, converters={'Order ID':str})
        tiktok_df = tiktok_df[['Order ID', 'Seller SKU', 'Variation', 'Quantity']]
        tiktok_df.columns = ['order_id', 'sku', 'p', 'q']
        # st.dataframe(tiktok_df.head())
        df = pd.concat([df, tiktok_df], axis = 0).reset_index(drop = True)

    if shopee_file:
        shopee_df = pd.read_excel(shopee_file)
        shopee_df = shopee_df[['หมายเลขคำสั่งซื้อ', 'เลขอ้างอิง SKU (SKU Reference No.)', 'ชื่อตัวเลือก', 'จำนวน']]
        shopee_df.columns = ['order_id', 'sku', 'p', 'q']

        # st.dataframe(shopee_df)
        df = pd.concat([df, shopee_df], axis = 0).reset_index(drop = True)

    if df.shape[0] != 0:
        for order_id in df['order_id'].unique():
            df1 = df[df['order_id'] == order_id].reset_index(drop = True)

            # st.dataframe(df1)

            d1 = {}
            
            for i in range(df1['sku'].shape[0]):
                sku = df1.loc[i, 'sku']
                q = int(df1.loc[i, 'q'])

                # st.write(sku)

                if str(sku) in compenent_d.keys():
                    
                    for item_d in compenent_d[str(sku)]['item']:
                        if item_d['n'] not in d1.keys():
                            d1[item_d['n']] = {'sku': item_d['sku'], 'q': q * item_d['q']}

                        else:
                            d1[item_d['n']]['q'] += q * d1[item_d['n']]['q']

                else:
                    name = sku_df[sku_df['ProductCode'] == sku]['Name'].tolist()[0]
                    if name not in d1.keys():
                        d1[name] = {'sku': sku, 'q': q}
                    else:
                        d1[name]['q'] += q

            # st.write(d1)
            #check nano
            wpp_count = 0
            small_wpp_count = 0
            
            for d2 in d1.values():
                if d2['sku'] in wpp_sku:
                    wpp_count += d2['q']
                elif d2['sku'] in small_wpp_sku:
                    small_wpp_count += d2['q']

            if wpp_count == 0:
                pass
            elif wpp_count <= 5:
                d1['กาวนาโนม้วนเล็ก ขนาด 1m x 3cm x 1mm'] = {'sku': '4586756746-1729009113315-1', 'q': 1}
            elif wpp_count > 5 and wpp_count <= 19:
                d1['กาวนาโนม้วนใหญ่ ขนาด 3m x 3cm x 1mm'] = {'sku': '4586756746-1682155194954-0', 'q': 1}
            else: 
                d1['กาวนาโนม้วนใหญ่ ขนาด 3m x 3cm x 1mm'] = {'sku': '4586756746-1682155194954-0', 'q': math.floor(wpp_count / 10)}
            
            
            if small_wpp_count == 0:
                pass
            elif small_wpp_count > 0 and small_wpp_count <= 19:
                d1['กาวนาโนม้วนเล็ก ขนาด 1m x 3cm x 1mm'] = {'sku': '4586756746-1729009113315-1', 'q': 1}
            else:
                d1['กาวนาโนม้วนเล็ก ขนาด 1m x 3cm x 1mm'] = {'sku': '4586756746-1729009113315-1', 'q': math.floor(wpp_count / 10)}


            for key, value in d1.items():
                if key not in d.keys():
                    d[key] = value
                else:
                    d[key]['q'] += value['q']

    result_df = pd.DataFrame()

    for key, value in d.items():
        result_df = pd.concat([result_df, 
                            pd.DataFrame([[key, value['sku'], value['q']]], columns = ['item', 'sku', 'q'])], 
                            axis = 0)

    if result_df.shape[0] != 0:
        result_df['pack'] = [False] * result_df.shape[0]
        result_df = result_df[['pack', 'item', 'q', 'sku']]
        result_df = result_df.sort_values(by = 'sku', ascending = True)

        st.data_editor(
            result_df,
            column_config={
                "favorite": st.column_config.CheckboxColumn(
                    "pack",
                    help="check if packed",
                    default=False,
                )
            },
            disabled=['item', 'sku', 'q'],
            hide_index=True,
        )
#%%
