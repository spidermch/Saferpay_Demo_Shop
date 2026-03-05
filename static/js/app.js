/* ============================================================
   Saferpay Explorer - Full SMB Merchant Demo
   ============================================================ */

// ---- State ----
var state = {
    shopView: 'catalog',
    cart: [],
    apiLogs: [],
    currentToken: null,
    currentTransactionId: null,
    currentOrderId: null,
    paymentResult: null,
    paymentFlow: 'paymentpage',
    selectedCustomerId: '',
    configured: false,
    checkoutDetails: { name: '', email: '', address: '', city: '', zip: '', country: '', phone: '' },
    paymentWindow: null,
    products: [],
    customers: [],
    icons: [],
    selectedIcon: '\uD83C\uDF81',
    customerDetailId: null,
};

// ---- Helpers ----
function fmt(minor, cur) { return (cur || 'CHF') + ' ' + (minor / 100).toFixed(2); }
function fmtTime(iso) { return new Date(iso).toLocaleTimeString('en-GB', {hour:'2-digit',minute:'2-digit',second:'2-digit'}); }
function esc(s) { var d = document.createElement('div'); d.textContent = s; return d.innerHTML; }
function $(id) { return document.getElementById(id); }

function syntaxHL(json) {
    if (typeof json !== 'string') json = JSON.stringify(json, null, 2);
    json = esc(json);
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function(m) {
        var c = 'json-number';
        if (/^"/.test(m)) { c = /:$/.test(m) ? 'json-key' : 'json-string'; }
        else if (/true|false/.test(m)) c = 'json-boolean';
        else if (/null/.test(m)) c = 'json-null';
        return '<span class="' + c + '">' + m + '</span>';
    });
}

function cartTotal() { return state.cart.reduce(function(s, i) { return s + i.price; }, 0); }

async function api(url, opts) {
    var r = await fetch(url, opts);
    return { ok: r.ok, status: r.status, data: await r.json() };
}

// ---- Tab Switching ----
function switchTab(name) {
    document.querySelectorAll('.tab-btn').forEach(function(b) { b.classList.toggle('active', b.dataset.tab === name); });
    document.querySelectorAll('.tab-content').forEach(function(e) { e.classList.toggle('active', e.id === 'tab-' + name); });
    if (name === 'products') loadProducts();
    if (name === 'orders') refreshOrders();
    if (name === 'customers') loadCustomers();
    if (name === 'code' && !codeState.currentFile) loadCode('app.py');
}
document.querySelectorAll('.tab-btn').forEach(function(b) { b.addEventListener('click', function() { switchTab(this.dataset.tab); }); });

// ================ SHOPPER VIEW ================
function renderShopper() {
    var el = $('shopper-content');
    switch(state.shopView) {
        case 'catalog': el.innerHTML = renderCatalog(); break;
        case 'cart': el.innerHTML = renderCart(); break;
        case 'customer_details': el.innerHTML = renderCustomerDetails(); break;
        case 'processing': el.innerHTML = renderProcessing(); break;
        case 'result': el.innerHTML = renderResult(); break;
    }
}

function flowIndicator() {
    var steps = ['Browse','Cart','Details','Initialize','Payment Page','Assert/Authorize','Capture'];
    var ci = 0, fail = false;
    if (state.shopView === 'cart') ci = 1;
    else if (state.shopView === 'customer_details') ci = 2;
    else if (state.shopView === 'processing') ci = 4;
    else if (state.shopView === 'result') {
        if (state.paymentResult && state.paymentResult.success) ci = state.paymentResult.captured ? 6 : 5;
        else { ci = 4; fail = true; }
    }
    var h = '<div class="flow-indicator">';
    for (var i = 0; i < steps.length; i++) {
        var cls = fail && i >= ci ? (i === ci ? 'fail' : '') : (i < ci ? 'done' : (i === ci ? 'active' : ''));
        h += '<div class="flow-step ' + cls + '"><span class="flow-dot"></span> ' + steps[i] + '</div>';
        if (i < steps.length - 1) h += '<div class="flow-line"></div>';
    }
    return h + '</div>';
}

function renderCatalog() {
    var prods = state.products.filter(function(p) { return p.active; });
    var cc = state.cart.length;
    var h = flowIndicator();
    h += '<div class="shop-nav"><h3>Shop</h3>';
    if (cc > 0) h += '<button class="cart-toggle" onclick="showCart()">Cart <span class="cart-badge">' + cc + '</span></button>';
    h += '</div><div class="product-grid">';
    if (prods.length === 0) h += '<p class="text-muted">No active products. Go to the Products tab to add some.</p>';
    prods.forEach(function(p) {
        h += '<div class="product-card"><div class="product-icon">' + p.icon + '</div>';
        h += '<div class="product-name">' + esc(p.name) + '</div>';
        h += '<div class="product-desc">' + esc(p.description || '') + '</div>';
        h += '<div class="product-price">' + fmt(p.price, p.currency) + '</div>';
        h += '<button class="btn btn-primary" onclick="addToCart(\'' + p.id + '\')">Add to Cart</button></div>';
    });
    return h + '</div>';
}

function renderCart() {
    if (!state.cart.length) { state.shopView = 'catalog'; renderShopper(); return ''; }
    var total = cartTotal();
    var h = flowIndicator();
    h += '<div class="shop-nav"><h3>Your Cart</h3><button class="cart-toggle" onclick="showCatalog()">Continue Shopping</button></div>';
    h += '<div class="cart-container"><div class="cart-items">';
    state.cart.forEach(function(item, idx) {
        h += '<div class="cart-item"><span class="cart-item-icon">' + item.icon + '</span>';
        h += '<div class="cart-item-info"><div class="cart-item-name">' + esc(item.name) + '</div>';
        h += '<div class="cart-item-price">' + fmt(item.price, item.currency) + '</div></div>';
        h += '<button class="cart-item-remove" onclick="removeFromCart(' + idx + ')">&times;</button></div>';
    });
    h += '</div>';
    // Checkout options
    h += '<div class="cart-footer">';
    h += '<div class="cart-total"><span>Total</span><span>' + fmt(total) + '</span></div>';
    h += '<div class="cart-actions"><button class="btn btn-secondary" onclick="showCatalog()">Back</button>';
    h += '<button class="btn btn-success" onclick="state.shopView=\'customer_details\';loadCustomers(true);renderShopper()">Proceed to Checkout</button></div></div></div>';
    return h;
}

