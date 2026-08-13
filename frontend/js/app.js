// Global user state
let currentUser = null;

// --- Auth Functions ---
function checkAuth() {
    const userJson = localStorage.getItem('user');
    if (userJson) {
        currentUser = JSON.parse(userJson);
        updateNavUser();
    }
}

function updateNavUser() {
    const userInfoDiv = document.getElementById('user-info');
    if (userInfoDiv && currentUser) {
        userInfoDiv.innerHTML = `
            <span class="text-white mr-4">Welcome, ${currentUser.username}</span>
            <button onclick="logout()" class="inline-block text-sm px-4 py-2 leading-none border rounded text-white border-white hover:border-transparent hover:text-teal-500 hover:bg-white">Logout</button>
        `;
    }
}

function logout() {
    localStorage.removeItem('user');
    currentUser = null;
    window.location.href = '/index.html';
}

async function handleLogin() {
    const usernameInput = document.getElementById('username').value;
    const passwordInput = document.getElementById('password').value;
    const errorMsg = document.getElementById('error-msg');

    try {
        const user = await fetchAPI('/auth/login', 'POST', { username: usernameInput, password: passwordInput });
        localStorage.setItem('user', JSON.stringify(user));
        window.location.href = '/index.html';
    } catch (error) {
        errorMsg.innerText = error.message;
        errorMsg.classList.remove('hidden');
    }
}

async function handleRegister() {
    const usernameInput = document.getElementById('username').value;
    const passwordInput = document.getElementById('password').value;
    const errorMsg = document.getElementById('error-msg');

    try {
        const user = await fetchAPI('/auth/register', 'POST', { username: usernameInput, password: passwordInput });
        localStorage.setItem('user', JSON.stringify(user));
        window.location.href = '/index.html';
    } catch (error) {
        errorMsg.innerText = error.message;
        errorMsg.classList.remove('hidden');
    }
}

// --- Article Display Functions ---
async function loadArticles(searchQuery = '') {
    const container = document.getElementById('articles-container');
    if (!container) return;

    container.innerHTML = '<p class="text-gray-500">Loading articles...</p>';
    
    let url = '/articles/';
    if (searchQuery) url += `?search=${encodeURIComponent(searchQuery)}`;

    try {
        const articles = await fetchAPI(url);
        renderArticles(articles, container);
        updateTrending(articles);
    } catch (error) {
        container.innerHTML = `<p class="text-red-500">Failed to load articles.</p>`;
    }
}

function renderArticles(articles, container) {
    if (articles.length === 0) {
        container.innerHTML = '<p class="text-gray-500">No articles found.</p>';
        return;
    }

    container.innerHTML = articles.map(art => `
        <div class="bg-white p-6 rounded shadow-sm border border-gray-100 hover:shadow-md transition cursor-pointer" onclick="openArticle(${art.id})">
            <h2 class="text-2xl font-bold text-teal-600 mb-2">${art.title}</h2>
            <div class="flex gap-2 mb-3">
                ${art.tags.map(t => `<span class="bg-gray-200 text-xs px-2 py-1 rounded text-gray-600">${t}</span>`).join('')}
            </div>
            <p class="text-gray-700 mb-4">${art.content.substring(0, 150)}...</p>
            <div class="text-sm text-gray-400 flex justify-between">
                <span>Author ID: ${art.author_id}</span>
                <span>👀 ${art.views} Views</span>
            </div>
        </div>
    `).join('');
}

function searchArticles() {
    const query = document.getElementById('search-input').value;
    loadArticles(query);
}

function updateTrending(articles) {
    const trendingContainer = document.getElementById('trending-container');
    if (!trendingContainer) return;

    // Sort by views descending
    const sorted = [...articles].sort((a, b) => b.views - a.views).slice(0, 5);
    
    if (sorted.length === 0) {
         trendingContainer.innerHTML = '<li class="text-gray-500 text-sm">No trending articles yet.</li>';
         return;
    }

    trendingContainer.innerHTML = sorted.map(art => `
        <li class="border-b pb-2 cursor-pointer hover:text-teal-600" onclick="openArticle(${art.id})">
            <div class="font-semibold text-gray-800 hover:text-teal-600">${art.title}</div>
            <div class="text-xs text-gray-500">👀 ${art.views} Views</div>
        </li>
    `).join('');
}

// --- Article Detail & Modal Functions ---
async function openArticle(id) {
    try {
        const art = await fetchAPI(`/articles/${id}`);
        
        document.getElementById('modal-title').innerText = art.title;
        document.getElementById('modal-author').innerText = `Author ID: ${art.author_id}`;
        document.getElementById('modal-views').innerText = `${art.views} Views`;
        document.getElementById('modal-content').innerText = art.content;
        
        document.getElementById('article-modal').classList.remove('hidden');
        
        // Reload background articles silently to update view counters in UI
        setTimeout(() => loadArticles(), 500); 
    } catch (error) {
        alert('Failed to load article details.');
    }
}

function closeModal() {
    document.getElementById('article-modal').classList.add('hidden');
}

// --- Editor Functions (Drafts & Publish) ---
async function autoSaveDraft() {
    if (!currentUser) return;
    
    const title = document.getElementById('article-title').value;
    const content = document.getElementById('article-content').value;
    const tagsStr = document.getElementById('article-tags').value;
    
    if (!title && !content) return; // Don't save empty draft
    
    const statusEl = document.getElementById('draft-status');
    statusEl.innerText = 'Saving...';
    
    try {
        await fetchAPI('/drafts/', 'POST', {
            author_id: currentUser.id,
            draft_data: {
                title,
                content,
                tags: tagsStr
            }
        });
        statusEl.innerText = 'Saved (Mongo)';
        statusEl.classList.add('text-teal-600');
        setTimeout(() => { statusEl.classList.remove('text-teal-600'); statusEl.classList.add('text-gray-500'); }, 2000);
    } catch (error) {
        statusEl.innerText = 'Failed to save';
        statusEl.classList.add('text-red-500');
    }
}

async function publishArticle() {
    if (!currentUser) {
        alert('Please login first');
        return;
    }

    const title = document.getElementById('article-title').value;
    const content = document.getElementById('article-content').value;
    const tagsStr = document.getElementById('article-tags').value;
    
    if (!title || !content) {
        alert('Title and content are required!');
        return;
    }

    const tags = tagsStr.split(',').map(t => t.trim()).filter(t => t);

    try {
        await fetchAPI('/articles/', 'POST', {
            title,
            content,
            author_id: currentUser.id,
            tags
        });
        alert('Article published successfully! (Saved to Postgres)');
        
        // Optionally clear draft in mongo here
        
        window.location.href = '/index.html';
    } catch (error) {
        alert('Failed to publish: ' + error.message);
    }
}
