# -*- coding: utf-8 -*-
"""
UIコンポーネントモジュール
SEM Particle Analyzer用の共通UIコンポーネント
"""

import streamlit as st
import numpy as np
from typing import Optional, Dict, Any, List
from config.languages import get_text, LANGUAGES
from config.settings import get_current_language, set_language, initialize_session_state

def render_language_selector():
    """言語選択UIの描画"""
    st.markdown("### Language")
    
    # 現在の言語を取得
    current_lang = get_current_language()
    
    # 言語選択
    selected_language = st.selectbox(
        "Please select a language / 言語を選択してください",
        options=list(LANGUAGES.keys()),
        index=list(LANGUAGES.values()).index(current_lang),
        key="language_selector"
    )
    
    # 言語が変更された場合
    new_lang_code = LANGUAGES[selected_language]
    if new_lang_code != current_lang:
        set_language(new_lang_code)
        st.experimental_rerun()
    
    return new_lang_code

def render_app_header():
    """アプリケーションヘッダーの描画"""
    lang = get_current_language()
    
    st.title(get_text("app_title", lang))
    st.markdown("---")

def render_sidebar_info():
    """サイドバー情報の描画"""
    lang = get_current_language()
    
    with st.sidebar:
        st.header(f"{get_text('system_info', lang) if lang == 'en' else 'システム情報'}")
        
        # 現在の状態表示
        render_status_indicators(lang)
        
        # 進行状況表示
        render_progress_indicator(lang)
        
        # ヘルプ情報
        render_help_section(lang)

def render_status_indicators(lang: str):
    """状態インジケーターの描画"""
    st.markdown(f"**{get_text('current_status', lang) if lang == 'en' else '現在の状態'}**")
    
    # 画像読み込み状態
    from modules.image_loader import is_image_loaded, is_scale_set
    
    if is_image_loaded():
        st.success(f"✅ {get_text('image_loaded', lang)}")
    else:
        st.error(f"❌ {get_text('error_no_image', lang)}")
    
    # スケール設定状態
    if is_scale_set():
        scale_info = st.session_state.get("scale_pixels_per_um", 0)
        st.success(f"✅ {get_text('scale_set', lang)}: {scale_info:.3f} px/μm")
    else:
        st.error(f"❌ {get_text('error_no_scale', lang)}")
    
    # 前処理状態
    from modules.image_processor import is_preprocessing_applied
    
    if is_preprocessing_applied():
        st.success(f"✅ {get_text('preprocessing_applied', lang) if lang == 'en' else '前処理適用済み'}")
    else:
        st.warning(f"⚠️ {get_text('preprocessing_not_applied', lang) if lang == 'en' else '前処理未適用'}")
    
    # 粒子検出状態
    from modules.particle_detector import is_particles_detected
    
    if is_particles_detected():
        particle_count = st.session_state.get("particle_count", 0)
        st.success(f"✅ {get_text('particles_detected', lang)}: {particle_count}")
    else:
        st.error(f"❌ {get_text('no_particles_detected', lang) if lang == 'en' else '粒子未検出'}")
    
    # 解析状態
    from modules.size_analyzer import is_analysis_completed
    
    if is_analysis_completed():
        st.success(f"✅ {get_text('analysis_completed', lang) if lang == 'en' else '解析完了'}")
    else:
        st.error(f"❌ {get_text('analysis_not_completed', lang) if lang == 'en' else '解析未完了'}")

def render_progress_indicator(lang: str):
    """進行状況インジケーターの描画"""
    st.markdown(f"**{get_text('progress', lang) if lang == 'en' else '進行状況'}**")
    
    # 各ステップの完了状態をチェック
    from modules.image_loader import is_image_loaded, is_scale_set
    from modules.image_processor import is_preprocessing_applied
    from modules.particle_detector import is_particles_detected
    from modules.size_analyzer import is_analysis_completed
    
    steps = [
        (get_text("tab_image_load", lang), is_image_loaded() and is_scale_set()),
        (get_text("tab_image_adjust", lang), is_preprocessing_applied()),
        (get_text("tab_particle_detect", lang), is_particles_detected()),
        (get_text("tab_size_analysis", lang), is_analysis_completed())
    ]
    
    completed_steps = sum(1 for _, completed in steps if completed)
    total_steps = len(steps)
    
    # プログレスバー
    progress = completed_steps / total_steps
    st.progress(progress)
    st.caption(f"{completed_steps}/{total_steps} {get_text('steps_completed', lang) if lang == 'en' else 'ステップ完了'}")
    
    # ステップリスト
    for step_name, completed in steps:
        if completed:
            st.markdown(f"✅ {step_name}")
        else:
            st.markdown(f"⭕ {step_name}")

