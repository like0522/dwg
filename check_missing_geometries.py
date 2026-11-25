import ezdxf
import re

doc = ezdxf.readfile("20261124(화)-이스턴 메탈 UAE-45801051.dxf")
msp = doc.modelspace()

# Collect all geometry primitives in Y < -75000
geoms = []
for e in msp:
    if e.dxftype() in ("LINE", "CIRCLE", "ARC", "LWPOLYLINE"):
        if e.dxftype() == "LINE":
            pts = [(e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)]
        elif e.dxftype() in ("CIRCLE", "ARC"):
            c = e.dxf.center
            r = e.dxf.radius
            pts = [(c.x - r, c.y - r), (c.x + r, c.y + r)]
        elif e.dxftype() == "LWPOLYLINE":
            pts = [(p[0], p[1]) for p in e.get_points()]
        ys = [p[1] for p in pts]
        xs = [p[0] for p in pts]
        if max(ys) < -75000:
            geoms.append({
                "type": e.dxftype(),
                "min_x": min(xs), "max_x": max(xs),
                "min_y": min(ys), "max_y": max(ys),
                "cx": sum(xs)/len(xs), "cy": sum(ys)/len(ys)
            })

# Collect item texts for 45801051 and 45801052
items_51 = []
items_52 = []
for e in msp.query("TEXT MTEXT"):
    pt = e.dxf.insert
    if pt.y < -104900:
        txt = e.dxf.text if e.dxftype() == "TEXT" else e.text
        m = re.match(r"^([0-9]{1,2})\.\s*(.*)", txt.strip())
        if m:
            item = {
                "no": int(m.group(1)),
                "spec": m.group(2),
                "x": round(pt.x, 1),
                "y": round(pt.y, 1)
            }
            if pt.x < 382000:
                items_51.append(item)
            else:
                items_52.append(item)

def check_items(items, title):
    print(f"\n=== {title} ===")
    # Group by column (x)
    cols = {}
    for it in items:
        col_x = round(it["x"] / 500) * 500
        cols.setdefault(col_x, []).append(it)
    
    for col_x, col_items in sorted(cols.items()):
        col_items.sort(key=lambda i: -i["y"]) # top to bottom (y descending)
        for idx, it in enumerate(col_items):
            y_top = it["y"] - 5 # just below the text baseline
            y_bot = col_items[idx+1]["y"] + 10 if idx + 1 < len(col_items) else it["y"] - 800
            x_left = it["x"] - 50
            x_right = it["x"] + 1400 # width of column
            
            # Find geometries inside this item's zone (between this text and next text)
            matched = [
                g for g in geoms
                if x_left <= g["cx"] <= x_right and y_bot <= g["cy"] <= y_top
            ]
            status = "OK (작도됨)" if len(matched) > 0 else "MISSING (단품도 누락!)"
            print(f"  Item {it['no']:2d} | {it['spec']:28s} | Y={it['y']:9.1f} | Shapes: {len(matched):2d} -> {status}")

check_items(items_51, "DWG NO. 45801051 (이스턴 메탈)")
check_items(items_52, "DWG NO. 45801052 (아콘 판넬 그리스)")
