
##
##  Read Milkshape3D MS3D (.ms3d) Files
##
##  Copyright 2023 Edward Blake
##
##  See the file "LICENSE" for information on usage and redistribution
##  of this file, and for a DISCLAIMER OF ALL WARRANTIES.
##

import struct
from ms3d.ms3d_cls import MS3DFileComments, MS3DFile, MS3DVertex, MS3DTriangle, MS3DGroup, MS3DMaterial, MS3DJoint, MS3DVertex_ex, MS3DJoint_ex, MS3DModel_ex, Mesh, MeshHelper


##
## flags
##	
READER_SELECTED = 1
READER_HIDDEN = 2
READER_SELECTED2 = 4
READER_DIRTY = 8

def file_read_str(fp, size):
	strval = fp.read(size)
	strval = strval.rstrip(b'\0')
	return strval.decode('ascii') # 'iso-8859-1' ?
def file_read_u8_maybe(fp):
	## 1 byte
	bt = fp.read(1)
	if len(bt) != 1:
		return None
	[v] = struct.unpack('B', bt)
	return v
def file_read_u8(fp):
	v = file_read_u8_maybe(fp)
	if v == None:
		raise "EOF"
	return v
def file_read_s8_maybe(fp):
	## 1 byte
	bt = fp.read(1)
	if len(bt) != 1:
		return None
	[v] = struct.unpack('b', bt)
	return v
def file_read_s8(fp):
	v = file_read_s8_maybe(fp)
	if v == None:
		raise "EOF"
	return v
def file_read_u16_maybe(fp):
	## 2 byte
	bt = fp.read(2)
	if len(bt) != 2:
		return None
	[v] = struct.unpack('H', bt)
	return v
def file_read_u16(fp):
	v = file_read_u16_maybe(fp)
	if v == None:
		raise "EOF"
	return v
def file_read_u32_maybe(fp):
	## 4 bytes
	bt = fp.read(4)
	if len(bt) != 4:
		return None
	[v] = struct.unpack('I', bt)
	return v
def file_read_u32(fp):
	v = file_read_u32_maybe(fp)
	if v == None:
		raise "EOF"
	return v
def file_read_float_maybe(fp):
	## 4 bytes
	bt = fp.read(4)
	if len(bt) != 4:
		return None
	[v] = struct.unpack('f', bt)
	return v
def file_read_float(fp):
	v = file_read_float_maybe(fp)
	if v == None:
		raise "EOF"
	return v
	
def read_ms3d_file(flname):
	if flname[-4:].lower() == ".txt":
		return read_ms3d_txt_file(flname)
	else:
		return read_ms3d_bin_file(flname)

## Read Milkshape 3D MS3D Files

def read_ms3d_bin_file(flname):
	fp = open(flname, "rb")
	if not ms3d_header_t(fp):
		raise Exception("Not a ms3d file")
		
	## number of vertices, 2 bytes
	vertices = []
	num_vertices = file_read_u16(fp)
	for i in range(0, num_vertices):
		v = ms3d_vertex_t(fp)
		vertices.append(v)
	
	triangles = []
	num_triangles = file_read_u16(fp) ## number of triangles, 2 bytes
	for i in range(0, num_triangles):
		tri = ms3d_triangle_t(fp)
		triangles.append(tri)
	
	groups = []
	num_groups = file_read_u16(fp) ## number of groups, 2 bytes
	for i in range(0, num_groups):
		g = ms3d_group_t(fp)
		groups.append(g)
	
	materials = []
	num_materials = file_read_u16(fp)  ## number of materials, 2 bytes
	for i in range(0, num_materials):
		m = ms3d_material_t(fp)
		materials.append(m)
	
	## keyframer data
	animation_fps = file_read_float(fp) ## 4 bytes
	current_time = file_read_float(fp) ## 4 bytes
	total_frames = file_read_u32(fp) ## 4 bytes
	anim = (animation_fps, current_time,total_frames)
	
	joints = []
	num_joints = file_read_u16(fp) ## number of joints, 2 bytes
	for i in range(0, num_joints):
		j = ms3d_joint_t(fp)
		joints.append(j)
	
	group_comments = []
	material_comments = []
	joint_comments = []
	model_comment = []
	extra = (None,None,None)
	sub_version = file_read_u32(fp) ## subVersion is = 1, 4 bytes
	if sub_version > 0:
		num_group_comments = file_read_u32(fp) ## 4 bytes
		for i in range(0, num_group_comments):
			c = ms3d_comment_t(fp)
			group_comments.append(c)
		num_material_comments = file_read_u32(fp) ## 4 bytes
		for i in range(0, num_material_comments):
			c = ms3d_comment_t(fp)
			material_comments.append(c)
		num_joint_comments = file_read_u32(fp) ## 4 bytes
		for i in range(0, num_joint_comments):
			c = ms3d_comment_t(fp)
			joint_comments.append(c)
		has_model_comment = file_read_u32(fp) ## 4 bytes
		for i in range(0, has_model_comment):
			c = ms3d_comment_t(fp)
			model_comment.append(c)
		extra = ms3d_extra(fp, num_vertices, num_joints)

	comments = MS3DFileComments()
	comments.group_comments = group_comments
	comments.material_comments = material_comments
	comments.joint_comments = joint_comments
	comments.model_comment = model_comment
	
	msf = MS3DFile()
	msf.vertices = vertices
	msf.triangles = triangles
	msf.groups = groups
	msf.materials = materials
	msf.anim = anim
	msf.joints = joints
	msf.comments = comments
	msf.extra = extra
	return msf


