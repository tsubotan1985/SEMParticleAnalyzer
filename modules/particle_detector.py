# -*- coding: utf-8 -*-
"""
粒子検出モジュール
SEM Particle Analyzer用の粒子検出・閾値化機能
"""

import streamlit as st
import numpy as np
import cv2
from skimage import measure, morphology, segmentation
from skimage.filters import threshold_otsu, threshold_li, threshold_yen, threshold_triangle, threshold_isodata
from typing import List, Dict, Any, Optional, Tuple
from config.languages import get_text
from config.settings import get_current_language, DETECTION_CONFIG, IMAGE_CONFIG
from utils.image_utils import (
    get_threshold_value, compare_threshold_methods, create_roi_mask, resize_image_for_display
)
from utils.math_utils import calculate_particle_properties
from modules.image_loader import is_image_loaded, get_original_image, get_scale_info
from modules.image_processor import get_processed_image, is_preprocessing_applied

def render_particle_detector():
    """粒子検出タブの描画"""
    lang = get_current_language()
    
    st.header(get_text("tab_particle_detect", lang))
    
    # 前提条件チェック
    if not is_image_loaded():
        st.warning(get_text("error_no_image", lang))
        return
    
    scale_info = get_scale_info()
    if scale_info is None:
        st.warning(get_text("error_no_scale", lang))
        return
    
    # 使用する画像を決定
    if is_preprocessing_applied():
        input_image = get_processed_image()
        st.info(f"{get_text('using_processed_image', lang) if lang == 'en' else '前処理済み画像を使用します'}")
    else:
        input_image = get_original_image()
        st.info(f"{get_text('using_original_image', lang) if lang == 'en' else '元画像を使用します'}")
    
    # 検出パラメータセクション
    render_detection_controls(input_image, lang)
    
    # 検出実行・結果表示セクション
    render_detection_results(input_image, scale_info, lang)

def render_detection_controls(image: np.ndarray, lang: str):
    """検出パラメータコントロールの描画"""
    st.subheader(get_text("particle_detection", lang))
    
    # 画像極性設定
    st.markdown(f"**{get_text('image_polarity', lang)}**")
    polarity = st.radio(
        get_text("image_polarity", lang),
        options=["white_bg_black_particles", "black_bg_white_particles"],
        format_func=lambda x: get_text(x, lang),
        key="polarity_radio",
        horizontal=True
    )
    st.session_state.detection_params["polarity"] = polarity
    
    # 関心領域設定
    st.markdown(f"**{get_text('roi_exclusion', lang)}**")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        bottom_exclusion = st.slider(
            get_text("bottom_exclusion_percent", lang),
            min_value=0.0,
            max_value=20.0,
            value=st.session_state.detection_params["bottom_exclusion"],
            step=0.5,
            key="bottom_exclusion_slider"
        )
        st.session_state.detection_params["bottom_exclusion"] = bottom_exclusion
    
    with col2:
        excluded_pixels = int(image.shape[0] * bottom_exclusion / 100)
        st.metric(
            label=f"{get_text('excluded_pixels', lang) if lang == 'en' else '除外ピクセル'}",
            value=f"{excluded_pixels} px"
        )
    
    # 閾値化手法設定
    st.markdown(f"**{get_text('threshold_method', lang)}**")
    
    threshold_method = st.selectbox(
        get_text("threshold_method", lang),
        options=["auto"] + DETECTION_CONFIG["threshold_methods"] + ["manual"],
        format_func=lambda x: get_text(x, lang) if x != "auto" and x != "manual" else get_text(f"{x}_threshold", lang),
        key="threshold_method_select"
    )
    st.session_state.detection_params["threshold_method"] = threshold_method
    
    # 自動閾値比較
    if threshold_method == "auto":
        render_auto_threshold_comparison(image, lang)
    
    # 手動閾値設定
    elif threshold_method == "manual":
        render_manual_threshold_controls(image, lang)
    
    # 検出パラメータ
    render_detection_parameters(lang)

