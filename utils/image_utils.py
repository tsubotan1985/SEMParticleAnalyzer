# -*- coding: utf-8 -*-
"""
画像処理ユーティリティ
SEM Particle Analyzer用の画像処理関数
"""

import numpy as np
import cv2
from PIL import Image
import streamlit as st
from skimage import filters, morphology, measure, segmentation
from skimage.filters import threshold_otsu, threshold_li, threshold_yen, threshold_triangle, threshold_isodata
from typing import Tuple, Optional, Dict, Any
import io

def load_image_from_uploaded_file(uploaded_file) -> Optional[np.ndarray]:
    """
    アップロードされたファイルから画像を読み込み
    
    Args:
        uploaded_file: Streamlitのアップロードファイル
        
    Returns:
        numpy配列の画像データ（グレースケール）
    """
    try:
        # PILで画像を開く
        image = Image.open(uploaded_file)
        
        # RGBに変換（必要に応じて）
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # numpy配列に変換
        img_array = np.array(image)
        
        # グレースケールに変換
        if len(img_array.shape) == 3:
            gray_image = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray_image = img_array
            
        return gray_image
        
    except Exception as e:
        st.error(f"画像の読み込みに失敗しました: {str(e)}")
        return None

def resize_image_for_display(image: np.ndarray, max_width: int = 1200) -> np.ndarray:
    """
    表示用に画像をリサイズ
    
    Args:
        image: 入力画像
        max_width: 最大幅
        
    Returns:
        リサイズされた画像
    """
    height, width = image.shape[:2]
    
    if width > max_width:
        scale = max_width / width
        new_width = max_width
        new_height = int(height * scale)
        
        if len(image.shape) == 3:
            resized = cv2.resize(image, (new_width, new_height))
        else:
            resized = cv2.resize(image, (new_width, new_height))
            
        return resized
    
    return image

def apply_gaussian_filter(image: np.ndarray, sigma: float) -> np.ndarray:
    """
    ガウシアンフィルタを適用
    
    Args:
        image: 入力画像
        sigma: ガウシアンのσ値
        
    Returns:
        フィルタ適用後の画像
    """
    return filters.gaussian(image, sigma=sigma, preserve_range=True).astype(np.uint8)

def apply_median_filter(image: np.ndarray, kernel_size: int) -> np.ndarray:
    """
    メディアンフィルタを適用
    
    Args:
        image: 入力画像
        kernel_size: カーネルサイズ
        
    Returns:
        フィルタ適用後の画像
    """
    # カーネルサイズは奇数である必要がある
    if kernel_size % 2 == 0:
        kernel_size += 1
        
    return cv2.medianBlur(image, kernel_size)

def adjust_brightness_contrast(image: np.ndarray, black_point: int, white_point: int, contrast: float) -> np.ndarray:
    """
    輝度・コントラスト調整
    
    Args:
        image: 入力画像
        black_point: ブラックポイント
        white_point: ホワイトポイント
        contrast: コントラスト倍率
        
    Returns:
        調整後の画像
    """
    # 正規化
    normalized = (image.astype(np.float32) - black_point) / (white_point - black_point)
    normalized = np.clip(normalized, 0, 1)
    
    # コントラスト調整
    adjusted = np.power(normalized, 1.0 / contrast)
    
    # 0-255の範囲に戻す
    result = (adjusted * 255).astype(np.uint8)
    
    return result