##
## The header
def ms3d_header_t(fp):
	v = fp.read(10)
	if v == b"MS3D000000":
		version = file_read_u32(fp)
		## version should be 4
		return True
	else:
		return False
	

##
## Vertex
##
def ms3d_vertex_t(fp):
	v = MS3DVertex()
	v.flags = file_read_u8(fp)
	v.v_x = file_read_float(fp)
	v.v_y = file_read_float(fp)
	v.v_z = file_read_float(fp)

	v.bone_id = file_read_s8(fp)           ## -1 = no bone
	v.ref_count = file_read_u8(fp)
	return v
	

## Triangles
##
def ms3d_triangle_t(fp):
	t = MS3DTriangle()
	t.flags = file_read_u16(fp)
	t.v_1 = file_read_u16(fp)
	t.v_2 = file_read_u16(fp)
	t.v_3 = file_read_u16(fp)
	
	vns_1x = file_read_float(fp)
	vns_1y = file_read_float(fp)
	vns_1z = file_read_float(fp)
	t.vn1 = (vns_1x, vns_1y, vns_1z)
	
	vns_2x = file_read_float(fp)
	vns_2y = file_read_float(fp)
	vns_2z = file_read_float(fp)
	t.vn2 = (vns_2x, vns_2y, vns_2z)
	
	vns_3x = file_read_float(fp)
	vns_3y = file_read_float(fp)
	vns_3z = file_read_float(fp)
	t.vn3 = (vns_3x, vns_3y, vns_3z)

	u1 = file_read_float(fp)
	u2 = file_read_float(fp)
	u3 = file_read_float(fp)

	v1 = file_read_float(fp)
	v2 = file_read_float(fp)
	v3 = file_read_float(fp)
	t.uv1 = (u1,v1)
	t.uv2 = (u2,v2)
	t.uv3 = (u3,v3)

	t.sg = file_read_u8(fp)           ## 1 - 32 (smoothing group)
	t.g_idx = file_read_u8(fp)        ## group index
	
	return t
	

##
## Groups
##
def ms3d_group_t(fp):
	g = MS3DGroup()
	g.flags = file_read_u8(fp)
	g.name = file_read_str(fp, 32)
	numtriangles = file_read_u16(fp)
	g.triangles = []
	for i in range(0, numtriangles):
		tri_idx = file_read_u16(fp)
		g.triangles.append(tri_idx)
	g.mat_index = file_read_s8(fp)              ## -1 = no material
	
	return g


##
## Materials
##
def ms3d_material_t(fp):
	mat = MS3DMaterial()
	mat.name = file_read_str(fp, 32)
	am_r = file_read_float(fp)
	am_g = file_read_float(fp)
	am_b = file_read_float(fp)
	am_a = file_read_float(fp)
	mat.ambient = (am_r, am_g, am_b, am_a)

	df_r = file_read_float(fp)
	df_g = file_read_float(fp)
	df_b = file_read_float(fp)
	df_a = file_read_float(fp)
	mat.diffuse = (df_r, df_g, df_b, df_a)

	sp_r = file_read_float(fp)
	sp_g = file_read_float(fp)
	sp_b = file_read_float(fp)
	sp_a = file_read_float(fp)
	mat.specular = (sp_r, sp_g, sp_b, sp_a)

	em_r = file_read_float(fp)
	em_g = file_read_float(fp)
	em_b = file_read_float(fp)
	em_a = file_read_float(fp)
	mat.emissive = (em_r, em_g, em_b, em_a)

	mat.shininess = file_read_float(fp)                          ## 0.0f - 128.0f
	mat.transparency = file_read_float(fp)                       ## 0.0f - 1.0f
	mat.mode = file_read_s8(fp)                     ## 0, 1, 2 is unused now
	mat.imagemap = file_read_str(fp, 128)                       ## Texture file name
	mat.alphamap = file_read_str(fp, 128)                       ## Alpha map file name
	return mat


