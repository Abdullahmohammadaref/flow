import { useEffect, useMemo, useState} from 'react'
import {ReactFlow, ReactFlowProvider, Background, Controls, useNodesState, useEdgesState, useReactFlow} from '@xyflow/react'
import type { Node, Edge, NodeTypes } from '@xyflow/react'
import FileNode from './FileNode.tsx'
import ImportNode from './ImportNode.tsx'
import EntityNode from './EntityNode.tsx'
import { transformGraph } from './transform.ts'
import { computeLayout } from './layout.ts'
import type { RawGraph } from './types.ts'

const nodeTypes: NodeTypes = {
  fileNode: FileNode,
  importNode: ImportNode,
  entityNode: EntityNode,
}

const LAYERS = ['libraries', 'functions', 'classes', 'decorators', 'globals'] as const
type Layer = (typeof LAYERS)[number]

function GraphInner({ raw }: { raw: RawGraph }) {
  const full = useMemo(() => transformGraph(raw), [raw])
  const { fitView } = useReactFlow()

  const [layers, setLayers] = useState<Record<Layer, boolean>>({
    libraries: false,
    functions: false,
    classes: false,
    decorators: false,
    globals: false,
  })

  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([])
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([])
  const [focusId, setFocusId] = useState<string | null>(null)
  const [search, setSearch] = useState('')

  function searchNode(query: string) {
    setSearch(query)
    if (!query) return
    const match = nodes.find(node => node.id.toLowerCase().includes(query.toLowerCase()))
    if (match) {
      fitView({ nodes: [{ id: match.id }], padding: 0.5, duration: 300 })
    }
  }

  // Recompute visible nodes/edges when layers change
  const { visibleNodes, visibleEdges } = useMemo(() => {
    const visible_nodes: Node[] = [...full.fileNodes]
    const visible_edges: Edge[] = [...full.fileEdges]
    if (layers.libraries) { visible_nodes.push(...full.importNodes); visible_edges.push(...full.libEdges) }
    if (layers.functions) { visible_nodes.push(...full.functionNodes); visible_edges.push(...full.functionEdges) }
    if (layers.classes) { visible_nodes.push(...full.classNodes); visible_edges.push(...full.classEdges) }
    if (layers.decorators) { visible_nodes.push(...full.decoratorNodes); visible_edges.push(...full.decoratorEdges) }
    if (layers.globals) { visible_nodes.push(...full.globalNodes); visible_edges.push(...full.globalEdges) }
    return { visibleNodes: visible_nodes, visibleEdges: visible_edges }
  }, [full, layers])

  // Compute layout and set nodes/edges whenever visible set changes
  useEffect(() => {
    const positions = computeLayout(
      visibleNodes.map(node => ({ id: node.id, type: node.type ?? 'fileNode' })),
      visibleEdges.map(edge => ({ source: edge.source, target: edge.target })),
    )
    const posMap = new Map(positions.map(position => [position.id, { x: position.x, y: position.y }]))

    setNodes(
      visibleNodes.map(node => ({
        ...node,
        position: posMap.get(node.id) ?? { x: 0, y: 0 },
      })),
    )
    setEdges(visibleEdges)

    // fitView after React Flow has measured the new nodes

    setTimeout(() => fitView({ padding: 0.15 }), 50)

  }, [visibleNodes, visibleEdges, setNodes, setEdges, fitView])

  const toggleLayer = (layer: Layer) => {
    setLayers(prev => ({ ...prev, [layer]: !prev[layer] }))
  }

  // Dim everything except the clicked node and its direct neighbors
  function focusNode(id: string | null) {
    setFocusId(id)
    setNodes(nodes =>
      nodes.map(node => {
        const connected =
          id === null ||
          node.id === id ||
          edges.some(
            edge =>
              (edge.source === id && edge.target === node.id) ||
              (edge.target === id && edge.source === node.id),
          )
        return { ...node, style: { opacity: connected ? 1 : 0.15 } }
      }),
    )
  }

  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <div
        style={{
          position: 'absolute',
          top: 10,
          right: 10,
          zIndex: 10,
          background: '#fff',
          padding: 8,
          fontSize: 12,
          border: '1px solid #ccc',
        }}
      >
        {LAYERS.map(layer => (
          <label key={layer} style={{ display: 'block' }}>
            <input
              type="checkbox"
              checked={layers[layer]}
              onChange={() => toggleLayer(layer)}
            />{' '}
            {layer}
          </label>
        ))}
        <div>{full.fileNodes.length} files</div>
        <div>{visibleNodes.length} nodes shown</div>
        <input
          type="text"
          placeholder="search node"
          value={search}
          onChange={edge => searchNode(edge.target.value)}
          style={{ marginTop: 6, width: '100%', boxSizing: 'border-box' }}
        />
      </div>

      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        onNodeClick={(_, node) => focusNode(focusId === node.id ? null : node.id)}
        onPaneClick={() => focusNode(null)}
        minZoom={0.01}
        maxZoom={4}
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  )
}

export default function Graph({ raw }: { raw: RawGraph }) {
  return (
    <ReactFlowProvider>
      <GraphInner raw={raw} />
    </ReactFlowProvider>
  )
}