function renderCustomerDetails() {
    var total = cartTotal();
    var cd = state.checkoutDetails;
    var h = flowIndicator();
    h += '<div class="shop-nav"><h3>Customer Details</h3><button class="cart-toggle" onclick="showCart()">Back to Cart</button></div>';
    h += '<div class="checkout-form-panel">';
    h += '<div class="checkout-section"><label>Full Name <span class="required">*</span></label><input type="text" id="cd-name" placeholder="John Doe" value="' + esc(cd.name || '') + '"></div>';
    h += '<div class="checkout-section"><label>Email Address <span class="required">*</span></label><input type="email" id="cd-email" placeholder="john@example.com" value="' + esc(cd.email || '') + '"></div>';
    h += '<div class="checkout-section"><label>Street Address <span class="required">*</span></label><input type="text" id="cd-address" placeholder="123 Main Street" value="' + esc(cd.address || '') + '"></div>';
    h += '<div style="display:flex;gap:.5rem">';
    h += '<div class="checkout-section" style="flex:1"><label>City <span class="required">*</span></label><input type="text" id="cd-city" placeholder="Zurich" value="' + esc(cd.city || '') + '"></div>';
    h += '<div class="checkout-section" style="flex:1"><label>Postal Code</label><input type="text" id="cd-zip" placeholder="8001" value="' + esc(cd.zip || '') + '"></div>';
    h += '</div>';
    h += '<div style="display:flex;gap:.5rem">';
    h += '<div class="checkout-section" style="flex:1"><label>Country</label><input type="text" id="cd-country" placeholder="Switzerland" value="' + esc(cd.country || '') + '"></div>';
    h += '<div class="checkout-section" style="flex:1"><label>Phone</label><input type="text" id="cd-phone" placeholder="+41 79 123 4567" value="' + esc(cd.phone || '') + '"></div>';
    h += '</div>';
    h += '<p style="font-size:.72rem;color:var(--text-muted);margin-top:.25rem">* Required fields</p>';
    h += '<div class="checkout-section" style="margin-top:.75rem"><label>Integration Method</label><select id="checkout-flow" onchange="state.paymentFlow=this.value">';
    h += '<option value="paymentpage"' + (state.paymentFlow === 'paymentpage' ? ' selected' : '') + '>Payment Page (full redirect)</option>';
    h += '<option value="transaction"' + (state.paymentFlow === 'transaction' ? ' selected' : '') + '>Transaction Interface (advanced)</option>';
    h += '</select><small>PaymentPage = simple all-in-one. Transaction = more control for the merchant.</small></div>';
    h += '<div style="margin-top:1rem"><button class="btn btn-success" onclick="proceedToPayment()" style="width:100%">Pay ' + fmt(total) + '</button></div>';
    h += '</div>';
    return h;
}

function proceedToPayment() {
    var name = ($('cd-name') || {}).value || '';
    var email = ($('cd-email') || {}).value || '';
    var address = ($('cd-address') || {}).value || '';
    var city = ($('cd-city') || {}).value || '';
    if (!name.trim() || !email.trim() || !address.trim() || !city.trim()) {
        alert('Please fill in all required fields (name, email, address, city).');
        return;
    }
    state.checkoutDetails = { name: name, email: email, address: address, city: city, zip: ($('cd-zip') || {}).value || '', country: ($('cd-country') || {}).value || '', phone: ($('cd-phone') || {}).value || '' };
    state.paymentFlow = ($('checkout-flow') || {}).value || state.paymentFlow;
    checkout();
}

function renderProcessing() {
    var h = flowIndicator();
    h += '<div class="processing-view"><div class="processing-spinner"></div><h3>Payment in Progress</h3>';
    h += '<p>Complete the payment in the Saferpay window.</p>';
    h += '<p class="mt-1 text-muted" style="font-size:.78rem">Popup blocked? <a href="#" id="payment-link" target="_blank" style="color:var(--primary)">Click here</a></p></div>';
    return h;
}

function renderResult() {
    var r = state.paymentResult; if (!r) return '';
    var h = flowIndicator() + '<div class="result-view">';
    if (r.success) {
        h += '<div class="result-icon success">&#10003;</div><h3>Payment Successful!</h3>';
        h += '<p>Transaction ' + (r.captured ? 'captured' : 'authorized') + ' via ' + esc(r.flow || '') + '.</p>';
        h += '<div class="result-details">';
        h += '<div class="result-detail-row"><span>Order</span><span>' + esc(r.orderId || '-') + '</span></div>';
        h += '<div class="result-detail-row"><span>Transaction</span><span>' + esc(r.transactionId || '-') + '</span></div>';
        h += '<div class="result-detail-row"><span>Amount</span><span>' + fmt(r.amount, r.currency) + '</span></div>';
        if (r.paymentMeans) {
            var brand = r.paymentMeans.Brand ? r.paymentMeans.Brand.Name : '';
            var masked = r.paymentMeans.DisplayText || '';
            h += '<div class="result-detail-row"><span>Card</span><span>' + esc(brand + ' ' + masked) + '</span></div>';
        }
        h += '<div class="result-detail-row"><span>Status</span><span class="status-badge ' + (r.captured ? 'status-captured' : 'status-authorized') + '">' + (r.captured ? 'Captured' : 'Authorized') + '</span></div>';
        h += '</div>';
        if (!r.captured) {
            h += '<button class="btn btn-success mb-1" onclick="capturePayment()">Capture Payment</button>';
            h += '<div class="text-muted" style="font-size:.72rem;max-width:280px">Capture triggers the actual money transfer.</div>';
        }
        h += '<button class="btn btn-secondary mt-2" onclick="newOrder()">New Order</button>';
    } else {
        h += '<div class="result-icon fail">&#10007;</div><h3>Payment Failed</h3>';
        h += '<p>' + esc(r.message || 'The payment was cancelled or an error occurred.') + '</p>';
        h += '<button class="btn btn-primary mt-2" onclick="newOrder()">Try Again</button>';
    }
    return h + '</div>';
}

// ---- Shop Actions ----
function addToCart(pid) {
    var p = state.products.find(function(x) { return x.id === pid; });
    if (p) { state.cart.push(Object.assign({}, p)); renderShopper(); }
}
function removeFromCart(i) { state.cart.splice(i, 1); if (!state.cart.length) state.shopView = 'catalog'; renderShopper(); }
function showCart() { state.shopView = 'cart'; loadCustomers(true); renderShopper(); }
function showCatalog() { state.shopView = 'catalog'; renderShopper(); }
function newOrder() { state.shopView = 'catalog'; state.cart = []; state.currentToken = null; state.currentTransactionId = null; state.paymentResult = null; state.checkoutDetails = {name:'',email:'',address:'',city:'',zip:'',country:'',phone:''}; renderShopper(); }

