import numpy as np
import librosa
from madmom.audio.chroma import DeepChromaProcessor
from madmom.features.chords import DeepChromaChordRecognitionProcessor
from madmom.processors import SequentialProcessor
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import Tuple, List, Dict, Any
import tempfile
import os

class ChordAnalyzer:
    """
    音楽コード分析を行うクラス
    コード進行は常にList[Tuple[float, float, str]]型（開始, 終了, コード名）で管理
    """
    def __init__(self):
        self.chroma_processor = DeepChromaProcessor()
        self.chord_processor = DeepChromaChordRecognitionProcessor()
        self.processor = SequentialProcessor([
            self.chroma_processor,
            self.chord_processor
        ])

    def analyze_audio_file(self, audio_path: str) -> Dict[str, Any]:
        """
        音声ファイルを分析してコード進行を取得
        Returns:
            {'chords': List[Tuple[float, float, str]], ...}
        """
        try:
            # コード進行を分析
            chords_arr = self.processor(audio_path)
            # madmomはstructured arrayで返す場合がある
            if hasattr(chords_arr, 'tolist'):
                chords_arr = chords_arr.tolist()
            elif isinstance(chords_arr, np.ndarray):
                chords_arr = chords_arr.tolist()
            # ここでchords_arrはList[Tuple[float, float, str]]
            chords: List[Tuple[float, float, str]] = []
            for c in chords_arr:
                # cがタプルで3要素ならそのまま
                if isinstance(c, tuple) and len(c) == 3:
                    chords.append((float(c[0]), float(c[1]), str(c[2])))
                # それ以外は無視
            if not chords:
                st.warning("コード進行が検出されませんでした。")
                return None
            # 統計情報
            chord_stats = self._analyze_chord_statistics(chords)
            return {
                'chords': chords,
                'statistics': chord_stats,
                'duration': chords[-1][1] if len(chords) > 0 else 0
            }
        except Exception as e:
            st.error(f"音声ファイルの分析中にエラーが発生しました: {str(e)}")
            return None

    def _analyze_chord_statistics(self, chords: List[Tuple[float, float, str]]) -> Dict[str, Any]:
        """
        コード進行の統計情報を分析
        Args:
            chords: List[Tuple[float, float, str]]
        Returns:
            統計情報の辞書
        """
        if not chords:
            return {}
        chord_counts = {}
        for _, _, label in chords:
            label_str = str(label).strip()
            if label_str and label_str != 'nan':
                if label_str in chord_counts:
                    chord_counts[label_str] += 1
                else:
                    chord_counts[label_str] = 1
        most_common = max(chord_counts.items(), key=lambda x: x[1]) if chord_counts else (None, 0)
        unique_chords = len(chord_counts)
        return {
            'total_chords': len(chords),
            'unique_chords': unique_chords,
            'most_common_chord': most_common[0],
            'most_common_count': most_common[1],
            'chord_distribution': chord_counts
        }

    def create_chord_timeline_plot(self, analysis_result: Dict[str, Any]) -> go.Figure:
        """
        コード進行のタイムライン図を作成
        Args:
            analysis_result: 分析結果
        Returns:
            PlotlyのFigureオブジェクト
        """
        if not analysis_result or 'chords' not in analysis_result:
            return go.Figure()
        chords: List[Tuple[float, float, str]] = analysis_result['chords']
        if not chords:
            return go.Figure()
        valid_chords = []
        valid_times = []
        for start, _, label in chords:
            label_str = str(label).strip()
            if label_str and label_str != 'nan':
                valid_chords.append(label_str)
                valid_times.append(start)
        if not valid_chords:
            return go.Figure()
        unique_chords = list(set(valid_chords))
        colors = px.colors.qualitative.Set3[:len(unique_chords)]
        color_map = dict(zip(unique_chords, colors))
        chord_colors = [color_map.get(chord, '#808080') for chord in valid_chords]
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=valid_times,
            y=valid_chords,
            mode='markers',
            marker=dict(
                size=10,
                color=chord_colors,
                line=dict(width=1, color='white')
            ),
            text=valid_chords,
            hovertemplate='<b>%{text}</b><br>時間: %{x:.1f}秒<extra></extra>',
            name='コード進行'
        ))
        fig.update_layout(
            title='コード進行のタイムライン',
            xaxis_title='時間 (秒)',
            yaxis_title='コード',
            height=400,
            showlegend=False
        )
        return fig

    def create_chord_distribution_plot(self, analysis_result: Dict[str, Any]) -> go.Figure:
        """
        コードの分布図を作成
        Args:
            analysis_result: 分析結果
        Returns:
            PlotlyのFigureオブジェクト
        """
        if not analysis_result or 'statistics' not in analysis_result:
            return go.Figure()
        stats = analysis_result['statistics']
        chord_dist = stats.get('chord_distribution', {})
        if not chord_dist:
            return go.Figure()
        valid_chord_dist = {k: v for k, v in chord_dist.items() if k and k != 'nan' and v > 0}
        if not valid_chord_dist:
            return go.Figure()
        chord_names = list(valid_chord_dist.keys())
        chord_counts = list(valid_chord_dist.values())
        fig = go.Figure(data=[
            go.Bar(
                x=chord_names,
                y=chord_counts,
                marker_color='lightblue',
                text=chord_counts,
                textposition='auto',
            )
        ])
        fig.update_layout(
            title='コードの出現回数',
            xaxis_title='コード',
            yaxis_title='出現回数',
            height=400
        )
        return fig

    def get_audio_info(self, audio_path: str) -> Dict[str, Any]:
        try:
            y, sr = librosa.load(audio_path, sr=None)
            duration = librosa.get_duration(y=y, sr=sr)
            sample_rate = sr
            num_samples = len(y)
            return {
                'duration': duration,
                'sample_rate': sample_rate,
                'num_samples': num_samples,
                'file_path': audio_path
            }
        except Exception as e:
            st.error(f"音声ファイル情報の取得中にエラーが発生しました: {str(e)}")
            return None 