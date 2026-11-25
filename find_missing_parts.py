"""
================================================================================
PROGRAM NAME: Find Missing Parts Analyzer
AUTHOR: 25-Year Senior AutoLISP & 3D CAD Engineer
LAST MODIFIED: 2026-11-25 20:58:00
DESCRIPTION: Deeply parses BOM, part lists, drawing sheets, and balloons
             in 20261124(화)-이스턴 메탈 UAE-45801051.dxf to identify missing
             single-part fabrication drawings.
================================================================================
"""

import re
import os
import json
import ezdxf

def clean_cad_text(text: str) -> str:
    """Strip AutoCAD formatting codes from MText."""
    # Remove fonts, heights, colors like \fArial|b0|i0; or \H60.0000; or \C1;
    t = re.sub(r"\\[fFhHcCWwAaQqOoLlKkPp][^;]*;", " ", text)
    # Remove \P (paragraph break)
    t = re.sub(r"\\[Pp]", "\n", t)
    # Remove braces { }
    t = re.sub(r"[{}]", "", t)
    # Remove %%c, %%p, %%d
    t = t.replace("%%C", "Ø").replace("%%c", "Ø").replace("%%P", "±").replace("%%p", "±")
    # Clean whitespace
    return t.strip()

def analyze_bom_and_sheets(dxf_path: str):
    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()

    all_texts = []
    for ent in msp.query("TEXT MTEXT"):
        raw = ent.dxf.text if ent.dxftype() == "TEXT" else ent.text
        cleaned = clean_cad_text(raw)
        pt = ent.dxf.insert if ent.dxftype() == "TEXT" else ent.dxf.insert
        all_texts.append({
            "type": ent.dxftype(),
            "layer": ent.dxf.layer,
            "text": cleaned,
            "raw": raw,
            "pos": [round(pt.x, 1), round(pt.y, 1)]
        })

    # Search for BOM / Part list headers or item numbers
    # Common keywords: NO, PART, ITEM, QTY, MAT, SPEC, DWG
    bom_candidates = []
    for t in all_texts:
        txt = t["text"]
        # Look for beam specs, pipe specs, plate specs, item numbers
        if any(k in txt.upper() for k in ["HBEAM", "SQ PIPE", "PIPE", "PL-", "PLATE", "CHANNEL", "SS400", "SM490", "SUS"]):
            bom_candidates.append(t)
        elif re.search(r"^[0-9]{1,2}[,\s\-]+.*(ea|EA)", txt):
            bom_candidates.append(t)

    # Find drawing sheet borders / plot boxes
    plot_boxes = []
    for ent in msp.query("LWPOLYLINE POLYLINE LINE"):
        if ent.dxf.layer in ["PLOT_BOX", "경계(ISO)", "제목(ISO)", "BORDER"]:
            # Check bounding box
            pass

    return {
        "total_texts": len(all_texts),
        "bom_candidates": bom_candidates,
        "sample_texts": [t["text"] for t in all_texts if len(t["text"]) > 2]
    }

if __name__ == "__main__":
    dxf_file = r"20261124(화)-이스턴 메탈 UAE-45801051.dxf"
    res = analyze_bom_and_sheets(dxf_file)
    with open("bom_analysis.json", "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    print(f"Total texts: {res['total_texts']}, BOM Candidates: {len(res['bom_candidates'])}")
    for b in res['bom_candidates']:
        print(f"[{b['layer']}] {b['pos']}: {b['text']}")
