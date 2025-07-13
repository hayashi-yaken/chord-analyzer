import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List, Tuple
import librosa

def render_advanced_analysis_page():
    """高度な分析ページを表示"""
    
    st.title("🔬 高度な分析")
    st.markdown("より詳細な音楽分析機能を提供します")
    
    # タブを作成
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎵 スペクトログラム分析", 
        "🎼 コード進行パターン", 
        "📊 統計分析", 
        "🎯 音楽的特徴"
    ])
    
    with tab1:
        render_spectrogram_analysis()
    
    with tab2:
        render_chord_pattern_analysis()
    
    with tab3:
        render_statistical_analysis()
    
    with tab4:
        render_musical_features()

def render_spectrogram_analysis():
    """スペクトログラム分析"""
    st.subheader("🎵 スペクトログラム分析")
    
    if 'audio_path' not in st.session_state or not st.session_state.audio_path:
        st.warning("音声ファイルをアップロードしてください")
        return
    
    audio_path = st.session_state.audio_path
    
    # スペクトログラムのパラメータ
    col1, col2 = st.columns(2)
    
    with col1:
        window_size = st.slider("ウィンドウサイズ", 512, 4096, 2048, step=512)
        hop_length = st.slider("ホップ長", 128, 1024, 512, step=128)
    
    with col2:
        n_mels = st.slider("メル周波数ビン数", 64, 256, 128, step=32)
        fmax = st.slider("最大周波数 (Hz)", 2000, 8000, 4000, step=500)
    
    if st.button("スペクトログラムを生成"):
        with st.spinner("スペクトログラムを生成中..."):
            try:
                # 音声ファイルを読み込み
                y, sr = librosa.load(audio_path, sr=None)
                
                # メルスペクトログラムを計算
                mel_spectrogram = librosa.feature.melspectrogram(
                    y=y, 
                    sr=sr, 
                    n_mels=n_mels,
                    hop_length=hop_length,
                    n_fft=window_size,
                    fmax=fmax
                )
                
                # dBスケールに変換
                mel_spectrogram_db = librosa.power_to_db(mel_spectrogram, ref=np.max)
                
                # プロットを作成
                fig = go.Figure(data=go.Heatmap(
                    z=mel_spectrogram_db,
                    colorscale='Viridis',
                    x=librosa.times_like(mel_spectrogram_db, sr=sr, hop_length=hop_length),
                    y=librosa.mel_frequencies(n_mels=n_mels, fmax=fmax),
                    colorbar=dict(title="dB")
                ))
                
                fig.update_layout(
                    title="メルスペクトログラム",
                    xaxis_title="時間 (秒)",
                    yaxis_title="周波数 (Hz)",
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"スペクトログラム生成中にエラーが発生しました: {str(e)}")

def render_chord_pattern_analysis():
    """コード進行パターン分析"""
    st.subheader("🎼 コード進行パターン分析")
    
    if 'analysis_result' not in st.session_state or not st.session_state.analysis_result:
        st.warning("コード分析を実行してください")
        return
    
    analysis_result = st.session_state.analysis_result
    chords: List[Tuple[float, float, str]] = analysis_result.get('chords', [])
    
    if not chords:
        st.warning("コード進行データがありません")
        return
    
    # 有効なコードのみをフィルタリング
    valid_chords = [str(label).strip() for _, _, label in chords if str(label).strip() and str(label).strip() != 'nan']
    
    if not valid_chords:
        st.warning("有効なコード進行データがありません")
        return
    
    # パターン分析
    st.write("**🔍 コード進行パターン**")
    
    # 2コードの組み合わせを分析
    bigrams = []
    for i in range(len(valid_chords) - 1):
        bigrams.append(f"{valid_chords[i]} → {valid_chords[i+1]}")
    
    if bigrams:
        bigram_counts = pd.Series(bigrams).value_counts()
        
        # 上位10個のパターンを表示
        st.write("**最も頻出する2コードパターン:**")
        for i, (pattern, count) in enumerate(bigram_counts.head(10).items()):
            st.write(f"{i+1}. {pattern}: {count}回")
    
    # コード進行の複雑さを分析
    st.write("**📈 コード進行の複雑さ**")
    
    # ユニークコードの割合
    unique_ratio = len(set(valid_chords)) / len(valid_chords) if valid_chords else 0
    st.metric("コード多様性", f"{unique_ratio:.2%}")
    
    # コード変化の頻度
    changes = sum(1 for i in range(1, len(valid_chords)) if valid_chords[i] != valid_chords[i-1])
    change_ratio = changes / (len(valid_chords) - 1) if len(valid_chords) > 1 else 0
    st.metric("コード変化頻度", f"{change_ratio:.2%}")

