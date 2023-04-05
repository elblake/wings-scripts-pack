
##
##  This file is part of the Godot Mesh Exporter for Wings3D
##
##  Copyright 2023 Edward Blake
##
##  See the file "LICENSE" for information on usage and redistribution
##  of this file, and for a DISCLAIMER OF ALL WARRANTIES.
##

import sys
import struct
from os import path

ARRAY_COMPRESS_DEFAULT = 2194432
ARRAY_FORMAT_VERTEX = 1
ARRAY_FORMAT_NORMAL = 2
ARRAY_FORMAT_TANGENT = 4
ARRAY_FORMAT_COLOR = 8
ARRAY_FORMAT_TEX_UV = 16
ARRAY_FORMAT_TEX_UV2 = 32
ARRAY_FORMAT_BONES = 64
ARRAY_FORMAT_WEIGHTS = 128
ARRAY_FORMAT_INDEX = 256

EXPORTER_STRING = "Exported with Godot Exporter Script for Wings3D"

class GodotFile:
	def __init__(self):
		self.list = []
	def add(self, it):
		self.list.append(it)
	def write_to(self, fo):
		for it in self.list:
			it.write(fo)
			
def str_indent(indent):
	return '  ' * indent

class Transform:
	def __init__(self, basis=None, origin=None):
		if basis != None:
			self.basis = basis
		else:
			self.basis = [1, 0, 0, 0, 1, 0, 0, 0, 1]
		if origin != None:
			self.origin = origin
		else:
			self.origin = [0, 0, 0]
	def wr_out(self, indent, fo):
		fo.write("Transform( ")
		u = 0
		list = self.basis + self.origin
		for it in list:
			if u > 0:
				fo.write(", ")
			fo.write(str(it))
			u = u + 1
		fo.write(" )")
	
class SubResource:
	def __init__(self, l):
		self.res = l
	def wr_out(self, indent, fo):
		fo.write("SubResource( ")
		fo.write(str(self.res))
		fo.write(" )")
	
class PoolByteArray:
	def __init__(self, l):
		self.list = l
	def wr_out(self, indent, fo):
		fo.write("PoolByteArray( ")
		u = 0
		for it in self.list:
			if u > 0:
				fo.write(", ")
			fo.write(str(it))
			u = u + 1
		fo.write(" )")
		
class Vector3Array:
	def __init__(self, l):
		self.list = l
	def wr_out(self, indent, fo):
		fo.write("Vector3Array( ")
		u = 0
		for it in self.list:
			if u > 0:
				fo.write(", ")
			fo.write(str(it))
			u = u + 1
		fo.write(" )")

class IntArray:
	def __init__(self, l):
		self.list = l
	def wr_out(self, indent, fo):
		fo.write("IntArray( ")
		u = 0
		for it in self.list:
			if u > 0:
				fo.write(", ")
			fo.write(str(it))
			u = u + 1
		fo.write(" )")
	
	
	
	
class AttributeList:
	def __init__(self):
		self.list = []
	def set(self, name, val):
		self.list.append((name, val))
	def wr_out(self, indent, fo):
		indent_1 = indent + 1
		fo.write("{\n")
		u = 0
		for atr in self.list:
			if u > 0:
				fo.write(",\n")
			fo.write(str_indent(indent_1) + "\"" + atr[0] + "\": ")
			atr[1].wr_out(indent_1, fo)
			u = u + 1
		fo.write("\n")
		fo.write("}")

class BasicString:
	def __init__(self, str):
		self.str = str
	def wr_out(self, indent, fo):
		fo.write("\"" + self.str + "\"")

class AABB:
	def __init__(self, l):
		self.list = l
	def wr_out(self, indent, fo):
		fo.write("AABB( ")
		u = 0
		for it in self.list:
			if u > 0:
				fo.write(", ")
			fo.write(str(it))
			u = u + 1
		fo.write(" )")

class BasicList:
	def __init__(self, l):
		self.list = l
	def wr_out(self, indent, fo):
		fo.write("[")
		if len(self.list) >= 1:
			indent_1 = indent + 1
			fo.write("\n")
			u = 0
			had_explanation = None
			for it in self.list:
				if u > 0:
					fo.write(", ")
					if had_explanation != None:
						fo.write("; " + had_explanation)
						had_explanation = None
					fo.write("\n")
				fo.write(str_indent(indent_1))
				it.wr_out(indent_1, fo)
				if isinstance(it, BasicNull):
					had_explanation = it.has_explanation()
				u = u + 1
			if had_explanation != None:
				fo.write("  ; " + had_explanation)
			fo.write("\n")
		else:
			fo.write("  ")
		fo.write("]")

