import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st

def create_time_series_plot(df: pd.DataFrame, column: str, title: str = None):
    """時系列グラフを作成する関数"""
    fig = px.line(df, y=column, title=title or f"{column}の時系列推移")
    fig.update_layout(
        xaxis_title="日付",
        yaxis_title=column,
        template="plotly_white"
    )
    return fig

def create_correlation_heatmap(df: pd.DataFrame):
    """相関マトリックスのヒートマップを作成する関数"""
    corr = df.corr()
    fig = px.imshow(
        corr,
        color_continuous_scale="RdBu",
        aspect="auto",
        title="相関マトリックス"
    )
    fig.update_layout(
        template="plotly_white"
    )
    return fig

def create_bar_chart(df: pd.DataFrame, x: str, y: str, title: str = None):
    """棒グラフを作成する関数"""
    fig = px.bar(df, x=x, y=y, title=title or f"{x}と{y}の関係")
    fig.update_layout(
        xaxis_title=x,
        yaxis_title=y,
        template="plotly_white"
    )
    return fig

def create_scatter_plot(df: pd.DataFrame, x: str, y: str, title: str = None):
    """散布図を作成する関数"""
    fig = px.scatter(df, x=x, y=y, title=title or f"{x}と{y}の散布図")
    fig.update_layout(
        xaxis_title=x,
        yaxis_title=y,
        template="plotly_white"
    )
    return fig

def calculate_population_and_voting_power(df_list):
    """複数の自治体の人口構成比と投票動向比率を計算する関数"""
    try:
        # df_listがDataFrameの場合はリストに変換
        if isinstance(df_list, pd.DataFrame):
            df_list = [df_list]
        
        # 結果を格納するリスト
        results = []
        
        # 年齢区分の定義
        age_groups = {
            '20歳未満': ['人.1', '人.2', '人.3', '人.4'],
            '30代': ['人.7', '人.8'],
            '40代': ['人.9', '人.10'],
            '50代': ['人.11', '人.12'],
            '60代': ['人.13', '人.14'],
            '70歳以上': ['人.15', '人.16', '人.17', '人.18', '人.19', '人.20', '人.21']
        }
        
        # 投票率の定義
        voting_rates = {
            '20歳未満': 0.0,
            '30代': 0.44,
            '40代': 0.53,
            '50代': 0.63,
            '60代': 0.72,
            '70歳以上': 0.60
        }
        
        # 年齢区分の順序
        age_order = ['20歳未満', '30代', '40代', '50代', '60代', '70歳以上']
        
        for df in df_list:
            if not isinstance(df, pd.DataFrame) or df.empty:
                continue
                
            # 市区町村名を取得
            city_name = str(df['市区町村名'].iloc[0])
            
            # 年齢区分ごとの集計
            total_pop = 0
            age_populations = {}
            
            # 人口を集計
            for age in age_order:
                columns = age_groups[age]
                pop = sum(float(df[col].iloc[0]) for col in columns if col in df.columns)
                age_populations[age] = pop
                total_pop += pop
            
            # 比率と投票影響度を計算
            if total_pop > 0:
                for age in age_order:
                    pop = age_populations[age]
                    ratio = (pop / total_pop) * 100
                    voting_power = ratio * voting_rates[age]
                    
                    results.append({
                        '自治体': city_name,
                        '年齢区分': age,
                        '人口構成比': ratio,
                        '投票影響度': voting_power
                    })
        
        # 結果をデータフレームに変換
        if not results:
            return pd.DataFrame(columns=['自治体', '年齢区分', '人口構成比', '投票影響度'])
        
        df_result = pd.DataFrame(results)
        
        # データ型を明示的に変換
        df_result['自治体'] = df_result['自治体'].astype(str)
        df_result['年齢区分'] = df_result['年齢区分'].astype(str)
        df_result['人口構成比'] = pd.to_numeric(df_result['人口構成比'], errors='coerce')
        df_result['投票影響度'] = pd.to_numeric(df_result['投票影響度'], errors='coerce')
        
        return df_result
        
    except Exception as e:
        print(f"データ処理エラー: {str(e)}")
        return pd.DataFrame(columns=['自治体', '年齢区分', '人口構成比', '投票影響度'])