// ---- Payment Flow ----
async function checkout() {
    if (!state.configured) { switchTab('config'); return; }
    if (!state.cart.length) return;
    var total = cartTotal();
    var desc = state.cart.map(function(i) { return i.name; }).join(', ');
    var items = state.cart.map(function(i) { return {name: i.name, price: i.price}; });

    state.shopView = 'processing';
    renderShopper();

    var cd = state.checkoutDetails;
    var body = { amount: total, currency: 'CHF', description: desc, items: items, customer_id: state.selectedCustomerId || null };
    var url, flow;

    // Add payer info from checkout details
    var parts = (cd.name || '').split(' ');
    body.payer = { LanguageCode: 'en', BillingAddress: { FirstName: parts[0] || '', LastName: parts.slice(1).join(' ') || '' } };
    if (cd.email) body.payer.BillingAddress.Email = cd.email;
    if (cd.address) body.payer.BillingAddress.Street = cd.address;
    if (cd.city) body.payer.BillingAddress.City = cd.city;
    if (cd.zip) body.payer.BillingAddress.Zip = cd.zip;
    if (cd.country) body.payer.BillingAddress.CountryCode = cd.country;

    if (state.paymentFlow === 'transaction') {
        url = '/api/transaction/initialize';
        flow = 'Transaction';
    } else {
        url = '/api/initialize';
        flow = 'PaymentPage';
    }

    try {
        var r = await api(url, { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(body) });
        if (r.data.log) addApiLog(r.data.log);
        if (r.data.success) {
            state.currentToken = r.data.token;
            state.currentOrderId = r.data.order_id;
            addApiLog({ id: 'redirect-' + Date.now(), timestamp: new Date().toISOString(), step: 'Redirect',
                endpoint: r.data.redirect_url, method: 'GET', request: null, response: null, status_code: 302,
                explanation: 'The customer is redirected to the Saferpay-hosted payment page to securely enter card details. Card data stays on Saferpay\'s PCI-certified servers.' });
            var w = 520, h = 700, l = (screen.width - w) / 2, t = (screen.height - h) / 2;
            state.paymentWindow = window.open(r.data.redirect_url, 'SaferpayPayment', 'width='+w+',height='+h+',left='+l+',top='+t+',scrollbars=yes');
            var link = $('payment-link'); if (link) link.href = r.data.redirect_url;
        } else {
            state.paymentResult = { success: false, message: typeof r.data.error === 'string' ? r.data.error : (r.data.error && r.data.error.ErrorMessage) || 'API error' };
            state.shopView = 'result'; renderShopper();
        }
    } catch(e) {
        state.paymentResult = { success: false, message: 'Network error: ' + e.message };
        state.shopView = 'result'; renderShopper();
    }
}

async function doAssertOrAuthorize() {
    if (!state.currentToken) return;
    var isTxn = state.paymentFlow === 'transaction';
    var url = isTxn ? '/api/transaction/authorize' : '/api/assert';
    try {
        var r = await api(url, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({token:state.currentToken}) });
        if (r.data.log) addApiLog(r.data.log);
        if (r.data.success) {
            state.currentTransactionId = r.data.transaction_id;
            state.paymentResult = { success: true, captured: false, orderId: state.currentOrderId, transactionId: r.data.transaction_id,
                amount: cartTotal(), currency: 'CHF', paymentMeans: (r.data.data && r.data.data.PaymentMeans) || null, flow: isTxn ? 'Transaction' : 'PaymentPage' };
        } else {
            state.paymentResult = { success: false, message: (r.data.error && r.data.error.ErrorMessage) || 'Assert/Authorize failed' };
        }
    } catch(e) { state.paymentResult = { success: false, message: 'Network error: ' + e.message }; }
    state.shopView = 'result'; renderShopper();
}

async function capturePayment() {
    if (!state.currentTransactionId) return;
    try {
        var r = await api('/api/capture', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({transaction_id:state.currentTransactionId, token:state.currentToken}) });
        if (r.data.log) addApiLog(r.data.log);
        if (r.data.success && state.paymentResult) state.paymentResult.captured = true;
    } catch(e) {}
    renderShopper();
}

// ---- Payment Return Handler ----
window.addEventListener('message', function(ev) {
    if (!ev.data || ev.data.type !== 'saferpay_return') return;
    if (ev.data.status === 'success' || ev.data.status === 'transaction_return') {
        doAssertOrAuthorize();
    } else {
        state.paymentResult = { success: false, message: 'Payment was cancelled by the customer.' };
        state.shopView = 'result'; renderShopper();
        addApiLog({ id:'abort-'+Date.now(), timestamp:new Date().toISOString(), step:'Abort', endpoint:'/return/fail', method:'GET', request:null, response:{status:'Customer cancelled'}, status_code:null,
            explanation:'The customer clicked Cancel on the payment page. No charge occurs.' });
    }
});

setInterval(function() {
    if (state.shopView === 'processing' && state.paymentWindow) {
        try { if (state.paymentWindow.closed) { state.paymentWindow = null; setTimeout(function() { if (state.shopView === 'processing') doAssertOrAuthorize(); }, 1500); } } catch(e) {}
    }
}, 1000);

// ================ DEVELOPER VIEW ================
function addApiLog(entry) { state.apiLogs.push(entry); renderDevPanel(); var p = $('developer-content'); if (p) p.scrollTop = p.scrollHeight; }