class BasicInteger:
	def __init__(self, l):
		self.value = l
	def wr_out(self, indent, fo):
		fo.write(str(self.value))

class ExtResource:
	def __init__(self, l):
		self.res = l
	def wr_out(self, indent, fo):
		fo.write("ExtResource( ")
		fo.write(str(self.res))
		fo.write(" )")
	
class BasicBool:
	def __init__(self, l):
		self.val = l
	def wr_out(self, indent, fo):
		if self.val == True: 
			fo.write("true")
		else:
			fo.write("false")

class BasicNull:
	def __init__(self, explanation=None):
		self.explanation = explanation
	def has_explanation(self):
		return self.explanation
	def wr_out(self, indent, fo):
		fo.write("null")


class BasicColor:
	def __init__(self, r, g, b, a):
		self.r = r
		self.g = g
		self.b = b
		self.a = a
	def wr_out(self, indent, fo):
		fo.write("Color( ")
		fo.write(str(self.r))
		fo.write(", ")
		fo.write(str(self.g))
		fo.write(", ")
		fo.write(str(self.b))
		fo.write(", ")
		fo.write(str(self.a))
		fo.write(" )")
	
		
	
class Vector2:
	def __init__(self, x, y):
		self.x = x
		self.y = y
	def wr_out(self, indent, fo):
		fo.write("Vector2( " + str(self.x) + ", " + str(self.y) + " )")


class NodeGDResourceHeader:
	def __init__(self, rtype):
		self.format = 2
		self.load_steps = 5
		self.restype = rtype
	def write(self, fo):
		write_node(fo, "gd_resource", [
			("type", self.restype),
			("load_steps", self.load_steps),
			("format", self.format)
		])
		fo.write("; " + EXPORTER_STRING + "\n")
		write_node_nl(fo)

class NodeGDArrayMeshResourceHeader:
	def __init__(self):
		self.format = 2
		self.load_steps = 5
	def write(self, fo):
		write_node(fo, "gd_resource", [
			("type", "MeshLibrary"),
			("load_steps", self.load_steps),
			("format", self.format)
		])
		fo.write("; " + EXPORTER_STRING + "\n")
		write_node_nl(fo)


class NodeExtResource:
	def __init__(self, id):
		self.path = "res://default.material"
		self.id = id
		self.rtype = "Material"
	def write(self, fo):
		write_node(fo, "ext_resource", [
			("path", self.path),
			("type", self.rtype),
			("id", self.id)
		])
		write_node_nl(fo)
	
def write_attr(fo, attr_name, attr_val):
	fo.write(attr_name + " = ")
	attr_val.wr_out(0, fo)
	fo.write("\n")
	
def write_attr_idx(fo, attr_name, idx, attr_val):
	write_attr(fo, attr_name + "/" + str(idx), attr_val)
	
def write_node(fo, node_type, node_attr=None):
	fo.write("[" + node_type)
	if node_attr != None:
		for atr in node_attr:
			fo.write(" " + atr[0] + "=")
			if type(atr[1]) is str:
				fo.write("\"" + atr[1] + "\"")
			else:
				fo.write(str(atr[1]))
	fo.write("]\n")
	
def write_node_nl(fo):
	fo.write("\n")
	

	
