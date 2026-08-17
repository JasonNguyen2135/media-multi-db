// Global user state
let currentUser = null;
let currentArticleId = null;

// --- Auth Functions ---
async function checkAuth() {
    const token = getToken();
    if (!token) return;

    try {
        // Gọi API /me để Backend giải mã Token và trả về thông tin user
        // Không còn bốc thông tin từ localStorage nữa!
        currentUser = await fetchAPI('/auth/me');
        updateNavUser();
    } catch (error) {
        // Token hết hạn hoặc sai -> xóa đi
        removeToken();
        currentUser = null;
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
    removeToken();
    currentUser = null;
    window.location.href = '/index.html';
}

async function handleLogin() {
    const usernameInput = document.getElementById('username').value;
    const passwordInput = document.getElementById('password').value;
    const errorMsg = document.getElementById('error-msg');

    try {
        const result = await fetchAPI('/auth/login', 'POST', { username: usernameInput, password: passwordInput });
        // Chỉ lưu Token vào sessionStorage, KHÔNG lưu id/username/role
        setToken(result.access_token);
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
        const result = await fetchAPI('/auth/register', 'POST', { username: usernameInput, password: passwordInput });
        // Chỉ lưu Token vào sessionStorage, KHÔNG lưu id/username/role
        setToken(result.access_token);
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
            ${art.image_id ? `<img src="${API_BASE}/articles/image/${art.image_id}" class="w-full h-48 object-cover rounded mb-4" alt="Article Cover">` : ''}
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
    currentArticleId = id;
    try {
        const art = await fetchAPI(`/articles/${id}`);
        
        document.getElementById('modal-title').innerText = art.title;
        document.getElementById('modal-author').innerText = `By: ${art.author_name || 'Unknown'}`;
        document.getElementById('modal-views').innerText = `${art.views || 0} Views`;
        
        // Show delete button only to the article's actual author (safe null check)
        const deleteBtn = document.getElementById('delete-btn');
        if (deleteBtn) {
            const isOwner = currentUser && Number(currentUser.id) === Number(art.author_id);
            isOwner ? deleteBtn.classList.remove('hidden') : deleteBtn.classList.add('hidden');
        }
        
        const imageContainer = document.getElementById('modal-image-container');
        if (imageContainer) {
            imageContainer.innerHTML = art.image_id
                ? `<img src="${API_BASE}/articles/image/${art.image_id}" class="w-full h-64 object-cover rounded mb-4" alt="Article Cover">`
                : '';
        }

        document.getElementById('modal-content').innerText = art.content;
        
        // Show/hide comment form based on login status
        const commentForm = document.getElementById('comment-form');
        const loginNotice = document.getElementById('comment-login-notice');
        if (commentForm && loginNotice) {
            if (currentUser) {
                commentForm.classList.remove('hidden');
                loginNotice.classList.add('hidden');
            } else {
                commentForm.classList.add('hidden');
                loginNotice.classList.remove('hidden');
            }
        }
        
        document.getElementById('article-modal').classList.remove('hidden');
        
        // Load comments
        loadComments(id);
        
        // Silently reload article list to update view counter
        setTimeout(() => loadArticles(), 500);
    } catch (error) {
        alert('Failed to load article details: ' + error.message);
    }
}

async function loadComments(articleId, silent = false) {
    const list = document.getElementById('comments-list');
    if (!list) return;
    if (!silent) list.innerHTML = '<p class="text-gray-400 text-sm">Loading comments...</p>';
    
    try {
        const comments = await fetchAPI(`/comments/${articleId}`);
        if (comments.length === 0) {
            list.innerHTML = '<p class="text-gray-400 text-sm italic">No comments yet. Be the first to comment!</p>';
        } else {
            list.innerHTML = comments.map(c => `
                <div class="flex gap-3 p-4 bg-gray-50 rounded-lg">
                    <div class="w-9 h-9 rounded-full bg-teal-500 flex items-center justify-center text-white font-bold flex-shrink-0 text-sm">
                        ${c.author_name.charAt(0).toUpperCase()}
                    </div>
                    <div class="flex-1">
                        <div class="flex items-center gap-2 mb-1">
                            <span class="font-semibold text-gray-800 text-sm">${c.author_name}</span>
                            <span class="text-xs text-gray-400">${new Date(c.created_at).toLocaleString()}</span>
                        </div>
                        <p class="text-gray-700 text-sm">${c.content}</p>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        if (!silent) list.innerHTML = '<p class="text-red-400 text-sm">Failed to load comments.</p>';
    }
    
    // Start auto-refresh every 5s while modal is open (only start once)
    if (!window._commentRefreshTimer && currentArticleId === articleId) {
        window._commentRefreshTimer = setInterval(() => {
            if (currentArticleId) loadComments(currentArticleId, true);
        }, 5000);
    }
}

async function submitComment() {
    if (!currentUser || !currentArticleId) return;
    
    const input = document.getElementById('comment-input');
    const content = input.value.trim();
    if (!content) {
        alert('Please write something before posting!');
        return;
    }
    
    const isAnonymous = document.getElementById('comment-anonymous').checked;
    const authorName = isAnonymous ? 'Anonymous' : currentUser.username;
    
    try {
        await fetchAPI(`/comments/${currentArticleId}`, 'POST', {
            article_id: currentArticleId,
            author_id: currentUser.id,
            author_name: authorName,
            content: content
        });
        input.value = '';
        document.getElementById('comment-anonymous').checked = false;
        loadComments(currentArticleId);
    } catch (error) {
        alert('Failed to post comment: ' + error.message);
    }
}

async function deleteArticle() {
    if (!currentUser || !currentArticleId) {
        alert('Error: Not logged in or no article selected.');
        return;
    }
    
    const authorId = Number(currentUser.id);
    if (!authorId) {
        alert('Error: Invalid user session. Please logout and login again.');
        return;
    }
    
    if (!confirm('Are you sure you want to delete this article? This cannot be undone.')) return;
    
    try {
        await fetchAPI(`/articles/${currentArticleId}?author_id=${authorId}`, 'DELETE');
        closeModal();
        loadArticles();
    } catch (error) {
        alert('Failed to delete: ' + error.message);
    }
}

function closeModal() {
    document.getElementById('article-modal').classList.add('hidden');
    // Stop comment auto-refresh when modal closes
    if (window._commentRefreshTimer) {
        clearInterval(window._commentRefreshTimer);
        window._commentRefreshTimer = null;
    }
    currentArticleId = null;
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
    const isAnonymous = document.getElementById('is-anonymous').checked;
    
    if (!title || !content) {
        alert('Title and content are required!');
        return;
    }

    const tags = tagsStr.split(',').map(t => t.trim()).filter(t => t);
    const imageFile = document.getElementById('article-image').files[0];
    
    let image_id = null;
    if (imageFile) {
        try {
            const formData = new FormData();
            formData.append('file', imageFile);
            
            const uploadRes = await fetch(`${API_BASE}/articles/upload-image`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${getToken()}`
                },
                body: formData
            });
            
            if (!uploadRes.ok) throw new Error("Image upload failed");
            
            const uploadData = await uploadRes.json();
            image_id = uploadData.image_id;
        } catch (error) {
            alert('Failed to upload image: ' + error.message);
            return;
        }
    }

    try {
        await fetchAPI('/articles/', 'POST', {
            title,
            content,
            author_id: currentUser.id,
            author_name: currentUser.username,
            is_anonymous: isAnonymous,
            tags,
            image_id
        });
        alert('Article published successfully! (Saved to Postgres)');
        window.location.href = '/index.html';
    } catch (error) {
        alert('Failed to publish: ' + error.message);
    }
}
