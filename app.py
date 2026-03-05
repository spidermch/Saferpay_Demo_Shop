import os
import uuid
import logging
import traceback
import json
import requests as http_requests
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from werkzeug.middleware.proxy_fix import ProxyFix

# ==================== Debug Logger ====================
DEBUG_LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'debug.log')

debug_logger = logging.getLogger('saferpay_debug')
debug_logger.setLevel(logging.DEBUG)
_fh = logging.FileHandler(DEBUG_LOG_FILE, encoding='utf-8')
_fh.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
debug_logger.addHandler(_fh)

def log_error(context, error, extra=None):
    """Log an error with context to the debug file for remote diagnostics."""
    entry = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'context': context,
        'error': str(error),
        'traceback': traceback.format_exc() if traceback.format_exc().strip() != 'NoneType: None' else None,
        'extra': extra,
    }
    debug_logger.error(json.dumps(entry, default=str))

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'saferpay-explorer-dev-key-change-me')
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

STORE = {}

DEFAULT_PRODUCTS = [
    {'id': 'prod_001', 'name': 'Swiss Luxury Watch', 'description': 'Elegant timepiece crafted in Switzerland', 'price': 29900, 'currency': 'CHF', 'icon': '\u231A', 'active': True},
    {'id': 'prod_002', 'name': 'Premium Chocolate Box', 'description': 'Assorted Swiss chocolate collection', 'price': 4990, 'currency': 'CHF', 'icon': '\U0001F36B', 'active': True},
    {'id': 'prod_003', 'name': 'Swiss Army Knife', 'description': 'Multi-tool classic red design', 'price': 8900, 'currency': 'CHF', 'icon': '\U0001F527', 'active': True},
    {'id': 'prod_004', 'name': 'Fondue Set Deluxe', 'description': 'Traditional ceramic fondue set for 4', 'price': 12900, 'currency': 'CHF', 'icon': '\U0001FAD5', 'active': True},
]

ICONS = ['\u231A', '\U0001F36B', '\U0001F527', '\U0001FAD5', '\U0001F455', '\U0001F45F', '\U0001F4F1', '\U0001F4BB',
         '\U0001F3AE', '\U0001F4DA', '\U0001F3A7', '\u2615', '\U0001F377', '\U0001F48D', '\U0001F381',
         '\U0001FA91', '\U0001F5BC', '\U0001F9F8', '\U0001F392', '\U0001F460']


def _uid():
    return uuid.uuid4().hex[:12]


def get_store():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    sid = session['session_id']
    if sid not in STORE:
        STORE[sid] = {
            'transactions': {},
            'logs': [],
            'products': [p.copy() for p in DEFAULT_PRODUCTS],
            'customers': {},
            'product_seq': len(DEFAULT_PRODUCTS) + 1,
        }
    return STORE[sid]


def get_config():
    return session.get('config')


def saferpay_request(endpoint, payload, config):
    url = f"{config['base_url']}/{endpoint}"
    auth = (config['username'], config['password'])
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    return http_requests.post(url, json=payload, auth=auth, headers=headers, timeout=30)


def build_request_header(config):
    return {
        "SpecVersion": config.get('spec_version', '1.50'),
        "CustomerId": config['customer_id'],
        "RequestId": str(uuid.uuid4()),
        "RetryIndicator": 0
    }


def generate_order_id(config, flow='PP'):
    prefix = config.get('order_id_prefix', 'DEMO')
    pattern = config.get('order_id_pattern', 'prefix-uuid')
    uid = uuid.uuid4().hex[:8].upper()
    ts = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    seq = str(int(datetime.utcnow().timestamp()))[-6:]
    if pattern == 'prefix-timestamp':
        return f"{prefix}-{ts}"
    elif pattern == 'prefix-seq':
        return f"{prefix}-{seq}"
    elif pattern == 'flow-prefix-uuid':
        tag = 'PP' if flow == 'PP' else 'TXN'
        return f"{tag}-{prefix}-{uid}"
    else:
        return f"{prefix}-{uid}"


def _make_log(step, endpoint, explanation, order_id=None):
    entry = {
        'id': _uid(),
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'step': step,
        'endpoint': endpoint,
        'method': 'POST',
        'request': None,
        'response': None,
        'status_code': None,
        'explanation': explanation,
    }
    if order_id:
        entry['order_id'] = order_id
    return entry


# ==================== Saferpay Spec Versions ====================