function renderDevPanel() {
    var el = $('developer-content');
    if (!state.apiLogs.length) { el.innerHTML = '<div class="dev-empty-state"><div class="dev-empty-icon">&lt;/&gt;</div><p>API calls appear here as payments flow.</p><p class="dev-hint">Add items, checkout, and watch the magic.</p></div>'; return; }
    var h = '';
    state.apiLogs.forEach(function(log, idx) {
        var step = (log.step || '').toLowerCase();
        var badge = step.indexOf('pp') === 0 ? 'pp' : step.indexOf('txn') === 0 ? 'txn' : step === 'redirect' ? 'redirect' : step === 'capture' ? 'capture' : 'error';
        var sOk = (log.status_code === 200 || log.status_code === 302) ? 's-ok' : 's-err';
        var open = idx === state.apiLogs.length - 1 ? ' open' : '';
        h += '<div class="api-entry' + open + '" id="api-entry-' + idx + '"><div class="api-entry-header" onclick="toggleEntry(' + idx + ')">';
        h += '<span class="api-step-badge badge-' + badge + '">' + esc(log.step) + '</span>';
        h += '<span class="api-entry-method">' + esc(log.method) + '</span>';
        h += '<span class="api-entry-endpoint">' + esc(log.endpoint) + '</span>';
        if (log.status_code) h += '<span class="api-entry-status ' + sOk + '">' + log.status_code + '</span>';
        h += '<span class="api-entry-time">' + fmtTime(log.timestamp) + '</span><span class="api-entry-toggle">&#9654;</span></div>';
        h += '<div class="api-entry-body">';
        if (log.explanation) h += '<div class="api-explanation">' + esc(log.explanation) + '</div>';
        if (log.request) h += '<div class="api-section"><div class="api-section-label">Request</div><div class="api-json">' + syntaxHL(log.request) + '</div></div>';
        if (log.response) h += '<div class="api-section"><div class="api-section-label">Response</div><div class="api-json">' + syntaxHL(log.response) + '</div></div>';
        h += '</div></div>';
    });
    el.innerHTML = h;
}
function toggleEntry(i) { var e = $('api-entry-' + i); if (e) e.classList.toggle('open'); }
function clearLogs() { state.apiLogs = []; renderDevPanel(); fetch('/api/logs/clear', {method:'POST'}); }

// ================ PRODUCTS VIEW ================
async function loadProducts(silent) {
    try {
        var r = await api('/api/products');
        state.products = r.data;
        if (!silent) renderProductsGrid();
        renderShopper();
    } catch(e) {}
}

function renderProductsGrid() {
    var el = $('products-grid'); if (!el) return;
    if (!state.products.length) { el.innerHTML = '<p class="text-muted">No products yet. Add your first product!</p>'; return; }
    var h = '';
    state.products.forEach(function(p) {
        h += '<div class="product-card' + (p.active ? '' : ' inactive') + '">';
        h += '<div class="product-actions">';
        h += '<button onclick="editProduct(\'' + p.id + '\')" title="Edit">&#9998;</button>';
        h += '<button onclick="toggleProduct(\'' + p.id + '\',' + !p.active + ')" title="' + (p.active ? 'Deactivate' : 'Activate') + '">' + (p.active ? '&#10005;' : '&#10003;') + '</button>';
        h += '<button onclick="deleteProduct(\'' + p.id + '\')" title="Delete">&#128465;</button></div>';
        h += '<div class="product-icon">' + p.icon + '</div>';
        h += '<div class="product-name">' + esc(p.name) + '</div>';
        h += '<div class="product-desc">' + esc(p.description || '') + '</div>';
        h += '<div class="product-price">' + fmt(p.price, p.currency) + '</div>';
        if (!p.active) h += '<div class="status-badge status-failed" style="margin-top:.4rem">Inactive</div>';
        h += '</div>';
    });
    el.innerHTML = h;
}

function renderIconPicker(selected) {
    var el = $('icon-picker'); if (!el) return;
    var icons = state.icons.length ? state.icons : ['\u231A','\uD83C\uDF6B','\uD83D\uDD27','\uD83E\uDED5','\uD83D\uDC55','\uD83D\uDC5F','\uD83D\uDCF1','\uD83D\uDCBB','\uD83C\uDFAE','\uD83D\uDCDA','\uD83C\uDFA7','\u2615','\uD83C\uDF77','\uD83D\uDC8D','\uD83C\uDF81','\uD83E\uDE91','\uD83D\uDDBC','\uD83E\uDDF8','\uD83C\uDF92','\uD83D\uDC60'];
    var h = '';
    icons.forEach(function(ic) {
        h += '<div class="icon-option' + (ic === selected ? ' selected' : '') + '" onclick="pickIcon(this,\'' + ic.replace(/'/g,"\\'") + '\')">' + ic + '</div>';
    });
    el.innerHTML = h;
}

function pickIcon(el, ic) {
    state.selectedIcon = ic;
    document.querySelectorAll('.icon-option').forEach(function(e) { e.classList.remove('selected'); });
    el.classList.add('selected');
}

function showAddProduct() {
    $('product-form-card').classList.remove('hidden');
    $('product-form-title').textContent = 'Add Product';
    $('pf-submit-btn').textContent = 'Add Product';
    $('pf-id').value = '';
    $('pf-name').value = '';
    $('pf-price').value = '';
    $('pf-desc').value = '';
    state.selectedIcon = '\uD83C\uDF81';
    renderIconPicker(state.selectedIcon);
}

function editProduct(pid) {
    var p = state.products.find(function(x) { return x.id === pid; });
    if (!p) return;
    $('product-form-card').classList.remove('hidden');
    $('product-form-title').textContent = 'Edit Product';
    $('pf-submit-btn').textContent = 'Save Changes';
    $('pf-id').value = p.id;
    $('pf-name').value = p.name;
    $('pf-price').value = (p.price / 100).toFixed(2);
    $('pf-desc').value = p.description || '';
    state.selectedIcon = p.icon;
    renderIconPicker(p.icon);
}

function hideProductForm() { $('product-form-card').classList.add('hidden'); }

async function saveProduct(ev) {
    ev.preventDefault();
    var pid = $('pf-id').value;
    var body = {
        name: $('pf-name').value,
        description: $('pf-desc').value,
        price: $('pf-price').value,
        icon: state.selectedIcon,
        currency: 'CHF'
    };
    if (pid) {
        await api('/api/products/' + pid, { method:'PUT', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body) });
    } else {
        await api('/api/products', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body) });
    }
    hideProductForm();
    await loadProducts();
}

async function deleteProduct(pid) {
    if (!confirm('Delete this product?')) return;
    await api('/api/products/' + pid, { method:'DELETE' });
    await loadProducts();
}

async function toggleProduct(pid, active) {
    await api('/api/products/' + pid, { method:'PUT', headers:{'Content-Type':'application/json'}, body: JSON.stringify({active:active}) });
    await loadProducts();
}

// ================ ORDERS VIEW ================
async function refreshOrders() {
    try {
        var r = await api('/api/transactions');
        renderOrderStats(r.data);
        renderOrderTable(r.data);
    } catch(e) {}
}

function renderOrderStats(txns) {
    var total = txns.length, rev = 0, auth = 0, cap = 0;
    txns.forEach(function(t) { rev += t.amount || 0; if (t.status === 'AUTHORIZED') auth++; if (t.status === 'CAPTURED') cap++; });
    $('stat-total').textContent = total;
    $('stat-revenue').textContent = fmt(rev);
    $('stat-authorized').textContent = auth;
    $('stat-captured').textContent = cap;
}

