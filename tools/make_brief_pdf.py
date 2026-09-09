#!/usr/bin/env python3
"""
Builds docs/WHAT-I-NEED-FROM-YOU.pdf — a printable version of the content brief.

    python3 tools/make_brief_pdf.py

The PDF follows the same design language as the website: monochrome, light
weights, small tracked uppercase headings, generous whitespace. It is meant to
be printed and worked through with a pen.
"""

import os, sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, Table, TableStyle, PageBreak, KeepTogether,
                                HRFlowable, ListFlowable, ListItem, CondPageBreak)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
OUT  = os.path.join(ROOT, "docs", "WHAT-I-NEED-FROM-YOU.pdf")

BRAND = "Sample Portfolio"

# ---------------------------------------------------------------- palette ---
INK    = colors.HexColor("#1a1a1a")
SOFT   = colors.HexColor("#4a4a4a")
MUTE   = colors.HexColor("#8c8c8c")
RULE   = colors.HexColor("#d9d6d1")
FILL   = colors.HexColor("#f4f3f1")
WHITE  = colors.white

# ------------------------------------------------------------------ fonts ---
def font(name, *paths):
    for p in paths:
        if os.path.exists(p):
            pdfmetrics.registerFont(TTFont(name, p))
            return True
    return False

L = "/usr/share/fonts/truetype/liberation/"
L2 = "/usr/share/fonts/truetype/liberation2/"
have = (font("UI",      L + "LiberationSans-Regular.ttf",  L2 + "LiberationSans-Regular.ttf")
        and font("UI-B", L + "LiberationSans-Bold.ttf",    L2 + "LiberationSans-Bold.ttf")
        and font("UI-I", L + "LiberationSans-Italic.ttf",  L2 + "LiberationSans-Italic.ttf"))
if have:
    from reportlab.pdfbase.pdfmetrics import registerFontFamily
    registerFontFamily("UI", normal="UI", bold="UI-B", italic="UI-I", boldItalic="UI-B")
    F, FB, FI = "UI", "UI-B", "UI-I"
else:
    F, FB, FI = "Helvetica", "Helvetica-Bold", "Helvetica-Oblique"


def track(s, em=None):
    """
    Pass-through, kept so the call sites still read as "tracked".

    Real letter-spacing comes from ParagraphStyle(charSpace=...) and
    canvas.setCharSpace(). Inserting thin spaces between characters by hand
    also swallows the word spaces, turning "BLOCKS LAUNCH?" into
    "BLOCKSLAUNCH?" — which is exactly what the first draft of this did.
    """
    return s


# ----------------------------------------------------------------- styles ---
def P(name, **kw):
    base = dict(fontName=F, fontSize=9.4, leading=15, textColor=SOFT,
                alignment=TA_LEFT, spaceAfter=0)
    base.update(kw)
    return ParagraphStyle(name, **base)

S = {
    "body":     P("body", spaceAfter=7),
    "lead":     P("lead", fontSize=10.6, leading=17.5, textColor=INK, spaceAfter=9),
    "small":    P("small", fontSize=8.4, leading=13, textColor=MUTE, spaceAfter=5),
    "h1":       P("h1", fontName=F, fontSize=21, leading=26, textColor=INK, spaceAfter=4),
    "h2":       P("h2", fontName=FB, fontSize=8.2, leading=13, textColor=INK, spaceAfter=10, charSpace=1.35),
    "h3":       P("h3", fontName=FB, fontSize=10, leading=14, textColor=INK, spaceAfter=5),
    "label":    P("label", fontName=FB, fontSize=7.4, leading=11, textColor=MUTE, spaceAfter=6, charSpace=1.1),
    "cell":     P("cell", fontSize=8.4, leading=12),
    "cellb":    P("cellb", fontName=FB, fontSize=8.4, leading=12, textColor=INK),
    "cellh":    P("cellh", fontName=FB, fontSize=7.2, leading=10.5, textColor=MUTE, charSpace=0.85),
    "note":     P("note", fontSize=8.8, leading=14, textColor=INK),
    "coverbig": P("coverbig", fontSize=30, leading=35, textColor=INK),
    "coversub": P("coversub", fontSize=11, leading=17, textColor=MUTE),
}


