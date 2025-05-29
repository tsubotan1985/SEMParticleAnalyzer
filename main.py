# -*- coding: utf-8 -*-
"""
SEM Particle Size Distribution Analysis System
メインアプリケーション
"""

import streamlit as st
from modules.ui_components import (
    initialize_ui, render_language_selector, render_app_header, 
    render_sidebar_info, render_analysis_summary_card
)
from modules.image_loader import render_image_loader
from modules.image_processor import render_image_processor
from modules.particle_detector import render_particle_detector
from modules.size_analyzer import render_size_analyzer
from config.languages import get_text
from config.settings import get_current_language

def main():
    """メインアプリケーション"""
    
    # UI初期化
    initialize_ui()
    
    # セッション状態初期化
    from config.settings import initialize_session_state
    initialize_session_state()
    
    # 言語選択
    lang = render_language_selector()
    
    # アプリケーションヘッダー
    render_app_header()
    
    # サイドバー情報
    render_sidebar_info()
    
    # メインコンテンツ
    render_main_content(lang)

def render_main_content(lang: str):
    """メインコンテンツの描画"""
    
    # タブの作成
    tab1, tab2, tab3, tab4 = st.tabs([
        get_text("tab_image_load", lang),
        get_text("tab_image_adjust", lang),
        get_text("tab_particle_detect", lang),
        get_text("tab_size_analysis", lang)
    ])
    
    # 各タブの内容
    with tab1:
        render_image_loader()
    
    with tab2:
        render_image_processor()
    
    with tab3:
        render_particle_detector()
    
    with tab4:
        render_size_analyzer()
    
    # 解析サマリー（フッター）
    render_footer_summary(lang)

def render_footer_summary(lang: str):
    """フッターサマリーの描画"""
    st.markdown("---")
    
    # 解析が完了している場合のみサマリーを表示
    from modules.size_analyzer import is_analysis_completed
    
    if is_analysis_completed():
        render_analysis_summary_card(lang)
    
    # アプリケーション情報
    with st.expander(f"ℹ️ {get_text('about', lang) if lang == 'en' else 'このアプリについて'}"):
        st.markdown(f"""
        **{get_text('app_title', lang)}**
        
        {get_text('app_description', lang) if lang == 'en' else 'SEM画像から粒径分布を解析するWebアプリケーションです。'}
        
        **{get_text('features', lang) if lang == 'en' else '主な機能'}:**
        - {get_text('feature1', lang) if lang == 'en' else '多形式画像対応（TIFF, PNG, BMP, JPG）'}
        - {get_text('feature2', lang) if lang == 'en' else '対話的スケール設定'}
        - {get_text('feature3', lang) if lang == 'en' else '高度な画像前処理'}
        - {get_text('feature4', lang) if lang == 'en' else '複数の閾値化手法'}
        - {get_text('feature5', lang) if lang == 'en' else '詳細な粒径分布解析'}
        - {get_text('feature6', lang) if lang == 'en' else '多形式出力（CSV, HTML, PNG）'}
        
        **{get_text('version', lang) if lang == 'en' else 'バージョン'}:** 1.0.0
        
        **{get_text('developed_by', lang) if lang == 'en' else '開発者'}:** SEM Analysis Team
        """)

if __name__ == "__main__":
    main()