import React, { useState, useEffect } from 'react';
import NetworkGraph from './components/NetworkGraph';
import NodeSidebar from './components/NodeSidebar';
import WordCloud from './components/WordCloud';
import { loadDataFromPublic } from './utils/dataProcessor';

function App() {
    const [data, setData] = useState(null);
    const [selectedNode, setSelectedNode] = useState(null);
    const [showLabels, setShowLabels] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [showWordCloud, setShowWordCloud] = useState(false);

    useEffect(() => {
        loadDefaultData();
    }, []);

    const loadDefaultData = async () => {
        setLoading(true);
        try {
            const loadedData = await loadDataFromPublic();
            setData(loadedData);
            setError(null);
        } catch (err) {
            console.error('No default data found:', err);
            setError('No default data found in /public/data.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="h-screen w-screen relative bg-[#2d2a3d] overflow-hidden">
            {/* Top Header - Floating */}
            <header className="fixed bottom-3 right-1 -translate-x-1/2 w-[100%] max-w-5xl bg-gradient-to-r from-[#4a3f5c] to-[#5d4e6f] shadow-2xl z-50 px-6 py-4 flex items-center justify-between rounded-xl border border-[#6b5b7f]/30 backdrop-blur-sm">
                <h1 className="text-2xl font-bold text-[#f4e9d8]">
                    Telegram Network Analysis</h1>
                <div className="flex items-center gap-4">
                    <label className="flex items-center gap-2 cursor-pointer">
                        <input
                            type="checkbox"
                            checked={showLabels}
                            onChange={(e) => setShowLabels(e.target.checked)}
                            className="w-4 h-4 rounded accent-[#d4885e]"
                        />
                        <span className="text-sm text-[#e8dcc8]">Show Labels</span>
                    </label>
                    <button
                        onClick={() => setShowWordCloud(!showWordCloud)}
                        className="px-4 py-2 bg-[#d4885e] hover:bg-[#c27850] text-[#f4e9d8] rounded-lg text-sm font-medium transition-colors"
                    >
                        {showWordCloud ? 'Hide' : 'Show'} Word Cloud
                    </button>
                </div>
            </header>

            {/* Main Content - Full Screen */}
            <div className="h-screen w-screen flex">
                {/* Network Graph - Full Screen */}
                <div className="flex-1 relative">
                    {loading && (
                        <div className="absolute inset-0 flex items-center justify-center bg-[#837f96] z-10">
                            <div className="text-center">
                                <div className="animate-spin rounded-full h-16 w-16 border-4 border-[#d4885e] border-t-transparent mb-4"></div>
                                <p className="text-lg text-[#b8a892]">Loading data...</p>
                            </div>
                        </div>
                    )}

                    {!data && !loading && (
                        <div className="absolute inset-0 flex flex-col items-center justify-center bg-[#2d2a3d] text-[#b8a892]">
                            <p className="text-lg mb-2">Loading data from /public/data...</p>
                        </div>
                    )}

                    {data && (
                        <NetworkGraph
                            data={data}
                            selectedNode={selectedNode}
                            onNodeClick={setSelectedNode}
                            showLabels={showLabels}
                        />
                    )}
                </div>

                {/* Fixed Right Sidebar */}
                <div className="w-96 bg-gradient-to-b from-[#4a3f5c] to-[#3d3450] shadow-2xl border-l border-[#6b5b7f]/30 flex flex-col">
                    <NodeSidebar
                        selectedNode={selectedNode}
                        data={data}
                        showWordCloud={showWordCloud}
                    />
                </div>
            </div>

            <div className="flex h-screen">
                {/* LEFT: WordCloud panel (only when toggled) */}
                {showWordCloud && (
                    <div className="w-1/4 min-w-[300px] bg-[#2b2440]">
                        <WordCloud messages={selectedNode?.messages || []} />
                    </div>
                )};
                {/* CENTER: Graph */}
                <div className={`${showWordCloud ? 'w-2/4' : 'w-3/4'}`}>
                    <NetworkGraph data={data} selectedNode={selectedNode} onNodeClick={setSelectedNode} />
                </div>

                {/* RIGHT: Sidebar (NodeSidebar) */}
                <div className="w-1/4">
                    <NodeSidebar selectedNode={selectedNode} data={data} />
                </div>
            </div>
            {/* Error message */}
            {error && (
                <div className="fixed top-24 left-1/2 transform -translate-x-1/2 bg-[#d4885e] text-[#f4e9d8] px-6 py-3 rounded-lg shadow-xl z-50 border border-[#c27850]">
                    {error}
                </div>
            )}
        </div>
    );
}

export default App;