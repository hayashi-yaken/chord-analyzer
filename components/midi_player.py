import streamlit as st
import subprocess
import os
from typing import Optional

def convert_midi_to_wav(midi_path: str) -> str:
    """MIDIファイルをWAVファイルに変換
    Args:
        midi_path: MIDIファイルのパス
    Returns:
        WAVファイルのパス
    """
    wav_path = midi_path.replace('.mid', '.wav')
    subprocess.run([
        'fluidsynth',
        '-ni',
        '/usr/share/sounds/sf2/FluidR3_GM.sf2',
        midi_path,
        '-F',
        wav_path
    ])
    return wav_path

def midi_player(midi_path: str, label: Optional[str] = None):
    """MIDIファイルをStreamlit上で再生するコンポーネント
    Args:
        midi_path: 再生するMIDIファイルのパス
        label: 表示用ラベル
    """
    if label:
        st.subheader(label)

    # MIDIファイルをWAVに変換
    wav_path = convert_midi_to_wav(midi_path)

    # WAVファイルを読み込んで再生
    with open(wav_path, "rb") as f:
        audio_bytes = f.read()
    st.audio(audio_bytes, format="audio/wav")

    # 元のMIDIファイルをダウンロード可能に
    with open(midi_path, "rb") as f:
        midi_bytes = f.read()
    st.download_button("MIDIファイルをダウンロード", midi_bytes, file_name="chord_progression.mid", mime="audio/midi")

    # 一時的なWAVファイルを削除
    os.remove(wav_path)