function renderOrderTable(txns) {
    var tb = $('txn-table-body');
    if (!txns.length) { tb.innerHTML = '<tr class="empty-row"><td colspan="8">No transactions yet.</td></tr>'; return; }
    var h = '';
    txns.forEach(function(t) {
        var sc = 'status-' + (t.status || 'initialized').toLowerCase();
        var pm = '';
        if (t.payment_means) {
            var b = t.payment_means.Brand ? t.payment_means.Brand.Name : '';
            pm = b + ' ' + (t.payment_means.DisplayText || '');
        }
        var flowTag = t.payment_flow === 'Transaction' ? '<span class="flow-tag txn">TXN</span>' : '<span class="flow-tag pp">PP</span>';
        h += '<tr>';
        h += '<td><strong>' + esc(t.order_id || '-') + '</strong>';
        if (t.description) h += '<div class="order-desc-hint">' + esc(t.description) + '</div>';
        h += '</td>';
        h += '<td>' + esc(t.customer_name || 'Guest') + '</td>';
        h += '<td>' + fmt(t.amount || 0, t.currency) + '</td>';
        h += '<td><span class="status-badge ' + sc + '">' + esc(t.status || '?') + '</span></td>';
        h += '<td>' + flowTag + '</td>';
        h += '<td>' + esc(pm || '-') + '</td>';
        h += '<td>' + (t.created ? fmtTime(t.created) : '-') + '</td>';
        h += '<td style="white-space:nowrap">';
        if (t.status === 'AUTHORIZED' && t.transaction_id) h += '<button class="btn btn-sm btn-success" onclick="captureMerchant(\'' + esc(t.transaction_id) + '\',\'' + esc(t.token) + '\')">Capture</button> ';
        else if (t.status === 'CAPTURED') h += '<span class="text-muted">Settled</span> ';
        if (t.order_id) h += '<button class="btn btn-sm btn-secondary" onclick="showOrderJourney(\'' + esc(t.order_id) + '\')">Journey</button>';
        h += '</td></tr>';
    });
    tb.innerHTML = h;
}

async function captureMerchant(tid, token) {
    try {
        var r = await api('/api/capture', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({transaction_id:tid,token:token})});
        if (r.data.log) addApiLog(r.data.log);
        refreshOrders();
        if (state.paymentResult && state.currentTransactionId === tid) { state.paymentResult.captured = true; renderShopper(); }
    } catch(e) {}
}

// ================ ORDER JOURNEY ================
async function showOrderJourney(orderId) {
    var overlay = $('order-journey-overlay');
    overlay.classList.remove('hidden');
    overlay.innerHTML = '<div class="journey-panel"><div class="processing-view"><div class="processing-spinner"></div><p>Loading journey...</p></div></div>';
    try {
        var r = await api('/api/orders/' + encodeURIComponent(orderId) + '/journey');
        if (r.ok) renderJourneyPanel(r.data);
        else overlay.innerHTML = '<div class="journey-panel"><p class="text-muted" style="padding:2rem">Could not load journey.</p><button class="btn btn-secondary" onclick="closeJourney()">Close</button></div>';
    } catch(e) {
        overlay.innerHTML = '<div class="journey-panel"><p class="text-muted" style="padding:2rem">Error: ' + esc(e.message) + '</p><button class="btn btn-secondary" onclick="closeJourney()">Close</button></div>';
    }
}

function renderJourneyPanel(data) {
    var h = '<div class="journey-panel">';
    h += '<div class="journey-header"><h3>Order Journey: ' + esc(data.order_id) + '</h3>';
    h += '<button class="btn btn-sm btn-secondary" onclick="closeJourney()">Close</button></div>';
    h += '<div class="journey-summary">';
    h += '<span>Flow: <strong>' + esc(data.flow) + '</strong></span>';
    h += '<span>Amount: <strong>' + fmt(data.amount, data.currency) + '</strong></span>';
    h += '<span>Status: <span class="status-badge status-' + (data.status || 'initialized').toLowerCase() + '">' + esc(data.status) + '</span></span>';
    if (data.description) h += '<span>Description: <strong>' + esc(data.description) + '</strong></span>';
    h += '</div>';
    h += '<div class="journey-timeline">';
    data.steps.forEach(function(step, idx) {
        var completedClass = step.completed ? 'step-done' : 'step-pending';
        h += '<div class="journey-step ' + completedClass + '">';
        h += '<div class="journey-step-marker"><div class="journey-dot"></div>';
        if (idx < data.steps.length - 1) h += '<div class="journey-connector"></div>';
        h += '</div>';
        h += '<div class="journey-step-content">';
        h += '<div class="journey-step-header">';
        h += '<span class="journey-step-name">' + esc(step.step) + '</span>';
        h += '<span class="journey-actor-badge badge-' + step.actor + '">' + esc(step.actor) + '</span>';
        if (step.optional) h += '<span class="journey-optional">optional</span>';
        if (step.timestamp) h += '<span class="journey-step-time">' + fmtTime(step.timestamp) + '</span>';
        if (step.status_code) h += '<span class="api-entry-status ' + (step.status_code === 200 ? 's-ok' : 's-err') + '">' + step.status_code + '</span>';
        h += '</div>';
        h += '<div class="journey-step-desc">' + esc(step.description) + '</div>';
        if (step.code_ref) h += '<div class="journey-code-ref">Code: <code>' + esc(step.code_ref) + '</code></div>';
        if (step.log_id) {
            var log = data.logs.find(function(l) { return l.id === step.log_id; });
            if (log) {
                h += '<details class="journey-log-detail"><summary>View API Request / Response</summary>';
                if (log.request) h += '<div class="api-section"><div class="api-section-label">Request</div><div class="api-json">' + syntaxHL(log.request) + '</div></div>';
                if (log.response) h += '<div class="api-section"><div class="api-section-label">Response</div><div class="api-json">' + syntaxHL(log.response) + '</div></div>';
                h += '</details>';
            }
        }
        h += '</div></div>';
    });
    h += '</div></div>';
    $('order-journey-overlay').innerHTML = h;
}

function closeJourney() { $('order-journey-overlay').classList.add('hidden'); }

