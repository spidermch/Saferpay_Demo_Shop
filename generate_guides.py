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

VERSION = "3.0.0"
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

    def step(self, icon, tool, action, expect):
        """Render a step with icon, tool, action, expected result."""
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*WL_RED)
        self.set_x(self.l_margin)
        self.cell(8, 6, icon)
        self.set_font("Helvetica", "B", 9.5)
        self.set_text_color(*WL_NAVY)
        self.cell(self.get_string_width(tool) + 2, 6, tool)
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*WL_DARK)
        self.multi_cell(0, 6, f"  {action}")
        # Expected result
        self.set_fill_color(240, 249, 255)
        w = self.w - self.l_margin - self.r_margin
        self.set_x(self.l_margin + 8)
        self.set_font("Helvetica", "I", 8.5)
        self.set_text_color(*WL_GREEN)
        self.cell(w - 8, 5, f"  >> You see: {expect}", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*WL_DARK)
        self.ln(2.5)


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
    for n, t in [
        ("1", "Quick Overview: 3 Ways to Run"),
        ("2", "Method A: One-Click .exe (Easiest)"),
        ("3", "Method B: Download from GitHub"),
        ("4", "Method C: Run from Source Code"),
        ("5", "Method D: Deploy to Railway (Cloud)"),
        ("6", "Configure Saferpay Credentials"),
        ("7", "Your First Payment (Step by Step)"),
        ("8", "Test Card Numbers"),
        ("9", "Troubleshooting"),
        ("10", "Project File Overview"),
        ("11", "Version History"),
    ]:
        pdf.toc_entry(n, t)

    # ============ 1 - Quick Overview ============
    pdf.add_page()
    pdf.section("1", "Quick Overview: 3 Ways to Run")
    pdf.txt("Choose the method that fits your situation. All three get you the same app.")
    pdf.ln(3)

    # Method A box
    pdf.set_fill_color(236, 253, 245)
    x0, w = pdf.l_margin, pdf.w - pdf.l_margin - pdf.r_margin
    y0 = pdf.get_y()
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*WL_GREEN)
    pdf.set_x(x0)
    pdf.cell(w, 7, "  [A]  ONE-CLICK .EXE  --  Best for: demos, presentations, quick access", fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(5, 80, 60)
    pdf.set_x(x0)
    pdf.cell(w, 5.5, "  Double-click Saferpay_Explorer.exe. Done. No install, no terminal, nothing.", fill=True, new_x="LMARGIN", new_y="NEXT")
    y1 = pdf.get_y()
    pdf.set_draw_color(*WL_GREEN)
    pdf.rect(x0, y0, w, y1 - y0)
    pdf.ln(4)

    # Method B box
    pdf.set_fill_color(*WL_LIGHT)
    y0 = pdf.get_y()
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*WL_NAVY)
    pdf.set_x(x0)
    pdf.cell(w, 7, "  [B]  GITHUB DOWNLOAD  --  Best for: getting the latest version", fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*WL_DARK)
    pdf.set_x(x0)
    pdf.cell(w, 5.5, "  Go to GitHub, download the .exe or the source code ZIP. Takes 2 minutes.", fill=True, new_x="LMARGIN", new_y="NEXT")
    y1 = pdf.get_y()
    pdf.set_draw_color(*WL_NAVY)
    pdf.rect(x0, y0, w, y1 - y0)
    pdf.ln(4)

    # Method C box
    pdf.set_fill_color(*WL_LIGHT)
    y0 = pdf.get_y()
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*WL_GREY)
    pdf.set_x(x0)
    pdf.cell(w, 7, "  [C]  PYTHON SOURCE  --  Best for: developers who want to modify code", fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*WL_DARK)
    pdf.set_x(x0)
    pdf.cell(w, 5.5, "  Needs Python installed. Clone repo, pip install, python app.py.", fill=True, new_x="LMARGIN", new_y="NEXT")
    y1 = pdf.get_y()
    pdf.set_draw_color(*WL_GREY)
    pdf.rect(x0, y0, w, y1 - y0)
    pdf.ln(4)

    # Method D box
    pdf.set_fill_color(255, 251, 235)
    y0 = pdf.get_y()
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*WL_AMBER)
    pdf.set_x(x0)
    pdf.cell(w, 7, "  [D]  RAILWAY CLOUD  --  Best for: sharing a URL with colleagues", fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(120, 60, 0)
    pdf.set_x(x0)
    pdf.cell(w, 5.5, "  Deploy to railway.app. Get a public URL anyone can access.", fill=True, new_x="LMARGIN", new_y="NEXT")
    y1 = pdf.get_y()
    pdf.set_draw_color(*WL_AMBER)
    pdf.rect(x0, y0, w, y1 - y0)
    pdf.ln(5)

    pdf.txt("Not sure? Start with Method A (one-click .exe). You can always switch later.")

    # ============ 2 - Method A: One-Click .exe ============
    pdf.add_page()
    pdf.section("2", "Method A: One-Click .exe (Easiest)")
    pdf.txt("Zero setup. No Python, no terminal, no commands. Just a double-click.")
    pdf.ln(2)
    pdf.sub("What You Need")
    pdf.bullet("Windows 10 or 11")
    pdf.bullet("The file: Saferpay_Explorer.exe (13 MB)")
    pdf.bullet("A web browser (Chrome, Edge, Firefox - already on your PC)")
    pdf.ln(2)
    pdf.sub("Step-by-Step")
    pdf.step(">>", "[File Explorer]", "Find Saferpay_Explorer.exe in your project folder",
             "A file called Saferpay_Explorer.exe (13 MB)")
    pdf.step(">>", "[Double-Click]", "Double-click the .exe file",
             "A black console window opens with text")
    pdf.step(">>", "[Console]", "Wait 2 seconds. The console shows 'Saferpay Explorer starting...'",
             "Your default browser opens automatically")
    pdf.step(">>", "[Browser]", "The app is running! You see the Saferpay Explorer with 3 main tabs",
             "The app at http://localhost:5000 with the Explorer tab active")
    pdf.ln(1)
    pdf.tip("THAT'S IT!", "4 steps. You're done. Go to Section 6 to configure your Saferpay credentials.")
    pdf.ln(2)
    pdf.sub("How to Stop the App")
    pdf.step(">>", "[Console]", "Click the X on the black console window, or press CTRL+C",
             "The console closes. The app stops. Browser shows 'page not available'.")
    pdf.ln(1)
    pdf.sub("Windows SmartScreen Warning (First Launch Only)")
    pdf.txt("Windows may show: 'Windows protected your PC' - this happens for all unsigned .exe files.")
    pdf.step(">>", "[SmartScreen]", "Click 'More info' (blue link), then click 'Run anyway'",
             "The app starts normally. This warning won't appear again.")

    # ============ 3 - Method B: GitHub Download ============
    pdf.add_page()
    pdf.section("3", "Method B: Download from GitHub")
    pdf.txt("Get the latest version from GitHub. Two options: download just the .exe, or download everything.")
    pdf.ln(2)
    pdf.sub("Option 1: Download Just the .exe (Fastest)")
    pdf.step(">>", "[Browser]", "Open: https://github.com/spidermch/Saferpay_Demo_Shop/releases",
             "A page showing 'Saferpay Explorer v3.0.0' with release notes")
    pdf.step(">>", "[Browser]", "Scroll down to 'Assets'. Click 'Saferpay_Explorer.exe'",
             "Download starts (13 MB). Wait for it to finish.")
    pdf.step(">>", "[File Explorer]", "Go to your Downloads folder. Find Saferpay_Explorer.exe",
             "The file Saferpay_Explorer.exe in your Downloads")
    pdf.step(">>", "[Double-Click]", "Double-click the .exe file (same as Method A from here)",
             "Console opens, then browser opens at http://localhost:5000")
    pdf.ln(2)
    pdf.sub("Option 2: Download Full Source Code (ZIP)")
    pdf.step(">>", "[Browser]", "Open: https://github.com/spidermch/Saferpay_Demo_Shop",
             "The GitHub repository page with file listing")
    pdf.step(">>", "[Browser]", "Click the green '<> Code' button (top right of file list)",
             "A dropdown menu appears")
    pdf.step(">>", "[Browser]", "Click 'Download ZIP'",
             "A file Saferpay_Demo_Shop-master.zip downloads")
    pdf.step(">>", "[File Explorer]", "Right-click the ZIP > 'Extract All' > choose a folder",
             "A folder with all project files: app.py, templates/, static/, etc.")
    pdf.tip("TIP", "With the full source you can also run from Python (Method C) or deploy to Railway (Method D).")
    pdf.ln(2)
    pdf.sub("Option 3: Git Clone (Developers)")
    pdf.step(">>", "[Terminal]", "Open CMD, PowerShell, or Git Bash",
             "A command line prompt")
    pdf.code(["git clone https://github.com/spidermch/Saferpay_Demo_Shop.git", "cd Saferpay_Demo_Shop"])
    pdf.step(">>", "[Terminal]", "Run the two commands above",
             "'Cloning into Saferpay_Demo_Shop...' and then the project folder")

    # ============ 4 - Method C: Run from Source ============
    pdf.add_page()
    pdf.section("4", "Method C: Run from Source Code")
    pdf.txt("For developers who want to modify the code. Requires Python to be installed.")
    pdf.ln(2)
    pdf.sub("Prerequisites: Install Python")
    pdf.step(">>", "[Browser]", "Go to https://www.python.org/downloads/ and click 'Download Python 3.12'",
             "A Python installer file downloads (about 25 MB)")
    pdf.step(">>", "[Installer]", "Run the installer. IMPORTANT: Check the box 'Add Python to PATH'!",
             "Python installs. The checkbox is at the BOTTOM of the first screen.")
    pdf.warn("ADD TO PATH", "If you forget this checkbox, 'python' won't work in the terminal. You'd need to reinstall.")
    pdf.step(">>", "[Terminal]", "Open CMD or PowerShell. Type: python --version",
             "'Python 3.12.8' (or similar). If you see this, Python is installed correctly.")
    pdf.ln(2)
    pdf.sub("Get the Project Files")
    pdf.txt("Use GitHub download (Section 3) or copy the project folder.")
    pdf.ln(2)
    pdf.sub("Install, Run, Open")
    pdf.step(">>", "[Terminal]", "Navigate to the project folder:",
             "Your prompt shows the project folder path")
    pdf.code(["cd C:\\Projects\\Saferpay_Demo_Shop"])
    pdf.step(">>", "[Terminal]", "Create a virtual environment and activate it:",
             "'(venv)' appears at the start of your prompt")
    pdf.code(["python -m venv venv", "venv\\Scripts\\activate"])
    pdf.step(">>", "[Terminal]", "Install dependencies (takes ~10 seconds):",
             "'Successfully installed Flask requests ...'")
    pdf.code(["pip install -r requirements.txt"])
    pdf.step(">>", "[Terminal]", "Start the app:",
             "'Running on http://127.0.0.1:5000'")
    pdf.code(["python app.py"])
    pdf.step(">>", "[Browser]", "Open http://localhost:5000 in your browser",
             "The Saferpay Explorer app with 3 main tabs")
    pdf.tip("TO STOP", "Press CTRL+C in the terminal. To restart: type 'python app.py' again.")

    # ============ 5 - Method D: Deploy to Railway ============
    pdf.add_page()
    pdf.section("5", "Method D: Deploy to Railway (Cloud)")
    pdf.txt("Host the app online so anyone with the URL can access it. Free tier available.")
    pdf.ln(2)
    pdf.sub("What is Railway?")
    pdf.txt("Railway (railway.app) is a cloud platform that runs your app on the internet. You get a public URL like saferpay-explorer.up.railway.app that colleagues can open from anywhere.")
    pdf.ln(2)
    pdf.sub("Step-by-Step (Browser Method - No CLI Needed)")
    pdf.step(">>", "[Browser]", "Go to https://railway.app and click 'Start a New Project'",
             "Sign-up page. Sign in with your GitHub account.")
    pdf.step(">>", "[Railway]", "Click 'Deploy from GitHub Repo'",
             "A list of your GitHub repositories")
    pdf.step(">>", "[Railway]", "Select 'Saferpay_Demo_Shop' from the list",
             "Railway starts building your app (takes 1-2 minutes)")
    pdf.step(">>", "[Railway]", "Click your project > Variables tab > 'New Variable'",
             "A form to add environment variables")
    pdf.step(">>", "[Railway]", "Add: Name=SECRET_KEY, Value=any-random-text-here",
             "The variable appears in the list")
    pdf.step(">>", "[Railway]", "Go to Settings > Networking > click 'Generate Domain'",
             "A public URL like xxx.up.railway.app")
    pdf.step(">>", "[Browser]", "Open your Railway URL in a new tab",
             "The Saferpay Explorer running in the cloud!")
    pdf.tip("AUTO-DEPLOY", "Push changes to GitHub and Railway automatically redeploys within 60 seconds.")

    # ============ 6 - Configure Saferpay Credentials ============
    pdf.add_page()
    pdf.section("6", "Configure Saferpay Credentials")
    pdf.txt("After the app is running (any method), you need to enter your Saferpay test credentials.")
    pdf.ln(2)
    pdf.sub("Where to Get Credentials")
    pdf.step(">>", "[Browser]", "Open https://test.saferpay.com/BO (Saferpay Backoffice)",
             "Saferpay Backoffice login page")
    pdf.step(">>", "[Backoffice]", "Log in with your Saferpay test account",
             "The Saferpay Backoffice dashboard")
    pdf.step(">>", "[Backoffice]", "Go to Settings > JSON API: note your Customer ID + Terminal ID",
             "Numeric IDs like Customer ID: 123456, Terminal ID: 12345678")
    pdf.step(">>", "[Backoffice]", "Go to Settings > JSON API Basic Authentication > Create new",
             "An API Username (API_XXXXXX_XXXXXXXX) and Password are shown")
    pdf.warn("SAVE THE PASSWORD", "The password is shown only ONCE. Copy it immediately! If you lose it, create a new one.")
    pdf.ln(2)
    pdf.sub("Enter Credentials in the App")
    pdf.step(">>", "[App]", "Click the 'Dev' tab, then the 'Config' sub-tab in Saferpay Explorer",
             "A form with 4 fields and a Save button")
    pdf.step(">>", "[App]", "Fill in: Customer ID, Terminal ID, API Username, API Password",
             "All 4 fields filled")
    pdf.step(">>", "[App]", "Click 'Save Configuration'",
             "Green message: 'Configuration saved'. Header badge turns green: 'Connected'.")
    pdf.tip("DONE!", "Your Saferpay Explorer is now connected to the Saferpay test environment. Go to Section 7 to make your first payment!")

    # ============ 7 - First Payment ============
    pdf.add_page()
    pdf.section("7", "Your First Payment (Step by Step)")
    pdf.txt("Let's make a test payment end-to-end. This takes about 60 seconds.")
    pdf.ln(2)
    pdf.step(">>", "[App]", "Click the 'Explorer' tab",
             "Split view: shop on the left, API console on the right")
    pdf.step(">>", "[Left Panel]", "Click 'Add to Cart' on any product (e.g. Swiss Luxury Watch)",
             "Cart badge shows '1'. Product is in your cart.")
    pdf.step(">>", "[Left Panel]", "Click 'Checkout' (or the cart icon)",
             "Cart summary with total, customer selector, and payment method choice")
    pdf.step(">>", "[Left Panel]", "Select 'Payment Page' as integration method",
             "'Payment Page' option is highlighted")
    pdf.step(">>", "[Left Panel]", "Click 'Pay Now'",
             "A popup window opens showing the Saferpay payment page")
    pdf.step(">>", "[Popup]", "Select 'Visa' and enter test card: 9010 1000 0000 0001 11",
             "Card form filled in")
    pdf.step(">>", "[Popup]", "Expiry: 12/2030, CVC: 123. Click 'Pay'",
             "3DS page may appear - click Submit. Popup closes automatically.")
    pdf.step(">>", "[Left Panel]", "The result appears: 'Payment Authorized'",
             "Green success message with transaction details")
    pdf.step(">>", "[Right Panel]", "Check the Developer View on the right side",
             "3 API calls logged: PP Initialize, PP Assert, with full JSON")
    pdf.step(">>", "[Left Panel]", "Click the green 'Capture' button",
             "Status changes to CAPTURED. Right panel shows Capture API call.")
    pdf.ln(2)
    pdf.tip("CONGRATULATIONS!", "You've completed your first end-to-end payment flow! Try the Transaction Interface method next or explore the Orders, Customers, and Code tabs.")

    # ============ 8 - Test Cards ============
    pdf.add_page()
    pdf.section("8", "Test Card Numbers")
    pdf.txt("Use these card numbers in the Saferpay test environment. They work for all test payments.")
    pdf.ln(2)
    for brand, num in [("Visa", "9010 1000 0000 0001 11"), ("Mastercard", "9030 1000 0000 0001 30"),
                        ("American Express", "9070 1000 0000 0007 43"), ("Diners", "9050 1000 0000 0005 17"), ("JCB", "9060 1000 0000 0006 26")]:
        pdf.set_font("Helvetica", "B", 9.5)
        pdf.set_text_color(*WL_DARK)
        pdf.cell(38, 5.5, f"  {brand}")
        pdf.set_font("Courier", "", 9.5)
        pdf.cell(0, 5.5, num, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.sub("Additional Details")
    pdf.bullet("Any future date (e.g. 12/2030)", "Expiry: ")
    pdf.bullet("Any 3 digits (e.g. 123)", "CVC: ")
    pdf.bullet("Click 'Submit' or enter 'password'", "3-D Secure: ")

    # ============ 9 - Troubleshooting ============
    pdf.page_check()
    pdf.section("9", "Troubleshooting")
    pdf.sub("SmartScreen blocks the .exe")
    pdf.txt("Click 'More info' then 'Run anyway'. This is normal for unsigned apps.")
    pdf.sub("Browser doesn't open automatically")
    pdf.txt("Open your browser manually and go to http://localhost:5000")
    pdf.sub("'python' not recognized (Source method)")
    pdf.txt("Reinstall Python. Make sure 'Add to PATH' is checked during installation.")
    pdf.sub("pip SSL/proxy errors (Source method)")
    pdf.code(["pip install -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org"])
    pdf.sub("Port 5000 already in use")
    pdf.txt("Another app is using port 5000. Either close it, or run on a different port:")
    pdf.code(["set PORT=8080 && python app.py"])
    pdf.sub("Payment popup blocked by browser")
    pdf.txt("Allow popups for localhost in your browser settings. A fallback link is also shown in the UI.")
    pdf.sub("401 Unauthorized from Saferpay API")
    pdf.txt("Wrong credentials. Go to Config tab and re-enter. Check: correct Customer ID? Correct username format (API_...)?  Correct environment (test vs prod)?")
    pdf.sub("App crashes / console closes immediately")
    pdf.txt("Open CMD first, then drag the .exe into the CMD window and press Enter. You can see the error message before it disappears.")

    # ============ 10 - Project Files ============
    pdf.add_page()
    pdf.section("10", "Project File Overview")
    pdf.txt("What each file does:")
    pdf.ln(2)
    for f, d in [("Saferpay_Explorer.exe", "One-click launcher - double-click to start!"),
                  ("app.py", "Flask backend: routes, payment logic, CRM, products, code viewer"),
                  ("run.py", "Launcher script used by the .exe (auto-opens browser)"),
                  ("requirements.txt", "Dependencies: Flask, requests, gunicorn"),
                  ("Procfile", "Railway start command (gunicorn)"),
                  ("templates/index.html", "SPA with 3 tabs (Explorer, Merchant Admin, Dev) with sub-tabs"),
                  ("templates/return.html", "Payment popup return page"),
                  ("static/js/app.js", "Client logic: cart, payments, CRM, code viewer"),
                  ("static/css/style.css", "Styling: responsive layout, dark dev console"),
                  ("static/img/", "Worldline logo assets"),
                  ("generate_guides.py", "PDF guide generator (creates this document)")]:
        pdf.set_font("Courier", "B", 8.5)
        pdf.set_text_color(*WL_RED)
        pdf.cell(42, 5.5, f)
        pdf.set_font("Helvetica", "", 8.5)
        pdf.set_text_color(*WL_DARK)
        pdf.multi_cell(0, 5.5, d)
        pdf.ln(0.5)

    # ============ 11 - Version History ============
    pdf.add_page()
    pdf.section("11", "Version History")
    pdf.version_entry("1.0.0", "March 2026", [
        "Initial release: Explorer split-view (Shopper + Developer)",
        "PaymentPage flow: Initialize, Assert, Capture",
        "Configuration tab with credential management",
    ])
    pdf.version_entry("2.0.0", "March 2026", [
        "Product catalog, Customer CRM, Transaction Interface flow",
        "Orders dashboard with stats and flow tagging",
        "Code viewer with 45 educational annotations",
    ])
    pdf.version_entry("2.1.0", "March 2026", [
        "Worldline branding in app header and PDF guides",
        "One-click .exe launcher (no Python needed)",
        "GitHub repository with releases",
        "Order Journey Viewer, Feature Audit, Version Selector",
        "Deployment Guide rewritten for clarity",
    ])
    pdf.version_entry("3.0.0", "March 2026", [
        "Tab restructure: 6 tabs consolidated into 3 (Explorer, Merchant Admin, Dev) with sub-tabs",
        "Merchant Admin sub-tabs: Items (catalog), Customers (CRM), Orders (transactions)",
        "Dev sub-tabs: Code (source viewer), Config (credentials), Feature Audit",
        "Enhanced product cards with larger size and hover effects",
        "Customer search/select at checkout: New Customer or Select Existing from CRM",
        "Full customer details form: Name, Email, Street, City, Postal Code, Country, Phone",
        "Post-order reset: webshop clears for next order after completion",
        "Feature Audit activation notes: 'How to enable' for every non-implemented feature",
        "Added OmniChannel AcquireTransaction and InsertAlias features",
        "Added MOTO (Mail Order/Telephone Order) transaction support",
    ])

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
                  ("4","Merchant Admin Tab"),("5","Dev Tab"),
                  ("6","Payment Flows Explained"),("7","API Reference"),
                  ("8","Test Cards"),("9","Version History")]:
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
    pdf.bullet("Customer search and selection at checkout")
    pdf.bullet("Feature audit with activation notes for backoffice setup")
    pdf.sub("Architecture")
    pdf.txt("Backend: Python Flask | Frontend: Vanilla JavaScript (no frameworks) | Deployment: Railway-ready | API: Saferpay JSON API v1.33")

    # 2 - Quick Start
    pdf.add_page()
    pdf.section("2", "Quick Start")
    pdf.txt("Get up and running in 5 steps:")
    pdf.ln(2)
    pdf.num(1, "Open the app in your browser (http://localhost:5000 or your Railway URL)")
    pdf.num(2, "Go to the Dev tab > Config sub-tab and enter your Saferpay test credentials")
    pdf.num(3, "Switch to the Explorer tab - you'll see the shop on the left, API console on the right")
    pdf.num(4, "Add products to the cart and click 'Pay Now'")
    pdf.num(5, "Complete payment with a test card and watch the API flow in real-time!")
    pdf.ln(4)
    pdf.tip("FIRST TIME?", "If you don't have credentials yet, you can still browse the UI. The app will prompt you to configure credentials when you try to make a payment.")
    pdf.ln(2)
    pdf.sub("Navigation")
    pdf.txt("The app has 3 main tabs in the top navigation bar:")
    pdf.ln(1)
    pdf.bullet("The payment flow visualizer with split-screen shop + API debugger", "Explorer: ")
    pdf.bullet("Merchant dashboard with sub-tabs: Items (catalog), Customers (CRM), Orders (transactions)", "Merchant Admin: ")
    pdf.bullet("Developer tools with sub-tabs: Code (source viewer), Config (credentials), Feature Audit", "Dev: ")

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

    # 4 - Merchant Admin
    pdf.add_page()
    pdf.section("4", "Merchant Admin Tab")
    pdf.txt("The Merchant Admin tab contains three sub-tabs for managing your store: Items, Customers, and Orders.")

    pdf.sub("Items (Product Catalog)")
    pdf.txt("Manage the product catalog that appears in the shop. The app starts with 4 demo products (Swiss-themed) but you can customize freely.")
    pdf.bullet("Click '+ Add Product' to create a new product with name, price (CHF), description, and icon")
    pdf.bullet("Click the pencil icon on any product card to edit it")
    pdf.bullet("X icon deactivates a product (can reactivate later); trash icon permanently deletes")
    pdf.tip("TIP", "Deactivate seasonal products instead of deleting them - you can reactivate them later without re-entering all the details.")

    pdf.sub("Customers (CRM)")
    pdf.txt("A lightweight CRM for managing customer relationships. Customers can be linked to orders for tracking and reporting.")
    pdf.bullet("Customer list shows cards with name, company, order count, and lifetime spend")
    pdf.bullet("Search bar to filter by name, email, or company")
    pdf.bullet("Click any customer to see full profile with notes and order history")
    pdf.bullet("Add timestamped notes for tracking interactions")
    pdf.bullet("When checking out in Explorer, select a customer to link the order")

    pdf.sub("Orders (Transactions)")
    pdf.txt("The merchant's view of all transactions processed through the shop.")
    pdf.bullet("Dashboard stats: Total Orders, Total Volume, Authorized, Captured")
    pdf.bullet("Transaction table with Order ID, customer, amount, status, flow, payment method, time")
    pdf.bullet("Green 'Capture' button on authorized transactions to settle payments")
    pdf.bullet("Status colors: Blue (Initialized), Amber (Authorized), Green (Captured), Red (Failed)")

    # 5 - Dev
    pdf.add_page()
    pdf.section("5", "Dev Tab")
    pdf.txt("The Dev tab contains three sub-tabs for developers and technical users: Code, Config, and Feature Audit.")

    pdf.sub("Code (Source Viewer)")
    pdf.txt("View the actual application source code with educational annotations. Four files available: app.py, app.js, style.css, index.html.")
    pdf.bullet("Key lines highlighted with purple background - click for explanations")
    pdf.bullet("Blue left border = API route/endpoint; Green left border = Saferpay API interaction")
    pdf.bullet("45 annotations covering session management, API auth, payment flows, security")
    pdf.bullet("Edit mode available with service password (contact team lead)")

    pdf.sub("Config (API Credentials)")
    pdf.txt("Set up your Saferpay JSON API credentials to connect to the test (or production) environment.")
    pdf.bullet("Your numeric Saferpay account identifier", "Customer ID: ")
    pdf.bullet("The terminal that processes payments", "Terminal ID: ")
    pdf.bullet("JSON API username (format: API_XXXXXX_XXXXXXXX)", "API Username: ")
    pdf.bullet("JSON API password (shown once when created)", "API Password: ")
    pdf.txt("Select Test or Production from the Base URL dropdown. Credentials are stored in browser session only.")
    pdf.warn("SESSION STORAGE", "Credentials are NOT saved permanently. Re-enter after clearing cookies or restarting the server.")

    pdf.sub("Feature Audit")
    pdf.txt("Coverage analysis of which Saferpay JSON API features are implemented in the demo vs available. Includes a donut chart and categorized feature list.")
    pdf.bullet("Every non-implemented feature shows 'How to enable' with backoffice activation instructions")
    pdf.bullet("OmniChannel: AcquireTransaction (POS to e-commerce), InsertAlias (store POS card data)")
    pdf.bullet("MOTO Transactions: mail/phone order processing")
    pdf.bullet("Activation notes cover license requirements, PCI compliance, and Saferpay Backoffice settings")

    # 6 - Payment Flows
    pdf.add_page()
    pdf.section("6", "Payment Flows Explained")
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

    # 7 - API Reference
    pdf.add_page()
    pdf.section("7", "API Reference")
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

    # 8 - Test Cards
    pdf.page_check()
    pdf.section("8", "Test Card Numbers")
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

    # 9 - Version History
    pdf.add_page()
    pdf.section("9", "Version History")
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
    pdf.version_entry("3.0.0", "March 2026", [
        "Tab restructure: 6 tabs consolidated into 3 (Explorer, Merchant Admin, Dev) with sub-tabs",
        "Merchant Admin sub-tabs: Items (catalog), Customers (CRM), Orders (transactions)",
        "Dev sub-tabs: Code (source viewer), Config (credentials), Feature Audit",
        "Enhanced product cards with larger size and hover effects",
        "Customer search/select at checkout: New Customer or Select Existing from CRM",
        "Full customer details form: Name, Email, Street, City, Postal Code, Country, Phone",
        "Post-order reset: webshop clears for next order after completion",
        "Feature Audit with activation notes: 'How to enable' for every non-implemented feature",
        "OmniChannel AcquireTransaction and InsertAlias features added to audit",
        "MOTO (Mail Order/Telephone Order) transaction support added to audit",
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
        "Open the app and go to Dev > Config sub-tab",
        "Enter your Saferpay test credentials",
        "Switch to Explorer and add products to cart",
        "Choose PaymentPage or Transaction at checkout",
        "Select a customer or enter new customer details",
        "Pay with a test card and watch the API flow",
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
