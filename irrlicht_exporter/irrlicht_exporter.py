
##
##  Irrlicht Mesh Exporter
##
##  Copyright 2023 Edward Blake
##
##  See the file "LICENSE" for information on usage and redistribution
##  of this file, and for a DISCLAIMER OF ALL WARRANTIES.
##

import w3d_e3d
import sys
from os import path
from xml.dom.minidom import getDOMImplementation


##
## Write Irrmesh File
## 

def export_fun(attr, filename, content):
	
	objs = content.objs
	
	matdict = {}
	for mt in content.mat:
		matdict[mt.name] = mt
		
	filename_dirname = path.dirname(filename)
	
	buffers = []
	for obj in objs:
		filename_a = path.splitext(filename)
		filenameext = filename_a[1]
		
		mesh = obj.obj
		vs = mesh.vs
		vc = mesh.vc
		tx = mesh.tx
		ns = mesh.ns
		vntc = ( vs, ns, tx, vc )
		mgr = irr_vlist_for_objs(vntc, [mesh])
		for gm in mgr:
			(matname, efs, vlist) = gm
			
			vertices = []
			for v in vlist:
				(coord, normal, uv, color) = v
				vertices.append((
					coord[0], coord[1], coord[2],
					normal[0], normal[1], normal[2],
					(color[0], color[1], color[2]),
					uv[0], uv[1]))
			faces = []
			for x in efs:
				for i in x:
					faces.append(i)
			
			mat = matdict[matname]
			mato = mat.attrs["opengl"]
			m={}
			m["Type"] = "solid"
			m["Ambient"] = tuple(mato.ambient)
			m["Diffuse"] = tuple(mato.diffuse)
			m["Emissive"] = tuple(mato.emission)
			m["Specular"] = tuple(mato.specular)
			m["Shininess"] = mato.shininess
			m["Param1"] = 0.000000
			m["Param2"] = 0.000000
			m["Texture1"] = ""
			if "maps" in mat.attrs:
				matm = mat.attrs["maps"]
				if "diffuse" in matm.maps:
					texfilename = matm.maps["diffuse"].filename
					m["Texture1"] = path.relpath(texfilename, filename_dirname)
			m["Texture2"] = ""
			m["Texture3"] = ""
			m["Texture4"] = ""
			m["Wireframe"] = False
			m["GouraudShading"] = True
			m["Lighting"] = False
			m["ZWriteEnable"] = True
			m["ZBuffer"] = 1
			m["BackfaceCulling"] = True
			m["FrontfaceCulling"] = False
			m["FogEnable"] = False
			m["NormalizeNormals"] = False
			m["BilinearFilter1"] = True
			m["BilinearFilter2"] = True
			m["BilinearFilter3"] = True
			m["BilinearFilter4"] = True
			m["TrilinearFilter1"] = False
			m["TrilinearFilter2"] = False
			m["TrilinearFilter3"] = False
			m["TrilinearFilter4"] = False
			m["AnisotropicFilter1"] = False
			m["AnisotropicFilter2"] = False
			m["AnisotropicFilter3"] = False
			m["AnisotropicFilter4"] = False
			m["TextureWrap1"] = "texture_clamp_repeat"
			m["TextureWrap2"] = "texture_clamp_repeat"
			m["TextureWrap3"] = "texture_clamp_repeat"
			m["TextureWrap4"] = "texture_clamp_repeat"
			buffers.append((m, vertices, faces))
	write_irr_file(filename, buffers)
	
	print("")
	o = OutputList()
	o.add_symbol("ok")
	o.write_list_out(sys.stdout)


