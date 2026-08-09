from decimal import Decimal
from io import BytesIO
from urllib.parse import quote_plus

import requests
from django.conf import settings
from django.core.files.base import ContentFile
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from settings_app.models import CompanySettings
from .models import Invoice
from .utils import amount_in_words


INK = colors.HexColor("#3D4053")
BORDER = colors.HexColor("#34384F")
LIGHT_BG = colors.HexColor("#F7F7FA")


def _register_invoice_fonts():
    try:
        pdfmetrics.registerFont(TTFont("InvoiceRegular", r"C:\Windows\Fonts\arial.ttf"))
        pdfmetrics.registerFont(TTFont("InvoiceBold", r"C:\Windows\Fonts\arialbd.ttf"))
        return "InvoiceRegular", "InvoiceBold"
    except Exception:
        return "Helvetica", "Helvetica-Bold"


FONT_REGULAR, FONT_BOLD = _register_invoice_fonts()


def _money(amount):
    return f"\u20b9 {amount:,.2f}"


def _quantity(value):
    if isinstance(value, Decimal) and value == value.to_integral_value():
        return str(int(value))
    return f"{value:g}"


def _date(value):
    return value.strftime("%d/%m/%Y")


def _paragraph(text, style):
    return Paragraph(str(text or ""), style)


def _safe_image(path, width, height):
    try:
        image = Image(path, width=width, height=height)
        image.hAlign = "CENTER"
        return image
    except Exception:
        return ""


def generate_invoice_pdf(sale):
    company = CompanySettings.load()
    invoice, _ = Invoice.objects.get_or_create(sale=sale)
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=12 * mm,
        leftMargin=12 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("InvoiceTitle", parent=styles["Title"], fontName=FONT_BOLD, fontSize=18, textColor=INK, leading=22, spaceAfter=6)
    business_style = ParagraphStyle("Business", parent=styles["Title"], fontName=FONT_BOLD, fontSize=21, textColor=INK, leading=26, alignment=0, spaceAfter=5)
    normal = ParagraphStyle("InvoiceNormal", parent=styles["Normal"], fontName=FONT_REGULAR, fontSize=9.3, textColor=INK, leading=13)
    bold = ParagraphStyle("InvoiceBold", parent=normal, fontName=FONT_BOLD)
    small_bold = ParagraphStyle("InvoiceSmallBold", parent=bold, fontSize=8.8, leading=12)
    center = ParagraphStyle("InvoiceCenter", parent=normal, alignment=1)

    page_width = A4[0] - doc.leftMargin - doc.rightMargin
    story = [Paragraph("Tax Invoice", title_style)]

    address_lines = (company.address or "Business address not configured").splitlines()
    contact_left = f"Phone:  <b>{company.phone or '-'}</b>"
    contact_right = f"Email:  <b>{company.email or '-'}</b>"
    tax_left = f"GSTIN: <b>{company.gst_number or '-'}</b>"
    tax_right = f"State: <b>33-Tamil Nadu</b>"

    logo = ""
    if company.logo:
        logo = _safe_image(company.logo.path, 36 * mm, 36 * mm)
    business_block = [
        _paragraph(company.business_name, business_style),
        *[_paragraph(line, normal) for line in address_lines],
        Spacer(1, 3 * mm),
        Table(
            [[_paragraph(contact_left, normal), _paragraph(contact_right, normal)], [_paragraph(tax_left, normal), _paragraph(tax_right, normal)]],
            colWidths=[74 * mm, 74 * mm],
            style=TableStyle([
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]),
        ),
    ]
    header = Table([[logo, business_block]], colWidths=[42 * mm, page_width - 42 * mm], rowHeights=[49 * mm])
    header.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.8, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (0, 0), 5 * mm),
        ("RIGHTPADDING", (0, 0), (0, 0), 4 * mm),
        ("LEFTPADDING", (1, 0), (1, 0), 4 * mm),
        ("RIGHTPADDING", (1, 0), (1, 0), 4 * mm),
    ]))
    story.append(header)

    bill_to_lines = [_paragraph("<b>Bill To:</b>", small_bold), _paragraph(f"<b>{sale.customer.name}</b>", bold)]
    if sale.customer.phone:
        bill_to_lines.append(_paragraph(f"Phone: {sale.customer.phone}", normal))
    if sale.customer.gst_number:
        bill_to_lines.append(_paragraph(f"GSTIN: {sale.customer.gst_number}", normal))
    if sale.customer.address:
        bill_to_lines.append(_paragraph(sale.customer.address.replace("\n", "<br/>"), normal))
    invoice_details = [
        _paragraph("<b>Invoice Details:</b>", small_bold),
        _paragraph(f"No:  <b>{sale.invoice_number}</b>", normal),
        _paragraph(f"Date:  <b>{_date(sale.invoice_date)}</b>", normal),
    ]
    details = Table([[bill_to_lines, invoice_details]], colWidths=[page_width / 2, page_width / 2], rowHeights=[24 * mm])
    details.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.8, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.8, BORDER),
        ("BACKGROUND", (0, 0), (-1, 0), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.extend([details, Spacer(1, 4 * mm)])

    item_data = [["#", "Item name", "HSN/ SAC", "Quantity", "Price/ Unit(\u20b9)", "Amount(\u20b9)"]]
    total_qty = 0
    for index, item in enumerate(sale.items.select_related("product"), start=1):
        total_qty += item.quantity
        item_data.append([
            str(index),
            _paragraph(f"<b>{item.product.name}</b>", bold),
            item.product.hsn_code or "",
            _quantity(item.quantity),
            _money(item.unit_price),
            _money(item.line_total),
        ])
    item_data.append(["", "Total", "", _quantity(total_qty), "", _money(sale.grand_total)])
    table = Table(item_data, colWidths=[10 * mm, 64 * mm, 27 * mm, 31 * mm, 30 * mm, page_width - 162 * mm])
    table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.8, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.8, BORDER),
        ("BACKGROUND", (0, 0), (-1, 0), LIGHT_BG),
        ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
        ("FONTNAME", (0, 1), (-1, -1), FONT_REGULAR),
        ("TEXTCOLOR", (0, 0), (-1, -1), INK),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (3, 0), (-1, -1), "RIGHT"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("FONTNAME", (0, -1), (-1, -1), FONT_BOLD),
    ]))
    story.append(table)

    totals_data = [
        ["Sub Total", ":", _money(sale.subtotal)],
        ["Total", ":", _money(sale.grand_total)],
        [_paragraph("<b>Invoice Amount in Words:</b>", bold), "", ""],
        [amount_in_words(sale.grand_total).replace("Only", "only"), "", ""],
        ["Received", ":", _money(sale.paid_amount)],
        ["Balance", ":", _money(sale.balance_due)],
    ]
    totals_table = Table(totals_data, colWidths=[65 * mm, 8 * mm, page_width - 73 * mm])
    totals_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.8, BORDER),
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, BORDER),
        ("LINEBELOW", (0, 1), (-1, 1), 0.8, BORDER),
        ("LINEBELOW", (0, 2), (-1, 2), 0.8, BORDER),
        ("LINEBELOW", (0, 3), (-1, 3), 0.8, BORDER),
        ("SPAN", (0, 2), (-1, 2)),
        ("SPAN", (0, 3), (-1, 3)),
        ("FONTNAME", (0, 0), (-1, -1), FONT_REGULAR),
        ("FONTNAME", (0, 1), (-1, 2), FONT_BOLD),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("TEXTCOLOR", (0, 0), (-1, -1), INK),
        ("ALIGN", (2, 0), (2, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.extend([totals_table, Spacer(1, 4 * mm)])

    terms_text = company.terms_and_conditions or company.invoice_footer or "Thanks for doing business with us!"
    terms = Table([
        [_paragraph("<b>Terms & Conditions:</b>", bold)],
        [_paragraph(terms_text, normal)],
    ], colWidths=[page_width])
    terms.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.8, BORDER),
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, BORDER),
        ("BACKGROUND", (0, 0), (-1, 0), LIGHT_BG),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(terms)

    signature = Table([
        ["", _paragraph(f"<b>For {company.business_name}:</b>", bold)],
        ["", _paragraph("Authorized Signatory", center)],
    ], colWidths=[page_width / 2, page_width / 2], rowHeights=[11 * mm, 27 * mm])
    signature.setStyle(TableStyle([
        ("BOX", (1, 0), (1, -1), 0.8, BORDER),
        ("LINEBELOW", (1, 0), (1, 0), 0.8, BORDER),
        ("VALIGN", (1, 0), (1, 0), "MIDDLE"),
        ("VALIGN", (1, 1), (1, 1), "BOTTOM"),
        ("LEFTPADDING", (1, 0), (1, -1), 4),
        ("RIGHTPADDING", (1, 0), (1, -1), 4),
        ("BOTTOMPADDING", (1, 1), (1, 1), 5),
    ]))
    story.append(signature)

    doc.build(story)
    filename = f"{sale.invoice_number}.pdf"
    invoice.pdf_file.save(filename, ContentFile(buffer.getvalue()), save=True)
    return invoice


