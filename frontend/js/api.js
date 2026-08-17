// Production (Port 80/443 qua Nginx proxy): API_BASE = '/api'
// Development (Port 8080): API_BASE = 'http://host:8000/api'
const API_BASE = (window.location.port === '8080')
    ? window.location.protocol + '//' + window.location.hostname + ':8000/api'
    : '/api';

// Lấy Token từ sessionStorage (an toàn hơn localStorage — tự xóa khi đóng tab)
function getToken() {
    return sessionStorage.getItem('token');
}

function setToken(token) {
    sessionStorage.setItem('token', token);
}

function removeToken() {
    sessionStorage.removeItem('token');
}

async function fetchAPI(endpoint, method = 'GET', body = null) {
    const options = {
        method,
        headers: {},
    };

    // Tự động gắn JWT Token vào mọi request (nếu đã đăng nhập)
    const token = getToken();
    if (token) {
        options.headers['Authorization'] = `Bearer ${token}`;
    }

    if (body) {
        options.headers['Content-Type'] = 'application/json';
        options.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, options);
        if (!response.ok) {
            const errorData = await response.json();
            let msg = 'Something went wrong';
            if (typeof errorData.detail === 'string') {
                msg = errorData.detail;
            } else if (Array.isArray(errorData.detail) && errorData.detail.length > 0) {
                msg = errorData.detail.map(e => e.msg).join(', ');
            }
            // Nếu Token hết hạn hoặc bị sai -> tự động logout
            if (response.status === 401) {
                removeToken();
                window.location.href = '/login.html';
                return;
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
