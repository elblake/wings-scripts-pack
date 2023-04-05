
##
##  Write Milkshape 3D Files
##
##  Copyright 2023 Edward Blake
##
##  See the file "LICENSE" for information on usage and redistribution
##  of this file, and for a DISCLAIMER OF ALL WARRANTIES.
##

import struct
from ms3d.ms3d_cls import MS3DFileComments, MS3DFile, MS3DVertex, MS3DTriangle, MS3DGroup, MS3DMaterial, MS3DJoint, MS3DVertex_ex, MS3DJoint_ex, MS3DModel_ex, Mesh, MeshHelper

##
## max values
##
WRITER_MAX_VERTICES = 65534
WRITER_MAX_TRIANGLES = 65534
WRITER_MAX_GROUPS = 255
WRITER_MAX_MATERIALS = 128
WRITER_MAX_JOINTS = 128

##
## flags
##
WRITER_SELECTED = 1
WRITER_HIDDEN = 2
WRITER_SELECTED2 = 4
WRITER_DIRTY = 8

def file_write_str(fp, size, dstr):
	data = dstr.encode('ascii')
	while len(data) < size:
		data = data + b'\0'
	fp.write(data)
def file_write_u8(fp, val):
	bt = struct.pack('B', val)
	fp.write(bt)
def file_write_s8(fp, val):
	bt = struct.pack('b', val)
	fp.write(bt)
def file_write_u16(fp, val):
	bt = struct.pack('H', val)
	fp.write(bt)
def file_write_u32(fp, val):
	## 4 bytes
	bt = struct.pack('I', val)
	fp.write(bt)
def file_write_float(fp, val):
	## 4 bytes
	bt = struct.pack('f', val)
	fp.write(bt)
	

def write_ms3d_file(flname, ms3df):
	if flname[-4:].lower() == '.txt':
		write_ms3d_txt_file(flname, ms3df)
	else:
		write_ms3d_bin_file(flname, ms3df)
	

##
## Write Milkshape MS3D (.ms3d) files
##

def write_ms3d_bin_file(flname, ms3df):
	fp = open(flname, "wb")
	
	vertices = ms3df.vertices
	triangles = ms3df.triangles
	groups = ms3df.groups
	materials = ms3df.materials
	anim = ms3df.anim
	joints = ms3df.joints
	comments = ms3df.comments
	extra = ms3df.extra
	ms3d_header_t(fp)
	
	file_write_u16(fp, len(vertices)) ## number of vertices, 2 bytes
	for v in vertices:
		ms3d_vertex_t(fp, v)
	
	file_write_u16(fp, len(triangles)) ## number of triangles, 2 bytes
	for tri in triangles:
		ms3d_triangle_t(fp, tri)
	
	file_write_u16(fp, len(groups)) ## number of groups, 2 bytes
	for g in groups:
		ms3d_group_t(fp, g)
	
	file_write_u16(fp, len(materials)) ## number of materials, 2 bytes
	for m in materials:
		ms3d_material_t(fp, m)
	
	## keyframer data
	(animation_fps, current_time,total_frames) = anim
	file_write_float(fp, animation_fps)  ## 4 bytes
	file_write_float(fp, current_time) ## 4 bytes
	file_write_u32(fp, total_frames) ## 4 bytes
	
	file_write_u16(fp, len(joints)) ## number of joints, 2 bytes
	for j in joints:
		ms3d_joint_t(fp, j)
	
	sub_version = 1
	file_write_u32(fp, sub_version) ## subVersion is = 1, 4 bytes
	
	if comments != None:
		group_comments = comments.group_comments
		material_comments = comments.material_comments
		joint_comments = comments.joint_comments
		model_comment = comments.model_comment
	else:
		group_comments = []
		material_comments = []
		joint_comments = []
		model_comment = []
		
	
	file_write_u32(fp, len(group_comments)) ## 4 bytes
	for c in group_comments:
		ms3d_comment_t(fp, c)
	file_write_u32(fp, len(material_comments)) ## 4 bytes
	for c in material_comments:
		ms3d_comment_t(fp, c)
	file_write_u32(fp, len(joint_comments)) ## 4 bytes
	for c in joint_comments:
		ms3d_comment_t(fp, c)
	file_write_u32(fp, len(model_comment)) ## 4 bytes
	for c in model_comment:
		ms3d_comment_t(fp, c)
	
	if extra != None:
		(ex_vs, ex_jn, ex_md) = extra
		## vertex extra information
		sub_version = 2
		file_write_u32(fp, sub_version)        ## subVersion is = 3, 4 bytes
		i = 0
		for v0 in vertices:
			if i >= len(ex_vs):
				v = None
			else:
				v = ex_vs[i]
			ms3d_vertex_ex_t(fp, sub_version, v)
			i = i + 1
		
		## joint extra information
		sub_version = 1
		file_write_u32(fp, sub_version)        ## subVersion is = 1, 4 bytes
		i = 0
		for j0 in joints:
			if i >= len(ex_jn):
				j = None
			else:
				j = ex_jn[i]
			ms3d_joint_ex_t(fp, sub_version, j)
			i = i + 1
		
		## model extra information
		sub_version = 1
		file_write_u32(fp, sub_version)        ## subVersion is = 1, 4 bytes
		ms3d_model_ex_t(fp, sub_version, ex_md)
		



