"""TDD for the perception layer — pixels→text tools for a non-multimodal agent."""

from pathlib import Path

import pytest
from PIL import Image, ImageDraw, ImageFont

from openclaw.reddust import perception

_FONTS = [
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/Library/Fonts/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]
_FONT = next((f for f in _FONTS if Path(f).exists()), None)

_CJK_FONTS = [
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/Supplemental/Songti.ttc",
]
_CJK = next((f for f in _CJK_FONTS if Path(f).exists()), None)


def _render(text, size=44, w=420, h=90):
    img = Image.new("RGB", (w, h), "white")
    ImageDraw.Draw(img).text((10, 18), text, fill="black",
                             font=ImageFont.truetype(_FONT, size))
    return img


@pytest.mark.skipif(not perception.ocr_available() or _FONT is None,
                    reason="tesseract or a TrueType font unavailable")
def test_ocr_reads_english_and_digits():
    txt = perception.ocr_text(_render("B2 STORAGE 42"), psm=7)
    assert "42" in txt and "STORAGE" in txt.upper()


@pytest.mark.skipif(not perception.ocr_available() or _FONT is None,
                    reason="tesseract or a TrueType font unavailable")
def test_ocr_recovers_digit_and_rotation_from_a_tile():
    """The orientation at which a digit reads upright reveals the tile's rotation
    — this is what makes the CI-03 jigsaw perceivable by a text agent."""
    tile = Image.new("RGB", (100, 100), (210, 214, 240))
    ImageDraw.Draw(tile).text((34, 14), "6", fill=(20, 20, 20),
                              font=ImageFont.truetype(_FONT, 60))
    # gen_ci03_fragments stores a tile as upright.rotate(-applied) (clockwise);
    # the perceiver must recover that applied angle.
    applied = 90
    stored = tile.rotate(-applied, expand=False)
    digit, rot = perception.ocr_digit_with_rotation(stored)
    assert digit == "6"
    assert rot == applied


@pytest.mark.skipif("chi_sim" not in perception.list_langs() or _CJK is None,
                    reason="chi_sim traineddata or a CJK font unavailable")
def test_ocr_reads_chinese_with_chi_sim():
    img = Image.new("RGB", (560, 90), "white")
    ImageDraw.Draw(img).text((12, 16), "净水 危险 撤离", fill="black",
                             font=ImageFont.truetype(_CJK, 46))
    txt = perception.ocr_text(img, lang="chi_sim", psm=7)
    assert "净水" in txt and "危险" in txt        # common terms read reliably


def test_describe_image_reports_size_and_dominant_color():
    img = Image.new("RGB", (120, 80), (200, 210, 240))   # bluish
    d = perception.describe_image(img)
    assert d["size"] == [120, 80]
    assert d["dominant_rgb"][2] > d["dominant_rgb"][0]


def test_ocr_text_returns_str_and_never_raises_on_blank():
    assert isinstance(perception.ocr_text(Image.new("RGB", (50, 50), "white")), str)
