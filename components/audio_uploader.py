import streamlit as st
import tempfile
from typing import Optional, Tuple

def audio_file_uploader() -> Tuple[Optional[str], Optional[str]]:
    """
    音声ファイルアップロードコンポーネント
    
    Returns:
        (ファイルパス, ファイル名) のタプル
    """
    st.subheader("🎵 音声ファイルをアップロード")
    
    # ファイルアップロード
    uploaded_file = st.file_uploader(
        "音声ファイルを選択してください",
        type=['mp3', 'wav', 'flac', 'm4a', 'ogg'],
        help="対応形式: MP3, WAV, FLAC, M4A, OGG"
    )
    
    if uploaded_file is not None:
        # ファイル情報を表示
        file_details = {
            "ファイル名": uploaded_file.name,
            "ファイルサイズ": f"{uploaded_file.size / 1024:.1f} KB",
            "ファイルタイプ": uploaded_file.type
        }
        
        st.write("**ファイル情報:**")
        for key, value in file_details.items():
            st.write(f"- {key}: {value}")
        
        # 一時ファイルとして保存
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            temp_path = tmp_file.name
        
        return temp_path, uploaded_file.name
    
    return None, None

def display_audio_player(audio_path: str, filename: str):
    """
    音声プレイヤーを表示
    
    Args:
        audio_path: 音声ファイルのパス
        filename: ファイル名
    """
    st.subheader("🎧 音声プレイヤー")
    
    # 音声ファイルを読み込んでプレイヤーを表示
    with open(audio_path, "rb") as audio_file:
        audio_bytes = audio_file.read()
    
    st.audio(audio_bytes, format=f'audio/{filename.split(".")[-1]}')
    
    # ファイルパスを表示（デバッグ用）
    if st.checkbox("デバッグ情報を表示"):
        st.code(f"ファイルパス: {audio_path}")

def audio_info_display(audio_info: dict):
    """
    音声ファイルの基本情報を表示
    
    Args:
        audio_info: 音声情報の辞書
    """
    if not audio_info:
        return
    
    st.subheader("📊 音声ファイル情報")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("再生時間", f"{audio_info['duration']:.1f}秒")
    
    with col2:
        st.metric("サンプリングレート", f"{audio_info['sample_rate']:,} Hz")
    
    with col3:
        st.metric("サンプル数", f"{audio_info['num_samples']:,}")
    
    # 詳細情報
    with st.expander("詳細情報"):
        st.json(audio_info) 