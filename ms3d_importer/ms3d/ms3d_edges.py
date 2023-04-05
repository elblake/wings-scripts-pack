
##
##  MS3D Edge Functions
##  
##  Copyright 2023 Edward Blake
##
##  See the file "LICENSE" for information on usage and redistribution
##  of this file, and for a DISCLAIMER OF ALL WARRANTIES.
##

def first_common(m, meshes):
	vv = []
	el = []
	for v in m.vertices:
		(flags, v_x,v_y,v_z, u,v, bindex) = v
		vv.append((v_x,v_y,v_z))
	for t in m.trianglefaces:
		(flags, v1,v2,v3, n1,n2,n3, sg) = t
		el.append((vv[v2],vv[v1]))
		el.append((vv[v3],vv[v2]))
		el.append((vv[v1],vv[v3]))
	i = 0;
	for mc in meshes:
		elcomp = rev_edgecoords(mc)
		for e in el:
			if e in elcomp:
				return i
		i = i + 1

def rev_edgecoords(m):
	el = []
	vv = []
	for v in m.vertices:
		(flags, v_x,v_y,v_z, u,v, bindex) = v
		vv.append((v_x,v_y,v_z))
	for t in m.trianglefaces:
		(flags, v1,v2,v3, n1,n2,n3, sg) = t
		el.append((vv[v1],vv[v2]))
		el.append((vv[v2],vv[v3]))
		el.append((vv[v3],vv[v1]))
	return el

def alledges(fs):
	al = []
	for f in fs:
		i = 0
		fvs = f.vs
		lenfvs = len(fvs)-1
		for v1 in fvs:
			if i == lenfvs:
				v2 = fvs[0]
			else:
				v2 = fvs[i+1]
			al.append((v1,v2))
			i = i + 1
	return al
