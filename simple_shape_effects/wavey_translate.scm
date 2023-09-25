
;;
;;  Wavey Translate
;;
;;  A wave translates the vertices of the object, creating a wavey surface, most
;;  useful to apply to a multisegmented plane.
;;
;;  Copyright 2023 Edward Blake
;;
;;  See the file "LICENSE" for information on usage and redistribution
;;  of this file, and for a DISCLAIMER OF ALL WARRANTIES.
;;


(define (command *params* *extra-params*)
	(define op     (list-ref (assoc "op" *extra-params*) 1))
	(define points (list-ref (assoc "points" *extra-params*) 1))

	;;(display "TEST:")(write points)(newline)

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

	(define (per_point X Y Z)
		(vector
			(+ (* amp_x (sin (* (+ (* Y wave_ang_x_y) (* Z wave_ang_x_z)) freq_x))) X)
			(+ (* amp_y (sin (* (+ (* X wave_ang_y_x) (* Z wave_ang_y_z)) freq_y))) Y)
			(+ (* amp_z (sin (* (+ (* X wave_ang_z_x) (* Y wave_ang_z_y)) freq_z))) Z))
		)

	(define NewPoints
		(map (lambda (p)
			(define a (vector-ref p 0))
			(define b (vector-ref p 1))
			(let ((x (vector-ref b 0))
				  (y (vector-ref b 1))
				  (z (vector-ref b 2)))
				(vector a (per_point x y z)))
		) points))

	(newline)
	(write (list (list 'set_points NewPoints)))
	)

(main-function command)
