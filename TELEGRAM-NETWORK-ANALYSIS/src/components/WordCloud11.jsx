import React from 'react';

const WordCloud = ({ words = [] }) => {
    // Default sample words if none provided
    const defaultWords = [
        { text: 'ukraine', size: 18 },
        { text: 'russia', size: 16 },
        { text: 'news', size: 14 },
        { text: 'today', size: 15 },
        { text: 'breaking', size: 12 },
        { text: 'אוקראינה', size: 16 },
        { text: 'חדשות', size: 14 },
        { text: 'اليوم', size: 15 },
        { text: 'أخبار', size: 13 },
    ];

    const displayWords = words.length > 0 ? words : defaultWords;

    return (
        <div className="flex flex-wrap gap-2 p-4 bg-gray-50 rounded">
            {displayWords.map((word, idx) => (
                <span
                    key={idx}
                    className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm"
                    style={{ fontSize: `${word.size || 12 + Math.random() * 8}px` }}
                >
                    {word.text}
                </span>
            ))}
        </div>
    );
};

export default WordCloud;