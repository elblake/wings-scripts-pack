
;;
;;  Raw triangles file import
;;
;;  Copyright 2023 Edward Blake
;;
;;  See the file "LICENSE" for information on usage and redistribution
;;  of this file, and for a DISCLAIMER OF ALL WARRANTIES.
;;

;;
;; Read Raw Triangles File
;; 

(use srfi-1)
(use srfi-13)

(define (remove_comment Ln)
	(define WhereComment (string-index Ln #\#))
	(if (equal? WhereComment #f)
		Ln
		(substring Ln 0 WhereComment)
		)
	)

(define (read_non_blank Fp)
	(let loop ()
		(define Ln (read-line Fp))
		(if (eof-object? Ln)
			Ln
			(begin
				(set! Ln (string-trim (remove_comment Ln)))
				(if (not (equal? Ln ""))
					Ln
					(loop))))
		)
	)

(define (split_spaces A)
	(let loop ((A (string->list A)) (L1 '()) (L2 '()))
		(cond
			((equal? '() A)
				(reverse (if (eq? 0 (length L1))
						L2
						(cons (list->string (reverse L1)) L2))))
			(#t
				(let ((C (car A))
					  (R (cdr A)))
					(cond
						((or (eq? C #\tab) (eq? C #\space))
							(if (eq? 0 (length L1))
								(loop R '() L2)
								(loop R '() (cons (list->string (reverse L1)) L2))))
						(#t
							(loop R (cons C L1) L2))))
				))
		)
	)

(define (append_object Name TL Objs)
	(if (equal? '() TL)
		Objs
		(let ((VertAndFaces (polygons_to_vlist TL)))
			(define Vert (list-ref VertAndFaces 0))
			(define Faces (list-ref VertAndFaces 1))
			(cons (list Name Vert Faces) Objs)))
	)

(define (read_raw_file Flname)
	(call-with-input-file Flname (lambda (Fp)
		(let loop ((Name "NoName") (Objs '()) (TL '()))
			(define NextLn (read_non_blank Fp))
			(if (eof-object? NextLn)
				(reverse (append_object Name (reverse TL) Objs))
				(let ()
					(define NextLn_a (split_spaces NextLn))
					(define FirstChar (car (string->list (car NextLn_a) 0 1)))
					(cond
						((or (and (char>=? FirstChar #\0) (char<=? FirstChar #\9)) (eq? FirstChar #\-) (eq? FirstChar #\.))
							(cond
								((eq? 10 (length NextLn_a))
									;; Texture name and triangle
									(let ((X1 (string->number (list-ref NextLn_a 0)) )
										  (Y1 (string->number (list-ref NextLn_a 1)) )
										  (Z1 (string->number (list-ref NextLn_a 2)) )
										  
										  (X2 (string->number (list-ref NextLn_a 3)) )
										  (Y2 (string->number (list-ref NextLn_a 4)) )
										  (Z2 (string->number (list-ref NextLn_a 5)) )
										  
										  (X3 (string->number (list-ref NextLn_a 6)) )
										  (Y3 (string->number (list-ref NextLn_a 7)) )
										  (Z3 (string->number (list-ref NextLn_a 8)) )
										  (MaterialName (list-ref NextLn_a 9)))
										(define Coord1 (vector X1 Y1 Z1))
										(define Coord2 (vector X2 Y2 Z2))
										(define Coord3 (vector X3 Y3 Z3))
										(loop Name Objs (cons (list (list Coord1 Coord2 Coord3) 'none) TL)))
									)
								((eq? 12 (length NextLn_a))
									;; Color and triangle
									(let ((X1 (string->number (list-ref NextLn_a 3)) )
										  (Y1 (string->number (list-ref NextLn_a 4)) )
										  (Z1 (string->number (list-ref NextLn_a 5)) )
										  
										  (X2 (string->number (list-ref NextLn_a 6)) )
										  (Y2 (string->number (list-ref NextLn_a 7)) )
										  (Z2 (string->number (list-ref NextLn_a 8)) )
										  
										  (X3 (string->number (list-ref NextLn_a 9)) )
										  (Y3 (string->number (list-ref NextLn_a 10)) )
										  (Z3 (string->number (list-ref NextLn_a 11)) )
										  
										  (R  (string->number (list-ref NextLn_a 0)) )
										  (G  (string->number (list-ref NextLn_a 1)) )
										  (B  (string->number (list-ref NextLn_a 2)) ))
										(define Coord1 (vector X1 Y1 Z1))
										(define Coord2 (vector X2 Y2 Z2))
										(define Coord3 (vector X3 Y3 Z3))
										(loop Name Objs (cons (list (list Coord1 Coord2 Coord3) (vector R G B)) TL)))
									)
								(#t
									;; Nine numbers for a triangle
									(let ((X1 (string->number (list-ref NextLn_a 0)) )
										  (Y1 (string->number (list-ref NextLn_a 1)) )
										  (Z1 (string->number (list-ref NextLn_a 2)) )
										  
										  (X2 (string->number (list-ref NextLn_a 3)) )
										  (Y2 (string->number (list-ref NextLn_a 4)) )
										  (Z2 (string->number (list-ref NextLn_a 5)) )
										  
										  (X3 (string->number (list-ref NextLn_a 6)) )
										  (Y3 (string->number (list-ref NextLn_a 7)) )
										  (Z3 (string->number (list-ref NextLn_a 8)) ))
										(define Coord1 (vector X1 Y1 Z1))
										(define Coord2 (vector X2 Y2 Z2))
										(define Coord3 (vector X3 Y3 Z3))
										(loop Name Objs (cons (list (list Coord1 Coord2 Coord3) 'none) TL)))
									)
								)
							)
						(#t
							(loop (car NextLn_a) (append_object Name (reverse TL) Objs) '()))
						)
					)
				)
			)) :encoding 'utf8)
	)


;;;
;;; Import.
;;;

(define (numbered_list A)
	(let loop ((A A) (I 0) (O '()))
		(if (equal? '() A)
			(reverse O)
			(loop (cdr A) (+ I 1) (cons (list I (car (car A))) O))))
	)

(define (import_fun Attr Filename)
	(define Objs (read_raw_file Filename))
	(define Objs_1
		(let loop ((Objs Objs) (O '()))
			(if (equal? '() Objs)
				(reverse O)
				(let ()
					(define VertAndFaces (car Objs))
					(define ObjName (list-ref VertAndFaces 0))
					(define Vertices (list-ref VertAndFaces 1))
					(define Faces (list-ref VertAndFaces 2))
					(define Vs (map (lambda (V)
						(define Coord V) ;(list-ref V 0))
						Coord) Vertices))
					
					(define Vc (map (lambda (F)
						(let ((Color (list-ref F 1)))
							(case Color
								((none) #(0.9 0.9 0.9) )
								(else   Color))
							)) Faces))
					
					(define Efs (map (lambda (X)
						(define CI (list-ref X 0))
						(define VI (list-ref X 1))
						(make-e3d_face 
							`(vs ,VI)
							`(vc ,(list CI CI CI))
						)) (numbered_list Faces)))
					
					(define Mesh (make-e3d_mesh
						`(type polygon)
						`(vs ,Vs)
						`(fs ,Efs)
						`(vc ,Vc)
						`(he ,(all_edges (map e3d_face-vs Efs)))
					))
					(define Obj (make-e3d_object `(name ,ObjName) `(obj ,Mesh)))
					(loop (cdr Objs) (cons Obj O))
					)
				)
			)
		)
		
	

	(newline)
	(write (list 'ok (make-e3d_file `(objs ,Objs_1))))
	)

;;;
;;;


(define (add_idx AC VList)
	(define X (assoc AC VList))
	(cond
		((eq? #f X)
			(let ((NIdx (length VList)))
				(set! VList (cons (list AC NIdx) VList))
				(values NIdx VList)))
		(#t
			(values (cadr X) VList))))

(define (nov1 L VList)
	(let loop ((L L) (VI '()) (VList VList))
		(if (equal? '() L)
			(values (reverse VI) VList)
			(call-with-values (lambda () (add_idx (car L) VList)) (lambda (Idx VList_1)
				;(set! VList VList_0)
				(loop (cdr L) (cons Idx VI) VList_1)
				))
			)
		)
	)

(define (nov L)
	(define VList '())
	(let loop ((L L) (FL '()) (VList VList))
		(if (equal? '() L)
			(values (reverse FL) VList)
			(let ((Vs1 (list-ref (car L) 0)) (Color (list-ref (car L) 1)))
			(call-with-values (lambda () (nov1 Vs1 VList)) (lambda (VI VList_1)
				(loop (cdr L) (cons (list VI Color) FL) VList_1)
				)))
			)
		)
	)

(define (polygons_to_vlist Polys)	
	(call-with-values (lambda () (nov Polys))
		(lambda (FL VL)
			(define VL_1
				(map (lambda (AB) (cadr AB))
					(sort (map (lambda (AB)
						(list (list-ref AB 1) (list-ref AB 0))
						) VL) (lambda (a b) (< (car a) (car b)))) ))
			(list VL_1 FL)))
	)

;;;
;;;

(define (edge_pairs Fs_0)
	(let ((E0 (car Fs_0)))
		(let loop ((Fs Fs_0) (OL '()))
			(if (> (length Fs) 1)
				(let ((E1 (car Fs)) (E2 (list-ref Fs 1)))
					(loop (cdr Fs) (cons (vector E1 E2) OL))
					)
				(let ((E1 (car Fs)))
					(reverse (cons (vector E1 E0) OL))
					)
				)
			)
		)
	)
(define (all_edges FL)
    (apply append (map (lambda (F) (edge_pairs F)) FL))
	)

(define (importer)
	;; the filename to import from is in "filename" of extra parameters.
	;;
	(define Filename (list-ref (assoc "filename" *extra-params*) 1))

	(import_fun '() Filename)
	)

(importer)
