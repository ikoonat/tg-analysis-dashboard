import React from 'react';
import { getTopConnections } from '../utils/networkCalculations';
import WordCloud from './WordCloud';

const NodeSidebar = ({ selectedNode, data }) => {
    if (!selectedNode) return null;

    const topConnections = getTopConnections(selectedNode, data);

    return (
        <div className="w-96 bg-white shadow-xl p-6 overflow-y-auto">
            <h2 className="text-xl font-bold mb-4 text-gray-800">Node Details</h2>

            <div className="mb-6">
                <div className="bg-gradient-to-r from-blue-500 to-purple-500 text-white p-4 rounded-lg mb-4">
                    <h3 className="font-bold text-lg mb-2">{selectedNode.username}</h3>
                    <p className="text-sm opacity-90">{selectedNode.name}</p>
                    <p className="text-xs opacity-75 mt-2">ID: {selectedNode.id}</p>
                </div>

                <div className="grid grid-cols-2 gap-4 mb-4">
                    <div className="bg-green-50 p-3 rounded">
                        <p className="text-xs text-green-600 font-semibold">Outgoing</p>
                        <p className="text-2xl font-bold text-green-700">{selectedNode.outgoing}</p>
                    </div>
                    <div className="bg-blue-50 p-3 rounded">
                        <p className="text-xs text-blue-600 font-semibold">Incoming</p>
                        <p className="text-2xl font-bold text-blue-700">{selectedNode.incoming}</p>
                    </div>
                </div>
            </div>

            <div className="mb-6">
                <h3 className="font-semibold text-gray-700 mb-3">Top 10 Connections</h3>
                <div className="space-y-2">
                    {topConnections.map((node, idx) => (
                        <div key={idx} className="p-2 bg-yellow-50 rounded border-l-4 border-yellow-400">
                            <p className="text-sm font-medium text-gray-800">{node.username}</p>
                            <p className="text-xs text-gray-600">{node.name}</p>
                            <p className="text-xs text-yellow-600 font-semibold mt-1">
                                {node.connectionCount} connections
                            </p>
                        </div>
                    ))}
                </div>
            </div>

            <div>
                <h3 className="font-semibold text-gray-700 mb-3">Word Cloud</h3>
                <WordCloud />
            </div>
        </div>
    );
};

export default NodeSidebar;