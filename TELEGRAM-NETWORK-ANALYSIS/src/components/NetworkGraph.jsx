import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

const NetworkGraph = ({
    data,
    selectedNode,
    onNodeClick,
    showLabels = false,
    showSteps = false,
    width = 1200,
    height = 700
}) => {
    const svgRef = useRef(null);
    const simulationRef = useRef(null);

    useEffect(() => {
        if (!data || !svgRef.current) return;

        d3.select(svgRef.current).selectAll('*').remove();

        const svg = d3.select(svgRef.current)
            .attr('width', width)
            .attr('height', height);

        const g = svg.append('g');

        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on('zoom', (event) => {
                g.attr('transform', event.transform);
            });

        svg.call(zoom);

        const simulation = d3.forceSimulation(data.nodes)
            .force('link', d3.forceLink(data.edges).id(d => d.id).distance(150))
            .force('charge', d3.forceManyBody().strength(-500))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius(d => Math.sqrt(d.outgoing + d.incoming) * 3 + 70));

        simulationRef.current = simulation;

        const link = g.append('g')
            .selectAll('line')
            .data(data.edges)
            .join('line')
            .attr('stroke', '#ff758cff')
            .attr('stroke-opacity', 0.8)
            .attr('stroke-width', 2);

        const node = g.append('g')
            .selectAll('circle')
            .data(data.nodes)
            .join('circle')
            .attr('r', d => Math.sqrt(d.outgoing + d.incoming) * 3 + 5)
            .attr('fill', '#ba64d4b4')
            .attr('stroke', '#7d5186b4')
            .attr('stroke-width', 2)
            .style('cursor', 'pointer')
            .call(d3.drag()
                .on('start', dragstarted)
                .on('drag', dragged)
                .on('end', dragended))
            .on('click', (event, d) => {
                event.stopPropagation();
                onNodeClick?.(d);
            });

        const labels = g.append('g')
            .selectAll('text')
            .data(data.nodes)
            .join('text')
            .attr('text-anchor', 'middle')
            .attr('dy', -15)
            .attr('font-size', '42px')
            .attr('font-weight', '400')
            .attr('fill', '#ffe5ffe1')
            .attr('stroke', '#181617ec')
            .attr('stroke-width', '6')
            .attr('paint-order', 'stroke')
            .attr('display', showLabels ? 'block' : 'none')
            .text(d => d.username || d.name);

        const stepLabels = g.append('g')
            .selectAll('text')
            .data(data.nodes)
            .join('text')
            .attr('class', 'step-label')
            .attr('text-anchor', 'middle')
            .attr('dy', 5)
            .attr('font-size', '15px')
            .attr('font-weight', '700')
            .attr('fill', '#fff7e8')
            .attr('stroke', '#33243d')
            .attr('stroke-width', '4')
            .attr('paint-order', 'stroke')
            .attr('display', 'none');

        function dragstarted(event) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
        }

        function dragged(event) {
            event.subject.fx = event.x;
            event.subject.fy = event.y;
        }

        function dragended(event) {
            if (!event.active) simulation.alphaTarget(0);
            event.subject.fx = null;
            event.subject.fy = null;
        }

        simulation.on('tick', () => {
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);

            node
                .attr('cx', d => d.x)
                .attr('cy', d => d.y);

            labels
                .attr('x', d => d.x)
                .attr('y', d => d.y);

            stepLabels
                .attr('x', d => d.x)
                .attr('y', d => d.y);
        });

        svg.on('click', () => {
            onNodeClick?.(null);
        });

        return () => {
            simulation.stop();
        };
    }, [data, width, height, showLabels]);

    useEffect(() => {
        if (!data || !svgRef.current) return;

        const svg = d3.select(svgRef.current);
        const outgoingNodes = new Set();
        const incomingNodes = new Set();
        const outgoingEdges = new Set();
        const incomingEdges = new Set();
        const hopDistances = new Map();

        const getEndpointId = (endpoint) => (
            typeof endpoint === 'object' ? endpoint.id : endpoint
        );

        if (selectedNode && showSteps) {
            const outgoing = new Map();
            data.edges.forEach(edge => {
                const sourceId = getEndpointId(edge.source);
                const targetId = getEndpointId(edge.target);
                if (!outgoing.has(sourceId)) outgoing.set(sourceId, []);
                outgoing.get(sourceId).push(targetId);
            });

            const queue = [selectedNode.id];
            hopDistances.set(selectedNode.id, 0);
            while (queue.length > 0) {
                const currentId = queue.shift();
                const currentDepth = hopDistances.get(currentId);
                if (currentDepth >= 6) continue;

                (outgoing.get(currentId) || []).forEach(targetId => {
                    if (!hopDistances.has(targetId)) {
                        hopDistances.set(targetId, currentDepth + 1);
                        queue.push(targetId);
                    }
                });
            }
        }

        if (selectedNode) {
            data.edges.forEach(edge => {
                // Track outgoing connections (this node shares TO others)
                if (getEndpointId(edge.source) === selectedNode.id) {
                    outgoingNodes.add(getEndpointId(edge.target));
                    outgoingEdges.add(edge);
                }
                // Track incoming connections (others share TO this node)
                if (getEndpointId(edge.target) === selectedNode.id) {
                    incomingNodes.add(getEndpointId(edge.source));
                    incomingEdges.add(edge);
                }
            });
        }

        svg.selectAll('circle')
            .attr('fill', d => {
                if (showSteps && selectedNode) {
                    const depth = hopDistances.get(d.id);
                    if (depth === 0) return '#f6c85f';
                    if (depth === 1) return '#ef8f62';
                    if (depth === 2) return '#d76573';
                    if (depth >= 3) return '#9b6bb3';
                    return '#6b6072';
                }
                // Selected node: bright purple
                if (selectedNode?.id === d.id) return '#a896d4ff';
                // Outgoing nodes (this node shares to them): coral/orange
                if (outgoingNodes.has(d.id)) return '#d4805e';
                // Incoming nodes (they share to this node): reddish pink
                if (incomingNodes.has(d.id)) return '#d87676';
                // Unconnected nodes: default peach
                return '#cc8d70ff';
            })
            .attr('opacity', d => {
                if (showSteps && selectedNode) {
                    return hopDistances.has(d.id) ? 1 : 0.12;
                }
                if (!selectedNode) return 1;
                if (d.id === selectedNode.id || outgoingNodes.has(d.id) || incomingNodes.has(d.id)) return 1;
                return 0.2; // Much more faded for unconnected nodes
            });

        svg.selectAll('line')
            .attr('stroke', d => {
                if (showSteps && selectedNode) {
                    const sourceDepth = hopDistances.get(getEndpointId(d.source));
                    const targetDepth = hopDistances.get(getEndpointId(d.target));
                    if (sourceDepth !== undefined && targetDepth === sourceDepth + 1) {
                        return sourceDepth === 0 ? '#f6c85f' : '#d76573';
                    }
                    return '#6b6072';
                }
                // Outgoing edges: orange
                if (outgoingEdges.has(d)) return '#e89547';
                // Incoming edges: reddish pink
                if (incomingEdges.has(d)) return '#d87676';
                // Unconnected edges: purple
                return '#85678bb4';
            })
            .attr('stroke-width', d => {
                if (showSteps && selectedNode) {
                    const sourceDepth = hopDistances.get(getEndpointId(d.source));
                    const targetDepth = hopDistances.get(getEndpointId(d.target));
                    if (sourceDepth !== undefined && targetDepth === sourceDepth + 1) {
                        return Math.max(1.5, 5 - sourceDepth * 0.6);
                    }
                    return 1;
                }
                if (outgoingEdges.has(d) || incomingEdges.has(d)) return 4;
                return 2;
            })
            .attr('stroke-opacity', d => {
                if (showSteps && selectedNode) {
                    const sourceDepth = hopDistances.get(getEndpointId(d.source));
                    const targetDepth = hopDistances.get(getEndpointId(d.target));
                    return sourceDepth !== undefined && targetDepth === sourceDepth + 1 ? 0.9 : 0.08;
                }
                if (!selectedNode) return 0.8; // When nothing selected, show all edges
                if (outgoingEdges.has(d) || incomingEdges.has(d)) return 1;
                return 0; // Completely hide unconnected edges
            });

        // Hide labels for unconnected nodes
        svg.selectAll('text')
            .attr('opacity', d => {
                if (!selectedNode) return 1; // Show all labels when nothing selected
                if (d.id === selectedNode.id || outgoingNodes.has(d.id) || incomingNodes.has(d.id)) return 1;
                return 0; // Hide labels for unconnected nodes
            });

            svg.selectAll('.step-label')
                .text(d => hopDistances.has(d.id) ? hopDistances.get(d.id) : '')
                .attr('display', showSteps && selectedNode ? 'block' : 'none')
                .attr('opacity', d => hopDistances.has(d.id) ? 1 : 0);
            }, [selectedNode, data, showSteps]);

    useEffect(() => {
        if (!svgRef.current) return;

        const svg = d3.select(svgRef.current);
        svg.selectAll('text')
            .attr('display', showLabels ? 'block' : 'none');
    }, [showLabels]);

    return <svg ref={svgRef} className="bg-[#d9c4c4] w-full h-full" />;
};

export default NetworkGraph;