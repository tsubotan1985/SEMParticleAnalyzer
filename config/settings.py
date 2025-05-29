# -*- coding: utf-8 -*-
"""
アプリケーション設定
SEM Particle Analyzer用の設定値
"""

import streamlit as st

# アプリケーション設定
APP_CONFIG = {
    "title": "SEM Particle Size Distribution Analysis System",
    "page_icon": "🔬",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# 画像処理設定
IMAGE_CONFIG = {
    "supported_formats": ["tiff", "tif", "png", "bmp", "jpg", "jpeg"],
    "max_file_size": 100,  # MB
    "default_bottom_exclusion": 6.5,  # %
    "max_image_width": 1200,  # 表示用最大幅
}

# 前処理設定
PREPROCESSING_CONFIG = {
    "gaussian_sigma_range": (0.1, 5.0),
    "gaussian_sigma_default": 1.0,
    "median_kernel_range": (1, 15),
    "median_kernel_default": 3,
    "black_point_range": (0, 255),
    "black_point_default": 0,
    "white_point_range": (0, 255), 
    "white_point_default": 255,
    "contrast_range": (0.5, 3.0),
    "contrast_default": 1.0,
}

# 粒子検出設定
DETECTION_CONFIG = {
    "threshold_methods": ["otsu", "li", "yen", "triangle", "isodata"],
    "threshold_range": (0, 255),
    "threshold_default": 128,
    "min_area_range": (1, 10000),
    "min_area_default": 10,
    "max_area_range": (100, 1000000),
    "max_area_default": 100000,
    "circularity_range": (0.0, 1.0),
    "circularity_default": 0.1,
    "circularity_step": 0.02,
}

# 解析設定
ANALYSIS_CONFIG = {
    "histogram_bins": 50,
    "size_metrics": ["short_axis", "long_axis", "mean_diameter", "equivalent_diameter"],
    "statistics_metrics": ["count", "mean", "std", "geometric_mean", "geometric_std", "min", "max"],
}

# セッション状態の初期化
def initialize_session_state():
    """セッション状態を初期化"""
    
    # 言語設定
    if "language" not in st.session_state:
        st.session_state.language = "ja"
    
    # 画像データ
    if "original_image" not in st.session_state:
        st.session_state.original_image = None
    
    if "processed_image" not in st.session_state:
        st.session_state.processed_image = None
        
    if "detected_image" not in st.session_state:
        st.session_state.detected_image = None
    
    # スケール設定
    if "scale_pixels_per_um" not in st.session_state:
        st.session_state.scale_pixels_per_um = None
        
    if "scale_set" not in st.session_state:
        st.session_state.scale_set = False
    
    # 前処理パラメータ
    if "preprocessing_params" not in st.session_state:
        st.session_state.preprocessing_params = {
            "gaussian_sigma": PREPROCESSING_CONFIG["gaussian_sigma_default"],
            "median_kernel": PREPROCESSING_CONFIG["median_kernel_default"],
            "black_point": PREPROCESSING_CONFIG["black_point_default"],
            "white_point": PREPROCESSING_CONFIG["white_point_default"],
            "contrast": PREPROCESSING_CONFIG["contrast_default"],
        }
    
    # 検出パラメータ
    if "detection_params" not in st.session_state:
        st.session_state.detection_params = {
            "polarity": "white_bg_black_particles",
            "bottom_exclusion": IMAGE_CONFIG["default_bottom_exclusion"],
            "threshold_method": "auto",
            "threshold_value": DETECTION_CONFIG["threshold_default"],
            "min_area": DETECTION_CONFIG["min_area_default"],
            "max_area": DETECTION_CONFIG["max_area_default"],
            "min_circularity": DETECTION_CONFIG["circularity_default"],
        }
    
    # 検出結果
    if "particles_data" not in st.session_state:
        st.session_state.particles_data = None
        
    if "particle_count" not in st.session_state:
        st.session_state.particle_count = 0
    
    # 解析結果
    if "analysis_results" not in st.session_state:
        st.session_state.analysis_results = None

def reset_workspace():
    """ワークスペースをリセット（新しい画像読み込み時）"""
    st.session_state.original_image = None
    st.session_state.processed_image = None
    st.session_state.detected_image = None
    st.session_state.scale_pixels_per_um = None
    st.session_state.scale_set = False
    st.session_state.particles_data = None
    st.session_state.particle_count = 0
    st.session_state.analysis_results = None

def get_current_language():
    """現在の言語設定を取得"""
    return st.session_state.get("language", "ja")

def set_language(lang_code):
    """言語を設定"""
    st.session_state.language = lang_code