def plot_population_and_voting_power(df):
    """人口構成比と投票影響度を棒グラフで表示する関数"""
    try:
        if df.empty:
            return None
            
        # 年齢区分の順序
        age_order = ['20歳未満', '30代', '40代', '50代', '60代', '70歳以上']
        
        # グラフの作成
        fig = go.Figure()
        
        # 人口構成比のグラフ（左側）
        for age in age_order:
            age_data = df[df['年齢区分'] == age].copy()
            age_data['人口構成比'] = pd.to_numeric(age_data['人口構成比'], errors='coerce')
            
            fig.add_trace(go.Bar(
                name=age,
                x=[f"{mun}\n(人口構成比)" for mun in age_data['自治体']],
                y=age_data['人口構成比'],
                text=[f'{v:.1f}%' for v in age_data['人口構成比']],
                textposition='auto',
                offsetgroup=0
            ))
        
        # 投票影響度のグラフ（右側）
        for age in age_order:
            age_data = df[df['年齢区分'] == age].copy()
            age_data['投票影響度'] = pd.to_numeric(age_data['投票影響度'], errors='coerce')
            
            fig.add_trace(go.Bar(
                name=age,
                x=[f"{mun}\n(投票影響度)" for mun in age_data['自治体']],
                y=age_data['投票影響度'],
                text=[f'{v:.1f}%' for v in age_data['投票影響度']],
                textposition='auto',
                offsetgroup=1
            ))
        
        # レイアウトの設定
        fig.update_layout(
            barmode='stack',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            height=500
        )
        
        return fig
        
    except Exception as e:
        print(f"グラフ作成エラー: {str(e)}")
        return None

def create_voting_power_chart(df_list):
    """投票動向と人口構成の比較グラフを作成する関数"""
    try:
        import plotly.graph_objects as go
        
        # 年齢区分の定義
        age_groups = {
            '20代': ['人.5', '人.6'],
            '30代': ['人.7', '人.8'],
            '40代': ['人.9', '人.10'],
            '50代': ['人.11', '人.12'],
            '60代': ['人.13', '人.14'],
            '70歳以上': ['人.15', '人.16', '人.17', '人.18', '人.19', '人.20', '人.21']
        }
        
        # 投票率の定義
        voting_rates = {
            '20代': 0.35,
            '30代': 0.44,
            '40代': 0.53,
            '50代': 0.63,
            '60代': 0.72,
            '70歳以上': 0.60
        }
        
        # 年齢区分の順序（若者から高齢者の順）
        age_order = ['20代', '30代', '40代', '50代', '60代', '70歳以上']
        
        # データの集計
        result_data = []
        municipality_names = {}  # コードから区町村名を逆引きするための辞書
        
        for _, row in df_list.iterrows():
            code = str(row['団体コード'])  # コードを文字列として扱う
            municipality = row['市区町村名']
            municipality_names[code] = municipality
            
            # デバッグ出力
            print(f"\n=== 処理中の自治体: {municipality} (コード: {code}) ===")
            
            # 20歳以上の総人口を計算
            total_pop = 0
            for age_cols in age_groups.values():
                for col in age_cols:
                    try:
                        value = float(row[col])
                        total_pop += value
                    except (ValueError, TypeError) as e:
                        print(f"エラー - {code} の {col}: {row[col]}, エラー: {str(e)}")
            
            print(f"総人口: {total_pop}")
            
            if total_pop == 0:
                print(f"警告: {code} の総人口が0です")
                continue
            
            # 各自治体の投票影響度の合計を計算するための一時データ
            municipality_voting_power = []
            
            for age_group in age_order:
                try:
                    # 人を計算
                    population = sum(float(row[col]) for col in age_groups[age_group])
                    # 構成比を計算
                    ratio = (population / total_pop * 100) if total_pop > 0 else 0
                    # 投票影響度を計算（一時保存）
                    voting_power = ratio * voting_rates[age_group]
                    municipality_voting_power.append(voting_power)
                    
                    print(f"{age_group} - 人口: {population}, 構成比: {ratio:.1f}%, 投票影響度: {voting_power:.1f}")
                except Exception as e:
                    print(f"エラー - {code} の {age_group} 処理中: {str(e)}")
            
            # 投票影響度の合計を計算
            total_voting_power = sum(municipality_voting_power)
            print(f"投票影響度合計: {total_voting_power}")
            
            # データを正規化して保存
            for age_group, voting_power in zip(age_order, municipality_voting_power):
                try:
                    population = sum(float(row[col]) for col in age_groups[age_group])
                    ratio = (population / total_pop * 100) if total_pop > 0 else 0
                    # 投票影響度を100%に正規化
                    normalized_voting_power = (voting_power / total_voting_power * 100) if total_voting_power > 0 else 0
                    
                    result_data.append({
                        '団体コード': code,
                        '市区町村名': municipality,
                        '年齢区分': age_group,
                        '人口構成比': ratio,
                        '投票影響度': normalized_voting_power
                    })
                    
                    print(f"{age_group} - 正規化後の投票影響度: {normalized_voting_power:.1f}%")
                except Exception as e:
                    print(f"エラー - {code} の {age_group} 正規化中: {str(e)}")
        
        # DataFrameに変換
        result_df = pd.DataFrame(result_data)
        
        # グラフの作成
        fig = go.Figure()
        
        # カラーマップの定義
        colors = {
            '20代': '#FFD700',      # 黄色
            '30代': '#FF7F00',      # オレンジ
            '40代': '#9370DB',      # 紫
            '50代': '#FF4500',      # 赤
            '60代': '#98FB98',      # 薄緑
            '70歳以上': '#20B2AA'    # ターコイズ
        }
        
        # x軸のラベルを作成（自治体ごとに人口構成比と投票影響度を並る）
        x_labels = []
        codes = sorted(municipality_names.keys())
        for code in codes:
            x_labels.extend([f"{municipality_names[code]}\n(人口構成比)", f"{municipality_names[code]}\n(投票影響度)"])
        
        # 年齢区分ごとにデータを追加
        for age in age_order:
            age_data = result_df[result_df['年齢区分'] == age]
            y_values = []
            text_values = []
            
            # 自治体ごとに人口構成比と投票影響度のデータを交互に配置
            for code in codes:
                mun_data = age_data[age_data['団体コード'] == code]
                if not mun_data.empty:
                    y_values.extend([
                        mun_data['人口構成比'].values[0],
                        mun_data['投票影響度'].values[0]
                    ])
                    text_values.extend([
                        f'{mun_data["人口構成比"].values[0]:.1f}%',
                        f'{mun_data["投票影響度"].values[0]:.1f}%'
                    ])
                else:
                    print(f"警告: {code} ({municipality_names.get(code, '不明')}) の {age} のデータが見つかりません")
                    y_values.extend([0, 0])
                    text_values.extend(['0.0%', '0.0%'])
            
            fig.add_trace(go.Bar(
                name=f"{age}",
                x=x_labels,
                y=y_values,
                text=text_values,
                textposition='auto',
                marker_color=colors[age],
                showlegend=True
            ))
        
        # レイアウトの設定
        fig.update_layout(
            title='年齢区分別の人口構成比と投票影響度（20歳以上）',
            barmode='stack',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            height=500,
            yaxis_title='割合 (%)',
            yaxis={'range': [0, 100]},
            margin=dict(t=100)
        )
        
        return fig
        
    except Exception as e:
        print(f"グラフ作成エラー: {str(e)}")
        return None

