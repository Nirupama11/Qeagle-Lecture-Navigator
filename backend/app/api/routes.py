from fastapi import APIRouter, HTTPException
from ..models.schemas import SearchRequest, SearchResponse, IngestRequest, IngestResponse, Segment
from ..services import transcript as transcript_service
from ..services.search import index_segments, semantic_search
from ..services.agent import generate_answer
from uuid import uuid4
import urllib.parse as urlparse
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


def _rid() -> str:
    return uuid4().hex[:12]


@router.post("/search_timestamps", response_model=SearchResponse)
async def search_timestamps(payload: SearchRequest):
    if not payload.query:
        raise HTTPException(status_code=400, detail="Query is required")
    rid = _rid()
    logger.info(f"[{rid}] search: query='{payload.query}' video_id={payload.video_id}")

    try:
        docs = await semantic_search(payload.query, k=payload.k, video_id=payload.video_id)
        results = [
            Segment(
                video_id=d.get("video_id"),
                t_start=float(d.get("start_time", 0.0)),
                t_end=float(d.get("end_time", 0.0)),
                title=d.get("title"),
                snippet=d.get("snippet") or d.get("text", ""),
                score=float(d.get("score", 0.0)),
            )
            for d in docs
        ]

        answer = await generate_answer(payload.query, docs)
        resp = SearchResponse(results=results, answer=answer)
        logger.info(f"[{rid}] search returned {len(results)} results")
        return resp

    except Exception as e:
        logger.exception(f"[{rid}] search_timestamps failed")
        raise HTTPException(status_code=500, detail=f"Search failed: {e}")


@router.post("/ingest_video", response_model=IngestResponse)
async def ingest_video(payload: IngestRequest):
    if not payload.video_url:
        raise HTTPException(status_code=400, detail="video_url is required")
    rid = _rid()
    logger.info(f"[{rid}] ingest_video url={payload.video_url}")

    try:
        # Try YouTube transcript first
        try:
            raw_segments = transcript_service.load_youtube_transcript(str(payload.video_url))
            logger.info(f"[{rid}] loaded YouTube transcript")
        except Exception as e:
            logger.warning(f"[{rid}] transcript not available, using Whisper fallback: {e}")
            raw_segments = transcript_service.load_whisper_transcript(str(payload.video_url))

        # Normalize format
        if raw_segments and isinstance(raw_segments[0], dict) and "text" in raw_segments[0]:
            segments = raw_segments
        else:
            segments = transcript_service.segment_transcript(raw_segments)

        # Parse video ID
        parsed = urlparse.urlparse(str(payload.video_url))
        qs = urlparse.parse_qs(parsed.query)
        video_id = qs.get("v", [None])[0] or parsed.path.split("/")[-1] or str(payload.video_url)
        title = f"YouTube {video_id}"

        # Index in vector store
        await index_segments(video_id, title, segments)
        logger.info(f"[{rid}] indexed {len(segments)} segments for {video_id}")
        return IngestResponse(video_id=video_id)

    except Exception as e:
        logger.exception(f"[{rid}] ingest_video failed")
        raise HTTPException(status_code=400, detail=f"Failed to ingest video: {e}")
