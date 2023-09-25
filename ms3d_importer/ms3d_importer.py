
##
##  Milkshape3D file import
##
##  Copyright 2023 Edward Blake
##
##  See the file "LICENSE" for information on usage and redistribution
##  of this file, and for a DISCLAIMER OF ALL WARRANTIES.
##

import w3d_e3d
import sys
from os import path

from ms3d import ms3d_import
from ms3d.ms3d_cls import MS3DFile, MS3DMaterial, Mesh, MeshHelper
from ms3d.ms3d_edges import first_common, alledges


###
### Import.
###

def import_fun(attr, filename):
	filename_dirname = path.dirname(filename)
	
	ms3df = ms3d_import.read_ms3d_file(filename)
	msh = MeshHelper()
	msh.get(ms3df)
	
	objdict = {}
	for m in msh.meshes:
		meshname = m.meshname
		if (meshname == None) or (meshname == ''):
			meshname = 'None'
		
		matname = 'default'
		if len(ms3df.materials) > m.materialindex:
			matname = ms3df.materials[m.materialindex].name
		
		meshidx = first_common(m, msh.meshes)
		
		if not meshidx in objdict:
			mesh = w3d_e3d.E3DMesh()
			mesh.type="polygon"
			mesh.fs = []
			mesh.ns = []
			mesh.vs = []
			mesh.tx = []
			objdict[meshidx] = [mesh, meshname]
		
		vsoffset = len(objdict[meshidx][0].vs)
		nsoffset = len(objdict[meshidx][0].ns)
		
		for v in m.vertices:
			(flags, v_x,v_y,v_z, uv_u,uv_v, bindex) = v
			objdict[meshidx][0].vs.append((v_x,v_y,v_z))
			objdict[meshidx][0].tx.append((uv_u,uv_v))
		
		for n in m.normals:
			(n_x,n_y,n_z) = n
			objdict[meshidx][0].ns.append((n_x,n_y,n_z))
		
		for t in m.trianglefaces:
			(flags,v1,v2,v3,n1,n2,n3,sg) = t
			face = w3d_e3d.E3DFace()
			face.vs = [v1+vsoffset,v2+vsoffset,v3+vsoffset]
			face.tx = [v1+vsoffset,v2+vsoffset,v3+vsoffset]
			face.ns = [n1+nsoffset,n2+nsoffset,n3+nsoffset]
			face.mat = [matname]
			objdict[meshidx][0].fs.append(face)
	
	objs = []
	for _,name_and_mesh in objdict.items():
		mesh = name_and_mesh[0]
		mesh.vc = []
		mesh.he = alledges(mesh.fs)
		meshname = name_and_mesh[1]
		obj = w3d_e3d.E3DObject()
		obj.name = meshname
		obj.obj = mesh
		objs.append(obj)
		
	mats = []
	for mat in ms3df.materials:
		nmat = w3d_e3d.Material()
		nmat.name = mat.name
		nmatogl = w3d_e3d.MaterialOpenGLAttributes()
		nmatogl.ambient = list(mat.ambient)
		nmatogl.specular = list(mat.specular)
		nmatogl.shininess = mat.shininess
		nmatogl.diffuse = list(mat.diffuse)
		nmatogl.emission = list(mat.emissive)
		nmat.attrs["opengl"] = nmatogl
		if mat.imagemap != '':
			nmatm = w3d_e3d.MaterialMaps()
			img = w3d_e3d.E3DImage()
			img.filename = path.join(filename_dirname, mat.imagemap)
			nmatm.maps["diffuse"] = img
			nmat.attrs["maps"] = nmatm
			
		mats.append(nmat)
	
	print("")
	e3df = w3d_e3d.E3DFile()
	e3df.objs = objs
	e3df.mat = mats
	o_ok = OutputList()
	o_ok.add_symbol("ok")
	o_ok.add_list(e3df.as_output_list())
	o_ok.write_list_out(sys.stdout)

def importer(params, params_by_key, extra_params):
	filename = extra_params["filename"]
	import_fun({}, filename)

w3d_main_function = importer