// ================ FEATURE AUDIT ================
async function showFeatureAudit() {
    var panel = $('feature-audit-panel'), mainView = $('orders-main-view');
    if (!panel.classList.contains('hidden')) { panel.classList.add('hidden'); mainView.classList.remove('hidden'); return; }
    mainView.classList.add('hidden');
    panel.classList.remove('hidden');
    $('feature-audit-content').innerHTML = '<div class="processing-view"><div class="processing-spinner"></div><p>Loading audit...</p></div>';
    try {
        var r = await api('/api/feature-audit');
        if (r.ok) renderFeatureAudit(r.data);
    } catch(e) { $('feature-audit-content').innerHTML = '<p class="text-muted" style="padding:2rem">Error loading audit.</p>'; }
}

function renderFeatureAudit(data) {
    var s = data.stats;
    var h = '<div class="audit-container">';
    h += '<div class="audit-score-card">';
    h += '<div class="audit-score-circle"><svg viewBox="0 0 36 36"><path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="var(--border)" stroke-width="3"/>';
    h += '<path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="var(--primary)" stroke-width="3" stroke-dasharray="' + s.coverage_pct + ', 100"/></svg>';
    h += '<span class="score-text">' + s.coverage_pct + '%</span></div>';
    h += '<div class="audit-score-info"><h3>Saferpay Feature Coverage</h3>';
    h += '<p>' + s.implemented + ' of ' + s.total + ' Saferpay API capabilities implemented in this demo</p></div></div>';
    data.categories.forEach(function(cat) {
        h += '<div class="audit-category card">';
        h += '<h4 class="audit-cat-title">' + esc(cat.name) + '</h4>';
        cat.features.forEach(function(f) {
            h += '<div class="audit-feature ' + (f.implemented ? 'implemented' : 'not-implemented') + '">';
            h += '<span class="audit-check">' + (f.implemented ? '&#10003;' : '&#9675;') + '</span>';
            h += '<div class="audit-feature-info"><strong>' + esc(f.name) + '</strong>';
            h += '<div class="audit-feature-desc">' + esc(f.description) + '</div>';
            if (f.endpoint) h += '<code class="audit-endpoint">' + esc(f.endpoint) + '</code>';
            h += '</div></div>';
        });
        h += '</div>';
    });
    h += '</div>';
    $('feature-audit-content').innerHTML = h;
}

function backToOrders() {
    $('feature-audit-panel').classList.add('hidden');
    $('orders-main-view').classList.remove('hidden');
}

// ================ CUSTOMERS VIEW ================
async function loadCustomers(silent) {
    try {
        var r = await api('/api/customers');
        state.customers = r.data;
        if (!silent) renderCustomerList();
    } catch(e) {}
}

function renderCustomerList() {
    var el = $('customers-grid'); if (!el) return;
    var q = ($('customer-search') || {}).value || '';
    q = q.toLowerCase();
    var filtered = state.customers.filter(function(c) {
        if (!q) return true;
        return (c.name + ' ' + c.email + ' ' + c.company).toLowerCase().indexOf(q) >= 0;
    });
    if (!filtered.length) {
        el.innerHTML = '<p class="text-muted">' + (q ? 'No customers match your search.' : 'No customers yet. Add your first customer!') + '</p>';
        return;
    }
    var h = '';
    filtered.forEach(function(c) {
        h += '<div class="customer-card" onclick="showCustomerDetail(\'' + c.id + '\')">';
        h += '<div class="customer-card-name">' + esc(c.name) + '</div>';
        h += '<div class="customer-card-company">' + esc(c.company || c.email || '') + '</div>';
        h += '<div class="customer-card-meta">';
        h += '<span><strong>' + (c.order_count || 0) + '</strong> orders</span>';
        h += '<span><strong>' + fmt(c.total_spent || 0) + '</strong> spent</span>';
        h += '</div></div>';
    });
    el.innerHTML = h;
}

function showAddCustomer() {
    $('customer-form-card').classList.remove('hidden');
    $('customer-form-title').textContent = 'Add Customer';
    $('cf-submit-btn').textContent = 'Add Customer';
    $('cf-id').value = '';
    $('cf-name').value = ''; $('cf-email').value = ''; $('cf-company').value = ''; $('cf-phone').value = ''; $('cf-address').value = '';
}

function editCustomer(cid) {
    var c = state.customers.find(function(x) { return x.id === cid; });
    if (!c) return;
    $('customer-form-card').classList.remove('hidden');
    $('customer-form-title').textContent = 'Edit Customer';
    $('cf-submit-btn').textContent = 'Save Changes';
    $('cf-id').value = c.id;
    $('cf-name').value = c.name; $('cf-email').value = c.email || ''; $('cf-company').value = c.company || ''; $('cf-phone').value = c.phone || ''; $('cf-address').value = c.address || '';
}

function hideCustomerForm() { $('customer-form-card').classList.add('hidden'); }

async function saveCustomer(ev) {
    ev.preventDefault();
    var cid = $('cf-id').value;
    var body = { name: $('cf-name').value, email: $('cf-email').value, company: $('cf-company').value, phone: $('cf-phone').value, address: $('cf-address').value };
    if (cid) {
        await api('/api/customers/' + cid, {method:'PUT', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)});
    } else {
        await api('/api/customers', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)});
    }
    hideCustomerForm();
    await loadCustomers();
    if (state.customerDetailId) showCustomerDetail(state.customerDetailId);
}

async function deleteCustomer(cid) {
    if (!confirm('Delete this customer?')) return;
    await api('/api/customers/' + cid, {method:'DELETE'});
    backToCustomerList();
    await loadCustomers();
}

function backToCustomerList() {
    state.customerDetailId = null;
    $('customer-list-view').classList.remove('hidden');
    $('customer-detail-view').classList.add('hidden');
    $('customer-form-card').classList.add('hidden');
    renderCustomerList();
}

