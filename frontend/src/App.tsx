import { useState, useEffect } from 'react'
import Graph from './Graph.tsx'
import type { RawGraph } from './types.ts'

export default function App() {
  const [graph, setGraph] = useState<RawGraph | null>(null)

  // Run ony once when component mount and fetch graph data from the backend.
  useEffect(() => {
    fetch('http://localhost:5000/graph')
      .then(response => response.json())
      .then(setGraph)
  }, [])

  if (graph) return <Graph raw={graph} />
}