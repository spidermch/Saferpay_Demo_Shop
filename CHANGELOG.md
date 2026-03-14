# Changelog - Saferpay Explorer

## v3.0 (2026-03-14)

### Tab Restructure
- Consolidated 6 tabs into 3 main tabs: **Explorer**, **Merchant Admin**, **Dev**
- Merchant Admin contains sub-tabs: Items (product catalog), Customers (CRM), Orders (transactions & journey)
- Dev contains sub-tabs: Code (source viewer), Config (API credentials), Feature Audit

### Webshop Improvements
- Product cards in shopper view are now larger and more prominent with hover effects
- Customer section after cart: choose "New Customer" or "Select Existing" from CRM
- Full customer details form: Name, Email, Street Address, City, Postal Code, Country, Phone
- After order completion, webshop resets for next order (clears dev panel logs)

### Feature Audit (moved to Dev tab)
- Every non-implemented feature now shows **"How to enable"** with backoffice activation instructions
- Added **OmniChannel AcquireTransaction** - transfer POS transactions to e-commerce
- Added **OmniChannel InsertAlias** - store POS card data as alias for e-commerce
- Added **MOTO Transactions** - mail/phone order processing
- Activation notes cover license requirements, PCI compliance, and Saferpay Backoffice settings

### Technical
- Sub-tab navigation with automatic data loading on tab switch
- Old tab name mappings preserved for backward compatibility of internal calls

---

## v2.1 (2025-12)

### Features
- Added SpecVersion support up to 1.50 (2026-01 Latest)
- Added versions 1.45 through 1.50 to the API version selector

---

## v2.0 (2025-11)

### Features
- Added customer details step in checkout flow
- Added debug logging system for remote diagnostics
- Added management overview PDF documentation

---

## v1.0 (2025-10)

### Initial Release
- Saferpay Explorer SMB Merchant Demo
- Split-view: Shopper panel + Developer API debugger
- PaymentPage and Transaction Interface flows
- Product catalog management
- Customer CRM with notes and order history
- Order journey visualization
- Source code viewer with annotations
- Feature audit with API coverage tracking
