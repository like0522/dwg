import ezdxf
import math

doc = ezdxf.readfile("20261124(화)-이스턴 메탈 UAE-45801051.dxf")
msp = doc.modelspace()

# In Sheet 1 (45801051), the main assembly view is 1:1 or 1:20?
# Wait: earlier we saw 5880.0 dim! Let's check actual modelspace width of the main H-beam in Sheet 1.
# And let's find all lines of length ~95mm or ~175mm (or scaled) and group them by view!
lines_95 = []
lines_175 = []

for e in msp.query("LINE"):
    p1, p2 = e.dxf.start, e.dxf.end
    if p1.y > -75000 and 374000 <= p1.x <= 387500:
        length = math.hypot(p2.x - p1.x, p2.y - p1.y)
        if abs(length - 95.0) < 0.5:
            lines_95.append((round(p1.x, 1), round(p1.y, 1), round(p2.x, 1), round(p2.y, 1), e.dxf.layer))
        elif abs(length - 175.0) < 0.5:
            lines_175.append((round(p1.x, 1), round(p1.y, 1), round(p2.x, 1), round(p2.y, 1), e.dxf.layer))

print(f"Total 95mm lines in Sheet 1: {len(lines_95)}")
# Cluster by Y region (Top view vs Front view vs Side view)
top_view_95 = [l for l in lines_95 if l[1] > -58500]
front_view_95 = [l for l in lines_95 if l[1] <= -58500]

print(f"  In Top View (Y > -58500): {len(top_view_95)} lines")
# Group by X coordinate (every rib has 2 lines of 95mm or 12x95 rectangle)
xs_top = sorted(set(round(l[0], 0) for l in top_view_95))
print(f"  Distinct X positions in Top View: {xs_top}")

print(f"  In Front/Section View (Y <= -58500): {len(front_view_95)} lines")
xs_front = sorted(set(round(l[0], 0) for l in front_view_95))
print(f"  Distinct X positions in Front/Section View: {xs_front}")

print(f"\nTotal 175mm lines in Sheet 1: {len(lines_175)}")
top_175 = [l for l in lines_175 if l[1] > -58500]
front_175 = [l for l in lines_175 if l[1] <= -58500]
print(f"  In Top View (Y > -58500): {len(top_175)} lines, X={sorted(set(round(l[0],0) for l in top_175))}")
print(f"  In Front/Section View (Y <= -58500): {len(front_175)} lines, X={sorted(set(round(l[0],0) for l in front_175))}")
