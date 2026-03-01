"""Generate Worldline Saferpay Explorer PDF Guides:
   1. Deployment Guide
   2. User Guide
Both with Worldline branding and version history.
"""

from fpdf import FPDF
import os

# ---- Brand Constants ----
WL_RED = (228, 0, 43)
WL_NAVY = (26, 31, 54)
WL_DARK = (30, 32, 40)
WL_GREY = (90, 95, 105)
WL_LIGHT = (245, 247, 250)
WL_WHITE = (255, 255, 255)
WL_GREEN = (16, 185, 129)
WL_AMBER = (180, 83, 9)

VERSION = "2.1.0"
DATE = "March 2026"


class WLGuide(FPDF):
    """Base PDF class with Worldline branding."""

    def __init__(self, title, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.doc_title = title
        self.set_auto_page_break(auto=True, margin=20)
        self.set_margins(20, 15, 20)

    def header(self):
        if self.page_no() == 1:
            return
        self._draw_logo_small(self.l_margin, 8)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(*WL_GREY)
        self.set_xy(self.l_margin + 50, 8)
        self.cell(0, 6, self.doc_title, align="L")
        self.cell(0, 6, f"Page {self.page_no()}", align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*WL_RED)
        self.line(self.l_margin, 16, self.w - self.r_margin, 16)
        self.ln(6)

    def footer(self):
        self.set_y(-14)
        self.set_font("Helvetica", "I", 6.5)
        self.set_text_color(*WL_GREY)
        self.cell(0, 8, f"Worldline  |  Saferpay Explorer v{VERSION}  |  Confidential", align="C")

    # ---- Logo Drawing ----
    def _draw_logo(self, x, y, scale=1.0):
        """Draw Worldline logo: red bar + WORLDLINE text."""
        bw = 5 * scale
        bh = 32 * scale
        self.set_fill_color(*WL_RED)
        self.rect(x, y, bw, bh, "F")
        self.set_font("Helvetica", "B", int(22 * scale))
        self.set_text_color(*WL_NAVY)
        self.set_xy(x + bw + 5 * scale, y + 8 * scale)
        self.cell(0, bh * 0.6, "WORLDLINE", new_x="LMARGIN", new_y="NEXT")

    def _draw_logo_small(self, x, y):
        self.set_fill_color(*WL_RED)
        self.rect(x, y, 2.5, 8, "F")
        self.set_font("Helvetica", "B", 7)
        self.set_text_color(*WL_NAVY)
        self.set_xy(x + 4, y + 1)
        self.cell(40, 6, "WORLDLINE")

    # ---- Cover Page ----
    def cover_page(self, subtitle, audience):
        self.add_page()
        # Red top bar
        self.set_fill_color(*WL_RED)
        self.rect(0, 0, self.w, 4, "F")
        # Logo
        self.ln(35)
        self._draw_logo(self.l_margin, self.get_y(), 1.3)
        self.ln(55)
        # Title
        self.set_font("Helvetica", "B", 30)
        self.set_text_color(*WL_NAVY)
        self.cell(0, 13, "Saferpay Explorer", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 16)
        self.set_text_color(*WL_GREY)
        self.cell(0, 10, subtitle, align="C", new_x="LMARGIN", new_y="NEXT")
        # Red line
        self.ln(4)
        self.set_draw_color(*WL_RED)
        self.set_line_width(0.8)
        self.line(65, self.get_y(), 145, self.get_y())
        self.set_line_width(0.2)
        self.ln(8)
        # Version
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*WL_DARK)
        self.cell(0, 7, f"Version {VERSION}  |  {DATE}", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(25)
        # Audience
        self.set_font("Helvetica", "", 8.5)
        self.set_text_color(*WL_GREY)
        self.cell(0, 6, audience, align="C", new_x="LMARGIN", new_y="NEXT")
        # Bottom bar
        self.set_fill_color(*WL_RED)
        self.rect(0, self.h - 4, self.w, 4, "F")

    # ---- Reusable Elements ----
    def section(self, num, title):
        self.ln(3)
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(*WL_NAVY)
        self.cell(0, 9, f"{num}.  {title}", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*WL_RED)
        self.line(self.l_margin, self.get_y(), self.l_margin + 50, self.get_y())
        self.ln(5)

    def sub(self, title):
        self.ln(1.5)
        self.set_font("Helvetica", "B", 10.5)
        self.set_text_color(*WL_DARK)
        self.cell(0, 6.5, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def txt(self, t):
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*WL_DARK)
        self.multi_cell(0, 5.2, t)
        self.ln(0.8)

    def code(self, lines):
        self.set_fill_color(*WL_LIGHT)
        self.set_font("Courier", "", 8.5)
        self.set_text_color(*WL_DARK)
        w = self.w - self.l_margin - self.r_margin
        for ln in lines:
            self.set_x(self.l_margin)
            self.cell(w, 5.5, f"  {ln}", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(2.5)

    def bullet(self, text, bold=""):
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*WL_DARK)
        self.set_x(self.get_x() + 3)
        self.cell(4, 5.2, "-")
        if bold:
            self.set_font("Helvetica", "B", 9.5)
            self.cell(self.get_string_width(bold) + 1, 5.2, bold)
            self.set_font("Helvetica", "", 9.5)
        self.multi_cell(0, 5.2, text)
        self.ln(0.4)

    def num(self, n, text):
        self.set_font("Helvetica", "B", 9.5)
        self.set_text_color(*WL_RED)
        self.set_x(self.get_x() + 2)
        self.cell(7, 5.5, f"{n}.")
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*WL_DARK)
        self.multi_cell(0, 5.5, text)
        self.ln(0.8)

    def tip(self, title, text):
        self.ln(1.5)
        self.set_fill_color(236, 253, 245)
        x0, w = self.l_margin, self.w - self.l_margin - self.r_margin
        y0 = self.get_y()
        self.set_font("Helvetica", "B", 8.5)
        self.set_text_color(*WL_GREEN)
        self.set_x(x0)
        self.cell(w, 5.5, f"  {title}", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 8.5)
        self.set_text_color(5, 80, 60)
        self.set_x(x0)
        self.multi_cell(w, 4.8, f"  {text}", fill=True)
        y1 = self.get_y()
        self.set_draw_color(*WL_GREEN)
        self.rect(x0, y0, w, y1 - y0)
        self.ln(3)

    def warn(self, title, text):
        self.ln(1.5)
        self.set_fill_color(255, 251, 235)
        x0, w = self.l_margin, self.w - self.l_margin - self.r_margin
        y0 = self.get_y()
        self.set_font("Helvetica", "B", 8.5)
        self.set_text_color(*WL_AMBER)
        self.set_x(x0)
        self.cell(w, 5.5, f"  {title}", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 8.5)
        self.set_text_color(120, 60, 0)
        self.set_x(x0)
        self.multi_cell(w, 4.8, f"  {text}", fill=True)
        y1 = self.get_y()
        self.set_draw_color(*WL_AMBER)
        self.rect(x0, y0, w, y1 - y0)
        self.ln(3)

    def page_check(self):
        if self.get_y() > 248:
            self.add_page()

    def toc_entry(self, num, title):
        self.set_font("Helvetica", "", 10.5)
        self.set_text_color(*WL_DARK)
        self.cell(8, 7, f"{num}.")
        self.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")

    def version_entry(self, ver, date, items):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*WL_NAVY)
        self.cell(0, 7, f"v{ver}  -  {date}", new_x="LMARGIN", new_y="NEXT")
        for it in items:
            self.bullet(it)
        self.ln(2)