def render_statistical_analysis():
    """統計分析"""
    st.subheader("📊 統計分析")
    
    if 'analysis_result' not in st.session_state or not st.session_state.analysis_result:
        st.warning("コード分析を実行してください")
        return
    
    analysis_result = st.session_state.analysis_result
    stats = analysis_result.get('statistics', {})
    
    if not stats:
        st.warning("統計データがありません")
        return
    
    # 基本統計
    st.write("**📈 基本統計**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("総コード数", stats.get('total_chords', 0))
    
    with col2:
        st.metric("ユニークコード数", stats.get('unique_chords', 0))
    
    with col3:
        avg_duration = analysis_result.get('duration', 0) / stats.get('total_chords', 1)
        st.metric("平均コード持続時間", f"{avg_duration:.1f}秒")
    
    # コード分布の詳細分析
    chord_dist = stats.get('chord_distribution', {})
    
    if chord_dist:
        st.write("**📊 コード分布の詳細**")
        
        # データフレームを作成
        df = pd.DataFrame([
            {'コード': chord, '出現回数': count, '割合': count/stats['total_chords']}
            for chord, count in chord_dist.items()
        ]).sort_values('出現回数', ascending=False)
        
        st.dataframe(df, use_container_width=True)
        
        # 円グラフ
        fig = px.pie(
            df, 
            values='出現回数', 
            names='コード',
            title="コード分布"
        )
        st.plotly_chart(fig, use_container_width=True)

def render_musical_features():
    """音楽的特徴の分析"""
    st.subheader("🎯 音楽的特徴")
    
    if 'analysis_result' not in st.session_state or not st.session_state.analysis_result:
        st.warning("コード分析を実行してください")
        return
    
    analysis_result = st.session_state.analysis_result
    chords: List[Tuple[float, float, str]] = analysis_result.get('chords', [])
    
    if not chords:
        st.warning("コード進行データがありません")
        return
    
    # 有効なコードのみをフィルタリング
    valid_chords = [str(label).strip() for _, _, label in chords if str(label).strip() and str(label).strip() != 'nan']
    
    if not valid_chords:
        st.warning("有効なコード進行データがありません")
        return
    
    # 音楽的特徴を分析
    st.write("**🎵 音楽的特徴分析**")
    
    # メジャー/マイナーコードの分析
    major_chords = [c for c in valid_chords if 'm' not in c and c != 'N']
    minor_chords = [c for c in valid_chords if 'm' in c]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("メジャーコード", len(major_chords))
        if valid_chords:
            st.metric("メジャーコード割合", f"{len(major_chords)/len(valid_chords):.1%}")
    
    with col2:
        st.metric("マイナーコード", len(minor_chords))
        if valid_chords:
            st.metric("マイナーコード割合", f"{len(minor_chords)/len(valid_chords):.1%}")
    
    # コード進行の特徴
    st.write("**🎼 コード進行の特徴**")
    
    # 最も長く続くコード
    if valid_chords:
        current_chord = valid_chords[0]
        max_streak = 1
        current_streak = 1
        
        for chord in valid_chords[1:]:
            if chord == current_chord:
                current_streak += 1
            else:
                if current_streak > max_streak:
                    max_streak = current_streak
                current_chord = chord
                current_streak = 1
        
        if current_streak > max_streak:
            max_streak = current_streak
        
        st.metric("最長コード持続", f"{max_streak}回")
    
    # コード進行の複雑さスコア
    if len(valid_chords) > 1:
        complexity_score = len(set(valid_chords)) / len(valid_chords) * 100
        st.metric("複雑さスコア", f"{complexity_score:.1f}/100")
        
        if complexity_score < 30:
            st.info("この曲は比較的シンプルなコード進行です")
        elif complexity_score < 70:
            st.info("この曲は中程度の複雑さのコード進行です")
        else:
            st.info("この曲は複雑なコード進行です") 