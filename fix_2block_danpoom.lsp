;; ============================================================================
;; PROGRAM : fix_2block_danpoom.lsp
;; AUTHOR  : Antigravity CAD Engine
;; ENCODING: ANSI (CP949)
;; LAST MODIFIED: 2026-11-25 13:44:00
;;
;; [VERSION HISTORY & ROLLBACK LOG]
;;   v1.0 (2026-11-25 13:38:00) - Initial release: Auto-fix missing item
;;        numbers, missing end-cap notes, 1-set quantity labels, and
;;        upper 100x50 material note typo in 2BLOCK-.dwg.
;;   v1.1 (2026-11-25 13:44:00) - Added green highlight box (AI_MOD_BOX,
;;        Color 3) around modified entities and ClearModBoxes cleanup command.
;; ============================================================================

(vl-load-com)

(defun *error* (msg / doc)
  (if (and msg (not (wcmatch (strcase msg) "*BREAK*,*CANCEL*,*EXIT*")))
    (princ (strcat "\n[ERROR] " msg))
  )
  (setq doc (vla-get-ActiveDocument (vlax-get-acad-object)))
  (if doc (vla-EndUndoMark doc))
  (princ)
)

(defun _ensure-box-layer (doc / layers lay)
  (setq layers (vla-get-Layers doc))
  (if (not (tblsearch "LAYER" "AI_MOD_BOX"))
    (progn
      (setq lay (vla-Add layers "AI_MOD_BOX"))
      (vla-put-Color lay 3)
    )
    (vla-put-Color (vla-Item layers "AI_MOD_BOX") 3)
  )
)

