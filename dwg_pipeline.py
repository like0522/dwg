"""
================================================================================
PROGRAM NAME: CAD DWG/DXF Headless Pipeline & Analyzer
AUTHOR: 25-Year Senior AutoLISP & 3D CAD Engineer
LAST MODIFIED: 2026-11-25 06:10:00
DESCRIPTION: High-speed headless DWG to DXF converter via accoreconsole and
             comprehensive DXF structure analyzer powered by ezdxf.
================================================================================
"""

import os
import sys
import json
import subprocess
import tempfile
from typing import Dict, Any, List
import ezdxf

ACCORECONSOLE_PATHS = [
    r"C:\Program Files\Autodesk\AutoCAD 2024\accoreconsole.exe",
    r"C:\Program Files\Autodesk\AutoCAD 2025\accoreconsole.exe",
    r"C:\Program Files\Autodesk\AutoCAD 2023\accoreconsole.exe",
    r"C:\Program Files\Autodesk\AutoCAD 2022\accoreconsole.exe",
]


def find_accoreconsole() -> str:
    """Find installed accoreconsole.exe on the system."""
    for path in ACCORECONSOLE_PATHS:
        if os.path.isfile(path):
            return path
    raise FileNotFoundError("AutoCAD accoreconsole.exe not found on system.")


def convert_dwg_to_dxf(dwg_path: str, dxf_path: str = None) -> str:
    """
    Convert DWG to DXF using headless accoreconsole.
    """
    dwg_abs = os.path.abspath(dwg_path)
    if not os.path.isfile(dwg_abs):
        raise FileNotFoundError(f"DWG file does not exist: {dwg_abs}")

    if not dxf_path:
        base, _ = os.path.splitext(dwg_abs)
        dxf_path = f"{base}.dxf"
    dxf_abs = os.path.abspath(dxf_path)

    accore = find_accoreconsole()

    # Create temporary script file for accoreconsole
    # Uses standard AutoCAD DXFOUT command
    with tempfile.NamedTemporaryFile("w", suffix=".scr", delete=False, encoding="ansi") as f:
        scr_path = f.name
        f.write("FILEDIA\n0\n")
        f.write(f'DXFOUT\n"{dxf_abs}"\n16\n')
        f.write("QUIT\nY\n")

    try:
        cmd = [accore, "/i", dwg_abs, "/s", scr_path]
        result = subprocess.run(
            cmd, capture_output=True, text=True, encoding="cp949", errors="replace", timeout=60
        )
        if not os.path.isfile(dxf_abs):
            raise RuntimeError(f"DXF conversion failed:\n{result.stdout}\n{result.stderr}")
        return dxf_abs
    finally:
        if os.path.isfile(scr_path):
            try:
                os.remove(scr_path)
            except OSError:
                pass


def analyze_dxf(dxf_path: str) -> Dict[str, Any]:
    """
    Analyze DXF entities, layers, block references and extents using ezdxf.
    """
    dxf_abs = os.path.abspath(dxf_path)
    if not os.path.isfile(dxf_abs):
        raise FileNotFoundError(f"DXF file not found: {dxf_abs}")

    doc = ezdxf.readfile(dxf_abs)
    msp = doc.modelspace()

    # 1. Layers
    layers_info = []
    for layer in doc.layers:
        layers_info.append({
            "name": layer.dxf.name,
            "color": layer.dxf.color,
            "is_off": layer.is_off(),
            "is_frozen": layer.is_frozen(),
        })

    # 2. Entity count breakdown
    entity_counts: Dict[str, int] = {}
    for entity in msp:
        dxftype = entity.dxftype()
        entity_counts[dxftype] = entity_counts.get(dxftype, 0) + 1

    # 3. Block reference stats
    blocks_inserted: Dict[str, int] = {}
    for insert in msp.query("INSERT"):
        bname = insert.dxf.name
        blocks_inserted[bname] = blocks_inserted.get(bname, 0) + 1

    # 4. Text strings sample
    texts = []
    for txt in msp.query("TEXT MTEXT"):
        content = txt.dxf.text if txt.dxftype() == "TEXT" else txt.text
        clean_content = content.strip().replace("\r\n", " ").replace("\n", " ")
        if clean_content:
            texts.append({
                "type": txt.dxftype(),
                "layer": txt.dxf.layer,
                "text": clean_content[:100]
            })

    return {
        "file_name": os.path.basename(dxf_abs),
        "dxf_version": doc.dxfversion,
        "total_modelspace_entities": len(msp),
        "entity_counts": entity_counts,
        "layers": layers_info,
        "block_references": blocks_inserted,
        "sample_texts_count": len(texts),
        "sample_texts": texts[:20]
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python dwg_pipeline.py <path_to_dwg_or_dxf>")
        sys.exit(1)

    target_file = sys.argv[1]
    ext = os.path.splitext(target_file)[1].lower()

    if ext == ".dwg":
        print(f"[1/2] Converting DWG to DXF: {target_file}")
        dxf_file = convert_dwg_to_dxf(target_file)
        print(f"      Created DXF: {dxf_file}")
    elif ext == ".dxf":
        dxf_file = target_file
    else:
        print("Error: Target file must be .dwg or .dxf")
        sys.exit(1)

    print(f"[2/2] Analyzing DXF: {dxf_file}")
    report = analyze_dxf(dxf_file)
    print("\n--- ANALYSIS RESULT ---")
    print(json.dumps(report, indent=2, ensure_ascii=False))
