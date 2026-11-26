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

---

## 4. Pipe Branch (Saddle / 가지관) Fabrication & Flat Pattern Check

When inspecting 90° pipe-to-pipe branch (가지관) drawings and plate-rolled flat patterns:
1. **Inner-Radius Saddle Intersection (내경 기준 새들 교차)**:
   - Verify the saddle cut curve uses the branch **inner radius** ($r_{Bi} = \text{OD}_b/2 - t$) intersecting the main pipe outer radius ($r_M = \text{OD}_m/2$), i.e., $z(\theta) = \sqrt{r_M^2 - (r_{Bi}\sin\theta)^2}$, so the branch inner wall does not protrude or leave an excessive root gap at the saddle.
2. **Neutral-Axis Rolling Width (중립축 기준 전개폭)**:
   - Verify plate rolling width matches $W = \pi \cdot (\text{OD}_b - t)$ (not $\pi \cdot \text{OD}_b$ or $\pi \cdot \text{ID}_b$).
3. **Seam Split & Centerline Alignment (용접 심 위치 및 중심선)**:
   - Check seam cut angle (e.g., $22.5^\circ$, $30^\circ$, $45^\circ$ offset vs $0^\circ$/$90^\circ$): offsetting avoids welding directly on the saddle peak/valley.
   - Verify `CL` lines in the flat pattern align strictly with the **true peaks and valleys** of the shifted sine-like saddle curve rather than fixed quarters.
4. **Curve Discretization Density (현도 곡선 세그먼트)**:
   - For CNC cutting / manual layout, verify curve chord length is fine enough (recommended $\approx 12\text{ mm}$, segment count as a multiple of 4) to prevent faceted polygon edges during rolling and fit-up.
