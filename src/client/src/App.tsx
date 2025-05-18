import React, { useEffect, useState } from 'react';
import './App.css';

type Stream = {
  source: string;
  resolution: string;
  framerate: number;
  bitrate: string;
  status: string;
};

type StreamsResponse = {
  raw: Record<string, Stream>;
  annotated: Record<string, Stream>;
};

type Metrics = {
  total_frames: number;
  total_detections: number;
  last_labels: string[];
};

const API_BASE = "http://localhost:8000";

const App: React.FC = () => {
  const [streams, setStreams] = useState<StreamsResponse | null>(null);
  const [metrics, setMetrics] = useState<Metrics | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}/streams`)
      .then(res => res.json())
      .then(setStreams);

    fetch(`${API_BASE}/analytics/metrics`)
      .then(res => res.json())
      .then(setMetrics);
  }, []);

  return (
    <div style={{ padding: 24 }}>
      <h1>Intelligent Streaming Platform</h1>
      <h2>Streams</h2>
      {!streams ? (
        <p>Loading streams...</p>
      ) : (
        <>
          <h3>Raw Streams</h3>
          <StreamList streams={streams.raw} type="raw" />
          <h3>Annotated Streams</h3>
          <StreamList streams={streams.annotated} type="annotated" />
        </>
      )}
      <h2>Analytics Metrics</h2>
      {!metrics ? (
        <p>Loading metrics...</p>
      ) : (
        <ul>
          <li>Total Frames: {metrics.total_frames}</li>
          <li>Total Detections: {metrics.total_detections}</li>
          <li>Last Labels: {metrics.last_labels?.join(', ')}</li>
        </ul>
      )}
      <hr />
      <p>
        <b>Note:</b> RTSP streams cannot be played directly in most browsers. Use a player like <a href="https://www.videolan.org/vlc/" target="_blank" rel="noopener noreferrer">VLC</a> or an in-browser player that supports RTSP over WebRTC/HLS.
      </p>
    </div>
  );
};

const StreamList: React.FC<{ streams: Record<string, Stream>, type: string }> = ({ streams, type }) => (
  <ul>
    {Object.entries(streams).map(([name, stream]) => (
      <li key={name}>
        <b>{name}</b> ({stream.status})<br />
        Source: {stream.source}<br />
        Resolution: {stream.resolution}, Framerate: {stream.framerate}, Bitrate: {stream.bitrate}<br />
        RTSP URL: <code>rtsp://localhost:8556/{name}</code>
      </li>
    ))}
    {Object.keys(streams).length === 0 && <li>No {type} streams running.</li>}
  </ul>
);

export default App;