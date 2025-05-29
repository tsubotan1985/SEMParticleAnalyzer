# -*- coding: utf-8 -*-
"""
画像読み込みモジュール
SEM Particle Analyzer用の画像読み込み・スケール設定機能
"""

import streamlit as st
import numpy as np
from PIL import Image
import math
from typing import Optional, Tuple
from config.languages import get_text
from config.settings import get_current_language, IMAGE_CONFIG
from utils.image_utils import load_image_from_uploaded_file, resize_image_for_display

# streamlit-drawable-canvasのインポート
try:
    from streamlit_drawable_canvas import st_canvas
    CANVAS_AVAILABLE = True
except ImportError:
    CANVAS_AVAILABLE = False
    st.warning("streamlit-drawable-canvas is not available. Scale setting will use alternative method.")

def render_image_loader():
    """画像読み込みタブの描画"""
    lang = get_current_language()
    
    st.header(get_text("tab_image_load", lang))
    
    # ファイルアップローダー
    uploaded_file = st.file_uploader(
        get_text("upload_image", lang),
        type=IMAGE_CONFIG["supported_formats"],
        help=get_text("supported_formats", lang)
    )
    
    if uploaded_file is not None:
        # 新しい画像が読み込まれた場合、ワークスペースをリセット
        if st.session_state.get("current_filename") != uploaded_file.name:
            from config.settings import reset_workspace
            reset_workspace()
            st.session_state.current_filename = uploaded_file.name
        
        # 画像を読み込み
        image = load_image_from_uploaded_file(uploaded_file)
        
        if image is not None:
            st.session_state.original_image = image
            st.success(get_text("image_loaded", lang))
            
            # 画像表示セクション
            render_image_display(image, lang)
            
            # スケール設定セクション
            render_scale_setting(image, lang)
    
    else:
        st.info(get_text("upload_image", lang))

def render_image_display(image: np.ndarray, lang: str):
    """画像表示セクション"""
    st.subheader(get_text("display_image", lang))
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # 表示用にリサイズ
        display_image = resize_image_for_display(image, IMAGE_CONFIG["max_image_width"])
        st.image(display_image, caption=f"{get_text('original_image', lang) if lang == 'en' else '元画像'}", use_column_width=True)
    
    with col2:
        st.metric(
            label=f"{get_text('image_size', lang) if lang == 'en' else '画像サイズ'}",
            value=f"{image.shape[1]} × {image.shape[0]}"
        )
        st.metric(
            label=f"{get_text('data_type', lang) if lang == 'en' else 'データ型'}",
            value=str(image.dtype)
        )
        
        # 再表示ボタン
        if st.button(get_text("display_image", lang)):
            st.experimental_rerun()

def render_scale_setting(image: np.ndarray, lang: str):
    """スケール設定セクション"""
    st.subheader(get_text("scale_setting", lang))
    
    if CANVAS_AVAILABLE:
        render_canvas_scale_setting(image, lang)
    else:
        render_manual_scale_setting(image, lang)

