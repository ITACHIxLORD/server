import math
import os
import sys
import time

# فعال‌سازی رنگ ANSI در ویندوز
if os.name == "nt":
    os.system("")

RED = "\033[91m"
PINK = "\033[95m"
WHITE = "\033[97m"
RESET = "\033[0m"

# --- فونت نقطه‌ای برای حروف اسم ---
FONT = {
    "r": ["# #", "# #", "#  ", "#  ", "#  "],
    "a": [" # ", "# #", "###", "# #", "# #"],
    "v": ["# #", "# #", "# #", " # ", " # "],
}


def build_text_matrix(name):
    """حروف اسم را کنار هم می‌چیند و یک ماتریس 0/1 می‌سازد."""
    rows = 5
    cols = []
    for i, ch in enumerate(name):
        glyph = FONT.get(ch.lower(), ["   "] * rows)
        cols.append(glyph)
        if i != len(name) - 1:
            cols.append([" "] * rows)  # فاصله بین حروف

    matrix = []
    for r in range(rows):
        line = []
        for glyph in cols:
            line.extend(1 if c == "#" else 0 for c in glyph[r])
        matrix.append(line)
    return matrix


def heart_points(size=1.0, layers=14):
    """قلب سه‌بعدی می‌سازد: چند لایه در عمق تا موقع چرخش ضخامت داشته باشد."""
    points = []
    for li in range(layers):
        # هر لایه کمی در عمق جابه‌جا می‌شود تا حجم ایجاد شود
        z = (li - (layers - 1) / 2) * 0.06 * size
        shrink = 1.0 - 0.04 * abs(li - (layers - 1) / 2)
        n = 220
        for i in range(n):
            t = 2 * math.pi * i / n
            hx = 16 * math.sin(t) ** 3
            hy = (
                13 * math.cos(t)
                - 5 * math.cos(2 * t)
                - 2 * math.cos(3 * t)
                - math.cos(4 * t)
            )
            x = hx * size * 0.07 * shrink
            y = -hy * size * 0.07 * shrink
            points.append((x, y, z))
    return points


def rotate_points(points, angle, tilt=0.35):
    """نقاط را حول محور عمودی و کمی حول محور افقی می‌چرخاند."""
    ca, sa = math.cos(angle), math.sin(angle)
    ct, st = math.cos(tilt), math.sin(tilt)
    out = []
    for x, y, z in points:
        # چرخش حول محور Y
        rx = x * ca + z * sa
        rz = -x * sa + z * ca
        # کمی چرخش حول محور X برای اینکه صفحه صاف نباشه
        ry = y * ct - rz * st
        rz2 = y * st + rz * ct
        out.append((rx, ry, rz2))
    return out


