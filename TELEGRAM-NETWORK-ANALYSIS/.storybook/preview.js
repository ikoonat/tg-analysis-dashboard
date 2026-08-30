// .storybook/preview.js (or .storybook/preview.ts if using TS)

import '../src/index.css';  // import your global Tailwind / base CSS

export const parameters = {
    actions: { argTypesRegex: '^on[A-Z].*' },
    controls: {
        matchers: {
            color: /(background|color)$/i,
            date: /Date$/,
        },
    },
};