async function showCustomerDetail(cid) {
    state.customerDetailId = cid;
    $('customer-list-view').classList.add('hidden');
    $('customer-detail-view').classList.remove('hidden');
    var c = state.customers.find(function(x) { return x.id === cid; });
    if (!c) { backToCustomerList(); return; }

    // Fetch orders for this customer
    var orders = [];
    try { var r = await api('/api/customers/' + cid + '/orders'); orders = r.data; } catch(e) {}

    var h = '<div class="customer-detail">';
    // Info card
    h += '<div class="customer-info-card"><h3>' + esc(c.name) + '&nbsp;';
    h += '<button class="btn btn-sm btn-secondary" onclick="editCustomer(\'' + cid + '\')">Edit</button>&nbsp;';
    h += '<button class="btn btn-sm btn-danger" onclick="deleteCustomer(\'' + cid + '\')">Delete</button></h3>';
    h += '<div class="info-row"><span>Email</span><span>' + esc(c.email || '-') + '</span></div>';
    h += '<div class="info-row"><span>Company</span><span>' + esc(c.company || '-') + '</span></div>';
    h += '<div class="info-row"><span>Phone</span><span>' + esc(c.phone || '-') + '</span></div>';
    h += '<div class="info-row"><span>Address</span><span>' + esc(c.address || '-') + '</span></div>';
    h += '<div class="info-row"><span>Orders</span><span>' + (c.order_count || 0) + '</span></div>';
    h += '<div class="info-row"><span>Lifetime Value</span><span><strong>' + fmt(c.total_spent || 0) + '</strong></span></div>';
    h += '</div>';

    // Notes card
    h += '<div class="customer-info-card"><h3>Notes</h3>';
    h += '<div class="notes-list">';
    if (c.notes && c.notes.length) {
        c.notes.slice().reverse().forEach(function(n) {
            h += '<div class="note-item">' + esc(n.text) + '<div class="note-time">' + fmtTime(n.created) + '</div></div>';
        });
    } else {
        h += '<p class="text-muted" style="font-size:.82rem">No notes yet.</p>';
    }
    h += '</div>';
    h += '<div class="note-input-row"><input type="text" id="note-input" placeholder="Add a note..." onkeydown="if(event.key===\'Enter\')addNote(\'' + cid + '\')"><button class="btn btn-sm btn-primary" onclick="addNote(\'' + cid + '\')">Add</button></div>';
    h += '</div>';

    // Orders
    h += '<div class="customer-info-card" style="grid-column:1/-1"><h3>Order History</h3>';
    if (orders.length) {
        h += '<table class="txn-table"><thead><tr><th>Order</th><th>Amount</th><th>Status</th><th>Flow</th><th>Time</th></tr></thead><tbody>';
        orders.forEach(function(o) {
            var sc = 'status-' + (o.status || 'initialized').toLowerCase();
            var ft = o.payment_flow === 'Transaction' ? '<span class="flow-tag txn">TXN</span>' : '<span class="flow-tag pp">PP</span>';
            h += '<tr><td>' + esc(o.order_id) + '</td><td>' + fmt(o.amount, o.currency) + '</td><td><span class="status-badge ' + sc + '">' + esc(o.status) + '</span></td><td>' + ft + '</td><td>' + fmtTime(o.created) + '</td></tr>';
        });
        h += '</tbody></table>';
    } else {
        h += '<p class="text-muted" style="font-size:.82rem">No orders for this customer yet.</p>';
    }
    h += '</div></div>';
    $('customer-detail-content').innerHTML = h;
}

async function addNote(cid) {
    var input = $('note-input');
    var text = input.value.trim();
    if (!text) return;
    input.value = '';
    await api('/api/customers/' + cid + '/notes', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({text:text})});
    await loadCustomers(true);
    showCustomerDetail(cid);
}

// ================ CONFIG ================
async function checkConfig() {
    try {
        var r = await api('/api/config/status');
        state.configured = r.data.configured;
        updateConfigUI(r.data);
        if (r.data.configured) {
            $('cfg-customer-id').value = r.data.customer_id || '';
            $('cfg-terminal-id').value = r.data.terminal_id || '';
            if (r.data.base_url) $('cfg-base-url').value = r.data.base_url;
            if (r.data.spec_version) $('cfg-spec-version').value = r.data.spec_version;
            if (r.data.order_id_prefix) $('cfg-order-prefix').value = r.data.order_id_prefix;
            if (r.data.order_id_pattern) $('cfg-order-pattern').value = r.data.order_id_pattern;
            if (r.data.default_description) $('cfg-order-desc').value = r.data.default_description;
            if (r.data.payer_note !== undefined) $('cfg-payer-note').value = r.data.payer_note;
        }
    } catch(e) { state.configured = false; }
}

function updateConfigUI(d) {
    var banner = $('config-banner'), badge = $('config-status-badge');
    if (d && d.configured) {
        banner.classList.add('hidden'); badge.className = 'header-status connected'; badge.textContent = 'Connected';
        document.querySelectorAll('.tab-content').forEach(function(e) { e.classList.remove('has-banner'); });
    } else {
        banner.classList.remove('hidden'); badge.className = 'header-status disconnected'; badge.textContent = 'Not configured';
        document.querySelectorAll('.tab-content').forEach(function(e) { e.classList.add('has-banner'); });
    }
}

async function saveConfig(ev) {
    ev.preventDefault();
    var msg = $('config-message'); msg.textContent = '';
    var body = { customer_id: $('cfg-customer-id').value, terminal_id: $('cfg-terminal-id').value, username: $('cfg-username').value, password: $('cfg-password').value, base_url: $('cfg-base-url').value, spec_version: $('cfg-spec-version').value, order_id_prefix: $('cfg-order-prefix').value, order_id_pattern: $('cfg-order-pattern').value, default_description: $('cfg-order-desc').value, payer_note: $('cfg-payer-note').value };
    try {
        var r = await api('/api/config', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)});
        if (r.ok) { state.configured = true; updateConfigUI({configured:true}); msg.className = 'form-message success'; msg.textContent = 'Saved!'; setTimeout(function(){switchTab('explorer');}, 600); }
        else { msg.className = 'form-message error'; msg.textContent = r.data.error || 'Failed'; }
    } catch(e) { msg.className = 'form-message error'; msg.textContent = 'Network error'; }
}

// ================ VERSION INFO ================
async function onVersionChange() {
    var selected = $('cfg-spec-version').value;
    var infoPanel = $('version-info-panel');
    try {
        var r = await api('/api/spec-versions');
        if (!r.ok) return;
        var versions = r.data.versions;
        var selIdx = -1;
        for (var i = 0; i < versions.length; i++) { if (versions[i].version === selected) { selIdx = i; break; } }
        if (selIdx < 0) { infoPanel.classList.add('hidden'); return; }
        var v = versions[selIdx];
        var h = '<div class="version-info-content">';
        h += '<h4>SpecVersion ' + esc(selected) + '</h4>';
        h += '<p class="version-release">Released: ' + esc(v.release) + '</p>';
        h += '<p class="version-notes">' + esc(v.notes) + '</p>';
        h += '<div class="version-features"><strong>Features introduced:</strong><ul>';
        v.features.forEach(function(f) { h += '<li>' + esc(f) + '</li>'; });
        h += '</ul></div>';
        if (selIdx < versions.length - 1) {
            h += '<div class="version-missing"><strong>Not available in this version:</strong><ul>';
            for (var j = selIdx + 1; j < versions.length; j++) {
                versions[j].features.forEach(function(f) { h += '<li>' + esc(f) + ' <span class="version-tag">(v' + versions[j].version + '+)</span></li>'; });
            }
            h += '</ul></div>';
        }
        h += '</div>';
        infoPanel.innerHTML = h;
        infoPanel.classList.remove('hidden');
    } catch(e) {}
}

