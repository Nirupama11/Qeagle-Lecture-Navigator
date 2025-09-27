import React, { useEffect, useRef } from 'react'

export function Player({ videoId, currentTime }) {
  const iframeRef = useRef(null)

  useEffect(() => {
    if (iframeRef.current && currentTime && videoId) {
      iframeRef.current.src = `https://www.youtube.com/embed/${videoId}?start=${Math.floor(currentTime)}&autoplay=1`
    }
  }, [currentTime, videoId])

  if (!videoId) return <div>No video loaded yet.</div>

  return (
    <div className="video-wrapper">
      <iframe
        ref={iframeRef}
        width="800"
        height="450"
        src={`https://www.youtube.com/embed/${videoId}`}
        frameBorder="0"
        allow="autoplay; encrypted-media"
        allowFullScreen
        title="Lecture Video"
      />
    </div>
  )
}
