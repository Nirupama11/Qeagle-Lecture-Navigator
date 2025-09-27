import React, { useMemo, useState } from 'react'
import { useApi } from './services/api'
import { VideoInput } from './components/VideoInput'
import { SearchBar } from './components/SearchBar'
import { Player } from './components/Player'

export default function App() {
  const api = useApi()
  const [videoId, setVideoId] = useState('')
  const [query, setQuery] = useState('')
  const [loadingIngest, setLoadingIngest] = useState(false)
  const [searching, setSearching] = useState(false)
  const [results, setResults] = useState([])
  const [answer, setAnswer] = useState('')
  const [currentTime, setCurrentTime] = useState(0)

  const canSearch = useMemo(() => videoId && query.length > 1, [videoId, query])

  async function handleIngest(url) {
    try {
      setLoadingIngest(true)
      const { video_id } = await api.ingestVideo(url)
      setVideoId(video_id)
    } catch (e) {
      alert('Failed to ingest video: ' + (e?.message || e))
    } finally {
      setLoadingIngest(false)
    }
  }

  async function handleSearch(q) {
    setQuery(q)
    if (!q || q.length < 2 || !videoId) return
    try {
      setSearching(true)
      const resp = await api.searchTimestamps({ query: q, k: 3, video_id: videoId })
      setResults(resp.results || [])
      setAnswer(resp.answer || '')
    } catch (e) {
      console.error(e)
    } finally {
      setSearching(false)
    }
  }

  function jumpTo(t) {
    setCurrentTime(t)
  }

  return (
    <div className="container vstack" style={{ gap: 16 }}>
      <h1 style={{ marginBottom: 0 }}>Lecture Navigator</h1>
      <p>Ingest subtitles, search, and jump to timestamps</p>

      <div className="panel vstack">
        <div className="hstack">
          <VideoInput onIngest={handleIngest} loading={loadingIngest} />
         
        </div>
        <div className="hstack">
          <SearchBar value={query} onChange={handleSearch} loading={searching} disabled={!videoId} />
        </div>
      </div>

      <div className="panel vstack">
        <div className="section-title">Player</div>
        <Player videoId={videoId} currentTime={currentTime} />
      </div>

      <div className="panel vstack">
        <div className="section-title">Answer</div>
        <div>{answer || 'Ask a question about the lecture.'}</div>
      </div>

      <div className="panel vstack">
        <div className="section-title">Top Matches</div>
        <div className="results-section">
          {results.length > 0 ? (
            results.map((r, idx) => {
              const isActive = currentTime >= r.t_start && currentTime <= r.t_end
              return (
                <div
                  key={idx}
                  className={`timestamp-card ${isActive ? 'active' : ''}`}
                  onClick={() => jumpTo(r.t_start)}
                >
                  <div className="timestamp-header">
                    ⏱ {Math.floor(r.t_start)}s - {Math.floor(r.t_end)}s
                  </div>
                  <div className="timestamp-snippet">{r.snippet}</div>
                  <button className="jump-btn">Jump ▶</button>
                </div>
              )
            })
          ) : (
            <div className="no-results">No results yet.</div>
          )}
        </div>
      </div>
    </div>
  )
}
