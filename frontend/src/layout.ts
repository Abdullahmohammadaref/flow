import { forceSimulation, forceLink, forceManyBody, forceCenter, forceCollide } from 'd3-force'

interface SimulationNode { id: string; type: string; x: number; y: number }
interface SimulationLink { source: string; target: string }

// Calculates mathematically using d3-force where to place the nodes on the canvas so they don't
// stack ontop of each other by default behavior
// connected nodes position effect the calculation and
export function computeLayout(
  rawNodes: { id: string; type: string }[],
  rawEdges: { source: string; target: string }[],
): { id: string; x: number; y: number }[] {

  const nodes: SimulationNode[] = rawNodes.map((node, i) => ({
    id: node.id,
    type: node.type,
    x: Math.cos((i / rawNodes.length) * 2 * Math.PI) * 100,
    y: Math.sin((i / rawNodes.length) * 2 * Math.PI) * 100,
  }))

  const ids = new Set(nodes.map(node => node.id))
  const links: SimulationLink[] = rawEdges.filter(edge => ids.has(edge.source) && ids.has(edge.target))

  const simulation = forceSimulation(nodes)
    .force(
      'link',
      forceLink<SimulationNode, SimulationLink>(links)
        .id(d => d.id)
        .distance(link => {
          const source = link.source as unknown as SimulationNode
          const target = link.target as unknown as SimulationNode
          if (source.type === 'entityNode' || target.type === 'entityNode') return 30
          if (source.type === 'importNode' || target.type === 'importNode') return 80
          return 150
        }),
    )
    .force(
      'charge',
      forceManyBody<SimulationNode>().strength(node => {
        if (node.type === 'fileNode') return -400
        if (node.type === 'entityNode') return -50
        return -150
      }),
    )
    .force('center', forceCenter(0, 0))
    .force(
      'collide',
      forceCollide<SimulationNode>().radius(node => (node.type === 'fileNode' ? 90 : 40)),
    )
    .stop()

  for (let i = 0; i < 300; i++)
    simulation.tick()

  return nodes.map(node => ({ id: node.id, x: node.x, y: node.y }))
}