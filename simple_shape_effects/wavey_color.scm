
;;
;;  Wavey Color
;;
;;  Waveforms modulate the colors.
;;
;;  Copyright 2023 Edward Blake
;;
;;  See the file "LICENSE" for information on usage and redistribution
;;  of this file, and for a DISCLAIMER OF ALL WARRANTIES.
;;

(define (command *params* *extra-params*)
	(define op     (list-ref (assoc "op" *extra-params*) 1))
	(define points (list-ref (assoc "points" *extra-params*) 1))
	(define Faces  (list-ref (assoc "faces" *extra-params*) 1))

	;; Amplitude of the waves
	(define amp_x (list-ref *params* 0))
	(define amp_y (list-ref *params* 1))
	(define amp_z (list-ref *params* 2))

	;; Angle of the waves
	(define wave_ang_x (* (/ (list-ref *params* 3) 180.0) 3.141592))
	(define wave_ang_y (* (/ (list-ref *params* 4) 180.0) 3.141592))
	(define wave_ang_z (* (/ (list-ref *params* 5) 180.0) 3.141592))

	(define wave_ang_x_y (sin wave_ang_x))
	(define wave_ang_x_z (cos wave_ang_x))

	(define wave_ang_y_x (sin wave_ang_y))
	(define wave_ang_y_z (cos wave_ang_y))

	(define wave_ang_z_x (sin wave_ang_z))
	(define wave_ang_z_y (cos wave_ang_z))

	;; Period of the waves
	(define freq_x (/ (* 2.0 3.141592) (list-ref *params* 6)))
	(define freq_y (/ (* 2.0 3.141592) (list-ref *params* 7)))
	(define freq_z (/ (* 2.0 3.141592) (list-ref *params* 8)))

	(define (mix_range A)
		(max 0.0 (min 1.0 A)))

	(define MixAmount (mix_range (list-ref *params* 9)))

	(define PointsByIdx (map (lambda (X) (cons (vector-ref X 0) (vector-ref X 1))) points))
		
	(define (rgb_c R)
		(if (< R 0.0) 0.0 (if (> R 1.0) 1.0 R)))

	(define (per_rgb X Y Z)
		(define R_1 (+ (* amp_x (sin (* (+ (* Y wave_ang_x_y) (* Z wave_ang_x_z)) freq_x))) X))
		(define G_1 (+ (* amp_y (sin (* (+ (* X wave_ang_y_x) (* Z wave_ang_y_z)) freq_y))) Y))
		(define B_1 (+ (* amp_z (sin (* (+ (* X wave_ang_z_x) (* Y wave_ang_z_y)) freq_z))) Z))
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
		

	(list (list 'set_face_colors NewFaceColors))
	)

(main-function command)
