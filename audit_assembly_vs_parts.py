import ezdxf
import re

def clean_cad_text(text: str) -> str:
    t = re.sub(r"\\[fFhHcCWwAaQqOoLlKkPp][^;]*;", " ", text)
    t = re.sub(r"\\[Pp]", " / ", t)
    t = re.sub(r"[{}]", "", t)
    t = t.replace("%%C", "Ø").replace("%%c", "Ø").replace("%%P", "±").replace("%%p", "±")
    return " ".join(t.split()).strip()

doc = ezdxf.readfile("20261124(화)-이스턴 메탈 UAE-45801051.dxf")
msp = doc.modelspace()

# 1. Identify all sheets in Y > -75000 by their DWG NO.
# Let's print all non-trivial texts & dimensions grouped by X range for each assembly sheet
sheets = [
    ("Sheet 1: 45801051 (FRAME)", 374000, 387500),
    ("Sheet 2: 45801052 (STAND)", 387500, 397000),
    ("Sheet 3: 45801053 (STAND)", 397000, 407000),
]

for name, x_min, x_max in sheets:
    print(f"\n==========================================")
    print(f"{name} (X: {x_min} ~ {x_max})")
    print(f"==========================================")
    
    # Texts / Callouts (excluding grid labels A-F, 1-8 and standard title block labels)
    skip_words = {"A", "B", "C", "D", "E", "F", "1", "2", "3", "4", "5", "6", "7", "8",
                  "DIMENSION", "SIZE", "MATERIAL", "SCALE", "WEIGHT", "PART NO.", "PROJECTION",
                  "HEAT TREATMENT", "PAINTING OR SURFACE TREATMENT", "SHEET", "/", "DRAWN",
                  "DESIGNED", "APPROVED", "CHECKED", "MACHINED", "SURFACE TEXTURE",
                  "UNLESS SPECIFIED", "DIM. TOLERANCE", "REV", "DATE", "DESCRIPTION",
                  "APPROVED_DATE", "ISSUE", "00", "mm", "A2", "6.3", "25", "( )", "` 0.05"}
    
    callouts = []
    for e in msp.query("TEXT MTEXT"):
        pt = e.dxf.insert
        if pt.y > -75000 and x_min <= pt.x < x_max:
            raw = e.dxf.text if e.dxftype() == "TEXT" else e.text
            cln = clean_cad_text(raw)
            if cln and cln not in skip_words:
                callouts.append((round(pt.x, 1), round(pt.y, 1), e.dxf.layer, cln))
    
    callouts.sort(key=lambda c: (-c[1], c[0]))
    print(f"--- Callouts & Annotations ({len(callouts)}) ---")
    for x, y, l, t in callouts:
        print(f"  ({x:8.1f}, {y:8.1f}) [{l}]: {t}")

    # Dimensions summary (unique measured values > 20mm)
    dims = []
    for d in msp.query("DIMENSION"):
        pt = d.dxf.defpoint if d.dxf.hasattr("defpoint") else None
        if pt and pt.y > -75000 and x_min <= pt.x < x_max:
            val = d.dxf.actual_measurement if d.dxf.hasattr("actual_measurement") else None
            txt = d.dxf.text if d.dxf.hasattr("text") else ""
            if val is not None:
                dims.append((round(val, 1), txt))
    
    # Sort unique dimension values descending to see major part lengths/widths
    unique_vals = sorted(set(v for v, _ in dims if v >= 10), reverse=True)
    print(f"--- Dimensions count: {len(dims)} | Major values (>=10): {unique_vals[:40]} ---")