SAFERPAY_SPEC_VERSIONS = [
    {'version': '1.05', 'release': '2015-Q3',
     'features': ['PaymentPage Initialize/Assert', 'Transaction Initialize/Authorize', 'Transaction Capture', 'Transaction Cancel'],
     'notes': 'Initial JSON API release. Core payment flows.'},
    {'version': '1.10', 'release': '2016-Q2',
     'features': ['Alias/Insert (Tokenization)', 'Alias/AssertInsert', 'Alias/Delete', 'Batch/Close'],
     'notes': 'Tokenization (Alias) support and batch settlement.'},
    {'version': '1.15', 'release': '2017-Q1',
     'features': ['Transaction/Refund', 'AuthorizeReferenced (Recurring)', 'Transaction/Inquire'],
     'notes': 'Refund capability and referenced (recurring) transactions.'},
    {'version': '1.20', 'release': '2018-Q1',
     'features': ['Secure Fields iFrame', 'PaymentPage Styling options'],
     'notes': 'Secure Fields integration for embedded card input on merchant page.'},
    {'version': '1.25', 'release': '2019-Q2',
     'features': ['3-D Secure 2.0 (SCA)', 'RiskFactors', 'Enhanced Payer object'],
     'notes': 'PSD2/SCA compliance with 3DS 2.x. Enhanced risk data submission.'},
    {'version': '1.30', 'release': '2020-Q4',
     'features': ['Multipart Capture', 'Server Notification URLs', 'Improved error codes'],
     'notes': 'Split settlement and server-to-server notifications.'},
    {'version': '1.33', 'release': '2023-03',
     'features': ['PayerNote field', 'Payconiq integration', 'Enhanced Redirect object'],
     'notes': 'Payconiq payments, PayerNote, and DCC enhancements.'},
    {'version': '1.38', 'release': '2024-01',
     'features': ['Account-to-Account Payments', 'Pending transaction status', '3DS challenge enforcement'],
     'notes': 'A2A force instant option and Secure PayGate enhancements.'},
    {'version': '1.41', 'release': '2024-07',
     'features': ['Scheme tokenization', 'Chase Paymentech acquiring', 'TWINT omni-channel/UoF', 'Saferpay Fields dual-branded cards'],
     'notes': 'Card lifecycle management via scheme tokenization. TWINT UoF support.'},
    {'version': '1.44', 'release': '2025-01',
     'features': ['Click to Pay Visa self-onboarding', 'Mastercard Click to Pay registration', 'BLIK enhancements', 'Enhanced Alias Inquire'],
     'notes': 'Click to Pay rollout and scheme tokenization risk management.'},
    {'version': '1.45', 'release': '2025-03',
     'features': ['Reka payment methods', 'Scheme tokenization improvements', 'Click to Pay improvements', 'User Administration enhancements'],
     'notes': 'Swiss Reka payments and improved scheme tokenization.'},
    {'version': '1.46', 'release': '2025-05',
     'features': ['External 3-D Secure data', 'Omnichannel for Worldline UK', 'Enhanced user self-service'],
     'notes': 'Accept external 3DS authentication results. Omnichannel UK support.'},
    {'version': '1.47', 'release': '2025-07',
     'features': ['Redesigned Payment Page (pilot)', 'Redesigned Backoffice (pilot)', 'DCC for Worldline UK', 'Cybersource fraud intelligence'],
     'notes': 'New Payment Page design pilot and Cybersource DFP integration.'},
    {'version': '1.48', 'release': '2025-09',
     'features': ['New Payment Page with Click to Pay', 'Boncard integration', 'Transaction Reporting via Management API', 'Multi-Use Payment Links journal'],
     'notes': 'Redesigned Payment Page GA with Click to Pay. Boncard (Swiss gift/loyalty). Management API reporting.'},
    {'version': '1.49', 'release': '2025-11',
     'features': ['Wero payment method (EPI)', 'Apple Pay in third-party browsers', 'BLIK on Transaction Interface', 'Single-Use Payment Link controls'],
     'notes': 'Wero (European Payment Initiative) launch. Apple Pay browser expansion.'},
    {'version': '1.50', 'release': '2026-01',
     'features': ['PostFinance Pay Instant Payout', 'Wero refund reasons', 'Saferpay OpenAPI specification', 'Mastercard Click to Pay tokenization'],
     'notes': 'Latest version. PostFinance instant payouts, OpenAPI spec, and Wero refund support.'},
]


# ==================== Feature Audit ====================

SAFERPAY_FEATURE_AUDIT = [
    {'name': 'Payment Initiation', 'features': [
        {'id': 'pp_init', 'name': 'PaymentPage Initialize', 'endpoint': 'Payment/v1/PaymentPage/Initialize', 'implemented': True,
         'description': 'Full-redirect payment page with all payment methods offered automatically.'},
        {'id': 'txn_init', 'name': 'Transaction Initialize', 'endpoint': 'Payment/v1/Transaction/Initialize', 'implemented': True,
         'description': 'Advanced flow with more merchant control over payment method selection.'},
    ]},
    {'name': 'Payment Verification', 'features': [
        {'id': 'pp_assert', 'name': 'PaymentPage Assert', 'endpoint': 'Payment/v1/PaymentPage/Assert', 'implemented': True,
         'description': 'Verify PaymentPage result and retrieve transaction details.'},
        {'id': 'txn_authorize', 'name': 'Transaction Authorize', 'endpoint': 'Payment/v1/Transaction/Authorize', 'implemented': True,
         'description': 'Verify Transaction Interface result and get authorization details.'},
    ]},
    {'name': 'Transaction Management', 'features': [
        {'id': 'capture', 'name': 'Transaction Capture', 'endpoint': 'Payment/v1/Transaction/Capture', 'implemented': True,
         'description': 'Settle authorized transactions to transfer funds to merchant.'},
        {'id': 'cancel', 'name': 'Transaction Cancel', 'endpoint': 'Payment/v1/Transaction/Cancel', 'implemented': False,
         'description': 'Void an authorization before capture. Releases reserved funds immediately.'},
        {'id': 'refund', 'name': 'Transaction Refund', 'endpoint': 'Payment/v1/Transaction/Refund', 'implemented': False,
         'description': 'Refund a previously captured transaction (partial or full).'},
        {'id': 'multipart', 'name': 'Multipart Capture', 'endpoint': 'Payment/v1/Transaction/MultipartCapture', 'implemented': False,
         'description': 'Capture an authorization in multiple partial amounts (split settlement).'},
    ]},
    {'name': 'Tokenization & Recurring', 'features': [
        {'id': 'alias_insert', 'name': 'Alias/Insert', 'endpoint': 'Payment/v1/Alias/Insert', 'implemented': False,
         'description': 'Store card details as a token (alias) for one-click or recurring payments.'},
        {'id': 'alias_assert', 'name': 'Alias/AssertInsert', 'endpoint': 'Payment/v1/Alias/AssertInsert', 'implemented': False,
         'description': 'Verify a stored alias after customer card registration flow.'},
        {'id': 'alias_delete', 'name': 'Alias/Delete', 'endpoint': 'Payment/v1/Alias/Delete', 'implemented': False,
         'description': 'Remove a stored card alias from Saferpay vault.'},
        {'id': 'auth_ref', 'name': 'AuthorizeReferenced', 'endpoint': 'Payment/v1/Transaction/AuthorizeReferenced', 'implemented': False,
         'description': 'Charge a stored alias (recurring or one-click) without customer redirect.'},
    ]},
    {'name': 'Secure Fields', 'features': [
        {'id': 'sf_init', 'name': 'Secure Fields Initialize', 'endpoint': 'Payment/v1/Transaction/Initialize', 'implemented': False,
         'description': 'Embed card input fields directly in merchant page via iFrame. Minimal PCI scope.'},
        {'id': 'sf_auth', 'name': 'Secure Fields Authorize', 'endpoint': 'Payment/v1/Transaction/Authorize', 'implemented': False,
         'description': 'Authorize a transaction initiated via Secure Fields.'},
    ]},
    {'name': 'Batch & Reporting', 'features': [
        {'id': 'batch', 'name': 'Batch/Close', 'endpoint': 'Payment/v1/Batch/Close', 'implemented': False,
         'description': 'Close the current batch of transactions for settlement processing.'},
        {'id': 'inquire', 'name': 'Transaction Inquire', 'endpoint': 'Payment/v1/Transaction/Inquire', 'implemented': False,
         'description': 'Query the current status of a transaction by TransactionId.'},
    ]},
    {'name': 'Risk & 3-D Secure', 'features': [
        {'id': '3ds', 'name': '3-D Secure (automatic)', 'endpoint': None, 'implemented': True,
         'description': '3-D Secure authentication is handled automatically by Saferpay during payment flows.'},
        {'id': 'risk', 'name': 'Risk Information', 'endpoint': None, 'implemented': False,
         'description': 'Send additional risk data (device info, basket, history) to improve authorization rates.'},
    ]},
]