class VertexArray:
	def __init__(self):
		self.list = []
		self.uv = False
		self.normals = False
	def add(self, xyz, nrm, uv=None):
		if uv != None:
			self.uv = True
		if nrm != None:
			self.normals = True
		self.list.append((xyz,nrm,uv))
	def has_uv(self):
		return self.uv
	def count(self):
		return len(self.list)
	def to_packed(self):
		## Pack to 32-bit float x y z + 16-bit octahedron normal x y + 16 bit float u v PoolByteArray
		blist = []
		for l in self.list:
			xyz = l[0]
			nrm = l[1]
			uv = l[2]
			x = float(xyz[0])
			y = float(xyz[1])
			z = float(xyz[2])
			n_o = godot_oct_compress(nrm)
			n_o_x = n_o[0]
			n_o_y = n_o[1]
			if self.uv:
				## With UV
				u = uv[0]
				v = uv[1]
				blist.extend(list(struct.pack('<fffeeee', x, y, z, n_o_x, n_o_y, u, v)))
			else:
				## Without UV
				blist.extend(list(struct.pack('<fffee', x, y, z, n_o_x, n_o_y)))
		return PoolByteArray(blist)
	def vertex_to_v3array(self):
		blist = []
		for l in self.list:
			blist.extend(list(l[0]))
		return Vector3Array(blist)
	def normal_to_v3array(self):
		if self.normals:
			blist = []
			for l in self.list:
				blist.extend(list(l[1]))
			return Vector3Array(blist)
		else:
			return BasicNull("No Normals")
	def uv1_to_v3array(self):
		blist = []
		for l in self.list:
			blist.extend(list(l))
		return Vector3Array(blist)
	def get_aabb(self):
		if len(self.list) == 0:
			return None
		min_x = self.list[0][0][0]
		min_y = self.list[0][0][1]
		min_z = self.list[0][0][2]
		max_x = min_x
		max_y = min_y
		max_z = min_z
		for l in self.list:
			xyz = l[0]
			x = xyz[0]
			y = xyz[1]
			z = xyz[2]
			if x < min_x:
				min_x = x
			if y < min_y:
				min_y = y
			if z < min_z:
				min_z = z
			if x > max_x:
				max_x = x
			if y > max_y:
				max_y = y
			if z > max_z:
				max_z = z
		return AABB([min_x, min_y, min_z, max_x - min_x, max_y - min_y, max_z - min_z])
		

class VertexIndexArray:
	def __init__(self):
		self.list = []
	def add(self, idx):
		self.list.append(idx)
	def count(self):
		return len(self.list)
	def to_packed(self):
		## Pack to little endian integers PoolByteArray
		blist = []
		for idx in self.list:
			blist.extend(list(struct.pack('<H', idx)))
		return PoolByteArray(blist)
	def to_int_array(self):
		return IntArray(self.list)

class Surface:
	def __init__(self, vertarray, vertidxarray = None, old_surface_format=False):
		self.primitive = 4
		self.aabb = None             ## A AABB
		self.blend_shape_data = []   ## A list
		self.material = None
		self.skeleton_aabb = []      ## A list
		
		## For "format", "array_data" and "array_index_data"
		self.array_data = None
		self.vertex_count = None
		self.array_index_data = None
		self.index_count = None
		self.format = None
		
		## For "arrays" (old surface format)
		self.arrays = None
		
		if old_surface_format:
			if (vertarray != None) and (vertidxarray != None):
				self.aabb = vertarray.get_aabb()
				blist = [
					vertarray.vertex_to_v3array(),
					vertarray.normal_to_v3array(),
					BasicNull("No Tangents"),
					BasicNull("No Vertex Colors"),
					BasicNull("No UV1"),
					BasicNull("No UV2"),
					BasicNull("No Bones"),
					BasicNull("No Weights"),
					vertidxarray.to_int_array()
				]
				self.arrays = BasicList(blist)
		else:
			# With UV
			format_num = ARRAY_COMPRESS_DEFAULT
			format_num += ARRAY_FORMAT_VERTEX
			format_num += ARRAY_FORMAT_NORMAL
			format_num += ARRAY_FORMAT_INDEX
			if vertarray != None:
				self.aabb = vertarray.get_aabb()
				self.vertex_count = vertarray.count()
				if vertarray.has_uv(): # have UV
					format_num += ARRAY_FORMAT_TANGENT
					format_num += ARRAY_FORMAT_TEX_UV
				self.array_data = vertarray.to_packed()
			if vertidxarray != None:
				self.index_count = vertidxarray.count()
				self.array_index_data = vertidxarray.to_packed()
			self.format = format_num
		

	def to_attrlist(self):
		atl1 = AttributeList()
		if self.aabb != None:
			atl1.set("aabb", self.aabb)
		
		## Using the "format", "array_data" and "array_index_data" attributes, this
		## is the new format for Godot resources.
		if self.array_data != None:
			atl1.set("array_data", self.array_data)
			if self.vertex_count != None:
				atl1.set("vertex_count", BasicInteger(self.vertex_count))
			atl1.set("format", BasicInteger(self.format))
		if self.array_index_data != None:
			atl1.set("array_index_data", self.array_index_data)
			if self.index_count != None:
				atl1.set("index_count", BasicInteger(self.index_count))
			atl1.set("blend_shape_data", BasicList(self.blend_shape_data))
		
		## Using the "arrays" attribute, note this might only work for .tscn files
		## and not for .tres files.
		if self.arrays != None:
			atl1.set("arrays", self.arrays)
		
		if self.material != None:
			atl1.set("material", self.material)
		
		atl1.set("primitive", BasicInteger(self.primitive))
		atl1.set("skeleton_aabb", BasicList(self.skeleton_aabb))
		return atl1