def write_irr_file(flname, buffers):
	g_minedge_x = 0.0
	g_minedge_y = 0.0
	g_minedge_z = 0.0
	g_maxedge_x = 0.0
	g_maxedge_y = 0.0
	g_maxedge_z = 0.0
	impl = getDOMImplementation()

	newdoc = impl.createDocument(None, "mesh", None)
	top_element = newdoc.documentElement
	top_element.setAttribute("xmlns", "http://irrlicht.sourceforge.net/IRRMESH_09_2007")
	top_element.setAttribute("version", "1.0")
	mesh_e = top_element
	
	comment = newdoc.createComment(' This file contains a static mesh in the Irrlicht Engine format with ' + str(len(buffers)) + ' materials.')
	mesh_e.appendChild(comment)
	
	bb1_e = newdoc.createElement('boundingBox')
	mesh_e.appendChild(bb1_e)
	
	for buf in buffers:
		b_minedge_x = 0.0
		b_minedge_y = 0.0
		b_minedge_z = 0.0
		b_maxedge_x = 0.0
		b_maxedge_y = 0.0
		b_maxedge_z = 0.0
		(m, vertices, faces) = buf

		bb1_b_e = newdoc.createElement('buffer')
		mesh_e.appendChild(bb1_b_e)
		
		bb2_e = newdoc.createElement('boundingBox')
		bb1_b_e.appendChild(bb2_e)
		
		bb2_m_e = newdoc.createElement('material')
		bb1_b_e.appendChild(bb2_m_e)
		
		add_enum(newdoc, bb2_m_e, "Type", m["Type"])
		add_color(newdoc, bb2_m_e, "Ambient", m["Ambient"])
		add_color(newdoc, bb2_m_e, "Diffuse", m["Diffuse"])
		add_color(newdoc, bb2_m_e, "Emissive", m["Emissive"])
		add_color(newdoc, bb2_m_e, "Specular", m["Specular"])
		add_float(newdoc, bb2_m_e, "Shininess", m["Shininess"])
		add_float(newdoc, bb2_m_e, "Param1", m["Param1"])
		add_float(newdoc, bb2_m_e, "Param2", m["Param2"])
		add_texture(newdoc, bb2_m_e, "Texture1", m["Texture1"])
		add_texture(newdoc, bb2_m_e, "Texture2", m["Texture2"])
		add_texture(newdoc, bb2_m_e, "Texture3", m["Texture3"])
		add_texture(newdoc, bb2_m_e, "Texture4", m["Texture4"])
		add_bool(newdoc, bb2_m_e, "Wireframe", m["Wireframe"])
		add_bool(newdoc, bb2_m_e, "GouraudShading", m["GouraudShading"])
		add_bool(newdoc, bb2_m_e, "Lighting", m["Lighting"])
		add_bool(newdoc, bb2_m_e, "ZWriteEnable", m["ZWriteEnable"])
		add_int(newdoc, bb2_m_e, "ZBuffer", m["ZBuffer"])
		add_bool(newdoc, bb2_m_e, "BackfaceCulling", m["BackfaceCulling"])
		add_bool(newdoc, bb2_m_e, "FrontfaceCulling", m["FrontfaceCulling"])
		add_bool(newdoc, bb2_m_e, "FogEnable", m["FogEnable"])
		add_bool(newdoc, bb2_m_e, "NormalizeNormals", m["NormalizeNormals"])
		add_bool(newdoc, bb2_m_e, "BilinearFilter1", m["BilinearFilter1"])
		add_bool(newdoc, bb2_m_e, "BilinearFilter2", m["BilinearFilter2"])
		add_bool(newdoc, bb2_m_e, "BilinearFilter3", m["BilinearFilter3"])
		add_bool(newdoc, bb2_m_e, "BilinearFilter4", m["BilinearFilter4"])
		add_bool(newdoc, bb2_m_e, "TrilinearFilter1", m["TrilinearFilter1"])
		add_bool(newdoc, bb2_m_e, "TrilinearFilter2", m["TrilinearFilter2"])
		add_bool(newdoc, bb2_m_e, "TrilinearFilter3", m["TrilinearFilter3"])
		add_bool(newdoc, bb2_m_e, "TrilinearFilter4", m["TrilinearFilter4"])
		add_bool(newdoc, bb2_m_e, "AnisotropicFilter1", m["AnisotropicFilter1"])
		add_bool(newdoc, bb2_m_e, "AnisotropicFilter2", m["AnisotropicFilter2"])
		add_bool(newdoc, bb2_m_e, "AnisotropicFilter3", m["AnisotropicFilter3"])
		add_bool(newdoc, bb2_m_e, "AnisotropicFilter4", m["AnisotropicFilter4"])
		add_enum(newdoc, bb2_m_e, "TextureWrap1", m["TextureWrap1"])
		add_enum(newdoc, bb2_m_e, "TextureWrap2", m["TextureWrap2"])
		add_enum(newdoc, bb2_m_e, "TextureWrap3", m["TextureWrap3"])
		add_enum(newdoc, bb2_m_e, "TextureWrap4", m["TextureWrap4"])
		
		vertices_e = newdoc.createElement('vertices')
		vertices_e.setAttribute("type", "standard")
		vertices_e.setAttribute("vertexCount", "%d" % len(vertices))
		vertices_b = []
		for vert in vertices:
			(x, y, z, nrm_x, nrm_y, nrm_z, color, u, v) = vert
			color_s = color_to_hex(color)
			line = ""
			line += float_str(x) + " " + float_str(y) + " " + float_str(z) + " "
			line += float_str(nrm_x) + " " + float_str(nrm_y) + " " + float_str(nrm_z) + " "
			line += color_s + " "
			line += float_str(u) + " " + float_str(v)
			vertices_b.append(line)
			
			if b_minedge_x > x:
				b_minedge_x = x
			if b_minedge_y > y:
				b_minedge_y = y
			if b_minedge_z > z:
				b_minedge_z = z
			if b_maxedge_x < x:
				b_maxedge_x = x
			if b_maxedge_y < y:
				b_maxedge_y = y
			if b_maxedge_z < z:
				b_maxedge_z = z
		
		vertices_b_t = newdoc.createTextNode("\n".join(vertices_b))
		vertices_e.appendChild(vertices_b_t)
		bb1_b_e.appendChild(vertices_e)
		
		indices_e = newdoc.createElement('indices')
		indices_e.setAttribute("indexCount", "%d" % len(faces))
		indices_b = []
		for idx in faces:
			indices_b.append(str(idx))
		indices_b_t = newdoc.createTextNode(" ".join(indices_b))
		indices_e.appendChild(indices_b_t)
		bb1_b_e.appendChild(indices_e)
		
		if g_minedge_x > b_minedge_x:
			g_minedge_x = b_minedge_x
		if g_minedge_y > b_minedge_y:
			g_minedge_y = b_minedge_y
		if g_minedge_z > b_minedge_z:
			g_minedge_z = b_minedge_z
		if g_maxedge_x < b_maxedge_x:
			g_maxedge_x = b_maxedge_x
		if g_maxedge_y < b_maxedge_y:
			g_maxedge_y = b_maxedge_y
		if g_maxedge_z < b_maxedge_z:
			g_maxedge_z = b_maxedge_z
		
		bb2_e.setAttribute('minEdge', float_str(b_minedge_x) + " " + float_str(b_minedge_y) + " " + float_str(b_minedge_z))
		bb2_e.setAttribute('maxEdge', float_str(b_maxedge_x) + " " + float_str(b_maxedge_y) + " " + float_str(b_maxedge_z))
		
	bb1_e.setAttribute('minEdge', float_str(g_minedge_x) + " " + float_str(g_minedge_y) + " " + float_str(g_minedge_z))
	bb1_e.setAttribute('maxEdge', float_str(g_maxedge_x) + " " + float_str(g_maxedge_y) + " " + float_str(g_maxedge_z))
		
	f2 = open(flname, "w", encoding="utf-8")
	newdoc.writexml(f2, '', ' ', "\n")
	f2.close()


