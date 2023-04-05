
##
##  MS3D Classes
##  
##  Copyright 2023 Edward Blake
##
##  See the file "LICENSE" for information on usage and redistribution
##  of this file, and for a DISCLAIMER OF ALL WARRANTIES.
##

class MS3DFile:
	def __init__(self):
		self.vertices = []
		self.triangles = []
		self.groups = []
		self.materials = []
		self.anim = (0, 0, 0)
		self.joints = []
		self.comments = None
		self.extra = None
		
	def update_ref_counts(self):
		for i in range(0, len(self.vertices)):
			self.vertices[i].ref_count = 0
			
		for t in self.triangles:
			self.vertices[t.v_1].ref_count = self.vertices[t.v_1].ref_count + 1
			self.vertices[t.v_2].ref_count = self.vertices[t.v_2].ref_count + 1
			self.vertices[t.v_3].ref_count = self.vertices[t.v_3].ref_count + 1
		
		for i in range(0, len(self.groups)):
			for tidx in self.groups[i].triangles:
				self.triangles[tidx].g_idx = i


class MS3DVertex:
	def __init__(self):
		self.flags = 0
		self.v_x = 0.0
		self.v_y = 0.0
		self.v_z = 0.0
		self.bone_id = -1
		self.ref_count = 0

class MS3DTriangle:
	def __init__(self):
		self.flags = 0
		self.v_1 = 0
		self.v_2 = 0
		self.v_3 = 0
		self.vn1 = (0.0, 0.0, 0.0)
		self.vn2 = (0.0, 0.0, 0.0)
		self.vn3 = (0.0, 0.0, 0.0)
		self.uv1 = (0.0, 0.0)
		self.uv2 = (0.0, 0.0)
		self.uv3 = (0.0, 0.0)
		self.sg = 0
		self.g_idx = 0

class MS3DGroup:
	def __init__(self):
		self.flags = 0
		self.name = ""
		self.triangles = []
		self.mat_index = -1

class MS3DMaterial:
	def __init__(self):
		self.name = ""
		self.ambient = (0.0, 0.0, 0.0, 0.0)
		self.diffuse = (0.0, 0.0, 0.0, 0.0)
		self.specular = (0.0, 0.0, 0.0, 0.0)
		self.emissive = (0.0, 0.0, 0.0, 0.0)
		self.shininess = 0.0
		self.transparency = 0.0
		self.mode = 0
		self.imagemap = ""
		self.alphamap = ""

class MS3DJoint:
	def __init__(self):
		self.flags = 0
		self.jointname = ""
		self.parentname = ""
		self.rot = (0.0, 0.0, 0.0)
		self.pos = (0.0, 0.0, 0.0)
		self.key_frames_rot = []
		self.key_frames_pos = []

class MS3DFileComments:
	def __init__(self):
		self.group_comments = []
		self.material_comments = []
		self.joint_comments = []
		self.model_comment = []

class MS3DVertex_ex:
	def __init__(self):
		self.bone_id1 = -1
		self.bone_id2 = -1
		self.bone_id3 = -1
		self.weight1 = 0.0
		self.weight2 = 0.0
		self.weight3 = 0.0
		self.extra1 = 0
		self.extra2 = 0

class MS3DJoint_ex:
	def __init__(self):
		self.col_r = 0.0
		self.col_g = 0.0
		self.col_b = 0.0

class MS3DModel_ex:
	def __init__(self):
		self.jointsize = 0.0
		self.transparencymode = 0
		self.alpharef = 0.0
		
class Mesh:
	def __init__(self):
		self.meshname = ""
		self.meshflags = 0
		self.materialindex = 0
		self.vertices = []
		self.normals = []
		self.trianglefaces = []
		
def list_triple(a):
	return (a[0], a[1], a[2])
		
