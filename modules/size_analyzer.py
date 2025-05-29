# -*- coding: utf-8 -*-
"""
粒径解析モジュール
SEM Particle Analyzer用の粒径分布解析機能
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List, Any, Optional
from config.languages import get_text
from config.settings import get_current_language, ANALYSIS_CONFIG
from utils.math_utils import (
    calculate_statistics, create_histogram_data, create_log_histogram_data,
    calculate_size_distribution_stats, fit_lognormal_distribution,
    calculate_d_values, calculate_span, create_particles_dataframe
)
from utils.export_utils import (
    create_csv_download, create_histogram_plot, create_statistics_table,
    create_html_report, save_analysis_results
)
from modules.particle_detector import get_particles_data, is_particles_detected
from modules.image_loader import get_scale_info

def render_size_analyzer():
    """粒径解析タブの描画"""
    lang = get_current_language()
    
    st.header(get_text("tab_size_analysis", lang))
    
    # 前提条件チェック
    if not is_particles_detected():
        st.warning(f"{get_text('no_particles_detected', lang) if lang == 'en' else '粒子が検出されていません。先に粒子検出を実行してください。'}")
        return
    
    particles_data = get_particles_data()
    scale_info = get_scale_info()
    
    # 粒子データをDataFrameに変換
    particles_df = create_particles_dataframe(particles_data, lang)
    
    # 解析実行・結果表示
    render_size_analysis_results(particles_df, scale_info, lang)
    
    # ダウンロードセクション
    render_download_section(particles_df, lang)

def render_size_analysis_results(particles_df: pd.DataFrame, pixels_per_um: float, lang: str):
    """粒径解析結果の表示"""
    st.subheader(get_text("size_analysis", lang))
    
    # 基本統計情報
    render_basic_statistics(particles_df, lang)
    
    # ヒストグラム表示
    render_histograms(particles_df, lang)
    
    # 詳細統計表
    render_detailed_statistics(particles_df, lang)
    
    # 分布フィッティング
    render_distribution_fitting(particles_df, lang)

def render_basic_statistics(particles_df: pd.DataFrame, lang: str):
    """基本統計情報の表示"""
    st.markdown(f"**{get_text('basic_statistics', lang) if lang == 'en' else '基本統計情報'}**")
    
    # 粒子数と基本メトリクス
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label=get_text("particle_count", lang),
            value=len(particles_df)
        )
    
    # サイズメトリクスの平均値
    size_columns = {
        "short_axis_um": get_text("short_axis", lang),
        "long_axis_um": get_text("long_axis", lang),
        "mean_diameter_um": get_text("mean_diameter", lang),
        "equivalent_diameter_um": get_text("equivalent_diameter", lang)
    }
    
    # 言語に応じたカラム名を取得
    from config.languages import get_column_names
    column_names = get_column_names(lang)
    
    # 実際のカラム名でアクセス
    actual_columns = {
        column_names["short_axis"]: get_text("short_axis", lang),
        column_names["long_axis"]: get_text("long_axis", lang),
        column_names["mean_diameter"]: get_text("mean_diameter", lang),
        column_names["equivalent_diameter"]: get_text("equivalent_diameter", lang)
    }
    
    cols = [col2, col3, col4]
    col_idx = 0
    
    for col_name, display_name in actual_columns.items():
        if col_name in particles_df.columns and col_idx < len(cols):
            mean_value = particles_df[col_name].mean()
            with cols[col_idx]:
                st.metric(
                    label=f"{display_name} (μm)",
                    value=f"{mean_value:.2f}"
                )
            col_idx += 1

def render_histograms(particles_df: pd.DataFrame, lang: str):
    """ヒストグラム表示"""
    st.markdown(f"**{get_text('histogram', lang)}**")
    
    # スケール選択
    scale_type = st.radio(
        f"{get_text('scale_type', lang) if lang == 'en' else 'スケールタイプ'}",
        options=["linear", "log"],
        format_func=lambda x: get_text(f"{x}_scale", lang),
        horizontal=True,
        key="histogram_scale_type"
    )
    
    # データ準備
    from config.languages import get_column_names
    column_names = get_column_names(lang)
    
    size_data = {}
    size_mapping = {
        "short_axis_um": column_names["short_axis"],
        "long_axis_um": column_names["long_axis"],
        "mean_diameter_um": column_names["mean_diameter"],
        "equivalent_diameter_um": column_names["equivalent_diameter"]
    }
    
    for key, col_name in size_mapping.items():
        if col_name in particles_df.columns:
            size_data[key] = particles_df[col_name].tolist()
    
    # ヒストグラム作成
    if size_data:
        fig = create_histogram_plot(size_data, lang, scale_type)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"{get_text('no_data_available', lang) if lang == 'en' else 'データが利用できません'}")

def render_detailed_statistics(particles_df: pd.DataFrame, lang: str):
    """詳細統計表の表示"""
    st.markdown(f"**{get_text('detailed_statistics', lang) if lang == 'en' else '詳細統計'}**")
    
    # 統計データを計算
    from config.languages import get_column_names
    column_names = get_column_names(lang)
    
    stats_data = {}
    size_mapping = {
        "short_axis_um": column_names["short_axis"],
        "long_axis_um": column_names["long_axis"],
        "mean_diameter_um": column_names["mean_diameter"],
        "equivalent_diameter_um": column_names["equivalent_diameter"]
    }
    
    for key, col_name in size_mapping.items():
        if col_name in particles_df.columns:
            data = particles_df[col_name].tolist()
            stats_data[key] = calculate_statistics(data)
            
            # D値を追加
            d_values = calculate_d_values(data)
            stats_data[key].update(d_values)
            
            # スパン値を追加
            span = calculate_span(d_values)
            stats_data[key]["span"] = span
    
    # 統計テーブルを作成・表示
    if stats_data:
        stats_table = create_statistics_table(stats_data, lang)
        st.dataframe(stats_table, use_container_width=True)
        
        # 解析結果をセッションに保存
        st.session_state.analysis_results = stats_data
    else:
        st.warning(f"{get_text('no_data_available', lang) if lang == 'en' else 'データが利用できません'}")

def render_distribution_fitting(particles_df: pd.DataFrame, lang: str):
    """分布フィッティングの表示"""
    with st.expander(f"{get_text('distribution_fitting', lang) if lang == 'en' else '分布フィッティング'}"):
        
        # フィッティング対象の選択
        from config.languages import get_column_names
        column_names = get_column_names(lang)
        
        available_columns = []
        display_names = []
        
        size_mapping = {
            column_names["short_axis"]: get_text("short_axis", lang),
            column_names["long_axis"]: get_text("long_axis", lang),
            column_names["mean_diameter"]: get_text("mean_diameter", lang),
            column_names["equivalent_diameter"]: get_text("equivalent_diameter", lang)
        }
        
        for col_name, display_name in size_mapping.items():
            if col_name in particles_df.columns:
                available_columns.append(col_name)
                display_names.append(display_name)
        
        if available_columns:
            selected_column = st.selectbox(
                f"{get_text('select_size_metric', lang) if lang == 'en' else 'サイズメトリクスを選択'}",
                options=available_columns,
                format_func=lambda x: size_mapping[x],
                key="fitting_column_select"
            )
            
            # 対数正規分布フィッティング
            data = particles_df[selected_column].tolist()
            fitting_results = fit_lognormal_distribution(data)
            
            if fitting_results:
                st.markdown(f"**{get_text('lognormal_fitting', lang) if lang == 'en' else '対数正規分布フィッティング'}**")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        label=f"{get_text('fitted_mean', lang) if lang == 'en' else 'フィッティング平均'}",
                        value=f"{fitting_results['mean']:.3f}"
                    )
                    st.metric(
                        label=f"{get_text('fitted_std', lang) if lang == 'en' else 'フィッティング標準偏差'}",
                        value=f"{fitting_results['std']:.3f}"
                    )
                
                with col2:
                    st.metric(
                        label=f"{get_text('fitted_median', lang) if lang == 'en' else 'フィッティング中央値'}",
                        value=f"{fitting_results['median']:.3f}"
                    )
                    st.metric(
                        label="R²",
                        value=f"{fitting_results['r_squared']:.3f}"
                    )
                
                with col3:
                    st.metric(
                        label="Shape",
                        value=f"{fitting_results['shape']:.3f}"
                    )
                    st.metric(
                        label="Scale",
                        value=f"{fitting_results['scale']:.3f}"
                    )
                
                # フィッティング結果のプロット
                render_fitting_plot(data, fitting_results, size_mapping[selected_column], lang)
            else:
                st.warning(f"{get_text('fitting_failed', lang) if lang == 'en' else 'フィッティングに失敗しました'}")

def render_fitting_plot(data: List[float], fitting_results: Dict[str, float], metric_name: str, lang: str):
    """フィッティング結果のプロット"""
    from scipy import stats
    
    # ヒストグラムとフィッティング曲線
    fig = go.Figure()
    
    # ヒストグラム
    fig.add_trace(go.Histogram(
        x=data,
        nbinsx=30,
        name=f"{get_text('observed', lang) if lang == 'en' else '観測値'}",
        opacity=0.7,
        histnorm='probability density'
    ))
    
    # フィッティング曲線
    x_range = np.linspace(min(data), max(data), 100)
    fitted_pdf = stats.lognorm.pdf(
        x_range, 
        fitting_results['shape'], 
        fitting_results['loc'], 
        fitting_results['scale']
    )
    
    fig.add_trace(go.Scatter(
        x=x_range,
        y=fitted_pdf,
        mode='lines',
        name=f"{get_text('lognormal_fit', lang) if lang == 'en' else '対数正規分布フィット'}",
        line=dict(color='red', width=2)
    ))
    
    fig.update_layout(
        title=f"{get_text('distribution_fitting', lang) if lang == 'en' else '分布フィッティング'} - {metric_name}",
        xaxis_title=f"{metric_name} (μm)",
        yaxis_title=f"{get_text('probability_density', lang) if lang == 'en' else '確率密度'}",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_download_section(particles_df: pd.DataFrame, lang: str):
    """ダウンロードセクション"""
    st.subheader(get_text("download_section", lang) if lang == "en" else "ダウンロード")
    
    col1, col2, col3 = st.columns(3)
    
    # CSV ダウンロード
    with col1:
        if st.button(get_text("download_csv", lang), use_container_width=True):
            csv_data = create_csv_download(particles_df, "particle_analysis")
            st.download_button(
                label=get_text("download_csv", lang),
                data=csv_data,
                file_name=f"particle_analysis_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                key="csv_download"
            )
    
    # 画像ダウンロード
    with col2:
        if st.button(get_text("download_image", lang), use_container_width=True):
            # ヒストグラム画像を生成
            from config.languages import get_column_names
            column_names = get_column_names(lang)
            
            size_data = {}
            size_mapping = {
                "short_axis_um": column_names["short_axis"],
                "long_axis_um": column_names["long_axis"],
                "mean_diameter_um": column_names["mean_diameter"],
                "equivalent_diameter_um": column_names["equivalent_diameter"]
            }
            
            for key, col_name in size_mapping.items():
                if col_name in particles_df.columns:
                    size_data[key] = particles_df[col_name].tolist()
            
            if size_data:
                fig = create_histogram_plot(size_data, lang, "linear")
                img_bytes = fig.to_image(format="png", width=1200, height=800)
                
                st.download_button(
                    label=get_text("download_image", lang),
                    data=img_bytes,
                    file_name=f"histogram_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.png",
                    mime="image/png",
                    key="image_download"
                )
    
    # HTML レポートダウンロード
    with col3:
        if st.button(get_text("download_report", lang), use_container_width=True):
            # レポート生成
            stats_data = st.session_state.get("analysis_results", {})
            
            # ヒストグラム図を準備
            from config.languages import get_column_names
            column_names = get_column_names(lang)
            
            size_data = {}
            size_mapping = {
                "short_axis_um": column_names["short_axis"],
                "long_axis_um": column_names["long_axis"],
                "mean_diameter_um": column_names["mean_diameter"],
                "equivalent_diameter_um": column_names["equivalent_diameter"]
            }
            
            for key, col_name in size_mapping.items():
                if col_name in particles_df.columns:
                    size_data[key] = particles_df[col_name].tolist()
            
            if size_data and stats_data:
                histogram_fig = create_histogram_plot(size_data, lang, "linear")
                
                # 解析パラメータ
                analysis_params = {
                    "pixels_per_um": get_scale_info(),
                    "threshold_method": st.session_state.get("detection_params", {}).get("threshold_method", "N/A"),
                    "min_area": st.session_state.get("detection_params", {}).get("min_area", "N/A"),
                    "min_circularity": st.session_state.get("detection_params", {}).get("min_circularity", "N/A")
                }
                
                html_report = create_html_report(
                    particles_df, stats_data, histogram_fig, analysis_params, lang
                )
                
                st.download_button(
                    label=get_text("download_report", lang),
                    data=html_report.encode('utf-8'),
                    file_name=f"analysis_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html",
                    key="report_download"
                )

def get_analysis_results() -> Optional[Dict[str, Dict[str, float]]]:
    """
    解析結果を取得
    
    Returns:
        解析結果（実行されていない場合はNone）
    """
    return st.session_state.get("analysis_results")

def is_analysis_completed() -> bool:
    """
    解析が完了しているかチェック
    
    Returns:
        解析が完了している場合True
    """
    return st.session_state.get("analysis_results") is not None

def create_summary_report(particles_df: pd.DataFrame, lang: str) -> str:
    """
    サマリーレポートを作成
    
    Args:
        particles_df: 粒子データ
        lang: 言語設定
        
    Returns:
        サマリーレポート文字列
    """
    from config.languages import get_column_names
    column_names = get_column_names(lang)
    
    # 基本統計
    particle_count = len(particles_df)
    
    # 等価直径の統計（利用可能な場合）
    equiv_col = column_names["equivalent_diameter"]
    if equiv_col in particles_df.columns:
        equiv_data = particles_df[equiv_col].tolist()
        equiv_stats = calculate_statistics(equiv_data)
        d_values = calculate_d_values(equiv_data)
        
        summary = f"""
{get_text('analysis_summary', lang) if lang == 'en' else '解析サマリー'}:
- {get_text('particle_count', lang)}: {particle_count}
- {get_text('equivalent_diameter', lang)} {get_text('mean', lang) if lang == 'en' else '平均'}: {equiv_stats['mean']:.2f} μm
- {get_text('equivalent_diameter', lang)} {get_text('geometric_mean', lang)}: {equiv_stats['geometric_mean']:.2f} μm
- D10: {d_values['d10']:.2f} μm
- D50: {d_values['d50']:.2f} μm
- D90: {d_values['d90']:.2f} μm
        """
    else:
        summary = f"""
{get_text('analysis_summary', lang) if lang == 'en' else '解析サマリー'}:
- {get_text('particle_count', lang)}: {particle_count}
        """
    
    return summary.strip()