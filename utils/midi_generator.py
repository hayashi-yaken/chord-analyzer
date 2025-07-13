import pretty_midi
import tempfile
import streamlit as st
from typing import List, Optional, Tuple

CHORD_ROOT_MAP = {
    'C': 60, 'C#': 61, 'Db': 61, 'D': 62, 'D#': 63, 'Eb': 63,
    'E': 64, 'F': 65, 'F#': 66, 'Gb': 66, 'G': 67, 'G#': 68, 'Ab': 68,
    'A': 69, 'A#': 70, 'Bb': 70, 'B': 71
}

CHORD_TYPE_MAP = {
    '': [0, 4, 7],
    'maj': [0, 4, 7],
    'min': [0, 3, 7],
    'm': [0, 3, 7],
    'dim': [0, 3, 6],
    'aug': [0, 4, 8],
    '7': [0, 4, 7, 10],
    'maj7': [0, 4, 7, 11],
    'm7': [0, 3, 7, 10],
    # 必要に応じて拡張
}

def parse_chord(chord):
    """
    chordがタプル (start, end, chord_name) なら chord_name を使う。
    それ以外はそのまま文字列として扱う。
    """
    if isinstance(chord, tuple) and len(chord) == 3:
        chord_str = chord[2]
    else:
        chord_str = chord
    if not isinstance(chord_str, str):
        chord_str = str(chord_str)
    if ':' in chord_str:
        root, ctype = chord_str.split(':', 1)
    else:
        root, ctype = chord_str, ''
    return root.strip().upper(), ctype.strip()

def chords_list_to_segments(chords: List[str], duration: float = 2.0) -> List[Tuple[float, float, str]]:
    """
    コード名リストから等間隔の(start, end, chord)リストに変換
    Args:
        chords: コード名リスト（例: ['D:maj', 'G:maj', ...]）
        duration: 1コードあたりの長さ（秒）
    Returns:
        (start, end, chord)のリスト
    """
    segments = []
    for i, chord in enumerate(chords):
        start = i * duration
        end = (i + 1) * duration
        segments.append((start, end, chord))
    return segments

def chords_to_midi(
    chord_segments: List[Tuple[float, float, str]],
    filename: Optional[str] = None,
    tempo: int = 100
) -> Optional[str]:
    """
    (開始, 終了, コード名)のリストからMIDIファイルを生成
    Args:
        chord_segments: [(start, end, chord), ...]
        filename: 保存先ファイル名（省略時は一時ファイル）
        tempo: テンポ（BPM）
    Returns:
        midiファイルのパス（または失敗時は None）
    """ 
    notes = []
    for chord_segment in chord_segments:
        start = chord_segment[0]
        end = chord_segment[1]
        chord = chord_segment[2]
        if not chord or chord == 'N':
            continue
        root, ctype = parse_chord(chord)
        if root not in CHORD_ROOT_MAP:
            continue
        root_note = CHORD_ROOT_MAP[root]
        intervals = CHORD_TYPE_MAP.get(ctype, CHORD_TYPE_MAP[''])
        chord_notes = [root_note + i for i in intervals]
        for pitch in chord_notes:
            note = pretty_midi.Note(velocity=80, pitch=pitch, start=start, end=end)
            notes.append(note)

    if len(notes) < 2:
        st.warning("MIDI生成には2つ以上のコードが必要です。")
        return None

    # MIDIファイルの作成
    pm = pretty_midi.PrettyMIDI()
    inst = pretty_midi.Instrument(program=0)
    inst.notes = notes
    pm.instruments.append(inst)

    try:
        if filename is None:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.mid')
            pm.write(tmp.name)
            return tmp.name
        else:
            pm.write(filename)
            return filename
    except Exception as e:
        st.error(f"MIDIファイルの保存に失敗しました: {e}")
        return None
