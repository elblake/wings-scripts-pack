
;;
;;  Color test
;;
;;  Sets a color based on where the point is in the scene.
;;
;;  Copyright 2023 Edward Blake
;;
;;  See the file "LICENSE" for information on usage and redistribution
;;  of this file, and for a DISCLAIMER OF ALL WARRANTIES.
;;


(define op     (list-ref (assoc "op" *extra-params*) 1))
(define points (list-ref (assoc "points" *extra-params*) 1))
(define Faces  (list-ref (assoc "faces" *extra-params*) 1))

(define (mix_range A)
	(max 0.0 (min 1.0 A)))

(define MixAmount (mix_range (list-ref *params* 0)))

(define PointsByIdx (map (lambda (X) (cons (vector-ref X 0) (vector-ref X 1))) points))


(define (rgb_c R)
	(if (< R 0.0) 0.0 (if (> R 1.0) 1.0 R)))

(define (per_rgb X Y Z)
	(define R_1 (if (< X 0.0) 0.0 1.0))
	(define G_1 (if (< Y 0.0) 0.0 1.0))
	(define B_1 (if (< Z 0.0) 0.0 1.0))
	(vector (rgb_c R_1) (rgb_c G_1) (rgb_c B_1))
	)

(define (map_vlist Fun ColorList0 VList0)
	(let loop ((ColorList ColorList0) (VList VList0) (Outp '()))
		(if (eq? '() ColorList)
			(reverse Outp)
			(loop (cdr ColorList) (cdr VList) (cons (Fun (car ColorList) (car VList)) Outp))
			)
		)
	)

(define (mix_color Col1 Col2 MixVal)
	(define C1R (vector-ref Col1 0))
	(define C1G (vector-ref Col1 1))
	(define C1B (vector-ref Col1 2))
	(define C2R (vector-ref Col2 0))
	(define C2G (vector-ref Col2 1))
	(define C2B (vector-ref Col2 2))
	(define C1MixVal (- 1.0 MixVal))
	(vector (+ (* C1MixVal C1R) (* MixVal C2R))
	        (+ (* C1MixVal C1G) (* MixVal C2G))
	        (+ (* C1MixVal C1B) (* MixVal C2B)))
	)

(define NewFaceColors
	(map (lambda (P)
		(define FIdx (vector-ref P 0))
		(define F (vector-ref P 1))
		(define VList (vector-ref F 0))
		(define ColorList (vector-ref F 1))
		(vector FIdx (map_vlist (lambda (B_0 VIdx)
			(define PrevCol (if (eq? #f B_0) (vector 0.7 0.7 0.7) B_0))
			(define V (cdr (assoc VIdx PointsByIdx)))
			(let ((X (vector-ref V 0))
				  (Y (vector-ref V 1))
				  (Z (vector-ref V 2)))
				(mix_color PrevCol (per_rgb X Y Z) MixAmount)
				)) ColorList VList))
	) Faces))

(newline)
(write (list (list 'set_face_colors NewFaceColors)))