def render_canvas_scale_setting(image: np.ndarray, lang: str):
    """streamlit-drawable-canvasを使用したスケール設定"""
    st.info(get_text("draw_scale_line", lang))
    
    # 表示用画像の準備
    canvas_width = min(800, image.shape[1])
    canvas_height = int(canvas_width * image.shape[0] / image.shape[1])
    display_image = resize_image_for_display(image, canvas_width)
    
    # グレースケール画像をRGBに変換
    if len(display_image.shape) == 2:
        display_image_rgb = np.stack([display_image] * 3, axis=-1)
    else:
        display_image_rgb = display_image
    
    # PILイメージに変換
    pil_image = Image.fromarray(display_image_rgb.astype(np.uint8))
    
    # 描画キャンバス
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",  # オレンジ色の塗りつぶし
        stroke_width=3,
        stroke_color="#FF0000",  # 赤色の線
        background_image=pil_image,
        update_streamlit=True,
        height=canvas_height,
        width=canvas_width,
        drawing_mode="line",
        point_display_radius=0,
        display_toolbar=True,
        key="scale_canvas",
    )
    
    # 描画結果の処理
    if canvas_result.json_data is not None:
        objects = canvas_result.json_data["objects"]
        
        if len(objects) > 0:
            # 最後に描画された線を取得
            last_line = objects[-1]
            
            if last_line["type"] == "path":
                # パスから線の座標を抽出
                path_data = last_line["path"]
                if len(path_data) >= 2:
                    # 開始点と終了点を取得
                    start_point = path_data[0]
                    end_point = path_data[-1]
                    
                    if start_point[0] == "M" and len(start_point) >= 3:
                        x1, y1 = start_point[1], start_point[2]
                    else:
                        x1, y1 = 0, 0
                    
                    # 終了点を探す
                    for point in reversed(path_data):
                        if len(point) >= 3 and isinstance(point[1], (int, float)):
                            x2, y2 = point[1], point[2]
                            break
                    else:
                        x2, y2 = x1, y1
                    
                    # 線の長さを計算
                    line_length_pixels = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                    
                    if line_length_pixels > 10:  # 最小線長チェック
                        # 元画像のスケールに変換
                        scale_factor = image.shape[1] / canvas_width
                        actual_line_length = line_length_pixels * scale_factor
                        
                        # スケール入力UI
                        col1, col2, col3 = st.columns([2, 2, 1])
                        
                        with col1:
                            scale_length_um = st.number_input(
                                get_text("scale_length_um", lang),
                                min_value=0.001,
                                max_value=10000.0,
                                value=1.0,
                                step=0.1,
                                format="%.3f",
                                key="scale_length_input"
                            )
                        
                        with col2:
                            if st.button(get_text("set_scale", lang), key="canvas_set_scale_button"):
                                if scale_length_um > 0:
                                    pixels_per_um = actual_line_length / scale_length_um
                                    st.session_state.scale_pixels_per_um = pixels_per_um
                                    st.session_state.scale_set = True
                                    st.success(get_text("scale_set", lang))
                                    st.experimental_rerun()
                        
                        with col3:
                            st.metric(
                                label=f"{get_text('line_length', lang) if lang == 'en' else '線の長さ'}",
                                value=f"{actual_line_length:.1f} px"
                            )
                        
                        # 線の情報を表示
                        st.info(f"{get_text('line_coordinates', lang) if lang == 'en' else '線の座標'}: ({x1:.0f}, {y1:.0f}) → ({x2:.0f}, {y2:.0f})")
            
            elif last_line["type"] == "line":
                # 直線の場合
                x1, y1 = last_line["x1"], last_line["y1"]
                x2, y2 = last_line["x2"], last_line["y2"]
                
                line_length_pixels = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                
                if line_length_pixels > 10:
                    scale_factor = image.shape[1] / canvas_width
                    actual_line_length = line_length_pixels * scale_factor
                    
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        scale_length_um = st.number_input(
                            get_text("scale_length_um", lang),
                            min_value=0.001,
                            max_value=10000.0,
                            value=1.0,
                            step=0.1,
                            format="%.3f",
                            key="scale_length_input"
                        )
                    
                    with col2:
                        if st.button(get_text("set_scale", lang), key="canvas_set_scale_button"):
                            if scale_length_um > 0:
                                pixels_per_um = actual_line_length / scale_length_um
                                st.session_state.scale_pixels_per_um = pixels_per_um
                                st.session_state.scale_set = True
                                st.success(get_text("scale_set", lang))
                                st.experimental_rerun()
                    
                    with col3:
                        st.metric(
                            label=f"{get_text('line_length', lang) if lang == 'en' else '線の長さ'}",
                            value=f"{actual_line_length:.1f} px"
                        )
                    
                    st.info(f"{get_text('line_coordinates', lang) if lang == 'en' else '線の座標'}: ({x1:.0f}, {y1:.0f}) → ({x2:.0f}, {y2:.0f})")
    
    # 使用方法の説明
    with st.expander(f"{get_text('canvas_instructions', lang) if lang == 'en' else 'キャンバス使用方法'}"):
        st.markdown(f"""
        1. {get_text('canvas_step1', lang) if lang == 'en' else '左側のツールバーで線描画モードを選択'}
        2. {get_text('canvas_step2', lang) if lang == 'en' else '画像上で既知の長さの線を描画'}
        3. {get_text('canvas_step3', lang) if lang == 'en' else '実際の長さ（μm）を入力'}
        4. {get_text('canvas_step4', lang) if lang == 'en' else 'スケールを設定ボタンをクリック'}
        """)