## MS3D header
def ms3d_header_t(fp):
	fp.write(b'MS3D000000')
	version = 4
	file_write_u32(fp, version)

## vertex
def ms3d_vertex_t(fp, v):
	flags = v.flags
	v_x = v.v_x
	v_y = v.v_y
	v_z = v.v_z
	bone_id = v.bone_id
	ref_count = v.ref_count
	
	file_write_u8(fp, flags)
	file_write_float(fp, v_x)
	file_write_float(fp, v_y)
	file_write_float(fp, v_z)

	file_write_s8(fp, bone_id)    ## -1 = no bone
	file_write_u8(fp, ref_count)
	

##
## Triangles
def ms3d_triangle_t(fp, tri):
	flags = tri.flags
	v_1 = tri.v_1
	v_2 = tri.v_2
	v_3 = tri.v_3
	vn1 = tri.vn1
	vn2 = tri.vn2
	vn3 = tri.vn3
	uv1 = tri.uv1
	uv2 = tri.uv2
	uv3 = tri.uv3
	sg = tri.sg
	g_idx = tri.g_idx
	
	file_write_u16(fp, flags)
	file_write_u16(fp, v_1)
	file_write_u16(fp, v_2)
	file_write_u16(fp, v_3)
	
	(vns_1x, vns_1y, vns_1z) = vn1
	file_write_float(fp, vns_1x)
	file_write_float(fp, vns_1y)
	file_write_float(fp, vns_1z)
	(vns_2x, vns_2y, vns_2z) = vn2
	file_write_float(fp, vns_2x)
	file_write_float(fp, vns_2y)
	file_write_float(fp, vns_2z)
	(vns_3x, vns_3y, vns_3z) = vn3
	file_write_float(fp, vns_3x)
	file_write_float(fp, vns_3y)
	file_write_float(fp, vns_3z)

	(u1,v1) = uv1
	(u2,v2) = uv2
	(u3,v3) = uv3
	file_write_float(fp, u1)
	file_write_float(fp, u2)
	file_write_float(fp, u3)

	file_write_float(fp, v1)
	file_write_float(fp, v2)
	file_write_float(fp, v3)

	file_write_u8(fp, sg)         ## 1 - 32
	file_write_u8(fp, g_idx)
	

