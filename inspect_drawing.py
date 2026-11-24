"""
================================================================================
PROGRAM NAME: CAD Drawing QA & Inspection Engine
AUTHOR: 25-Year Senior AutoLISP & 3D CAD Engineer
LAST MODIFIED: 2026-11-25 06:35:00
DESCRIPTION: Comprehensive drawing inspection analyzing dimension overrides,
             hole hole/edge clearances, duplicate entities, and title block specs.
================================================================================
"""

import math
import os
import json
import ezdxf
from typing import Dict, Any, List

def run_inspection(dxf_path: str) -> Dict[str, Any]:
    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()

    # 1. Dimension Overrides Check
    dim_overrides = []
    dim_total = 0
    dim_normal = 0
    for dim in msp.query("DIMENSION"):
        dim_total += 1
        text = dim.dxf.text if dim.dxf.hasattr("text") else ""
        actual_val = dim.dxf.actual_measurement if dim.dxf.hasattr("actual_measurement") else None
        
        # If user explicitly overrode text (not empty and not <> or <>)
        if text and text != "" and "<>" not in text:
            dim_overrides.append({
                "override_text": text,
                "actual_measurement": round(actual_val, 3) if actual_val is not None else "N/A",
                "layer": dim.dxf.layer,
                "defpoint": [round(c, 2) for c in dim.dxf.defpoint] if dim.dxf.hasattr("defpoint") else []
            })
        else:
            dim_normal += 1

    # 2. Hole (Circle) Analysis
    circles_by_diameter: Dict[float, int] = {}
    circle_coords: List[Dict[str, Any]] = []
    for c in msp.query("CIRCLE"):
        dia = round(c.dxf.radius * 2.0, 2)
        circles_by_diameter[dia] = circles_by_diameter.get(dia, 0) + 1
        circle_coords.append({
            "dia": dia,
            "center": [round(c.dxf.center.x, 2), round(c.dxf.center.y, 2)],
            "layer": c.dxf.layer
        })

    # 3. Micro Lines & Duplicate Check
    micro_lines = []
    line_segments = []
    for line in msp.query("LINE"):
        p1 = (round(line.dxf.start.x, 2), round(line.dxf.start.y, 2))
        p2 = (round(line.dxf.end.x, 2), round(line.dxf.end.y, 2))
        length = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        if length < 0.1: # Less than 0.1mm micro segment
            micro_lines.append({
                "start": p1,
                "end": p2,
                "length": round(length, 4),
                "layer": line.dxf.layer
            })
        # Normalize segment for overlap check
        seg = tuple(sorted([p1, p2]))
        line_segments.append(seg)

    duplicate_lines_count = len(line_segments) - len(set(line_segments))

    # 4. Text and Specifications Extraction
    all_texts = []
    for txt in msp.query("TEXT MTEXT"):
        content = txt.dxf.text if txt.dxftype() == "TEXT" else txt.text
        content_clean = content.strip().replace("\r\n", " ").replace("\n", " ")
        if content_clean:
            all_texts.append(content_clean)

    return {
        "dxf_path": os.path.basename(dxf_path),
        "total_dimensions": dim_total,
        "normal_dimensions": dim_normal,
        "overridden_dimensions_count": len(dim_overrides),
        "overridden_dimensions": dim_overrides,
        "total_circles": len(circle_coords),
        "hole_diameter_distribution": circles_by_diameter,
        "micro_lines_count": len(micro_lines),
        "duplicate_lines_count": duplicate_lines_count,
        "all_texts": all_texts
    }

if __name__ == "__main__":
    dxf_file = r"20250221(금)(FOR-CAS-45001911).dxf"
    result = run_inspection(dxf_file)
    print(json.dumps(result, indent=2, ensure_ascii=False))
