from PIL import Image, ImageDraw

# position to "X" lines
def pos_to_lines(pos, line_length):
    x, y = pos
    return [
        ((x - line_length / 2, y - line_length / 2), (x + line_length / 2, y + line_length / 2)),
        ((x + line_length / 2, y - line_length / 2), (x - line_length / 2, y + line_length / 2))
    ]

def draw_x_at(img, pos, t=2, color='blue', length=10):
    copy = img.copy()
    draw = ImageDraw.Draw(copy)
    for line in pos_to_lines(pos, length):
        draw.line(line, fill=color, width=t)
    return copy

def composite_at(background, foreground, pos):
    if background.mode != 'RGBA':
        background = background.convert('RGBA')

    tmp_img = Image.new('RGBA', background.size, (0, 0, 0, 0))
    tmp_img.paste(foreground, pos)
    return Image.alpha_composite(background, tmp_img)