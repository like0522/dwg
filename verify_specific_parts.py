import ezdxf
import math

doc = ezdxf.readfile("20261124(화)-이스턴 메탈 UAE-45801051.dxf")
msp = doc.modelspace()

print("=== 1. SEARCHING FOR DIMENSIONS NEAR 46, 250, 280 ===")
for d in msp.query("DIMENSION"):
    pt = d.dxf.defpoint if d.dxf.hasattr("defpoint") else None
    val = d.dxf.actual_measurement if d.dxf.hasattr("actual_measurement") else None
    if pt and val is not None and pt.y > -75000:
        v = round(val, 2)
        if any(abs(v - target) < 0.5 for target in [46.0, 250.0, 280.0]):
            print(f"  DIM val={v:6.1f} | text='{d.dxf.text}' | pos=({round(pt.x,1)}, {round(pt.y,1)}) | layer={d.dxf.layer}")

print("\n=== 2. SEARCHING FOR DIMENSIONS NEAR 95, 175, 12 ===")
for d in msp.query("DIMENSION"):
    pt = d.dxf.defpoint if d.dxf.hasattr("defpoint") else None
    val = d.dxf.actual_measurement if d.dxf.hasattr("actual_measurement") else None
    if pt and val is not None and pt.y > -75000:
        v = round(val, 2)
        if any(abs(v - target) < 0.5 for target in [95.0, 175.0, 12.0]):
            print(f"  DIM val={v:6.1f} | text='{d.dxf.text}' | pos=({round(pt.x,1)}, {round(pt.y,1)}) | layer={d.dxf.layer}")

print("\n=== 3. SEARCHING FOR RECTANGULAR / PLATE SHAPES WITH 95x175 OR 12x95 OR 12x175 ===")
# Check horizontal/vertical lines of length 95, 175, 250, 280, 46
target_lens = [46.0, 95.0, 175.0, 250.0, 280.0]
hits = {tl: [] for tl in target_lens}

for e in msp.query("LINE"):
    p1 = e.dxf.start
    p2 = e.dxf.end
    if p1.y > -75000 and 374000 <= p1.x <= 387500: # Sheet 1 (45801051)
        length = math.hypot(p2.x - p1.x, p2.y - p1.y)
        # Note: Sheet 1 scale is 1:20 or 1:1? Let's check actual modelspace lengths vs scale!
        for tl in target_lens:
            # Check 1:1, 1:8, 1:20
            if abs(length - tl) < 0.5:
                hits[tl].append(("1:1", round(p1.x,1), round(p1.y,1), round(length,2), e.dxf.layer))
            elif abs(length * 20 - tl) < 2.0:
                hits[tl].append(("1:20", round(p1.x,1), round(p1.y,1), round(length,2), e.dxf.layer))
            elif abs(length * 8 - tl) < 2.0:
                hits[tl].append(("1:8", round(p1.x,1), round(p1.y,1), round(length,2), e.dxf.layer))

for tl, hlist in hits.items():
    print(f"\nLength {tl}mm matches ({len(hlist)} lines):")
    for h in hlist[:30]:
        print(f"  Scale {h[0]} | pos=({h[1]}, {h[2]}) | raw_len={h[3]} | layer={h[4]}")
