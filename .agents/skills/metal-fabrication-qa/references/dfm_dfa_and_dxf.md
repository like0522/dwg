# DFM / DFA & 2D DXF Cutting Preflight Standards

Integrated from `Mechanical-AI-Skill` and `cad-dxf-skill` best practices for welded steel fabrication, post-weld machining, and CNC/laser/plasma cutting.

---

## 1. Design for Manufacturing (DFM) - 제관 및 가공성 검증

1. **Post-Weld Machining Allowance (선 제관 후 가공 여유)**:
   - **Thickness Direction (t)**: When a top pad/block has a `6.3` finish mark, verify raw stock thickness exceeds finished drawing thickness by standard plate step (`+1.0 mm ~ +6.0 mm`), unless explicitly marked as a stepped cut (`단가공`).
   - **Planar Direction (Width / Length)**: Check `Quote Ekosystem` real-time measurements against Danpoom stock dimensions; standard milling allowance on machined sides is `+5.0 ~ +7.0 mm` (or `+2.5 mm` per side for symmetric machining).
2. **Tool Access & Tap Clearance**:
   - Verify tap depth (`DP`) does not exceed plate thickness minus safe bottom wall unless `THRU` is specified (e.g., `M6 DP12` on `65t` block is safe; `M14x2 DP28` requires ≥ 32 mm or through-flange check).
   - Check corner chamfers (`C5`, `C30`, `C50`) on gussets and stiffeners to ensure weld-seam clearance (`스캘럽/모따기` 간섭 방지).

---

## 2. Design for Assembly (DFA) - 조립 및 간섭 검증

1. **Structural Member End Deductions (형강 마구리 공제)**:
   - Verify cross-beam lengths deduct mating beam web/flange thickness (`L_cut = L_span - t_web` or `L_overall - B_beam - t_web`).
   - Check bolt/pin clearances (e.g., `Ø27 THRU` for M24 bolts, `Ø20` pin tolerances).
2. **Symmetry & Opposite-Hand (LH/RH) Check**:
   - When multiple `STAND` or `FRAME` assemblies exist in one DWG (e.g., `45801052` & `45801053`), verify whether the second assembly is mirror-symmetric (`대칭`) or requires its own dedicated Danpoom sheet.

---

## 3. 2D DXF Cutting Preflight Checklist (레이저/플라즈마/워터젯 절단용)

When exporting or inspecting flat patterns (`.dxf`) for CNC cutting:
1. **Scale & Units**: Strictly `1:1` scale in `mm` (never scaled to paper viewport scale like `1:15` or `1:20`).
2. **Clean Geometry**:
   - Convert splines/ellipses to polylines/arcs if required by legacy nesting CAM.
   - Remove dimension lines, centerlines, text, and title blocks from cutting layers—keep only outer contour and internal hole contours on dedicated cutting layers.
3. **Closed Contours**: Outer profile and every internal cutout must be single closed loops with zero duplicate overlapping segments.