##
## Groups
##
def ms3d_group_t(fp, g):
	flags = g.flags
	name = g.name
	triangles = g.triangles
	mat_index = g.mat_index
	if name == None:
		name = 'none'
	
	file_write_u8(fp, flags)
	file_write_str(fp, 32, name)
	file_write_u16(fp, len(triangles))
	for tri_idx in triangles:
		file_write_u16(fp, tri_idx)
	file_write_s8(fp, mat_index)         ## -1 = no material
	

##
## Materials
##
def ms3d_material_t(fp, mat):
	name = mat.name
	ambient = mat.ambient
	diffuse = mat.diffuse
	specular = mat.specular
	emissive = mat.emissive
	shininess = mat.shininess
	transparency = mat.transparency
	mode = mat.mode
	imagemap = mat.imagemap
	alphamap = mat.alphamap
	
	file_write_str(fp, 32, name)
	(am_r, am_g, am_b, am_a) = ambient
	file_write_float(fp, am_r)
	file_write_float(fp, am_g)
	file_write_float(fp, am_b)
	file_write_float(fp, am_a)
	
	(df_r, df_g, df_b, df_a) = diffuse
	file_write_float(fp, df_r)
	file_write_float(fp, df_g)
	file_write_float(fp, df_b)
	file_write_float(fp, df_a)

	(sp_r, sp_g, sp_b, sp_a) = specular
	file_write_float(fp, sp_r)
	file_write_float(fp, sp_g)
	file_write_float(fp, sp_b)
	file_write_float(fp, sp_a)

	(em_r, em_g, em_b, em_a) = emissive
	file_write_float(fp, em_r)
	file_write_float(fp, em_g)
	file_write_float(fp, em_b)
	file_write_float(fp, em_a)

	file_write_float(fp, shininess)    ## 0.0f - 128.0f
	file_write_float(fp, transparency) ## 0.0f - 1.0f
	file_write_s8(fp, mode)            ## 0, 1, 2 is unused now
	file_write_str(fp, 128, imagemap)  ## Texture file name
	file_write_str(fp, 128, alphamap)  ## Alpha map file name


def ms3d_joint_t(fp, joint):
	flags = joint.flags
	jointname = joint.jointname
	parentname = joint.parentname
	rot = joint.rot
	pos = joint.pos
	key_frames_rot = joint.key_frames_rot
	key_frames_pos = joint.key_frames_pos
	
	file_write_u8(fp, flags)
	file_write_str(fp, 32, jointname)
	file_write_str(fp, 32, parentname)
	
	(rot_x, rot_y, rot_z) = rot
	file_write_float(fp, rotationX)
	file_write_float(fp, rotationY)
	file_write_float(fp, rotationZ)

	(pos_x, pos_y, pos_z) = pos
	file_write_float(fp, positionX)
	file_write_float(fp, positionY)
	file_write_float(fp, positionZ)

	file_write_u16(fp, len(key_frames_rot))
	file_write_u16(fp, len(key_frames_pos))

	for kr in key_frames_rot:
		(time, r_x,r_y,r_z) = kr
		file_write_float(fp, time)
		file_write_float(fp, r_x)
		file_write_float(fp, r_y)
		file_write_float(fp, r_z)
	for kp in key_frames_pos:
		(time, p_x,p_y,p_z) = kp
		file_write_float(fp, time)
		file_write_float(fp, p_x)
		file_write_float(fp, p_y)
		file_write_float(fp, p_z)
	

##
## Group comments
##
def ms3d_comment_t(fp, cm):
	(index, comment) = cm
	commentdat = bytes(comment)
	file_write_u32(fp, index)           ## index of group, material or joint
	file_write_u32(fp, len(commentdat)) ## length of comment
	file_write_str(fp, commentdat)      ## comment
	


