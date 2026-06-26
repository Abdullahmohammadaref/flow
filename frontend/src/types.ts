export interface GraphNode {
  type: string
  imports?: Record<string, string>
  functions?: string[]
  classes?: string[]
  is_entry_point?: boolean
  has_wait_state?: boolean
  decorators?: string[]
  base_classes?: string[]
  global_variables?: string[]
  file_role?: string
  pagerank_score?: number
  imports_count?: number
  file_role_prediction_confidence?: number
  id: string
}
export interface GraphEdge {
  source: string
  target: string
  dependency_order?: number | null
  execution_order?: number | null
  has_circular_dependency?: boolean
}
export interface RawGraph {
  nodes: GraphNode[]
  edges: GraphEdge[]
}
export interface FileNode extends Record<string, unknown> {
  label: string
  role: string
  color: string
  confidence: number | null
  pagerank: number
  functionCount: number
  classCount: number
  isEntryPoint: boolean
  hasCircularDependency: boolean
}
export interface ImportNode extends Record<string, unknown> {
  label: string
  color: string
}

export interface EntityNode extends Record<string, unknown> {
  label: string
  type: 'function' | 'class' | 'decorator' | 'global_variable'
  color: string
  fileCount: number
}