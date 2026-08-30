// src/components/WordCloud.jsx
import React, { useEffect, useState } from 'react';
import Papa from 'papaparse';

const palette = ['#d4885e', '#c27850', '#b8a892', '#e8dcc8', '#6b5b7f', '#7d6d91'];
const stopwordLanguages = [
    'arabic', 'belarusian', 'english', 'finnish', 'german',
    'hebrew', 'polish', 'russian', 'swedish', 'ukrainian'
];

const isRTL = (word) => /[\u0590-\u08FF]/.test(word);

const hashWord = (word) => {
    let hash = 0;
    for (let index = 0; index < word.length; index += 1) {
        hash = (hash * 31 + word.charCodeAt(index)) >>> 0;
    }
    return hash;
};

const getRotation = (word) => {
    const hash = hashWord(word);
    return hash % 10 === 0 ? (hash % 2 === 0 ? 90 : -90) : 0;
};

const extractWords = (text) => {
    if (!text) return [];

    return text
        .replace(/[\n\r]/g, ' ')
        .replace(/[^\p{L}\p{N}\s]/gu, '')
        .split(/\s+/)
        .map(w => w.trim().toLowerCase())
        .filter(w => w.length > 1 && !/^\d+$/.test(w));
};

const WordCloud = ({ username }) => {
    const [words, setWords] = useState(null);
    const [stopwords, setStopwords] = useState(new Set());
    const [error, setError] = useState(null);

    /* -------------------------
    LOAD STOPWORDS (ALL AVAILABLE LANGUAGE FILES)
    --------------------------*/
    useEffect(() => {
        async function loadStopwords() {
            try {
                const stopwordTexts = await Promise.all(
                    stopwordLanguages.map(language =>
                        fetch(`/data/stopwords/${language}_stopwords.txt`).then(res => {
                            if (!res.ok) throw new Error(`Stopword fetch failed: ${res.status}`);
                            return res.text();
                        })
                    )
                );

                const set = new Set(
                    stopwordTexts.flatMap(text => text.split('\n'))
                        .map(w => w.trim().toLowerCase())
                        .filter(Boolean)
                );

                setStopwords(set);
                console.log(`WordCloud: Loaded ${set.size} stopwords`);
            } catch (err) {
                console.error('Failed loading stopwords:', err);
            }
        }

        loadStopwords();
    }, []);

    /* -------------------------
       LOAD & PROCESS CSV
    --------------------------*/
    useEffect(() => {
        if (!username) {
            console.warn('WordCloud: no username provided');
            setWords([]);
            return;
        }

        const path = `/data/per_channel/${username}.csv`;
        console.log('WordCloud: fetching CSV from', path);

        fetch(path)
            .then(res => {
                if (!res.ok) {
                    throw new Error(`CSV fetch failed: ${res.status}`);
                }
                return res.text();
            })
            .then(csvText => {
                const parsed = Papa.parse(csvText, {
                    header: true,
                    skipEmptyLines: true
                });

                if (!parsed.data || parsed.data.length === 0) {
                    console.warn('WordCloud: no CSV data found');
                    setWords([]);
                    return;
                }

                const freq = {};

                parsed.data.forEach(msg => {
                    const txt =
                        msg.Message_Text ||
                        msg.message_text ||
                        msg.text ||
                        '';

                    const extracted = extractWords(txt);

                    extracted.forEach(word => {
                        if (!stopwords.has(word)) {
                            freq[word] = (freq[word] || 0) + 1;
                        }
                    });
                });

                const freqWords = Object.entries(freq)
                    .map(([text, count]) => ({ text, count }))
                    .sort((a, b) => b.count - a.count)
                    .slice(0, 120);

                if (freqWords.length === 0) {
                    console.warn('WordCloud: no valid words after filtering');
                    setWords([]);
                    return;
                }

                const max = freqWords[0].count;

                const sized = freqWords.map((w, i) => ({
                    ...w,
                    size: 12 + (w.count / max) * 34,
                    color: palette[i % palette.length],
                    rotation: getRotation(w.text)
                }));

                setWords(sized);
            })
            .catch(err => {
                console.error('WordCloud: CSV error:', err);
                setError(err.message);
                setWords([]);
            });
    }, [username, stopwords]);

    /* -------------------------
       RENDER
    --------------------------*/

    if (error) {
        return (
            <div className="p-4 bg-[#2e263f] rounded-md text-red-400 text-sm border border-[#6b5b7f]/30">
                WordCloud Error: {error}
            </div>
        );
    }

    if (words === null) {
        return (
            <div className="p-4 bg-[#2e263f] rounded-md text-[#b8a892] text-sm border border-[#6b5b7f]/30 text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-2 border-[#d4885e] border-t-transparent mx-auto mb-2"></div>
                Loading word cloud...
            </div>
        );
    }

    if (words.length === 0) {
        return (
            <div className="p-4 bg-[#2e263f] rounded-md text-[#b8a892] text-sm border border-[#6b5b7f]/30 text-center">
                No words available for Word Cloud
            </div>
        );
    }

    return (
        <div className="flex flex-wrap gap-2 p-4 bg-[#2e263f] border border-[#6b5b7f]/30 rounded-md justify-center overflow-y-auto h-full custom-scrollbar">
            {words.map((w, i) => (
                <span
                    key={i}
                    className="inline-block px-2 py-1 rounded select-none hover:brightness-125 transition-[filter] cursor-default"
                    style={{
                        fontSize: `${w.size}px`,
                        color: w.color,
                        transform: `rotate(${w.rotation}deg)`,
                        transformOrigin: 'center center',
                        fontFamily: isRTL(w.text)
                            ? '"Noto Sans Hebrew","Noto Sans Arabic",Arial,sans-serif'
                            : 'Arial, "Segoe UI", sans-serif',
                        direction: isRTL(w.text) ? 'rtl' : 'ltr'
                    }}
                    title={`${w.count} occurrence${w.count > 1 ? 's' : ''}`}
                >
                    {w.text}
                </span>
            ))}
        </div>
    );
};

export default WordCloud;