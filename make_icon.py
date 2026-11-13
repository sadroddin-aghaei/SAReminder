from PIL import Image, ImageDraw
K = 8; ACC = (255, 48, 48, 255)
def bez(p0, p1, p2, p3, n=24):
    out = []
    for i in range(n + 1):
        t = i / n; u = 1 - t
        out.append((u**3*p0[0]+3*u*u*t*p1[0]+3*u*t*t*p2[0]+t**3*p3[0], u**3*p0[1]+3*u*u*t*p1[1]+3*u*t*t*p2[1]+t**3*p3[1]))
    return out
pts = bez((32,88),(40,80),(42,70),(42,56)) + bez((42,56),(42,40),(52,32),(64,32)) + bez((64,32),(76,32),(86,40),(86,56)) + bez((86,56),(86,70),(88,80),(96,88))
im = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
d.rounded_rectangle((32, 32, 992, 992), 224, fill=ACC)
d.polygon([(x*K, y*K) for x, y in pts], fill="white"); d.ellipse((60*K, 22*K, 68*K, 30*K), fill="white"); d.ellipse((55*K, 92*K, 73*K, 104*K), fill="white")
im.save("assets/icon.png"); im.save("assets/icon.ico", sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)]); im.save("assets/icon.icns")
