
;;
;;  OFF file export
;;
;;  Copyright 2023 Edward Blake
;;
;;  See the file "LICENSE" for information on usage and redistribution
;;  of this file, and for a DISCLAIMER OF ALL WARRANTIES.
;;


(use srfi-1)
(use srfi-13)
;; sort assumed available from (use stfi-95)

;;;
;;; Export.
;;;

(define (export_fun Attr Filename Contents)
	(define Objs (e3d_file-objs Contents))
	
	(define Obj (car Objs))
	(define Mesh (combine_objects Objs))
	
	(let ((Vs (e3d_mesh-vs Mesh))
			(Vc (e3d_mesh-vc Mesh))
			(Tx (e3d_mesh-tx Mesh))
			(Ns (e3d_mesh-ns Mesh)))
		
		(define VNTC (list
			Vs
			Ns
			Tx
			Vc
			))
		 (call-with-values (lambda () (off_vlist_for_objs VNTC (list Mesh)))
			(lambda (Efs VList)
				(define OffExts '(has_c has_st))
		
				(define Vertices (map (lambda (VI) (car VI)
					) VList))
				(define Faces (map (lambda (X) X) Efs))
				
				(write_off_file Filename OffExts Vertices Faces)
				
			;	(wings-set-variable! "test" '(1 2 3 4))
			;	(wings-query "1")
			
				(newline)
				(write '(ok))
				))
		)

	)

(define (off_vlist_for_objs VNTC BList)
	(let loop ((BList BList)
		(OMesh (list))
		(VList (list)))
		
		(cond
			((equal? BList '())
				(values
				  (apply append (reverse OMesh))
				  (map (lambda (AC)
						(cdr AC))
				  (sort (map (lambda (AB)
						(list (list-ref AB 1) (list-ref AB 0))
						) VList) (lambda (a b) (< (car a) (car b))))))
				)
			(#t
			  (let ()
				(define M (car BList))
				(define BList_1 (cdr BList))
				(let ((Faces (e3d_mesh-fs M)))
					(call-with-values (lambda () (off_vlist_for_face VNTC Faces '() VList) )
						(lambda (Face_2 VList_2)
							(loop BList_1 (cons Face_2 OMesh) VList_2)
							))
					)))
	)))
	
	

(define (off_vlist_for_face VNTC Faces OEdges VList)
	
	(let loop ((Faces Faces)
		(OEdges (list))
		(VList VList))
		(cond
			((equal? Faces '())
				(values
					(reverse OEdges)
					VList
					)
				)
			(#t
			  (let()
				(define AL (car Faces))
				(define Faces_1 (cdr Faces))
				
				(let ((Edges_V (e3d_face-vs AL))
						(Edges_N (e3d_face-ns AL))
						(Edges_T (e3d_face-tx AL))
						(Edges_C (e3d_face-vc AL)))
					(call-with-values (lambda () (off_vlist_for_edges_1 VNTC Edges_V Edges_N Edges_T Edges_C (list) VList) )
						(lambda (AL_2 VList_2)
							(loop Faces_1 (cons (list 'face AL_2 'none) OEdges) VList_2)
							))
					)))
	)))
	

(define (off_vlist_for_edges_1 VNTC Edges_V Edges_N Edges_T Edges_C OEdge VList)
	(let loop ((Edges_V Edges_V)
			(Edges_N Edges_N)
			(Edges_T Edges_T)
			(Edges_C Edges_C)
			(OEdge OEdge)
			(VList VList))
		(cond
			((equal? Edges_V '())
				(values
					(reverse OEdge)
					VList
					)
				)
			(#t 
			  (let ()
				(define Idx (car Edges_V))
				(define Edges_V_1 (cdr Edges_V))
				(define Normal #f)
				(define Edges_N2 #f)
				(define UV #f)
				(define Edges_T2 #f)
				(define Color #f)
				(define Edges_C2 #f)
				(define AVs (list-ref VNTC 0))
				(define ANs (list-ref VNTC 1))
				(define ATs (list-ref VNTC 2))
				(define ACs (list-ref VNTC 3))
				
				
				(define Coord (list-ref AVs Idx))
				(cond
					((eq? Edges_N '()) 
						(set! Normal  #(0.0 0.0 0.0) )
						(set! Edges_N2  (list))
						)
					(#t (let ((N (car Edges_N)))
						(set! Edges_N2 (cdr Edges_N))
						(set! Normal  (list-ref ANs N) )
						)))
				
				(cond
					((eq? Edges_T '())
						(set! UV  #(0.0  0.0) )
						(set! Edges_T2  (list))
						)
					(#t (let ((T (car Edges_T)))
						(set! Edges_T2 (cdr Edges_T))
						(set! UV  (list-ref ATs T) )
						)))
				
				
				(cond
					((eq? Edges_C '())
						(set! Color  #(0.7 0.7 0.7) )
						(set! Edges_C2  (list))
						)
					(#t (let ((C (car Edges_C)))
						(set! Edges_C2 (cdr Edges_C))
						(set! Color  (list-ref ACs C))
						)))
				
				(let ((Vert  (list 'v Coord Normal Color UV)))
					(call-with-values (lambda () (off_vlist_index VList Vert) )
						(lambda (Idx2 VList_2)
							(loop Edges_V_1 Edges_N2 Edges_T2 Edges_C2 (cons Idx2 OEdge) VList_2)
							)))
				)))
	))

(define (off_vlist_index List NewVert)
	(define Found (assoc NewVert List))
	(cond
		((eq? Found #f)
			(let ((NewIdx (length List)))
				(values
					NewIdx
					(cons (list NewVert NewIdx) List)
					)
				))
		(#t (let ((Idx (list-ref Found 1)))
			(values Idx List)
			)))
	
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

;;;
;;;

(define (write_off_file FileName OffExts Vertices Faces)
	(call-with-output-file FileName (lambda (Fp)
		; Header
		; Texture coordinates
		(if (memv 'has_st OffExts)
			(display "ST" Fp)
			#t)
		; Colors
		(if (memv 'has_c OffExts)
			(display "C" Fp)
			#t)
		; Normals
		(if (memv 'has_n OffExts)
			(display "N" Fp)
			#t)
		(display "OFF" Fp)
		(newline Fp)
		
		(display (format "~w ~w ~w\n" (length Vertices) (length Faces) 0) Fp)
		(newline Fp)
		(write_vertices Fp Vertices OffExts)
		(write_faces Fp Faces)
		#t) :encoding 'utf8
	))
	
(define (write_vertices Fp Vertices OffExts)
	(cond
		((equal? Vertices '())
			#t)
		(#t 
			(let*((V (car Vertices))
				  (Coords (list-ref V 1))
				  (Norms (list-ref V 2))
				  (VColor (list-ref V 3))
				  (UV (list-ref V 4))
				  (RVertices (cdr Vertices)))
				(let ((V_X (vector-ref Coords 0))
					  (V_Y (vector-ref Coords 1))
					  (V_Z (vector-ref Coords 2)))
					(display (format "~f ~f ~f " V_X V_Y V_Z) Fp)
					
					(if (memv 'has_n OffExts)
						(write_vertices_normals Fp Norms)
						#t)
					(if (memv 'has_c OffExts)
						(write_vertices_colors Fp VColor)
						#t)
					(if (memv 'has_st OffExts)
						(write_vertices_texcoords Fp UV)
						#t)
					(newline Fp)
					(write_vertices Fp RVertices OffExts))))
	))

(define (write_vertices_normals Fp XYZ)
	(cond
		((eq? XYZ 'none)
			(display (format "~f ~f ~f " 0.0 0.0 0.0) Fp))
		(#t
			(let ((V_X (vector-ref XYZ 0))
				  (V_Y (vector-ref XYZ 1))
				  (V_Z (vector-ref XYZ 2)))
				(display (format "~f ~f ~f " V_X V_Y V_Z) Fp)))
	))
	
;; Colors are in RGBA floats
(define (write_vertices_colors Fp RGB)
	(cond
		((eq? RGB 'none)
			(display (format "~f ~f ~f ~f " 0.7 0.7 0.7 1.0) Fp))
		(#t
			(let ((V_R (vector-ref RGB 0))
				  (V_G (vector-ref RGB 1))
				  (V_B (vector-ref RGB 2)))
				(display (format "~f ~f ~f ~f " V_R V_G V_B 1.0) Fp)))
	))

(define (write_vertices_texcoords Fp VU)
	(cond
		((eq? VU 'none)
			(display (format "~f ~f " 0.0 0.0) Fp))
		(#t
			(let ((V_U (vector-ref VU 0))
				  (V_V (vector-ref VU 1)))
				(display (format "~f ~f " V_U V_V) Fp)))
		))


(define (write_faces Fp Faces)
	(let loop ((Faces Faces))
		(cond
			((equal? Faces '())
				#t)
			(#t
				(let ((F1 (car Faces))
					  (RFaces (cdr Faces)))
					(define VertIndices (list-ref F1 1))
					(define FaceColor (list-ref F1 2))
					(display (format "~w " (length VertIndices)) Fp)
					(map (lambda (VertIdx)
						(display (format " ~w" VertIdx) Fp)
						) VertIndices)
					(write_faces_colorspec Fp FaceColor)
					(newline Fp)
					(loop RFaces)))
	)))
	
(define (write_faces_colorspec Fp ColorSpec)
	; to end-of-line; may be 0 to 4 numbers
	(cond
		((eq? ColorSpec 'none)
			; nothing: default
			#t)
		((exact? ColorSpec)
			; integer: colormap index
			(display (format " ~w" ColorIndex) Fp))
		((and (vector? ColorSpec) (eq? (vector-length ColorSpec) 3))
			(let ((R (vector-ref ColorSpec 0))
				  (G (vector-ref ColorSpec 1))
				  (B (vector-ref ColorSpec 2)))
				; 3 or 4 floats: RGB[A] values 0..1
				(display (format " ~f ~f ~f" R G B) Fp)
				))
		((and (vector? ColorSpec) (eq? (vector-length ColorSpec) 4))
			(let ((R (vector-ref ColorSpec 0))
				  (G (vector-ref ColorSpec 1))
				  (B (vector-ref ColorSpec 2))
				  (A (vector-ref ColorSpec 3)))
				; 3 or 4 floats: RGB[A] values 0..1
				(display (format " ~f ~f ~f ~f" R G B A) Fp)
				))
	))

;;;
;;;

(define (exporter)
	;; e3d_file tuple is found in "content" of extra parameters, and the
	;; filename to export to is in filename.
	;;
	(define Filename (list-ref (assoc "filename" *extra-params*) 1))
	(define Content (list-ref (assoc "content" *extra-params*) 1))
	(newline)
	(export_fun '() Filename Content)
	)

; UNCOMMENT: 
(exporter)