(defun _draw-green-box (ent / obj minp maxp p1 p2 x1 y1 x2 y2 pad)
  (setq pad 15.0)
  (setq obj (vlax-ename->vla-object ent))
  (if (not (vl-catch-all-error-p
             (vl-catch-all-apply 'vla-GetBoundingBox (list obj 'minp 'maxp))))
    (progn
      (setq p1 (vlax-safearray->list minp))
      (setq p2 (vlax-safearray->list maxp))
      (setq x1 (- (car p1) pad) y1 (- (cadr p1) pad))
      (setq x2 (+ (car p2) pad) y2 (+ (cadr p2) pad))
      (entmakex
        (list
          '(0 . "LWPOLYLINE")
          '(100 . "AcDbEntity")
          '(8 . "AI_MOD_BOX")
          '(62 . 3)
          '(100 . "AcDbPolyline")
          '(90 . 4)
          '(70 . 1)
          (cons 10 (list x1 y1))
          (cons 10 (list x2 y1))
          (cons 10 (list x2 y2))
          (cons 10 (list x1 y2))
        )
      )
    )
  )
)

(defun _replace-text-in-range (xmin xmax ymin ymax old-prefix new-prefix / ss i ent ed txt x y changed)
  (setq changed 0)
  (setq ss (ssget "X" '((0 . "TEXT,MTEXT"))))
  (if ss
    (progn
      (setq i 0)
      (while (< i (sslength ss))
        (setq ent (ssname ss i))
        (setq ed (entget ent))
        (setq txt (cdr (assoc 1 ed)))
        (setq x (car (cdr (assoc 10 ed))))
        (setq y (cadr (cdr (assoc 10 ed))))
        (if (and (>= x xmin) (<= x xmax) (>= y ymin) (<= y ymax))
          (if (wcmatch txt (strcat old-prefix "*"))
            (progn
              (setq txt (strcat new-prefix (substr txt (+ 1 (strlen old-prefix)))))
              (entmod (subst (cons 1 txt) (assoc 1 ed) ed))
              (entupd ent)
              (_draw-green-box ent)
              (setq changed (1+ changed))
            )
          )
        )
        (setq i (1+ i))
      )
      (setq ss nil)
    )
  )
  changed
)

(defun _replace-substr-in-range (xmin xmax ymin ymax old-sub new-sub / ss i ent ed txt pos x y changed)
  (setq changed 0)
  (setq ss (ssget "X" '((0 . "TEXT,MTEXT"))))
  (if ss
    (progn
      (setq i 0)
      (while (< i (sslength ss))
        (setq ent (ssname ss i))
        (setq ed (entget ent))
        (setq txt (cdr (assoc 1 ed)))
        (setq x (car (cdr (assoc 10 ed))))
        (setq y (cadr (cdr (assoc 10 ed))))
        (if (and (>= x xmin) (<= x xmax) (>= y ymin) (<= y ymax))
          (if (setq pos (vl-string-search old-sub txt))
            (progn
              (setq txt (vl-string-subst new-sub old-sub txt))
              (entmod (subst (cons 1 txt) (assoc 1 ed) ed))
              (entupd ent)
              (_draw-green-box ent)
              (setq changed (1+ changed))
            )
          )
        )
        (setq i (1+ i))
      )
      (setq ss nil)
    )
  )
  changed
)

(defun c:Fix2BlockDanpoom ( / doc cnt )
  (setq doc (vla-get-ActiveDocument (vlax-get-acad-object)))
  (vla-StartUndoMark doc)
  (_ensure-box-layer doc)
  (setq cnt 0)

  ;; 1. NO. 2 (1BLOCK): Renumber 26 -> 25
  (setq cnt (+ cnt (_replace-text-in-range 388000.0 391500.0 -105000.0 -85000.0 "26. KS" "25. KS")))

  ;; 2. NO. 3 & NO. 4: Clarify 1-set unit quantities in DWG NO. header
  (setq cnt (+ cnt (_replace-substr-in-range 403500.0 407000.0 -105000.0 -85000.0 "스테이볼트홀 강관 미들 4EA" "스테이볼트홀 강관 미들 4EA (1SET 기준)")))
  (setq cnt (+ cnt (_replace-substr-in-range 407500.0 411000.0 -105000.0 -85000.0 "스테이볼트홀 강관 END 2EA" "스테이볼트홀 강관 END 2EA (1SET 기준)")))

  ;; 3. NO. 6: Add missing end-cap note on item 6 and renumber 6,10,11,12,13,14,15 -> 4..10
  (setq cnt (+ cnt (_replace-substr-in-range 425500.0 429000.0 -105000.0 -85000.0 "(N:206.6kg / G:207.3kg)" "(N:206.6kg / G:207.3kg)-4.5t 마구리")))
  (setq cnt (+ cnt (_replace-text-in-range 425500.0 429000.0 -105000.0 -85000.0 "6. 각관 100x50" "4. 각관 100x50")))
  (setq cnt (+ cnt (_replace-text-in-range 425500.0 429000.0 -105000.0 -85000.0 "10. 4.5tx94x344" "5. 4.5tx94x344")))
  (setq cnt (+ cnt (_replace-text-in-range 425500.0 429000.0 -105000.0 -85000.0 "11. 4.5tx44x94" "6. 4.5tx44x94")))
  (setq cnt (+ cnt (_replace-text-in-range 425500.0 429000.0 -105000.0 -85000.0 "12, PIPE" "7. PIPE")))
  (setq cnt (+ cnt (_replace-text-in-range 425500.0 429000.0 -105000.0 -85000.0 "13. 10tx200x200" "8. 10tx200x200")))
  (setq cnt (+ cnt (_replace-text-in-range 425500.0 429000.0 -105000.0 -85000.0 "14. 10tx160x200" "9. 10tx160x200")))
  (setq cnt (+ cnt (_replace-text-in-range 425500.0 429000.0 -105000.0 -85000.0 "15. 10tx40x100" "10. 10tx40x100")))

  ;; 4. NO. 7: Renumber 6,10,11,12,13,14,15 -> 4..10
  (setq cnt (+ cnt (_replace-text-in-range 429500.0 433000.0 -105000.0 -85000.0 "6. 각관 100x50" "4. 각관 100x50")))
  (setq cnt (+ cnt (_replace-text-in-range 429500.0 433000.0 -105000.0 -85000.0 "10. 4.5tx94x344" "5. 4.5tx94x344")))
  (setq cnt (+ cnt (_replace-text-in-range 429500.0 433000.0 -105000.0 -85000.0 "11. 4.5tx44x94" "6. 4.5tx44x94")))
  (setq cnt (+ cnt (_replace-text-in-range 429500.0 433000.0 -105000.0 -85000.0 "12, PIPE" "7. PIPE")))
  (setq cnt (+ cnt (_replace-text-in-range 429500.0 433000.0 -105000.0 -85000.0 "13. 10tx200x200" "8. 10tx200x200")))
  (setq cnt (+ cnt (_replace-text-in-range 429500.0 433000.0 -105000.0 -85000.0 "14. 10tx160x200" "9. 10tx160x200")))
  (setq cnt (+ cnt (_replace-text-in-range 429500.0 433000.0 -105000.0 -85000.0 "15. 10tx40x100" "10. 10tx40x100")))

  ;; 5. Upper Notes: Fix 50x50x4.5T -> 100x50x4.5T in Base Plates (NO. 6 & NO. 7)
  (setq cnt (+ cnt (_replace-substr-in-range 429000.0 441000.0 -85000.0 -70000.0 "50x50x4.5T" "100x50x4.5T")))

  (vla-EndUndoMark doc)
  (princ (strcat "\n[Fix2BlockDanpoom] Modified: " (itoa cnt) " items (Green boxes drawn on AI_MOD_BOX). Run ClearModBoxes to remove boxes."))
  (princ)
)

(defun c:ClearModBoxes ( / doc ss i cnt )
  (setq doc (vla-get-ActiveDocument (vlax-get-acad-object)))
  (vla-StartUndoMark doc)
  (setq cnt 0)
  (setq ss (ssget "X" '((8 . "AI_MOD_BOX"))))
  (if ss
    (progn
      (setq i 0)
      (while (< i (sslength ss))
        (entdel (ssname ss i))
        (setq cnt (1+ cnt))
        (setq i (1+ i))
      )
      (setq ss nil)
    )
  )
  (vla-EndUndoMark doc)
  (princ (strcat "\n[ClearModBoxes] Removed " (itoa cnt) " highlight boxes."))
  (princ)
)

(princ "\nLoaded fix_2block_danpoom.lsp (v1.1). Commands: Fix2BlockDanpoom / ClearModBoxes")
(princ)
