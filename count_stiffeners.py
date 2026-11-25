import ezdxf
import math

doc = ezdxf.readfile("20261124(화)-이스턴 메탈 UAE-45801051.dxf")
msp = doc.modelspace()

# Find all 12mm lines (stiffener thickness) in Sheet 1 (X: 374000 ~ 387500, Y > -75000)
# Notice earlier in verify_specific_parts: 1:1 scale is used in the main views!
# Wait: why did 175mm return 0? Maybe chamfered or 176mm or 174mm, or 175 minus something!
# Let's check all lines of length 11.5~12.5, 90~98, 170~180 in Sheet 1!
lines_12 = []
lines_95 = []
lines_175 = []

for e in msp.query("LINE"):
    p1, p2 = e.dxf.start, e.dxf.end
    if p1.y > -75000 and 374000 <= p1.x <= 387500:
        L = math.hypot(p2.x - p1.x, p2.y - p1.y)
        if 11.5 <= L <= 12.5:
            lines_12.append((round(p1.x,1), round(p1.y,1), round(p2.x,1), round(p2.y,1), round(L,2), e.dxf.layer))
        elif 92.0 <= L <= 98.0:
            lines_95.append((round(p1.x,1), round(p1.y,1), round(L,2), e.dxf.layer))
        elif 170.0 <= L <= 180.0:
            lines_175.append((round(p1.x,1), round(p1.y,1), round(L,2), e.dxf.layer))

print(f"Lines ~12mm (11.5~12.5): {len(lines_12)}")
# Group 12mm lines in Top View (Y between -58500 and -55000)
top_12 = [l for l in lines_12 if -58500 < l[1] < -55000]
print(f"  In Top View (-58500 < Y < -55000): {len(top_12)} lines")
for l in sorted(top_12, key=lambda x: (x[0], x[1])):
    print(f"    pos=({l[0]}, {l[1]}) -> ({l[2]}, {l[3]}) L={l[4]} [{l[5]}]")

print(f"\nLines ~95mm (92~98): {len(lines_95)}")
for l in lines_95:
    print(f"  pos=({l[0]}, {l[1]}) L={l[2]} [{l[3]}]")

print(f"\nLines ~175mm (170~180): {len(lines_175)}")
for l in lines_175:
    print(f"  pos=({l[0]}, {l[1]}) L={l[2]} [{l[3]}]")
