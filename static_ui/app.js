const app = {
  state: {
    token: localStorage.getItem('celib_token'),
    user: null,
    books: [],
    filteredBooks: [],
    currentBook: null,
    theme: localStorage.getItem('celib_theme') || 'dark',
    fontSize: 100,
    purchasedBooks: JSON.parse(localStorage.getItem('celib_purchased') || '[]'),
    searchQuery: '',
    selectedCategory: null,
    // PDF Reader State
    pdfDoc: null,
    currentPage: 1,
    totalPages: 0,
    scale: 1.5,
    rendering: false
  },

  init: async () => {
    app.setTheme(app.state.theme);
    app.updateAuthUI();
    if (app.state.token) {
      await app.refreshLibrary();
    }
    const view = window.location.hash.replace('#', '') || 'library';
    app.navigate(view);
  },

  getHeaders: () => ({ 'Authorization': `Bearer ${app.state.token}` }),

  parseJwt: (token) => {
    try { return JSON.parse(atob(token.split('.')[1])); } catch (e) { return {}; }
  },

  updateAuthUI: () => {
    if (app.state.token) app.showApp();
    else app.showAuth();
  },

  // Auth Flow
  showAuth: () => {
    document.getElementById('authContainer').classList.remove('hidden');
    document.getElementById('appShell').classList.add('hidden');
  },

  showApp: () => {
    document.getElementById('authContainer').classList.add('hidden');
    document.getElementById('appShell').classList.remove('hidden');

    const claims = app.parseJwt(app.state.token);
    document.getElementById('authStatus').textContent = claims.email;

    // Show admin nav if user is admin
    if (claims.isAdmin) {
      const adminNav = document.querySelector('.admin-only');
      if (adminNav) {
        adminNav.classList.remove('hidden');
        adminNav.classList.add('visible');
      }
    }

    app.navigate('library');
  },

  switchAuthTab: (tab) => {
    document.querySelectorAll('.auth-tab').forEach(el => el.classList.remove('active'));
    document.getElementById(`tab${tab.charAt(0).toUpperCase() + tab.slice(1)}`).classList.add('active');

    if (tab === 'login') {
      document.getElementById('formLogin').classList.remove('hidden');
      document.getElementById('formSignup').classList.add('hidden');
    } else {
      document.getElementById('formLogin').classList.add('hidden');
      document.getElementById('formSignup').classList.remove('hidden');
    }
  },

  login: async () => {
    const email = document.getElementById('li_email').value;
    const password = document.getElementById('li_pass').value;
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      const data = await res.json();
      if (res.ok) {
        localStorage.setItem('celib_token', data.token);
        app.state.token = data.token;
        app.state.user = data.user;
        app.init();
      } else alert(data.error);
    } catch (e) { alert('Login failed'); }
  },

  signup: async () => {
    const name = document.getElementById('su_name').value;
    const email = document.getElementById('su_email').value;
    const password = document.getElementById('su_pass').value;
    try {
      const res = await fetch('/api/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, password })
      });
      const data = await res.json();
      if (res.ok) {
        localStorage.setItem('celib_token', data.token);
        app.state.token = data.token;
        app.state.user = data.user;
        app.init();
      } else alert(data.error);
    } catch (e) { alert('Signup failed'); }
  },

  logout: () => {
    localStorage.removeItem('celib_token');
    app.state.token = null;
    app.state.user = null;
    window.location.reload();
  },

  // Navigation
  navigate: (view) => {
    document.querySelectorAll('.view').forEach(el => el.classList.add('hidden'));
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));

    const target = document.getElementById(`view-${view}`);
    if (target) target.classList.remove('hidden');

    // Highlight nav
    const nav = document.querySelector(`.nav-item[onclick*="${view}"]`);
    if (nav) nav.classList.add('active');

    // Load admin dashboard if navigating to admin view
    if (view === 'admin') {
      app.loadAdminDashboard();
    }
  },

  // Library
  refreshLibrary: async () => {
    try {
      const res = await fetch('/api/books/', { headers: app.getHeaders() });
      if (res.ok) {
        app.state.books = await res.json();
        app.state.filteredBooks = app.state.books;
        app.renderCategoryFilters();
        app.renderLibrary();
      }
    } catch (e) { console.error(e); }
  },

  renderLibrary: () => {
    const grid = document.getElementById('libraryGrid');
    if (!grid) return;
    grid.innerHTML = '';

    const booksToRender = app.state.filteredBooks.length > 0 ? app.state.filteredBooks : app.state.books;

    if (booksToRender.length === 0) {
      grid.innerHTML = '<div style="grid-column: 1/-1; text-align:center; padding:60px; color:var(--text-muted);">No books found</div>';
      return;
    }

    booksToRender.forEach(book => {
      const isPaid = book.price > 0;
      const isPurchased = !isPaid || app.state.purchasedBooks.includes(book.id);

      const card = document.createElement('div');
      card.className = `book-card ${!isPurchased ? 'locked' : ''}`;
      card.onclick = () => app.handleBookClick(book, isPurchased);

      // Generate random gradient for cover
      const hue = Math.floor(Math.random() * 360);

      // Category badges
      const categories = book.categories || [];
      const categoryBadges = categories.length > 0
        ? `<div class="category-badges">${categories.map(cat => `<span class="category-badge">${cat}</span>`).join('')}</div>`
        : '';

      card.innerHTML = `
        <div class="book-cover" style="background: linear-gradient(135deg, hsl(${hue}, 40%, 20%), hsl(${hue}, 40%, 10%))">
          <span>${book.title[0]}</span>
          <div class="price-badge ${isPaid ? '' : 'free'}">
            ${isPaid ? '$' + book.price.toFixed(2) : 'FREE'}
          </div>
        </div>
        <div class="book-info">
          <div class="book-title">${book.title}</div>
          <div class="book-author">${book.author}</div>
          ${categoryBadges}
        </div>
      `;
      grid.appendChild(card);
    });
  },

  // Search and Filter Functions
  searchBooks: (query) => {
    app.state.searchQuery = query.toLowerCase();
    app.applyFilters();
  },

  filterByCategory: (category) => {
    app.state.selectedCategory = app.state.selectedCategory === category ? null : category;
    app.renderCategoryFilters();
    app.applyFilters();
  },

  clearSearch: () => {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) searchInput.value = '';
    app.state.searchQuery = '';
    app.state.selectedCategory = null;
    app.renderCategoryFilters();
    app.applyFilters();
  },

  applyFilters: () => {
    let filtered = app.state.books;

    // Apply search filter
    if (app.state.searchQuery) {
      filtered = filtered.filter(book => {
        const searchText = `${book.title} ${book.author} ${(book.categories || []).join(' ')}`.toLowerCase();
        return searchText.includes(app.state.searchQuery);
      });
    }

    // Apply category filter
    if (app.state.selectedCategory) {
      filtered = filtered.filter(book => {
        return (book.categories || []).includes(app.state.selectedCategory);
      });
    }

    app.state.filteredBooks = filtered;
    app.renderLibrary();
  },

  extractCategories: () => {
    const categoriesSet = new Set();
    app.state.books.forEach(book => {
      if (book.categories && Array.isArray(book.categories)) {
        book.categories.forEach(cat => categoriesSet.add(cat));
      }
    });
    return Array.from(categoriesSet).sort();
  },

  renderCategoryFilters: () => {
    const container = document.getElementById('categoryFilters');
    if (!container) return;

    const categories = app.extractCategories();
    if (categories.length === 0) {
      container.innerHTML = '';
      return;
    }

    container.innerHTML = `
      <div style="font-size:0.8rem; font-weight:600; color:var(--text-muted); margin-bottom:10px;">FILTER BY CATEGORY</div>
      ${categories.map(cat => `
        <div class="category-chip ${app.state.selectedCategory === cat ? 'active' : ''}" 
             onclick="app.filterByCategory('${cat}')">
          ${cat}
        </div>
      `).join('')}
    `;
  },

  handleBookClick: (book, isPurchased) => {
    if (isPurchased) {
      app.openReader(book);
    } else {
      app.showPurchaseModal(book);
    }
  },

  showPurchaseModal: (book) => {
    const modal = document.getElementById('summaryModal');
    const body = document.getElementById('summaryBody');
    const title = modal.querySelector('h2');

    title.innerHTML = `<span>🔒</span> Unlock Book`;
    body.innerHTML = `
      <div class="purchase-modal">
        <p>You need to purchase <strong>${book.title}</strong> to read it.</p>
        <div class="purchase-price">$${book.price.toFixed(2)}</div>
        <button onclick="app.buyBook('${book.id}')" style="font-size:1.2rem; padding: 15px 40px;">
          Purchase Now
        </button>
        <p style="margin-top:20px; font-size:0.8rem; color:var(--text-muted)">
          (This is a demo. No real money will be charged.)
        </p>
      </div>
    `;
    modal.classList.remove('hidden');
  },

  buyBook: (bookId) => {
    const book = app.state.books.find(b => b.id === bookId);
    if (book) {
      app.closeModal('summaryModal');
      app.showPaymentModal(book);
    }
  },

  togglePriceInput: (show) => {
    const container = document.getElementById('priceInputContainer');
    if (show) {
      container.classList.remove('hidden');
      document.getElementById('up_price').focus();
    } else {
      container.classList.add('hidden');
      document.getElementById('up_price').value = '';
    }
  },

  uploadBook: async () => {
    const title = document.getElementById('up_title').value;
    const author = document.getElementById('up_author').value;

    const isPaid = document.querySelector('input[name="pricingType"][value="paid"]').checked;
    let price = 0;
    if (isPaid) {
      price = parseFloat(document.getElementById('up_price').value);
      if (isNaN(price) || price <= 0) {
        alert('Please enter a valid price for a paid book.');
        return;
      }
    }

    const desc = document.getElementById('up_desc').value;
    const fileInput = document.getElementById('up_file');
    const file = fileInput.files[0];

    if (!title || !author || !file) {
      alert('Please fill in all fields and select a PDF file.');
      return;
    }

    try {
      const createRes = await fetch('/api/books', {
        method: 'POST',
        headers: { ...app.getHeaders(), 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, author, description: desc, price: price })
      });
      const bookData = await createRes.json();
      if (!createRes.ok) throw new Error(bookData.error);

      const fd = new FormData();
      fd.append('file', file);
      const upRes = await fetch('/api/upload', {
        method: 'POST',
        headers: app.getHeaders(),
        body: fd
      });
      const upData = await upRes.json();
      if (!upRes.ok) throw new Error(upData.error);

      const linkRes = await fetch(`/api/books/${bookData.id}`, {
        method: 'PUT',
        headers: { ...app.getHeaders(), 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename: upData.filename || upData.url })
      });

      if (linkRes.ok) {
        alert('Book added successfully!');
        app.navigate('library');
        app.refreshLibrary();
        document.getElementById('up_title').value = '';
        document.getElementById('up_author').value = '';
        document.getElementById('up_price').value = '';
        document.getElementById('up_desc').value = '';
        fileInput.value = '';
      }
    } catch (e) { alert('Error: ' + e.message); }
  },

  // PDF Reader with PDF.js
  openReader: async (book) => {
    console.log('Opening PDF reader for:', book.title);
    app.state.currentBook = book;
    document.getElementById('readerTitle').textContent = book.title;
    document.getElementById('readerView').classList.remove('hidden');

    const canvas = document.getElementById('pdfCanvas');
    const loadingIndicator = document.getElementById('loadingIndicator');
    loadingIndicator.classList.remove('hidden');

    try {
      const pdfUrl = book.filename ? `/pdf/${book.filename}` : book.url;
      console.log('Loading PDF from:', pdfUrl);

      const loadingTask = pdfjsLib.getDocument(pdfUrl);
      app.state.pdfDoc = await loadingTask.promise;
      app.state.totalPages = app.state.pdfDoc.numPages;
      app.state.currentPage = 1;

      console.log(`PDF loaded: ${app.state.totalPages} pages`);

      await app.renderPDFSpread(1);
      loadingIndicator.classList.add('hidden');

      app.updatePageIndicator();

      app.setupTouchGestures();

    } catch (error) {
      console.error('Error loading PDF:', error);
      loadingIndicator.innerHTML = `<div style="color:red;">Failed to load PDF: ${error.message}</div>`;
    }
  },

  renderPDFSpread: async (leftPageNum) => {
    if (app.state.rendering) return;
    app.state.rendering = true;

    const canvasLeft = document.getElementById('pdfCanvasLeft');
    const canvasRight = document.getElementById('pdfCanvasRight');
    const ctxLeft = canvasLeft.getContext('2d');
    const ctxRight = canvasRight.getContext('2d');

    try {
      // Render left page
      if (leftPageNum <= app.state.totalPages) {
        const leftPage = await app.state.pdfDoc.getPage(leftPageNum);
        const leftViewport = leftPage.getViewport({ scale: app.state.scale });
        canvasLeft.width = leftViewport.width;
        canvasLeft.height = leftViewport.height;
        await leftPage.render({ canvasContext: ctxLeft, viewport: leftViewport }).promise;
        canvasLeft.style.display = 'block';
      } else {
        canvasLeft.style.display = 'none';
      }

      // Render right page
      const rightPageNum = leftPageNum + 1;
      if (rightPageNum <= app.state.totalPages) {
        const rightPage = await app.state.pdfDoc.getPage(rightPageNum);
        const rightViewport = rightPage.getViewport({ scale: app.state.scale });
        canvasRight.width = rightViewport.width;
        canvasRight.height = rightViewport.height;
        await rightPage.render({ canvasContext: ctxRight, viewport: rightViewport }).promise;
        canvasRight.style.display = 'block';
      } else {
        canvasRight.style.display = 'none';
      }

      app.state.currentPage = leftPageNum;
      app.updatePageIndicator();

    } catch (error) {
      console.error('Error rendering spread:', error);
    } finally {
      app.state.rendering = false;
    }
  },

  updatePageIndicator: () => {
    const leftPage = app.state.currentPage;
    const rightPage = Math.min(leftPage + 1, app.state.totalPages);
    const indicator = leftPage === rightPage
      ? `Page ${leftPage} of ${app.state.totalPages}`
      : `Pages ${leftPage}-${rightPage} of ${app.state.totalPages}`;
    document.getElementById('pageIndicator').textContent = indicator;
    document.getElementById('prevPageBtn').disabled = leftPage <= 1;
    document.getElementById('nextPageBtn').disabled = rightPage >= app.state.totalPages;
  },

  nextSpread: async () => {
    const nextPage = app.state.currentPage + 2;
    if (nextPage > app.state.totalPages) return;

    const canvasLeft = document.getElementById('pdfCanvasLeft');
    canvasLeft.classList.add('flipping-left');

    setTimeout(async () => {
      await app.renderPDFSpread(nextPage);
      canvasLeft.classList.remove('flipping-left');
    }, 400);
  },

  prevSpread: async () => {
    const prevPage = Math.max(1, app.state.currentPage - 2);
    if (prevPage === app.state.currentPage) return;

    const canvasRight = document.getElementById('pdfCanvasRight');
    canvasRight.classList.add('flipping-right');

    setTimeout(async () => {
      await app.renderPDFSpread(prevPage);
      canvasRight.classList.remove('flipping-right');
    }, 400);
  },

  zoomIn: async () => {
    app.state.scale = Math.min(app.state.scale + 0.25, 3.0);
    await app.renderPDFSpread(app.state.currentPage);
    document.getElementById('zoomLevel').textContent = Math.round(app.state.scale * 100) + '%';
  },

  zoomOut: async () => {
    app.state.scale = Math.max(app.state.scale - 0.25, 0.5);
    await app.renderPDFSpread(app.state.currentPage);
    document.getElementById('zoomLevel').textContent = Math.round(app.state.scale * 100) + '%';
  },

  resetZoom: async () => {
    app.state.scale = 1.5;
    await app.renderPDFSpread(app.state.currentPage);
    document.getElementById('zoomLevel').textContent = '100%';
  },

  setupTouchGestures: () => {
    const leftZone = document.getElementById('touchLeft');
    const rightZone = document.getElementById('touchRight');

    leftZone.onclick = () => app.prevSpread();
    rightZone.onclick = () => app.nextSpread();

    document.addEventListener('keydown', (e) => {
      if (!document.getElementById('readerView').classList.contains('hidden')) {
        if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
          app.prevSpread();
        } else if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === ' ') {
          e.preventDefault();
          app.nextSpread();
        }
      }
    });
  },

  closeReader: () => {
    document.getElementById('readerView').classList.add('hidden');
    app.state.currentBook = null;
    app.state.pdfDoc = null;
  },

  toggleSettings: () => {
    const menu = document.getElementById('readerSettings');
    menu.classList.toggle('show');
  },

  setTheme: (theme) => {
    app.state.theme = theme;
    localStorage.setItem('celib_theme', theme);
    document.body.className = `theme-${theme}`;

    document.querySelectorAll('.theme-circle').forEach(el => {
      el.classList.remove('active');
      if (el.getAttribute('onclick').includes(theme)) el.classList.add('active');
    });
  },

  adjustFont: (delta) => {
    app.state.fontSize = Math.max(50, Math.min(200, app.state.fontSize + (delta * 10)));
    document.getElementById('fontSizeDisplay').textContent = `${app.state.fontSize}%`;
  },

  showSummary: async () => {
    if (!app.state.currentBook) return;
    const modal = document.getElementById('summaryModal');
    const body = document.getElementById('summaryBody');
    const title = modal.querySelector('h2');

    title.innerHTML = `<span>✨</span> AI Insights`;
    modal.classList.remove('hidden');
    body.innerHTML = 'Analyzing book content with AI... <br><small>This may take a few seconds.</small>';

    try {
      const res = await fetch('/api/ai/summarize', {
        method: 'POST',
        headers: { ...app.getHeaders(), 'Content-Type': 'application/json' },
        body: JSON.stringify({ bookId: app.state.currentBook.id })
      });
      const data = await res.json();

      if (res.ok) {
        let html = `
          <div style="margin-bottom:15px"><strong>Summary:</strong><br>${data.summary}</div>
          <div style="margin-bottom:15px"><strong>Reading Time:</strong> ${data.reading_minutes} mins</div>
        `;
        if (data.categories && data.categories.length) {
          html += `<div style="margin-bottom:15px"><strong>Categories:</strong><br>${data.categories.map(c => `<span class="badge">${c}</span>`).join(' ')}</div>`;
        }
        if (data.keywords && data.keywords.length) {
          html += `<div style="margin-bottom:15px"><strong>Keywords:</strong><br>${data.keywords.map(k => `<span class="badge">${k}</span>`).join(' ')}</div>`;
        }
        if (data.characters && data.characters.length) {
          html += `<div style="margin-bottom:15px"><strong>Characters:</strong><br>${data.characters.join(', ')}</div>`;
        }
        if (data.source === 'local-fallback') {
          html += `<div style="margin-top:20px; font-size:0.8rem; color:#666;">* Generated using local analysis (Gemini key not found)</div>`;
        }
        body.innerHTML = html;

        // Refresh library to show updated categories
        await app.refreshLibrary();
      } else {
        body.textContent = 'Error: ' + (data.error || 'Failed to summarize');
      }
    } catch (e) {
      body.textContent = 'Error: ' + e.message;
    }
  },

  closeModal: (id) => {
    document.getElementById(id).classList.add('hidden');
  },

  // Admin Dashboard Functions
  loadAdminDashboard: async () => {
    try {
      // Load analytics
      const analyticsRes = await fetch('/api/admin/analytics', {
        headers: app.getHeaders()
      });
      const analytics = await analyticsRes.json();

      document.getElementById('statCustomers').textContent = analytics.totalCustomers;
      document.getElementById('statRevenue').textContent = `₹${analytics.totalRevenue.toFixed(2)}`;
      document.getElementById('statTransactions').textContent = analytics.totalTransactions;
      const successRate = analytics.totalTransactions > 0
        ? (analytics.successfulPayments / analytics.totalTransactions * 100).toFixed(1)
        : 0;
      document.getElementById('statSuccessRate').textContent = `${successRate}%`;

      // Load customers
      const customersRes = await fetch('/api/admin/customers', {
        headers: app.getHeaders()
      });
      const customers = await customersRes.json();

      const tbody = document.getElementById('customersTableBody');
      tbody.innerHTML = customers.map(c => `
        <tr>
          <td>${c.name}</td>
          <td>${c.email}</td>
          <td>${c.purchaseCount}</td>
          <td>₹${c.totalSpent.toFixed(2)}</td>
          <td>
            <button class="secondary" onclick="app.deleteCustomer('${c.id}')" style="padding:8px 16px;">Delete</button>
          </td>
        </tr>
      `).join('');

      // Load payments
      const paymentsRes = await fetch('/api/admin/payments', {
        headers: app.getHeaders()
      });
      const payments = await paymentsRes.json();

      const paymentsBody = document.getElementById('paymentsTableBody');
      paymentsBody.innerHTML = payments.slice(0, 10).map(p => `
        <tr>
          <td>${new Date(p.createdAt).toLocaleDateString()}</td>
          <td>${p.userId.substring(0, 8)}...</td>
          <td>₹${p.amount.toFixed(2)}</td>
          <td>${p.method.toUpperCase()}</td>
          <td><span class="badge">${p.status}</span></td>
        </tr>
      `).join('');

    } catch (e) {
      console.error('Error loading admin dashboard:', e);
      alert('Error loading admin dashboard. Make sure you are logged in as admin.');
    }
  },

  deleteCustomer: async (customerId) => {
    if (!confirm('Are you sure you want to delete this customer?')) return;

    try {
      const res = await fetch(`/api/admin/customer/${customerId}`, {
        method: 'DELETE',
        headers: app.getHeaders()
      });

      if (res.ok) {
        alert('Customer deleted successfully');
        app.loadAdminDashboard();
      } else {
        const data = await res.json();
        alert('Error: ' + (data.error || 'Failed to delete customer'));
      }
    } catch (e) {
      alert('Error deleting customer: ' + e.message);
    }
  },

  // Payment Functions
  showPaymentModal: (book) => {
    app.state.currentPaymentBook = book;
    document.getElementById('paymentBookInfo').innerHTML = `
      <h3>${book.title}</h3>
      <p>by ${book.author}</p>
      <p style="font-size:1.5rem; color:var(--accent); margin-top:10px;">₹${book.price.toFixed(2)}</p>
    `;
    document.getElementById('cardForm').classList.add('hidden');
    document.getElementById('upiForm').classList.add('hidden');
    document.getElementById('paymentModal').classList.remove('hidden');
  },

  selectPaymentMethod: (method) => {
    document.getElementById('cardForm').classList.add('hidden');
    document.getElementById('upiForm').classList.add('hidden');

    if (method === 'card') {
      document.getElementById('cardForm').classList.remove('hidden');
    } else {
      document.getElementById('upiForm').classList.remove('hidden');
    }
  },

  processPayment: async (method) => {
    const book = app.state.currentPaymentBook;

    try {
      // Initiate payment
      const initRes = await fetch('/api/payment/initiate', {
        method: 'POST',
        headers: { ...app.getHeaders(), 'Content-Type': 'application/json' },
        body: JSON.stringify({ bookId: book.id, method })
      });

      if (!initRes.ok) {
        throw new Error('Failed to initiate payment');
      }

      const { paymentId } = await initRes.json();

      // Verify payment (demo mode - auto success)
      const verifyRes = await fetch('/api/payment/verify', {
        method: 'POST',
        headers: { ...app.getHeaders(), 'Content-Type': 'application/json' },
        body: JSON.stringify({ paymentId })
      });

      const result = await verifyRes.json();

      if (result.status === 'success') {
        alert('✅ Payment successful! Book unlocked.');
        app.closeModal('paymentModal');
        app.state.purchasedBooks.push(book.id);
        localStorage.setItem('celib_purchased', JSON.stringify(app.state.purchasedBooks));
        app.refreshLibrary();
        setTimeout(() => app.openReader(book), 300);
      } else {
        throw new Error('Payment verification failed');
      }
    } catch (e) {
      alert('❌ Payment failed: ' + e.message);
    }
  }
};

document.addEventListener('DOMContentLoaded', app.init);