def ms3d_vertex_ex_t(fp, sub_version, exv):
	if exv == None:
		bone_id1 = -1
		bone_id2 = -1
		bone_id3 = -1
		weight1 = 0.0
		weight2 = 0.0
		weight3 = 0.0
		extra1 = 0
		extra2 = 0
	else:
		bone_id1 = exv.bone_id1
		bone_id2 = exv.bone_id2
		bone_id3 = exv.bone_id3
		weight1 = exv.weight1
		weight2 = exv.weight2
		weight3 = exv.weight3
		extra1 = exv.extra1
		extra2 = exv.extra2
		
	# for subversion == 1
	file_write_s8(fp, bone_id1)
	file_write_s8(fp, bone_id2)
	file_write_s8(fp, bone_id3) # index of joint or -1
	file_write_u8(fp, int(weight1 * 255))
	file_write_u8(fp, int(weight2 * 255))
	file_write_u8(fp, int(weight3 * 255))
	if sub_version == 1:
		pass
	elif sub_version == 2:
		file_write_u32(fp, extra1) ## vertex extra
			
	elif sub_version == 3:
		file_write_u32(fp, extra1)
		file_write_u32(fp, extra2) ## vertex extra
	

## for subVersion == 1
def ms3d_joint_ex_t(fp, sub_version, exj):
	if exj == None:
		col_r = 0.8
		col_g = 0.8
		col_b = 0.8
	else:
		col_r = exj.col_r
		col_g = exj.col_g
		col_b = exj.col_b
	file_write_float(fp, col_r)
	file_write_float(fp, col_g)
	file_write_float(fp, col_b)	## joint color
	

## for subVersion == 1
def ms3d_model_ex_t(fp, sub_version, ex):
	if ex == None:
		jointsize = 0.0
		transparencymode = 0
		alpharef = 1.0
	else:
		jointsize = ex.jointsize
		transparencymode = ex.transparencymode
		alpharef = ex.alpharef
	file_write_float(fp, jointsize)
	file_write_u32(fp, transparencymode)
	file_write_float(fp, alpharef)


##
## Write Milkshape 3D Text (.txt) files
##

def write_ms3d_txt_file(flname, ms3df):
	mh = MeshHelper()
	mh.get(ms3df)
	meshes = mh.meshes
	materials = ms3df.materials
	
	fp = open(flname, "w", encoding="utf-8")
	
	write_txt_header(fp)
	write_txt_newline(fp)
	write_txt_section(fp, "Frames", 30)  ## total frames
	write_txt_section(fp, "Frame", 1)    ## current frame
	write_txt_newline(fp)
	
	## number of meshes
	write_txt_section(fp, "Meshes", len(meshes))
	for m in meshes:
		write_txt_mesh(fp, m)
	write_txt_newline(fp)
	
	## number of materials
	write_txt_section(fp, "Materials", len(materials))
	for m in materials:
		write_txt_material(fp, m)
	write_txt_newline(fp)
	
	## number of joints
	write_txt_section(fp, "Bones", 0)
	write_txt_section(fp, "GroupComments", 0)
	write_txt_section(fp, "MaterialComments", 0)
	write_txt_section(fp, "BoneComments", 0)
	write_txt_section(fp, "ModelComment", 0)
	
	
def write_txt_mesh(fp, mesh):
	meshname = mesh.meshname
	flags = mesh.meshflags
	materialindex = mesh.materialindex
	vertices = mesh.vertices
	normals = mesh.normals
	trianglefaces = mesh.trianglefaces
	
	
	## Mesh name, flags, material index
	write_txt_line(fp, "sii", [meshname, flags, materialindex])
	
	## Number of vertices
	write_txt_line_number(fp, len(vertices))
	for v in vertices:
		(flags, v_x, v_y, v_z, v_u, v_v, boneindex) = v
		## Vertex flags, x, y, z, u, v, bone index
		write_txt_line(fp, "ifffffi", [flags, v_x, v_y, v_z, v_u, v_v, boneindex])
	
	## Number of normals
	write_txt_line_number(fp, len(normals))
	for n in normals:
		(n_x, n_y, n_z) = n
		## Normal x, y, z
		write_txt_line(fp, "fff", [n_x, n_y, n_z])
	
	## Number of triangles
	write_txt_line_number(fp, len(trianglefaces))
	for tri in trianglefaces:
		(flags, idx1, idx2, idx3, nidx1, nidx2, nidx3, smoothinggroup) = tri
		## Triangle flags, vertex index1, vertex index2, vertex index3, normal index1, normal index 2, normal index 3, smoothing group
		write_txt_line(fp, "iiiiiiii", [flags, idx1, idx2, idx3, nidx1, nidx2, nidx3, smoothinggroup])

	


