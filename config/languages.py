# -*- coding: utf-8 -*-
"""
多言語対応設定
SEM Particle Analyzer用の日本語・英語対応
"""

LANGUAGES = {
    "日本語": "ja",
    "English": "en"
}

TRANSLATIONS = {
    "ja": {
        # アプリケーション全般
        "app_title": "SEM粒径分布解析システム",
        "language_selection": "言語選択",
        "select_language": "言語を選択してください",
        
        # タブ名
        "tab_image_load": "画像読み込み",
        "tab_image_adjust": "画像調整", 
        "tab_particle_detect": "粒子検出",
        "tab_size_analysis": "粒径解析",
        
        # 画像読み込み
        "upload_image": "画像ファイルをアップロード",
        "supported_formats": "対応形式: TIFF, PNG, BMP, JPG",
        "display_image": "画像を表示",
        "scale_setting": "スケール設定",
        "draw_scale_line": "スケール線を描画してください（水平方向）",
        "scale_length_um": "スケール長さ (μm)",
        "set_scale": "スケールを設定",
        "pixels_per_um": "ピクセル/μm",
        
        # 画像調整
        "preprocessing": "前処理",
        "auto_settings": "自動設定",
        "apply_settings": "設定を適用",
        "gaussian_filter": "ガウシアンフィルタ",
        "median_filter": "メディアンフィルタ",
        "black_point": "ブラックポイント",
        "white_point": "ホワイトポイント",
        "contrast": "コントラスト",
        "sigma": "σ値",
        "kernel_size": "カーネルサイズ",
        
        # 粒子検出
        "particle_detection": "粒子検出",
        "image_polarity": "画像極性",
        "white_bg_black_particles": "白地に黒い粒子",
        "black_bg_white_particles": "黒地に白い粒子",
        "roi_exclusion": "関心領域除外",
        "bottom_exclusion_percent": "下部除外率 (%)",
        "threshold_method": "閾値化手法",
        "auto_threshold": "自動閾値",
        "manual_threshold": "手動閾値",
        "threshold_value": "閾値",
        "min_area": "最小面積",
        "max_area": "最大面積",
        "min_circularity": "最小円形度",
        "detect_particles": "粒子を検出",
        "otsu": "Otsu法",
        "li": "Li法",
        "yen": "Yen法",
        "triangle": "Triangle法",
        "isodata": "Isodata法",
        
        # 粒径解析
        "size_analysis": "粒径解析",
        "histogram": "ヒストグラム",
        "linear_scale": "線形スケール",
        "log_scale": "対数スケール",
        "short_axis": "短辺",
        "long_axis": "長辺",
        "mean_diameter": "平均直径",
        "equivalent_diameter": "等価直径",
        "statistics": "統計情報",
        "geometric_mean": "幾何平均",
        "geometric_std": "幾何標準偏差",
        "particle_count": "粒子数",
        "download_csv": "CSVダウンロード",
        "download_image": "画像ダウンロード",
        "download_report": "レポートダウンロード",
        
        # 単位・ラベル
        "unit_um": "μm",
        "unit_pixels": "ピクセル",
        "unit_percent": "%",
        "count": "個数",
        "frequency": "頻度",
        
        # メッセージ
        "image_loaded": "画像が読み込まれました",
        "scale_set": "スケールが設定されました",
        "processing_complete": "処理が完了しました",
        "particles_detected": "個の粒子が検出されました",
        "error_no_image": "画像が読み込まれていません",
        "error_no_scale": "スケールが設定されていません",
        "error_processing": "処理中にエラーが発生しました",
        "line_coordinates": "線の座標",
        "clear_canvas": "キャンバスをクリア",
        "fallback_to_manual": "手動設定に切り替えます",
        "manual_scale_info": "手動でスケールを設定してください。画像上の既知の長さを測定し、ピクセル数と実際の長さを入力してください。",
        "measure_known_length": "既知の長さを測定してください",
        "pixel_length": "ピクセル長さ",
        "pixel_length_help": "画像上で測定したピクセル数を入力してください",
        "actual_length_help": "実際の長さをμm単位で入力してください",
        "invalid_values": "有効な値を入力してください",
        "calculated_scale": "計算されるスケール",
        "manual_coordinate_input": "手動座標入力",
        "set_line": "線を設定",
        "clear_line": "線をクリア",
        "click_scale_instruction": "画像上で2点をクリックしてスケール線を描画してください",
        "points_selected": "選択された点",
        "reset_points": "ポイントをリセット",
        "canvas_instructions": "キャンバス使用方法",
        "canvas_step1": "左側のツールバーで線描画モードを選択",
        "canvas_step2": "画像上で既知の長さの線を描画",
        "canvas_step3": "実際の長さ（μm）を入力",
        "canvas_step4": "スケールを設定ボタンをクリック",
    },
    
    "en": {
        # Application general
        "app_title": "SEM Particle Size Distribution Analysis System",
        "language_selection": "Language Selection",
        "select_language": "Please select a language",
        
        # Tab names
        "tab_image_load": "Image Loading",
        "tab_image_adjust": "Image Adjustment",
        "tab_particle_detect": "Particle Detection", 
        "tab_size_analysis": "Size Analysis",
        
        # Image loading
        "upload_image": "Upload Image File",
        "supported_formats": "Supported formats: TIFF, PNG, BMP, JPG",
        "display_image": "Display Image",
        "scale_setting": "Scale Setting",
        "draw_scale_line": "Please draw scale line (horizontal)",
        "scale_length_um": "Scale Length (μm)",
        "set_scale": "Set Scale",
        "pixels_per_um": "Pixels/μm",
        
        # Image adjustment
        "preprocessing": "Preprocessing",
        "auto_settings": "Auto Settings",
        "apply_settings": "Apply Settings",
        "gaussian_filter": "Gaussian Filter",
        "median_filter": "Median Filter",
        "black_point": "Black Point",
        "white_point": "White Point",
        "contrast": "Contrast",
        "sigma": "Sigma",
        "kernel_size": "Kernel Size",
        
        # Particle detection
        "particle_detection": "Particle Detection",
        "image_polarity": "Image Polarity",
        "white_bg_black_particles": "White background, black particles",
        "black_bg_white_particles": "Black background, white particles",
        "roi_exclusion": "ROI Exclusion",
        "bottom_exclusion_percent": "Bottom Exclusion (%)",
        "threshold_method": "Threshold Method",
        "auto_threshold": "Auto Threshold",
        "manual_threshold": "Manual Threshold",
        "threshold_value": "Threshold Value",
        "min_area": "Min Area",
        "max_area": "Max Area",
        "min_circularity": "Min Circularity",
        "detect_particles": "Detect Particles",
        "otsu": "Otsu",
        "li": "Li",
        "yen": "Yen",
        "triangle": "Triangle",
        "isodata": "Isodata",
        
        # Size analysis
        "size_analysis": "Size Analysis",
        "histogram": "Histogram",
        "linear_scale": "Linear Scale",
        "log_scale": "Log Scale",
        "short_axis": "Short Axis",
        "long_axis": "Long Axis",
        "mean_diameter": "Mean Diameter",
        "equivalent_diameter": "Equivalent Diameter",
        "statistics": "Statistics",
        "geometric_mean": "Geometric Mean",
        "geometric_std": "Geometric Std",
        "particle_count": "Particle Count",
        "download_csv": "Download CSV",
        "download_image": "Download Image",
        "download_report": "Download Report",
        
        # Units and labels
        "unit_um": "μm",
        "unit_pixels": "pixels",
        "unit_percent": "%",
        "count": "Count",
        "frequency": "Frequency",
        
        # Messages
        "image_loaded": "Image loaded successfully",
        "scale_set": "Scale set successfully",
        "processing_complete": "Processing completed",
        "particles_detected": "particles detected",
        "error_no_image": "No image loaded",
        "error_no_scale": "Scale not set",
        "error_processing": "Error occurred during processing",
        "line_coordinates": "Line Coordinates",
        "clear_canvas": "Clear Canvas",
        "fallback_to_manual": "Switching to manual setting",
        "manual_scale_info": "Please set the scale manually. Measure a known length on the image and enter the pixel count and actual length.",
        "measure_known_length": "Please measure a known length",
        "pixel_length": "Pixel Length",
        "pixel_length_help": "Enter the number of pixels measured on the image",
        "actual_length_help": "Enter the actual length in μm units",
        "invalid_values": "Please enter valid values",
        "calculated_scale": "Calculated Scale",
        "manual_coordinate_input": "Manual Coordinate Input",
        "set_line": "Set Line",
        "clear_line": "Clear Line",
        "click_scale_instruction": "Click two points on the image to draw a scale line",
        "points_selected": "Points Selected",
        "reset_points": "Reset Points",
        "canvas_instructions": "Canvas Instructions",
        "canvas_step1": "Select line drawing mode from the left toolbar",
        "canvas_step2": "Draw a line of known length on the image",
        "canvas_step3": "Enter the actual length (μm)",
        "canvas_step4": "Click the Set Scale button",
    }
}

def get_text(key: str, lang: str = "ja") -> str:
    """
    指定された言語のテキストを取得
    
    Args:
        key: テキストキー
        lang: 言語コード ("ja" or "en")
    
    Returns:
        翻訳されたテキスト
    """
    return TRANSLATIONS.get(lang, TRANSLATIONS["ja"]).get(key, key)

def get_column_names(lang: str = "ja") -> dict:
    """
    CSV出力用のカラム名を取得
    
    Args:
        lang: 言語コード
        
    Returns:
        カラム名の辞書
    """
    if lang == "en":
        return {
            "particle_id": "Particle_ID",
            "short_axis": "Short_Axis_um",
            "long_axis": "Long_Axis_um", 
            "mean_diameter": "Mean_Diameter_um",
            "equivalent_diameter": "Equivalent_Diameter_um",
            "area": "Area_um2",
            "circularity": "Circularity"
        }
    else:
        return {
            "particle_id": "粒子ID",
            "short_axis": "短辺_um",
            "long_axis": "長辺_um",
            "mean_diameter": "平均直径_um", 
            "equivalent_diameter": "等価直径_um",
            "area": "面積_um2",
            "circularity": "円形度"
        }