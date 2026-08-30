import WordCloud from '../src/components/WordCloud';

export default {
    title: 'Components/WordCloud',
    component: WordCloud,
};

export const Default = {
    args: {
        words: [
            { text: 'ukraine', size: 18 },
            { text: 'russia', size: 16 },
            { text: 'news', size: 14 },
        ],
    },
};