def write_txt_material(fp, mat):
	materialname = mat.name
	ambient = mat.ambient
	diffuse = mat.diffuse
	specular = mat.specular
	emissive = mat.emissive
	shininess = mat.shininess
	transparency = mat.transparency
	colormap = mat.imagemap
	alphamap = mat.alphamap
	
	## Material name
	write_txt_line(fp, "s", [materialname])
	
	## Ambient
	(am_r, am_g, am_b, am_a) = ambient
	write_txt_line(fp, "ffff", [am_r, am_g, am_b, am_a])

	## Diffuse
	(df_r, df_g, df_b, df_a) = diffuse
	write_txt_line(fp, "ffff", [df_r, df_g, df_b, df_a])

	## Specular
	(sp_r, sp_g, sp_b, sp_a) = specular
	write_txt_line(fp, "ffff", [sp_r, sp_g, sp_b, sp_a])

	## Emissive
	(em_r, em_g, em_b, em_a) = emissive
	write_txt_line(fp, "ffff", [em_r, em_g, em_b, em_a])

	## Shininess
	write_txt_line(fp, "f", [shininess])

	## Transparency
	write_txt_line(fp, "f", [transparency])

	## Texture map
	write_txt_line(fp, "s", [colormap])

	## Alpha map
	write_txt_line(fp, "s", [alphamap])
	

def write_txt_joint(fp, joint):
	jointname = joint.jointname
	jointparentname = joint.parentname
	flags = joint.flags
	(posx, posy, posz) = joint.pos
	(rotx, roty, rotz) = joint.rot
	positionkeys = joint.key_frames_pos
	rotationkeys = joint.key_frames_rot
	
	## Name
	write_txt_line(fp, "s", [jointname])
	## Parent name
	write_txt_line(fp, "s", [jointparentname])
	## Joint flags, posx, posy, posz, rotx, roty, rotz
	write_txt_line(fp, "iffffff", [flags, posx, posy, posz, rotx, roty, rotz])
	
	## Number of position keys
	write_txt_line_number(fp, len(positionkeys))
	for pk in positionkeys:
		(time, posx, posy, posz) = pk
		## Position key time, posx, posy, posz
		write_txt_line(fp, "ffff", [time, posx, posy, posz])
	
	## Number of rotation keys
	write_txt_line_number(fp, len(rotationkeys))
	for rk in rotationkeys:
		(time, rotx, roty, rotz) = rk
		## Rotation key time, rotx, roty, rotz
		write_txt_line(fp, "ffff", [time, rotx, roty, rotz])
	



def write_txt_line(fp, valuestypes, valueslist):
	first_elem = True
	for i in range(0, len(valuestypes)):
		if first_elem == True:
			first_elem = False
		else:
			fp.write(" ")
		tp = valuestypes[i]
		val = valueslist[i]
		if tp == 's':
			print(";;" + str(val))
			fp.write("\"%s\"" % (val))
		elif tp == 'i':
			fp.write("%d" % (val))
		elif tp == 'f':
			fp.write("%.06f" % (val))
	fp.write("\n")

def write_txt_header(fp):
	fp.write("// MilkShape 3D ASCII\n")
def write_txt_newline(fp):
	fp.write("\n")

def write_txt_line_number(fp, num):
	fp.write("%d\n" % (num))

def write_txt_section(fp, sectionnm, num):
	fp.write("%s: %d\n" % (sectionnm, num))

