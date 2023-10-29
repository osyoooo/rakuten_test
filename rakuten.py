APP_ID = st.secrets["db_rakutenAPI"]

input_score = st.sidebar.number_input('ここに入力した数字以上の評価のホテルを表示します※例_4.01', format="%.2f", min_value=0.0, step=0.01)
checkinDate = st.sidebar.date_input('チェックイン日')
checkoutDate = st.sidebar.date_input('チェックアウト日')

if st.sidebar.button('すべてを入力して実行'):
    if checkinDate and checkoutDate and input_score is not None:
        # 何らかの処理を実行
        st.write("入力されたスコア:", input_score)
        st.write("チェックイン日:", checkinDate.strftime('%Y-%m-%d'))
        st.write("チェックアウト日:", checkoutDate.strftime('%Y-%m-%d'))
    else:
        st.sidebar.error('すべての項目を入力してください')

REQUEST_URL = "https://app.rakuten.co.jp/services/api/Travel/SimpleHotelSearch/20170426?"

params = {
    'format':'json',
    'largeClassCode': 'japan',
    'middleClassCode': 'kumamoto',
    'smallClassCode': 'kumamoto',
    'checkinDate': checkinDate,
    'checkoutDate': checkoutDate,
    'applicationId': APP_ID    
}

res = requests.get(REQUEST_URL, params)

result = res.json()

len(result['hotels'])

df = pd.DataFrame()

for i in range(0,len(result['hotels'])):
    hotel_info = result['hotels'][i]['hotel'][0]['hotelBasicInfo'] 
    temp_df = pd.DataFrame(hotel_info,index=[i]) 
    df = pd.concat([df,temp_df])

df2 = df[ df['reviewAverage'] > float(input_score)]

latitude_list = [] 
longtude_list = []

name_list = df2["hotelName"].values.tolist() 
df2 = df2.reset_index(drop=True)

# postalCode, address1, address2 のデータを結合して hotel_locate カラムに設定
df2['hotel_locate'] = "〒" + df2['postalCode'] + df2['address1'] + df2['address2']

url = "https://msearch.gsi.go.jp/address-search/AddressSearch?q=" # パラメータ付URLをアクセス先としてurlに代入

# dfの住所0-34番目を取り出すためのindexをiに代入
for i in range(0,len(df2)):

    q = df2["hotel_locate"][i][9:] # i番目ホテル住所を指定し、[9:]で住所のみ抽出し、qに代入
    res = requests.get(url + q) # パラメータに住所を足し算して、パラメータ付URLを完成させて、リクエストし、結果をresに代入

    latitude_list.append(res.json()[0]["geometry"]["coordinates"][1]) # APIから取得した緯度をlatitude_listに追加
    longtude_list.append(res.json()[0]["geometry"]["coordinates"][0]) # APIから取得した経度をlongtude_listに追加

df2['latitude'] = latitude_list
df2['longitude'] = longtude_list

#ここでdf2のカラムからテーブルに表示したいカラムのみをdf3にいれる
selected_columns = ['hotelNo', 'hotelName', 'reviewAverage', 'reviewCount', 'hotel_locate', 'hotelMinCharge', 'hotelInformationUrl']
df3 = df2[selected_columns]

# Streamlitを使用してデータフレームを表示
st.dataframe(df2)

def app():
    st.title("ホテルの位置情報")
    
    # 緯度と経度だけを抽出
    map_data = df2[["latitude", "longitude"]]
    
    # マップにデータを表示
    st.map(map_data)

    # テーブルとしてもデータを表示
    st.write("ホテルの詳細情報")
    st.dataframe(df3)

# Streamlitアプリケーションを実行
if __name__ == '__main__':
    app()