# ==================== Journey Templates ====================

JOURNEY_TEMPLATES = {
    'PaymentPage': [
        {'step': 'Cart & Checkout', 'actor': 'merchant',
         'description': 'Customer selects products and clicks "Pay Now". The merchant app collects cart items, calculates total, and prepares the payment request.',
         'code_ref': 'app.js : checkout()', 'api_call': None},
        {'step': 'PaymentPage/Initialize', 'actor': 'saferpay',
         'description': 'Merchant server sends Initialize request to Saferpay with amount, currency, OrderId, and return URLs. Saferpay creates a payment session and returns a Token + RedirectUrl.',
         'code_ref': 'app.py : initialize_payment()', 'api_call': 'Payment/v1/PaymentPage/Initialize'},
        {'step': 'Customer Redirect', 'actor': 'browser',
         'description': 'Customer is redirected to the Saferpay-hosted payment page in a popup. Card data is entered on Saferpay servers - PCI scope stays with Saferpay, the merchant never sees raw card numbers.',
         'code_ref': 'app.js : window.open()', 'api_call': None},
        {'step': 'PaymentPage/Assert', 'actor': 'saferpay',
         'description': 'After customer returns, merchant calls Assert to verify the payment. Saferpay returns TransactionId, payment means details (card brand, masked number), liability shift info, and authorization status.',
         'code_ref': 'app.py : assert_payment()', 'api_call': 'Payment/v1/PaymentPage/Assert'},
        {'step': 'Transaction/Capture', 'actor': 'saferpay', 'optional': True,
         'description': 'Merchant captures (settles) the authorized amount. Authorization only reserved funds on the card; Capture triggers the actual money transfer to the merchant account.',
         'code_ref': 'app.py : capture_payment()', 'api_call': 'Payment/v1/Transaction/Capture'},
    ],
    'Transaction': [
        {'step': 'Cart & Checkout', 'actor': 'merchant',
         'description': 'Customer selects products and clicks "Pay Now". With Transaction Interface, merchant can also send Payer info (name, email) for a better UX on the payment page.',
         'code_ref': 'app.js : checkout()', 'api_call': None},
        {'step': 'Transaction/Initialize', 'actor': 'saferpay',
         'description': 'Merchant server sends Initialize request via the Transaction Interface. This gives more control than PaymentPage: specific payment method preselection, Secure Fields, custom styling. Returns Token + RedirectUrl.',
         'code_ref': 'app.py : transaction_initialize()', 'api_call': 'Payment/v1/Transaction/Initialize'},
        {'step': 'Customer Redirect', 'actor': 'browser',
         'description': 'Customer is redirected to Saferpay for payment. Unlike PaymentPage, the Transaction flow uses a single ReturnUrl (no separate Abort URL).',
         'code_ref': 'app.js : window.open()', 'api_call': None},
        {'step': 'Transaction/Authorize', 'actor': 'saferpay',
         'description': 'After customer returns, merchant calls Authorize (instead of Assert) to verify the transaction. Returns the same data: TransactionId, payment means, liability shift, and 3-D Secure details.',
         'code_ref': 'app.py : transaction_authorize()', 'api_call': 'Payment/v1/Transaction/Authorize'},
        {'step': 'Transaction/Capture', 'actor': 'saferpay', 'optional': True,
         'description': 'Capture is identical for both flows - same endpoint, same request. Settles the authorized amount to the merchant.',
         'code_ref': 'app.py : capture_payment()', 'api_call': 'Payment/v1/Transaction/Capture'},
    ],
}


