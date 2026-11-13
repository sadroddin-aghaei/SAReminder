from PIL import Image, ImageDraw, ImageFont
im = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
d.rounded_rectangle((40, 40, 984, 984), 220, fill=(255, 48, 48, 255))
for f in ("arialbd.ttf", "Arial Bold.ttf", "DejaVuSans-Bold.ttf"):
    try: font = ImageFont.truetype(f, 520); break
    except OSError: font = ImageFont.load_default(size=520)
d.text((512, 512), "SA", font=font, fill=(0, 0, 0, 255), anchor="mm")
im.save("assets/icon.ico", sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)]); im.save("assets/icon.icns")