// ================ SPLIT HANDLE ================
(function(){
    var handle = $('split-handle'); if (!handle) return;
    var sv = handle.parentElement, dragging = false;
    handle.addEventListener('mousedown', function(e) { dragging = true; e.preventDefault(); document.body.style.cursor = 'col-resize'; document.body.style.userSelect = 'none'; });
    document.addEventListener('mousemove', function(e) { if (!dragging) return; var r = sv.getBoundingClientRect(); var pct = Math.max(25, Math.min(75, ((e.clientX - r.left) / r.width) * 100)); sv.querySelector('.shopper-panel').style.cssText = 'flex:none;width:'+pct+'%'; sv.querySelector('.developer-panel').style.cssText = 'flex:none;width:'+(100-pct)+'%'; });
    document.addEventListener('mouseup', function() { if (dragging) { dragging = false; document.body.style.cursor = ''; document.body.style.userSelect = ''; } });
})();

// ================ CODE VIEWER ================
var codeState = {
    currentFile: null,
    content: '',
    annotations: {},
    unlocked: false,
    editMode: false,
};

async function loadCode(filename, btnEl) {
    // Update file tab buttons
    document.querySelectorAll('.code-file-btn').forEach(function(b) { b.classList.toggle('active', b.dataset.file === filename); });
    try {
        var r = await api('/api/code/' + filename);
        if (!r.ok) { $('code-content').innerHTML = '<p style="padding:1.5rem;color:var(--danger)">' + esc(r.data.error || 'Failed to load') + '</p>'; return; }
        codeState.currentFile = filename;
        codeState.content = r.data.content;
        codeState.annotations = r.data.annotations || {};
        $('code-filename').textContent = filename;
        $('code-lang').textContent = r.data.language;
        renderCodeView();
    } catch(e) {
        $('code-content').innerHTML = '<p style="padding:1.5rem;color:var(--danger)">Error loading file: ' + esc(e.message) + '</p>';
    }
}

function renderCodeView() {
    var el = $('code-content');
    var saveBtn = $('code-save-btn');

    if (codeState.editMode && codeState.unlocked) {
        // Edit mode: show textarea
        el.innerHTML = '<textarea id="code-textarea">' + esc(codeState.content) + '</textarea>';
        saveBtn.classList.remove('hidden');
        return;
    }
    saveBtn.classList.add('hidden');

    // Read-only annotated view
    var lines = codeState.content.split('\n');
    var h = '<table class="code-table">';
    lines.forEach(function(line, idx) {
        var lineNum = idx + 1;
        var lineStr = String(lineNum);
        var ann = codeState.annotations[lineStr];
        var isRoute = /(@app\.route|@app\.get|@app\.post)/.test(line);
        var isSaferpay = /(saferpay_request|saferpay|Payment\/v1)/.test(line);
        var cls = '';
        if (ann) cls += ' annotated';
        if (isRoute) cls += ' route';
        if (isSaferpay) cls += ' saferpay';
        h += '<tr class="code-row' + cls + '"' + (ann ? ' onclick="toggleAnnotation(' + lineNum + ')" title="Click for explanation"' : '') + '>';
        h += '<td class="code-ln">' + lineNum + '</td>';
        h += '<td class="code-line">' + esc(line) + '</td></tr>';
        if (ann) {
            h += '<tr class="annotation-row" id="ann-' + lineNum + '"><td class="code-annotation" colspan="2"><strong>Line ' + lineNum + ':</strong> ' + esc(ann) + '</td></tr>';
        }
    });
    h += '</table>';
    el.innerHTML = h;
}

function toggleAnnotation(lineNum) {
    var row = $('ann-' + lineNum);
    if (row) row.classList.toggle('visible');
}

function showUnlockPrompt() {
    if (codeState.unlocked) {
        // Toggle edit mode
        codeState.editMode = !codeState.editMode;
        $('unlock-btn').textContent = codeState.editMode ? 'View Mode' : 'Edit Mode';
        renderCodeView();
        return;
    }
    $('unlock-prompt').classList.remove('hidden');
    $('unlock-password').value = '';
    $('unlock-message').textContent = '';
    $('unlock-password').focus();
}

async function unlockCode() {
    var pw = $('unlock-password').value;
    var msg = $('unlock-message');
    try {
        var r = await api('/api/code/unlock', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({password:pw})});
        if (r.ok && r.data.unlocked) {
            codeState.unlocked = true;
            codeState.editMode = true;
            $('unlock-prompt').classList.add('hidden');
            $('lock-badge').textContent = 'Edit Enabled';
            $('lock-badge').className = 'lock-badge unlocked';
            $('unlock-btn').textContent = 'View Mode';
            renderCodeView();
        } else {
            msg.className = 'form-message error';
            msg.textContent = 'Wrong password.';
        }
    } catch(e) { msg.className = 'form-message error'; msg.textContent = 'Error'; }
}

async function saveCode() {
    if (!codeState.unlocked || !codeState.currentFile) return;
    var textarea = $('code-textarea');
    if (!textarea) return;
    var content = textarea.value;
    try {
        var r = await api('/api/code/' + codeState.currentFile, {
            method:'POST', headers:{'Content-Type':'application/json'},
            body:JSON.stringify({password:'', content: content})
        });
        // Need password - fetch from state (we verified it already)
        // Actually re-send with stored... let's prompt
        var pw = prompt('Confirm service password to save:');
        if (!pw) return;
        r = await api('/api/code/' + codeState.currentFile, {
            method:'POST', headers:{'Content-Type':'application/json'},
            body:JSON.stringify({password:pw, content:content})
        });
        if (r.ok) {
            codeState.content = content;
            alert(r.data.message || 'Saved!');
        } else {
            alert(r.data.error || 'Save failed');
        }
    } catch(e) { alert('Error: ' + e.message); }
}

// ================ INIT ================
(async function() {
    await checkConfig();
    await loadProducts(true);
    try { var r = await api('/api/icons'); state.icons = r.data; } catch(e) {}
    await loadCustomers(true);
    renderShopper();
    // Set initial lock badge
    $('lock-badge').className = 'lock-badge locked';
})();