def render_help_section(lang: str):
    """ヘルプセクションの描画"""
    with st.expander(f"ℹ️ {get_text('help', lang) if lang == 'en' else 'ヘルプ'}"):
        
        st.markdown(f"**{get_text('workflow', lang) if lang == 'en' else 'ワークフロー'}**")
        
        workflow_steps = [
            get_text("step1_load_image", lang) if lang == "en" else "1. 画像を読み込み、スケールを設定",
            get_text("step2_adjust_image", lang) if lang == "en" else "2. 画像の前処理を実行（オプション）",
            get_text("step3_detect_particles", lang) if lang == "en" else "3. 粒子検出パラメータを調整して検出実行",
            get_text("step4_analyze_size", lang) if lang == "en" else "4. 粒径分布を解析・ダウンロード"
        ]
        
        for step in workflow_steps:
            st.markdown(f"- {step}")
        
        st.markdown(f"**{get_text('tips', lang) if lang == 'en' else 'ヒント'}**")
        
        tips = [
            get_text("tip1", lang) if lang == "en" else "スケール設定は水平方向に正確に線を引いてください",
            get_text("tip2", lang) if lang == "en" else "前処理の自動設定は2値化を容易にする観点で最適化されます",
            get_text("tip3", lang) if lang == "en" else "粒子検出では最小面積と円形度で不要な検出を除外できます",
            get_text("tip4", lang) if lang == "en" else "解析結果はCSV、画像、HTMLレポートでダウンロード可能です"
        ]
        
        for tip in tips:
            st.markdown(f"💡 {tip}")

def render_error_message(message: str, error_type: str = "error"):
    """エラーメッセージの表示"""
    if error_type == "error":
        st.error(f"❌ {message}")
    elif error_type == "warning":
        st.warning(f"⚠️ {message}")
    elif error_type == "info":
        st.info(f"ℹ️ {message}")
    else:
        st.error(f"❌ {message}")

def render_success_message(message: str):
    """成功メッセージの表示"""
    st.success(f"✅ {message}")

def render_processing_spinner(message: str):
    """処理中スピナーの表示"""
    return st.spinner(f"⏳ {message}...")

def render_metric_card(label: str, value: str, delta: Optional[str] = None):
    """メトリクスカードの表示"""
    st.metric(label=label, value=value, delta=delta)

def render_data_table(data: Dict[str, Any], title: str):
    """データテーブルの表示"""
    st.markdown(f"**{title}**")
    
    if isinstance(data, dict):
        # 辞書をDataFrameに変換
        import pandas as pd
        df = pd.DataFrame(list(data.items()), columns=["Parameter", "Value"])
        st.dataframe(df, use_container_width=True)
    else:
        st.dataframe(data, use_container_width=True)

def render_image_comparison(images: List[np.ndarray], titles: List[str], max_width: int = 400):
    """画像比較表示"""
    if len(images) != len(titles):
        st.error("画像数とタイトル数が一致しません")
        return
    
    cols = st.columns(len(images))
    
    for i, (image, title) in enumerate(zip(images, titles)):
        with cols[i]:
            st.markdown(f"**{title}**")
            from utils.image_utils import resize_image_for_display
            display_image = resize_image_for_display(image, max_width)
            st.image(display_image, use_column_width=True)

def render_parameter_summary(params: Dict[str, Any], title: str, lang: str):
    """パラメータサマリーの表示"""
    with st.expander(f"📋 {title}"):
        
        for key, value in params.items():
            if isinstance(value, float):
                st.markdown(f"- **{key}**: {value:.3f}")
            elif isinstance(value, int):
                st.markdown(f"- **{key}**: {value}")
            else:
                st.markdown(f"- **{key}**: {value}")

