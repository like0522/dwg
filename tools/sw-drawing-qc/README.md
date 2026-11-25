# SW Drawing QC — Automated Engineering Drawing Quality Inspector

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)

**Instantly find what's wrong with your engineering drawings — before your reviewer does.**

Built for mechanical engineers and drafters. Reads DXF/PDF files from SolidWorks, AutoCAD, CATIA, etc. Detects missing dimensions, missing tolerances, surface roughness gaps, GD&T issues, title block problems — and now recognizes mechanical features (bearing seats, keyways, threads, fillets, hole patterns) automatically.

---

## What It Detects

| Category | Checks |
|---|---|
| **Dimensions** | Missing linear/radial/diameter dims, closed chains, redundant dims |
| **Tolerances** | Missing size tolerances, missing GD&T, tolerance-roughness mismatch |
| **Surface Finish** | Missing Ra on machined surfaces, wrong Ra for tolerance grade |
| **Title Block** | Empty material/scale/revision fields, missing technical notes |
| **Feature Recog.** | Bearing seats, keyways, threaded holes, chamfers, fillets, hole patterns |
| **Standards** | ISO 2768 / GB/T 1804 general tolerance compliance |

## Quick Demo

```
$ python sw_qc_parser.py lever.dxf --features --rules gb_baseline

============================================================
  Engineering Drawing QC Inspector — Pro v2.0
  lever.DXF
============================================================
  Dimensions: 0        (⚠ none found!)
  GD&T: 0              (⚠ none found!)
  Circles/Arcs: 6 / 4
  Features detected: 5

  Issues: 18
  !! Material not specified
  !! No dimensions found — part cannot be manufactured
  !! Bearing Seat detected (100% conf.) — needs H7 + Cylindricity
  !  Keyway detected (90% conf.) — needs N9 + Symmetry
  !  Missing ISO 2768-m citation in technical notes
============================================================
```

## Two Tiers

| | Free | Pro |
|---|---|---|
| **DXF Analysis** | Basic text scan | Structured entity extraction (ezdxf) |
| **Feature Recognition** | ❌ | 8 types auto-detected |
| **Standards Tables** | Manual reference | Full ISO 2768 / GB/T 1804 lookup |
| **PDF Support** | ❌ | ✅ (pymupdf) |
| **Rule Engine** | ❌ | 7 industry presets + custom YAML |
| **Report Formats** | Markdown | Markdown + JSON + Excel |
| **How to Get** | This repo | [See below](#pro-version) |

## Installation

```bash
# Free version — just the skill file, no dependencies
# Copy skills/sw-drawing-qc.md to ~/.claude/skills/

# Pro version — requires Python
pip install ezdxf openpyxl pymupdf pyyaml
```

## Usage

### Free (Claude Code Skill)
```
"Check this drawing: /path/to/part.dxf"
```
Claude reads the DXF directly and applies the QC checklist.

### Pro (Python CLI)
```bash
python sw_qc_parser.py drawing.dxf                    # basic scan
python sw_qc_parser.py drawing.dxf --features          # + feature recognition
python sw_qc_parser.py drawing.dxf --features --rules gb_baseline  # + standards
python sw_qc_parser.py drawing.dxf --features --rules automotive --json --excel  # full output
python sw_qc_parser.py drawing.pdf --pdf --json         # PDF input
```

## Supported Standards

### ISO Edition
- **ISO 2768** — General tolerances (f/m/c/v classes)
- **ISO 1101** — Geometric tolerances (GD&T, H/K/L classes)
- **ISO 1302** — Surface texture (Ra)
- **ISO 128** — Technical drawing layout
- **ISO 2553** — Welding symbols

### GB Edition (for Chinese market)
- **GB/T 1804** — General tolerances (f/m/c/v)
- **GB/T 1184** — Geometric tolerances (H/K/L)
- **GB/T 131** — Surface roughness
- **GB/T 4458** — Drawing layout
- **GB/T 4459** — Standard features (threads, gears, center holes)

## Industry Presets

| Preset | Industry |
|---|---|
| `iso_baseline` / `gb_baseline` | General engineering |
| `automotive` | Automotive (IATF 16949) |
| `mold` | Mold & die |
| `sheet_metal` | Sheet metal fabrication |
| `welding` | Welded structures |
| `hydraulic` | Hydraulic components |
| `gear` | Gears |

## Pro Version

The Pro version adds:
- Structured DXF parsing with ezdxf (reads actual DIMENSION entities)
- Feature recognition — detects what each geometry *is* (bearing seat, keyway, etc.)
- ISO/GB standards lookup tables — not just generic advice, actual tolerance values
- PDF support via pymupdf
- Excel reports for sign-off
- Custom YAML rules for company-specific standards

**Get it at:** [SkillHQ](https://peerpush.net/p/skillhq) • [AgentStore](https://agentstore.tools) • 闲鱼 (search "工程图QC")

Or contact the author for direct licensing.

## License

Free version: MIT — do whatever you want.
Pro version & standards modules: Licensed — contact for commercial terms.
