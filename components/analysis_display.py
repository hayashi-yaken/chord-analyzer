import streamlit as st
from typing import Dict, Any, List, Tuple
import pandas as pd

def display_analysis_results(analysis_result: Dict[str, Any]):
    """
    分析結果を表示
    Args:
        analysis_result: 分析結果の辞書
    """
    if not analysis_result:
        st.warning("分析結果がありません。")
        return
    st.subheader("🎼 コード分析結果")
    # 統計情報を表示
    stats = analysis_result.get('statistics', {})
    if stats:
        display_statistics(stats)
    # コード進行のタイムライン
    if 'chords' in analysis_result:
        display_chord_timeline(analysis_result)
    # コード分布
    if 'statistics' in analysis_result:
        display_chord_distribution(analysis_result)

def display_statistics(stats: Dict[str, Any]):
    st.write("**📈 統計情報**")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("総コード数", stats.get('total_chords', 0))
    with col2:
        st.metric("ユニークコード数", stats.get('unique_chords', 0))
    with col3:
        most_common = stats.get('most_common_chord', 'N/A')
        st.metric("最も頻出コード", most_common)
    with col4:
        most_common_count = stats.get('most_common_count', 0)
        st.metric("最頻出回数", most_common_count)

def display_chord_timeline(analysis_result: Dict[str, Any]):
    st.write("**⏰ コード進行タイムライン**")
    chords: List[Tuple[float, float, str]] = analysis_result['chords']
    # 有効なデータのみをフィルタリング
    valid_data = []
    for start, end, label in chords:
        label_str = str(label).strip()
        if label_str and label_str != 'nan':
            valid_data.append({
                '開始 (秒)': start,
                '終了 (秒)': end,
                'コード': label_str
            })
    if not valid_data:
        st.warning("有効なコード進行データがありません")
        return
    df = pd.DataFrame(valid_data)
    st.dataframe(df, use_container_width=True)
    # プロット表示
    if 'timeline_plot' in analysis_result:
        st.plotly_chart(analysis_result['timeline_plot'], use_container_width=True)

def display_chord_distribution(analysis_result: Dict[str, Any]):
    st.write("**📊 コード分布**")
    stats = analysis_result['statistics']
    chord_dist = stats.get('chord_distribution', {})
    if chord_dist:
        df = pd.DataFrame([
            {'コード': chord, '出現回数': count}
            for chord, count in chord_dist.items()
        ]).sort_values('出現回数', ascending=False)
        st.dataframe(df, use_container_width=True)
        if 'distribution_plot' in analysis_result:
            st.plotly_chart(analysis_result['distribution_plot'], use_container_width=True)

def display_chord_progression_summary(analysis_result: Dict[str, Any]):
    if not analysis_result or 'chords' not in analysis_result:
        return
    chords: List[Tuple[float, float, str]] = analysis_result['chords']
    # 有効なコードのみをフィルタリング
    valid_chords = [str(label).strip() for _, _, label in chords if str(label).strip() and str(label).strip() != 'nan']
    if not valid_chords:
        st.warning("有効なコード進行データがありません")
        return
    st.write("**🎵 コード進行サマリー**")
    chord_progression = " → ".join(valid_chords)
    st.text_area("コード進行", chord_progression, height=100)
    if len(valid_chords) > 1:
        changes = sum(1 for i in range(1, len(valid_chords)) if valid_chords[i] != valid_chords[i-1])
        st.metric("コード変化回数", changes)
        duration = analysis_result.get('duration', 0)
        avg_duration = duration / len(valid_chords) if len(valid_chords) > 0 else 0
        st.metric("平均コード持続時間", f"{avg_duration:.1f}秒")

def display_analysis_progress():
    progress_bar = st.progress(0)
    status_text = st.empty()
    return progress_bar, status_text

def update_analysis_progress(progress_bar, status_text, progress: float, message: str):
    progress_bar.progress(progress)
    status_text.text(message) 