###
### Export.
###

def irr_vlist_for_objs(vntc, blist):
	mdict = {}
	omesh = []
	for m in blist:
		faces = m.fs
		mdict = irr_vlist_for_face(vntc, faces, mdict)
	mgroup = []
	for mname,val in mdict.items():
		efs = val[0]
		vlist = val[1]
		mgroup.append((mname, efs, vlist))
	return mgroup

def irr_vlist_for_face(vntc, faces, mdict):
	for al in faces:
		edges_v = al.vs
		edges_n = al.ns
		edges_t = al.tx
		edges_c = al.vc
		
		if len(al.mat) == 0:
			mat = 'default'
		else:
			mat = al.mat[0]
		
		if not mat in mdict:
			mdict[mat] = [[], []]
		
		(al_2, vlist_2) = irr_vlist_for_edges_1(vntc, edges_v, edges_n, edges_t, edges_c, mdict[mat][1])
		
		mdict[mat][1] = vlist_2
		mdict[mat][0].append(al_2)
	
	return mdict

def irr_vlist_for_edges_1(vntc, edges_v, edges_n, edges_t, edges_c, vlist):
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
			color = (0.7, 0.7, 0.7, 1.0)
		else:
			color = acs[edges_c[i]]
		
		vert = (coord, normal, uv, color)
		(idx2, vlist_2) = irr_vlist_index(vlist, vert)
		
		oedge.append(idx2)
		i = i + 1
	
	return ( oedge, vlist )
	
