import NodeSidebar from '../src/components/NodeSidebar';

const sampleData = {
    nodes: [
        { id: '1', username: 'channel_a', name: 'Channel A', outgoing: 5, incoming: 3 },
        { id: '2', username: 'channel_b', name: 'Channel B', outgoing: 3, incoming: 5 },
    ],
    edges: [
        { source: '1', target: '2' },
    ],
};

export default {
    title: 'Components/NodeSidebar',
    component: NodeSidebar,
};

export const Default = {
    args: {
        selectedNode: sampleData.nodes[0],
        data: sampleData,
    },
};