def build_journey_steps(txn, logs, flow):
    templates = JOURNEY_TEMPLATES.get(flow, JOURNEY_TEMPLATES['PaymentPage'])
    steps = []
    for tmpl in templates:
        step = dict(tmpl)
        if tmpl['api_call']:
            match = next((l for l in logs if tmpl['api_call'] in l.get('endpoint', '')), None)
            if match:
                step['log_id'] = match['id']
                step['status_code'] = match.get('status_code')
                step['timestamp'] = match.get('timestamp')
                step['completed'] = True
            else:
                step['completed'] = False
        else:
            # Non-API steps: completed based on order status progression
            step['completed'] = txn.get('status') not in (None, '')
        steps.append(step)
    return steps


# ==================== Pages ====================

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/return/success')
def return_success():
    return render_template('return.html', status='success')


@app.route('/return/fail')
def return_fail():
    return render_template('return.html', status='fail')


@app.route('/return/transaction')
def return_transaction():
    return render_template('return.html', status='transaction_return')


# ==================== Config API ====================

@app.route('/api/config', methods=['POST'])
def save_config():
    data = request.json
    required = ['customer_id', 'terminal_id', 'username', 'password']
    missing = [f for f in required if not data.get(f, '').strip()]
    if missing:
        return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400
    session['config'] = {
        'customer_id': data['customer_id'].strip(),
        'terminal_id': data['terminal_id'].strip(),
        'username': data['username'].strip(),
        'password': data['password'].strip(),
        'base_url': data.get('base_url', 'https://test.saferpay.com/api').strip().rstrip('/'),
        'spec_version': data.get('spec_version', '1.50').strip(),
        'order_id_prefix': data.get('order_id_prefix', 'DEMO').strip() or 'DEMO',
        'order_id_pattern': data.get('order_id_pattern', 'prefix-uuid').strip(),
        'default_description': data.get('default_description', 'Saferpay Explorer Demo Order').strip(),
        'payer_note': data.get('payer_note', '').strip(),
    }
    return jsonify({'status': 'ok'})


@app.route('/api/config/status')
def config_status():
    config = get_config()
    if config:
        return jsonify({
            'configured': True,
            'customer_id': config['customer_id'],
            'terminal_id': config['terminal_id'],
            'base_url': config['base_url'],
            'spec_version': config.get('spec_version', '1.50'),
            'order_id_prefix': config.get('order_id_prefix', 'DEMO'),
            'order_id_pattern': config.get('order_id_pattern', 'prefix-uuid'),
            'default_description': config.get('default_description', 'Saferpay Explorer Demo Order'),
            'payer_note': config.get('payer_note', ''),
        })
    return jsonify({'configured': False})


# ==================== Products API ====================

@app.route('/api/products')
def list_products():
    store = get_store()
    return jsonify(store['products'])


@app.route('/api/products', methods=['POST'])
def add_product():
    store = get_store()
    data = request.json
    if not data.get('name', '').strip():
        return jsonify({'error': 'Product name is required'}), 400
    price = data.get('price', 0)
    if isinstance(price, str):
        price = int(float(price.replace(',', '.')) * 100)
    seq = store['product_seq']
    store['product_seq'] = seq + 1
    product = {
        'id': f'prod_{seq:03d}',
        'name': data['name'].strip(),
        'description': data.get('description', '').strip(),
        'price': int(price),
        'currency': data.get('currency', 'CHF'),
        'icon': data.get('icon', '\U0001F381'),
        'active': True,
    }
    store['products'].append(product)
    return jsonify(product), 201


@app.route('/api/products/<pid>', methods=['PUT'])
def update_product(pid):
    store = get_store()
    product = next((p for p in store['products'] if p['id'] == pid), None)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    data = request.json
    if 'name' in data:
        product['name'] = data['name'].strip()
    if 'description' in data:
        product['description'] = data['description'].strip()
    if 'price' in data:
        p = data['price']
        if isinstance(p, str):
            p = int(float(p.replace(',', '.')) * 100)
        product['price'] = int(p)
    if 'icon' in data:
        product['icon'] = data['icon']
    if 'active' in data:
        product['active'] = bool(data['active'])
    if 'currency' in data:
        product['currency'] = data['currency']
    return jsonify(product)


@app.route('/api/products/<pid>', methods=['DELETE'])
def delete_product(pid):
    store = get_store()
    store['products'] = [p for p in store['products'] if p['id'] != pid]
    return jsonify({'status': 'ok'})


@app.route('/api/icons')
def list_icons():
    return jsonify(ICONS)


# ==================== Customers API ====================

@app.route('/api/customers')
def list_customers():
    store = get_store()
    customers = list(store['customers'].values())
    for c in customers:
        c['order_count'] = sum(1 for t in store['transactions'].values() if t.get('customer_id') == c['id'])
        c['total_spent'] = sum(t.get('amount', 0) for t in store['transactions'].values()
                               if t.get('customer_id') == c['id'] and t.get('status') in ('AUTHORIZED', 'CAPTURED'))
    customers.sort(key=lambda c: c.get('created', ''), reverse=True)
    return jsonify(customers)


@app.route('/api/customers', methods=['POST'])
def add_customer():
    store = get_store()
    data = request.json
    if not data.get('name', '').strip():
        return jsonify({'error': 'Customer name is required'}), 400
    cid = f'cust_{_uid()}'
    customer = {
        'id': cid,
        'name': data['name'].strip(),
        'email': data.get('email', '').strip(),
        'company': data.get('company', '').strip(),
        'phone': data.get('phone', '').strip(),
        'address': data.get('address', '').strip(),
        'notes': [],
        'created': datetime.utcnow().isoformat() + 'Z',
    }
    store['customers'][cid] = customer
    return jsonify(customer), 201


