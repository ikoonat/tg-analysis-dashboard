import React, { useState, useEffect } from 'react';
import { loadCompleteChannelData } from '../utils/dataProcessor';

const PLUTCHIK = [
    "Joy",
    "Trust",
    "Fear",
    "Surprise",
    "Sadness",
    "Disgust",
    "Anger",
    "Anticipation"
];

const NodeSidebar = ({ selectedNode, data }) => {
    const [channelData, setChannelData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [activeTab, setActiveTab] = useState('overview');

    useEffect(() => {
        if (selectedNode?.username) {
            loadChannelDetails();
        }
    }, [selectedNode]);

    const loadChannelDetails = async () => {
        setLoading(true);
        try {
            const details = await loadCompleteChannelData(selectedNode.username);
            setChannelData(details);
        } catch (error) {
            console.error('Error loading channel details:', error);
            setChannelData(null);
        } finally {
            setLoading(false);
        }
    };

    if (!selectedNode) return null;

    const outgoingConnections = data.edges.filter(e => e.source.id === selectedNode.id);
    const incomingConnections = data.edges.filter(e => e.target.id === selectedNode.id);

    return (
        <div className="h-full bg-gradient-to-b from-[#4f4662] to-[#3a3250] shadow-2xl overflow-hidden flex flex-col text-[#e8dcc8]">

            {/* Header */}
            <div className="bg-gradient-to-r from-[#5f4b8b] to-[#46346e] p-6 border-b border-[#6b5b7f]/50">
                <h2 className="text-xl font-bold mb-2">{selectedNode.name}</h2>
                <p className="text-[#c7bca8] text-sm">@{selectedNode.username}</p>
            </div>

            {/* Tabs */}
            <div className="flex border-b border-[#6b5b7f]/40 bg-[#3a314d]">
                {['overview', 'connections', 'details'].map(tab => (
                    <button
                        key={tab}
                        onClick={() => setActiveTab(tab)}
                        className={`flex-1 py-3 text-sm font-medium transition
                            ${activeTab === tab
                                ? 'border-b-2 border-[#a78bfa] text-[#e8dcc8] bg-[#2e263f]'
                                : 'text-[#c7bca8] hover:text-[#f2eadb]'
                            }`}
                    >
                        {tab.charAt(0).toUpperCase() + tab.slice(1)}
                    </button>
                ))}
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">

                {/* ================= OVERVIEW ================= */}
                {activeTab === 'overview' && (
                    <div className="space-y-4">
                        <div className="bg-[#322b43] rounded-lg p-4 border border-[#6b5b7f]/30">
                            <div className="text-sm text-[#c7bca8] mb-1">Outgoing Shares</div>
                            <div className="text-2xl font-bold text-[#FFBC96]">
                                {selectedNode.outgoing}
                            </div>
                        </div>

                        <div className="bg-[#322b43] rounded-lg p-4 border border-[#6b5b7f]/30">
                            <div className="text-sm text-[#c7bca8] mb-1">Incoming Shares</div>
                            <div className="text-2xl font-bold text-[#FFAAAA]">
                                {selectedNode.incoming}
                            </div>
                        </div>

                        {loading && (
                            <div className="text-center py-8 text-[#c7bca8]">
                                Loading channel details...
                            </div>
                        )}

                        {/* Sentiment Section */}
                        {channelData?.summary?.Sentiment && (
                            <div className="pt-4 border-t border-[#6b5b7f]/40 space-y-2">
                                <h3 className="font-semibold text-[#e8dcc8]">Sentiment</h3>
                                <div className="flex justify-between text-sm">
                                    <span>Positive</span>
                                    <span className="font-semibold text-green-400">
                                        {channelData.summary.Sentiment.Positive || 0}
                                    </span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span>Negative</span>
                                    <span className="font-semibold text-red-400">
                                        {channelData.summary.Sentiment.Negative || 0}
                                    </span>
                                </div>
                            </div>
                        )}

                        {/* Emotive Words Section */}
                        <div className="pt-4 border-t border-[#6b5b7f]/40 space-y-3">
                            <h3 className="font-semibold text-[#e8dcc8]">
                                Emotive Words
                            </h3>

                            <a
                                href="https://www.6seconds.org/2022/03/13/plutchik-wheel-emotions/"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-white-400 underline text-xs"
                            >
                                View Plutchik’s Wheel of Emotions
                            </a>

                            <a
                                href="https://saifmohammad.com/WebPages/NRC-Emotion-Lexicon.htm"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-white-400 underline text-xs block"
                            >
                                Emolex Lexicon Reference
                            </a>

                            <div className="grid grid-cols-2 gap-2 pt-2 text-sm">
                                {PLUTCHIK.map((emotion, index) => (
                                    <div
                                        key={index}
                                        className="bg-[#2e263f] border border-[#6b5b7f]/30 rounded px-2 py-1 flex justify-between"
                                    >
                                        <span>{emotion}</span>
                                        <span className="font-semibold text-[#a78bfa]">
                                            {channelData?.summary?.Dominant_Emotions?.[emotion.toLowerCase()] || 0}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {/* ================= CONNECTIONS ================= */}
                {activeTab === 'connections' && (
                    <div className="space-y-6">

                        <div>
                            <h3 className="font-semibold mb-3">
                                Shares To ({outgoingConnections.length})
                            </h3>

                            <div className="space-y-2 max-h-64 overflow-y-auto custom-scrollbar">
                                {outgoingConnections.map((edge, i) => (
                                    <div key={i} className="bg-[#2e263f] rounded p-3 border border-[#6b5b7f]/20">
                                        <div className="font-medium text-sm">
                                            {edge.target.name}
                                        </div>
                                        <div className="text-xs text-[#c7bca8]">
                                            @{edge.target.username}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div>
                            <h3 className="font-semibold mb-3">
                                Shares From ({incomingConnections.length})
                            </h3>

                            <div className="space-y-2 max-h-64 overflow-y-auto custom-scrollbar">
                                {incomingConnections.map((edge, i) => (
                                    <div key={i} className="bg-[#2e263f] rounded p-3 border border-[#6b5b7f]/20">
                                        <div className="font-medium text-sm">
                                            {edge.source.name}
                                        </div>
                                        <div className="text-xs text-[#c7bca8]">
                                            @{edge.source.username}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                    </div>
                )}

                {/* ================= DETAILS ================= */}
                {activeTab === 'details' && (
                    <div className="space-y-6">

                        {/* Channel Stats moved HERE */}
                        {channelData?.summary && (
                            <div className="space-y-4">
                                <h3 className="font-semibold text-[#e8dcc8]">
                                    Channel Stats
                                </h3>

                                <div className="grid grid-cols-2 gap-3">
                                    {[
                                        { label: 'Total Messages', value: channelData.summary.Total_Messages },
                                        { label: 'Original Posts', value: channelData.summary.Original_Posts },
                                        { label: 'Total Views', value: channelData.summary.Total_Views },
                                        { label: 'Total Forwards', value: channelData.summary.Total_Forwards }
                                    ].map((item, i) => (
                                        <div key={i} className="bg-[#2e263f] rounded p-3 border border-[#6b5b7f]/20">
                                            <div className="text-xs text-[#c7bca8]">{item.label}</div>
                                            <div className="text-lg font-semibold">
                                                {item.value || 0}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        <h3 className="font-semibold mb-3 pt-4 border-t border-[#6b5b7f]/40">
                            Recent Messages
                        </h3>

                        {loading && (
                            <div className="text-center py-8 text-[#c7bca8]">
                                Loading messages...
                            </div>
                        )}

                        {channelData?.messages && channelData.messages.length > 0 ? (
                            <div className="space-y-3 max-h-96 overflow-y-auto custom-scrollbar">
                                {channelData.messages.slice(0, 10).map((msg, i) => (
                                    <div
                                        key={i}
                                        className="border border-[#6b5b7f]/40 rounded-lg p-3 bg-[#2e263f] hover:bg-[#382f4a] transition"
                                    >
                                        <div className="text-xs text-[#c7bca8] mb-2">
                                            {new Date(msg.Message_Date).toLocaleDateString()}
                                        </div>
                                        <div className="text-sm line-clamp-3">
                                            {msg.Message_Text || 'No text'}
                                        </div>

                                        {msg.Message_URL && (
                                            <a
                                                href={msg.Message_URL}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="text-xs text-[#a78bfa] hover:underline mt-2 inline-block"
                                            >
                                                View Message →
                                            </a>
                                        )}
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-8 text-[#c7bca8]">
                                No message data available
                            </div>
                        )}
                    </div>
                )}

            </div>
        </div>
    );
};

export default NodeSidebar;
