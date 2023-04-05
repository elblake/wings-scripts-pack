
##
##  Panda3D 3D Mesh Exporter
##
##  Copyright 2023 Edward Blake
##
##  See the file "LICENSE" for information on usage and redistribution
##  of this file, and for a DISCLAIMER OF ALL WARRANTIES.
##

import w3d_e3d
import sys
from os import path

from egg_text import nodes

##
## Write Panda3D File
## 

def quote_path(p):
	p = p.replace("\\", "/")
	if p[1] == ":":
		p_r = p[2:]
		if p_r[0] != "/":
			p_r = "/" + p_r
		p_1 = "/" + p[0] + p_r
	else:
		p_1 = p
	return "\"" + p_1 + "\""
	

def write_panda3d_file(flname, objs, materials):
	f = nodes.EggFile()
	f.add(nodes.CoordinateSystem())
	f.add(nodes.Comment("Exported with Wings3D Panda3D Exporter Script"))
	
	flname_dirname = path.dirname(flname)
	
	mt_trefs = {}
	for mt in materials:
		matname = mt.name
		mat = mt.attrs["opengl"]
		trefsl = []
		mrefnm = matname + ".material"
		t = nodes.Material(mrefnm)
		t.ambient = tuple(mat.ambient)
		t.diffuse = tuple(mat.diffuse)
		t.emission = tuple(mat.emission)
		t.specular = tuple(mat.specular)
		t.shininess = mat.shininess
		f.add(t)
		trefsl.append(nodes.MRef(mrefnm)) 
		if "maps" in mt.attrs:
			if "normal" in mt.attrs["maps"].maps:
				trefnm = matname + ".normal"
				texfilename_0 = mt.attrs["maps"].maps["normal"].filename
				texfilename = path.relpath(texfilename_0, flname_dirname)
				t = nodes.Texture(trefnm, quote_path(texfilename))
				if "alpha" in mt.attrs["maps"].maps:
					t.format = "rgba"
					texfilename_0 = mt.attrs["maps"].maps["alpha"].filename
					texfilename = path.relpath(texfilename_0, flname_dirname)
					t.alpha_file = quote_path(texfilename)
				else:
					t.format = "rgb"
				t.envtype = "normal_height"
				f.add(t)
				trefsl.append(nodes.TRef(trefnm))
			if "diffuse" in mt.attrs["maps"].maps:
				trefnm = matname + ".diffuse"
				texfilename_0 = mt.attrs["maps"].maps["diffuse"].filename
				texfilename = path.relpath(texfilename_0, flname_dirname)
				t = nodes.Texture(trefnm, quote_path(texfilename))
				t.format = "rgb"
				f.add(t)
				trefsl.append(nodes.TRef(trefnm))
		mt_trefs[matname] = trefsl
		
	pss_idx = 1
	
	for v_f in objs:
		(vertices, faces) = v_f
		
		shapename = "surfaceShp" + str(pss_idx)
		shapename_verts = shapename + ".verts"
		
		g = nodes.Group(shapename)
		vp = nodes.VertexPool(shapename_verts)
		f.add(g)
		
		for vattr in vertices:
			(coord, normal, uv, color) = vattr
			v = nodes.Vertex(coord[0], coord[1], coord[2])
			if uv != None:
				v.uv = nodes.UV(uv[0], uv[1])
			if normal != None:
				v.normal = nodes.Normal(normal[0], normal[1], normal[2])
			vp.add(v)
		g.add(vp)
		
		for vattr in faces:
			vindices = vattr[0]
			matname = vattr[1]
			trefsl_r = []
			for tr_str in mt_trefs[matname]:
				trefsl_r.append(tr_str)
			p = nodes.Polygon(vindices, nodes.Ref(shapename_verts), trefsl_r)
			g.add(p)
		
		pss_idx = pss_idx + 1
	
	fp = open(flname, "w", encoding="utf-8")
	f.write_to(fp)
	fp.close()



###
### Export.
###

def export_fun(attr, filename, content):
	
	objs = content.objs
	
	objs_1 = []
	for obj in objs:
		filename_a = path.splitext(filename)
		filenameext = filename_a[1]
		
		mesh = obj.obj
		vs = mesh.vs
		vc = mesh.vc
		tx = mesh.tx
		ns = mesh.ns
		
		vntc = ( vs, ns, tx, vc )
		(efs, vlist) = panda3d_vlist_for_objs(vntc, [mesh])
		
		vertices = []
		for vattr in vlist:
			vertices.append(vattr)
		faces = []
		for vattr in efs:
			faces.append(vattr)
		objs_1.append((vertices, faces))
		
	write_panda3d_file(filename, objs_1, content.mat)
	
	print("")
	o = OutputList()
	o.add_symbol("ok")
	o.write_list_out(sys.stdout)


def panda3d_vlist_for_objs(vntc, blist):
	omesh = []
	vlist = []
	for m in blist:
		faces = m.fs
		(face_2, vlist_2) = panda3d_vlist_for_face(vntc, faces, vlist)
		for f2 in face_2:
			omesh.append(f2)
	la2 = vlist_2
	return ( omesh, la2 )

def panda3d_vlist_for_face(vntc, faces, vlist):
	oedges = []
	for al in faces:
		edges_v = al.vs
		edges_n = al.ns
		edges_t = al.tx
		edges_c = al.vc
		(al_2, vlist_2) = panda3d_vlist_for_edges_1(vntc, edges_v, edges_n, edges_t, edges_c, vlist)
		
		matname = 'default'
		if len(al.mat) > 0:
			matname = al.mat[0]
		
		vlist = vlist_2
		oedges.append((al_2, matname))
	
	return ( oedges, vlist )

def panda3d_vlist_for_edges_1(vntc, edges_v, edges_n, edges_t, edges_c, vlist):
	oedge = []
	i = 0
	for idx in edges_v:
		( avs, ans, ats, acs ) = vntc
		coord = avs[idx]
		if len(edges_n) <= i:
			normal = None
		else:
			normal = ans[edges_n[i]]
		
		if len(edges_t) <= i:
			uv = None
		else:
			uv = ats[edges_t[i]]
		
		if len(edges_c) <= i:
			color = None
		else:
			color = acs[edges_c[i]]
			
		vert = (coord, normal, uv, color)
		(idx2, vlist_2) = panda3d_vlist_index(vlist, vert)
		
		oedge.append(idx2)
		i = i + 1
	
	return ( oedge, vlist )
	
def list_find(list, nv):
	for idx in range(0, len(list)):
		if list[idx] == nv:
			return idx
	return -1

def panda3d_vlist_index(list, newvert):
	idx = list_find(list, newvert) ## TODO: Might need to implement this myself.
	if idx >= 0:
		return ( idx, list )
	else:
		newidx = len(list)
		list.append(newvert)
		return ( newidx, list )


def exporter():
	filename = extra_params["filename"]
	content = w3d_e3d.E3DFile()
	content.load_from(extra_params["content"])
	export_fun({}, filename, content)

exporter()

