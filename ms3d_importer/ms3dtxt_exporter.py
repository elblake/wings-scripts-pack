
##
##  MilkShape3D Exporter
##
##  Copyright 2023 Edward Blake
##
##  See the file "LICENSE" for information on usage and redistribution
##  of this file, and for a DISCLAIMER OF ALL WARRANTIES.
##

import w3d_e3d
import sys
from os import path

from ms3d import ms3d_export
from ms3d.ms3d_cls import MS3DFile, MS3DMaterial, Mesh, MeshHelper


###
### Export.
###

def export_fun(attr, filename, content):
	
	objs = content.objs
	
	filename_dirname = path.dirname(filename)
	
	i = 0
	index_of_mat = {}
	for mt in content.mat:
		index_of_mat[mt.name] = i
		i = i + 1
	
	ms3df = MS3DFile()
	msh = MeshHelper()
	
	for obj in objs:
		objname = 'None'
		if obj.name != None:
			objname = obj.name
		
		mdict = {}
		mdict_nv = {}
		mesh = obj.obj
		
		for face in mesh.fs: # Face table (list of e3d_face).
			if len(face.mat) == 0:
				mat = 'default'
			else:
				mat = face.mat[0]
			if not mat in mdict:
				mdict[mat] = Mesh()
				mdict[mat].meshname = objname + "_" + mat
				mdict[mat].materialindex = index_of_mat[mat]
				for coord in mesh.ns: # Normal table
					mdict[mat].normals.append(coord)
				mdict_nv[mat] = {}
			vv = []
			for i in range(0, 3):
				(v_x,v_y,v_z) = mesh.vs[face.vs[i]]
				if len(face.tx) > i:
					(u,v) = mesh.tx[face.tx[i]]
				else:
					u = 0.0
					v = 0.0
				if ((v_x,v_y,v_z), (u,v)) in mdict_nv[mat]:
					vv.append(mdict_nv[mat][((v_x,v_y,v_z), (u,v))])
				else:
					vv0 = len(mdict[mat].vertices)
					mdict_nv[mat][((v_x,v_y,v_z), (u,v))] = vv0
					vv.append(vv0)
					flags = 0
					bindex = -1
					mdict[mat].vertices.append((flags, v_x,v_y,v_z, u,v, bindex))
			
			[v1,v2,v3] = vv
			[n1,n2,n3] = face.ns
			#face.mat
			flags = 0
			sg = face.sg
			mdict[mat].trianglefaces.append((flags,v1,v2,v3,n1,n2,n3,sg))
		
		for mnm, m in mdict.items():
			msh.meshes.append(m)
	
	ms3df.materials = []
	for mt in content.mat:
		mto = mt.attrs["opengl"]
		nmat = MS3DMaterial()
		nmat.name = mt.name
		nmat.ambient = tuple(mto.ambient)
		nmat.diffuse = tuple(mto.diffuse)
		nmat.specular = tuple(mto.specular)
		nmat.emissive = tuple(mto.emission)
		nmat.shininess = mto.shininess
		nmat.transparency = 1.0
		if "maps" in mt.attrs:
			if "diffuse" in mt.attrs["maps"].maps:
				texfilename = mt.attrs["maps"].maps["diffuse"].filename
				nmat.imagemap = path.relpath(texfilename, filename_dirname)
			if "alpha" in mt.attrs["maps"].maps:
				texfilename = mt.attrs["maps"].maps["alpha"].filename
				nmat.alphamap = path.relpath(texfilename, filename_dirname)
		ms3df.materials.append(nmat)
	
	msh.set(ms3df)
	ms3df.update_ref_counts()
	
	ms3d_export.write_ms3d_file(filename, ms3df)
	
	print("")
	o = OutputList()
	o.add_symbol("ok")
	o.write_list_out(sys.stdout)


def exporter(params, params_by_key, extra_params):
	filename = extra_params["filename"]
	content = w3d_e3d.E3DFile()
	content.load_from(extra_params["content"])
	export_fun({}, filename, content)

w3d_main_function = exporter

