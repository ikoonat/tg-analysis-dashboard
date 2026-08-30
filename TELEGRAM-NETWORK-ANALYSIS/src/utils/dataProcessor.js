import Papa from 'papaparse';

/**
 * Process telegram_shares.csv into nodes and edges
 */
export const processCSV = (csvText) => {
    const result = Papa.parse(csvText, {
        header: true,
        skipEmptyLines: true,
        transformHeader: (header) => header.trim()
    });

    const edges = [];
    const nodeMap = new Map();

    result.data.forEach(row => {
        const fromId = row['From_Channel_ID'];
        const toId = row['To_Channel_ID'];
        const fromUsername = row['From_Channel_Username'];
        const toUsername = row['To_Channel_Username'];
        const fromName = row['From_Channel_Name'];
        const toName = row['To_Channel_Name'];

        if (!fromId || !toId) return;

        // Create or update source node
        if (!nodeMap.has(fromId)) {
            nodeMap.set(fromId, {
                id: fromId,
                username: fromUsername || 'Unknown',
                name: fromName || 'Unknown',
                outgoing: 0,
                incoming: 0,
                messages: []
            });
        }

        // Create or update target node
        if (!nodeMap.has(toId)) {
            nodeMap.set(toId, {
                id: toId,
                username: toUsername || 'Unknown',
                name: toName || 'Unknown',
                outgoing: 0,
                incoming: 0,
                messages: []
            });
        }

        // Update edge counts
        nodeMap.get(fromId).outgoing++;
        nodeMap.get(toId).incoming++;

        // Create edge
        edges.push({
            source: fromId,
            target: toId,
            messageId: row['Message_ID'],
            messageUrl: row['Message_URL'],
            messageDate: row['Message_Date'],
            messagePreview: row['Message_Text_Preview']
        });
    });

    const nodes = Array.from(nodeMap.values());
    return { nodes, edges };
};

/**
 * Load channel summary JSON for a specific username
 */
export const loadChannelSummary = async (username) => {
    try {
        const res = await fetch(`/data/per_channel/${username}_summary.json`);
        if (!res.ok) throw new Error(`Failed to load summary for ${username}`);
        return await res.json();
    } catch (error) {
        console.error(`Error loading summary for ${username}:`, error);
        return null;
    }
};

/**
 * Load channel messages CSV for a specific username
 */
export const loadChannelMessages = async (username) => {
    try {
        const res = await fetch(`/data/per_channel/${username}.csv`);
        if (!res.ok) throw new Error(`Failed to load messages for ${username}`);
        const text = await res.text();

        const result = Papa.parse(text, {
            header: true,
            skipEmptyLines: true,
            transformHeader: (header) => header.trim()
        });

        return result.data;
    } catch (error) {
        console.error(`Error loading messages for ${username}:`, error);
        return [];
    }
};

/**
 * Auto-load telegram_shares.csv from /public/data
 */
export const loadDataFromPublic = async () => {
    try {
        // Load the main telegram_shares.csv file
        const res = await fetch('/data/telegram_shares.csv');
        if (!res.ok) {
            throw new Error('Failed to load telegram_shares.csv');
        }

        const text = await res.text();
        const graphData = processCSV(text);

        console.log('Loaded network data:', {
            nodes: graphData.nodes.length,
            edges: graphData.edges.length
        });

        return graphData;
    } catch (error) {
        console.error('Error loading data from public:', error);
        throw error;
    }
};

/**
 * Load complete data for a specific channel (summary + messages)
 */
export const loadCompleteChannelData = async (username) => {
    const [summary, messages] = await Promise.all([
        loadChannelSummary(username),
        loadChannelMessages(username)
    ]);

    return {
        summary,
        messages
    };
};