def list_find(list, nv):
	for idx in range(0, len(list)):
		if list[idx] == nv:
			return idx
	return -1

def irr_vlist_index(list, newvert):
	idx = list_find(list, newvert) ## TODO: Might need to implement this myself.
	if idx >= 0:
		return ( idx, list )
	else:
		newidx = len(list)
		list.append(newvert)
		return ( newidx, list )
	

def add_enum(newdoc, e, enum_name, enum_val):
	enum_e = newdoc.createElement('enum')
	enum_e.setAttribute('name', enum_name)
	enum_e.setAttribute('value', enum_val)
	e.appendChild(enum_e)

def hex2d(a):
	return "%02x" % a

def color_to_hex(color_val):
	r = int(color_val[0] * 255.0)
	g = int(color_val[1] * 255.0)
	b = int(color_val[2] * 255.0)
	if len(color_val) == 3:
		a = 255
	else:
		a = int(color_val[3] * 255.0)
	val = "" + hex2d(a) + hex2d(b) + hex2d(g) + hex2d(r)
	return val
	
def add_color(newdoc, e, color_name, color_val):
	val = color_to_hex(color_val)
	color_e = newdoc.createElement('color')
	color_e.setAttribute("name", color_name)
	color_e.setAttribute("value", val)
	e.appendChild(color_e)

def add_float(newdoc, e, float_name, float_val):
	float_e = newdoc.createElement('float')
	float_e.setAttribute("name", float_name)
	float_e.setAttribute("value", float_str(float_val))
	e.appendChild(float_e)

def add_texture(newdoc, e, tex_name, texture_val):
	tex_e = newdoc.createElement('texture')
	tex_e.setAttribute("name", tex_name)
	tex_e.setAttribute("value", texture_val)
	e.appendChild(tex_e)
	
def add_bool(newdoc, e, bool_name, bool_val):
	b = bool(bool_val)
	bool_e = newdoc.createElement('bool')
	bool_e.setAttribute("name", bool_name)
	bool_e.setAttribute("value", str(b).lower())
	e.appendChild(bool_e)

def add_int(newdoc, e, float_name, int_val):
	int_e = newdoc.createElement('int')
	int_e.setAttribute("name", float_name)
	int_e.setAttribute("value", str(int_val))
	e.appendChild(int_e)

def float_str(f):
	return "%.06f" % f


def exporter():
	filename = extra_params["filename"]
	content = w3d_e3d.E3DFile()
	content.load_from(extra_params["content"])
	export_fun({}, filename, content)

exporter()

