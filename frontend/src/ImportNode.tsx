import { Handle, Position } from '@xyflow/react'
import type { NodeProps, Node } from '@xyflow/react'
import type { ImportNode } from './types.ts'

type ImportNodeType = Node<ImportNode, 'importNode'>

export default function ImportNode({ data }: NodeProps<ImportNodeType>) {
  return (
    <div style={{ background: '#fff', border: `3px solid ${data.color}`, borderRadius: 20, padding: 7}}>
      <Handle type="target" position={Position.Top} />
      {data.label}
    </div>
  )
}