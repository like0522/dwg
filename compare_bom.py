"""
================================================================================
PROGRAM NAME: Compare BOM vs Single-Part Drawings
AUTHOR: 25-Year Senior AutoLISP & 3D CAD Engineer
LAST MODIFIED: 2026-11-25 21:05:00
================================================================================
"""

import json
import re
import ezdxf

def parse_bom_and_details():
    doc = ezdxf.readfile("20261124(화)-이스턴 메탈 UAE-45801051.dxf")
    msp = doc.modelspace()

    # Collect all texts
    texts = []
    for ent in msp.query("TEXT MTEXT"):
        raw = ent.dxf.text if ent.dxftype() == "TEXT" else ent.text
        # Clean
        t = re.sub(r"\\[fFhHcCWwAaQqOoLlKkPp][^;]*;", " ", raw)
        t = re.sub(r"\\[Pp]", " / ", t)
        t = re.sub(r"[{}]", "", t)
        t = t.replace("%%C", "Ø").replace("%%c", "Ø").replace("%%P", "±").replace("%%p", "±")
        cln = " ".join(t.split()).strip()
        if cln:
            texts.append({
                "x": round(ent.dxf.insert.x, 1),
                "y": round(ent.dxf.insert.y, 1),
                "layer": ent.dxf.layer,
                "text": cln
            })

    # 1. Filter BOM of 45801051 (Y < -90000, X around 377000~380000)
    bom_45801051 = []
    for t in texts:
        if t["y"] < -90000 and 376000 < t["x"] < 381000:
            m = re.match(r"^([0-9]{1,2})\.\s*(.*)", t["text"])
            if m:
                num = int(m.group(1))
                spec = m.group(2)
                bom_45801051.append({
                    "item_no": num,
                    "spec": spec,
                    "pos": (t["x"], t["y"])
                })
    bom_45801051.sort(key=lambda x: x["item_no"])

    # 2. Look at the upper region (Y > -70000) where drawing sheets are placed
    # Let's inspect drawing titles, sheet title blocks, part numbers
    # Each drawing sheet typically has DWG NO, TITLE, or part callouts
    upper_texts = [t for t in texts if t["y"] > -75000]

    # Let's see what parts are mentioned in upper_texts
    # Check for part callouts, e.g. "1.", "NO. 1", or beam specs
    return {
        "bom_items": bom_45801051,
        "upper_texts_count": len(upper_texts),
        "upper_texts": upper_texts
    }

if __name__ == "__main__":
    res = parse_bom_and_details()
    print("=== BOM 45801051 ITEMS (조립도 BOM 목록) ===")
    for b in res["bom_items"]:
        print(f"  Item {b['item_no']:2d}: {b['spec']}")

    print("\n=== UPPER REGION TEXTS (단품도/상세도 영역) ===")
    # Group upper texts by sheets (clusters by X)
    sheets = {}
    for t in res["upper_texts"]:
        # Sheet bands by X (around 380000, 390000, 400000 etc.)
        sheet_id = round(t["x"] / 9000)
        sheets.setdefault(sheet_id, []).append(t)

    for sid, stexts in sorted(sheets.items()):
        print(f"\n--- SHEET CLUSTER (X approx {sid*9000}) ({len(stexts)} texts) ---")
        for st in stexts:
            # print notable texts like titles, specs, drawing numbers
            txt = st["text"]
            if any(k in txt for k in ["45801", "H2", "HBEAM", "SQ", "PIPE", "각관", "STAND", "FRAME", "DWG", "PART", "SCALE", "1 :", "Sec", "View", "NOTE", "DETAIL", "EA"]):
                print(f"    ({st['x']}, {st['y']}): {txt}")