def display_age_analysis(df: pd.DataFrame, prefecture: str):
    """年齢構成分析を表示する関数"""
    st.header("年齢構成分析")
    
    # 年齢区分の定義
    age_groups = {
        '20歳未満': ['0歳～4歳', '5歳～9歳', '10歳～14歳', '15歳～19歳'],
        '30代': ['30歳～34歳', '35歳～39歳'],
        '40代': ['40歳～44歳', '45歳～49歳'],
        '50代': ['50歳～54歳', '55歳～59歳'],
        '60代': ['60歳～64歳', '65歳～69歳'],
        '70歳以上': ['70歳～74歳', '75歳～79歳', '80歳～84歳', '85歳～89歳', '90歳～94歳', '95歳～99歳', '100歳以上']
    }
    
    # 年齢区分ごとの人口を計算
    results = []
    for _, row in df.iterrows():
        city_name = row['市区町村名']
        total_pop = float(row['総数'])
        
        for group, columns in age_groups.items():
            population = sum(float(row[col]) for col in columns)
            ratio = (population / total_pop * 100) if total_pop > 0 else 0
            results.append({
                '市区町村名': city_name,
                '年齢区分': group,
                '人口': population,
                '構成比': ratio
            })
    
    age_df = pd.DataFrame(results)
    
    # グラフの作成
    fig = px.bar(
        age_df,
        x='市区町村名',
        y='構成比',
        color='年齢区分',
        title=f'{prefecture}の年齢構成比率',
        labels={'構成比': '構成比率 (%)', '市区町村名': '市区町村'},
        height=600,  # 高さを600pxに変更
        text=age_df['構成比'].apply(lambda x: f'{x:.1f}%')  # パーセント表示を追加
    )
    
    fig.update_layout(
        barmode='stack',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        yaxis={'range': [0, 100]},
        margin=dict(t=100, b=50),  # 上下のマージンを調整
        uniformtext_minsize=8,  # テキストの最小サイズ
        uniformtext_mode='hide'  # 小さすぎるテキストは非表示
    )
    
    # テキストの位置を調整
    fig.update_traces(
        textposition='auto',
        textangle=0,
        texttemplate='%{text}'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # データテーブルの表示
    if st.checkbox('詳細データを表示'):
        st.dataframe(
            age_df.pivot(
                index='市区町村名',
                columns='年齢区分',
                values=['人口', '構成比']
            ).style.format({
                ('人口', ''): '{:,.0f}',
                ('構成比', ''): '{:.1f}%'
            })
        )

def display_voting_trend(df: pd.DataFrame, prefecture: str):
    """投票傾向分析を表示する関数"""
    st.header("投票傾向分析")
    
    # 投票率の定義
    voting_rates = {
        '20代': 0.35,
        '30代': 0.44,
        '40代': 0.53,
        '50代': 0.63,
        '60代': 0.72,
        '70歳以上': 0.60
    }
    
    # 年齢区分の定義
    age_groups = {
        '20代': ['20歳～24歳', '25歳～29歳'],
        '30代': ['30歳～34歳', '35歳～39歳'],
        '40代': ['40歳～44歳', '45歳～49歳'],
        '50代': ['50歳～54歳', '55歳～59歳'],
        '60代': ['60歳～64歳', '65歳～69歳'],
        '70歳以上': ['70歳～74歳', '75歳～79歳', '80歳～84歳', '85歳～89歳', '90歳～94歳', '95歳～99歳', '100歳以上']
    }
    
    # 投票影響度を計算
    results = []
    for _, row in df.iterrows():
        city_name = row['市区町村名']
        total_pop = sum(sum(float(row[col]) for col in cols) for cols in age_groups.values())
        
        for group, columns in age_groups.items():
            population = sum(float(row[col]) for col in columns)
            ratio = (population / total_pop * 100) if total_pop > 0 else 0
            voting_power = ratio * voting_rates[group]
            
            results.append({
                '市区町村名': city_name,
                '年齢区分': group,
                '人口構成比': ratio,
                '投票影響度': voting_power
            })
    
    voting_df = pd.DataFrame(results)
    
    # 投票影響度を100%に正規化
    for city in voting_df['市区町村名'].unique():
        city_mask = voting_df['市区町村名'] == city
        total_power = voting_df.loc[city_mask, '投票影響度'].sum()
        if total_power > 0:
            voting_df.loc[city_mask, '投票影響度'] = voting_df.loc[city_mask, '投票影響度'] / total_power * 100
    
    # グラフの作成
    fig = go.Figure()
    
    # カラーマップの定義
    colors = {
        '20代': '#FFD700',      # 黄色
        '30代': '#FF7F00',      # オレンジ
        '40代': '#9370DB',      # 紫
        '50代': '#FF4500',      # 赤
        '60代': '#98FB98',      # 薄緑
        '70歳以上': '#20B2AA'    # ターコイズ
    }
    
    # x軸のラベルを作成
    cities = sorted(voting_df['市区町村名'].unique())
    x_labels = []
    for city in cities:
        x_labels.extend([f"{city}\n(人口構成比)", f"{city}\n(投票影響度)"])
    
    # 年齢区分ごとにデータを追加
    for age in age_groups.keys():
        age_data = voting_df[voting_df['年齢区分'] == age]
        y_values = []
        text_values = []
        
        for city in cities:
            city_data = age_data[age_data['市区町村名'] == city]
            if not city_data.empty:
                y_values.extend([
                    city_data['人口構成比'].values[0],
                    city_data['投票影響度'].values[0]
                ])
                text_values.extend([
                    f'{city_data["人口構成比"].values[0]:.1f}%',
                    f'{city_data["投票影響度"].values[0]:.1f}%'
                ])
            else:
                y_values.extend([0, 0])
                text_values.extend(['0.0%', '0.0%'])
        
        fig.add_trace(go.Bar(
            name=age,
            x=x_labels,
            y=y_values,
            text=text_values,
            textposition='auto',
            marker_color=colors[age]
        ))
    
    # レイアウトの設定
    fig.update_layout(
        title='年齢区分別の人口構成比と投票影響度',
        barmode='stack',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=600,
        yaxis_title='割合 (%)',
        yaxis={'range': [0, 100]},
        margin=dict(t=100, b=50)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 説明を追加
    st.markdown("""
    **グラフの見方：**
    - 左側の棒グラフは各年齢区分の人口構成比を示しています
    - 右側の棒グラフは投票率を加味した実際の投票影響度を示しています
    - 投票影響度は、人口構成比に各年齢区分の平均投票率を掛けて算出しています
    """)
    
    # データテーブルの表示
    if st.checkbox('投票傾向の詳細データを表示'):
        st.dataframe(
            voting_df.pivot(
                index='市区町村名',
                columns='年齢区分',
                values=['人口構成比', '投票影響度']
            ).style.format('{:.1f}%')
        )