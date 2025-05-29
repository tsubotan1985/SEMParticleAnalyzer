# SEM粒径分布解析システム / SEM Particle Size Distribution Analysis System

[English](#english) | [日本語](#japanese)

---

## English

### Overview

The SEM Particle Size Distribution Analysis System is a comprehensive web application built with Streamlit for analyzing particle size distributions from SEM (Scanning Electron Microscope) images. The system provides an intuitive interface for image processing, particle detection, and statistical analysis with interactive visualization capabilities.

### Features

#### 🖼️ Image Processing
- **Multi-format Support**: TIFF, PNG, BMP, JPG image formats
- **Interactive Scale Setting**: Mouse-operated line drawing for precise scale calibration
- **Advanced Preprocessing**: Gaussian filtering, median filtering, contrast adjustment
- **Auto-adjustment**: Intelligent parameter optimization based on image characteristics

#### 🔍 Particle Detection
- **Adaptive Thresholding**: Multiple algorithms (Otsu, Li, Yen, Triangle, Isodata)
- **Flexible Parameters**: Configurable area and circularity filters
- **ROI Exclusion**: Bottom region exclusion for sample preparation artifacts
- **Real-time Preview**: Instant visualization of detection results

#### 📊 Size Analysis
- **Multiple Metrics**: Short axis, long axis, mean diameter, equivalent diameter
- **Statistical Analysis**: Geometric mean, geometric standard deviation
- **Interactive Histograms**: Linear and logarithmic scale options
- **Data Export**: CSV download with detailed measurements

#### 🌐 User Interface
- **Bilingual Support**: Japanese and English interface
- **Responsive Design**: Optimized for various screen sizes
- **Interactive Canvas**: streamlit-drawable-canvas integration
- **Real-time Updates**: Dynamic parameter adjustment

### Installation

#### Prerequisites
- Python 3.8 or higher
- pip package manager

#### Local Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd SEMParticleAnalyzer
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
streamlit run main.py
```

#### Docker Installation

1. **Using Docker Compose (Recommended)**
```bash
docker-compose up -d
```

2. **Using Docker directly**
```bash
docker build -t sem-analyzer .
docker run -p 8501:8501 sem-analyzer
```

### Usage

#### 1. Image Loading
- Upload your SEM image using the file uploader
- Supported formats: TIFF, PNG, BMP, JPG
- The image will be displayed with basic information

#### 2. Scale Setting
- **Interactive Method**: Draw a line on a known length using the canvas
- **Manual Method**: Enter pixel length and actual length manually
- Set the scale in micrometers (μm)

#### 3. Image Preprocessing
- **Auto Adjustment**: Click for intelligent parameter optimization
- **Manual Adjustment**: Fine-tune parameters using sliders
  - Gaussian Filter: Noise reduction
  - Median Filter: Salt-and-pepper noise removal
  - Black/White Point: Contrast adjustment

#### 4. Particle Detection
- Configure detection parameters:
  - **Image Polarity**: White/black background selection
  - **Threshold Method**: Choose appropriate algorithm
  - **Size Filters**: Set minimum/maximum area
  - **Circularity Filter**: Exclude non-circular objects
- Preview results in real-time

#### 5. Size Analysis
- View statistical summary
- Explore interactive histograms
- Download results as CSV
- Generate analysis reports

### Technical Specifications

#### Dependencies
- **Streamlit**: 1.24.0 (Web framework)
- **OpenCV**: 4.8.0+ (Image processing)
- **scikit-image**: 0.21.0+ (Advanced image analysis)
- **NumPy**: 1.24.0+ (Numerical computing)
- **Pandas**: 2.0.0+ (Data manipulation)
- **Matplotlib**: 3.7.0+ (Plotting)
- **Plotly**: 5.15.0+ (Interactive visualization)
- **streamlit-drawable-canvas**: 0.9.2 (Interactive drawing)

#### System Requirements
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 1GB free space
- **Browser**: Modern web browser with JavaScript enabled
- **Network**: Internet connection for initial setup

### Project Structure

```
SEMParticleAnalyzer/
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose configuration
├── .gitignore             # Git ignore rules
├── README.md              # This file
├── config/                # Configuration files
│   ├── __init__.py
│   ├── languages.py       # Multilingual text definitions
│   └── settings.py        # Application settings
├── modules/               # Core application modules
│   ├── __init__.py
│   ├── image_loader.py    # Image loading and scale setting
│   ├── image_processor.py # Image preprocessing
│   ├── particle_detector.py # Particle detection algorithms
│   ├── size_analyzer.py   # Size analysis and statistics
│   └── ui_components.py   # UI helper components
├── utils/                 # Utility functions
│   ├── __init__.py
│   ├── image_utils.py     # Image processing utilities
│   ├── math_utils.py      # Mathematical calculations
│   └── export_utils.py    # Data export functions
└── assets/               # Static assets
    └── styles.css        # Custom CSS styles
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### License

This project is licensed under the MIT License - see the LICENSE file for details.

### Support

For support, please open an issue on the GitHub repository or contact the development team.

---

## Japanese

### 概要

SEM粒径分布解析システムは、SEM（走査電子顕微鏡）画像から粒径分布を解析するためのStreamlitベースの包括的なWebアプリケーションです。画像処理、粒子検出、統計解析のための直感的なインターフェースとインタラクティブな可視化機能を提供します。

### 機能

#### 🖼️ 画像処理
- **多形式対応**: TIFF、PNG、BMP、JPG画像形式をサポート
- **インタラクティブスケール設定**: マウス操作による線描画で精密なスケール校正
- **高度な前処理**: ガウシアンフィルタ、メディアンフィルタ、コントラスト調整
- **自動調整**: 画像特性に基づくインテリジェントなパラメータ最適化

#### 🔍 粒子検出
- **適応的閾値処理**: 複数のアルゴリズム（Otsu、Li、Yen、Triangle、Isodata）
- **柔軟なパラメータ**: 設定可能な面積と円形度フィルタ
- **ROI除外**: サンプル調製アーティファクトのための底部領域除外
- **リアルタイムプレビュー**: 検出結果の即座の可視化

#### 📊 サイズ解析
- **複数の指標**: 短軸、長軸、平均直径、等価直径
- **統計解析**: 幾何平均、幾何標準偏差
- **インタラクティブヒストグラム**: 線形および対数スケールオプション
- **データエクスポート**: 詳細な測定値のCSVダウンロード

#### 🌐 ユーザーインターフェース
- **多言語対応**: 日本語と英語のインターフェース
- **レスポンシブデザイン**: 様々な画面サイズに最適化
- **インタラクティブキャンバス**: streamlit-drawable-canvas統合
- **リアルタイム更新**: 動的なパラメータ調整

### インストール

#### 前提条件
- Python 3.8以上
- pipパッケージマネージャー

#### ローカルインストール

1. **リポジトリのクローン**
```bash
git clone <repository-url>
cd SEMParticleAnalyzer
```

2. **仮想環境の作成**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **依存関係のインストール**
```bash
pip install -r requirements.txt
```

4. **アプリケーションの実行**
```bash
streamlit run main.py
```

#### Dockerインストール

1. **Docker Composeを使用（推奨）**
```bash
docker-compose up -d
```

2. **Dockerを直接使用**
```bash
docker build -t sem-analyzer .
docker run -p 8501:8501 sem-analyzer
```

### 使用方法

#### 1. 画像読み込み
- ファイルアップローダーを使用してSEM画像をアップロード
- 対応形式：TIFF、PNG、BMP、JPG
- 画像が基本情報と共に表示されます

#### 2. スケール設定
- **インタラクティブ方式**: キャンバス上で既知の長さに線を描画
- **手動方式**: ピクセル長と実際の長さを手動入力
- マイクロメートル（μm）単位でスケールを設定

#### 3. 画像前処理
- **自動調整**: インテリジェントなパラメータ最適化のためにクリック
- **手動調整**: スライダーを使用してパラメータを微調整
  - ガウシアンフィルタ: ノイズ除去
  - メディアンフィルタ: 塩胡椒ノイズ除去
  - ブラック/ホワイトポイント: コントラスト調整

#### 4. 粒子検出
- 検出パラメータの設定：
  - **画像極性**: 白/黒背景の選択
  - **閾値方法**: 適切なアルゴリズムの選択
  - **サイズフィルタ**: 最小/最大面積の設定
  - **円形度フィルタ**: 非円形オブジェクトの除外
- リアルタイムで結果をプレビュー

#### 5. サイズ解析
- 統計サマリーの表示
- インタラクティブヒストグラムの探索
- CSV形式での結果ダウンロード
- 解析レポートの生成

### 技術仕様

#### 依存関係
- **Streamlit**: 1.24.0（Webフレームワーク）
- **OpenCV**: 4.8.0+（画像処理）
- **scikit-image**: 0.21.0+（高度な画像解析）
- **NumPy**: 1.24.0+（数値計算）
- **Pandas**: 2.0.0+（データ操作）
- **Matplotlib**: 3.7.0+（プロット）
- **Plotly**: 5.15.0+（インタラクティブ可視化）
- **streamlit-drawable-canvas**: 0.9.2（インタラクティブ描画）

#### システム要件
- **RAM**: 最小4GB、推奨8GB
- **ストレージ**: 1GB以上の空き容量
- **ブラウザ**: JavaScript対応の最新Webブラウザ
- **ネットワーク**: 初期セットアップ用のインターネット接続

### プロジェクト構造

```
SEMParticleAnalyzer/
├── main.py                 # メインアプリケーションエントリーポイント
├── requirements.txt        # Python依存関係
├── Dockerfile             # Docker設定
├── docker-compose.yml     # Docker Compose設定
├── .gitignore             # Git無視ルール
├── README.md              # このファイル
├── config/                # 設定ファイル
│   ├── __init__.py
│   ├── languages.py       # 多言語テキスト定義
│   └── settings.py        # アプリケーション設定
├── modules/               # コアアプリケーションモジュール
│   ├── __init__.py
│   ├── image_loader.py    # 画像読み込みとスケール設定
│   ├── image_processor.py # 画像前処理
│   ├── particle_detector.py # 粒子検出アルゴリズム
│   ├── size_analyzer.py   # サイズ解析と統計
│   └── ui_components.py   # UIヘルパーコンポーネント
├── utils/                 # ユーティリティ関数
│   ├── __init__.py
│   ├── image_utils.py     # 画像処理ユーティリティ
│   ├── math_utils.py      # 数学的計算
│   └── export_utils.py    # データエクスポート関数
└── assets/               # 静的アセット
    └── styles.css        # カスタムCSSスタイル
```

### 貢献

1. リポジトリをフォーク
2. 機能ブランチを作成（`git checkout -b feature/amazing-feature`）
3. 変更をコミット（`git commit -m 'Add amazing feature'`）
4. ブランチにプッシュ（`git push origin feature/amazing-feature`）
5. プルリクエストを開く

### ライセンス

このプロジェクトはMITライセンスの下でライセンスされています - 詳細はLICENSEファイルを参照してください。

### サポート

サポートについては、GitHubリポジトリでissueを開くか、開発チームにお問い合わせください。

---

## Screenshots / スクリーンショット

### Image Loading and Scale Setting / 画像読み込みとスケール設定
![Scale Setting](docs/images/scale-setting.png)

### Particle Detection / 粒子検出
![Particle Detection](docs/images/particle-detection.png)

### Size Analysis / サイズ解析
![Size Analysis](docs/images/size-analysis.png)

---

## Changelog / 変更履歴

### v1.0.0 (2025-05-29)
- ✨ Initial release / 初回リリース
- 🖼️ Image loading and scale setting / 画像読み込みとスケール設定
- 🔍 Particle detection algorithms / 粒子検出アルゴリズム
- 📊 Size analysis and statistics / サイズ解析と統計
- 🌐 Bilingual support (Japanese/English) / 多言語対応（日本語/英語）
- 🐳 Docker containerization / Dockerコンテナ化
- 🎨 Interactive canvas drawing / インタラクティブキャンバス描画

---

**Made with ❤️ for the scientific community**