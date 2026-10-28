"""Minimal check that the wheel loads and its bundled codecs work on this glibc."""
import io
import platform
import sys

from PIL import Image, features

print(f"python {platform.python_version()} ({sys.executable})")
print("Pillow", features.version("pil"))
for codec in ("jpg", "jpg_2000", "zlib", "libtiff", "webp", "freetype2", "littlecms2", "avif"):
    assert features.check(codec), f"{codec} support missing"
    print(f"  {codec:12} {features.version(codec)}")

img = Image.new("RGB", (64, 48), (200, 30, 90))
for fmt in ("JPEG", "PNG", "WEBP", "TIFF"):
    buf = io.BytesIO()
    img.save(buf, fmt)
    buf.seek(0)
    back = Image.open(buf)
    back.load()
    assert back.size == img.size, fmt
    print(f"  {fmt} roundtrip ok ({buf.getbuffer().nbytes} bytes)")
print("OK")