def ms3d_joint_t(fp):
	j = MS3DJoint()
	j.flags = file_read_u8(fp)
	j.jointname = file_read_str(fp, 32)
	j.parentname = file_read_str(fp, 32)
	
	rot_x = file_read_float(fp)
	rot_y = file_read_float(fp)
	rot_z = file_read_float(fp)
	j.rot = (rot_x, rot_y, rot_z)
	
	pos_x = file_read_float(fp)
	pos_y = file_read_float(fp)
	pos_z = file_read_float(fp)
	j.pos = (pos_x, pos_y, pos_z)

	num_key_frames_rot = file_read_u16(fp)
	num_key_frames_trans = file_read_u16(fp)
	
	j.key_frames_rot = []
	for i in range(0, num_key_frames_rot):
		time = file_read_float(fp)                               # time in seconds
		r_x = file_read_float(fp)
		r_y = file_read_float(fp)
		r_z = file_read_float(fp)
		j.key_frames_rot.append((time, r_x,r_y,r_z))
	
	j.key_frames_pos = []
	for i in range(0, num_key_frames_trans):
		time = file_read_float(fp)                               ## time in seconds
		p_x = file_read_float(fp)
		p_y = file_read_float(fp)
		p_z = file_read_float(fp)
		j.key_frames_pos.append((time, p_x,p_y,p_z))
	return j


##
## Group comments
##
def ms3d_comment_t(fp):
	index = file_read_u32(fp)         ## index of group, material or joint
	clen = file_read_u32(fp)          ## length of comment
	comment = file_read_str(fp, clen) ## comment
	return (index, comment)
	

def ms3d_extra(fp, num_vertices, num_joints):
	
	extra_vs = []
	sub_version = file_read_u32_maybe(fp)
	if sub_version == None:
		return (None, None, None)
		
	## print("sub_version vs=" + str(sub_version))
	if sub_version > 0 and sub_version < 4:
		for i in range(0, num_vertices):
			ex = ms3d_vertex_ex_t(fp, sub_version)
			extra_vs.append(ex)
	else:
		return (None, None, None)
	
	extra_jn = []
	sub_version = file_read_u32_maybe(fp)
	if sub_version == None:
		return (None, None, None)
	## print("sub_version jn=" + str(sub_version))
	if sub_version > 0 and sub_version < 2:
		for i in range(0, num_joints):
			ex = ms3d_joint_ex_t(fp, sub_version)
			extra_jn.append(ex)
	else:
		return (None, None, None)
	
	extra_md = None
	sub_version = file_read_u32_maybe(fp)
	if sub_version == None:
		return (None, None, None)
	## print("sub_version md=" + str(sub_version))
	if sub_version > 0 and sub_version < 2:
		extra_md = ms3d_model_ex_t(fp, sub_version)
	return (extra_vs, extra_jn, extra_md)


def ms3d_vertex_ex_t(fp, sub_version):
	vex = MS3DVertex_ex()
	vex.bone_id1 = file_read_s8(fp)
	vex.bone_id2 = file_read_s8(fp)
	vex.bone_id3 = file_read_s8(fp)             ## index of joint or -1
	vex.weight1 = file_read_u8(fp) / 100.0
	vex.weight2 = file_read_u8(fp) / 100.0
	vex.weight3 = file_read_u8(fp) / 100.0
	
	vex.extra1 = 0
	vex.extra2 = 0
	## vertex extra
	if sub_version == 1:
		pass
	elif sub_version == 2:
		# for subversion == 2
		vex.extra1 = file_read_u32(fp)
	elif sub_version == 3:
		# for subversion == 3
		vex.extra1 = file_read_u32(fp)
		vex.extra2 = file_read_u32(fp)
	return vex
	

## for subVersion == 1
def ms3d_joint_ex_t(fp, sub_version):
	exj = MS3DJoint_ex()
	exj.col_r = 0.8
	exj.col_g = 0.8
	exj.col_b = 0.8
	if sub_version >= 1:
		exj.col_r = file_read_float(fp)
		exj.col_g = file_read_float(fp)
		exj.col_b = file_read_float(fp)
	return exj
	