def auto_preprocessing_params(image: np.ndarray) -> Dict[str, Any]:
    """
    2値化を容易にする観点での自動前処理パラメータ設定
    
    Args:
        image: 入力画像
        
    Returns:
        推奨パラメータの辞書
    """
    # ヒストグラム解析
    hist = cv2.calcHist([image], [0], None, [256], [0, 256])
    
    # ノイズレベルの推定（高周波成分）
    laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()
    
    # パラメータ決定
    params = {}
    
    # ガウシアンフィルタ（ノイズレベルに応じて）
    if laplacian_var > 1000:
        params["gaussian_sigma"] = float(1.5)
    elif laplacian_var > 500:
        params["gaussian_sigma"] = float(1.0)
    else:
        params["gaussian_sigma"] = float(0.5)
    
    # メディアンフィルタ（ノイズ除去）
    params["median_kernel"] = int(3)
    
    # ブラックポイント・ホワイトポイント（ヒストグラムの1%と99%点）
    cumsum = np.cumsum(hist.flatten())
    total_pixels = cumsum[-1]
    
    black_point_idx = np.where(cumsum >= total_pixels * 0.01)[0]
    white_point_idx = np.where(cumsum >= total_pixels * 0.99)[0]
    
    params["black_point"] = int(black_point_idx[0]) if len(black_point_idx) > 0 else 0
    params["white_point"] = int(white_point_idx[0]) if len(white_point_idx) > 0 else 255
    
    # コントラスト（ヒストグラムの分散に基づく）
    mean_intensity = np.mean(image)
    std_intensity = np.std(image)
    
    if std_intensity < 30:
        params["contrast"] = float(1.5)  # 低コントラスト画像
    elif std_intensity > 80:
        params["contrast"] = float(0.8)  # 高コントラスト画像
    else:
        params["contrast"] = float(1.0)  # 標準
    
    return params

def apply_preprocessing(image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
    """
    前処理パラメータを適用
    
    Args:
        image: 入力画像
        params: 前処理パラメータ
        
    Returns:
        前処理後の画像
    """
    result = image.copy()
    
    # ガウシアンフィルタ
    if params.get("gaussian_sigma", 0) > 0:
        result = apply_gaussian_filter(result, params["gaussian_sigma"])
    
    # メディアンフィルタ
    if params.get("median_kernel", 0) > 1:
        result = apply_median_filter(result, params["median_kernel"])
    
    # 輝度・コントラスト調整
    result = adjust_brightness_contrast(
        result,
        params.get("black_point", 0),
        params.get("white_point", 255),
        params.get("contrast", 1.0)
    )
    
    return result

def get_threshold_value(image: np.ndarray, method: str) -> int:
    """
    指定された手法で閾値を計算
    
    Args:
        image: 入力画像
        method: 閾値化手法
        
    Returns:
        閾値
    """
    try:
        if method == "otsu":
            return threshold_otsu(image)
        elif method == "li":
            return threshold_li(image)
        elif method == "yen":
            return threshold_yen(image)
        elif method == "triangle":
            return threshold_triangle(image)
        elif method == "isodata":
            return threshold_isodata(image)
        else:
            return threshold_otsu(image)  # デフォルト
    except:
        return 128  # フォールバック

def compare_threshold_methods(image: np.ndarray) -> Dict[str, int]:
    """
    複数の閾値化手法を比較
    
    Args:
        image: 入力画像
        
    Returns:
        各手法の閾値辞書
    """
    methods = ["otsu", "li", "yen", "triangle", "isodata"]
    thresholds = {}
    
    for method in methods:
        thresholds[method] = get_threshold_value(image, method)
    
    return thresholds

def create_roi_mask(image: np.ndarray, bottom_exclusion_percent: float) -> np.ndarray:
    """
    関心領域マスクを作成（下部除外）
    
    Args:
        image: 入力画像
        bottom_exclusion_percent: 下部除外率（%）
        
    Returns:
        ROIマスク（True=関心領域）
    """
    height, width = image.shape
    mask = np.ones((height, width), dtype=bool)
    
    # 下部除外
    exclusion_height = int(height * bottom_exclusion_percent / 100)
    if exclusion_height > 0:
        mask[-exclusion_height:, :] = False
    
    return mask

def convert_to_pil_image(image: np.ndarray) -> Image.Image:
    """
    numpy配列をPIL Imageに変換
    
    Args:
        image: numpy配列の画像
        
    Returns:
        PIL Image
    """
    if len(image.shape) == 2:
        # グレースケール
        return Image.fromarray(image, mode='L')
    else:
        # カラー
        return Image.fromarray(image, mode='RGB')

def image_to_bytes(image: np.ndarray, format: str = 'PNG') -> bytes:
    """
    画像をバイト列に変換（ダウンロード用）
    
    Args:
        image: numpy配列の画像
        format: 出力フォーマット
        
    Returns:
        画像のバイト列
    """
    pil_image = convert_to_pil_image(image)
    
    # バイト列に変換
    img_buffer = io.BytesIO()
    pil_image.save(img_buffer, format=format)
    img_buffer.seek(0)
    
    return img_buffer.getvalue()