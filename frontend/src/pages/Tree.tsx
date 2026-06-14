import { useEffect, useState } from 'react'
import type { TreeNode } from '../api/plants'
import { getTree } from '../api/plants'
import { ORIGIN_LABELS, stateLabel } from '../labels'

const GONE = new Set(['discarded', 'given_away'])

export default function Tree() {
  const [roots, setRoots] = useState<TreeNode[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getTree()
      .then(setRoots)
      .catch((err) => setError(err instanceof Error ? err.message : String(err)))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="flex flex-col gap-4">
      <h2 className="text-lg font-semibold">Stamboom</h2>
      <p className="text-sm text-stone-500">
        Een rode markering bij broertjes/zusjes betekent: in dit groepje is een plant ziek
        weggegooid — houd de rest extra in de gaten.
      </p>
      {error && <p className="text-sm text-red-600">{error}</p>}
      {loading && <p className="text-stone-500">Laden…</p>}
      {!loading && roots.length === 0 && (
        <p className="rounded-xl border border-dashed border-stone-300 p-8 text-center text-stone-500">
          Nog geen planten om een stamboom van te tonen.
        </p>
      )}
      <ul className="flex flex-col gap-1">
        {/* Roots have no shared parent, so no sibling disease flag among them. */}
        {roots.map((node) => (
          <TreeBranch key={node.id} node={node} siblingDisease={false} />
        ))}
      </ul>
    </div>
  )
}

function TreeBranch({ node, siblingDisease }: { node: TreeNode; siblingDisease: boolean }) {
  const gone = GONE.has(node.state)
  // A sibling is at risk if any child of this node was discarded for disease.
  const childHasDisease = node.children.some((c) => c.disease_warning)

  return (
    <li>
      <div className={`flex flex-wrap items-center gap-2 py-1 ${gone ? 'opacity-50' : ''}`}>
        {node.thumbnail ? (
          <img src={node.thumbnail} alt="" className="h-8 w-8 rounded object-cover" />
        ) : (
          <span className="h-8 w-8 rounded bg-stone-100" />
        )}
        <span className="font-mono font-medium">{node.label}</span>
        <span className="text-sm text-stone-400">{ORIGIN_LABELS[node.origin]}</span>
        {gone && (
          <span className="rounded bg-stone-200 px-1.5 py-0.5 text-xs text-stone-600">
            {stateLabel(node.state)}
          </span>
        )}
        {node.disease_warning && (
          <span className="rounded bg-red-100 px-1.5 py-0.5 text-xs font-medium text-red-700">
            ziek
          </span>
        )}
        {siblingDisease && !node.disease_warning && (
          <span className="rounded bg-red-50 px-1.5 py-0.5 text-xs font-medium text-red-600">
            ⚠ in de gaten houden
          </span>
        )}
      </div>
      {node.children.length > 0 && (
        // Indent children with a left border to show the lineage hierarchy.
        <ul className="ml-4 border-l border-stone-200 pl-4">
          {node.children.map((child) => (
            <TreeBranch key={child.id} node={child} siblingDisease={childHasDisease} />
          ))}
        </ul>
      )}
    </li>
  )
}