## for subVersion == 1
def ms3d_model_ex_t(fp, sub_version):
	exm = MS3DModel_ex()
	exm.jointsize = 0.01
	exm.transparencymode = 0
	exm.alpharef = 1.0
	if sub_version >= 1:
		exm.jointsize = file_read_float(fp)	## joint size, since subVersion == 1
		exm.transparencymode = file_read_u32(fp)
		exm.alpharef = file_read_float(fp)
	return exm



##
## Read Milkshape 3D Text files
##

def read_ms3d_txt_file(flname):
	fp = open(flname, "r", encoding="utf-8")
	meshes = []
	materials = []
	
	while True:
		[section_name, num] = read_txt_line_section(fp)
		if section_name == "eof":
			break
		section_name = section_name.lower()
		if section_name == "frames":
			num_frames = num   ## Total frames
		if section_name == "frame":
			frame_number = num  ## Current frame
		if section_name == "meshes":
			num_meshes = num  ## Number of meshes
			for m_i in range(0, num_meshes):
				m = read_txt_mesh(fp, num_meshes)
				meshes.append(m)
		if section_name == "materials":
			## Number of materials
			num_materials = num
			for m_i in range(0, num_materials):
				m = read_txt_material(fp, num_materials)
				materials.append(m)
		if section_name == "bones":
			## Number of joints
			num_bones = num
			for m_i in range(0, num_bones):
				read_txt_bone(fp, num_bones)
		if section_name == "groupcomments":
			num_group_comments = num
			for m_i in range(0, num_group_comments):
				read_txt_group_comment(fp, num_group_comments)
		if section_name == "materialcomments":
			num_material_comments = num
			for m_i in range(0, num_material_comments):
				read_txt_material_comment(fp, num_material_comments)
		if section_name == "bonecomments":
			num_bone_comments = num
			for m_i in range(0, num_bone_comments):
				read_txt_bone_comment(fp, num_bone_comments)
		if section_name == "modelcomment":
			num_model_comment = num
			for m_i in range(0, num_model_comment):
				read_txt_model_comment(fp, num_model_comment)
	ms3df = MS3DFile()
	ms3df.materials = materials
	mh = MeshHelper()
	mh.meshes = meshes
	mh.set(ms3df)
	return ms3df
	


def read_txt_header(fp):
	line_0 = fp.readline()
	line_1 = line_0.strip().lower()
	return line_1 == "// milkshape 3d ascii"


def read_txt_mesh(fp, num_meshes):
	## Mesh name, flags, material index
	[meshname, meshflags, materialindex] = read_txt_line(fp, "sii")
	
	vertices = []
	normals = []
	trianglefaces = []
	
	## Number of vertices
	vs = []
	[num_lines_1] = read_txt_line(fp, "i")
	for i in range(0, num_lines_1):
		## Vertex flags, x, y, z, u, v, bone index
		[flags, v_x,v_y,v_z, u,v, bindex] = read_txt_line(fp, "ifffffi")
		vertices.append((flags, v_x,v_y,v_z, u,v, bindex))
	
	## Number of normals
	ns = []
	[num_lines_2] = read_txt_line(fp, "i")
	for i in range(0, num_lines_2):
		## Normal x, y, z
		[nrm_x, nrm_y, nrm_z] = read_txt_line(fp, "fff")
		normals.append((nrm_x, nrm_y, nrm_z))
	
	## Number of triangles
	tris = []
	[num_lines_3] = read_txt_line(fp, "i")
	for i in range(0, num_lines_3):
		## Triangle flags, vertex index1, vertex index2, vertex index3, normal index1, normal index 2, normal index 3, smoothing group
		[flags,v1,v2,v3,n1,n2,n3,sg] = read_txt_line(fp, "iiiiiiii")
		trianglefaces.append((flags,v1,v2,v3,n1,n2,n3,sg))
		
	m = Mesh()
	m.meshname = meshname
	m.meshflags = meshflags
	m.materialindex = materialindex
	m.vertices = vertices
	m.normals = normals
	m.trianglefaces = trianglefaces
	return m