@app.route('/api/customers/<cid>', methods=['PUT'])
def update_customer(cid):
    store = get_store()
    customer = store['customers'].get(cid)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    data = request.json
    for field in ('name', 'email', 'company', 'phone', 'address'):
        if field in data:
            customer[field] = data[field].strip()
    return jsonify(customer)


@app.route('/api/customers/<cid>', methods=['DELETE'])
def delete_customer(cid):
    store = get_store()
    store['customers'].pop(cid, None)
    return jsonify({'status': 'ok'})


@app.route('/api/customers/<cid>/notes', methods=['POST'])
def add_customer_note(cid):
    store = get_store()
    customer = store['customers'].get(cid)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    data = request.json
    text = data.get('text', '').strip()
    if not text:
        return jsonify({'error': 'Note text is required'}), 400
    note = {
        'id': f'note_{_uid()}',
        'text': text,
        'created': datetime.utcnow().isoformat() + 'Z',
    }
    customer['notes'].append(note)
    return jsonify(note), 201


@app.route('/api/customers/<cid>/orders')
def customer_orders(cid):
    store = get_store()
    orders = [t for t in store['transactions'].values() if t.get('customer_id') == cid]
    orders.sort(key=lambda o: o.get('created', ''), reverse=True)
    return jsonify(orders)


# ==================== Payment: PaymentPage Flow ====================

@app.route('/api/initialize', methods=['POST'])
def initialize_payment():
    config = get_config()
    if not config:
        return jsonify({'error': 'Not configured. Go to Config tab first.'}), 400

    data = request.json
    store = get_store()
    order_id = generate_order_id(config, 'PP')
    base_url = request.url_root.rstrip('/')
    description = data.get('description') or config.get('default_description', 'Saferpay Explorer Demo Order')

    payload = {
        "RequestHeader": build_request_header(config),
        "TerminalId": config['terminal_id'],
        "Payment": {
            "Amount": {
                "Value": str(data['amount']),
                "CurrencyCode": data.get('currency', 'CHF')
            },
            "OrderId": order_id,
            "Description": description
        },
        "ReturnUrl": {"Url": f"{base_url}/return/success"},
        "Abort": {"Url": f"{base_url}/return/fail"}
    }
    if config.get('payer_note'):
        payload["Payment"]["PayerNote"] = config['payer_note']

    log_entry = _make_log('PP Initialize', 'Payment/v1/PaymentPage/Initialize',
        'PaymentPage/Initialize creates a payment session. The response includes a Token '
        '(used later to Assert the outcome) and a RedirectUrl (the Saferpay-hosted payment page '
        'where the customer enters their card details). All payment methods enabled on the terminal '
        'are offered automatically. Card data never touches the merchant server.',
        order_id)
    log_entry['request'] = payload

    try:
        resp = saferpay_request('Payment/v1/PaymentPage/Initialize', payload, config)
        log_entry['status_code'] = resp.status_code
        log_entry['response'] = resp.json()
        store['logs'].append(log_entry)

        if resp.status_code == 200:
            resp_data = resp.json()
            token = resp_data.get('Token')
            store['transactions'][token] = {
                'token': token, 'order_id': order_id,
                'amount': data['amount'], 'currency': data.get('currency', 'CHF'),
                'items': data.get('items', []),
                'customer_id': data.get('customer_id'),
                'payment_flow': 'PaymentPage',
                'status': 'INITIALIZED',
                'created': datetime.utcnow().isoformat() + 'Z',
                'redirect_url': resp_data.get('RedirectUrl'),
                'transaction_id': None, 'payment_means': None,
                'description': description,
            }
            return jsonify({'success': True, 'token': token,
                            'redirect_url': resp_data.get('RedirectUrl'),
                            'order_id': order_id, 'log': log_entry})
        else:
            return jsonify({'success': False, 'error': resp.json(), 'log': log_entry}), 400
    except Exception as e:
        log_error('initialize_payment', e, extra={'order_id': order_id})
        log_entry['status_code'] = 0
        log_entry['response'] = {'error': str(e)}
        store['logs'].append(log_entry)
        return jsonify({'success': False, 'error': str(e), 'log': log_entry}), 500


@app.route('/api/assert', methods=['POST'])
def assert_payment():
    config = get_config()
    if not config:
        return jsonify({'error': 'Not configured'}), 400
    data = request.json
    token = data.get('token')
    store = get_store()
    order_id = store['transactions'].get(token, {}).get('order_id') if token else None

    payload = {"RequestHeader": build_request_header(config), "Token": token}
    log_entry = _make_log('PP Assert', 'Payment/v1/PaymentPage/Assert',
        'PaymentPage/Assert validates the payment after the customer returns. Returns the '
        'authorization result including TransactionId, payment means details (card brand, masked '
        'number), and liability shift information. Must be called before the token expires (~20 min).',
        order_id)
    log_entry['request'] = payload

    try:
        resp = saferpay_request('Payment/v1/PaymentPage/Assert', payload, config)
        log_entry['status_code'] = resp.status_code
        log_entry['response'] = resp.json()
        store['logs'].append(log_entry)

        if resp.status_code == 200:
            resp_data = resp.json()
            txn_id = resp_data.get('Transaction', {}).get('Id')
            if token in store['transactions']:
                store['transactions'][token].update({
                    'status': 'AUTHORIZED', 'transaction_id': txn_id,
                    'payment_means': resp_data.get('PaymentMeans', {}),
                    'liability': resp_data.get('Liability', {}),
                    'six_transaction_reference': resp_data.get('Transaction', {}).get('SixTransactionReference'),
                })
            return jsonify({'success': True, 'data': resp_data, 'transaction_id': txn_id, 'log': log_entry})
        else:
            if token in store['transactions']:
                store['transactions'][token]['status'] = 'FAILED'
            return jsonify({'success': False, 'error': resp.json(), 'log': log_entry}), 400
    except Exception as e:
        log_error('assert_payment', e, extra={'token': token})
        log_entry['status_code'] = 0
        log_entry['response'] = {'error': str(e)}
        store['logs'].append(log_entry)
        return jsonify({'success': False, 'error': str(e), 'log': log_entry}), 500