def H1(t):     return Paragraph(t, S["h1"])
def Section(t, need=62 * mm):
    """Start a section, breaking first only if too little room is left."""
    return [CondPageBreak(need), H1(t), Rule(INK, 1.0, after=12)]
def H2(t):     return Paragraph(track(t.upper()), S["h2"])
def H3(t):     return Paragraph(t, S["h3"])
def LBL(t):    return Paragraph(track(t.upper(), .12), S["label"])
def Body(t):   return Paragraph(t, S["body"])
def Lead(t):   return Paragraph(t, S["lead"])
def Small(t):  return Paragraph(t, S["small"])
def Rule(c=RULE, w=0.6, before=0, after=10):
    return HRFlowable(width="100%", thickness=w, color=c,
                      spaceBefore=before, spaceAfter=after)


def bullets(items, style="body"):
    return ListFlowable(
        [ListItem(Paragraph(i, S[style]), leftIndent=12, value="circle")
         for i in items],
        bulletType="bullet", bulletFontSize=4, bulletOffsetY=3,
        leftIndent=10, spaceAfter=8)


def checks(items):
    """
    Tick-box list — this document is meant to be printed and worked through.

    The box is a fixed-size nested table, not a character and not a border on
    the outer cell. The bundled fonts have no ballot-box glyph (it renders as a
    solid black rectangle), and a BOX style on the outer cell stretches to the
    full row height, which on a two-line item draws a tall thin bar.
    """
    def box():
        b = Table([[""]], colWidths=[3.1 * mm], rowHeights=[3.1 * mm])
        b.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.7, MUTE),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        return b

    rows = [[box(), Paragraph(i, S["body"])] for i in items]
    t = Table(rows, colWidths=[7 * mm, None])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (0, -1), 3),      # nudge the box onto the baseline
        ("TOPPADDING", (1, 0), (1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return t


def table(head, rows, widths, zebra=True, headline=True):
    data = [[Paragraph(track(str(h).upper(), .10), S["cellh"]) for h in head]]
    for r in rows:
        data.append([c if hasattr(c, "wrap")
                     else Paragraph(str(c), S["cell"]) for c in r])
    t = Table(data, colWidths=widths, repeatRows=1)
    st = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, 0), 0.6, RULE),
        ("LINEBELOW", (0, 1), (-1, -2), 0.35, colors.HexColor("#ece9e4")),
    ]
    if headline:
        st.append(("LINEABOVE", (0, 0), (-1, 0), 0.6, INK))
    if zebra:
        for i in range(1, len(data)):
            if i % 2 == 0:
                st.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#faf9f8")))
    t.setStyle(TableStyle(st))
    return t


def callout(title, text):
    inner = [LBL(title), Paragraph(text, S["note"])]
    t = Table([[inner]], colWidths=[None])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), FILL),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LINEBEFORE", (0, 0), (0, -1), 2, INK),
    ]))
    return KeepTogether([Spacer(1, 4), t, Spacer(1, 12)])


