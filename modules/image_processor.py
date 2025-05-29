# -*- coding: utf-8 -*-
"""
画像前処理モジュール
SEM Particle Analyzer用の画像前処理機能
"""

import streamlit as st
import numpy as np
import cv2
from typing import Dict, Any, Optional
from config.languages import get_text
from config.settings import get_current_language, PREPROCESSING_CONFIG
from utils.image_utils import (
    apply_gaussian_filter, apply_median_filter, adjust_brightness_contrast,
    auto_preprocessing_params, apply_preprocessing, resize_image_for_display
)
from modules.image_loader import is_image_loaded, get_original_image

def render_image_processor():
    """画像前処理タブの描画"""
    lang = get_current_language()
    
    st.header(get_text("tab_image_adjust", lang))
    
    # 画像が読み込まれているかチェック
    if not is_image_loaded():
        st.warning(get_text("error_no_image", lang))
        return
    
    original_image = get_original_image()
    
    # 前処理パラメータセクション
    render_preprocessing_controls(original_image, lang)
    
    # プレビューセクション
    render_preprocessing_preview(original_image, lang)

def render_preprocessing_controls(image: np.ndarray, lang: str):
    """前処理コントロールの描画"""
    st.subheader(get_text("preprocessing", lang))
    
    # 自動設定ボタン
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button(get_text("auto_settings", lang)):
            auto_params = auto_preprocessing_params(image)
            
            # セッション状態を更新
            st.session_state.preprocessing_params.update(auto_params)
            st.success(f"{get_text('auto_settings', lang)} {get_text('processing_complete', lang)}")
            st.experimental_rerun()
    
    with col2:
        st.info(f"{get_text('auto_settings', lang)}: {get_text('auto_settings_help', lang) if lang == 'en' else '2値化を容易にする観点で自動設定します'}")
    
    # パラメータ調整
    st.markdown("---")
    
    # ガウシアンフィルタ
    st.markdown(f"**{get_text('gaussian_filter', lang)}**")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        gaussian_sigma = st.slider(
            get_text("sigma", lang),
            min_value=PREPROCESSING_CONFIG["gaussian_sigma_range"][0],
            max_value=PREPROCESSING_CONFIG["gaussian_sigma_range"][1],
            value=st.session_state.preprocessing_params["gaussian_sigma"],
            step=0.1,
            key="gaussian_sigma_slider"
        )
        st.session_state.preprocessing_params["gaussian_sigma"] = gaussian_sigma
    
    with col2:
        st.metric(
            label=get_text("sigma", lang),
            value=f"{gaussian_sigma:.1f}"
        )
    
    # メディアンフィルタ
    st.markdown(f"**{get_text('median_filter', lang)}**")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        median_kernel = st.slider(
            get_text("kernel_size", lang),
            min_value=PREPROCESSING_CONFIG["median_kernel_range"][0],
            max_value=PREPROCESSING_CONFIG["median_kernel_range"][1],
            value=st.session_state.preprocessing_params["median_kernel"],
            step=2,  # 奇数のみ
            key="median_kernel_slider"
        )
        # 奇数に調整
        if median_kernel % 2 == 0:
            median_kernel += 1
        st.session_state.preprocessing_params["median_kernel"] = median_kernel
    
    with col2:
        st.metric(
            label=get_text("kernel_size", lang),
            value=f"{median_kernel}"
        )
    
    # 輝度調整
    st.markdown(f"**{get_text('brightness_adjustment', lang) if lang == 'en' else '輝度調整'}**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        black_point = st.slider(
            get_text("black_point", lang),
            min_value=PREPROCESSING_CONFIG["black_point_range"][0],
            max_value=PREPROCESSING_CONFIG["black_point_range"][1],
            value=st.session_state.preprocessing_params["black_point"],
            key="black_point_slider"
        )
        st.session_state.preprocessing_params["black_point"] = black_point
    
    with col2:
        white_point = st.slider(
            get_text("white_point", lang),
            min_value=PREPROCESSING_CONFIG["white_point_range"][0],
            max_value=PREPROCESSING_CONFIG["white_point_range"][1],
            value=st.session_state.preprocessing_params["white_point"],
            key="white_point_slider"
        )
        st.session_state.preprocessing_params["white_point"] = white_point
    
    # コントラスト調整
    st.markdown(f"**{get_text('contrast', lang)}**")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        contrast = st.slider(
            get_text("contrast", lang),
            min_value=PREPROCESSING_CONFIG["contrast_range"][0],
            max_value=PREPROCESSING_CONFIG["contrast_range"][1],
            value=st.session_state.preprocessing_params["contrast"],
            step=0.1,
            key="contrast_slider"
        )
        st.session_state.preprocessing_params["contrast"] = contrast
    
    with col2:
        st.metric(
            label=get_text("contrast", lang),
            value=f"{contrast:.1f}"
        )

