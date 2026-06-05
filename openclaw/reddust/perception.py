"""Perception tools: turn pixels into text a *non-multimodal* agent can use.

The Red Dust agent (e.g. deepseek-v4-pro via openclaw) can't see images.  This
module is the bridge — auxiliary tools a task's ``tools.py`` can expose so a
text-only agent can still attempt visual tasks:

* :func:`ocr_text` — read printed text/digits (Tesseract, fed via stdin so it
  works regardless of temp-dir sandboxing).
* :func:`ocr_digit_with_rotation` — for tile/jigsaw tasks: the orientation at
  which a glyph reads upright reveals the piece's rotation.
* :func:`describe_image` — cheap, dependency-free visual features (size,
  dominant colour) for spatial reasoning.

Backends are pluggable.  Tesseract is the lightweight default (English/digits
out of the box; Chinese needs the ``chi_sim`` traineddata).  For full
PDF/table/figure extraction, a heavier backend (MinerU / PaddleOCR) can be
slotted behind :func:`read_document` later — see README.
"""
import io
import shutil
import subprocess

from PIL import Image

_TESS = "tesseract"


def ocr_available() -> bool:
    return shutil.which(_TESS) is not None


def list_langs() -> list[str]:
    if not ocr_available():
        return []
    p = subprocess.run([_TESS, "--list-langs"], capture_output=True)
    lines = p.stdout.decode("utf-8", "replace").splitlines()
    return [ln.strip() for ln in lines[1:] if ln.strip()]


def _png_bytes(image) -> bytes:
    if isinstance(image, (bytes, bytearray)):
        return bytes(image)
    if isinstance(image, str):
        with open(image, "rb") as f:
            return f.read()
    buf = io.BytesIO()
    image.convert("RGB").save(buf, format="PNG")
    return buf.getvalue()


def _run_tess(png: bytes, psm: int, lang: str = "eng", extra=None) -> str:
    if not ocr_available():
        return ""
    cmd = [_TESS, "stdin", "stdout", "--psm", str(psm), "-l", lang] + (extra or [])
    try:
        p = subprocess.run(cmd, input=png, capture_output=True, timeout=30)
    except Exception:
        return ""
    return p.stdout.decode("utf-8", "replace").strip()


def ocr_text(image, lang: str = "eng", psm: int = 6) -> str:
    """OCR an image (PIL Image / path / PNG bytes) → text. '' if unavailable."""
    return _run_tess(_png_bytes(image), psm, lang)


def detect_tile_rotation(image) -> int:
    """Rotation (0/90/180/270) of a tile, read from a dark orientation marker
    placed in the upright top-left corner — robust + digit-agnostic."""
    img = Image.open(image).convert("L") if isinstance(image, str) else image.convert("L")
    w, h = img.size
    s = max(8, min(w, h) // 4)
    corners = {0: (0, 0, s, s), 90: (w - s, 0, w, s),
               180: (w - s, h - s, w, h), 270: (0, h - s, s, h)}

    def brightness(box):
        data = img.crop(box).tobytes()
        return sum(data) / (len(data) or 1)

    means = {r: brightness(b) for r, b in corners.items()}
    return min(means, key=means.get)            # darkest corner = where the marker is


def ocr_digit(image):
    """Read a single centered digit (0-9) from a tile, or None. Crops out the
    border/marker, binarizes, upscales, pads with a white margin, and takes a
    majority vote across page-seg modes for a reliable single-char read."""
    img = Image.open(image).convert("RGB") if isinstance(image, str) else image.convert("RGB")
    w, h = img.size
    c = img.crop((int(w * 0.16), int(h * 0.16), int(w * 0.84), int(h * 0.84))).convert("L")
    c = c.resize((c.width * 8, c.height * 8)).point(lambda p: 0 if p < 120 else 255)
    pad = 80
    canvas = Image.new("L", (c.width + 2 * pad, c.height + 2 * pad), 255)
    canvas.paste(c, (pad, pad))
    png = _png_bytes(canvas)
    votes: dict[str, int] = {}
    for psm in (10, 8, 7, 13):
        out = _run_tess(png, psm, extra=["-c", "tessedit_char_whitelist=0123456789"])
        ds = [ch for ch in out if ch.isdigit()]
        if len(ds) == 1:
            votes[ds[0]] = votes.get(ds[0], 0) + 1
    return max(votes, key=votes.get) if votes else None


def read_tile(image):
    """Perceive a jigsaw tile → ``(digit, rotation)`` (digit None for distractors)."""
    img = Image.open(image).convert("RGB") if isinstance(image, str) else image.convert("RGB")
    rot = detect_tile_rotation(img)
    return ocr_digit(img.rotate(rot, expand=False)), rot


def ocr_digit_with_rotation(image, digits: str = "012345678"):
    """Return ``(digit, rotation)`` where ``rotation`` ∈ {0,90,180,270} is the
    angle at which a single digit reads upright, or ``(None, None)``."""
    img = Image.open(image).convert("RGB") if isinstance(image, str) else image
    for rot in (0, 90, 180, 270):
        txt = ocr_text(img.rotate(rot, expand=False), psm=10)
        hit = "".join(c for c in txt if c in digits)
        if len(hit) == 1:
            # rotating the stored piece by `rot` made it upright → it was
            # rotated by `rot` clockwise relative to upright.
            return hit, rot
    return None, None


def describe_image(image) -> dict:
    """Cheap, dependency-free features for spatial reasoning (no OCR)."""
    img = (Image.open(image).convert("RGB") if isinstance(image, str)
           else image.convert("RGB"))
    w, h = img.size
    dominant = list(img.resize((1, 1)).getpixel((0, 0)))
    return {"size": [w, h], "dominant_rgb": dominant}


def read_document(path: str) -> str:  # pragma: no cover - backend stub
    """PDF/document → structured text.  Stub for a heavy backend (MinerU /
    PaddleOCR) installed on demand for doc-heavy tasks; falls back to Tesseract
    on a single image.  Raises if no document backend is available."""
    if path.lower().endswith((".png", ".jpg", ".jpeg", ".tif", ".tiff")):
        return ocr_text(path)
    raise NotImplementedError(
        "PDF/document parsing needs a backend (e.g. MinerU). "
        "Install it and wire it here for doc-heavy RD-PF tasks.")