def render_download_buttons(download_data: Dict[str, bytes], lang: str):
    """ダウンロードボタンの表示"""
    st.markdown(f"**{get_text('download_section', lang) if lang == 'en' else 'ダウンロード'}**")
    
    cols = st.columns(len(download_data))
    
    for i, (file_type, data) in enumerate(download_data.items()):
        with cols[i]:
            if file_type == "csv":
                st.download_button(
                    label=get_text("download_csv", lang),
                    data=data,
                    file_name=f"analysis_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            elif file_type == "html":
                st.download_button(
                    label=get_text("download_report", lang),
                    data=data,
                    file_name=f"report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html"
                )
            elif file_type == "png":
                st.download_button(
                    label=get_text("download_image", lang),
                    data=data,
                    file_name=f"histogram_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.png",
                    mime="image/png"
                )

def render_confirmation_dialog(message: str, key: str) -> bool:
    """確認ダイアログの表示"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.warning(message)
    
    with col2:
        return st.button("確認", key=key)

def render_reset_button(lang: str, key: str = "reset_button") -> bool:
    """リセットボタンの表示"""
    return st.button(
        f"🔄 {get_text('reset', lang) if lang == 'en' else 'リセット'}",
        key=key,
        help=f"{get_text('reset_help', lang) if lang == 'en' else '現在の設定をリセットします'}"
    )

def render_export_options(lang: str):
    """エクスポートオプションの表示"""
    st.markdown(f"**{get_text('export_options', lang) if lang == 'en' else 'エクスポートオプション'}**")
    
    export_formats = st.multiselect(
        f"{get_text('select_formats', lang) if lang == 'en' else 'フォーマットを選択'}",
        options=["CSV", "PNG", "HTML"],
        default=["CSV"],
        key="export_formats"
    )
    
    return export_formats

def render_analysis_summary_card(lang: str):
    """解析サマリーカードの表示"""
    from modules.particle_detector import get_particles_data
    from modules.size_analyzer import get_analysis_results
    
    particles_data = get_particles_data()
    analysis_results = get_analysis_results()
    
    if particles_data and analysis_results:
        st.markdown(f"**{get_text('analysis_summary', lang) if lang == 'en' else '解析サマリー'}**")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label=get_text("particle_count", lang),
                value=len(particles_data)
            )
        
        # 等価直径の統計（利用可能な場合）
        if "equivalent_diameter_um" in analysis_results:
            equiv_stats = analysis_results["equivalent_diameter_um"]
            
            with col2:
                st.metric(
                    label=f"{get_text('mean', lang) if lang == 'en' else '平均'} (μm)",
                    value=f"{equiv_stats.get('mean', 0):.2f}"
                )
            
            with col3:
                st.metric(
                    label=f"{get_text('geometric_mean', lang)} (μm)",
                    value=f"{equiv_stats.get('geometric_mean', 0):.2f}"
                )
            
            with col4:
                st.metric(
                    label="D50 (μm)",
                    value=f"{equiv_stats.get('d50', 0):.2f}"
                )

def initialize_ui():
    """UI初期化"""
    # セッション状態の初期化
    initialize_session_state()
    
    # ページ設定
    from config.settings import APP_CONFIG
    
    st.set_page_config(
        page_title=APP_CONFIG["title"],
        page_icon=APP_CONFIG["page_icon"],
        layout=APP_CONFIG["layout"],
        initial_sidebar_state=APP_CONFIG["initial_sidebar_state"]
    )
    
    # カスタムCSS（オプション）
    render_custom_css()

def render_custom_css():
    """カスタムCSSの適用"""
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        border-bottom: 2px solid #f0f0f0;
        margin-bottom: 2rem;
    }
    
    .status-indicator {
        padding: 0.5rem;
        border-radius: 0.5rem;
        margin: 0.25rem 0;
    }
    
    .status-success {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    
    .status-error {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    
    .status-warning {
        background-color: #fff3cd;
        color: #856404;
        border: 1px solid #ffeaa7;
    }
    
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# pandas のインポートを追加
import pandas as pd