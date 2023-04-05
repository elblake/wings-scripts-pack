
;;
;;  Heightmap Exporter
;;
;;  Export a bitmap height map by sampling at fixed intervals the maximum
;;  height of models in the scene.
;;
;;  Copyright 2023 Edward Blake
;;
;;  See the file "LICENSE" for information on usage and redistribution
;;  of this file, and for a DISCLAIMER OF ALL WARRANTIES.
;;

(use srfi-1)
(use srfi-13)
;; sort assumed available from (use stfi-95)


(define (write_to_pgm FileNm Vals MaxVal)
	(define Width (length (car Vals)))
	(define Height (length Vals))
	(call-with-output-file FileNm (lambda (Fo)
		(format Fo "P2\n")
		(format Fo "~w ~w\n" Width Height)
		(format Fo "~w\n" MaxVal)
		(let loop_z ((Vals Vals))
			(if (not (pair? Vals))
				#t
				(let ()
					(let loop_x ((Vals (car Vals)))
						(if (not (pair? Vals))
							#t
							(let ()
								(format Fo "~w " (car Vals))
								(loop_x (cdr Vals)))))
					(format Fo "\n")
					(loop_z (cdr Vals)))
				)
			)
		))
	)

(define (tri_area L1 L2 L3)
    (define S (/ (+ L1 L2 L3) 2.0))
	(define Area (sqrt (* S (- S L1) (- S L2) (- S L3))))
	;;(format (current-output-port) ">> ~w ~w ~w -> ~w\n" L1 L2 L3 Area)
	(if (real? Area) Area 0.0)
	)

(define (line_length X1 Z1 X2 Z2)
    (if (> X1 X2)
		(line_length_1 X2 Z1 X1 Z2)
		(line_length_1 X1 Z1 X2 Z2)
		)
	)
(define (line_length_1 X1 Z1 X2 Z2)
    (if (> Z1 Z2)
		(line_length_2 X1 Z2 X2 Z1)
		(line_length_2 X1 Z1 X2 Z2)
		)
	)
(define (line_length_2 X1 Z1 X2 Z2)
    (define XD (- X2 X1))
    (define ZD (- Z2 Z1))
    (sqrt (+ (* XD XD) (* ZD ZD)))
	)
	
(define (tri_height X Z Tri)
	(define T1X (vector-ref Tri 0))
	(define T1Y (vector-ref Tri 1))
	(define T1Z (vector-ref Tri 2))
	(define T2X (vector-ref Tri 3))
	(define T2Y (vector-ref Tri 4))
	(define T2Z (vector-ref Tri 5))
	(define T3X (vector-ref Tri 6))
	(define T3Y (vector-ref Tri 7))
	(define T3Z (vector-ref Tri 8))
	(define L1L2L (line_length T1X T1Z T2X T2Z))
	(define L2L3L (line_length T2X T2Z T3X T3Z))
	(define L3L1L (line_length T3X T3Z T1X T1Z))
	(define LLT (tri_area L1L2L L2L3L L3L1L))
	(if (< LLT 0.00001)
		-10000.0
		(let ()
			(define L1L (line_length X Z T1X T1Z))
			(define L2L (line_length X Z T2X T2Z))
			(define L3L (line_length X Z T3X T3Z))
			(define U12 (/ (tri_area L1L L2L L1L2L) LLT))
			(define U23 (/ (tri_area L2L L3L L2L3L) LLT))
			(define U31 (/ (tri_area L3L L1L L3L1L) LLT))
			(define TotArea (+ U12 U23 U31))
			(if (> (+ U12 U23 U31) 1.0001)
				-10000.0
				(+ (* T3Y U12) (* T1Y U23) (* T2Y U31)))
			)
		)
	)

(define (level_at X Z Tris)
	(let loop ((Tris Tris) (MaxHeight -10000.0))
		(if (not (pair? Tris))
			MaxHeight
			(let ((Triangle (car Tris)))
				(loop (cdr Tris)
				      (max (tri_height X Z Triangle) MaxHeight)))
			)
		)
	)

