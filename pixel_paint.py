from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os, sys

# ---------------- AYARLAR ----------------
input_image = "ceyda.jpg"        # Fotoğraf dosyası adı (root dizinde olmalı)
output_image = "pixel_art_numbered.png"
pixel_size = 50                  # Kaç piksele küçültülsün
color_count = 20                 # Kaç renk olsun
cell_size = 20                   # Her karenin piksel boyutu
crop_mode = "pad"                # "crop" veya "pad"
# -----------------------------------------

# Dosya kontrolü
if not os.path.exists(input_image):
    print(f"Hata: '{input_image}' bulunamadı. Fotoğraf aynı klasörde mi?")
    sys.exit(1)

# Fotoğrafı aç ve kare yap
img = Image.open(input_image).convert("RGB")
w, h = img.size

if crop_mode == "crop":
    min_side = min(w, h)
    img = img.crop(((w - min_side)//2, (h - min_side)//2, (w + min_side)//2, (h + min_side)//2))
else:
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

# Renk rehberi sözlüğü
color_map = {i+1: colors[i] for i in range(len(colors))}

# Çıktı görseli oluştur (numaralı piksel şablonu)
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
        idx = int(labels[y, x]) + 1  # 1’den başlasın
        x0, y0 = x * cell_size, y * cell_size
        draw.rectangle([x0, y0, x0+cell_size-1, y0+cell_size-1], outline=(200,200,200))
        text = str(idx)
        if font:
            draw.text((x0+3, y0+2), text, fill=(0,0,0), font=font)
        else:
            draw.text((x0+3, y0+2), text, fill=(0,0,0))

# Kaydet
out.save(output_image)
print(f"✅ Çıktı oluşturuldu: {output_image}")

# ------------------ RENK REHBERİ ------------------
# TXT olarak
txt_path = os.path.join(os.getcwd(), "renk_tablosu.txt")
with open(txt_path, "w") as f:
    for idx, color in color_map.items():
        hex_color = "#{:02x}{:02x}{:02x}".format(*color)
        f.write(f"{idx}: {hex_color}\n")

# Görsel olarak
guide_width = 300
guide_height = len(color_map) * 30
guide = Image.new("RGB", (guide_width, guide_height), "white")
draw_guide = ImageDraw.Draw(guide)

for i, (idx, color) in enumerate(color_map.items()):
    y = i * 30
    draw_guide.rectangle([0, y, 40, y + 30], fill=color)
    hex_color = "#{:02x}{:02x}{:02x}".format(*color)
    if font:
        draw_guide.text((50, y + 8), f"{idx} → {hex_color}", fill="black", font=font)
    else:
        draw_guide.text((50, y + 8), f"{idx} → {hex_color}", fill="black")

guide.save("color_guide.png")
print(f"✅ Renk rehberi oluşturuldu: renk_tablosu.txt ve color_guide.png")
