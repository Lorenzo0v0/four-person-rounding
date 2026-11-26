"""Typeset paper.html as a three-page PDF (lxml and ReportLab)."""
from html import escape
from pathlib import Path

from lxml import html
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph, Table, TableStyle

ROOT = Path(__file__).resolve().parent
FONTS = Path("/usr/share/fonts/truetype/dejavu")
for name, file in (("Body", "DejaVuSerif"), ("BodyB", "DejaVuSerif-Bold"),
                   ("BodyI", "DejaVuSerif-Italic"), ("BodyBI", "DejaVuSerif-BoldItalic"),
                   ("UI", "DejaVuSans"), ("UIB", "DejaVuSans-Bold")):
    pdfmetrics.registerFont(TTFont(name, str(FONTS / (file + ".ttf"))))
pdfmetrics.registerFontFamily("Body", normal="Body", bold="BodyB", italic="BodyI", boldItalic="BodyBI")
ink = colors.HexColor("#182e31")
teal = colors.HexColor("#426d68")
pale = colors.HexColor("#ebf2ef")
def style(font, size, leading, color=ink):
    return ParagraphStyle(font, fontName=font, fontSize=size, leading=leading, textColor=color)
styles = {"h1":style("Body",26,30), "h2":style("Body",17,21), "h3":style("UIB",10.3,14,teal),
          "p":style("Body",10.1,14.5), "small":style("Body",9.1,12.8), "ref":style("Body",8.7,12),
          "tag":style("UIB",8,12,teal), "caption":style("UI",8.4,12,teal),
          "eq":style("Body",10.2,15), "abstract":style("Body",10.6,15.1)}
def markup(node):
    tag = node.tag
    inner = escape(node.text or "") + "".join(markup(child) + escape(child.tail or "") for child in node)
    if tag in ("i", "b", "sub", "sup"):
        return f"<{tag}>{inner}</{tag}>"
    if tag == "br":
        return "<br/>"
    if tag == "a":
        return f'<link href="{escape(node.get("href"))}" color="#35695f">{inner}</link>'
    return inner

doc = html.fromstring((ROOT/"paper.html").read_text())
pdf = Canvas(str(ROOT/"paper.pdf"), pagesize=letter, invariant=1)
pdf.setTitle(doc.find(".//title").text_content())
pdf.setAuthor("Prepared with OpenAI Codex")
left, right = 54, 558
width = right - left
def paragraph(node, key, x, y, available):
    item = Paragraph(markup(node), styles[key])
    _, height = item.wrap(available, 750)
    item.drawOn(pdf, x, y-height)
    return y-height
for page in doc.findall(".//section"):
    head, foot = [page.find(t).findall("span") for t in ("header","footer")]
    for pair, at in ((head,753),(foot,28)):
        pdf.setFont("UI",7.6)
        pdf.setFillColor(teal)
        pdf.drawString(left,at,pair[0].text_content())
        pdf.drawRightString(right,at,pair[1].text_content())
        pdf.setStrokeColor(colors.HexColor("#aabfb8"))
        line_at = at-8 if at>100 else at+14
        pdf.line(left,line_at,right,line_at)
    y = 730
    for part in page:
        tag = part.tag
        if tag in ("header","footer"):
            continue
        if tag == "table":
            y = paragraph(part.find("caption"),"caption",left,y,width)-4
            rows = [[c.text_content().strip() for c in tr] for tr in part.findall(".//tr")]
            if len(rows[0]) == 4:
                widths = [33,139,68,width-240]
            else:
                label_width = 116 if len(rows[0])==8 else 81
                widths = [label_width]+[(width-label_width)/(len(rows[0])-1)]*(len(rows[0])-1)
            t = Table(rows,colWidths=widths)
            t.setStyle(TableStyle([("FONTNAME",(0,0),(-1,-1),"UI"),("FONTSIZE",(0,0),(-1,-1),8.25),
                        ("TEXTCOLOR",(0,0),(-1,-1),ink),("BACKGROUND",(0,0),(-1,0),pale),
                        ("FONTNAME",(0,0),(-1,0),"UIB"),("TOPPADDING",(0,0),(-1,-1),3),
                        ("BOTTOMPADDING",(0,0),(-1,-1),3),("LINEBELOW",(0,-1),(-1,-1),.4,teal)]))
            _, h = t.wrap(width,700)
            t.drawOn(pdf,left,y-h)
            y -= h+10
        elif part.get("class")=="abstract":
            top = y
            for child in part.findall("p"):
                key = "tag" if child.get("class") else "abstract"
                y = paragraph(child,key,left+12,y,width-12)-3
            pdf.setStrokeColor(teal)
            pdf.setLineWidth(1.8)
            pdf.line(left,top,left,y+3)
            pdf.setLineWidth(.5)
            y -= 6
        else:
            key = part.get("class", tag)
            if tag in ("h2","h3"):
                y -= 5
            y = paragraph(part,key,left,y,width)-(9 if tag.startswith("h") else 6)
    if y < 46:
        raise RuntimeError(f"Page content overlaps footer (baseline {y:.1f})")
    pdf.showPage()
pdf.save()