(define (levels_row IZ Tris LenX SclX SclZ TrlX TrlZ)
	(let loop_z ((IX 0) (RL '()))
		(if (< IX LenX)
			(loop_z (+ IX 1) (cons (level_at (+ (* IX SclX) TrlX) (+ (* IZ SclZ) TrlZ) Tris) RL))
			(reverse RL)
			)
		)
	)
(define (levels Tris LenX LenZ SclX SclZ TrlX TrlZ)
	(let loop_x ((IZ 0) (OL '()))
		(if (< IZ LenZ)
			(loop_x (+ IZ 1) (cons (levels_row IZ Tris LenZ SclX SclZ TrlX TrlZ) OL))
			(reverse OL)
			)
		)
	)


(define (integer_clip_entry Val MaxVal SclY TrlY)
	(define Val1 (inexact->exact (round (+ (* Val SclY) TrlY))))
	(if (< Val1 0) 0
		(if (> Val1 MaxVal)
			MaxVal
			Val1))
	)
(define (integer_clip_row Vals MaxVal SclY TrlY)
	(let loop_z ((Vals Vals) (RL '()))
		(if (not (pair? Vals))
			(reverse RL)
			(loop_z (cdr Vals) (cons (integer_clip_entry (car Vals) MaxVal SclY TrlY) RL))
			)
		)
	)
(define (integer_clip Heights MaxVal SclY TrlY)
	(let loop_x ((Heights Heights) (OL '()))
		(if (not (pair? Heights))
			(reverse OL)
			(loop_x (cdr Heights) (cons (integer_clip_row (car Heights) MaxVal SclY TrlY) OL))
			)
		)
	)

(define (triangle_list VList Faces)
	(define VList_1 (list->vector VList))
	(map (lambda (VL)
			(define Coord1 (vector-ref VList_1 (list-ref VL 0)))
			(define Coord2 (vector-ref VList_1 (list-ref VL 1)))
			(define Coord3 (vector-ref VList_1 (list-ref VL 2)))
			(define T1X (vector-ref Coord1 0))
			(define T1Y (vector-ref Coord1 1))
			(define T1Z (vector-ref Coord1 2))
			(define T2X (vector-ref Coord2 0))
			(define T2Y (vector-ref Coord2 1))
			(define T2Z (vector-ref Coord2 2))
			(define T3X (vector-ref Coord3 0))
			(define T3Y (vector-ref Coord3 1))
			(define T3Z (vector-ref Coord3 2))
			(vector T1X T1Y T1Z T2X T2Y T2Z T3X T3Y T3Z)
			) Faces)
	)

(define (mesh_to_heights VList Faces MaxVal LenX LenZ SclX SclY SclZ TrlX TrlY TrlZ)
	;; List of vectors each containing three points of a triangle
	(define Tris (triangle_list VList Faces))
	(define Heights_0 (levels Tris LenX LenZ SclX SclZ TrlX TrlZ))
	(integer_clip Heights_0 MaxVal SclY TrlY))
	
(define (mesh_to_pgm FileNm VList Faces LenX LenZ SclX SclY SclZ TrlX TrlY TrlZ)
	(define MaxVal 32767)
	(define Heights (mesh_to_heights VList Faces MaxVal LenX LenZ SclX SclY SclZ TrlX TrlY TrlZ))
	(write_to_pgm FileNm Heights MaxVal)
	)


;;;
;;; Export.
;;;

(define (export_fun Filename Contents PixelWidth ScaleXZ ScaleY TrlX TrlY TrlZ)
	(define Objs (e3d_file-objs Contents))
	(define Mesh (combine_objects Objs))
	
	(let ((Vs (e3d_mesh-vs Mesh)))
		(define Faces (map (lambda (X) (e3d_face-vs X)) (e3d_mesh-fs Mesh)))
		(mesh_to_pgm Filename Vs Faces PixelWidth PixelWidth ScaleXZ ScaleY ScaleXZ TrlX TrlY TrlZ)
	
		(newline)
		(write '(ok))
		)
	)

(define (combine_objects Objs)
	(let loop (
		(VsOffset 0)
		(VcOffset 0)
		(TxOffset 0)
		(NoOffset 0)
		(Objs Objs)
		(Vs_L (list))
		(Fs_L (list))
		(Vc_L (list))
		(Tx_L (list))
		(No_L (list)))
		(cond
			((equal? Objs '())
				(make-e3d_mesh
					`(fs ,(map (lambda (E4)
							(define Ef (list-ref E4 0))
							(define Ec (list-ref E4 1))
							(define Et (list-ref E4 2))
							(define En (list-ref E4 3))
							(make-e3d_face `(vs ,Ef) `(vc ,Ec) `(tx ,Et) `(ns ,En))
							) Fs_L))
					`(vs ,Vs_L)
					`(vc ,Vc_L)
					`(tx ,Tx_L)
					`(ns ,No_L)
					)
				)
			(#t
			  (let ()
				(define Obj (car Objs))
				(define Objs_1 (cdr Objs))
				
				(define Mesh (e3d_object-obj Obj))
				(let ((Vs (e3d_mesh-vs Mesh))
						(Vc (e3d_mesh-vc Mesh))
						(Tx (e3d_mesh-tx Mesh))
						(No (e3d_mesh-ns Mesh)))
					(define Efs (map (lambda (F)
						(define Ef (e3d_face-vs F))
						(define Ec (e3d_face-vc F))
						(define Et (e3d_face-tx F))
						(define En (e3d_face-ns F))
						(list
						  (map (lambda (E) (+ E VsOffset)) Ef)
						  (map (lambda (C) (+ C VcOffset)) Ec)
						  (map (lambda (T) (+ T TxOffset)) Et)
						  (map (lambda (N) (+ N NoOffset)) En) )
						) (e3d_mesh-fs Mesh) ))
					(loop
						(+ VsOffset (length Vs))
						(+ VcOffset (length Vc))
						(+ TxOffset (length Tx))
						(+ NoOffset (length No))
						Objs_1
						(append Vs_L Vs)
						(append Fs_L Efs)
						(append Vc_L Vc)
						(append Tx_L Tx)
						(append No_L No) )
					)))
	)))
	
(define (get_param x)
	(car (car (cdr (assoc x *params*)))))

(define (exporter)
	;; e3d_file tuple is found in "content" of extra parameters, and the
	;; filename to export to is in filename.
	;;
	(define Filename (list-ref (assoc "filename" *extra-params*) 1))
	(define Content (list-ref (assoc "content" *extra-params*) 1))
	(define PixelWidth (get_param 'pixel_width))
	(define ScaleXZ (get_param 'scale_xz))
	(define ScaleY (get_param 'scale_y))
	(define TrlX (get_param 'trl_x))
	(define TrlY (get_param 'trl_y))
	(define TrlZ (get_param 'trl_z))

	(newline)
	(export_fun Filename Content PixelWidth ScaleXZ ScaleY TrlX TrlY TrlZ)
	)

(exporter)