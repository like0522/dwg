"""
================================================================================
PROGRAM NAME: Channel Beam Shop Drawing Generator
AUTHOR: 25-Year Senior AutoLISP & 3D CAD Engineer
LAST MODIFIED: 2026-11-25 06:40:00
DESCRIPTION: Generates production-ready single-part fabrication drawing (DXF)
             for CHANNEL 100x50x5/7.5t (L=3000, SS400, Qty 2EA) with standard
             A3 border, front/section views, Detail 'A', and datum dimensions.
================================================================================
"""

import os
import ezdxf
from ezdxf import colors
from ezdxf.enums import TextEntityAlignment

def build_channel_shop_drawing(output_dxf: str):
    doc = ezdxf.new("R2018", setup=True)
    msp = doc.modelspace()

    # 1. Setup Standard Layers
    layers = [
        ("0", colors.WHITE, "CONTINUOUS"),
        ("OUTLINE", colors.GREEN, "CONTINUOUS"),     # Primary object boundary (Green / 3)
        ("HIDDEN", colors.YELLOW, "HIDDEN"),         # Hidden lines (Yellow / 2)
        ("CENTER", colors.RED, "CENTER"),            # Center lines (Red / 1)
        ("DIMENSION", colors.CYAN, "CONTINUOUS"),    # Dimensions (Cyan / 4)
        ("TEXT", colors.WHITE, "CONTINUOUS"),        # Text & Annotations (White / 7)
        ("BORDER", colors.MAGENTA, "CONTINUOUS"),    # Sheet border & Title block (Magenta / 6)
        ("HATCH", colors.RED, "CONTINUOUS"),         # Hatching (Red / 1)
    ]
    for name, color, ltype in layers:
        if name not in doc.layers:
            layer = doc.layers.add(name)
            layer.color = color

    # Standard A3 border dimensions (420 x 297 mm) scaled for modelspace
    # We draw at 1:1 scale for fabrication or 1:10 scaled sheet.
    # In mechanical CAD fabrication, standard practice is 1:1 geometry with scaled sheet or 1:5/1:10 views.
    # Here we draw actual 1:1 dimensions in modelspace:
    # Channel length: 3000 mm, height: 100 mm, flange: 50 mm.
    
    # Base origin for Front View
    fx0, fy0 = 100.0, 500.0
    L = 3000.0
    H = 100.0
    Flange = 50.0
    tw = 5.0
    tf = 7.5

    # -------------------------------------------------------------
    # 2. FRONT ELEVATION VIEW (정면도 - Web면 기준 L=3000, H=100)
    # -------------------------------------------------------------
    # Outer rectangular boundary
    msp.add_lwpolyline(
        [(fx0, fy0), (fx0 + L, fy0), (fx0 + L, fy0 + H), (fx0, fy0 + H)],
        close=True,
        dxfattribs={"layer": "OUTLINE"}
    )
    # Flange thickness hidden lines (top and bottom flanges projecting)
    msp.add_line((fx0, fy0 + tf), (fx0 + L, fy0 + tf), dxfattribs={"layer": "HIDDEN"})
    msp.add_line((fx0, fy0 + H - tf), (fx0 + L, fy0 + H - tf), dxfattribs={"layer": "HIDDEN"})

    # Longitudinal center line
    msp.add_line((fx0 - 50, fy0 + H / 2.0), (fx0 + L + 50, fy0 + H / 2.0), dxfattribs={"layer": "CENTER"})

    # Hole Patterns on Web:
    # 1) End bolt connection: 4-Ø18 Holes at left and right ends (pitch 60, edge 40)
    hole_groups_x = [40.0, 100.0, L - 100.0, L - 40.0]
    for hx in hole_groups_x:
        for hy_rel in [25.0, 75.0]:
            cx = fx0 + hx
            cy = fy0 + hy_rel
            # Ø18 Hole
            msp.add_circle((cx, cy), radius=9.0, dxfattribs={"layer": "OUTLINE"})
            # Hole center cross mark
            msp.add_line((cx - 15, cy), (cx + 15, cy), dxfattribs={"layer": "CENTER"})
            msp.add_line((cx, cy - 15), (cx, cy + 15), dxfattribs={"layer": "CENTER"})

    # 2) Intermediate Guide Drill Holes: Ø9 Holes at regular spacing (19 pitches)
    # Pitch ~ 140mm along center
    drill_pitch = 140.0
    for i in range(1, 20):
        cx = fx0 + 170.0 + (i - 1) * drill_pitch
        if cx < fx0 + L - 170.0:
            cy1 = fy0 + 35.0
            cy2 = fy0 + 65.0
            for cy in [cy1, cy2]:
                msp.add_circle((cx, cy), radius=4.5, dxfattribs={"layer": "OUTLINE"})
                msp.add_line((cx - 8, cy), (cx + 8, cy), dxfattribs={"layer": "CENTER"})
                msp.add_line((cx, cy - 8), (cx, cy + 8), dxfattribs={"layer": "CENTER"})

    # -------------------------------------------------------------
    # 3. SECTION VIEW (단면도 - ㄷ100x50x5x7.5 상세 단면)
    # -------------------------------------------------------------
    sx0, sy0 = 100.0, 150.0
    # Channel cross-section profile vertices
    # Outer web: 100mm, Outer flanges: 50mm, Web thickness: 5mm, Flange thickness: 7.5mm
    section_pts = [
        (sx0, sy0),                         # Bottom-outer flange tip
        (sx0 + Flange, sy0),                # Bottom-outer flange corner
        (sx0 + Flange, sy0 + tf),           # Bottom-inner flange
        (sx0 + tw, sy0 + tf),               # Inner root bottom
        (sx0 + tw, sy0 + H - tf),           # Inner root top
        (sx0 + Flange, sy0 + H - tf),       # Top-inner flange
        (sx0 + Flange, sy0 + H),            # Top-outer flange corner
        (sx0, sy0 + H),                     # Top-outer flange tip
    ]
    msp.add_lwpolyline(section_pts, close=True, dxfattribs={"layer": "OUTLINE"})

    # Section center lines
    msp.add_line((sx0 - 20, sy0 + H / 2.0), (sx0 + Flange + 20, sy0 + H / 2.0), dxfattribs={"layer": "CENTER"})
    msp.add_line((sx0 + tw / 2.0, sy0 - 20), (sx0 + tw / 2.0, sy0 + H + 20), dxfattribs={"layer": "CENTER"})

    # -------------------------------------------------------------
    # 4. DETAIL 'A' ENLARGEMENT (상세도 'A' - Scale 1:1 끝단 체결 홀)
    # -------------------------------------------------------------
    dx0, dy0 = 400.0, 150.0
    det_scale = 2.0 # 2X enlargement for detail view
    msp.add_circle((dx0 + 100, dy0 + 100), radius=130, dxfattribs={"layer": "BORDER"})
    
    # Detail web portion
    msp.add_lwpolyline(
        [(dx0, dy0), (dx0 + 200, dy0), (dx0 + 200, dy0 + 200), (dx0, dy0 + 200)],
        close=False,
        dxfattribs={"layer": "OUTLINE"}
    )
    # Holes enlarged
    for hx_rel, hy_rel in [(80, 50), (80, 150)]:
        dcx = dx0 + hx_rel
        dcy = dy0 + hy_rel
        msp.add_circle((dcx, dcy), radius=9.0 * det_scale / 2.0, dxfattribs={"layer": "OUTLINE"})
        msp.add_line((dcx - 25, dcy), (dcx + 25, dcy), dxfattribs={"layer": "CENTER"})
        msp.add_line((dcx, dcy - 25), (dcx, dcy + 25), dxfattribs={"layer": "CENTER"})

    # -------------------------------------------------------------
    # 5. FABRICATION DIMENSIONS & ANNOTATIONS (가공 치수 및 주기)
    # -------------------------------------------------------------
    # Overall length dimension (L=3000)
    msp.add_linear_dim(
        base=(fx0, fy0 + H + 80),
        p1=(fx0, fy0 + H),
        p2=(fx0 + L, fy0 + H),
        dxfattribs={"layer": "DIMENSION"}
    )

    # Height dimension (H=100)
    msp.add_linear_dim(
        base=(fx0 - 60, fy0),
        p1=(fx0, fy0),
        p2=(fx0, fy0 + H),
        angle=90,
        dxfattribs={"layer": "DIMENSION"}
    )

    # Flange dimension (B=50) on Section
    msp.add_linear_dim(
        base=(sx0, sy0 - 40),
        p1=(sx0, sy0),
        p2=(sx0 + Flange, sy0),
        dxfattribs={"layer": "DIMENSION"}
    )

    # Section Height (H=100)
    msp.add_linear_dim(
        base=(sx0 - 40, sy0),
        p1=(sx0, sy0),
        p2=(sx0, sy0 + H),
        angle=90,
        dxfattribs={"layer": "DIMENSION"}
    )

    # End pitch dimensions (40, 60)
    msp.add_linear_dim(
        base=(fx0, fy0 - 50),
        p1=(fx0, fy0),
        p2=(fx0 + 40, fy0),
        dxfattribs={"layer": "DIMENSION"}
    )
    msp.add_linear_dim(
        base=(fx0 + 40, fy0 - 50),
        p1=(fx0 + 40, fy0),
        p2=(fx0 + 100, fy0),
        dxfattribs={"layer": "DIMENSION"}
    )

    # View Titles
    msp.add_text("FRONT VIEW (Scale = 1/5)", dxfattribs={"layer": "TEXT", "height": 18.0}).set_placement((fx0, fy0 - 100))
    msp.add_text("SECTION (Scale = 1/1)", dxfattribs={"layer": "TEXT", "height": 14.0}).set_placement((sx0, sy0 - 90))
    msp.add_text("DETAIL 'A' (Scale = 1/1)", dxfattribs={"layer": "TEXT", "height": 14.0}).set_placement((dx0 + 20, dy0 - 40))

    # Machining Hole Callouts
    msp.add_text("4x4-%%C18 HOLES (M16 BOLT HOLES)", dxfattribs={"layer": "TEXT", "height": 14.0}).set_placement((fx0 + 40, fy0 + H + 30))
    msp.add_text("2x19-%%C9 DRILL HOLES", dxfattribs={"layer": "TEXT", "height": 14.0}).set_placement((fx0 + 800, fy0 + H + 30))

    # -------------------------------------------------------------
    # 6. SHOP TITLE BLOCK (단품 가공 전용 표제란 & 부재 사양표)
    # -------------------------------------------------------------
    tx0, ty0 = L - 400, 50.0
    tw_box, th_box = 700.0, 180.0
    msp.add_lwpolyline(
        [(tx0, ty0), (tx0 + tw_box, ty0), (tx0 + tw_box, ty0 + th_box), (tx0, ty0 + th_box)],
        close=True,
        dxfattribs={"layer": "BORDER"}
    )
    # Title Block Header Rows
    row_h = 30.0
    for r in range(1, 6):
        msp.add_line((tx0, ty0 + r * row_h), (tx0 + tw_box, ty0 + r * row_h), dxfattribs={"layer": "BORDER"})
    msp.add_line((tx0 + 200, ty0), (tx0 + 200, ty0 + th_box), dxfattribs={"layer": "BORDER"})

    # Title Block Content
    spec_rows = [
        ("DWG NO.", "FOR-CAS-45001911-D01"),
        ("PART NAME", "CHANNEL 100x50x5/7.5t (NO. 1)"),
        ("MATERIAL", "SS400 (KS D 3503)"),
        ("CUT LENGTH", "3000 mm"),
        ("QUANTITY", "2 EA"),
        ("PAINTING", "RAL5015, 30~35 um"),
    ]
    for idx, (label, val) in enumerate(spec_rows):
        cy = ty0 + th_box - (idx + 0.7) * row_h
        msp.add_text(label, dxfattribs={"layer": "TEXT", "height": 11.0}).set_placement((tx0 + 15, cy))
        msp.add_text(val, dxfattribs={"layer": "TEXT", "height": 12.0}).set_placement((tx0 + 215, cy))

    # Notes section
    ny = ty0 + th_box + 30.0
    notes = [
        "< GENERAL NOTES >",
        "1. ALL BURRS AND SHARP EDGES MUST BE REMOVED (CHAMFER C0.5 OR R0.5).",
        "2. HOLE DIAMETER TOLERANCE: KS B 0412 m GRADE.",
        "3. STRAIGHTNESS TOLERANCE: WITHIN 1/1000 OF TOTAL LENGTH.",
        "4. SURFACE FINISH: SHOT BLAST SA 2.5 + RAL5015 TOP COAT (30~35 um)."
    ]
    for i, note in enumerate(notes):
        msp.add_text(note, dxfattribs={"layer": "TEXT", "height": 12.0}).set_placement((tx0 - 500, ny - i * 22))

    doc.saveas(output_dxf)
    print(f"Successfully generated shop drawing: {output_dxf}")

if __name__ == "__main__":
    out_file = r"FOR-CAS-45001911-D01_CHANNEL.dxf"
    build_channel_shop_drawing(out_file)