def scale_matrix(matrix, factor):
    """ماتریس را بزرگ می‌کند تا در ترمینال دیده شود."""
    h = len(matrix)
    w = len(matrix[0])
    out = [[0] * (w * factor) for _ in range(h * factor)]
    for r in range(h * factor):
        for c in range(w * factor):
            out[r][c] = matrix[r // factor][c // factor]
    return out


def render(points, width, height):
    """نقاط چرخیده را به بافر کاراکتری با سایه‌پردازی تبدیل می‌کند."""
    buf = [[" "] * width for _ in range(height)]
    depth = [[-1e9] * width for _ in range(height)]

    # مقیاس افقی مناسب ترمینال (کاراکترها بلندتر از عرض‌اند)
    sx = 26.0
    sy = 16.0

    for x, y, z in points:
        px = int(round(x * sx + width / 2))
        py = int(round(y * sy + height / 2))
        if 0 <= px < width and 0 <= py < height and z > depth[py][px]:
            depth[py][px] = z
            if z > 0.3:
                buf[py][px] = WHITE + "@" + RESET
            elif z > -0.3:
                buf[py][px] = PINK + "#" + RESET
            else:
                buf[py][px] = RED + "*" + RESET
    return buf


def make_points(matrix):
    """هر پیکسل ماتریس را به یک نقطه سه‌بعدی تبدیل می‌کند."""
    h = len(matrix)
    w = len(matrix[0])
    points = []
    for r in range(h):
        for c in range(w):
            if matrix[r][c]:
                x = (c - w / 2) * 0.5
                y = (r - h / 2) * 0.9  # کشیدگی عمودی برای ترمینال
                points.append((x, y, 0.0))
    return points


def heart_shell_points(name, size=1.0, layers=7, n=420, depth=0.55):
    """فقط پوسته‌ی قلب را با حروف اسم می‌سازد.

    برخلاف نسخه‌ی قبلی که کل داخل قلب را پر می‌کرد (و به یک بلوک حروف
    تبدیل می‌شد)، اینجا فقط نقاط نزدیک به مرز قلب نگه داشته می‌شوند تا
    هنگام چرخش، شکل قلب حفظ شود و حروف r/a/v سطح آن را بسازند.
    """
    chars = [c for c in name.lower() if c != " "] or ["*"]
    points = []
    for li in range(layers):
        # لایه‌های عمق: بیرونی‌ترین لایه‌ها کمی کوچک‌تر تا حس حجم بدهند
        z = (li - (layers - 1) / 2) * (depth / max(layers - 1, 1))
        shrink = 1.0 - 0.06 * abs(li - (layers - 1) / 2)
        for i in range(n):
            t = 2 * math.pi * i / n
            hx = 16 * math.sin(t) ** 3
            hy = (
                13 * math.cos(t)
                - 5 * math.cos(2 * t)
                - 2 * math.cos(3 * t)
                - math.cos(4 * t)
            )
            x = hx * size * 0.07 * shrink
            y = -hy * size * 0.07 * shrink
            ch = chars[i % len(chars)]
            points.append((x, y, z, ch))
    return points


def render_heart_name(points, width, height):
    """نقاط قلبِ حروف‌دار را به بافر کاراکتری تبدیل می‌کند."""
    buf = [[" "] * width for _ in range(height)]
    depth = [[-1e9] * width for _ in range(height)]

    # مقیاس افقی مناسب ترمینال (کاراکترها بلندتر از عرض‌اند)
    sx = 24.0
    sy = 14.0

    for x, y, z, ch in points:
        px = int(round(x * sx + width / 2))
        py = int(round(y * sy + height / 2))
        # فقط نزدیک‌ترین نقطه در هر پیکسل رندر شود تا شکل حفظ شود
        if 0 <= px < width and 0 <= py < height and z > depth[py][px]:
            depth[py][px] = z
            if z > 0.15:
                color = WHITE
            elif z > -0.15:
                color = PINK
            else:
                color = RED
            buf[py][px] = color + ch + RESET
    return buf


# --- وضعیت انیمیشن: هم برای ترمینال و هم برای مرورگر (Pyodide) مشترک است ---
_ANIM = {"points": [], "chars": [], "angle": 0.0, "width": 80, "height": 30}


def init_animation(name="rava", width=80, height=30):
    """حالت انیمیشن را می‌سازد (و دوباره ریست می‌کند).

    در مرورگر، index.html این تابع را موقع فشردن دکمه Run صدا می‌زند.
    """
    base_points = heart_shell_points(name, size=1.0)
    _ANIM["points"] = [(x, y, z) for x, y, z, _ in base_points]
    _ANIM["chars"] = [c for _, _, _, c in base_points]
    _ANIM["angle"] = 0.0
    _ANIM["width"] = width
    _ANIM["height"] = height
    return True


def next_frame(step=0.10):
    """یک فریم می‌سازد، زاویه را جلو می‌برد و متن خروجی را برمی‌گرداند.

    این تابع جایگزین حلقه‌ی `while True` + `time.sleep` شده است، چون در
    مرورگر آن حلقه صفحه را برای همیشه فریز می‌کند. مرورگر هر ~۵۰ میلی‌ثانیه
    یک بار این تابع را صدا می‌زند و منطق رندر کاملاً دست‌نخورده می‌ماند.
    """
    if not _ANIM["points"]:
        init_animation()

    angle = _ANIM["angle"]
    rotated = rotate_points(_ANIM["points"], angle)
    tagged = [(x, y, z, ch) for (x, y, z), ch in zip(rotated, _ANIM["chars"])]
    buf = render_heart_name(tagged, _ANIM["width"], _ANIM["height"])
    _ANIM["angle"] = angle + step
    return "\n".join("".join(row) for row in buf)


def main():
    # خودِ اسم "rava" پوسته‌ی قلب را می‌سازد و کل قلب می‌چرخد
    init_animation("rava", 80, 30)

    try:
        while True:
            os.system("cls" if os.name == "nt" else "clear")
            print(next_frame())
            time.sleep(0.05)
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
