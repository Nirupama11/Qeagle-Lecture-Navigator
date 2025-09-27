import React, { useState } from 'react'

export function VideoInput({ onIngest, loading }){
  const [url, setUrl] = useState('')

  return (
    <div className="hstack" style={{width:'100%'}}>
      <input className="input" placeholder="Paste YouTube URL (https://youtube.com/watch?v=...)" value={url} onChange={e=>setUrl(e.target.value)} />
      <button className="button" disabled={!url || loading} onClick={()=> onIngest?.(url)}>
        {loading? 'Processing...' : 'Ingest'}
      </button>
    </div>
  )
}





