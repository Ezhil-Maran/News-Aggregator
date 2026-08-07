const API_BASE_URL = "http://127.0.0.1:8000";

/**
 * Fetches the latest AI-generated news.
 */
export async function fetchNews() {
    try {
        const response = await fetch(`${API_BASE_URL}/news`);

        if (!response.ok) {
            throw new Error(`Server returned ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error("Failed to fetch news:", error);
        throw error;
    }
}