def read_txt_material(fp, num_materials):

	## Material name
	[materialname] = read_txt_line(fp, "s")

	## Ambient
	[am_r, am_g, am_b, am_a] = read_txt_line(fp, "ffff")
	ambient = (am_r, am_g, am_b, am_a)

	## Diffuse
	[df_r, df_g, df_b, df_a] = read_txt_line(fp, "ffff")
	diffuse = (df_r, df_g, df_b, df_a)

	## Specular
	[sp_r, sp_g, sp_b, sp_a] = read_txt_line(fp, "ffff")
	specular = (sp_r, sp_g, sp_b, sp_a)

	## Emissive
	[em_r, em_g, em_b, em_a] = read_txt_line(fp, "ffff")
	emissive = (em_r, em_g, em_b, em_a)

	## Shininess
	[shininess] = read_txt_line(fp, "f")

	## Transparency
	[transparency] = read_txt_line(fp, "f")

	## Texture map
	[colormap] = read_txt_line(fp, "s")

	## Alpha map
	[alphamap] = read_txt_line(fp, "s")

	mat = MS3DMaterial()
	mat.name = materialname
	mat.ambient = ambient
	mat.diffuse = diffuse
	mat.specular = specular
	mat.emissive = emissive
	mat.shininess = shininess
	mat.transparency = transparency
	mat.mode = 0
	mat.imagemap = colormap
	mat.alphamap = alphamap
	return mat


def read_txt_bone(fp, NumBones):
	
	## Name
	[joint_name] = read_txt_line(fp, "s")

	## Parent name
	[parent_name] = read_txt_line(fp, "s")

	## Joint flags, posx, posy, posz, rotx, roty, rotz
	[flags, pos_x, pos_y, pos_z, rot_x, rot_y, rot_z] = read_txt_line(fp, "iffffff")

	## Number of position keys
	[num_position_keys] = read_txt_line(fp, "i")
	key_frames_pos = []
	for i in range(0, num_position_keys):
		## Position key time, posx, posy, posz
		[time, pos_x, pos_y, pos_z] = read_txt_line(fp, "ffff")
		key_frames_pos.append((time, pos_x, pos_y, pos_z))
	
	## Number of rotation keys
	[num_rotation_keys] = read_txt_line(fp, "i")
	key_frames_rot = []
	for i in range(0, num_rotation_keys):
		## Rotation key time, rotx, roty, rotz
		[time, rot_x, rot_y, rot_z] = read_txt_line(fp, "ffff")
		key_frames_rot.append((time, rot_x, rot_y, rot_z))
	
	joint = MS3DJoint()
	joint.flags = flags
	joint.jointname = joint_name
	joint.parentname = parent_name
	joint.rot = (rot_x, rot_y, rot_z)
	joint.pos = (pos_x, pos_y, pos_z)
	joint.key_frames_rot = key_frames_rot
	joint.key_frames_pos = key_frames_pos
	return joint


def read_txt_group_comment(fp, NumGroupComments):
	return None


def read_txt_material_comment(fp, NumMaterialComments):
	return None


def read_txt_bone_comment(fp, NumBoneComments):
	return None


def read_txt_model_comment(fp, NumModelComment):
	return None


def read_txt_line_section(fp):
	line_0 = fp.readline()
	if line_0 == "":
		return ["eof", 0]
	line_1 = strip_comments(line_0).strip()
	while line_1 == "":
		line_0 = fp.readline()
		if line_0 == "":
			return ["eof", 0]
		line_1 = strip_comments(line_0).strip()
	[section_name, int_number_s] = line_1.split(":")
	return [section_name, int(int_number_s)]

def read_txt_line(fp, types):
	line_0 = fp.readline()
	line_1 = strip_comments(line_0).strip()
	while line_1 == "":
		line_0 = fp.readline()
		line_1 = strip_comments(line_0).strip()
	type_vals = []
	i2 = 0
	for t in types:
		## Advance until a non space character
		while (line_1[i2] == ' ') or (line_1[i2] == '\t'):
			i2 = i2 + 1
		if t == "s":
			if line_1[i2] == '"':
				i2b = i2 + 1
				i2 = i2 + 1
				while line_1[i2] != '"':
					i2 = i2 + 1
				strval = line_1[i2b:i2]
				type_vals.append(strval)
				i2 = i2 + 1
		
		elif t == "i":
			i2b = i2
			i2 = i2 + 1
			while i2 < len(line_1) and (line_1[i2] != ' ') and (line_1[i2] != '\t'):
				i2 = i2 + 1
			strval = line_1[i2b:i2]
			type_vals.append(int(strval))
		
		elif t == "f":
			i2b = i2
			i2 = i2 + 1
			while i2 < len(line_1) and (line_1[i2] != ' ') and (line_1[i2] != '\t'):
				i2 = i2 + 1
			strval = line_1[i2b:i2]
			type_vals.append(float(strval))
	return type_vals
	
	
## Remove comments
def strip_comments(line_0):
	i2 = 0
	i2l = len(line_0)
	while True:
		if i2+1 >= i2l:
			return line_0
		if (line_0[i2] == '/') and (line_0[i2+1] == '/'):
			ret = line_0[0:i2]
			return ret
		i2 = i2 + 1