class NodeArrayMeshSubResource:
	def __init__(self, id):
		self.resource_name = None
		self.surfaces = []
		self.id = id
	def add_surface(self, srf):
		self.surfaces.append(srf)
	def write(self, fo):
		write_node(fo, "sub_resource", [("type", "ArrayMesh"), ("id", self.id)])
		if self.resource_name != None:
			write_attr(fo, "resource_name", BasicString(self.resource_name))
		idx = 0
		for sr in self.surfaces:
			atl1 = sr.to_attrlist()
			write_attr_idx(fo, "surfaces", idx, atl1)
			idx = idx + 1
		write_node_nl(fo)

class NodeImageSubResource:
	def __init__(self, id):
		self.bitmap = []
		self.format = "RGBA8"
		self.width = 64
		self.height = 64
		self.id = id
	def write(self, fo):
		atl1 = AttributeList()
		if self.bitmap != None:
			atl1.set("data", PoolByteArray(self.bitmap))
		atl1.set("format", BasicString(self.format))
		atl1.set("height", BasicInteger(self.height))
		atl1.set("mipmaps", BasicBool(False))
		atl1.set("width", BasicInteger(self.width))
		
		write_node(fo, "sub_resource", [("type", "Image"), ("id", self.id)])
		write_attr(fo, "data", atl1)
		write_node_nl(fo)

class NodeImageTextureSubResource:
	def __init__(self, id):
		self.image = None # SubResource
		self.size = None # Vector2
		self.id = id
	def write(self, fo):
		write_node(fo, "sub_resource", [("type", "ImageTexture"), ("id", self.id)])
		if self.image != None:
			write_attr(fo, "image", self.image)
		if self.size != None:
			write_attr(fo, "size", self.size)
		write_node_nl(fo)
	
	
def write_item(fo, idx, attr_name, attr_val):
	write_attr(fo, "item/" + str(idx) + "/" + attr_name, attr_val)

class NodeResourceMeshItem:
	def __init__(self, nm):
		self.preview = None
		self.navmesh_transform = Transform()
		self.name = nm
		self.mesh = None
		self.mesh_transform = Transform()
		self.shapes = []
	def write(self, fo, idx):
		write_item(fo, idx, "name", BasicString(self.name))
		if self.mesh != None:
			write_item(fo, idx, "mesh", self.mesh)
		if self.mesh_transform != None:
			write_item(fo, idx, "mesh_transform", self.mesh_transform)
		write_item(fo, idx, "shapes", BasicList(self.shapes))
		if self.navmesh_transform != None:
			write_item(fo, idx, "navmesh_transform", self.navmesh_transform)
		if self.preview != None:
			write_item(fo, idx, "preview", self.preview)

class NodeResourceMaterialAlbedo:
	def __init__(self, albc):
		self.color = albc
		self.albedo_texture = None
	def write(self, fo, idx):
		write_attr(fo, "albedo_color", self.color)
		if self.albedo_texture != None:
			write_attr(fo, "albedo_texture", ExtResource(self.albedo_texture))

class NodeResource:
	def __init__(self):
		self.resources = []
	def add(self, item):
		self.resources.append(item)
	def write(self, fo):
		idx = 0
		write_node(fo, "resource")
		for res in self.resources:
			res.write(fo, idx)
			idx = idx + 1
		write_node_nl(fo)



## Godot vertex data uses an octahedral compression on normal vectors
def godot_oct_compress(v):
	most = abs(v[0]) + abs(v[1]) + abs(v[2])
	v_x = v[0] / most
	v_y = v[1] / most
	v_z = v[2] / most
	
	if v_z >= 0.0:
		oc_x = v_x
		oc_y = v_y
	else:
		if v_x >= 0.0:
			oc_x_sign = 1.0
		else:
			oc_x_sign = -1.0
		oc_x = oc_x_sign * (1.0 - abs(v_y))
		if v_y >= 0.0:
			oc_y_sign = 1.0
		else:
			oc_y_sign = -1.0
		oc_y = oc_y_sign * (1.0 - abs(v_x))
	oc_x = oc_x * 0.5 + 0.5
	oc_y = oc_y * 0.5 + 0.5
	return (oc_x, oc_y)