# ==================== Payment: Transaction Flow ====================

@app.route('/api/transaction/initialize', methods=['POST'])
def transaction_initialize():
    config = get_config()
    if not config:
        return jsonify({'error': 'Not configured. Go to Config tab first.'}), 400

    data = request.json
    store = get_store()
    order_id = generate_order_id(config, 'TXN')
    base_url = request.url_root.rstrip('/')
    description = data.get('description') or config.get('default_description', 'Saferpay Explorer Demo Order')

    payload = {
        "RequestHeader": build_request_header(config),
        "TerminalId": config['terminal_id'],
        "Payment": {
            "Amount": {
                "Value": str(data['amount']),
                "CurrencyCode": data.get('currency', 'CHF')
            },
            "OrderId": order_id,
            "Description": description
        },
        "ReturnUrl": {"Url": f"{base_url}/return/transaction"},
    }
    if config.get('payer_note'):
        payload["Payment"]["PayerNote"] = config['payer_note']

    # Add payer info if customer is selected
    if data.get('payer'):
        payload["Payer"] = data['payer']

    log_entry = _make_log('TXN Initialize', 'Payment/v1/Transaction/Initialize',
        'Transaction/Initialize creates a transaction via the Transaction Interface. Unlike '
        'PaymentPage, this gives the merchant more control: specific payment method preselection, '
        'Secure Fields integration, and custom styling. The response also returns a Token and '
        'RedirectUrl, but the flow continues with Transaction/Authorize instead of PaymentPage/Assert.',
        order_id)
    log_entry['request'] = payload

    try:
        resp = saferpay_request('Payment/v1/Transaction/Initialize', payload, config)
        log_entry['status_code'] = resp.status_code
        log_entry['response'] = resp.json()
        store['logs'].append(log_entry)

        if resp.status_code == 200:
            resp_data = resp.json()
            token = resp_data.get('Token')
            redirect_url = resp_data.get('Redirect', {}).get('RedirectUrl') or resp_data.get('RedirectUrl', '')
            store['transactions'][token] = {
                'token': token, 'order_id': order_id,
                'amount': data['amount'], 'currency': data.get('currency', 'CHF'),
                'items': data.get('items', []),
                'customer_id': data.get('customer_id'),
                'payment_flow': 'Transaction',
                'status': 'INITIALIZED',
                'created': datetime.utcnow().isoformat() + 'Z',
                'redirect_url': redirect_url,
                'transaction_id': None, 'payment_means': None,
                'description': description,
            }
            return jsonify({'success': True, 'token': token,
                            'redirect_url': redirect_url,
                            'order_id': order_id, 'log': log_entry})
        else:
            return jsonify({'success': False, 'error': resp.json(), 'log': log_entry}), 400
    except Exception as e:
        log_error('transaction_initialize', e, extra={'order_id': order_id})
        log_entry['status_code'] = 0
        log_entry['response'] = {'error': str(e)}
        store['logs'].append(log_entry)
        return jsonify({'success': False, 'error': str(e), 'log': log_entry}), 500


@app.route('/api/transaction/authorize', methods=['POST'])
def transaction_authorize():
    config = get_config()
    if not config:
        return jsonify({'error': 'Not configured'}), 400
    data = request.json
    token = data.get('token')
    store = get_store()
    order_id = store['transactions'].get(token, {}).get('order_id') if token else None

    payload = {"RequestHeader": build_request_header(config), "Token": token}
    log_entry = _make_log('TXN Authorize', 'Payment/v1/Transaction/Authorize',
        'Transaction/Authorize checks the result after the customer completes the Transaction flow. '
        'Functionally similar to PaymentPage/Assert but used exclusively with the Transaction '
        'Interface. Returns TransactionId, payment means, liability shift, and 3-D Secure details.',
        order_id)
    log_entry['request'] = payload

    try:
        resp = saferpay_request('Payment/v1/Transaction/Authorize', payload, config)
        log_entry['status_code'] = resp.status_code
        log_entry['response'] = resp.json()
        store['logs'].append(log_entry)

        if resp.status_code == 200:
            resp_data = resp.json()
            txn_id = resp_data.get('Transaction', {}).get('Id')
            if token in store['transactions']:
                store['transactions'][token].update({
                    'status': 'AUTHORIZED', 'transaction_id': txn_id,
                    'payment_means': resp_data.get('PaymentMeans', {}),
                    'liability': resp_data.get('Liability', {}),
                    'six_transaction_reference': resp_data.get('Transaction', {}).get('SixTransactionReference'),
                })
            return jsonify({'success': True, 'data': resp_data, 'transaction_id': txn_id, 'log': log_entry})
        else:
            if token in store['transactions']:
                store['transactions'][token]['status'] = 'FAILED'
            return jsonify({'success': False, 'error': resp.json(), 'log': log_entry}), 400
    except Exception as e:
        log_error('transaction_authorize', e, extra={'token': token})
        log_entry['status_code'] = 0
        log_entry['response'] = {'error': str(e)}
        store['logs'].append(log_entry)
        return jsonify({'success': False, 'error': str(e), 'log': log_entry}), 500


