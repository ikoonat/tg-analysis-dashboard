// src/utils/networkCalculations.js

/**
 * Get top outgoing connections for a selected node from a graph dataset.
 * @param {Object} selectedNode — a node object { id, username, name, ... }
 * @param {Object} graph — object with { nodes: [...], edges: [...] }
 * @param {number} limit — maximum number of top connections to return
 * @returns {Array} — list of connected nodes, each enriched with connectionCount
 */
export function getTopConnections(selectedNode, graph, limit = 10) {
    if (!selectedNode || !graph || !Array.isArray(graph.edges) || !Array.isArray(graph.nodes)) {
        return [];
    }

    const counts = new Map();

    graph.edges.forEach(edge => {
        // only consider outgoing from selectedNode
        if (edge.source === selectedNode.id) {
            const t = edge.target;
            counts.set(t, (counts.get(t) || 0) + 1);
        }
    });

    const sorted = Array.from(counts.entries())
        .sort(([, c1], [, c2]) => c2 - c1)
        .slice(0, limit);

    return sorted
        .map(([nodeId, count]) => {
            const node = graph.nodes.find(n => n.id === nodeId);
            return node ? { ...node, connectionCount: count } : null;
        })
        .filter(n => n !== null);
}

/**
 * Get IDs of all nodes directly connected to selectedNode (incoming or outgoing).
 * @param {Object} selectedNode
 * @param {Object} graph
 * @returns {Set<string>} — set of connected node IDs
 */
export function getConnectedNodeIds(selectedNode, graph) {
    const connected = new Set();
    if (!selectedNode || !graph || !Array.isArray(graph.edges)) return connected;

    graph.edges.forEach(edge => {
        if (edge.source === selectedNode.id) {
            connected.add(edge.target);
        }
        if (edge.target === selectedNode.id) {
            connected.add(edge.source);
        }
    });

    return connected;
}

/**
 * Merge multiple graph datasets into a single graph.
 * Useful if you loaded multiple CSVs and want to combine them.
 * @param {Object} dataObject — object whose values are graph-like { nodes, edges }
 * @returns {Object} — merged graph { nodes, edges }
 */
export function mergeGraphs(dataObject) {
    const nodeMap = new Map();
    const edges = [];

    for (const key in dataObject) {
        const graph = dataObject[key];
        if (!graph || !Array.isArray(graph.nodes) || !Array.isArray(graph.edges)) continue;

        // add nodes
        graph.nodes.forEach(n => {
            if (!nodeMap.has(n.id)) {
                nodeMap.set(n.id, { ...n });
            } else {
                // optional: aggregate counts
                const existing = nodeMap.get(n.id);
                existing.outgoing = (existing.outgoing || 0) + (n.outgoing || 0);
                existing.incoming = (existing.incoming || 0) + (n.incoming || 0);
            }
        });

        // add edges (assuming simple edge list)
        edges.push(...graph.edges);
    }

    return {
        nodes: Array.from(nodeMap.values()),
        edges
    };
}
