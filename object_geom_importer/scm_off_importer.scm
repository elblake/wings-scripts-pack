
;;
;;  OFF file import
;;
;;  Copyright 2023 Edward Blake
;;
;;  See the file "LICENSE" for information on usage and redistribution
;;  of this file, and for a DISCLAIMER OF ALL WARRANTIES.
;;


(use srfi-1)
(use srfi-13)

;;;
;;; Import.
;;;

(define (import_fun Attr Filename)
	(define ObjName Filename)
	(let ((VertAndFaces (read_off_file Filename)))
		(define OffExts (list-ref VertAndFaces 0))
		(define Vertices (list-ref VertAndFaces 1))
		(define Faces (list-ref VertAndFaces 2))
		(define Vs (map (lambda (V)
				(list-ref V 1)
				) Vertices))
		
		(define Vc (map (lambda (V)
			(let ((Color (list-ref V 3)))
				(case Color
					((none) #(0.9 0.9 0.9) )
					(else   Color))
				)) Vertices))
		
		(define Tx (map (lambda (V)
			(let ((UV (list-ref V 4)))
				(case UV
					((none) #(0.0 0.0) )
					(else   UV))
				)) Vertices))
		
		(define Efs (map (lambda (X)
					(define Idxs (list-ref X 1))
					(make-e3d_face 
						`(vs ,Idxs)
						
						`(vc ,Idxs)
						`(tx ,Idxs)
						`(ns ,(list))
					)) Faces))
		
		(define Mesh (make-e3d_mesh
			`(type polygon)
			`(vs ,Vs)
			`(fs ,Efs)
			
			`(vc ,Vc)
			`(tx ,Tx)
			`(ns ,(list))
			
			`(he ,(all_edges (map e3d_face-vs Efs)))
		))
		
		(define Obj (make-e3d_object `(name ,ObjName) `(obj ,Mesh)))

		(newline)
		(write (list 'ok (make-e3d_file `(objs ,(list Obj)))))
		
	))

;;;;
;;;;

(define (read_off_file FileName)
	(call-with-input-file FileName (lambda (Fp)
		(define OffExts (read_header Fp))
		(define NDimensions
			(cond
				((memv 'has_dim OffExts)
					(read_next_number Fp))
				((memv 'has_4d OffExts)
					4)
				(#t
					3)))
		(cond
			((< NDimensions 3)
				(error 'need_3_dimensions))
			(#t
				(let ()
					(define NVertices (read_next_number Fp))
					(define NFaces (read_next_number Fp))
					(define NEdgesUnused (read_next_number Fp))
				
					(define VerticesList (read_vertices Fp NVertices NDimensions OffExts))
					(define Faces (read_faces Fp NFaces))
					
					(list OffExts VerticesList Faces))
				)
			)
		) :encoding 'utf8))
	

(define (read_vertices Fp Start NDimensions OffExts)
	(let loop ((N Start) (VerticesList '()))
		(cond
			((eq? N 0)
				(reverse VerticesList))
			(#t
				(let*((V_X (read_next_number Fp))
				      (V_Y (read_next_number Fp))
					  (V_Z (read_next_number Fp)))
				;; Read but don't use extra dimensions
				(define _Unused (read_extra_dims Fp (- NDimensions 3)))
				(define Norms
					(if (memv 'has_n OffExts)
						(read_vertices_normals Fp)
						'none))
				(define VColor
					(if (memv 'has_c OffExts)
						(read_vertices_colors Fp)
						'none))
				(define UV
					(if (memv 'has_st OffExts)
						(read_vertices_texcoords Fp)
						'none))
				(loop (- N 1)
					  (cons (list 'v (vector (exact->inexact V_X)
					                         (exact->inexact V_Y)
											 (exact->inexact V_Z))
									 Norms VColor UV)
					        VerticesList))))
			)
		)
	)
	
(define (read_extra_dims Fp N)
	(cond
		((eq? N 0)
			#t)
		(#t
			(read_next_number Fp)
			(read_extra_dims Fp (- N 1))))
	)

(define (read_vertices_normals Fp)
	(define V_X (read_next_number Fp))
	(define V_Y (read_next_number Fp))
	(define V_Z (read_next_number Fp))
	(vector (exact->inexact V_X)
		    (exact->inexact V_Y)
			(exact->inexact V_Z)))
	
;; Colors are in RGBA floats.
(define (read_vertices_colors Fp)
	(define V_R (read_next_number Fp))
	(define V_G (read_next_number Fp))
	(define V_B (read_next_number Fp))
	(define V_Alpha (read_next_number Fp))
	(vector (exact->inexact V_R)
		    (exact->inexact V_G)
			(exact->inexact V_B)))
	
(define (read_vertices_texcoords Fp)
	(define V_U (read_next_number Fp))
	(define V_V (read_next_number Fp))
	(vector (exact->inexact V_U)
		    (exact->inexact V_V)))

(define (read_faces Fp N)
	(let loop ((N N) (Faces '()))
		(cond
			((eq? N 0)
				(reverse Faces))
			(#t
				(let ()
				;; Faces are line-ending significant.
				;;
				(define NumVerts (read_next_number Fp))
				;; Get the next indices less one, the last vertice is read with
				;; everything else up to the new line.
				;;
				(define VertIndices_0 (read_most_indices (- NumVerts 1) Fp))
				
				;; Get the rest of the line
				(define WholeLine (read_next_to_newline Fp))
				(define LL0 (filter (lambda (Prt) (not (equal? "" Prt)))
					(split_spaces WholeLine)))
				
				(define LastIndice_S (car LL0))
				(define RestOfList (cdr LL0))
				(define LastIndice (string->number LastIndice_S))
				(define VertIndices (append VertIndices_0 (list LastIndice)))
				(define FaceColor (parse_color_spec (list_to_color_list RestOfList)))
				(loop (- N 1)
					(cons (list 'face VertIndices FaceColor) Faces)))
				)
			)
		)
	)
(define (read_most_indices N Fp)
	(cond
		((<= N 0)
			'())
		(#t
			(let ((I (read_next_number Fp)))
				(cons I (read_most_indices (- N 1) Fp)))))
	)

(define (parse_color_spec RestOfList)
	;; to end-of-line; may be 0 to 4 numbers
	(cond 
		((equal? '() RestOfList)
			;; nothing: default
			'none
			)
		((eq? (length RestOfList) 1)
			(let ((ColorIndex (car RestOfList)))
				;; integer: colormap index
				ColorIndex
			))
		((eq? (length RestOfList) 4)
			(cond
				((exact? (car RestOfList))
					(let ((R (list-ref RestOfList 0))
						  (G (list-ref RestOfList 1))
						  (B (list-ref RestOfList 2))
						  (A (list-ref RestOfList 3)))
						;; 3 or 4 integers: RGB[A] values 0..255
						(vector (/ R 255.0) (/ G 255.0) (/ B 255.0) (/ A 255.0)))
					)
				((inexact? (car RestOfList))
					(let ((R (list-ref RestOfList 0))
						  (G (list-ref RestOfList 1))
						  (B (list-ref RestOfList 2))
						  (A (list-ref RestOfList 3)))
						;; 3 or 4 floats: RGB[A] values 0..1
						(vector R G B A))
					))
			)
		((eq? (length RestOfList) 3)
			(cond
				((exact? (car RestOfList))
					(let ((R (list-ref RestOfList 0))
						  (G (list-ref RestOfList 1))
						  (B (list-ref RestOfList 2)))
						;; 3 or 4 integers: RGB[A] values 0..255
						(vector (/ R 255.0) (/ G 255.0) (/ B 255.0) 1.0))
					)
				((inexact? (car RestOfList))
					(let ((R (list-ref RestOfList 0))
						  (G (list-ref RestOfList 1))
						  (B (list-ref RestOfList 2)))
						;; 3 or 4 floats: RGB[A] values 0..1
						(vector R G B 1.0))
					))
			)
	))
(define (list_to_color_list List_0)
	(cond
		((equal? '() List_0)
			'())
		(#t
			(let ((A (car List_0))
				  (List (cdr List_0)))
				(cond
					((inexact? (string->number A))
						(cons (string->number A) (list_to_color_list List)))
					((exact? (string->number A))
						(cons (string->number A) (list_to_color_list List)))))
			))
	)

(define (read_header_1 A)
	(let loop ((R_1 A) (OffExts '()))
	(cond
		((equal? "OFF" R_1)
			OffExts)
		((equal? "ST" (substring R_1 0 2))
			(loop (substring R_1 2 -1) (cons 'has_st OffExts)))
		((equal? "C" (substring R_1 0 1))
			(loop (substring R_1 1 -1) (cons 'has_c OffExts)))
		((equal? "N" (substring R_1 0 1))
			(loop (substring R_1 1 -1) (cons 'has_n OffExts)))
		((equal? "4" (substring R_1 0 1))
			(loop (substring R_1 1 -1) (cons 'has_4d OffExts)))
		((equal? "n" (substring R_1 0 1))
			(loop (substring R_1 1 -1) (cons 'has_dim OffExts)))
		))
	)
(define (read_header Fp)
	(define A (read_next_to_space Fp))
	(cond
		((eq? (string->number A) #f)
			(read_header_1 A))
		(#t
			;; An integer number was encountered, there was no header
			(set-port-position! Fp 0)
			'()))
	)
	
	
(define (read_next_to_space Fp2)
	(let loop ((Chars '()))
		(cond
			((equal? '() Chars)
				(let ((C1 (read-char Fp2)))
					(cond
						((or (eq? C1 #\return) (eq? C1 #\newline) (eq? C1 #\space) (eq? C1 #\tab))
							(read_next_to_space Fp2)
							)
						((eq? C1 #\#)
							(read-line Fp2)
							(loop '())
							)
						(#t
							(loop (list C1))
							)
						)
					)
				)
			(#t
				(let ((C1 (read-char Fp2)))
					(cond
						((or (eq? C1 #\return) (eq? C1 #\newline) (eq? C1 #\space) (eq? C1 #\tab))
							(list->string (reverse Chars)))
						((equal? C1 #\#)
							(read-line Fp2)
							(loop Chars))
						(#t
							(loop (cons C1 Chars))))
					)
				)
		)))

(define (read_next_number Fp2)
	(define NextNumber_S (read_next_to_space Fp2))
	(define NextNumber (string->number NextNumber_S))
	(cond
		((eq? NextNumber #f)
			0)
		(#t
			NextNumber))
		)

(define (read_next_to_newline Fp2)
	(let loop ((Chars '()))
		(define C1 (read-char Fp2))
		(cond
			((or (eq? C1 #\return) (eq? C1 #\newline))
				(cond 
					((equal? '() Chars)
						(read_next_to_newline Fp2))
					(#t
						(list->string (reverse Chars)))
				))
			((eq? C1 #\#)
				;; Read the rest up to new line after comment.
				(let ((CommentItself (read-line Fp2)))
					(list->string (reverse Chars)))
				)
			(#t
				(loop (cons C1 Chars))
				))
	))

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


;UNCOMMENT:
(importer)