def render_preprocessing_preview(image: np.ndarray, lang: str):
    """前処理プレビューの描画"""
    st.subheader(f"{get_text('preview', lang) if lang == 'en' else 'プレビュー'}")
    
    # 適用ボタン
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        apply_button = st.button(get_text("apply_settings", lang), type="primary")
    
    with col2:
        reset_button = st.button(f"{get_text('reset', lang) if lang == 'en' else 'リセット'}", key="preprocessing_reset_button")
    
    if reset_button:
        reset_preprocessing_params()
        st.experimental_rerun()
    
    # 前処理を適用
    processed_image = apply_preprocessing(image, st.session_state.preprocessing_params)
    
    # 適用ボタンが押された場合
    if apply_button:
        st.session_state.processed_image = processed_image
        st.success(get_text("processing_complete", lang))
    
    # プレビュー表示
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**{get_text('original_image', lang) if lang == 'en' else '元画像'}**")
        display_original = resize_image_for_display(image, 400)
        st.image(display_original, use_column_width=True)
        
        # 元画像の統計情報
        render_image_stats(image, lang, "original")
    
    with col2:
        st.markdown(f"**{get_text('processed_image', lang) if lang == 'en' else '処理後画像'}**")
        display_processed = resize_image_for_display(processed_image, 400)
        st.image(display_processed, use_column_width=True)
        
        # 処理後画像の統計情報
        render_image_stats(processed_image, lang, "processed")
    
    # ヒストグラム比較
    render_histogram_comparison(image, processed_image, lang)

def render_image_stats(image: np.ndarray, lang: str, image_type: str):
    """画像統計情報の表示"""
    stats = {
        "min": int(np.min(image)),
        "max": int(np.max(image)),
        "mean": f"{np.mean(image):.1f}",
        "std": f"{np.std(image):.1f}"
    }
    
    with st.expander(f"{get_text('statistics', lang)} ({image_type})"):
        col1, col2 = st.columns(2)
        with col1:
            st.metric(f"{get_text('min', lang) if lang == 'en' else '最小値'}", stats["min"])
            st.metric(f"{get_text('mean', lang) if lang == 'en' else '平均'}", stats["mean"])
        with col2:
            st.metric(f"{get_text('max', lang) if lang == 'en' else '最大値'}", stats["max"])
            st.metric(f"{get_text('std', lang) if lang == 'en' else '標準偏差'}", stats["std"])

def render_histogram_comparison(original: np.ndarray, processed: np.ndarray, lang: str):
    """ヒストグラム比較の表示"""
    with st.expander(f"{get_text('histogram', lang)} {get_text('comparison', lang) if lang == 'en' else '比較'}"):
        import matplotlib.pyplot as plt
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        
        # 元画像のヒストグラム（英語表示のみ）
        ax1.hist(original.flatten(), bins=50, alpha=0.7, color='blue', edgecolor='black')
        ax1.set_title("Original Image")
        ax1.set_xlabel("Intensity")
        ax1.set_ylabel("Frequency")
        ax1.grid(True, alpha=0.3)
        
        # 処理後画像のヒストグラム（英語表示のみ）
        ax2.hist(processed.flatten(), bins=50, alpha=0.7, color='red', edgecolor='black')
        ax2.set_title("Processed Image")
        ax2.set_xlabel("Intensity")
        ax2.set_ylabel("Frequency")
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

def reset_preprocessing_params():
    """前処理パラメータをリセット"""
    st.session_state.preprocessing_params = {
        "gaussian_sigma": PREPROCESSING_CONFIG["gaussian_sigma_default"],
        "median_kernel": PREPROCESSING_CONFIG["median_kernel_default"],
        "black_point": PREPROCESSING_CONFIG["black_point_default"],
        "white_point": PREPROCESSING_CONFIG["white_point_default"],
        "contrast": PREPROCESSING_CONFIG["contrast_default"],
    }

def get_processed_image() -> Optional[np.ndarray]:
    """
    処理済み画像を取得
    
    Returns:
        処理済み画像（適用されていない場合はNone）
    """
    return st.session_state.get("processed_image")

def is_preprocessing_applied() -> bool:
    """
    前処理が適用されているかチェック
    
    Returns:
        前処理が適用されている場合True
    """
    return st.session_state.get("processed_image") is not None

def get_current_preprocessing_params() -> Dict[str, Any]:
    """
    現在の前処理パラメータを取得
    
    Returns:
        前処理パラメータの辞書
    """
    return st.session_state.get("preprocessing_params", {})

def apply_current_preprocessing(image: np.ndarray) -> np.ndarray:
    """
    現在のパラメータで前処理を適用
    
    Args:
        image: 入力画像
        
    Returns:
        前処理後の画像
    """
    params = get_current_preprocessing_params()
    return apply_preprocessing(image, params)

def validate_preprocessing_params() -> bool:
    """
    前処理パラメータの妥当性をチェック
    
    Returns:
        パラメータが妥当な場合True
    """
    params = get_current_preprocessing_params()
    
    # 基本的な範囲チェック
    if params.get("gaussian_sigma", 0) < 0:
        return False
    
    if params.get("median_kernel", 1) < 1:
        return False
    
    if params.get("black_point", 0) < 0 or params.get("black_point", 0) > 255:
        return False
    
    if params.get("white_point", 255) < 0 or params.get("white_point", 255) > 255:
        return False
    
    if params.get("black_point", 0) >= params.get("white_point", 255):
        return False
    
    if params.get("contrast", 1.0) <= 0:
        return False
    
    return True