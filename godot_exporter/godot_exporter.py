
##
##  Godot Mesh Library (.tres) Exporter
##
##  Requires Python 3.6 or later for struct.pack features
##
##  Copyright 2023 Edward Blake
##
##  See the file "LICENSE" for information on usage and redistribution
##  of this file, and for a DISCLAIMER OF ALL WARRANTIES.
##

import w3d_e3d
import sys
from os import path

from godot_text import nodes

##
## Write Godot Mesh Library File
## 

def write_godot_file(flname, objs_1, materials):
	f = nodes.GodotFile()
	
	(flname_bname, _) = path.splitext(path.basename(flname))
	flname_dirname = path.dirname(flname)
	
	nd = nodes.NodeGDResourceHeader("MeshLibrary")
	f.add(nd)
	
	mt_rf = {}
	i = 1
	for mt in materials:
		mat_flname = flname_bname + "__m__" + mt.name + ".tres"
		write_material_file(path.join(flname_dirname, mat_flname), mt.name, mt, flname_dirname)
		nd = nodes.NodeExtResource(i)
		nd.path = "res://" + mat_flname
		nd.type = "Material"
		f.add(nd)
		mt_rf[mt.name] = i
		i = i + 1
	
	for ob1 in objs_1:
		(objname, mgroup) = ob1
		
		nd = nodes.NodeArrayMeshSubResource(1)
		nd.resource_name = objname + "test"
		
		## Split object into surfaces based on material
		for gm in mgroup:
			(matname, vertices, faces) = gm
			va = nodes.VertexArray()
			for v in vertices:
				(coord, normal, uv, color) = v
				va.add(
					(coord[0], coord[1], coord[2]),
					(normal[0], normal[1], normal[2]), None)
			ia = nodes.VertexIndexArray()
			for vindices in faces:
				vindices1 = vindices.copy()
				vindices1.reverse()
				for vidx in vindices1:
					ia.add(vidx)
			sr = nodes.Surface(va, ia)
			sr.material = nodes.ExtResource(mt_rf[matname])
			nd.add_surface(sr)
		f.add(nd)

		nd = nodes.NodeResource()
		ndi = nodes.NodeResourceMeshItem(objname)
		ndi.mesh = nodes.SubResource(1)
		nd.add(ndi)
		f.add(nd)
	
	fo = open(flname, "w", encoding="utf-8")
	f.write_to(fo)
	fo.close()

def write_material_file(matflname, matname, mat, flname_dirname):
	f = nodes.GodotFile()
	
	nd = nodes.NodeGDResourceHeader("SpatialMaterial")
	f.add(nd)
	
	tx_id = 1
	albedo_texref = None
	if "maps" in mat.attrs:
		if "diffuse" in mat.attrs["maps"].maps:
			mt = mat.attrs["maps"].maps["diffuse"]
			texfilename = path.relpath(mt.filename, flname_dirname)
			nd = nodes.NodeExtResource(1)
			nd.path = "res://" + texfilename
			nd.type = "Texture"
			albedo_texref = tx_id
			f.add(nd)
			tx_id = tx_id + 1
	
	col = mat.attrs["opengl"].diffuse
	col_r = col[0]
	col_g = col[1]
	col_b = col[2]
	col_a = col[3]
	
	nd = nodes.NodeResource()
	ndi = nodes.NodeResourceMaterialAlbedo(nodes.BasicColor(col_r,col_g,col_b,col_a))
	ndi.albedo_texture = albedo_texref
	nd.add(ndi)
	f.add(nd)
	
	fo = open(matflname, "w", encoding="utf-8")
	f.write_to(fo)
	fo.close()



###
### Export.
###

def export_fun(attr, filename, content):
	
	objs = content.objs
	
	i = 0
	index_of_mat = {}
	for mt in content.mat:
		index_of_mat[mt.name] = i
		i = i + 1
	
	objs_1 = []
	ia = 0
	for obj in objs:
		ia = ia + 1
		objname = 'Obj' + str(ia)
		if obj.name != None:
			objname = obj.name
		
		mgroup = []
		filename_a = path.splitext(filename)
		filenameext = filename_a[1]
		## filenameprefix = path.rootname(filename, filenameext)
		mesh = obj.obj
		vs = mesh.vs
		vc = mesh.vc
		tx = mesh.tx
		ns = mesh.ns
		vntc = ( vs, ns, tx, vc )
		
		mgr = godot_vlist_for_objs(vntc, [mesh])
		for gm in mgr:
			(matname, efs, vlist) = gm
			vertices = []
			for v in vlist:
				(coord, normal, uv, color) = v
				vertices.append((coord, normal, uv, color))
			faces = []
			for x in efs:
				faces.append(x)
			mgroup.append((matname, vertices, faces))
		objs_1.append((objname, mgroup))
	write_godot_file(filename, objs_1, content.mat)
	
	print("")
	o = OutputList()
	o.add_symbol("ok")
	o.write_list_out(sys.stdout)


def godot_vlist_for_objs(vntc, blist):
	mdict = {}
	omesh = []
	for m in blist:
		faces = m.fs
		mdict = godot_vlist_for_face(vntc, faces, mdict)
	mgroup = []
	for mname,val in mdict.items():
		efs = val[0]
		vlist = val[1]
		mgroup.append((mname, efs, vlist))
	return mgroup

def godot_vlist_for_face(vntc, faces, mdict):
	for al in faces:
		edges_v = al.vs
		edges_n = al.ns
		edges_t = al.tx
		edges_c = al.vc
		
		if len(al.mat) == 0:
			mat = 'mat'
		else:
			mat = al.mat[0]
		
		if not mat in mdict:
			mdict[mat] = [[], []]
		
		(al_2, vlist_2) = godot_vlist_for_edges_1(vntc, edges_v, edges_n, edges_t, edges_c, mdict[mat][1])
		
		mdict[mat][1] = vlist_2
		mdict[mat][0].append(al_2)
	
	return mdict

def godot_vlist_for_edges_1(vntc, edges_v, edges_n, edges_t, edges_c, vlist):
	oedge = []
	i = 0
	for idx in edges_v:
		( avs, ans, ats, acs ) = vntc
		coord = avs[idx]
		if len(edges_n) <= i:
			normal = (0.0, 0.0, 0.0)
		else:
			normal = ans[edges_n[i]]
	
		if len(edges_t) <= i:
			uv = (0.0, 0.0)
		else:
			uv = ats[edges_t[i]]
		
		if len(edges_c) <= i:
			color = (0.7, 0.7, 0.7)
		else:
			color = acs[edges_c[i]]
		
		vert = (coord, normal, uv, color)
		(idx2, vlist_2) = godot_vlist_index(vlist, vert)
		
		oedge.append(idx2)
		i = i + 1
	
	return ( oedge, vlist )
	
def list_find(list, nv):
	for idx in range(0, len(list)):
		if list[idx] == nv:
			return idx
	return -1

def godot_vlist_index(list, newvert):
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
