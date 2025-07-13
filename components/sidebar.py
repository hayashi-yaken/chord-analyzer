import streamlit as st
from typing import Dict, Any

def render_sidebar():
    """
    サイドバーを表示
    """
    st.sidebar.title("🎸 Chord Analyzer")
    st.sidebar.markdown("---")
    
    # アプリケーション情報
    st.sidebar.subheader("ℹ️ アプリケーション情報")
    st.sidebar.markdown("""
    **Chord Analyzer** は、コード推定のための機械学習モデルを使用して音楽のコード進行を分析するアプリケーションです。
    
    ### 対応形式
    - MP3
    - WAV
    - FLAC
    - M4A
    - OGG
    """)
    
    # 分析設定
    st.sidebar.subheader("⚙️ 分析設定")
    
    # 分析精度の設定
    analysis_quality = st.sidebar.selectbox(
        "分析精度",
        ["高精度", "標準", "高速"],
        help="高精度ほど時間がかかりますが、より正確な結果が得られます"
    )
    
    # 表示設定
    st.sidebar.subheader("📊 表示設定")
    
    show_timeline = st.sidebar.checkbox("タイムライン表示", value=True)
    show_distribution = st.sidebar.checkbox("分布図表示", value=True)
    show_statistics = st.sidebar.checkbox("統計情報表示", value=True)
    
    # エクスポート設定
    st.sidebar.subheader("💾 エクスポート設定")
    
    export_format = st.sidebar.selectbox(
        "エクスポート形式",
        ["CSV", "JSON", "PDF"]
    )
    
    # ヘルプとサポート
    st.sidebar.markdown("---")
    st.sidebar.subheader("❓ ヘルプ")
    
    if st.sidebar.button("使い方"):
        show_help_modal()
    
    if st.sidebar.button("バグ報告"):
        show_bug_report_modal()
    
    # 設定を辞書として返す
    settings = {
        'analysis_quality': analysis_quality,
        'show_timeline': show_timeline,
        'show_distribution': show_distribution,
        'show_statistics': show_statistics,
        'export_format': export_format
    }
    
    return settings

def show_help_modal():
    """
    ヘルプモーダルを表示
    """
    st.sidebar.markdown("""
    ### 使い方
    
    1. **ファイルアップロード**: 音声ファイルをアップロードします
    2. **分析実行**: 「分析開始」ボタンをクリックします
    3. **結果確認**: 分析結果を確認します
    
    ### 分析結果の見方
    
    - **タイムライン**: 時間軸でのコード進行
    - **分布図**: コードの出現頻度
    - **統計情報**: コードの統計データ
    """)

def show_bug_report_modal():
    """
    バグ報告モーダルを表示
    """
    st.sidebar.markdown("""
    ### バグ報告
    
    問題が発生した場合は、以下の情報を含めて報告してください：
    
    - 使用したファイル形式
    - エラーメッセージ
    - 期待される動作
    
    **連絡先**: 開発チームまでお問い合わせください
    """)

def display_file_info(audio_path: str, filename: str):
    """
    ファイル情報をサイドバーに表示
    
    Args:
        audio_path: 音声ファイルのパス
        filename: ファイル名
    """
    st.sidebar.markdown("---")
    st.sidebar.subheader("📁 ファイル情報")
    
    st.sidebar.write(f"**ファイル名**: {filename}")
    st.sidebar.write(f"**パス**: {audio_path}")
    
    # ファイルサイズを取得
    try:
        import os
        file_size = os.path.getsize(audio_path)
        st.sidebar.write(f"**サイズ**: {file_size / 1024:.1f} KB")
    except:
        st.sidebar.write("**サイズ**: 不明")

def display_analysis_status(analysis_result: Dict[str, Any]):
    """
    分析状況をサイドバーに表示
    
    Args:
        analysis_result: 分析結果
    """
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 分析状況")
    
    if analysis_result:
        stats = analysis_result.get('statistics', {})
        
        st.sidebar.success("✅ 分析完了")
        st.sidebar.write(f"**分析時間**: {analysis_result.get('duration', 0):.1f}秒")
        st.sidebar.write(f"**検出コード数**: {stats.get('total_chords', 0)}")
        st.sidebar.write(f"**ユニークコード数**: {stats.get('unique_chords', 0)}")
    else:
        st.sidebar.info("⏳ 分析待ち")

def export_results(analysis_result: Dict[str, Any], format_type: str):
    """
    分析結果をエクスポート
    
    Args:
        analysis_result: 分析結果
        format_type: エクスポート形式
    """
    if not analysis_result:
        st.sidebar.warning("エクスポートする分析結果がありません")
        return
    
    st.sidebar.subheader("💾 エクスポート")
    
    if format_type == "CSV":
        export_to_csv(analysis_result)
    elif format_type == "JSON":
        export_to_json(analysis_result)
    elif format_type == "PDF":
        export_to_pdf(analysis_result)

def export_to_csv(analysis_result: Dict[str, Any]):
    """
    CSV形式でエクスポート
    
    Args:
        analysis_result: 分析結果
    """
    import pandas as pd
    
    # コード進行データ
    if 'chords' in analysis_result and 'times' in analysis_result:
        df = pd.DataFrame({
            '時間 (秒)': analysis_result['times'],
            'コード': analysis_result['chords']
        })
        
        csv = df.to_csv(index=False)
        st.sidebar.download_button(
            label="CSVダウンロード",
            data=csv,
            file_name="chord_analysis.csv",
            mime="text/csv"
        )

def export_to_json(analysis_result: Dict[str, Any]):
    """
    JSON形式でエクスポート
    
    Args:
        analysis_result: 分析結果
    """
    import json
    
    json_str = json.dumps(analysis_result, indent=2, ensure_ascii=False)
    st.sidebar.download_button(
        label="JSONダウンロード",
        data=json_str,
        file_name="chord_analysis.json",
        mime="application/json"
    )

def export_to_pdf(analysis_result: Dict[str, Any]):
    """
    PDF形式でエクスポート（実装予定）
    
    Args:
        analysis_result: 分析結果
    """
    st.sidebar.info("PDFエクスポート機能は開発中です") 