class MeshHelper:
	def __init__(self):
		self.meshes = []
	
	def set(self, m):
		gidx = 0
		for mesh in self.meshes:
			
			meshname_0 = mesh.meshname
			flags_0 = mesh.meshflags
			materialindex_0 = mesh.materialindex
			vertices_0 = mesh.vertices
			normals_0 = mesh.normals
			trianglefaces_0 = mesh.trianglefaces
			
			g = MS3DGroup()
			g.flags = flags_0
			g.name = meshname_0
			g.mat_index = materialindex_0
			
			nv = [] # Vertices
			for v in vertices_0:
				(flags, v_x, v_y, v_z, v_u, v_v, boneindex) = v
				v = MS3DVertex()
				v.flags = flags
				v.v_x = v_x
				v.v_y = v_y
				v.v_z = v_z
				v.bone_id = boneindex
				nv.append(len(m.vertices))
				m.vertices.append(v)
			
			g.triangles = []
			for tri in trianglefaces_0:
				(flags, idx1, idx2, idx3, nidx1, nidx2, nidx3, smoothinggroup) = tri
				
				t = MS3DTriangle()
				t.flags = flags
				t.v_1 = nv[idx1]
				t.v_2 = nv[idx2]
				t.v_3 = nv[idx3]
				t.vn1 = list_triple(normals_0[nidx1])
				t.vn2 = list_triple(normals_0[nidx2])
				t.vn3 = list_triple(normals_0[nidx3])
				
				(_, _, _, _, v_u1, v_v1, _) = vertices_0[idx1]
				(_, _, _, _, v_u2, v_v2, _) = vertices_0[idx2]
				(_, _, _, _, v_u3, v_v3, _) = vertices_0[idx3]
				t.uv1 = (v_u1,v_v1)
				t.uv2 = (v_u2,v_v2)
				t.uv3 = (v_u3,v_v3)

				t.sg = smoothinggroup
				t.g_idx = gidx
				
				tri_idx = len(m.triangles)
				m.triangles.append(t)
				
				g.triangles.append(tri_idx)
			
			m.groups.append(g)
			gidx = gidx + 1
		m.update_ref_counts()
			
	def get(self, ms3df):
		vertices_0 = ms3df.vertices
		triangles_0 = ms3df.triangles
		groups_0 = ms3df.groups
		
		for g in groups_0:
			triangles = g.triangles
			
			nv = {} ## Vertices
			nn = {} ## Normals
			
			m = Mesh()
			m.meshname = g.name
			m.meshflags = g.flags
			m.materialindex = g.mat_index
			m.vertices = []
			m.normals = []
			m.trianglefaces = []
			
			for tri_idx in triangles:
				tri = triangles_0[tri_idx]
				
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
				
				if v_1 in nv:
					v1 = nv[v_1]
				else:
					v = vertices_0[v_1]
					nv[v_1] = len(m.vertices)
					v1 = nv[v_1]
					(uvu1,uvv1) = uv1
					m.vertices.append((v.flags, v.v_x,v.v_y,v.v_z, uvu1,uvv1, v.bone_id))
				
				if v_2 in nv:
					v2 = nv[v_2]
				else:
					v = vertices_0[v_2]
					nv[v_2] = len(m.vertices)
					v2 = nv[v_2]
					(uvu2,uvv2) = uv2
					m.vertices.append((v.flags, v.v_x,v.v_y,v.v_z, uvu2,uvv2, v.bone_id))
				
				if v_3 in nv:
					v3 = nv[v_3]
				else:
					v = vertices_0[v_3]
					nv[v_3] = len(m.vertices)
					v3 = nv[v_3]
					(uvu3,uvv3) = uv3
					m.vertices.append((v.flags, v.v_x,v.v_y,v.v_z, uvu3,uvv3, v.bone_id))
				
				if vn1 in nn:
					n1 = nn[vn1]
				else:
					nn[vn1] = len(m.normals)
					n1 = nn[vn1]
					m.normals.append(vn1)
				
				if vn2 in nn:
					n2 = nn[vn2]
				else:
					nn[vn2] = len(m.normals)
					n2 = nn[vn2]
					m.normals.append(vn2)
				
				if vn3 in nn:
					n3 = nn[vn3]
				else:
					nn[vn3] = len(m.normals)
					n3 = nn[vn3]
					m.normals.append(vn3)
				
				## triangle: flags, vertex index1, vertex index2, vertex index3, normal index1, normal index 2, normal index 3, smoothing group
				m.trianglefaces.append((flags,v1,v2,v3,n1,n2,n3,sg))
			
			self.meshes.append(m)

