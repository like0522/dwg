# Geometric DRC, Readback Verification & Drafting Standards

Integrated from `AutoCAD-skills`, `CAD & Mechanical Design Skill`, and `AutoCAD-MCP` best practices.

---

## 1. Execution Safety & Readback Verification Gate

Never assume a CAD creation or modification command succeeded without verifying the actual entity state.

### Readback Protocol
1. **Before Modification**: Record existing layer states, system variables (`OSMODE`, `CMDECHO`, `INSUNITS`), and entity handles.
2. **Atomic Execution**: Wrap multi-entity operations in Undo marks (`vla-StartUndoMark` / `vla-EndUndoMark`).
3. **Post-Write Readback**:
   - Query the created/modified entity handle or bounding box (`GetBoundingBox`).
   - Verify target `Layer`, `TextString`, `Measurement`, and `Coordinates` match intent.
   - For AutoLISP scripts, always run parenthesis balance verification before loading into AutoCAD.
4. **Visual Diff Highlighting (`AI_MOD_BOX`)**:
   - Whenever an AutoLISP script modifies or adds entities on a drawing, draw a green (`Color = 3`) closed `LWPOLYLINE` bounding box around each affected entity on layer `AI_MOD_BOX`, and always provide a cleanup command (`ClearModBoxes`) that removes only `AI_MOD_BOX` entities.

---

## 2. Semantic Design Rule Checks (DRC)

Before releasing any fabrication drawing or Danpoom sheet, evaluate:

1. **Geometric Integrity**:
   - No unintended entity crossings, duplicate overlapping lines (`OVERKILL` check), or near-miss unclosed endpoints on cutting profiles.
   - All closed cutting contours (`LWPOLYLINE`) must have `Closed = True` or endpoint distance `< 0.01 mm`.
2. **Multi-View & Section Consistency**:
   - Cross-sectional views (`Sec A-A`, `View C`) and detail callouts must match the main plan/elevation dimensions and plate thicknesses.
   - Hole counts in callouts (e.g., `8-Ø27 THRU`) must equal `(holes per plate) × (BOM plate quantity)`.
3. **Drafting & Annotation Standards**:
   - Default unit: **millimeters (mm)** (`INSUNITS = 4`).
   - Projection: **Third-angle projection (삼각법)** default for KS/ASME; verify **First-angle (일각법)** if European/GB/T customer template is used.
   - GD&T / Surface Texture: Machining marks (`6.3`, `25`, `▽▽`) must clearly point to the machined face, and corresponding machining allowances must be accounted for in the raw stock BOM.
4. **BOM & Balloon Authority**:
   - Item numbers in the cutting list (`1. ...`, `2. ...`) must map 1:1 to balloon callouts or drawn profiles.
   - Every item requires: `Item No.`, `Material/Profile`, `Thickness/Section`, `Width × Length`, `Quantity`, and `Machining/Tap Notes`.
