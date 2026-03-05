"""Generate Management Overview PDF for Saferpay Explorer."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import os

W, H = A4
PRIMARY = HexColor('#0033A0')
ACCENT = HexColor('#00A0E3')
SUCCESS = HexColor('#10b981')
DARK = HexColor('#1a1d23')
GRAY = HexColor('#5f6672')
LIGHT_BG = HexColor('#f0f2f5')
WHITE = HexColor('#ffffff')

def draw_header(c, y, title, subtitle=None):
    c.setFillColor(PRIMARY)
    c.rect(0, y - 2*mm, W, 18*mm, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont('Helvetica-Bold', 16)
    c.drawString(20*mm, y + 5*mm, title)
    if subtitle:
        c.setFont('Helvetica', 9)
        c.drawString(20*mm, y + 0.5*mm, subtitle)
    return y - 8*mm

def draw_section(c, y, title):
    c.setFillColor(PRIMARY)
    c.setFont('Helvetica-Bold', 13)
    c.drawString(20*mm, y, title)
    c.setStrokeColor(ACCENT)
    c.setLineWidth(1.5)
    c.line(20*mm, y - 3*mm, W - 20*mm, y - 3*mm)
    return y - 10*mm

def draw_bullet(c, y, text, indent=25):
    c.setFillColor(ACCENT)
    c.circle(indent*mm - 3*mm, y + 1.2*mm, 1.5*mm, fill=1, stroke=0)
    c.setFillColor(DARK)
    c.setFont('Helvetica', 9.5)
    # Wrap text manually
    words = text.split(' ')
    line = ''
    max_w = W - (indent + 22)*mm
    for word in words:
        test = line + ' ' + word if line else word
        if c.stringWidth(test, 'Helvetica', 9.5) < max_w:
            line = test
        else:
            c.drawString(indent*mm, y, line)
            y -= 4.5*mm
            line = word
    if line:
        c.drawString(indent*mm, y, line)
        y -= 4.5*mm
    return y - 1*mm

def draw_text(c, y, text, font='Helvetica', size=9.5, indent=20, color=DARK):
    c.setFillColor(color)
    c.setFont(font, size)
    words = text.split(' ')
    line = ''
    max_w = W - (indent + 22)*mm
    for word in words:
        test = line + ' ' + word if line else word
        if c.stringWidth(test, font, size) < max_w:
            line = test
        else:
            c.drawString(indent*mm, y, line)
            y -= 4.5*mm
            line = word
    if line:
        c.drawString(indent*mm, y, line)
        y -= 4.5*mm
    return y

def draw_flow_box(c, y, step_num, title, desc):
    box_w = W - 40*mm
    box_h = 18*mm
    x = 20*mm
    # Box
    c.setFillColor(LIGHT_BG)
    c.roundRect(x, y - box_h, box_w, box_h, 3*mm, fill=1, stroke=0)
    # Number circle
    c.setFillColor(PRIMARY)
    c.circle(x + 8*mm, y - box_h/2, 4*mm, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont('Helvetica-Bold', 11)
    c.drawCentredString(x + 8*mm, y - box_h/2 - 1.5*mm, str(step_num))
    # Text
    c.setFillColor(DARK)
    c.setFont('Helvetica-Bold', 10)
    c.drawString(x + 16*mm, y - 5*mm, title)
    c.setFillColor(GRAY)
    c.setFont('Helvetica', 8.5)
    c.drawString(x + 16*mm, y - 11*mm, desc)
    # Arrow
    if step_num < 6:
        c.setFillColor(ACCENT)
        c.setFont('Helvetica-Bold', 14)
        c.drawCentredString(W/2, y - box_h - 3*mm, 'v')
    return y - box_h - 7*mm

def generate():
    out = os.path.join(os.path.dirname(__file__), 'Saferpay_Explorer_Management_Overview.pdf')
    c = canvas.Canvas(out, pagesize=A4)

    # ===== PAGE 1: Cover =====
    c.setFillColor(PRIMARY)
    c.rect(0, H - 90*mm, W, 90*mm, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont('Helvetica-Bold', 28)
    c.drawString(25*mm, H - 40*mm, 'Saferpay Explorer')
    c.setFont('Helvetica', 14)
    c.drawString(25*mm, H - 52*mm, 'Interactive Payment Integration Demo Tool')
    c.setFont('Helvetica', 10)
    c.drawString(25*mm, H - 65*mm, 'Management Overview | Sales Enablement | Product Brief')
    c.setFillColor(ACCENT)
    c.rect(25*mm, H - 72*mm, 40*mm, 1*mm, fill=1, stroke=0)

    y = H - 110*mm
    c.setFillColor(DARK)
    c.setFont('Helvetica-Bold', 12)
    c.drawString(25*mm, y, 'What is Saferpay Explorer?')
    y -= 8*mm
    y = draw_text(c, y, 'Saferpay Explorer is an interactive, self-contained demo application that lets merchants, sales engineers, and partners experience the full Saferpay payment integration lifecycle in real-time. It combines a working webshop with a live API debugger, giving both technical and non-technical audiences an immediate understanding of how Saferpay works.', indent=25, color=GRAY)

    y -= 8*mm
    c.setFillColor(DARK)
    c.setFont('Helvetica-Bold', 12)
    c.drawString(25*mm, y, 'Target Audience')
    y -= 8*mm
    for item in ['Sales teams demoing Saferpay to prospective merchants',
                 'Pre-sales engineers conducting technical evaluations',
                 'Partner integrators learning the API before coding',
                 'Training sessions for new employees on payment flows',
                 'Merchant CTOs evaluating Saferpay vs. competitors']:
        y = draw_bullet(c, y, item)

    y -= 6*mm
    # Footer
    c.setFillColor(GRAY)
    c.setFont('Helvetica', 7)
    c.drawString(20*mm, 12*mm, 'Confidential - Worldline / Saferpay Explorer Management Overview')
    c.drawRightString(W - 20*mm, 12*mm, 'Page 1 of 3')

    c.showPage()

    # ===== PAGE 2: SMART Goals & USPs =====
    y = H - 15*mm
    y = draw_header(c, y, 'SMART Goals & Unique Selling Points')

    y -= 10*mm
    y = draw_section(c, y, 'SMART Goals')

    goals = [
        ('Specific', 'Reduce merchant onboarding demo time from 2 hours to 20 minutes by providing a complete, working demo environment with pre-configured products, CRM, and live API visibility.'),
        ('Measurable', 'Achieve 40% faster deal closure by enabling sales teams to show live payment flows during the first meeting. Track demo-to-conversion rate improvement quarter over quarter.'),
        ('Achievable', 'Single .exe deployment requires zero infrastructure - any sales engineer can run it on their laptop with just test credentials. No dev environment, no Docker, no cloud setup needed.'),
        ('Relevant', 'Directly supports Worldline\'s merchant acquisition strategy by making Saferpay\'s technical superiority visible and tangible to decision-makers during the evaluation phase.'),
        ('Time-bound', 'Deploy to all sales teams within Q2 2026. Measure impact on demo satisfaction scores and pipeline velocity by end of Q3 2026.'),
    ]
    for label, desc in goals:
        c.setFillColor(PRIMARY)
        c.setFont('Helvetica-Bold', 10)
        c.drawString(20*mm, y, label)
        y -= 5*mm
        y = draw_text(c, y, desc, indent=20, color=GRAY, size=8.5)
        y -= 3*mm

    y -= 5*mm
    y = draw_section(c, y, 'Unique Selling Points (USPs)')

    usps = [
        'Split-Screen Experience: Shopper view + Developer API debugger side-by-side. Decision-makers see the customer journey while technical staff see every API call in real-time.',
        'Full E-Commerce Flow: Browse products, add to cart, enter customer details, pay, capture - the complete merchant lifecycle in one tool.',
        'Zero-Infrastructure Demo: Ships as a single executable. No servers, no databases, no configuration beyond API credentials.',
        'Live API Transparency: Every Saferpay API call (Initialize, Assert, Authorize, Capture) is logged with request/response payloads and plain-English explanations.',
        'Built-in CRM & Product Catalog: Fully functional customer management and product CRUD to simulate real merchant operations.',
        'Feature Audit Dashboard: Visual coverage report showing which Saferpay API features are implemented, helping merchants plan their integration roadmap.',
        'Order Journey Visualization: Timeline view tracing each transaction through the complete payment lifecycle with API details at each step.',
        'Code Transparency: Full source code viewer with educational annotations - builds trust by showing there is no magic, just clean API integration.',
        'Error Diagnostics: Automatic error logging to debug.log for remote troubleshooting - support teams can diagnose issues without screen sharing.',
    ]
    for usp in usps:
        y = draw_bullet(c, y, usp)
        if y < 25*mm:
            c.setFillColor(GRAY)
            c.setFont('Helvetica', 7)
            c.drawString(20*mm, 12*mm, 'Confidential - Worldline / Saferpay Explorer Management Overview')
            c.drawRightString(W - 20*mm, 12*mm, 'Page 2 of 3')
            c.showPage()
            y = H - 20*mm

    c.setFillColor(GRAY)
    c.setFont('Helvetica', 7)
    c.drawString(20*mm, 12*mm, 'Confidential - Worldline / Saferpay Explorer Management Overview')
    c.drawRightString(W - 20*mm, 12*mm, 'Page 2 of 3')
    c.showPage()

    # ===== PAGE 3: High-Level Flow =====
    y = H - 15*mm
    y = draw_header(c, y, 'High-Level End-User Flow')

    y -= 12*mm
    steps = [
        ('Browse & Shop', 'End user browses product catalog, selects items, adds to cart'),
        ('Customer Details', 'User enters name, email, address - mandatory before payment'),
        ('Select Payment Method', 'Choose PaymentPage (redirect) or Transaction Interface (advanced)'),
        ('Secure Payment', 'User is redirected to Saferpay-hosted page for card entry (PCI compliant)'),
        ('Verification', 'System calls Assert/Authorize to verify payment result'),
        ('Capture & Settlement', 'Merchant captures the authorized amount - money transfer initiated'),
    ]
    for i, (title, desc) in enumerate(steps, 1):
        y = draw_flow_box(c, y, i, title, desc)

    y -= 5*mm
    y = draw_section(c, y, 'Technical Architecture')
    y -= 2*mm

    arch_items = [
        'Backend: Python/Flask lightweight server with in-memory session store',
        'Frontend: Vanilla JavaScript SPA - zero dependencies, full transparency',
        'API Auth: HTTP Basic Authentication (Saferpay JSON API)',
        'Security: Service password for code editing, session-based config, debug logging',
        'Deployment: PyInstaller .exe / Heroku / Railway / any Python host',
        'Debug: Automatic error logging to debug.log with full tracebacks and context',
    ]
    for item in arch_items:
        y = draw_bullet(c, y, item)

    y -= 8*mm
    c.setFillColor(PRIMARY)
    c.setFont('Helvetica-Bold', 11)
    c.drawCentredString(W/2, y, 'Ready to accelerate your payment demos?')
    y -= 6*mm
    c.setFillColor(GRAY)
    c.setFont('Helvetica', 9)
    c.drawCentredString(W/2, y, 'Contact your Worldline sales representative for deployment and credentials.')

    c.setFillColor(GRAY)
    c.setFont('Helvetica', 7)
    c.drawString(20*mm, 12*mm, 'Confidential - Worldline / Saferpay Explorer Management Overview')
    c.drawRightString(W - 20*mm, 12*mm, 'Page 3 of 3')

    c.save()
    print(f'Generated: {out}')

if __name__ == '__main__':
    generate()
