# -*- coding: utf-8 -*-
"""
出力・エクスポートユーティリティ
SEM Particle Analyzer用のデータ出力関数
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import io
import base64
from datetime import datetime
from typing import Dict, List, Any, Optional
import streamlit as st

def create_csv_download(df: pd.DataFrame, filename: str = "particle_analysis") -> bytes:
    """
    CSVダウンロード用のバイト列を作成
    
    Args:
        df: 出力するDataFrame
        filename: ファイル名（拡張子なし）
        
    Returns:
        CSVのバイト列
    """
    # CSVに変換
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')  # BOM付きUTF-8
    csv_string = csv_buffer.getvalue()
    
    return csv_string.encode('utf-8-sig')

def create_histogram_plot(data: Dict[str, List[float]], 
                         language: str = "ja",
                         scale_type: str = "linear") -> go.Figure:
    """
    粒径ヒストグラムのプロットを作成
    
    Args:
        data: 粒径データの辞書
        language: 言語設定
        scale_type: スケールタイプ ("linear" or "log")
        
    Returns:
        Plotlyの図
    """
    from config.languages import get_text
    
    # サブプロット作成
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            get_text("short_axis", language),
            get_text("long_axis", language),
            get_text("mean_diameter", language),
            get_text("equivalent_diameter", language)
        ]
    )
    
    # データキーとプロット位置のマッピング
    plot_mapping = [
        ("short_axis_um", 1, 1),
        ("long_axis_um", 1, 2),
        ("mean_diameter_um", 2, 1),
        ("equivalent_diameter_um", 2, 2)
    ]
    
    for key, row, col in plot_mapping:
        if key in data and data[key]:
            values = data[key]
            
            if scale_type == "log":
                # 対数スケール
                positive_values = [v for v in values if v > 0]
                if positive_values:
                    fig.add_trace(
                        go.Histogram(
                            x=positive_values,
                            name=get_text(key.replace("_um", ""), language),
                            xbins=dict(
                                start=np.log10(min(positive_values)),
                                end=np.log10(max(positive_values)),
                                size=(np.log10(max(positive_values)) - np.log10(min(positive_values))) / 30
                            ),
                            showlegend=False
                        ),
                        row=row, col=col
                    )
                    fig.update_xaxes(type="log", row=row, col=col)
            else:
                # 線形スケール
                fig.add_trace(
                    go.Histogram(
                        x=values,
                        name=get_text(key.replace("_um", ""), language),
                        nbinsx=30,
                        showlegend=False
                    ),
                    row=row, col=col
                )
    
    # レイアウト更新
    fig.update_layout(
        title=f"{get_text('histogram', language)} ({get_text(f'{scale_type}_scale', language)})",
        height=600,
        showlegend=False
    )
    
    # 軸ラベル
    for i in range(1, 3):
        for j in range(1, 3):
            fig.update_xaxes(title_text=f"{get_text('unit_um', language)}", row=i, col=j)
            fig.update_yaxes(title_text=get_text("count", language), row=i, col=j)
    
    return fig

def create_statistics_table(stats_data: Dict[str, Dict[str, float]], 
                           language: str = "ja") -> pd.DataFrame:
    """
    統計情報テーブルを作成
    
    Args:
        stats_data: 統計データ
        language: 言語設定
        
    Returns:
        統計情報のDataFrame
    """
    from config.languages import get_text
    
    # 統計項目の翻訳
    stat_translations = {
        "count": get_text("particle_count", language),
        "mean": get_text("mean", language) if language == "en" else "平均",
        "std": get_text("std", language) if language == "en" else "標準偏差",
        "geometric_mean": get_text("geometric_mean", language),
        "geometric_std": get_text("geometric_std", language),
        "min": get_text("min", language) if language == "en" else "最小値",
        "max": get_text("max", language) if language == "en" else "最大値",
        "median": get_text("median", language) if language == "en" else "中央値",
        "d10": "D10",
        "d50": "D50",
        "d90": "D90"
    }
    
    # サイズメトリクスの翻訳
    size_translations = {
        "short_axis_um": get_text("short_axis", language),
        "long_axis_um": get_text("long_axis", language),
        "mean_diameter_um": get_text("mean_diameter", language),
        "equivalent_diameter_um": get_text("equivalent_diameter", language)
    }
    
    # テーブル作成
    table_data = []
    
    for size_metric, size_name in size_translations.items():
        if size_metric in stats_data:
            stats = stats_data[size_metric]
            row = {"サイズメトリクス" if language == "ja" else "Size Metric": size_name}
            
            for stat_key, stat_name in stat_translations.items():
                if stat_key in stats:
                    value = stats[stat_key]
                    if stat_key == "count":
                        row[stat_name] = f"{int(value)}"
                    else:
                        row[stat_name] = f"{value:.3f}"
                else:
                    row[stat_name] = "-"
            
            table_data.append(row)
    
    return pd.DataFrame(table_data)

def create_html_report(particles_df: pd.DataFrame,
                      stats_data: Dict[str, Dict[str, float]],
                      histogram_fig: go.Figure,
                      analysis_params: Dict[str, Any],
                      language: str = "ja") -> str:
    """
    HTMLレポートを作成
    
    Args:
        particles_df: 粒子データ
        stats_data: 統計データ
        histogram_fig: ヒストグラム図
        analysis_params: 解析パラメータ
        language: 言語設定
        
    Returns:
        HTMLレポート文字列
    """
    from config.languages import get_text
    
    # ヒストグラムをHTMLに変換
    histogram_html = histogram_fig.to_html(include_plotlyjs='cdn')
    
    # 統計テーブル
    stats_table = create_statistics_table(stats_data, language)
    stats_html = stats_table.to_html(index=False, escape=False)
    
    # 現在時刻
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # HTMLテンプレート
    html_template = f"""
    <!DOCTYPE html>
    <html lang="{language}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{get_text('app_title', language)} - {get_text('download_report', language)}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                line-height: 1.6;
            }}
            .header {{
                text-align: center;
                border-bottom: 2px solid #333;
                padding-bottom: 20px;
                margin-bottom: 30px;
            }}
            .section {{
                margin-bottom: 30px;
            }}
            .section h2 {{
                color: #333;
                border-bottom: 1px solid #ccc;
                padding-bottom: 10px;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin-bottom: 20px;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
                font-weight: bold;
            }}
            .params {{
                background-color: #f9f9f9;
                padding: 15px;
                border-radius: 5px;
            }}
            .params ul {{
                margin: 0;
                padding-left: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{get_text('app_title', language)}</h1>
            <h2>{get_text('download_report', language)}</h2>
            <p>{get_text('generated', language) if language == 'en' else '生成日時'}: {current_time}</p>
        </div>
        
        <div class="section">
            <h2>{get_text('analysis_params', language) if language == 'en' else '解析パラメータ'}</h2>
            <div class="params">
                <ul>
                    <li>{get_text('particle_count', language)}: {len(particles_df)}</li>
                    <li>{get_text('scale_setting', language)}: {analysis_params.get('pixels_per_um', 'N/A')} {get_text('pixels_per_um', language)}</li>
                    <li>{get_text('threshold_method', language)}: {analysis_params.get('threshold_method', 'N/A')}</li>
                    <li>{get_text('min_area', language)}: {analysis_params.get('min_area', 'N/A')} {get_text('unit_pixels', language)}</li>
                    <li>{get_text('min_circularity', language)}: {analysis_params.get('min_circularity', 'N/A')}</li>
                </ul>
            </div>
        </div>
        
        <div class="section">
            <h2>{get_text('statistics', language)}</h2>
            {stats_html}
        </div>
        
        <div class="section">
            <h2>{get_text('histogram', language)}</h2>
            {histogram_html}
        </div>
        
        <div class="section">
            <h2>{get_text('particle_data', language) if language == 'en' else '粒子データ'}</h2>
            <p>{get_text('total_particles', language) if language == 'en' else '総粒子数'}: {len(particles_df)}</p>
            {particles_df.head(100).to_html(index=False, escape=False)}
            {f'<p>{get_text("showing_first_100", language) if language == "en" else "最初の100個を表示"}</p>' if len(particles_df) > 100 else ''}
        </div>
    </body>
    </html>
    """
    
    return html_template

def create_summary_plot(stats_data: Dict[str, Dict[str, float]], 
                       language: str = "ja") -> go.Figure:
    """
    サマリープロットを作成
    
    Args:
        stats_data: 統計データ
        language: 言語設定
        
    Returns:
        Plotlyの図
    """
    from config.languages import get_text
    
    # データ準備
    size_metrics = []
    means = []
    stds = []
    geometric_means = []
    geometric_stds = []
    
    size_translations = {
        "short_axis_um": get_text("short_axis", language),
        "long_axis_um": get_text("long_axis", language),
        "mean_diameter_um": get_text("mean_diameter", language),
        "equivalent_diameter_um": get_text("equivalent_diameter", language)
    }
    
    for metric, name in size_translations.items():
        if metric in stats_data:
            stats = stats_data[metric]
            size_metrics.append(name)
            means.append(stats.get("mean", 0))
            stds.append(stats.get("std", 0))
            geometric_means.append(stats.get("geometric_mean", 0))
            geometric_stds.append(stats.get("geometric_std", 0))
    
    # サブプロット作成
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=[
            f"{get_text('mean', language) if language == 'en' else '算術平均'} ± {get_text('std', language) if language == 'en' else '標準偏差'}",
            f"{get_text('geometric_mean', language)} ± {get_text('geometric_std', language)}"
        ]
    )
    
    # 算術平均のプロット
    fig.add_trace(
        go.Bar(
            x=size_metrics,
            y=means,
            error_y=dict(type='data', array=stds),
            name=get_text('mean', language) if language == 'en' else '算術平均',
            showlegend=False
        ),
        row=1, col=1
    )
    
    # 幾何平均のプロット
    fig.add_trace(
        go.Bar(
            x=size_metrics,
            y=geometric_means,
            error_y=dict(type='data', array=[g-1 for g in geometric_stds]),  # 幾何標準偏差の表示調整
            name=get_text('geometric_mean', language),
            showlegend=False
        ),
        row=1, col=2
    )
    
    # レイアウト更新
    fig.update_layout(
        title=get_text('statistics', language),
        height=400
    )
    
    # 軸ラベル
    fig.update_yaxes(title_text=f"{get_text('unit_um', language)}", row=1, col=1)
    fig.update_yaxes(title_text=f"{get_text('unit_um', language)}", row=1, col=2)
    
    return fig

def save_analysis_results(particles_df: pd.DataFrame,
                         stats_data: Dict[str, Dict[str, float]],
                         analysis_params: Dict[str, Any],
                         language: str = "ja") -> Dict[str, bytes]:
    """
    解析結果を保存用に準備
    
    Args:
        particles_df: 粒子データ
        stats_data: 統計データ
        analysis_params: 解析パラメータ
        language: 言語設定
        
    Returns:
        保存用データの辞書
    """
    results = {}
    
    # CSV
    results["csv"] = create_csv_download(particles_df)
    
    # ヒストグラム（線形）
    size_data = {
        "short_axis_um": particles_df.get("short_axis_um", []).tolist() if "short_axis_um" in particles_df.columns else [],
        "long_axis_um": particles_df.get("long_axis_um", []).tolist() if "long_axis_um" in particles_df.columns else [],
        "mean_diameter_um": particles_df.get("mean_diameter_um", []).tolist() if "mean_diameter_um" in particles_df.columns else [],
        "equivalent_diameter_um": particles_df.get("equivalent_diameter_um", []).tolist() if "equivalent_diameter_um" in particles_df.columns else []
    }
    
    histogram_fig = create_histogram_plot(size_data, language, "linear")
    
    # HTML レポート
    html_report = create_html_report(particles_df, stats_data, histogram_fig, analysis_params, language)
    results["html"] = html_report.encode('utf-8')
    
    return results