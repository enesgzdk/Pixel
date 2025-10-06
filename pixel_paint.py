from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os, sys

# ---------------- AYARLAR ----------------
input_image = "2.jpeg"      # Fotoğraf dosyası adı (aynı klasörde olmalı)
output_image = "pixel_art_numbered.png"
pixel_size = 50                         # Kaç piksele küçültülsün (örn. 50x50)
color_count = 20                        # Kaç farklı renk kullanılacak
cell_size = 20                          # Her karenin piksel boyutu (çıktı boyutu)
crop_mode = "pad"                       # "crop" veya "pad"
# -----------------------------------------

# Dosya kontrolü
if not os.path.exists(input_image):
    print(f"Hata: '{input_image}' bulunamadı. Fotoğraf aynı klasörde mi?")
    sys.exit(1)

# Fotoğrafı aç ve kare yap
img = Image.open(input_image).convert("RGB")
w, h = img.size

if crop_mode == "crop":
    # Orta kısmı kırp
    min_side = min(w, h)
    img = img.crop(((w - min_side)//2, (h - min_side)//2, (w + min_side)//2, (h + min_side)//2))
else:
    # Kenarlara beyaz ekle
    max_side = max(w, h)
    canvas = Image.new("RGB", (max_side, max_side), (255, 255, 255))
    canvas.paste(img, ((max_side - w)//2, (max_side - h)//2))
    img = canvas

# Küçült (pikselleştir)
img_small = img.resize((pixel_size, pixel_size), Image.NEAREST)

# Renkleri azalt (quantize)
img_quant = img_small.quantize(colors=color_count, method=Image.MEDIANCUT)
labels = np.array(img_quant)

# Paletten RGB renkleri al
palette = img_quant.getpalette()
colors = []
for i in range(color_count):
    r, g, b = palette[3*i], palette[3*i+1], palette[3*i+2]
    colors.append((r, g, b))

# Çıktı görseli oluştur
out_w = pixel_size * cell_size
out_h = pixel_size * cell_size
out = Image.new("RGB", (out_w, out_h), (255, 255, 255))
draw = ImageDraw.Draw(out)

# Yazı tipi
try:
    font = ImageFont.truetype("Arial.ttf", size=max(10, cell_size//2))
except:
    font = None

for y in range(pixel_size):
    for x in range(pixel_size):
        idx = int(labels[y, x])
        x0, y0 = x * cell_size, y * cell_size
        draw.rectangle([x0, y0, x0+cell_size-1, y0+cell_size-1], outline=(200,200,200))
        text = str(idx+1)
        if font:
            draw.text((x0+3, y0+2), text, fill=(0,0,0), font=font)
        else:
            draw.text((x0+3, y0+2), text, fill=(0,0,0))

# Kaydet
out.save(output_image)
print(f"✅ Çıktı oluşturuldu: {output_image}")
