import { Handle, Position } from '@xyflow/react'
import type { NodeProps, Node } from '@xyflow/react'
import type { FileNode } from './types.ts'

type FileNodeType = Node<FileNode, 'fileNode'>

export default function FileNode({ data }: NodeProps<FileNodeType>) {
  return (
    <div style={{ background: '#fff', border: `3px solid ${data.color}`, padding: 5 }}>
      <Handle type="target" position={Position.Top} />
      <div><b>{data.label}</b></div>
      <div>file role: {data.role}</div>
      <div>prediction confidence: {data.confidence}</div>
      <div>pagerank (importance): {data.pagerank}</div>
      <div>functions count: {data.functionCount}</div>
      <div>classes count: {data.classCount}</div>
      <div>Is entry point?: {data.isEntryPoint ? 'yes' : 'no'}</div>
      {data.hasCircularDependency && <div style={{ color: 'red' }}>⚠ circular dependency</div>}
      <Handle type="source" position={Position.Bottom} />
    </div>
  )
}