# ==================== Shared: Capture ====================

@app.route('/api/capture', methods=['POST'])
def capture_payment():
    config = get_config()
    if not config:
        return jsonify({'error': 'Not configured'}), 400
    data = request.json
    transaction_id = data.get('transaction_id')
    token = data.get('token')
    store = get_store()
    order_id = store['transactions'].get(token, {}).get('order_id') if token else None

    payload = {
        "RequestHeader": build_request_header(config),
        "TransactionReference": {"TransactionId": transaction_id}
    }
    log_entry = _make_log('Capture', 'Payment/v1/Transaction/Capture',
        'Captures (settles) the authorized transaction. Authorization only reserves the amount; '
        'Capture triggers the actual money transfer. Shared by both PaymentPage and Transaction flows.',
        order_id)
    log_entry['request'] = payload

    try:
        resp = saferpay_request('Payment/v1/Transaction/Capture', payload, config)
        log_entry['status_code'] = resp.status_code
        log_entry['response'] = resp.json()
        store['logs'].append(log_entry)
        if resp.status_code == 200:
            if token and token in store['transactions']:
                store['transactions'][token]['status'] = 'CAPTURED'
            return jsonify({'success': True, 'data': resp.json(), 'log': log_entry})
        else:
            return jsonify({'success': False, 'error': resp.json(), 'log': log_entry}), 400
    except Exception as e:
        log_error('capture_payment', e, extra={'transaction_id': transaction_id})
        log_entry['status_code'] = 0
        log_entry['response'] = {'error': str(e)}
        store['logs'].append(log_entry)
        return jsonify({'success': False, 'error': str(e), 'log': log_entry}), 500


# ==================== Data API ====================

@app.route('/api/transactions')
def get_transactions():
    store = get_store()
    txns = list(store['transactions'].values())
    # enrich with customer name
    for t in txns:
        cid = t.get('customer_id')
        if cid and cid in store['customers']:
            t['customer_name'] = store['customers'][cid]['name']
        else:
            t['customer_name'] = 'Guest'
    txns.sort(key=lambda t: t.get('created', ''), reverse=True)
    return jsonify(txns)


@app.route('/api/logs')
def get_logs():
    return jsonify(get_store()['logs'])


@app.route('/api/logs/clear', methods=['POST'])
def clear_logs():
    get_store()['logs'] = []
    return jsonify({'status': 'ok'})


@app.route('/api/transactions/clear', methods=['POST'])
def clear_transactions():
    get_store()['transactions'] = {}
    return jsonify({'status': 'ok'})


# ==================== Spec Versions & Feature Audit ====================

@app.route('/api/spec-versions')
def spec_versions():
    config = get_config()
    current = config.get('spec_version', '1.50') if config else '1.50'
    return jsonify({'current': current, 'versions': SAFERPAY_SPEC_VERSIONS})


@app.route('/api/feature-audit')
def feature_audit():
    total = sum(len(cat['features']) for cat in SAFERPAY_FEATURE_AUDIT)
    implemented = sum(1 for cat in SAFERPAY_FEATURE_AUDIT for f in cat['features'] if f['implemented'])
    return jsonify({
        'categories': SAFERPAY_FEATURE_AUDIT,
        'stats': {
            'total': total,
            'implemented': implemented,
            'coverage_pct': round((implemented / total) * 100) if total > 0 else 0,
        }
    })


@app.route('/api/orders/<order_id>/journey')
def order_journey(order_id):
    store = get_store()
    txn = next((t for t in store['transactions'].values() if t.get('order_id') == order_id), None)
    if not txn:
        return jsonify({'error': 'Order not found'}), 404
    order_logs = sorted(
        [l for l in store['logs'] if l.get('order_id') == order_id],
        key=lambda l: l.get('timestamp', '')
    )
    flow = txn.get('payment_flow', 'PaymentPage')
    steps = build_journey_steps(txn, order_logs, flow)
    return jsonify({
        'order_id': order_id, 'flow': flow,
        'status': txn.get('status'), 'amount': txn.get('amount'),
        'currency': txn.get('currency'), 'created': txn.get('created'),
        'description': txn.get('description', ''),
        'steps': steps, 'logs': order_logs,
    })


# ==================== Code Viewer API ====================

SERVICE_PASSWORD = '1235789'