def render_manual_scale_setting(image: np.ndarray, lang: str):
    """手動スケール設定（代替方法）"""
    st.info(f"{get_text('manual_scale_info', lang) if lang == 'en' else '手動でスケールを設定してください。画像上の既知の長さを測定し、ピクセル数と実際の長さを入力してください。'}")
    
    # 画像表示
    display_image = resize_image_for_display(image, 800)
    st.image(display_image, caption=f"{get_text('measure_known_length', lang) if lang == 'en' else '既知の長さを測定してください'}", use_container_width=True)
    
    # 手動入力
    col1, col2, col3 = st.columns(3)
    
    with col1:
        pixel_length = st.number_input(
            f"{get_text('pixel_length', lang) if lang == 'en' else 'ピクセル長さ'}",
            min_value=1.0,
            max_value=float(max(image.shape)),
            value=100.0,
            step=1.0,
            help=f"{get_text('pixel_length_help', lang) if lang == 'en' else '画像上で測定したピクセル数を入力してください'}"
        )
    
    with col2:
        actual_length_um = st.number_input(
            get_text("scale_length_um", lang),
            min_value=0.001,
            max_value=10000.0,
            value=1.0,
            step=0.1,
            format="%.3f",
            help=f"{get_text('actual_length_help', lang) if lang == 'en' else '実際の長さをμm単位で入力してください'}"
        )
    
    with col3:
        if st.button(get_text("set_scale", lang), key="manual_set_scale_button"):
            if pixel_length > 0 and actual_length_um > 0:
                pixels_per_um = pixel_length / actual_length_um
                st.session_state.scale_pixels_per_um = pixels_per_um
                st.session_state.scale_set = True
                st.success(get_text("scale_set", lang))
                st.experimental_rerun()
            else:
                st.error(f"{get_text('invalid_values', lang) if lang == 'en' else '有効な値を入力してください'}")
    
    # 計算されるスケール情報を表示
    if pixel_length > 0 and actual_length_um > 0:
        calculated_scale = pixel_length / actual_length_um
        st.info(f"{get_text('calculated_scale', lang) if lang == 'en' else '計算されるスケール'}: {calculated_scale:.3f} {get_text('pixels_per_um', lang)}")
    
    # 現在のスケール設定を表示
    if st.session_state.get("scale_set", False):
        st.success(
            f"✅ {get_text('scale_setting', lang)}: "
            f"{st.session_state.scale_pixels_per_um:.3f} {get_text('pixels_per_um', lang)}"
        )
        
        # スケール情報
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                label=get_text("pixels_per_um", lang),
                value=f"{st.session_state.scale_pixels_per_um:.3f}"
            )
        with col2:
            um_per_pixel = 1.0 / st.session_state.scale_pixels_per_um
            st.metric(
                label=f"{get_text('unit_um', lang)}/pixel",
                value=f"{um_per_pixel:.3f}"
            )
    else:
        st.warning(get_text("error_no_scale", lang))

def get_scale_info() -> Optional[float]:
    """
    現在のスケール情報を取得
    
    Returns:
        ピクセル/μm変換係数（設定されていない場合はNone）
    """
    if st.session_state.get("scale_set", False):
        return st.session_state.get("scale_pixels_per_um")
    return None

def is_image_loaded() -> bool:
    """
    画像が読み込まれているかチェック
    
    Returns:
        画像が読み込まれている場合True
    """
    return st.session_state.get("original_image") is not None

def is_scale_set() -> bool:
    """
    スケールが設定されているかチェック
    
    Returns:
        スケールが設定されている場合True
    """
    return st.session_state.get("scale_set", False)

def get_original_image() -> Optional[np.ndarray]:
    """
    元画像を取得
    
    Returns:
        元画像（読み込まれていない場合はNone）
    """
    return st.session_state.get("original_image")

def validate_image_and_scale() -> Tuple[bool, str]:
    """
    画像とスケールの設定状態を検証
    
    Returns:
        (検証結果, エラーメッセージ)
    """
    lang = get_current_language()
    
    if not is_image_loaded():
        return False, get_text("error_no_image", lang)
    
    if not is_scale_set():
        return False, get_text("error_no_scale", lang)
    
    return True, ""

def reset_scale():
    """スケール設定をリセット"""
    st.session_state.scale_pixels_per_um = None
    st.session_state.scale_set = False

def calculate_image_stats(image: np.ndarray) -> dict:
    """
    画像の基本統計情報を計算
    
    Args:
        image: 入力画像
        
    Returns:
        統計情報の辞書
    """
    return {
        "width": image.shape[1],
        "height": image.shape[0],
        "channels": len(image.shape),
        "dtype": str(image.dtype),
        "min_value": int(np.min(image)),
        "max_value": int(np.max(image)),
        "mean_value": float(np.mean(image)),
        "std_value": float(np.std(image))
    }