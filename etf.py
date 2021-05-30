from pandas.core.accessor import CachedAccessor
import altair as alt
import datetime as dt
import pandas as pd
from pandas_datareader import data as pdr
import streamlit as st
import yfinance as yf

# アプリタイトル設定
st.title("米国ETFトップ10株価可視化アプリ")

yf.pdr_override()

# ETF株価データを取得してDataFrameに格納するfunction
@st.cache
def get_data(_start, _end, _tickers):
    # データを格納するDataFrameを生成
    df = pd.DataFrame()
    # _tickersに格納された銘柄分ループでデータ取得
    for brand in _tickers.keys():
        data = pdr.get_data_yahoo(_tickers[brand], start=_start, end=_end)
        # ダウンロードしたデータは日付がindexになっているので、そのindexの表示形式を「dd 英語月名 YYYY」に変更する
        data.index = data.index.strftime("%d %B %Y")
        # 終値のみ取得したいのでCloseカラムのデータのみ取得する
        data = data[["Close"]]
        # 複数取得したい場合は下記の通りカンマで連結する
        # data = data[["Close", "Adj Close"]]
        # カラム名をCloseからSPY（銘柄名）へ変更する
        data.columns = [_tickers[brand]]
        # 銘柄ごとに縦に並べたいので、行と列を入れ替える
        data = data.T
        # index名にNameを追記
        data.index.name = "Name"
        # データをDataFrameに追加
        df = pd.concat([df, data])
    return df

# 学長おすすめの米国ETF銘柄
tickers = {
    "vwo": "VWO",
    "iefa": "IEFA",
    "gld": "GLD",
    "vea": "VEA",
    "agg": "AGG",
    "qqq": "QQQ",
    "vti": "VTI",
    "voo": "VOO",
    "ivv": "IVV",
    "spy": "SPY",
}
# 検索可能な日付範囲
# 最大値は当日
# date型に揃える（揃ってないとエラーとなる）
min_date = dt.datetime.strptime("2017-01-01", "%Y-%m-%d").date()
max_date = dt.date.today()

# サイドバー設定
st.sidebar.write("""
    # 米国ETF株価
    以下のオプションから表示期間を選択してください
""")

start = st.sidebar.date_input(
    "表示開始日を選択してください",
    min_date
)

end = st.sidebar.date_input(
    "表示終了日を選択してください",
    max_date
)

if start > dt.date.today():
    st.error("エラー：開始日に未来日が選択されています")

elif end > dt.date.today():
    st.error("エラー：終了日に未来日が選択されています")

elif start > end:
    st.error("エラー：終了日が開始日よりも過去日になっています")

else:
    # データ取得
    df = get_data(start, end, tickers)

    # グラフを表示する銘柄の選択
    # df.indexで銘柄名が返ってくるのでそれを配列に入れる
    brand = st.multiselect(
        "表示する銘柄を選択してください",
        list(df.index),
        # デフォルト表示（おすすめTOP5）
        ["SPY","IVV","VOO", "VTI", "QQQ"]
    )

    if not brand:
        st.error("銘柄が一つも選択されていません")
    else:
        # loc関数は単独および複数の要素の値を列名および行名で取得する関数
        print(brand)
        data =df.loc[brand]
        st.write("### 株価(USD)", data.sort_index())
        # データの日付をカラムに戻す
        data = data.T.reset_index()
        # pandasのmelt関数で、日付、銘柄名、株価、というデータに変換する
        # カラム名をStock Price(USD)とする
        data = pd.melt(data, id_vars=["Date"]).rename(
            columns={"value": "Stock Price(USD)"}
        )

        # グラフの作成
        chart = (
            alt.Chart(data)
            # clipは表外にはみ出すデータを表示しないためのプロパティ
            .mark_line(opacity=0.8, clip=True)
            .encode(
                # :Tを入れることでaltairがdateまたはtimeの値だと認識してくれる
                x = "Date:T",
                # :Qとすることで連続した数値をデータであることをaltairに伝えることが可能
                y = alt.Y("Stock Price(USD):Q", stack = None),
                # :Nとすることで不連続で順不同のデータであることをaltairに伝えることが可能
                color="Name:N"
                # この辺りの詳細：https://altair-viz.github.io/user_guide/encoding.html
            )
        )
        st.write("""
            ### チャート
        """)
        st.altair_chart(chart, use_container_width = True)
