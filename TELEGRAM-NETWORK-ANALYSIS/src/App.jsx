import React, { useState, useEffect } from 'react';
import NetworkGraph from './components/NetworkGraph';
import NodeSidebar from './components/NodeSidebar';
import WordCloud from './components/WordCloud';
import { loadDataFromPublic } from './utils/dataProcessor';

function App() {
    const [data, setData] = useState(null);
    const [selectedNode, setSelectedNode] = useState(null);
    const [showLabels, setShowLabels] = useState(false);
    const [showSteps, setShowSteps] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [showWordCloud, setShowWordCloud] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState([]);

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

    const handleSearch = (query) => {
        setSearchQuery(query);
        if (!query.trim() || !data) {
            setSearchResults([]);
            return;
        }

        const results = data.nodes.filter(node =>
            node.username.toLowerCase().includes(query.toLowerCase()) ||
            node.name.toLowerCase().includes(query.toLowerCase())
        ).slice(0, 10);

        setSearchResults(results);
    };

    const handleSelectSearchResult = (node) => {
        setSelectedNode(node);
        setSearchQuery('');
        setSearchResults([]);
    };

    return (
        <div className="h-screen w-screen relative bg-[#2d2a3d] overflow-hidden">
            {/* Top Header - Floating, doesn't go all the way across */}
            <header className="fixed top-4 left-4 right-[420px] bg-gradient-to-r from-[#4a3f5c] to-[#5d4e6f] shadow-2xl z-50 px-6 py-4 flex items-center justify-between rounded-xl border border-[#6b5b7f]/30 backdrop-blur-sm">
                <h1 className="text-2xl font-bold text-[#f4e9d8]">Telegram Network Analysis</h1>

                <div className="flex items-center gap-4">
                    {/* Search Box */}
                    <div className="relative">
                        <input
                            type="text"
                            placeholder="Search username..."
                            value={searchQuery}
                            onChange={(e) => handleSearch(e.target.value)}
                            className="px-4 py-2 bg-[#3d3450] text-[#e8dcc8] rounded-lg text-sm border border-[#6b5b7f]/50 focus:outline-none focus:border-[#d4885e] w-64"
                        />

                        {/* Search Results Dropdown */}
                        {searchResults.length > 0 && (
                            <div className="absolute top-full mt-2 w-full bg-[#4a3f5c] border border-[#6b5b7f]/50 rounded-lg shadow-xl max-h-64 overflow-y-auto custom-scrollbar z-50">
                                {searchResults.map((node, i) => (
                                    <button
                                        key={i}
                                        onClick={() => handleSelectSearchResult(node)}
                                        className="w-full text-left px-4 py-3 hover:bg-[#5d4e6f] transition-colors border-b border-[#6b5b7f]/30 last:border-b-0"
                                    >
                                        <div className="font-medium text-[#e8dcc8] text-sm">{node.name}</div>
                                        <div className="text-xs text-[#b8a892]">@{node.username}</div>
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>

                    <label className="flex items-center gap-2 cursor-pointer">
                        <input
                            type="checkbox"
                            checked={showLabels}
                            onChange={(e) => setShowLabels(e.target.checked)}
                            className="w-4 h-4 rounded accent-[#d4885e]"
                        />
                        <span className="text-sm text-[#e8dcc8]">Show Labels</span>
                    </label>

                    <label className="flex items-center gap-2 cursor-pointer">
                        <input
                            type="checkbox"
                            checked={showSteps}
                            onChange={(e) => setShowSteps(e.target.checked)}
                            className="w-4 h-4 rounded accent-[#d4885e]"
                        />
                        <span className="text-sm text-[#e8dcc8]">Show Steps</span>
                    </label>

                    <button
                        onClick={() => setShowWordCloud(!showWordCloud)}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${showWordCloud
                                ? 'bg-[#d4885e] text-[#f4e9d8]'
                                : 'bg-[#6b5b7f] text-[#e8dcc8] hover:bg-[#7d6d91]'
                            }`}
                    >
                        {showWordCloud ? 'Hide' : 'Show'} Word Cloud
                    </button>
                </div>
            </header>

            {/* Main Content - Full Screen with sidebars */}
            <div className="h-screen w-screen flex">
                {/* Left Sidebar - Word Cloud (toggleable) */}
                {showWordCloud && (
                    <div className="w-96 bg-gradient-to-b from-[#4a3f5c] to-[#3d3450] shadow-2xl border-r border-[#6b5b7f]/30 flex flex-col overflow-hidden">
                        <div className="bg-gradient-to-r from-[#5d4e6f] to-[#6b5b7f] text-[#f4e9d8] p-4 border-b border-[#6b5b7f]/30">
                            <h3 className="text-lg font-bold">Word Cloud</h3>
                            <p className="text-xs text-[#d4c4b0]">
                                {selectedNode ? `@${selectedNode.username}` : 'Select a channel to view words'}
                            </p>
                        </div>
                        <div className="flex-1 overflow-hidden p-4">
                            {selectedNode ? (
                                <WordCloud username={selectedNode.username} />
                            ) : (
                                <div className="flex items-center justify-center h-full text-[#b8a892] text-center">
                                    <p>Click on a channel to see its word cloud</p>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* Network Graph - Takes remaining space */}
                <div className="flex-1 relative">
                    {loading && (
                        <div className="absolute inset-0 flex items-center justify-center bg-[#2d2a3d] z-10">
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
                            showSteps={showSteps}
                        />
                    )}
                </div>

                {/* Right Sidebar - Fixed, always visible */}
                <div className="w-96 bg-gradient-to-b from-[#4a3f5c] to-[#3d3450] shadow-2xl border-l border-[#6b5b7f]/30 flex flex-col">
                    <NodeSidebar
                        selectedNode={selectedNode}
                        data={data}
                    />
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