# ============================================================
#  DEPLOYMENT GUIDE
# ============================================================
def build_deployment_guide():
    pdf = WLGuide("Saferpay Explorer - Deployment Guide", "P", "mm", "A4")
    pdf.cover_page("Deployment Guide", "For: Worldline colleagues - Sales, Operations, Developers, Merchants")

    # TOC
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 17)
    pdf.set_text_color(*WL_NAVY)
    pdf.cell(0, 11, "Table of Contents", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    for n, t in [("1","One-Click Start (Recommended)"),("2","Prerequisites (Developer Setup)"),("3","Check Your System"),("4","Get the Project Files"),
                  ("5","Run from Source"),("6","Deploy to Railway"),("7","Configure Saferpay Credentials"),
                  ("8","Test Card Numbers"),("9","Troubleshooting"),("10","Project File Overview"),("11","Version History")]:
        pdf.toc_entry(n, t)

    # 1 - One-Click Start
    pdf.add_page()
    pdf.section("1", "One-Click Start (Recommended)")
    pdf.txt("The fastest way to run Saferpay Explorer. No Python installation needed, no command line, no setup - just one double-click.")
    pdf.ln(2)
    pdf.sub("How to Start")
    pdf.num(1, "Locate the file Saferpay_Explorer.exe in the project folder")
    pdf.num(2, "Double-click it")
    pdf.num(3, "A console window opens showing 'Saferpay Explorer starting...'")
    pdf.num(4, "Your browser opens automatically at http://localhost:5000")
    pdf.num(5, "Done! Go to the Config tab and enter your Saferpay credentials.")
    pdf.ln(2)
    pdf.tip("ONE CLICK - THAT'S IT", "The .exe bundles Python, Flask, and all dependencies. Nothing else to install. Just double-click and go.")
    pdf.ln(2)
    pdf.sub("How to Stop")
    pdf.txt("Close the console window (the black terminal), or press CTRL+C in it.")
    pdf.sub("Windows SmartScreen Warning")
    pdf.txt("On first launch, Windows may show 'Windows protected your PC'. This is normal for unsigned executables. Click 'More info' and then 'Run anyway'.")
    pdf.sub("When to Use the .exe vs Python")
    pdf.bullet("Use the .exe for demos, presentations, quick access - no setup required", "Use .exe: ")
    pdf.bullet("Use Python if you want to modify the source code or deploy to a server", "Use Python: ")
    pdf.warn("NOTE", "The .exe runs on the machine where you double-click it. For cloud deployment (Railway), use the Python source method (Section 5-6).")

    # 2 - Prerequisites (Developer Setup)
    pdf.add_page()
    pdf.section("2", "Prerequisites (Developer Setup)")
    pdf.txt("Only needed if you want to run from source code or deploy to a server. Skip this if you use the .exe.")
    pdf.sub("Required Software")
    pdf.bullet("Python 3.9 or higher - https://www.python.org/downloads/", "Python 3.9+: ")
    pdf.txt('    IMPORTANT: Check "Add Python to PATH" during installation!')
    pdf.bullet("pip (comes with Python)", "pip: ")
    pdf.bullet("Git - https://git-scm.com/downloads", "Git: ")
    pdf.bullet("A web browser (Chrome, Edge, Firefox)", "Browser: ")
    pdf.sub("For Railway Deployment (Optional)")
    pdf.bullet("Railway account - https://railway.app", "Account: ")
    pdf.bullet("Railway CLI - details in Section 6", "CLI: ")
    pdf.sub("For Saferpay API Access")
    pdf.bullet("Saferpay test credentials (Customer ID, Terminal ID, API Username, Password)", "Credentials: ")
    pdf.bullet("Saferpay Backoffice: https://test.saferpay.com/BO", "Backoffice: ")
    pdf.tip("TIP", "You can explore the UI without credentials. The Config tab will prompt when needed.")

    # 3
    pdf.add_page()
    pdf.section("3", "Check Your System")
    pdf.txt("Open CMD or PowerShell and verify:")
    pdf.sub("Python")
    pdf.code(["python --version", "# Expected: Python 3.9+ (e.g. Python 3.12.8)"])
    pdf.sub("pip")
    pdf.code(["pip --version", "# If not found: python -m pip --version"])
    pdf.sub("Git")
    pdf.code(["git --version"])
    pdf.sub("Network")
    pdf.code(["curl https://test.saferpay.com/api --head"])
    pdf.warn("CORPORATE PROXY", "Set HTTPS_PROXY and HTTP_PROXY env vars if behind a proxy.")

    # 4
    pdf.section("4", "Get the Project Files")
    pdf.txt("Only needed if running from source. If using the .exe, skip to Section 7.")
    pdf.sub("Option A: Git Clone")
    pdf.code(["git clone <REPOSITORY_URL>", "cd Saferpay_Demo_Shop"])
    pdf.sub("Option B: Copy Folder")
    pdf.num(1, "Extract ZIP to e.g. C:\\Projects\\Saferpay_Demo_Shop")
    pdf.num(2, "cd C:\\Projects\\Saferpay_Demo_Shop")
    pdf.sub("Verify Structure")
    pdf.code(["Saferpay_Explorer.exe   <-- One-click start!", "app.py  requirements.txt  Procfile  runtime.txt", "templates/  static/  generate_guides.py"])

    # 5
    pdf.add_page()
    pdf.section("5", "Run from Source (Developer Method)")
    pdf.txt("Alternative to the .exe. Use this if you want to modify the code or need a custom setup.")
    pdf.sub("Step 1: Virtual Environment")
    pdf.code(["python -m venv venv", "venv\\Scripts\\activate        # Windows CMD", "source venv/bin/activate     # macOS/Linux"])
    pdf.sub("Step 2: Install Dependencies")
    pdf.code(["pip install -r requirements.txt"])
    pdf.sub("Step 3: Start the App")
    pdf.code(["python app.py", "# Running on http://127.0.0.1:5000"])
    pdf.sub("Step 4: Open Browser")
    pdf.code(["http://localhost:5000"])
    pdf.tip("TIP", "Press CTRL+C to stop. Run 'python app.py' to restart.")

    # 6
    pdf.add_page()
    pdf.section("6", "Deploy to Railway")
    pdf.txt("Railway is a cloud platform. The app includes Procfile + runtime.txt for auto-detection.")
    pdf.sub("CLI Method")
    pdf.num(1, "Sign up at https://railway.app")
    pdf.num(2, "Install CLI: npm install -g @railway/cli")
    pdf.num(3, "railway login")
    pdf.num(4, "cd Saferpay_Demo_Shop && railway init")
    pdf.num(5, "railway variables set SECRET_KEY=your-random-key")
    pdf.num(6, "railway up")
    pdf.num(7, "railway open")
    pdf.sub("Dashboard Method (No CLI)")
    pdf.num(1, "Push to GitHub")
    pdf.num(2, "railway.app > New Project > Deploy from GitHub")
    pdf.num(3, "Add SECRET_KEY in Variables tab")
    pdf.num(4, "Settings > Networking > Generate Domain")
    pdf.tip("TIP", "GitHub pushes trigger automatic redeployment.")

    # 7
    pdf.page_check()
    pdf.section("7", "Configure Saferpay Credentials")
    pdf.txt("Open the app > Config tab. Enter:")
    pdf.bullet("Customer ID - Your numeric account ID", "Customer ID: ")
    pdf.bullet("Terminal ID - From Settings > Terminals", "Terminal ID: ")
    pdf.bullet("API Username - Format: API_XXXXXX_XXXXXXXX", "Username: ")
    pdf.bullet("API Password - Shown once on creation", "Password: ")
    pdf.warn("NOTE", "Credentials stored in browser session only. Re-enter after restart.")

    # 8
    pdf.section("8", "Test Card Numbers")
    for brand, num in [("Visa","9010 1000 0000 0001 11"),("Mastercard","9030 1000 0000 0001 30"),
                        ("American Express","9070 1000 0000 0007 43"),("Diners","9050 1000 0000 0005 17"),("JCB","9060 1000 0000 0006 26")]:
        pdf.set_font("Helvetica", "B", 9.5)
        pdf.set_text_color(*WL_DARK)
        pdf.cell(38, 5.5, f"  {brand}")
        pdf.set_font("Courier", "", 9.5)
        pdf.cell(0, 5.5, num, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.txt("Expiry: any future date | CVC: any 3 digits | 3DS: submit or 'password'")

    # 9
    pdf.add_page()
    pdf.section("9", "Troubleshooting")
    pdf.sub("'python' not recognized")
    pdf.txt("Reinstall Python with 'Add to PATH' checked.")
    pdf.sub("pip SSL/proxy errors")
    pdf.code(["pip install -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org"])
    pdf.sub("Port 5000 in use")
    pdf.code(["set PORT=8080 && python app.py"])
    pdf.sub("Popup blocked")
    pdf.txt("Allow popups for localhost. Fallback link is shown in the UI.")
    pdf.sub("401 Unauthorized from Saferpay")
    pdf.txt("Check username/password in Config tab. Ensure correct environment (test vs prod).")

    # 10
    pdf.section("10", "Project File Overview")
    for f, d in [("Saferpay_Explorer.exe","One-click launcher - double-click to start!"),
                  ("app.py","Flask backend: routes, payment logic, CRM, products, code viewer"),
                  ("run.py","Launcher script used by the .exe (auto-opens browser)"),
                  ("requirements.txt","Dependencies: Flask, requests, gunicorn"),
                  ("Procfile","Railway start command (gunicorn)"),
                  ("templates/index.html","SPA with 6 tabs: Explorer, Products, Orders, Customers, Code, Config"),
                  ("static/js/app.js","Client logic: cart, payments, CRM, code viewer"),
                  ("static/css/style.css","Styling: responsive layout, dark dev console"),
                  ("static/img/","Worldline logo assets"),
                  ("generate_guides.py","PDF guide generator script")]:
        pdf.set_font("Courier", "B", 8.5)
        pdf.set_text_color(*WL_RED)
        pdf.cell(42, 5.5, f)
        pdf.set_font("Helvetica", "", 8.5)
        pdf.set_text_color(*WL_DARK)
        pdf.multi_cell(0, 5.5, d)
        pdf.ln(0.5)

    # 11
    pdf.add_page()
    pdf.section("11", "Version History")
    pdf.version_entry("1.0.0", "March 2026", [
        "Initial release: Explorer split-view (Shopper + Developer)",
        "PaymentPage flow: Initialize, Assert, Capture",
        "Configuration tab with credential management",
        "Merchant dashboard with transaction table",
        "Railway deployment support (Procfile, runtime.txt)",
    ])
    pdf.version_entry("2.0.0", "March 2026", [
        "Product catalog management (add, edit, delete, icon picker)",
        "Customer CRM (contacts, notes, search, lifetime value)",
        "Transaction Interface flow (Initialize, Authorize, Capture)",
        "Orders tab with dashboard stats and flow tagging",
        "Customer linking at checkout",
        "Code viewer with 45 educational annotations",
        "Password-protected edit mode (service code: ask admin)",
    ])
    pdf.version_entry("2.1.0", "March 2026", [
        "Worldline branding: logo in app header and PDF guides",
        "Comprehensive User Guide PDF (this document)",
        "Updated Deployment Guide PDF with branding",
        "Version history tracking for all releases",
    ])
    pdf.sub("Planned")
    pdf.bullet("Recurring/subscription payment demo")
    pdf.bullet("Refund/Cancel transaction flow")
    pdf.bullet("Secure Fields (iframe card input) integration")
    pdf.bullet("Multi-currency support and conversion display")
    pdf.bullet("Webhook/notification handling demo")
    pdf.bullet("PDF invoice generation per order")

    pdf.output("Saferpay_Explorer_Deployment_Guide.pdf")
    print("  -> Saferpay_Explorer_Deployment_Guide.pdf")


# ============================================================
#  USER GUIDE
# ============================================================
def build_user_guide():
    pdf = WLGuide("Saferpay Explorer - User Guide", "P", "mm", "A4")
    pdf.cover_page("User Guide", "For: Worldline Sales, Operations, Developers, Technical Merchants")

    # TOC
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 17)
    pdf.set_text_color(*WL_NAVY)
    pdf.cell(0, 11, "Table of Contents", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    for n, t in [("1","Introduction"),("2","Quick Start"),("3","Explorer Tab"),
                  ("4","Products Tab"),("5","Orders Tab"),("6","Customers (CRM) Tab"),
                  ("7","Code Tab"),("8","Configuration Tab"),
                  ("9","Payment Flows Explained"),("10","API Reference"),
                  ("11","Test Cards"),("12","Version History")]:
        pdf.toc_entry(n, t)

    # 1 - Introduction
    pdf.add_page()
    pdf.section("1", "Introduction")
    pdf.sub("What is Saferpay Explorer?")
    pdf.txt("Saferpay Explorer is an educational demo web application that visualizes the Worldline Saferpay JSON API payment flow from multiple perspectives simultaneously. It combines a demo webshop, live API debugger, merchant dashboard, customer CRM, and annotated source code viewer in one interactive tool.")
    pdf.sub("Who is it for?")
    pdf.bullet("Sales teams - demonstrate Saferpay to prospects in live meetings")
    pdf.bullet("Operations teams - understand the payment flow end-to-end")
    pdf.bullet("Developers - learn the API with real requests/responses and annotated code")
    pdf.bullet("Merchants - see what happens behind the scenes when a customer pays")
    pdf.sub("Key Features")
    pdf.bullet("Split-screen: Shopper view + Developer API console side by side")
    pdf.bullet("Two payment flows: PaymentPage (simple) and Transaction Interface (advanced)")
    pdf.bullet("Product catalog management with add/edit/delete")
    pdf.bullet("Customer CRM with notes, search, and order history")
    pdf.bullet("Annotated source code viewer for learning")
    pdf.bullet("Real Saferpay test environment integration")
    pdf.bullet("Mobile-responsive, presentation-ready UI")
    pdf.sub("Architecture")
    pdf.txt("Backend: Python Flask | Frontend: Vanilla JavaScript (no frameworks) | Deployment: Railway-ready | API: Saferpay JSON API v1.33")

    # 2 - Quick Start
    pdf.add_page()
    pdf.section("2", "Quick Start")
    pdf.txt("Get up and running in 5 steps:")
    pdf.ln(2)
    pdf.num(1, "Open the app in your browser (http://localhost:5000 or your Railway URL)")
    pdf.num(2, "Go to the Config tab and enter your Saferpay test credentials")
    pdf.num(3, "Switch to the Explorer tab - you'll see the shop on the left, API console on the right")
    pdf.num(4, "Add products to the cart and click 'Pay Now'")
    pdf.num(5, "Complete payment with a test card and watch the API flow in real-time!")
    pdf.ln(4)
    pdf.tip("FIRST TIME?", "If you don't have credentials yet, you can still browse the UI. The app will prompt you to configure credentials when you try to make a payment.")
    pdf.ln(2)
    pdf.sub("Navigation")
    pdf.txt("The app has 6 main tabs in the top navigation bar:")
    pdf.ln(1)
    pdf.bullet("The payment flow visualizer with split-screen", "Explorer: ")
    pdf.bullet("Manage your product catalog", "Products: ")
    pdf.bullet("View transactions, stats, and capture payments", "Orders: ")
    pdf.bullet("Customer relationship management", "Customers: ")
    pdf.bullet("View annotated source code", "Code: ")
    pdf.bullet("API credentials and environment settings", "Config: ")

    # 3 - Explorer
    pdf.add_page()
    pdf.section("3", "Explorer Tab")
    pdf.txt("The Explorer is the heart of Saferpay Explorer. It shows the customer journey (left) and the technical API flow (right) simultaneously.")
    pdf.sub("Shopper View (Left Panel)")
    pdf.txt("This simulates what a customer sees on a merchant's webshop:")
    pdf.num(1, "BROWSE: View the product catalog with prices. Click 'Add to Cart' to build your order.")
    pdf.num(2, "CART: Review items, remove unwanted ones. Select a customer from CRM (optional) and choose a payment integration method.")
    pdf.num(3, "PAYMENT: Click 'Pay Now'. A popup opens with the Saferpay payment page. Enter a test card number.")
    pdf.num(4, "RESULT: See whether the payment was authorized. Optionally capture it.")
    pdf.sub("Developer View (Right Panel)")
    pdf.txt("Shows every API call in real-time as it happens:")
    pdf.bullet("Each call shows: HTTP method, endpoint URL, status code, timestamp")
    pdf.bullet("Click any entry to expand and see the full JSON request and response")
    pdf.bullet("Educational annotations explain what each API call does and why")
    pdf.bullet("Color-coded: blue = PaymentPage, pink = Transaction, green = Capture")
    pdf.sub("Flow Indicator")
    pdf.txt("The progress bar at the top of the shopper view shows where you are in the flow: Browse > Cart > Initialize > Payment Page > Assert/Authorize > Capture")
    pdf.sub("Split Handle")
    pdf.txt("Drag the divider between panels to resize them. Useful when presenting or when you want more space for the JSON output.")
    pdf.sub("Payment Integration Choice")
    pdf.txt("At checkout, you choose between two Saferpay integration methods:")
    pdf.bullet("All-in-one redirect. Saferpay shows all enabled payment methods. Simplest integration. Uses PaymentPage/Initialize + PaymentPage/Assert.", "Payment Page: ")
    pdf.bullet("More merchant control. Supports Secure Fields, payment method preselection, and customer data injection. Uses Transaction/Initialize + Transaction/Authorize.", "Transaction Interface: ")

    # 4 - Products
    pdf.add_page()
    pdf.section("4", "Products Tab")
    pdf.txt("Manage the product catalog that appears in the shop. The app starts with 4 demo products (Swiss-themed) but you can customize freely.")
    pdf.sub("Adding a Product")
    pdf.num(1, "Click '+ Add Product' button")
    pdf.num(2, "Enter the product name (required) and price in CHF")
    pdf.num(3, "Add an optional description")
    pdf.num(4, "Pick an icon from the icon grid (20 options)")
    pdf.num(5, "Click 'Add Product'")
    pdf.sub("Editing a Product")
    pdf.txt("Click the pencil icon on any product card. The form pre-fills with the current values. Make changes and click 'Save Changes'.")
    pdf.sub("Deactivating / Deleting")
    pdf.bullet("X icon: Deactivates the product (hidden from shop, can reactivate later)")
    pdf.bullet("Trash icon: Permanently deletes the product")
    pdf.tip("TIP", "Deactivate seasonal products instead of deleting them - you can reactivate them later without re-entering all the details.")

    # 5 - Orders
    pdf.add_page()
    pdf.section("5", "Orders Tab")
    pdf.txt("The merchant's view of all transactions processed through the shop.")
    pdf.sub("Dashboard Stats")
    pdf.txt("Four metric cards at the top show:")
    pdf.bullet("Total number of payment attempts", "Total Orders: ")
    pdf.bullet("Sum of all transaction amounts", "Total Volume: ")
    pdf.bullet("Payments approved but not yet settled", "Authorized: ")
    pdf.bullet("Payments settled (money will transfer)", "Captured: ")
    pdf.sub("Transaction Table")
    pdf.txt("Shows all transactions with: Order ID, customer name, amount, status badge, integration flow (PP or TXN), payment method, time, and action buttons.")
    pdf.sub("Capturing Payments")
    pdf.txt("Authorized transactions show a green 'Capture' button. Clicking it sends Transaction/Capture to Saferpay, settling the payment. The status changes from AUTHORIZED to CAPTURED.")
    pdf.sub("Status Colors")
    pdf.bullet("Blue - Payment session created, customer hasn't completed yet", "INITIALIZED: ")
    pdf.bullet("Amber - Payment approved, money reserved on card", "AUTHORIZED: ")
    pdf.bullet("Green - Payment settled, money will transfer to merchant", "CAPTURED: ")
    pdf.bullet("Red - Payment cancelled, declined, or error occurred", "FAILED: ")

    # 6 - Customers
    pdf.add_page()
    pdf.section("6", "Customers (CRM) Tab")
    pdf.txt("A lightweight CRM for managing customer relationships. Customers can be linked to orders for tracking and reporting.")
    pdf.sub("Customer List")
    pdf.txt("Shows all customers as cards with name, company, order count, and lifetime spend. Use the search bar to filter by name, email, or company.")
    pdf.sub("Adding a Customer")
    pdf.num(1, "Click '+ Add Customer'")
    pdf.num(2, "Enter name (required), email, company, phone, address")
    pdf.num(3, "Click 'Add Customer'")
    pdf.sub("Customer Detail View")
    pdf.txt("Click any customer card to see their full profile:")
    pdf.bullet("Contact information (email, company, phone, address)")
    pdf.bullet("Order count and lifetime value")
    pdf.bullet("Notes section - add timestamped notes about the customer")
    pdf.bullet("Full order history with status and payment flow")
    pdf.sub("Notes")
    pdf.txt("Notes are useful for tracking interactions: 'VIP customer - always offer express checkout', 'Prefers invoice payment', 'Contacted about recurring billing', etc.")
    pdf.sub("Linking to Orders")
    pdf.txt("When checking out in the Explorer, select a customer from the dropdown. The order will be linked to that customer, and their order count/lifetime value updates automatically.")

    # 7 - Code
    pdf.add_page()
    pdf.section("7", "Code Tab")
    pdf.txt("View the actual application source code with educational annotations. Perfect for developers who want to understand how the Saferpay integration works.")
    pdf.sub("File Selection")
    pdf.txt("Four files are available: app.py (backend), app.js (frontend), style.css (styling), index.html (template). Click any file tab to load it.")
    pdf.sub("Annotations")
    pdf.txt("Key lines are highlighted with a purple background. Click any highlighted line to reveal an explanation of what that code does and why it matters for the payment integration.")
    pdf.txt("There are 45 annotations across the codebase covering: session management, API authentication, payment flows, security considerations, and architectural decisions.")
    pdf.sub("Line Highlighting")
    pdf.bullet("Purple background = annotated line (click for explanation)")
    pdf.bullet("Blue left border = API route/endpoint definition")
    pdf.bullet("Green left border = Saferpay API interaction")
    pdf.sub("Edit Mode")
    pdf.txt("By default, code is read-only. To enable editing:")
    pdf.num(1, "Click 'Unlock Edit' button")
    pdf.num(2, "Enter the service password")
    pdf.num(3, "Code switches to an editable text area")
    pdf.num(4, "Click 'Save Changes' (re-confirms password)")
    pdf.warn("IMPORTANT", "Code editing is restricted to authorized service personnel. The password is not shared in this guide - contact your team lead. Python changes require a server restart.")

    # 8 - Config
    pdf.add_page()
    pdf.section("8", "Configuration Tab")
    pdf.txt("Set up your Saferpay JSON API credentials to connect to the test (or production) environment.")
    pdf.sub("Required Fields")
    pdf.bullet("Your numeric Saferpay account identifier", "Customer ID: ")
    pdf.bullet("The terminal that processes payments", "Terminal ID: ")
    pdf.bullet("JSON API username (format: API_XXXXXX_XXXXXXXX)", "API Username: ")
    pdf.bullet("JSON API password (shown once when created)", "API Password: ")
    pdf.sub("Environment")
    pdf.txt("Select Test or Production from the Base URL dropdown. Always use Test for demos and development.")
    pdf.sub("Connection Status")
    pdf.txt("The header shows a green 'Connected' badge when configured, or red 'Not configured' when credentials are missing. A yellow banner at the top also prompts setup.")
    pdf.warn("SESSION STORAGE", "Credentials are stored in your browser session cookie. They are NOT saved permanently on the server. You'll need to re-enter them after clearing cookies or restarting.")

    # 9 - Payment Flows
    pdf.add_page()
    pdf.section("9", "Payment Flows Explained")
    pdf.sub("Flow 1: Payment Page")
    pdf.txt("The simplest Saferpay integration. Recommended for most merchants.")
    pdf.ln(1)
    pdf.num(1, "INITIALIZE: Merchant sends PaymentPage/Initialize with amount, currency, order ID, and return URLs. Saferpay returns a Token and RedirectUrl.")
    pdf.num(2, "REDIRECT: Customer's browser opens the Saferpay-hosted payment page. They see all enabled payment methods and enter card details. Card data stays on Saferpay's PCI-certified servers.")
    pdf.num(3, "RETURN: After payment, customer is redirected back to the merchant's ReturnUrl (success) or Abort URL (cancel).")
    pdf.num(4, "ASSERT: Merchant calls PaymentPage/Assert with the Token to verify the result. Returns TransactionId, payment means, liability shift info.")
    pdf.num(5, "CAPTURE: Merchant calls Transaction/Capture with the TransactionId to settle the payment. Money transfers from customer to merchant.")
    pdf.ln(2)
    pdf.sub("Flow 2: Transaction Interface")
    pdf.txt("More control for the merchant. Supports Secure Fields and payment method preselection.")
    pdf.ln(1)
    pdf.num(1, "INITIALIZE: Merchant sends Transaction/Initialize. Can include Payer data (name, email). Returns Token and RedirectUrl.")
    pdf.num(2, "REDIRECT: Same as Payment Page - customer completes payment on Saferpay.")
    pdf.num(3, "RETURN: Customer returns to the single ReturnUrl (no separate abort URL).")
    pdf.num(4, "AUTHORIZE: Merchant calls Transaction/Authorize (instead of Assert). Same result data.")
    pdf.num(5, "CAPTURE: Same as PaymentPage - Transaction/Capture settles the payment.")
    pdf.ln(2)
    pdf.sub("Key Differences")
    pdf.txt("PaymentPage is simpler (2 URLs vs 1, auto payment method display). Transaction gives more control (Payer data, Secure Fields, specific payment methods). Both end with the same Capture call.")
    pdf.tip("EDUCATIONAL NOTE", "In the Developer View, PaymentPage calls are labeled 'PP Initialize' / 'PP Assert' and Transaction calls are labeled 'TXN Initialize' / 'TXN Authorize'. The Capture step is shared.")

    # 10 - API Reference
    pdf.add_page()
    pdf.section("10", "API Reference")
    pdf.txt("All internal API endpoints used by the application:")
    pdf.ln(2)
    endpoints = [
        ("POST /api/config", "Save API credentials to session"),
        ("GET /api/config/status", "Check if credentials are configured"),
        ("GET /api/products", "List all products"),
        ("POST /api/products", "Add a new product"),
        ("PUT /api/products/<id>", "Update a product"),
        ("DELETE /api/products/<id>", "Delete a product"),
        ("GET /api/customers", "List all customers with stats"),
        ("POST /api/customers", "Add a new customer"),
        ("PUT /api/customers/<id>", "Update customer details"),
        ("DELETE /api/customers/<id>", "Delete a customer"),
        ("POST /api/customers/<id>/notes", "Add a note to a customer"),
        ("GET /api/customers/<id>/orders", "Get customer's order history"),
        ("POST /api/initialize", "PaymentPage/Initialize"),
        ("POST /api/assert", "PaymentPage/Assert"),
        ("POST /api/transaction/initialize", "Transaction/Initialize"),
        ("POST /api/transaction/authorize", "Transaction/Authorize"),
        ("POST /api/capture", "Transaction/Capture (shared)"),
        ("GET /api/transactions", "List all transactions"),
        ("GET /api/code/<file>", "Get annotated source code"),
        ("POST /api/code/unlock", "Verify service password"),
    ]
    for ep, desc in endpoints:
        pdf.set_font("Courier", "B", 8)
        pdf.set_text_color(*WL_RED)
        pdf.cell(56, 5.2, ep)
        pdf.set_font("Helvetica", "", 8.5)
        pdf.set_text_color(*WL_DARK)
        pdf.cell(0, 5.2, desc, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(0.3)

    # 11 - Test Cards
    pdf.page_check()
    pdf.section("11", "Test Card Numbers")
    for brand, num in [("Visa","9010 1000 0000 0001 11"),("Mastercard","9030 1000 0000 0001 30"),
                        ("American Express","9070 1000 0000 0007 43"),("Diners Club","9050 1000 0000 0005 17"),
                        ("JCB","9060 1000 0000 0006 26")]:
        pdf.set_font("Helvetica", "B", 9.5)
        pdf.set_text_color(*WL_DARK)
        pdf.cell(38, 5.5, f"  {brand}")
        pdf.set_font("Courier", "", 9.5)
        pdf.cell(0, 5.5, num, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.txt("Expiry: any future date (e.g. 12/2030)  |  CVC: any 3 digits  |  3DS: 'password'")

    # 12 - Version History
    pdf.add_page()
    pdf.section("12", "Version History")
    pdf.version_entry("1.0.0", "March 2026", [
        "Initial release with Explorer split-view",
        "PaymentPage flow (Initialize, Assert, Capture)",
        "Configuration tab with credential management",
        "Merchant dashboard with transaction table",
        "Railway deployment support",
    ])
    pdf.version_entry("2.0.0", "March 2026", [
        "Product catalog management (CRUD + icon picker)",
        "Customer CRM (contacts, notes, search, lifetime value)",
        "Transaction Interface flow as alternative to PaymentPage",
        "Enhanced Orders tab with stats and flow tagging",
        "Customer linking at checkout with Payer data forwarding",
        "Code viewer with 45 educational annotations",
        "Password-protected edit mode for service personnel",
    ])
    pdf.version_entry("2.1.0", "March 2026", [
        "Worldline branding in app header (logo, divider, version)",
        "Comprehensive User Guide PDF (this document)",
        "Updated Deployment Guide PDF with Worldline branding",
        "Version history tracking in both PDFs and app",
    ])
    pdf.sub("Roadmap")
    pdf.bullet("Refund (Transaction/Refund) and Cancel (Transaction/Cancel) flows")
    pdf.bullet("Recurring/subscription payment demo")
    pdf.bullet("Secure Fields integration (iframe card input)")
    pdf.bullet("Multi-currency and dynamic currency conversion")
    pdf.bullet("Webhook/notification endpoint demo")
    pdf.bullet("PDF invoice generation per order")
    pdf.bullet("Batch capture for multiple transactions")
    pdf.bullet("Dashboard analytics with charts")

    # Final page
    pdf.add_page()
    pdf.ln(25)
    pdf._draw_logo(60, pdf.get_y(), 1.2)
    pdf.ln(50)
    pdf.set_font("Helvetica", "B", 17)
    pdf.set_text_color(*WL_NAVY)
    pdf.cell(0, 11, "You're All Set!", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(*WL_DARK)
    for i, step in enumerate([
        "Open the app and go to Config tab",
        "Enter your Saferpay test credentials",
        "Switch to Explorer and add products to cart",
        "Choose PaymentPage or Transaction at checkout",
        "Pay with a test card and watch the API flow",
        "Explore Orders, Customers, and Code tabs",
    ], 1):
        pdf.cell(0, 7.5, f"     {i}.  {step}", align="L", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    pdf.set_draw_color(*WL_RED)
    pdf.set_line_width(0.6)
    pdf.line(65, pdf.get_y(), 145, pdf.get_y())
    pdf.set_line_width(0.2)
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(*WL_GREY)
    pdf.cell(0, 6, f"Saferpay Explorer v{VERSION}  |  Built for Worldline  |  {DATE}", align="C")

    pdf.output("Saferpay_Explorer_User_Guide.pdf")
    print("  -> Saferpay_Explorer_User_Guide.pdf")


if __name__ == "__main__":
    print("Generating Worldline Saferpay Explorer guides...")
    build_deployment_guide()
    build_user_guide()
    print("Done!")