# --------------------------------------------------------------- document ---
class Doc(BaseDocTemplate):
    def __init__(self, path):
        super().__init__(path, pagesize=A4,
                         leftMargin=22 * mm, rightMargin=22 * mm,
                         topMargin=24 * mm, bottomMargin=20 * mm,
                         title="What I Need From You — " + BRAND,
                         author=BRAND, subject="Website content brief")
        frame = Frame(self.leftMargin, self.bottomMargin,
                      self.width, self.height, id="main")
        self.addPageTemplates([
            PageTemplate(id="cover", frames=[frame], onPage=self._cover),
            PageTemplate(id="body", frames=[frame], onPage=self._chrome),
        ])

    def _cover(self, c, d):
        c.saveState()
        c.setStrokeColor(INK); c.setLineWidth(1.4)
        c.line(22 * mm, A4[1] - 18 * mm, A4[0] - 22 * mm, A4[1] - 18 * mm)
        c.restoreState()

    def _chrome(self, c, d):
        c.saveState()
        w, h = A4
        c.setFont(F, 7)
        c.setFillColor(MUTE)
        c.setCharSpace(1.4)                       # real tracking on the canvas
        c.drawString(22 * mm, h - 14 * mm, BRAND.upper())
        c.drawRightString(w - 22 * mm, h - 14 * mm, "WEBSITE CONTENT BRIEF")
        c.setCharSpace(0)
        c.setStrokeColor(RULE); c.setLineWidth(0.5)
        c.line(22 * mm, h - 17 * mm, w - 22 * mm, h - 17 * mm)
        c.line(22 * mm, 14 * mm, w - 22 * mm, 14 * mm)
        c.setFont(F, 7.5); c.setFillColor(MUTE)
        c.drawRightString(w - 22 * mm, 10 * mm, str(c.getPageNumber() - 1))
        c.restoreState()


