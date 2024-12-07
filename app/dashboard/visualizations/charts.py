import plotly.graph_objects as go
import pandas as pd
from app.dashboard.utils.constants import AGE_ORDER, GRAPH_COLORS

def create_age_distribution_chart(df: pd.DataFrame, title: str = None) -> go.Figure:
    """年齢構成比のグラフを作成する関数"""
    try:
        # 市区町村のリストを取得
        municipalities = sorted(df['市区町村名'].unique())
        
        # グラフの作成
        fig = go.Figure()
        
        # 年齢区分ごとにデータを追加
        for age in AGE_ORDER:
            age_data = df[df['年齢区分'] == age]
            percentages = []
            
            for mun in municipalities:
                data = age_data[age_data['市区町村名'] == mun]
                percentage = data['構成比'].iloc[0] if not data.empty else 0
                percentages.append(percentage)
            
            fig.add_trace(go.Bar(
                name=age,
                x=municipalities,
                y=percentages,
                text=[f"{val:.1f}%" for val in percentages],
                textposition='auto',
                marker_color=GRAPH_COLORS[age]
            ))
        
        # レイアウトの設定
        fig.update_layout(
            title=title or '年齢区分別人口構成比',
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
            yaxis_title='構成比（％）',
            yaxis={'range': [0, 100]},
            xaxis_title='市区町村'
        )
        
        return fig
    
    except Exception as e:
        raise Exception(f"年齢構成比グラフの作成に失敗しました: {str(e)}")

def create_voting_power_chart(df: pd.DataFrame) -> go.Figure:
    """投票動向グラフを作成する関数"""
    try:
        # 市区町村のリストを取得
        municipalities = sorted(df['市区町村名'].unique())
        
        # グラフの作成
        fig = go.Figure()
        
        # x軸のラベルを作成
        x_labels = []
        for mun in municipalities:
            x_labels.extend([f"{mun}\n(人口構成比)", f"{mun}\n(投票影響度)"])
        
        # 年齢区分ごとにデータを追加
        for age in AGE_ORDER:
            age_data = df[df['年齢区分'] == age]
            y_values = []
            text_values = []
            
            for mun in municipalities:
                mun_data = age_data[age_data['市区町村名'] == mun]
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
                    y_values.extend([0, 0])
                    text_values.extend(['0.0%', '0.0%'])
            
            fig.add_trace(go.Bar(
                name=age,
                x=x_labels,
                y=y_values,
                text=text_values,
                textposition='auto',
                marker_color=GRAPH_COLORS[age],
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
        raise Exception(f"投票動向グラフの作成に失敗しました: {str(e)}") 