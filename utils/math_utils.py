# -*- coding: utf-8 -*-
"""
数学・統計ユーティリティ
SEM Particle Analyzer用の数学計算関数
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
from scipy import stats
import math

def calculate_particle_properties(contour: np.ndarray, pixels_per_um: float) -> Dict[str, float]:
    """
    単一粒子の特性を計算
    
    Args:
        contour: 粒子の輪郭
        pixels_per_um: ピクセル/μm変換係数
        
    Returns:
        粒子特性の辞書
    """
    # 面積（ピクセル）
    area_pixels = cv2.contourArea(contour)
    area_um2 = area_pixels / (pixels_per_um ** 2)
    
    # 外接矩形
    rect = cv2.minAreaRect(contour)
    width, height = rect[1]
    
    # 短辺・長辺
    short_axis_pixels = min(width, height)
    long_axis_pixels = max(width, height)
    short_axis_um = short_axis_pixels / pixels_per_um
    long_axis_um = long_axis_pixels / pixels_per_um
    
    # 平均直径
    mean_diameter_um = (short_axis_um + long_axis_um) / 2
    
    # 等価直径（面積から計算）
    equivalent_diameter_um = 2 * math.sqrt(area_um2 / math.pi)
    
    # 円形度
    perimeter = cv2.arcLength(contour, True)
    if perimeter > 0:
        circularity = 4 * math.pi * area_pixels / (perimeter ** 2)
    else:
        circularity = 0
    
    # アスペクト比
    aspect_ratio = long_axis_pixels / short_axis_pixels if short_axis_pixels > 0 else 0
    
    return {
        "area_pixels": area_pixels,
        "area_um2": area_um2,
        "short_axis_pixels": short_axis_pixels,
        "long_axis_pixels": long_axis_pixels,
        "short_axis_um": short_axis_um,
        "long_axis_um": long_axis_um,
        "mean_diameter_um": mean_diameter_um,
        "equivalent_diameter_um": equivalent_diameter_um,
        "circularity": circularity,
        "aspect_ratio": aspect_ratio,
        "perimeter": perimeter
    }

def calculate_statistics(data: List[float]) -> Dict[str, float]:
    """
    基本統計量を計算
    
    Args:
        data: データリスト
        
    Returns:
        統計量の辞書
    """
    if not data or len(data) == 0:
        return {}
    
    data_array = np.array(data)
    
    # 基本統計量
    stats_dict = {
        "count": len(data),
        "mean": np.mean(data_array),
        "std": np.std(data_array, ddof=1) if len(data) > 1 else 0,
        "min": np.min(data_array),
        "max": np.max(data_array),
        "median": np.median(data_array),
        "q25": np.percentile(data_array, 25),
        "q75": np.percentile(data_array, 75),
    }
    
    # 幾何平均・幾何標準偏差（正の値のみ）
    positive_data = data_array[data_array > 0]
    if len(positive_data) > 0:
        log_data = np.log(positive_data)
        geometric_mean = np.exp(np.mean(log_data))
        geometric_std = np.exp(np.std(log_data, ddof=1)) if len(positive_data) > 1 else 1
        
        stats_dict["geometric_mean"] = geometric_mean
        stats_dict["geometric_std"] = geometric_std
    else:
        stats_dict["geometric_mean"] = 0
        stats_dict["geometric_std"] = 0
    
    return stats_dict

def create_histogram_data(data: List[float], bins: int = 50) -> Tuple[np.ndarray, np.ndarray]:
    """
    ヒストグラムデータを作成
    
    Args:
        data: データリスト
        bins: ビン数
        
    Returns:
        (ヒストグラム値, ビン境界)
    """
    if not data or len(data) == 0:
        return np.array([]), np.array([])
    
    hist, bin_edges = np.histogram(data, bins=bins)
    return hist, bin_edges

def create_log_histogram_data(data: List[float], bins: int = 50) -> Tuple[np.ndarray, np.ndarray]:
    """
    対数スケールヒストグラムデータを作成
    
    Args:
        data: データリスト
        bins: ビン数
        
    Returns:
        (ヒストグラム値, ビン境界)
    """
    if not data or len(data) == 0:
        return np.array([]), np.array([])
    
    # 正の値のみ使用
    positive_data = [x for x in data if x > 0]
    if not positive_data:
        return np.array([]), np.array([])
    
    # 対数スケールでビンを作成
    log_min = np.log10(min(positive_data))
    log_max = np.log10(max(positive_data))
    log_bins = np.logspace(log_min, log_max, bins + 1)
    
    hist, bin_edges = np.histogram(positive_data, bins=log_bins)
    return hist, bin_edges

def calculate_size_distribution_stats(particles_data: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """
    粒径分布の統計情報を計算
    
    Args:
        particles_data: 粒子データのDataFrame
        
    Returns:
        各サイズメトリクスの統計情報
    """
    size_metrics = ["short_axis_um", "long_axis_um", "mean_diameter_um", "equivalent_diameter_um"]
    results = {}
    
    for metric in size_metrics:
        if metric in particles_data.columns:
            data = particles_data[metric].tolist()
            results[metric] = calculate_statistics(data)
    
    return results

def fit_lognormal_distribution(data: List[float]) -> Dict[str, float]:
    """
    対数正規分布をフィッティング
    
    Args:
        data: データリスト
        
    Returns:
        フィッティングパラメータ
    """
    if not data or len(data) == 0:
        return {}
    
    # 正の値のみ使用
    positive_data = [x for x in data if x > 0]
    if len(positive_data) < 2:
        return {}
    
    try:
        # 対数正規分布のパラメータ推定
        shape, loc, scale = stats.lognorm.fit(positive_data, floc=0)
        
        # 統計量計算
        mean = stats.lognorm.mean(shape, loc, scale)
        std = stats.lognorm.std(shape, loc, scale)
        median = stats.lognorm.median(shape, loc, scale)
        
        return {
            "shape": shape,
            "loc": loc,
            "scale": scale,
            "mean": mean,
            "std": std,
            "median": median,
            "r_squared": calculate_lognormal_r_squared(positive_data, shape, loc, scale)
        }
    except:
        return {}

def calculate_lognormal_r_squared(data: List[float], shape: float, loc: float, scale: float) -> float:
    """
    対数正規分布フィッティングのR²値を計算
    
    Args:
        data: 実データ
        shape, loc, scale: 対数正規分布パラメータ
        
    Returns:
        R²値
    """
    try:
        # 理論値計算
        sorted_data = np.sort(data)
        theoretical_cdf = stats.lognorm.cdf(sorted_data, shape, loc, scale)
        
        # 実測値のCDF
        n = len(sorted_data)
        empirical_cdf = np.arange(1, n + 1) / n
        
        # R²計算
        ss_res = np.sum((empirical_cdf - theoretical_cdf) ** 2)
        ss_tot = np.sum((empirical_cdf - np.mean(empirical_cdf)) ** 2)
        
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        return max(0, min(1, r_squared))  # 0-1の範囲にクリップ
    except:
        return 0

def calculate_d_values(data: List[float]) -> Dict[str, float]:
    """
    D10, D50, D90値を計算
    
    Args:
        data: データリスト
        
    Returns:
        D値の辞書
    """
    if not data or len(data) == 0:
        return {}
    
    data_array = np.array(data)
    
    return {
        "d10": np.percentile(data_array, 10),
        "d50": np.percentile(data_array, 50),  # median
        "d90": np.percentile(data_array, 90),
    }

def calculate_span(d_values: Dict[str, float]) -> float:
    """
    スパン値を計算 (D90 - D10) / D50
    
    Args:
        d_values: D値の辞書
        
    Returns:
        スパン値
    """
    if "d10" in d_values and "d50" in d_values and "d90" in d_values and d_values["d50"] > 0:
        return (d_values["d90"] - d_values["d10"]) / d_values["d50"]
    return 0

def create_particles_dataframe(particles_list: List[Dict[str, float]], language: str = "ja") -> pd.DataFrame:
    """
    粒子データのDataFrameを作成
    
    Args:
        particles_list: 粒子データのリスト
        language: 言語設定
        
    Returns:
        粒子データのDataFrame
    """
    if not particles_list:
        return pd.DataFrame()
    
    # DataFrameを作成
    df = pd.DataFrame(particles_list)
    
    # 粒子IDを追加
    df.insert(0, "particle_id", range(1, len(df) + 1))
    
    # 言語に応じてカラム名を変更
    from config.languages import get_column_names
    column_names = get_column_names(language)
    
    rename_mapping = {
        "particle_id": column_names["particle_id"],
        "short_axis_um": column_names["short_axis"],
        "long_axis_um": column_names["long_axis"],
        "mean_diameter_um": column_names["mean_diameter"],
        "equivalent_diameter_um": column_names["equivalent_diameter"],
        "area_um2": column_names["area"],
        "circularity": column_names["circularity"]
    }
    
    # 存在するカラムのみリネーム
    existing_columns = {k: v for k, v in rename_mapping.items() if k in df.columns}
    df = df.rename(columns=existing_columns)
    
    return df

# OpenCVのインポートを追加
import cv2