# ------------------------------------------------------------------ story ---
def build():
    s = []

    # ---------------------------------------------------------- COVER ------
    s += [Spacer(1, 52 * mm),
          Paragraph(BRAND.upper(), P("cb1", fontSize=10, textColor=MUTE, charSpace=3.2)),
          Spacer(1, 16),
          Paragraph("What I Need<br/>From You", S["coverbig"]),
          Spacer(1, 14),
          Rule(INK, 1.0, after=14),
          Paragraph("The complete list of content and images required to turn the "
                    "placeholder website into the real one.", S["coversub"]),
          Spacer(1, 60 * mm),
          Paragraph("READ SECTION 1 FIRST",
                    P("cb2", fontName=FB, fontSize=7.6, textColor=INK, charSpace=1.5)),
          Spacer(1, 5),
          Paragraph("It will save you a large amount of unnecessary work.", S["small"]),
          PageBreak()]

    # ------------------------------------------------- 1 · READ THIS FIRST --
    s += [H1("You do not need all of it"), Rule(INK, 1.0, after=14)]
    s += [Lead("The site has <b>125 image slots</b> and about <b>4,000 words</b> of "
               "placeholder text. That is what a practice with a twenty-year archive "
               "fills.")]
    s += [Body("You almost certainly should not try to fill all of it now. An "
               "architecture site is judged on the quality of what it shows, not the "
               "quantity. <b>Six well-shot projects with real descriptions beat twelve "
               "thin ones</b>, every time.")]
    s += [Body("So there are two lists in this document: the launch minimum, and the "
               "full build. Work to the first. Grow into the second over the next year.")]
    s += [Spacer(1, 14), H2("The launch minimum"), Rule()]

    s += [table(
        ["Item", "Quantity", "Why this number"],
        [["Projects", Paragraph("<b>4–6</b>", S["cellb"]),
          "Below 4 the grid looks empty; above 6 you start padding"],
         ["Photos per project", "6–10", "Fewer than 6 and the page has no rhythm"],
         ["Home slideshow", "3–5", "Your strongest single image from each project"],
         ["Principal portraits", "1 each", "Non-negotiable — people hire people"],
         ["Team headshots", "0 or all", "A half-full grid looks worse than no grid"],
         ["Firm description", "2–3 paras", "The most-read text on the whole site"],
         ["Design philosophy", "1–2 paras", "How you approach a site and a brief"],
         ["Project description", "2–4 paras each", "This is what makes it a portfolio"],
         ["News / awards / press", "0 or what's true", "Empty sections get deleted, not padded"],
         ["Address, phone, emails", "all", "Currently all placeholder"]],
        [42 * mm, 26 * mm, None])]

    s += [Spacer(1, 12),
          callout("In total",
                  "Roughly <b>45–70 images</b> and <b>1,200 words</b>. Achievable in "
                  "a week if the photography already exists.")]

    s += [callout("If a section has nothing real behind it",
                  "Tell me and I will remove it entirely — the page and its navigation "
                  "tab. A News page with two entries reads as an abandoned site. No News "
                  "page reads as a deliberate one. This applies to News, Press, Awards, "
                  "Books and the Team grid.")]

    # ------------------------------------------------------ A · STUDIO -----
    s += [*Section("A · Studio details", 96 * mm)]
    s += [Body("Small, but this blocks launch. Every one of these is currently a "
               "placeholder, including the phone number and every email address.")]
    s += [Spacer(1, 8)]
    s += [table(
        ["#", "I need", "Currently says"],
        [["A1", "Firm name, exactly as it should appear", "Sample Portfolio"],
         ["A2", "Tagline under the logo — 2 to 4 words", "Architecture + Interiors"],
         ["A3", "Your domain name, even if unregistered", "sampleportfolio.com"],
         ["A4", "Studio street address, as on a letterhead", "#00, 00th Main…"],
         ["A5", "Phone number(s) — one or two", "+91 00 0000 0000"],
         ["A6", "General email (shown in the footer)", "studio@…"],
         ["A7", "New-project enquiries email", "projects@…"],
         ["A8", "Careers email", "careers@…"],
         ["A9", "Social links — full URLs", "Instagram / LinkedIn / Pinterest"],
         ["A10", "Copyright year", "2026"],
         ["A11", "Project categories — these become the filter tabs",
          "Residential, Institutional, Hospitality, Workplace, Retail"]],
        [10 * mm, 78 * mm, None])]
    s += [Spacer(1, 10),
          callout("On categories",
                  "Only include a category you have at least one project for. An empty "
                  "tab reads as a broken site. Five is the current count; three is fine.")]

    # ------------------------------------------------------ B · HOME -------
    s += [*Section("B · Home page", 78 * mm)]
    s += [table(
        ["#", "I need", "Notes"],
        [["B1", "3–5 slideshow images", "Your single strongest photograph from each of "
                                        "your best projects. Landscape"],
         ["B2", "The same images cropped portrait", "Optional — for phones. If you skip "
                                                    "this I'll smart-crop the landscape version"],
         ["B3", "Caption for the first slide", "A project name, its location and year"],
         ["B4", "Which projects are 'Selected Work'", "Up to 6. Or I'll use your first six"],
         ["B5", "One-paragraph practice statement", "2–3 sentences, mid-homepage"]],
        [10 * mm, 55 * mm, None])]
    s += [Spacer(1, 8), Small("<b>Images needed:</b> 3–5 landscape, optionally 3–5 portrait.")]

    # ------------------------------------------------------ C · ABOUT ------
    s += [*Section("C · About page", 110 * mm)]
    s += [Lead("The most important text on the site. A prospective client reads this "
               "before they look at a single project.")]
    s += [Spacer(1, 6)]
    s += [table(
        ["#", "I need", "Length", "Notes"],
        [["C1", "'The Firm'", "2–5 paras",
          "When founded and by whom, what you do, the kind of client, any recognition"],
         ["C2", "'Design Philosophy'", "1–2 paras",
          "How you approach a site and a brief. Your voice, not marketing language"],
         ["C3", "Principal: name", "", ""],
         ["C4", "Principal: role title", "", "e.g. 'Founder & Principal'"],
         ["C5", "Principal: biography", "2–3 paras",
          "Education, career, awards, speaking, publications"],
         ["C6", "Principal: portrait photo", "1", "Portrait orientation, head and shoulders"],
         ["C7", "Repeat C3–C6 per principal", "", "Currently set up for two"],
         ["C8", "Team names and roles", "", "Or say 'skip the team section'"],
         ["C9", "Team headshots", "all or none", "A partial grid looks unfinished"]],
        [10 * mm, 42 * mm, 20 * mm, None])]

    s += [Spacer(1, 10),
          callout("On team photos",
                  "They display in greyscale and turn colour on hover, which hides a lot "
                  "of inconsistency in colour but none in framing. They don't need to be "
                  "professionally lit — but they do need to be <b>consistent</b>. Same "
                  "background, same distance, same rough lighting. Mismatched snapshots "
                  "are very obvious once they're lined up in a grid.")]

    s += [Spacer(1, 6), Small("<b>Images needed:</b> one per principal, plus one per "
                              "team member (or none at all).")]

    # --------------------------------------------------- D · PROJECTS ------
    s += [*Section("D · Projects", 110 * mm)]
    s += [Lead("The main body of work. There is a fill-in template — use one copy "
               "per project.")]
    s += [Spacer(1, 8), H2("Text, per project"), Rule()]
    s += [table(
        ["#", "Field", "Notes"],
        [["D1", "Project name", "As you want it titled"],
         ["D2", "Location", "City, or city and state"],
         ["D3", "Year completed", ""],
         ["D4", "Category", "Must be one from A11"],
         ["D5", Paragraph("<b>Description</b>", S["cellb"]),
          Paragraph("<b>2–4 paragraphs minimum.</b> The brief, the site, the response, "
                    "the materials. This is what separates a portfolio from a photo album",
                    S["cell"])],
         ["D6", "Pull quote", "Optional. One sentence lifted from D5, shown large mid-page"],
         ["D7", "Built area", "e.g. '640 sqm' — optional"],
         ["D8", "Client", "'Private' is fine"],
         ["D9", "Project team", "Names of who worked on it"],
         ["D10", "Photographer credit", "Ask your photographer before publishing"],
         ["D11", "Feature on homepage?", "yes / no"]],
        [10 * mm, 38 * mm, None])]

    s += [Spacer(1, 14), H2("Images, per project"), Rule()]
    s += [table(
        ["#", "Slot", "Count", "Final size", "Notes"],
        [["D12", "Cover", "1", "1200 × 900", "The grid thumbnail. Must read at small size"],
         ["D13", "Hero", "1", "2400 × 1350", "Full-width banner. Often your best image"],
         ["D14", "Gallery", Paragraph("<b>6–12</b>", S["cellb"]), "2000 × 1333",
          "The main sequence. Order matters"]],
        [10 * mm, 20 * mm, 15 * mm, 25 * mm, None])]

    s += [Spacer(1, 12),
          callout("Cover and hero are usually different images",
                  "The cover competes with eleven others in a grid, so it needs to be "
                  "legible at 400px wide — usually a clear, simple, wide shot. The hero "
                  "has the whole screen, so it can be atmospheric.")]

    seq = [H3("Sequencing the gallery"), Spacer(1, 2),
           Body("The best project pages read like a walk through the building:"),
           bullets(["Arrival and approach",
                   "The exterior, whole building",
                   "The principal space",
                   "Secondary spaces",
                   "A detail — a material, a junction, a piece of joinery",
                   "Something quiet to end on — evening light, a view out"]),
           Body("Name your files so they sort in that order: <font name='%s'>01-approach.jpg, "
               "02-exterior.jpg, 03-living.jpg</font>." % F)]
    s += [KeepTogether(seq)]

    # ------------------------------------------------------ E · NEWS -------
    s += [*Section("E · News, Press, Awards, Books", 92 * mm)]
    s += [Lead("All four of these sections are optional. Tell me which to delete.")]
    s += [Spacer(1, 6)]
    s += [table(
        ["#", "Section", "I need per entry", "Images?"],
        [["E1", "News highlight", "One sentence, a date, an image, a link if there is one", "Yes"],
         ["E2", "Press", "Publication, article title, author, page range, date", "No"],
         ["E3", "Awards", "Award name, category, project, and the year to group it under", "No"],
         ["E4", "Books", "Book title, publisher, city, year", "No"]],
        [10 * mm, 28 * mm, None, 18 * mm])]

    s += [Spacer(1, 12), H3("News entries read as sentences, not headlines"), Spacer(1, 4)]
    s += [Body("Good: <i>“Riverside House wins Best Residential Interior at the 2026 "
               "Trends Awards.”</i>")]
    s += [Body("Not: <i>“Award Win!”</i> — that's a headline, and it says nothing.")]
    s += [Spacer(1, 8),
          callout("The one exception to deleting empty sections",
                  "If you have even two or three awards, keep the Awards page. It's the "
                  "section prospective clients look for, and unlike News it doesn't look "
                  "stale when it's short — an award from 2024 is still an award.")]

    # ------------------------------------------------------ F · BRAND ------
    s += [*Section("F · Brand assets", 78 * mm)]
    s += [table(
        ["#", "I need", "Notes"],
        [["F1", "Logo files", "SVG preferred, otherwise high-res PNG with transparency. "
                              "Currently the logo is set in type"],
         ["F2", "Brand typeface", "Only if the practice has one and you hold a web licence. "
                                  "Otherwise I'll keep Jost + Inter, which are free"],
         ["F3", "Brand colour", "Optional. The site is deliberately monochrome so the "
                                "photography carries the colour. One accent at most"],
         ["F4", "Favicon source", "A square mark that reads at 32px — usually a monogram, "
                                  "not the full logo"]],
        [10 * mm, 34 * mm, None])]

    # ------------------------------------------------ G · PHOTOGRAPHY ------
    s += [*Section("G · Photography specification", 100 * mm)]
    s += [Lead("Give me the largest files you have. Do not resize, crop or compress "
               "anything first.")]
    s += [Body("The pipeline handles all of it automatically — resolution, colour mode, "
               "rotation, cropping, compression, renaming. Every manual edit you make "
               "first loses quality it cannot recover.")]
    s += [Spacer(1, 8)]
    s += [table(
        ["Property", "What I want"],
        [["File size", "The original. 10–15 MB is ideal. 50 MB is fine"],
         ["Format", "JPG, TIFF, PNG, HEIC, WebP — all handled"],
         ["Resolution", "Any. 300 DPI print files convert to 72 DPI automatically"],
         ["Colour", "Any. CMYK print files convert to RGB automatically"],
         ["Orientation", "Any. Camera rotation flags are applied automatically"],
         ["Minimum width",
          Paragraph("<b>2400px for heroes, 2000px for gallery.</b> Anything smaller gets "
                    "upscaled and will look soft", S["cell"])]],
        [34 * mm, None])]

    s += [KeepTogether([Spacer(1, 14), H2("What I cannot fix"), Rule(),
          bullets(["An image that is too small to begin with",
                   "A photograph that is out of focus or badly exposed",
                   "A screenshot of a photograph",
                   "Anything pulled from Instagram or WhatsApp — already compressed "
                   "and downsized"]),
          Body("Always go back to the photographer's original files.")])]

    # ------------------------------------------------------ H · LEGAL ------
    s += [*Section("H · Legal and admin", 86 * mm)]
    s += [table(
        ["#", "Item", "Why"],
        [["H1", "Photographer permission",
          "Most architectural photography is licensed, not sold. Publishing without "
          "permission is the most common legal problem practices hit"],
         ["H2", "Client permission",
          "Some private clients don't want their house identified or located"],
         ["H3", "Privacy policy",
          "Required in most jurisdictions if you add a contact form"],
         ["H4", "Hostinger login",
          "Only if you want me to walk you through the upload"]],
        [10 * mm, 42 * mm, None]), Spacer(1, 20)]

    # ------------------------------------------------ ORDER OF WORK --------
    s += [*Section("Suggested order of work", 100 * mm)]
    s += [Body("Do it in this sequence. Each step makes the site usable on its own, so "
               "you can stop at any point and still have something coherent.")]
    s += [Spacer(1, 8)]
    s += [checks([
        "<b>Section A — studio details.</b> Half an hour, and it removes every fake "
        "phone number and email address from the site.",
        "<b>Sections C1–C7 — the firm and the principals.</b> The highest-value writing "
        "you will do.",
        "<b>One complete project</b> — text and images. This proves the whole pipeline "
        "works and gives you a template for the rest.",
        "<b>Three to five more projects.</b>",
        "<b>Section B — the home page</b>, chosen from the images you now actually have.",
        "<b>Section E — news and awards</b>, only if there is something real.",
        "<b>Section F — logo and favicon.</b>",
        "<b>Sections G and H</b> — photographer credits and permissions, before you go live.",
    ])]

    # ------------------------------------------- MISSING CONTENT -----------
    s += [Spacer(1, 18), *Section("If something is missing", 100 * mm)]
    s += [table(
        ["Situation", "What I'll do"],
        [["Fewer projects than 12", "Delete the extra folders. The grid adapts"],
         ["No photo for one slot", "Leave the neutral grey placeholder — it reads as "
                                   "'coming soon', not as broken"],
         ["No project description yet", "One honest factual sentence. Never lorem ipsum, "
                                        "which reads as an abandoned site"],
         ["No team photos", "Delete the whole Team section"],
         ["No awards or press", "Delete those pages and their navigation tabs"],
         ["No logo file", "Keep the typographic logo — it suits this design anyway"],
         ["Photo too small", Paragraph("I'll flag it. You'll need a bigger original — "
                                       "<b>this one I can't work around</b>", S["cell"])]],
        [46 * mm, None])]

    s += [Spacer(1, 14),
          callout("The governing principle",
                  "<b>Ship less, complete.</b> Every visible placeholder costs more "
                  "credibility than the missing content would have earned. Cut the "
                  "section instead.")]

    # ------------------------------------------------ HOW TO SEND ----------
    s += [*Section("How to send it to me", 150 * mm)]
    s += [Body("There are fill-in forms in the <b>intake</b> folder. Open them in any "
               "text editor, type your answers under each heading, and hand them back. "
               "I'll convert them into the format the site needs.")]
    s += [Spacer(1, 6)]
    s += [table(
        ["Form", "Covers", "Required?"],
        [["01-studio-details", "Firm name, address, phone, emails, categories, home page",
          Paragraph("<b>Yes</b>", S["cellb"])],
         ["02-about", "The Firm, Design Philosophy, principals, team",
          Paragraph("<b>Yes</b>", S["cellb"])],
         ["03-projects", "One block per project — copy it 4–6 times",
          Paragraph("<b>Yes</b>", S["cellb"])],
         ["04-news-press-awards", "News, Press, Awards, Books — all optional", "No"]],
        [40 * mm, None, 22 * mm])]

    s += [Spacer(1, 12),
          Body("<b>Images:</b> drop them into the matching folder inside "
               "<b>image-prep/inbox</b> — there's a short README in each one explaining "
               "exactly what it produces — then run the processor. Or just tell me where "
               "they are and I'll sort it out.")]

    s += [Spacer(1, 12),
          callout("You don't have to fill in forms",
                  "Tell me about a project the way you'd describe it to someone, and I'll "
                  "draft the copy and hand it back for you to correct. Most people find "
                  "editing a draft far easier than facing a blank page.")]

    s += [KeepTogether([
        Rule(RULE, 0.5, before=10, after=8),
        Small("Full reference: <b>docs/WHAT-I-NEED-FROM-YOU.md</b> &nbsp;·&nbsp; "
              "Fill-in forms: <b>intake/</b> &nbsp;·&nbsp; "
              "How to replace things yourself: <b>docs/06-CONTENT-GUIDE.md</b>")])]

    doc = Doc(OUT)
    doc.build(s)
    print(f"Wrote {OUT}  ({os.path.getsize(OUT)//1024} KB)")


if __name__ == "__main__":
    build()
