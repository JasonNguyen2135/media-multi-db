// Tự động lấy IP/Domain hiện tại của web và gọi tới port 8000 (Backend)
const API_BASE = window.location.protocol + '//' + window.location.hostname + ':8000/api';

async function fetchAPI(endpoint, method = 'GET', body = null) {
    const options = {
        method,
        headers: {},
    };

    if (body) {
        options.headers['Content-Type'] = 'application/json';
        options.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, options);
        if (!response.ok) {
            const errorData = await response.json();
            // FastAPI validation errors return {detail: [{msg: ...}]}, others return {detail: "string"}
            let msg = 'Something went wrong';
            if (typeof errorData.detail === 'string') {
                msg = errorData.detail;
            } else if (Array.isArray(errorData.detail) && errorData.detail.length > 0) {
                msg = errorData.detail.map(e => e.msg).join(', ');
            }
            throw new Error(msg);
        }
        // Handle empty responses (e.g., 204 No Content)
        const text = await response.text();
        return text ? JSON.parse(text) : {};
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}