def render_auto_threshold_comparison(image: np.ndarray, lang: str):
    """自動閾値比較の表示"""
    with st.expander(f"{get_text('auto_threshold', lang)} {get_text('comparison', lang) if lang == 'en' else '比較'}"):
        # ROIマスクを適用
        roi_mask = create_roi_mask(image, st.session_state.detection_params["bottom_exclusion"])
        roi_image = image[roi_mask]
        
        # 各手法の閾値を計算
        thresholds = compare_threshold_methods(roi_image)
        
        # 結果表示
        cols = st.columns(len(thresholds))
        
        for i, (method, threshold) in enumerate(thresholds.items()):
            with cols[i]:
                st.metric(
                    label=get_text(method, lang),
                    value=f"{threshold:.0f}"
                )
        
        # 推奨手法の選択（Otsu法をデフォルト）
        recommended_method = "otsu"  # 実際にはより高度な選択ロジックを実装可能
        st.info(f"{get_text('recommended', lang) if lang == 'en' else '推奨'}: {get_text(recommended_method, lang)}")
        
        # 選択された手法を保存
        st.session_state.detection_params["selected_auto_method"] = recommended_method
        st.session_state.detection_params["threshold_value"] = thresholds[recommended_method]

def render_manual_threshold_controls(image: np.ndarray, lang: str):
    """手動閾値コントロールの描画"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        threshold_value = st.slider(
            get_text("threshold_value", lang),
            min_value=DETECTION_CONFIG["threshold_range"][0],
            max_value=DETECTION_CONFIG["threshold_range"][1],
            value=st.session_state.detection_params["threshold_value"],
            key="threshold_value_slider"
        )
        st.session_state.detection_params["threshold_value"] = threshold_value
    
    with col2:
        st.metric(
            label=get_text("threshold_value", lang),
            value=f"{threshold_value}"
        )
    
    # リアルタイムプレビュー
    render_threshold_preview(image, threshold_value, lang)

def render_threshold_preview(image: np.ndarray, threshold: int, lang: str):
    """閾値プレビューの表示"""
    # ROIマスクを適用
    roi_mask = create_roi_mask(image, st.session_state.detection_params["bottom_exclusion"])
    
    # 2値化
    polarity = st.session_state.detection_params["polarity"]
    if polarity == "white_bg_black_particles":
        binary = image < threshold
    else:
        binary = image > threshold
    
    # ROI外をマスク
    binary = binary & roi_mask
    
    # プレビュー表示
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**{get_text('original_image', lang) if lang == 'en' else '元画像'}**")
        display_original = resize_image_for_display(image, 300)
        st.image(display_original, use_column_width=True)
    
    with col2:
        st.markdown(f"**{get_text('binary_image', lang) if lang == 'en' else '2値化画像'}**")
        display_binary = resize_image_for_display((binary * 255).astype(np.uint8), 300)
        st.image(display_binary, use_column_width=True)

def render_detection_parameters(lang: str):
    """検出パラメータの描画"""
    st.markdown(f"**{get_text('detection_parameters', lang) if lang == 'en' else '検出パラメータ'}**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 最小面積
        min_area = st.number_input(
            get_text("min_area", lang),
            min_value=DETECTION_CONFIG["min_area_range"][0],
            max_value=DETECTION_CONFIG["min_area_range"][1],
            value=st.session_state.detection_params["min_area"],
            step=1,
            key="min_area_input"
        )
        st.session_state.detection_params["min_area"] = min_area
        
        # 最小円形度
        min_circularity = st.number_input(
            get_text("min_circularity", lang),
            min_value=DETECTION_CONFIG["circularity_range"][0],
            max_value=DETECTION_CONFIG["circularity_range"][1],
            value=st.session_state.detection_params["min_circularity"],
            step=DETECTION_CONFIG["circularity_step"],
            format="%.2f",
            key="min_circularity_input"
        )
        st.session_state.detection_params["min_circularity"] = min_circularity
    
    with col2:
        # 画像が読み込まれている場合は画像面積を最大値として使用
        if "original_image" in st.session_state and st.session_state.original_image is not None:
            image_area = st.session_state.original_image.shape[0] * st.session_state.original_image.shape[1]
            max_area_limit = max(DETECTION_CONFIG["max_area_range"][1], image_area)
        else:
            max_area_limit = DETECTION_CONFIG["max_area_range"][1]
        
        # 最大面積
        max_area = st.number_input(
            get_text("max_area", lang),
            min_value=DETECTION_CONFIG["max_area_range"][0],
            max_value=max_area_limit,
            value=st.session_state.detection_params["max_area"],
            step=100,
            key="max_area_input"
        )
        st.session_state.detection_params["max_area"] = max_area
        
        # 画像面積に基づく自動設定の説明
        if "original_image" in st.session_state and st.session_state.original_image is not None:
            image_area = st.session_state.original_image.shape[0] * st.session_state.original_image.shape[1]
            if max_area == image_area:
                st.info(f"🔄 {get_text('auto_set_to_image_area', lang) if lang == 'en' else '画像面積に自動設定'}")

def render_detection_results(image: np.ndarray, pixels_per_um: float, lang: str):
    """検出結果の表示"""
    st.subheader(f"{get_text('detection_results', lang) if lang == 'en' else '検出結果'}")
    
    # 検出実行ボタン
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        detect_button = st.button(get_text("detect_particles", lang), type="primary")
    
    with col2:
        if st.button(f"{get_text('reset', lang) if lang == 'en' else 'リセット'}", key="detection_reset_button"):
            reset_detection_results()
            st.experimental_rerun()
    
    if detect_button:
        with st.spinner(f"{get_text('detecting', lang) if lang == 'en' else '検出中'}..."):
            particles_data, detected_image = detect_particles(image, pixels_per_um)
            
            if particles_data:
                st.session_state.particles_data = particles_data
                st.session_state.detected_image = detected_image
                st.session_state.particle_count = len(particles_data)
                
                st.success(f"{len(particles_data)} {get_text('particles_detected', lang)}")
            else:
                st.warning(f"{get_text('no_particles_detected', lang) if lang == 'en' else '粒子が検出されませんでした'}")
    
    # 検出結果の表示
    if st.session_state.get("particles_data"):
        render_detection_visualization(lang)
        render_detection_statistics(lang)

def detect_particles(image: np.ndarray, pixels_per_um: float) -> Tuple[List[Dict], Optional[np.ndarray]]:
    """
    粒子検出を実行
    
    Args:
        image: 入力画像
        pixels_per_um: ピクセル/μm変換係数
        
    Returns:
        (粒子データリスト, 検出結果画像)
    """
    params = st.session_state.detection_params
    
    # ROIマスクを作成
    roi_mask = create_roi_mask(image, params["bottom_exclusion"])
    
    # 閾値を決定
    if params["threshold_method"] == "auto":
        method = params.get("selected_auto_method", "otsu")
        roi_image = image[roi_mask]
        threshold = get_threshold_value(roi_image, method)
    elif params["threshold_method"] == "manual":
        threshold = params["threshold_value"]
    else:
        # 個別手法
        roi_image = image[roi_mask]
        threshold = get_threshold_value(roi_image, params["threshold_method"])
    
    # 2値化
    if params["polarity"] == "white_bg_black_particles":
        binary = image < threshold
    else:
        binary = image > threshold
    
    # ROI外をマスク
    binary = binary & roi_mask
    
    # ノイズ除去
    binary = morphology.remove_small_objects(binary, min_size=params["min_area"])
    
    # 輪郭検出
    contours, _ = cv2.findContours(
        binary.astype(np.uint8), 
        cv2.RETR_EXTERNAL, 
        cv2.CHAIN_APPROX_SIMPLE
    )
    
    # 粒子データを計算
    particles_data = []
    valid_contours = []
    
    for contour in contours:
        # 面積フィルタ
        area = cv2.contourArea(contour)
        if area < params["min_area"] or area > params["max_area"]:
            continue
        
        # 円形度フィルタ
        perimeter = cv2.arcLength(contour, True)
        if perimeter > 0:
            circularity = 4 * np.pi * area / (perimeter ** 2)
            if circularity < params["min_circularity"]:
                continue
        else:
            continue
        
        # 粒子特性を計算
        particle_props = calculate_particle_properties(contour, pixels_per_um)
        particles_data.append(particle_props)
        valid_contours.append(contour)
    
    # 検出結果画像を作成
    detected_image = create_detection_overlay(image, valid_contours)
    
    return particles_data, detected_image

def create_detection_overlay(image: np.ndarray, contours: List[np.ndarray]) -> np.ndarray:
    """
    検出結果のオーバーレイ画像を作成
    
    Args:
        image: 元画像
        contours: 検出された輪郭リスト
        
    Returns:
        オーバーレイ画像
    """
    # カラー画像に変換
    if len(image.shape) == 2:
        overlay = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    else:
        overlay = image.copy()
    
    # 輪郭を描画
    cv2.drawContours(overlay, contours, -1, (0, 255, 0), 2)
    
    # 粒子番号を描画
    for i, contour in enumerate(contours):
        # 重心を計算
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            
            # 番号を描画
            cv2.putText(overlay, str(i+1), (cx-10, cy+5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
    
    return overlay

def render_detection_visualization(lang: str):
    """検出結果の可視化"""
    st.markdown(f"**{get_text('detection_visualization', lang) if lang == 'en' else '検出結果可視化'}**")
    
    detected_image = st.session_state.get("detected_image")
    if detected_image is not None:
        display_detected = resize_image_for_display(detected_image, 800)
        st.image(display_detected, caption=f"{get_text('detected_particles', lang) if lang == 'en' else '検出された粒子'}", use_column_width=True)

def render_detection_statistics(lang: str):
    """検出統計の表示"""
    particles_data = st.session_state.get("particles_data", [])
    
    if not particles_data:
        return
    
    st.markdown(f"**{get_text('detection_statistics', lang) if lang == 'en' else '検出統計'}**")
    
    # 基本統計
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label=get_text("particle_count", lang),
            value=len(particles_data)
        )
    
    with col2:
        areas = [p["area_um2"] for p in particles_data]
        st.metric(
            label=f"{get_text('mean', lang) if lang == 'en' else '平均'} {get_text('area', lang) if lang == 'en' else '面積'} (μm²)",
            value=f"{np.mean(areas):.2f}"
        )
    
    with col3:
        diameters = [p["equivalent_diameter_um"] for p in particles_data]
        st.metric(
            label=f"{get_text('mean', lang) if lang == 'en' else '平均'} {get_text('equivalent_diameter', lang)} (μm)",
            value=f"{np.mean(diameters):.2f}"
        )
    
    with col4:
        circularities = [p["circularity"] for p in particles_data]
        st.metric(
            label=f"{get_text('mean', lang) if lang == 'en' else '平均'} {get_text('circularity', lang)}",
            value=f"{np.mean(circularities):.3f}"
        )

def reset_detection_results():
    """検出結果をリセット"""
    st.session_state.particles_data = None
    st.session_state.detected_image = None
    st.session_state.particle_count = 0

def get_particles_data() -> Optional[List[Dict]]:
    """
    検出された粒子データを取得
    
    Returns:
        粒子データリスト（検出されていない場合はNone）
    """
    return st.session_state.get("particles_data")

def get_detected_image() -> Optional[np.ndarray]:
    """
    検出結果画像を取得
    
    Returns:
        検出結果画像（検出されていない場合はNone）
    """
    return st.session_state.get("detected_image")

def is_particles_detected() -> bool:
    """
    粒子が検出されているかチェック
    
    Returns:
        粒子が検出されている場合True
    """
    particles_data = get_particles_data()
    return particles_data is not None and len(particles_data) > 0