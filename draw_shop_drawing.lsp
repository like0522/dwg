;;; ==============================================================================
;;; PROGRAM NAME: DRAW_SHOP_DRAWING.LSP
;;; AUTHOR: 25-Year Senior AutoLISP & 3D CAD Engineer
;;; ENCODING: ANSI (CP949)
;;; LAST MODIFIED: 2026-11-25 06:40:00
;;; [VERSION HISTORY & ROLLBACK LOG]
;;; v1.0 (2026-11-25 06:40:00): Initial creation of Channel Beam Shop Drawing
;;; ==============================================================================

(vl-load-com)

(defun c:SHOP_CHANNEL ( / *error* acadObj docObj mspace oldOsm oldEcho
                          fx0 fy0 L H Flange tw tf p1 p2 p3 p4
                          holeX i cx cy1 cy2 sx0 sy0 secPts
                          dx0 dy0 tx0 ty0 twBox thBox rowH )

  ;; Error Handler
  (defun *error* ( msg )
    (if oldOsm (setvar "OSMODE" oldOsm))
    (if oldEcho (setvar "CMDECHO" oldEcho))
    (if docObj (vla-EndUndoMark docObj))
    (if (and msg (not (wcmatch (strcase msg t) "*break*,*cancel*,*exit*")))
      (princ (strcat "\nError encountered: " msg))
    )
    (princ)
  )

  ;; Save System Variables & Start Undo
  (setq oldOsm (getvar "OSMODE"))
  (setq oldEcho (getvar "CMDECHO"))
  (setvar "CMDECHO" 0)
  (setvar "OSMODE" 0)

  (setq acadObj (vlax-get-acad-object))
  (setq docObj (vla-get-ActiveDocument acadObj))
  (setq mspace (vla-get-ModelSpace docObj))
  (vla-StartUndoMark docObj)

  ;; Geometry Parameters: CHANNEL 100x50x5/7.5t, L=3000
  (setq fx0 100.0)
  (setq fy0 500.0)
  (setq L 3000.0)
  (setq H 100.0)
  (setq Flange 50.0)
  (setq tw 5.0)
  (setq tf 7.5)

  ;; 1. FRONT VIEW: Outer Web Boundary
  (setq p1 (list fx0 fy0 0.0))
  (setq p2 (list (+ fx0 L) fy0 0.0))
  (setq p3 (list (+ fx0 L) (+ fy0 H) 0.0))
  (setq p4 (list fx0 (+ fy0 H) 0.0))

  (vl-cmdf "_.RECTANG" "_non" p1 "_non" p3)

  ;; Flange Hidden Projection Lines
  (vl-cmdf "_.LINE" "_non" (list fx0 (+ fy0 tf) 0.0) "_non" (list (+ fx0 L) (+ fy0 tf) 0.0) "")
  (vl-cmdf "_.LINE" "_non" (list fx0 (+ fy0 H (- tf)) 0.0) "_non" (list (+ fx0 L) (+ fy0 H (- tf)) 0.0) "")

  ;; Web Centerline
  (vl-cmdf "_.LINE" "_non" (list (- fx0 50.0) (+ fy0 (/ H 2.0)) 0.0)
                     "_non" (list (+ fx0 L 50.0) (+ fy0 (/ H 2.0)) 0.0) "")

  ;; Bolt Holes 4x4-Dia18 at ends
  (foreach hx '(40.0 100.0 2900.0 2960.0)
    (foreach hy_rel '(25.0 75.0)
      (setq cx (+ fx0 hx))
      (setq cy (+ fy0 hy_rel))
      (vl-cmdf "_.CIRCLE" "_non" (list cx cy 0.0) 9.0)
      (vl-cmdf "_.LINE" "_non" (list (- cx 15.0) cy 0.0) "_non" (list (+ cx 15.0) cy 0.0) "")
      (vl-cmdf "_.LINE" "_non" (list cx (- cy 15.0) 0.0) "_non" (list cx (+ cy 15.0) 0.0) "")
    )
  )

  ;; Intermediate 2x19-Dia9 Drill Holes
  (setq i 1)
  (while (< i 20)
    (setq cx (+ fx0 170.0 (* (1- i) 140.0)))
    (if (< cx (+ fx0 L -170.0))
      (progn
        (setq cy1 (+ fy0 35.0))
        (setq cy2 (+ fy0 65.0))
        (vl-cmdf "_.CIRCLE" "_non" (list cx cy1 0.0) 4.5)
        (vl-cmdf "_.CIRCLE" "_non" (list cx cy2 0.0) 4.5)
      )
    )
    (setq i (1+ i))
  )

  ;; 2. SECTION VIEW: Channel Profile
  (setq sx0 100.0)
  (setq sy0 150.0)
  (vl-cmdf "_.PLINE"
           "_non" (list sx0 sy0 0.0)
           "_non" (list (+ sx0 Flange) sy0 0.0)
           "_non" (list (+ sx0 Flange) (+ sy0 tf) 0.0)
           "_non" (list (+ sx0 tw) (+ sy0 tf) 0.0)
           "_non" (list (+ sx0 tw) (+ sy0 H (- tf)) 0.0)
           "_non" (list (+ sx0 Flange) (+ sy0 H (- tf)) 0.0)
           "_non" (list (+ sx0 Flange) (+ sy0 H) 0.0)
           "_non" (list sx0 (+ sy0 H) 0.0)
           "_close")

  ;; 3. DETAIL 'A' Boundary Circle
  (setq dx0 400.0)
  (setq dy0 150.0)
  (vl-cmdf "_.CIRCLE" "_non" (list (+ dx0 100.0) (+ dy0 100.0) 0.0) 130.0)

  ;; 4. Dimensions
  (vl-cmdf "_.DIMLINEAR" "_non" p4 "_non" p3 "_non" (list fx0 (+ fy0 H 80.0) 0.0))
  (vl-cmdf "_.DIMLINEAR" "_non" p1 "_non" p4 "_non" (list (- fx0 60.0) fy0 0.0))

  ;; 5. Shop Title Block
  (setq tx0 (- (+ fx0 L) 400.0))
  (setq ty0 50.0)
  (setq twBox 700.0)
  (setq thBox 180.0)
  (vl-cmdf "_.RECTANG" "_non" (list tx0 ty0 0.0) "_non" (list (+ tx0 twBox) (+ ty0 thBox) 0.0))

  ;; View Titles and Callouts
  (vl-cmdf "_.TEXT" "_non" (list fx0 (- fy0 100.0) 0.0) 18.0 0.0 "FRONT VIEW (Scale = 1/5)")
  (vl-cmdf "_.TEXT" "_non" (list sx0 (- sy0 80.0) 0.0) 14.0 0.0 "SECTION (Scale = 1/1)")
  (vl-cmdf "_.TEXT" "_non" (list (+ dx0 20.0) (- dy0 40.0) 0.0) 14.0 0.0 "DETAIL 'A' (Scale = 1/1)")

  (vl-cmdf "_.TEXT" "_non" (list (+ fx0 40.0) (+ fy0 H 30.0) 0.0) 14.0 0.0 "4x4-%%C18 HOLES (M16 BOLT HOLES)")
  (vl-cmdf "_.TEXT" "_non" (list (+ fx0 800.0) (+ fy0 H 30.0) 0.0) 14.0 0.0 "2x19-%%C9 DRILL HOLES")

  (vl-cmdf "_.TEXT" "_non" (list (+ tx0 20.0) (+ ty0 140.0) 0.0) 12.0 0.0 "DWG NO.: FOR-CAS-45001911-D01")
  (vl-cmdf "_.TEXT" "_non" (list (+ tx0 20.0) (+ ty0 105.0) 0.0) 12.0 0.0 "PART: CHANNEL 100x50x5/7.5t (NO. 1)")
  (vl-cmdf "_.TEXT" "_non" (list (+ tx0 20.0) (+ ty0 70.0) 0.0) 12.0 0.0 "MAT'L: SS400 | Q'TY: 2 EA | L=3000")
  (vl-cmdf "_.TEXT" "_non" (list (+ tx0 20.0) (+ ty0 35.0) 0.0) 12.0 0.0 "PAINTING: RAL5015, 30~35 um")

  ;; End Undo & Restore System Variables
  (vla-EndUndoMark docObj)
  (setvar "OSMODE" oldOsm)
  (setvar "CMDECHO" oldEcho)
  (vl-cmdf "_.ZOOM" "_E")
  (princ "\n[SUCCESS] Channel Beam Shop Drawing generated successfully. Command: SHOP_CHANNEL")
  (princ)
)

(princ "\nLoaded: DRAW_SHOP_DRAWING.LSP | Command: SHOP_CHANNEL\n")
(princ)
