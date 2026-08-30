import NetworkGraph from '../src/components/NetworkGraph';

const sampleData = {
    nodes: [
        { id: '1', username: 'channel_a', name: 'Channel A', outgoing: 5, incoming: 3 },
        { id: '2', username: 'channel_b', name: 'Channel B', outgoing: 3, incoming: 5 },
        { id: '3', username: 'channel_c', name: 'Channel C', outgoing: 2, incoming: 2 },
    ],
    edges: [
        { source: '1', target: '2' },
        { source: '1', target: '3' },
        { source: '2', target: '3' },
    ],
};

export default {
    title: 'Components/NetworkGraph',
    component: NetworkGraph,
    parameters: {
        layout: 'fullscreen',
    },
};

export const Default = {
    args: {
        data: sampleData,
        showLabels: true,
        width: 800,
        height: 600,
    },
};

export const WithoutLabels = {
    args: {
        data: sampleData,
        showLabels: false,
        width: 800,
        height: 600,
    },
};

export const RelationshipSteps = {
    args: {
        data: sampleData,
        selectedNode: sampleData.nodes[0],
        showLabels: true,
        showSteps: true,
        width: 800,
        height: 600,
    },
};