def whatsapp_web_url(sale):
    message = f"Hello {sale.customer.name}, your invoice {sale.invoice_number} for Rs. {sale.grand_total:.2f} is ready."
    digits = "".join(ch for ch in sale.customer.phone if ch.isdigit())
    if len(digits) == 10:
        digits = f"91{digits}"
    return f"https://wa.me/{digits}?text={quote_plus(message)}"


def send_whatsapp_document(invoice):
    token = settings.WHATSAPP_CLOUD_TOKEN
    phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
    if not token or not phone_number_id or not invoice.pdf_file:
        return {"configured": False, "fallback_url": whatsapp_web_url(invoice.sale)}
    sale = invoice.sale
    digits = "".join(ch for ch in sale.customer.phone if ch.isdigit())
    if len(digits) == 10:
        digits = f"91{digits}"
    base = f"https://graph.facebook.com/{settings.WHATSAPP_API_VERSION}/{phone_number_id}"
    headers = {"Authorization": f"Bearer {token}"}
    with invoice.pdf_file.open("rb") as pdf:
        media = requests.post(f"{base}/media", headers=headers, files={"file": (invoice.pdf_file.name, pdf, "application/pdf")}, data={"messaging_product": "whatsapp"}, timeout=30)
    media.raise_for_status()
    media_id = media.json()["id"]
    payload = {
        "messaging_product": "whatsapp",
        "to": digits,
        "type": "document",
        "document": {"id": media_id, "filename": f"{sale.invoice_number}.pdf", "caption": f"Invoice {sale.invoice_number} - Rs. {sale.grand_total:.2f}"},
    }
    response = requests.post(f"{base}/messages", headers={**headers, "Content-Type": "application/json"}, json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    invoice.shared_on_whatsapp = True
    invoice.whatsapp_message_id = data.get("messages", [{}])[0].get("id", "")
    invoice.save(update_fields=["shared_on_whatsapp", "whatsapp_message_id", "updated_at"])
    return {"configured": True, "response": data}
