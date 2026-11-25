"""
================================================================================
PROGRAM NAME: Sheet Cluster & Part List Inspector
AUTHOR: 25-Year Senior AutoLISP & 3D CAD Engineer
LAST MODIFIED: 2026-11-25 21:00:00
================================================================================
"""

import json
import ezdxf
import re

def clean_cad_text(text: str) -> str:
    t = re.sub(r"\\[fFhHcCWwAaQqOoLlKkPp][^;]*;", " ", text)
    t = re.sub(r"\\[Pp]", " / ", t)
    t = re.sub(r"[{}]", "", t)
    t = t.replace("%%C", "Ø").replace("%%c", "Ø").replace("%%P", "±").replace("%%p", "±")
    return " ".join(t.split()).strip()

def cluster_sheets():
    doc = ezdxf.readfile("20261124(화)-이스턴 메탈 UAE-45801051.dxf")
    msp = doc.modelspace()

    # Find all PLOT_BOX rectangles or large polylines/rectangles
    boxes = []
    for ent in msp.query("LWPOLYLINE"):
        pts = [(p[0], p[1]) for p in ent.get_points()]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        w = max_x - min_x
        h = max_y - min_y
        if w > 2000 and h > 1500:
            boxes.append({
                "layer": ent.dxf.layer,
                "bbox": [min_x, min_y, max_x, max_y],
                "w": round(w, 1),
                "h": round(h, 1)
            })

    # Collect all texts
    texts = []
    for ent in msp.query("TEXT MTEXT"):
        raw = ent.dxf.text if ent.dxftype() == "TEXT" else ent.text
        cln = clean_cad_text(raw)
        pt = ent.dxf.insert
        if cln:
            texts.append({
                "x": round(pt.x, 1),
                "y": round(pt.y, 1),
                "layer": ent.dxf.layer,
                "text": cln
            })

    # Group texts by X coordinate intervals (e.g. step of 5000 or 10000)
    # Sort texts by X, then Y
    texts.sort(key=lambda t: (t["x"], t["y"]))

    res = {
        "boxes": boxes,
        "all_texts": texts
    }

    with open("sheet_clusters.json", "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)

    print(f"Detected {len(boxes)} large boxes, {len(texts)} texts.")
    # Print distinct clusters
    print("\n--- SAMPLE TEXTS BY REGION ---")
    current_band = None
    for t in texts:
        band = round(t["x"] / 5000) * 5000
        if band != current_band:
            current_band = band
            print(f"\n=== REGION X approx {band} ===")
        print(f"  ({t['x']}, {t['y']}) [{t['layer']}]: {t['text']}")

if __name__ == "__main__":
    cluster_sheets()
