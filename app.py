import streamlit as st
import os
from typing import List, Dict, Any, Tuple

# カスタムモジュールのインポート
from utils.chord_analyzer import ChordAnalyzer
from utils.midi_generator import chords_to_midi
from components.audio_uploader import audio_file_uploader, display_audio_player, audio_info_display
from components.analysis_display import (
    display_analysis_results, 
    display_chord_progression_summary,
    display_analysis_progress,
    update_analysis_progress
)
from components.sidebar import (
    render_sidebar, 
    display_file_info, 
    display_analysis_status,
    export_results
)
from components.midi_player import midi_player
from pages.advanced_analysis import render_advanced_analysis_page

# ページ設定
st.set_page_config(
    page_title="Chord Analyzer",
    page_icon="🎸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# セッション状態の初期化
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'audio_path' not in st.session_state:
    st.session_state.audio_path = None
if 'filename' not in st.session_state:
    st.session_state.filename = None

def main():
    """メインアプリケーション"""
    
    # サイドバーを表示
    settings = render_sidebar()
    
    # ページ選択
    page = st.sidebar.selectbox(
        "ページ選択",
        ["🏠 ホーム", "🔬 高度な分析"],
        help="分析機能を選択してください"
    )
    
    if page == "🏠 ホーム":
        render_home_page(settings)
    elif page == "🔬 高度な分析":
        render_advanced_analysis_page()

def render_home_page(settings: Dict[str, Any]):
    """ホームページを表示"""
    
    # ヘッダー
    st.title("🎸 Chord Analyzer")
    st.markdown("コード推定機械学習モデルを使用した音楽コード分析アプリケーション")
    st.markdown("---")
    
    # メインコンテンツ
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # ファイルアップロード
        audio_path, filename = audio_file_uploader()
        
        if audio_path and filename:
            # セッション状態を更新
            st.session_state.audio_path = audio_path
            st.session_state.filename = filename
            
            # ファイル情報をサイドバーに表示
            display_file_info(audio_path, filename)
            
            # 音声プレイヤーを表示
            display_audio_player(audio_path, filename)
            
            # 音声ファイルの基本情報を取得・表示
            analyzer = ChordAnalyzer()
            audio_info = analyzer.get_audio_info(audio_path)
            if audio_info:
                audio_info_display(audio_info)
            
            # 分析ボタン
            if st.button("🔍 コード分析を開始", type="primary"):
                perform_analysis(audio_path, settings)
    
    with col2:
        # 分析状況を表示
        display_analysis_status(st.session_state.analysis_result)
        
        # エクスポート機能
        if st.session_state.analysis_result:
            export_results(st.session_state.analysis_result, settings['export_format'])
    
    # 分析結果の表示
    if st.session_state.analysis_result:
        display_analysis_results(st.session_state.analysis_result)
        display_chord_progression_summary(st.session_state.analysis_result)
        # コード進行からMIDI生成・再生
        chords: List[Tuple[float, float, str]] = st.session_state.analysis_result.get('chords', [])
        # 有効なコードのみ抽出
        valid_chords = [c for c in chords if str(c[2]).strip() and str(c[2]).strip() != 'nan']
        if valid_chords:
            if st.button('🎹 コード進行をMIDIで再生'):
                # コード名だけのリストなら変換
                midi_path = chords_to_midi(valid_chords)
                if midi_path:
                    midi_player(midi_path, label="コード進行MIDI再生")

def perform_analysis(audio_path: str, settings: Dict[str, Any]):
    """コード分析を実行"""
    
    # プログレスバーを表示
    progress_bar, status_text = display_analysis_progress()
    
    try:
        # 分析精度に応じた設定
        quality_settings = {
            "高精度": {"hop_size": 0.05, "window_size": 0.2},
            "標準": {"hop_size": 0.1, "window_size": 0.1},
            "高速": {"hop_size": 0.2, "window_size": 0.05}
        }
        
        current_settings = quality_settings.get(settings['analysis_quality'], quality_settings["標準"])
        
        # 分析の進行状況を更新
        update_analysis_progress(progress_bar, status_text, 0.2, "音声ファイルを読み込み中...")
        
        # ChordAnalyzerを初期化
        analyzer = ChordAnalyzer()
        
        update_analysis_progress(progress_bar, status_text, 0.4, "コード進行を分析中...")
        
        # コード分析を実行
        analysis_result = analyzer.analyze_audio_file(audio_path)
        
        if analysis_result:
            update_analysis_progress(progress_bar, status_text, 0.7, "プロットを生成中...")
            
            # プロットを生成
            if settings['show_timeline']:
                analysis_result['timeline_plot'] = analyzer.create_chord_timeline_plot(analysis_result)
            
            if settings['show_distribution']:
                analysis_result['distribution_plot'] = analyzer.create_chord_distribution_plot(analysis_result)
            
            update_analysis_progress(progress_bar, status_text, 1.0, "分析完了！")
            
            # 結果をセッション状態に保存
            st.session_state.analysis_result = analysis_result
            
            st.success("✅ コード分析が完了しました！")
            
            # ページを再読み込み
            st.rerun()
        else:
            st.error("❌ コード分析に失敗しました。")
            
    except Exception as e:
        st.error(f"❌ 分析中にエラーが発生しました: {str(e)}")
        update_analysis_progress(progress_bar, status_text, 0.0, "エラーが発生しました")

def cleanup_temp_files():
    """一時ファイルをクリーンアップ"""
    if st.session_state.audio_path and os.path.exists(st.session_state.audio_path):
        try:
            os.unlink(st.session_state.audio_path)
        except:
            pass

# アプリケーション終了時のクリーンアップ
import atexit
atexit.register(cleanup_temp_files)

if __name__ == "__main__":
    main()
