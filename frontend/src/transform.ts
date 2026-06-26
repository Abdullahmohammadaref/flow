import type { Node, Edge } from '@xyflow/react'
import type { RawGraph, GraphNode, ImportNode, EntityNode } from './types.ts'

const FileNodeColors: Record<string, string> = {
  migration: '#433e3e',
  test: '#2dd4bf',
  utility: '#9eca1a',
  model: '#ef4f0a',
  other: '#775151',
  script: '#f97316',
  core: '#07a64c',
  commandLineInterface_command: '#000000',
  config: '#2217c1',
  view: '#5b9cf6',
  router: '#efc006',
  enum: '#cc38e3',
  prediction_model: '#063b73',
  entry_point: '#56c96b',
  middleware: '#8e1717',
}
const ImportNodeColors: Record<string, string> = {
  internal_import: '#2c8114',
  external_import: '#d30606',
  standard_import: '#1c6ee1',
}
const EntityNodeColors: Record<string, string> = {
  function: '#67e8f9',
  class: '#f472b6',
  decorator: '#818cf8',
  global_variable: '#fbbf24',
}



function extractEntities(raw: RawGraph, attrs: (keyof GraphNode)[], type: string) {
  const nodeMap = new Map<string, Node>()
  const edges: Edge[] = []
  const edgeSeen = new Set<string>()

  for (const file of raw.nodes) {
    if (file.type !== 'LocalFile') continue

    for (const attr of attrs) {
      const names = (file[attr] as string[] | undefined) ?? []

      for (const name of names) {
        const id = `${type}:${name}`

        if (!nodeMap.has(id)) {
          nodeMap.set(id, {
            id,
            type: 'entityNode',
            position: { x: 0, y: 0 },
            data: { label: name, type, color: EntityNodeColors[type], fileCount: 0 },
          })
        }
        ; (nodeMap.get(id)!.data as EntityNode).fileCount++

        const edgeId = `${file.id}->${id}`
        if (!edgeSeen.has(edgeId)) {
          edgeSeen.add(edgeId)
          edges.push({ id: edgeId, source: file.id, target: id })
        }
      }
    }
  }

  return { nodes: [...nodeMap.values()], edges }
}
export function transformGraph(raw: RawGraph) {
  const fileNodes: Node[] = []
  const importNodes: Node[] = []

  for (const node of raw.nodes) {
    if (node.type === 'LocalFile') {
      const role = node.file_role ?? 'other'
      fileNodes.push({
        id: node.id,
        type: 'fileNode',
        position: { x: 0, y: 0 },
        data: {
          label: node.id,
          role,
          color: FileNodeColors[role] ?? FileNodeColors.other,
          confidence: node.file_role_prediction_confidence ?? null,
          pagerank: node.pagerank_score ?? 0,
          functionCount: node.functions?.length ?? 0,
          classCount: node.classes?.length ?? 0,
          importCount: node.imports_count ?? 0,
          isEntryPoint: node.is_entry_point ?? false,
          hasWaitState: node.has_wait_state ?? false,
          decoratorCount: node.decorators?.length ?? 0,
          globalVariableCount: node.global_variables?.length ?? 0,
          baseClassCount: node.base_classes?.length ?? 0,
          hasCircularDependency: false,
        },
      })
    } else {
      importNodes.push({
        id: node.id,
        type: 'importNode',
        position: { x: 0, y: 0 },
        data: {
          label: node.id,
          color: ImportNodeColors[node.type] ?? '#4a5070',
        } satisfies ImportNode,
      })
    }
  }

  const fileIds = new Set(fileNodes.map(node => node.id))
  const importIds = new Set(importNodes.map(node => node.id))
  const fileEdges: Edge[] = []
  const libEdges: Edge[] = []

  raw.edges.forEach((graphEdge, number) => {
    const dependencyOrder = graphEdge.dependency_order
    const executionOrder = graphEdge.execution_order
    const isCircular = graphEdge.has_circular_dependency ?? false
    const label = (dependencyOrder != null || executionOrder != null) ? `dependencyOrder:${dependencyOrder ?? '–'} executionOrder:${executionOrder ?? '–'}` : undefined
    const edge: Edge = {
      id: `${number}`,
      source: graphEdge.source,
      target: graphEdge.target,
      label,
      style: isCircular ? { stroke: 'red', strokeWidth: 2 } : undefined,
    }
    if (importIds.has(graphEdge.target))
      libEdges.push(edge)
    else if (fileIds.has(graphEdge.target))
      fileEdges.push(edge)
    if (isCircular) {
      for (const fileNode of fileNodes) {
        if (fileNode.id === graphEdge.source || fileNode.id === graphEdge.target) {
          (fileNode.data as Record<string, unknown>).hasCircularDependency = true
        }
      }
    }
  })

  const functions = extractEntities(raw, ['functions'], 'function')
  const classes = extractEntities(raw, ['classes', 'base_classes'], 'class')
  const decorators = extractEntities(raw, ['decorators'], 'decorator')
  const globals = extractEntities(raw, ['global_variables'], 'global_variable')

  return {
    fileNodes, importNodes, fileEdges, libEdges,
    functionNodes: functions.nodes, functionEdges: functions.edges,
    classNodes: classes.nodes, classEdges: classes.edges,
    decoratorNodes: decorators.nodes, decoratorEdges: decorators.edges,
    globalNodes: globals.nodes, globalEdges: globals.edges,
  }
}