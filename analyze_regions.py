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

# 1. Check CP_AUDIT layers
for lname in ["CP_AUDIT_OK", "CP_AUDIT_WARN", "CP_AUDIT_MISS"]:
    ents = [e for e in msp if e.dxf.layer == lname]
    print(f"Layer {lname}: {len(ents)} entities")
    for e in ents[:10]:
        print("  ", e.dxftype(), getattr(e.dxf, 'center', getattr(e.dxf, 'start', None)))

# 2. Check all texts in Y < -75000
print("\n=== ALL TEXTS IN Y < -75000 ===")
lower_texts = []
for e in msp.query("TEXT MTEXT"):
    pt = e.dxf.insert
    if pt.y < -75000:
        raw = e.dxf.text if e.dxftype() == "TEXT" else e.text
        lower_texts.append((round(pt.x,1), round(pt.y,1), e.dxf.layer, clean_cad_text(raw)))
lower_texts.sort(key=lambda x: (x[0], -x[1]))
for x, y, l, t in lower_texts:
    print(f"  ({x:8.1f}, {y:9.1f}) [{l}]: {t}")

# 3. Check entity bounding boxes in Y < -75000
print("\n=== ENTITIES IN Y < -75000 BY TYPE ===")
counts = {}
for e in msp:
    pt = None
    if hasattr(e.dxf, "insert"): pt = e.dxf.insert
    elif hasattr(e.dxf, "start"): pt = e.dxf.start
    elif hasattr(e.dxf, "center"): pt = e.dxf.center
    elif hasattr(e.dxf, "defpoint"): pt = e.dxf.defpoint
    if pt and pt.y < -75000:
        counts[e.dxftype()] = counts.get(e.dxftype(), 0) + 1
print(counts)
