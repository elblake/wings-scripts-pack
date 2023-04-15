
;;
;;  Distorted Scaling
;;  The amount of scaling applied on each point depends on its location
;;  such that some points get scaled more than others, creating a
;;  distorted effect.
;;
;;  Copyright 2023 Edward Blake
;;
;;  See the file "LICENSE" for information on usage and redistribution
;;  of this file, and for a DISCLAIMER OF ALL WARRANTIES.
;;

(define op     (list-ref (assoc "op" *extra-params*) 1))
(define points (list-ref (assoc "points" *extra-params*) 1))

;(display "TEST:")(write points)(newline)

;; The center of the ripple
(define center_x (list-ref *params* 0))
(define center_y (list-ref *params* 1))
(define center_z (list-ref *params* 2))

(define ripple_amp (list-ref *params* 3))
(define ripple_freq (/ (* 2.0 3.141592) (list-ref *params* 4)))

(define (get_distance x y z)
	(define xz (sqrt (+ (* x x) (* z z))))
	(sqrt (+ (* xz xz) (* y y)))
	)

(define (per_point x y z)
	(let ((x1 (- x center_x))
		  (y1 (- y center_y))
		  (z1 (- z center_z)))
		(define rad (get_distance x y z))
		(define scl (+ 1.0 (* ripple_amp (sin (* rad ripple_freq)))))
		(let ((x2 (* scl x1))
			  (y2 (* scl y1))
			  (z2 (* scl z1)))
			(let ((x3 (+ center_x x2))
				  (y3 (+ center_y y2))
				  (z3 (+ center_z z2)))
				(vector x3 y3 z3)
				)
			)
		)
  )

(define newpoints
	(map (lambda (p)
		(define a (vector-ref p 0))
		(define b (vector-ref p 1))
		(let ((x (vector-ref b 0))
		      (y (vector-ref b 1))
		      (z (vector-ref b 2)))
			(vector a (per_point x y z)))
	) points))

(newline)
(write (list (list 'set_points newpoints)))
