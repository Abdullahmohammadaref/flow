import { Handle, Position } from '@xyflow/react'
import type { NodeProps, Node } from '@xyflow/react'
import type { EntityNode } from './types.ts'

type EntityNodeType = Node<EntityNode, 'entityNode'>

export default function EntityNode({ data }: NodeProps<EntityNodeType>) {
  return (
    <div style={{ background: '#fff', border: `3px solid ${data.color}`, borderRadius: 15, padding: 5}}>
      <Handle type="target" position={Position.Top} />
      <div>{data.type}: {data.label}</div>
      <div>used in {data.fileCount} files</div>
    </div>
  )
}