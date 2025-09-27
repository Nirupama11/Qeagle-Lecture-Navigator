from __future__ import annotations

from typing import List, Dict, Any, Tuple
from loguru import logger

from youtube_transcript_api import YouTubeTranscriptApi
import webvtt
import srt
import tempfile, os, shutil


def _clean_text(text: str) -> str:
    t = text.strip()
    # remove common filler words
    t = t.replace(" uh ", " ").replace(" um ", " ").replace(" uh.", ".").replace(" um.", ".")
    t = " ".join(t.split())
    return t


def _segment_chunks(
    sentences: List[Tuple[float, float, str]],
    window: float = 45.0,
    overlap: float = 15.0,
) -> List[Dict[str, Any]]:
    """Segment sentences into overlapping windows for retrieval."""
    segments: List[Dict[str, Any]] = []
    n = len(sentences)
    if n == 0:
        return segments

    i = 0
    while i < n:
        start = sentences[i][0]
        end = start
        texts: List[str] = []
        j = i
        while j < n and (sentences[j][1] - start) <= window:
            texts.append(sentences[j][2])
            end = sentences[j][1]
            j += 1

        snippet = _clean_text(" ".join(texts))
        if snippet:
            segments.append({
                "start_time": float(start),
                "end_time": float(end),
                "text": snippet,
                "metadata": {},
            })

        # advance index with overlap
        advance_to = start + max(window - overlap, 1.0)
        k = i
        while k < n and sentences[k][0] < advance_to:
            k += 1
        i = max(k, i + 1)

    return segments


def segment_transcript(
    sentences: List[Tuple[float, float, str]],
    window: float = 30.0,
    overlap: float = 15.0,
) -> List[Dict[str, Any]]:
    """Public wrapper to segment transcript sentences into overlapping chunks."""
    return _segment_chunks(sentences, window=window, overlap=overlap)


def load_youtube_transcript(video_url: str, window: float = 30.0, overlap: float = 15.0) -> List[Dict[str, Any]]:
    """Load YouTube transcript if available, else raise error."""
    import urllib.parse as urlparse
    parsed = urlparse.urlparse(video_url)
    qs = urlparse.parse_qs(parsed.query)
    video_id = qs.get("v", [None])[0] or parsed.path.split("/")[-1] or video_url

    if not video_id:
        raise ValueError("Invalid YouTube URL or ID")

    logger.info(f"Downloading transcript for video: {video_id}")
    items = YouTubeTranscriptApi.get_transcript(video_id)
    sentences = [
        (float(i["start"]), float(i["start"]) + float(i["duration"]), _clean_text(i["text"]))
        for i in items
    ]
    return _segment_chunks(sentences, window=window, overlap=overlap)


def load_whisper_transcript(video_url: str, window: float = 30.0, overlap: float = 15.0) -> List[Dict[str, Any]]:
    """
    Download audio from YouTube and transcribe using Whisper (local).
    Requires: yt-dlp, openai-whisper, ffmpeg
    """
    import yt_dlp
    import whisper

    tmpdir = tempfile.mkdtemp()
    out_file = os.path.join(tmpdir, "audio.mp3")

    try:
        # Step 1: Download best audio
        ydl_opts = {"format": "bestaudio/best", "outtmpl": out_file, "quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info(f"Downloading audio for Whisper: {video_url}")
            ydl.download([video_url])

        # Step 2: Pick model
        file_size_mb = os.path.getsize(out_file) / (1024 * 1024)
        if file_size_mb > 50:  # heuristic: use tiny for long videos
            model_name = "tiny"
        else:
            model_name = "small"

        logger.info(f"Running Whisper transcription with model={model_name}...")
        model = whisper.load_model(model_name)
        result = model.transcribe(out_file)

        # Step 3: Convert to segment format
        sentences = []
        for seg in result["segments"]:
            start = float(seg["start"])
            end = float(seg["end"])
            text = _clean_text(seg["text"])
            if text:
                sentences.append((start, end, text))

        return _segment_chunks(sentences, window=window, overlap=overlap)

    finally:
        # cleanup
        try:
            shutil.rmtree(tmpdir)
        except Exception:
            pass


def load_vtt(file_path: str, window: float = 30.0, overlap: float = 15.0) -> List[Dict[str, Any]]:
    sentences: List[Tuple[float, float, str]] = []
    for caption in webvtt.read(file_path):
        start = _to_seconds(caption.start)
        end = _to_seconds(caption.end)
        text = _clean_text(caption.text)
        if text:
            sentences.append((start, end, text))
    return _segment_chunks(sentences, window=window, overlap=overlap)


def load_srt(file_path: str, window: float = 30.0, overlap: float = 15.0) -> List[Dict[str, Any]]:
    sentences: List[Tuple[float, float, str]] = []
    with open(file_path, "r", encoding="utf-8") as f:
        subs = list(srt.parse(f.read()))
    for sub in subs:
        start = sub.start.total_seconds()
        end = sub.end.total_seconds()
        text = _clean_text(sub.content)
        if text:
            sentences.append((start, end, text))
    return _segment_chunks(sentences, window=window, overlap=overlap)


def _to_seconds(hhmmss: str) -> float:
    h, m, s = hhmmss.replace(",", ".").split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)