# Annotations: line-number -> explanation (for key educational lines)
ANNOTATIONS = {
    'app.py': {
        6: 'ProxyFix ensures correct URLs when behind a reverse proxy (Railway, Heroku, etc.)',
        8: 'Flask is the lightweight web framework powering the backend',
        9: 'SECRET_KEY signs session cookies - use a strong random value in production',
        10: 'ProxyFix trusts X-Forwarded-* headers from one proxy hop',
        12: 'In-memory store: fast for demo, but lost on restart. Use Redis/DB in production.',
        30: 'All Saferpay API calls use HTTP Basic Auth (username:password)',
        34: 'Always set a timeout on external HTTP calls to avoid hanging requests',
        38: 'SpecVersion 1.50 = the Saferpay JSON API protocol version we target',
        43: 'RetryIndicator=0 means this is the first attempt (increment on retries)',
        50: 'Single-page app: Flask serves one HTML page, JS handles all views',
        97: 'Session stores config in signed cookie - never store secrets in plain cookies in prod',
        109: 'CSRF note: in production, add CSRF tokens to all state-changing requests',
        126: 'PaymentPage/Initialize: creates a payment session, returns redirect URL',
        133: 'ReturnUrl: where Saferpay sends the customer after successful payment',
        134: 'Abort URL: where customer lands if they cancel on the payment page',
        150: 'HTTP 200 from Saferpay = payment session created. Token is the key to everything.',
        164: 'We track each transaction in our store keyed by the Saferpay Token',
        191: 'PaymentPage/Assert: called AFTER customer returns to verify the payment worked',
        201: 'The Token ties the Assert back to the original Initialize call',
        222: 'Transaction/Initialize: alternative flow giving merchant more control',
        235: 'For Transaction flow, ReturnUrl is a single URL (no separate Abort)',
        237: 'Payer object sends customer info to Saferpay (name, email) for better UX',
        257: 'Redirect.RedirectUrl: where to send the customer for this specific transaction',
        285: 'Transaction/Authorize: similar to Assert but for the Transaction Interface',
        303: 'Transaction/Capture: this is the SAME endpoint regardless of PaymentPage or Transaction',
        309: 'Capture = "settle" = actually move the money. Authorization was just a reservation.',
    },
    'app.js': {
        1: 'Client-side JavaScript: no frameworks, vanilla JS for full transparency',
        4: 'State object: single source of truth for the entire UI',
        22: 'fmt() converts minor units (cents) to display format: 29900 -> "CHF 299.00"',
        24: 'syntaxHL(): custom JSON syntax highlighter without external libraries',
        43: 'Tab switching: toggles CSS classes, lazy-loads data for each tab',
        50: 'renderShopper(): state machine pattern - shopView controls which screen shows',
        83: 'Products loaded from server API, not hardcoded - merchant can add/remove',
        101: 'Checkout shows customer selector + payment flow choice (PP vs TXN)',
        120: 'checkout(): the main payment flow orchestrator',
        130: 'For Transaction flow, we attach Payer info (name, email) from CRM',
        140: 'window.open(): payment page opens in popup so split-view stays visible',
        146: 'doAssertOrAuthorize(): called after customer returns from Saferpay',
        147: 'Routes to PP/Assert or TXN/Authorize based on which flow was used',
        167: 'postMessage listener: popup window communicates back to parent via this',
        175: 'Fallback: poll for popup close in case postMessage fails (cross-origin)',
        188: 'addApiLog(): every API call is pushed to the dev panel in real-time',
        226: 'Product CRUD: full create/read/update/delete for the product catalog',
        270: 'Customer CRM: search, notes, order history, lifetime value tracking',
        310: 'showCustomerDetail(): builds a full customer profile page with all data',
    },
}


@app.route('/api/code/<filename>')
def get_code(filename):
    allowed = {
        'app.py': 'app.py',
        'app.js': os.path.join('static', 'js', 'app.js'),
        'style.css': os.path.join('static', 'css', 'style.css'),
        'index.html': os.path.join('templates', 'index.html'),
    }
    if filename not in allowed:
        return jsonify({'error': 'File not available'}), 404
    filepath = os.path.join(os.path.dirname(__file__), allowed[filename])
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404
    annotations = ANNOTATIONS.get(filename, {})
    return jsonify({
        'filename': filename,
        'content': content,
        'annotations': {str(k): v for k, v in annotations.items()},
        'language': 'python' if filename.endswith('.py') else ('javascript' if filename.endswith('.js') else ('css' if filename.endswith('.css') else 'html'))
    })


@app.route('/api/code/<filename>', methods=['POST'])
def save_code(filename):
    data = request.json
    if data.get('password') != SERVICE_PASSWORD:
        return jsonify({'error': 'Invalid service password'}), 403
    allowed = {
        'app.py': 'app.py',
        'app.js': os.path.join('static', 'js', 'app.js'),
        'style.css': os.path.join('static', 'css', 'style.css'),
        'index.html': os.path.join('templates', 'index.html'),
    }
    if filename not in allowed:
        return jsonify({'error': 'File not available'}), 404
    filepath = os.path.join(os.path.dirname(__file__), allowed[filename])
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(data.get('content', ''))
        return jsonify({'status': 'ok', 'message': f'{filename} saved. Restart server to apply Python changes.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/code/unlock', methods=['POST'])
def unlock_code():
    data = request.json
    if data.get('password') == SERVICE_PASSWORD:
        return jsonify({'unlocked': True})
    return jsonify({'unlocked': False, 'error': 'Wrong password'}), 403


# ==================== Debug Log API ====================

@app.route('/api/debug/logs')
def get_debug_logs():
    """Read the debug log file for remote diagnostics."""
    data = request.args
    if data.get('password') != SERVICE_PASSWORD:
        return jsonify({'error': 'Unauthorized'}), 403
    try:
        if os.path.exists(DEBUG_LOG_FILE):
            with open(DEBUG_LOG_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            # Return last 200 lines max
            return jsonify({'logs': lines[-200:], 'total_lines': len(lines)})
        return jsonify({'logs': [], 'total_lines': 0})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/debug/logs/clear', methods=['POST'])
def clear_debug_logs():
    data = request.json or {}
    if data.get('password') != SERVICE_PASSWORD:
        return jsonify({'error': 'Unauthorized'}), 403
    try:
        with open(DEBUG_LOG_FILE, 'w', encoding='utf-8') as f:
            f.write('')
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== Global Error Handler ====================

@app.errorhandler(Exception)
def handle_exception(e):
    log_error('unhandled_exception', e, extra={'url': request.url, 'method': request.method})
    return jsonify({'error': 'Internal server error', 'message': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
