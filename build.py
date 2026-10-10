#!/usr/bin/env python3
"""Genera docs/ (web + vCard + QR + PDF) para la tarjeta digital de Servicios Integrados "Velázquez".
Uso:  python3 build.py            (edita CONFIG abajo y vuelve a correr)"""
import base64, io, shutil, subprocess, urllib.parse
from pathlib import Path
import qrcode, qrcode.image.svg
from PIL import Image, ImageDraw, ImageFilter

CONFIG = {
    "phones": ["8132725743", "8124042499"],  # en orden: cel principal, cel 2
    "whatsapp": "8124042499",  # el que tiene WhatsApp Business
    "url": "https://hadezib.github.io/jorge-servicios/",
    "fb": "https://www.facebook.com/jorge.moreno.56878",
    "messenger": "https://m.me/jorge.moreno.56878",
    "wa_msg": "¡Hola! Vi la tarjeta de Servicios Integrados Velázquez y necesito un servicio 🔧\nEquipo y marca: \nQué falla tiene: \nColonia: ",
}

ROOT = Path(__file__).parent
SRC, DIST = ROOT / "src", ROOT / "docs"  # docs/ = lo que publica GitHub Pages
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def qr_svg(url):
    img = qrcode.make(url, image_factory=qrcode.image.svg.SvgPathImage, border=0,
                      error_correction=qrcode.constants.ERROR_CORRECT_M)
    svg = img.to_string(encoding="unicode")
    return svg[svg.index("<svg"):]


def vcard(c, tels):
    photo = io.BytesIO()
    Image.open(ROOT / "img/logo.jpg").resize((240, 240)).save(photo, "JPEG", quality=80)
    b64 = base64.b64encode(photo.getvalue()).decode()
    lines = [
        "BEGIN:VCARD", "VERSION:3.0",
        "N:;Servicios Integrados Velázquez;;;", "FN:Servicios Integrados Velázquez",
        "ORG:Servicios Integrados Velázquez", "TITLE:Refrigeración\\, línea blanca y aire acondicionado",
    ] + [f"TEL;TYPE=CELL,VOICE{',PREF' if i == 0 else ''}:{t}" for i, t in enumerate(tels)] + [
        f"URL:{c['url']}",
        f"X-SOCIALPROFILE;TYPE=facebook:{c['fb']}",
        "ADR;TYPE=WORK:;;;Monterrey;Nuevo León;;México",
        "NOTE:Mantenimiento y reparación a domicilio: refrigeradores\\, lavadoras\\, secadoras\\, minisplits\\, vitrinas\\, cámaras de refrigeración y fábricas de hielo.",
    ]
    photo_line = "PHOTO;ENCODING=b;TYPE=JPEG:" + b64
    folded = [photo_line[:75]] + [" " + photo_line[i:i + 74] for i in range(75, len(photo_line), 74)]
    return "\r\n".join(lines + folded + ["END:VCARD", ""])


def og_image():
    bg = Image.open(ROOT / "img/condensadora.jpg").convert("RGB")
    w, h = 1200, 630
    bg = bg.resize((w, int(bg.height * w / bg.width))).crop((0, 80, w, 80 + h)).filter(ImageFilter.GaussianBlur(3))
    bg = Image.blend(bg, Image.new("RGB", (w, h), (3, 4, 9)), 0.45)
    logo = Image.open(ROOT / "img/logo.jpg").resize((460, 460))
    mask = Image.new("L", (460, 460), 0); ImageDraw.Draw(mask).ellipse((0, 0, 459, 459), fill=255)
    bg.paste(logo, ((w - 460) // 2, (h - 460) // 2), mask)
    bg.save(DIST / "img/og.jpg", quality=85)


def main():
    c = CONFIG
    clean = lambda n: "".join(ch for ch in n if ch.isdigit())[-10:]
    show = lambda d: f"{d[:2]} {d[2:6]} {d[6:]}"
    nums = [clean(n) for n in c["phones"]]
    wa = clean(c["whatsapp"])
    tokens = {"{{WA}}": "52" + wa, "{{WA_SHOW}}": show(wa)}
    for i, d in enumerate(nums, 1):
        tokens[f"{{{{TEL{i}}}}}"] = "+52" + d
        tokens[f"{{{{TEL{i}_SHOW}}}}"] = show(d)
    tokens.update({
        "{{WA_MSG}}": urllib.parse.quote(c["wa_msg"]),
        "{{URL}}": c["url"], "{{URL_SHOW}}": c["url"].split("//")[1].rstrip("/"),
        "{{FB}}": c["fb"], "{{MSGR}}": c["messenger"], "{{QR}}": qr_svg(c["url"]),
    })
    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(SRC, DIST)
    shutil.copytree(ROOT / "img", DIST / "img")
    for name in ("index.html", "pdf.html"):
        p = DIST / name
        html = p.read_text()
        for k, v in tokens.items():
            html = html.replace(k, v)
        p.write_text(html)
    (DIST / "contacto.vcf").write_text(vcard(c, ["+52" + d for d in nums]))
    (DIST / ".nojekyll").write_text("")
    og_image()
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    "--virtual-time-budget=8000", "--run-all-compositor-stages-before-draw",
                    f"--print-to-pdf={DIST / 'Servicios-Integrados-Velazquez.pdf'}", (DIST / "pdf.html").as_uri()],
                   check=True, capture_output=True)
    print("OK ->", DIST, "| tels:", [show(d) for d in nums], "| wa:", show(wa))


if __name__ == "__main__":
    main()
