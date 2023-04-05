
##
##  Panda3D Nodes
##  
##  Copyright 2023 Edward Blake
##
##  See the file "LICENSE" for information on usage and redistribution
##  of this file, and for a DISCLAIMER OF ALL WARRANTIES.
##

def str_indent(indent):
	return indent * "  "

class Tangent:
	def __init__(self, x,y,z):
		self.x = x
		self.y = y
		self.z = z
	def wr_out(self, indent, fo):
		fo.write(str_indent(indent) + "<Tangent> { " + str(self.x) + " " + str(self.y) + " " + str(self.z) + " }\n")

class Binormal:
	def __init__(self, x,y,z):
		self.x = x
		self.y = y
		self.z = z
	def wr_out(self, indent, fo):
		fo.write(str_indent(indent) + "<Binormal> { " + str(self.x) + " " + str(self.y) + " " + str(self.z) + " }\n")

class Normal:
	def __init__(self, x,y,z):
		self.x = x
		self.y = y
		self.z = z
	def wr_out(self, indent, fo):
		fo.write(str_indent(indent) + "<Normal> { " + str(self.x) + " " + str(self.y) + " " + str(self.z) + " }\n")

class RGBA:
	def __init__(self, r,g,b,a):
		self.r = r
		self.g = g
		self.b = b
		self.a = a
	def wr_out(self, indent, fo):
		fo.write(str_indent(indent) + "<RGBA> { " + str(self.r) + " " + str(self.g) + " " + str(self.b) + " " + str(self.a) + " }\n")
		
class Scalar:
	def __init__(self, nm, cont):
		self.name = nm
		self.content = cont
	def wr_out(self, indent, fo):
		fo.write(str_indent(indent) + "<Scalar> " + self.name + " { " + self.content + " }\n")

class TRef:
	def __init__(self, cont):
		self.content = cont
	def wr_out(self, indent, fo):
		fo.write(str_indent(indent) + "<TRef> { " + self.content + " }\n")

class MRef:
	def __init__(self, cont):
		self.content = cont
	def wr_out(self, indent, fo):
		fo.write(str_indent(indent) + "<MRef> { " + self.content + " }\n")

class CoordinateSystem:
	def wr_out(self, indent, fo):
		fo.write(str_indent(indent) + "<CoordinateSystem> { Y-Up }\n")

class Comment:
	def __init__(self, text):
		self.comment = text
	def wr_out(self, indent, fo):
		fo.write(str_indent(indent) + "<Comment> {\n")
		fo.write(str_indent(indent) + "  \"" + self.comment.replace("\\", "\\\\").replace("\"", "\\\"") + "\"\n")
		fo.write(str_indent(indent) + "}\n")

class Texture:
	def __init__(self, nm, texfile):
		self.name = nm
		self.fname = texfile
		self.format = "rgba"
		self.alpha_file = None
		self.wrapu = "repeat"
		self.wrapv = "repeat"
		self.minfilter = "linear_mipmap_linear"
		self.magfilter = "linear"
		self.envtype = None
	def wr_out(self, indent, fo):
		indent_1 = indent + 1
		fo.write(str_indent(indent) + "<Texture> " + self.name + " {\n")
		fo.write(str_indent(indent_1) + "" + self.fname + "\n")
		Scalar("format", self.format).wr_out(indent_1, fo)
		if self.alpha_file != None:
			Scalar("alpha-file", self.alpha_file).wr_out(indent_1, fo)
		Scalar("wrapu", self.wrapu).wr_out(indent_1, fo)
		Scalar("wrapv", self.wrapv).wr_out(indent_1, fo)
		Scalar("minfilter", self.minfilter).wr_out(indent_1, fo)
		Scalar("magfilter", self.magfilter).wr_out(indent_1, fo)
		if self.envtype != None:
			Scalar("envtype", self.envtype).wr_out(indent_1, fo)
		fo.write(str_indent(indent) + "}\n")

class Material:
	def __init__(self, nm):
		self.name = nm
		self.ambient = (0.0,0.0,0.0,0.0)
		self.diffuse = (0.0,0.0,0.0,0.0)
		self.emission = (0.0,0.0,0.0,0.0)
		self.specular = (0.0,0.0,0.0,0.0)
		self.shininess = 0.0
	
	def wr_out(self, indent, fo):
		indent_1 = indent + 1
		fo.write(str_indent(indent) + "<Material> " + self.name + " {\n")
		(diffr, diffg, diffb, diffa) = self.diffuse
		Scalar("diffr", str(diffr)).wr_out(indent_1, fo)
		Scalar("diffg", str(diffg)).wr_out(indent_1, fo)
		Scalar("diffb", str(diffb)).wr_out(indent_1, fo)
		Scalar("diffa", str(diffa)).wr_out(indent_1, fo)
		(ambr, ambg, ambb, amba) = self.ambient
		Scalar("ambr", str(ambr)).wr_out(indent_1, fo)
		Scalar("ambg", str(ambg)).wr_out(indent_1, fo)
		Scalar("ambb", str(ambb)).wr_out(indent_1, fo)
		Scalar("amba", str(amba)).wr_out(indent_1, fo)
		(emitr, emitg, emitb, emita) = self.emission
		Scalar("emitr", str(emitr)).wr_out(indent_1, fo)
		Scalar("emitg", str(emitg)).wr_out(indent_1, fo)
		Scalar("emitb", str(emitb)).wr_out(indent_1, fo)
		Scalar("emita", str(emita)).wr_out(indent_1, fo)
		(specr, specg, specb, speca) = self.specular
		Scalar("specr", str(specr)).wr_out(indent_1, fo)
		Scalar("specg", str(specg)).wr_out(indent_1, fo)
		Scalar("specb", str(specb)).wr_out(indent_1, fo)
		Scalar("speca", str(speca)).wr_out(indent_1, fo)
		Scalar("shininess", str(self.shininess)).wr_out(indent_1, fo)

		fo.write(str_indent(indent) + "}\n")

class Group:
	def __init__(self, nm):
		self.name = nm
		self.list = []
	def wr_out(self, indent, fo):
		indent_1 = indent + 1
		fo.write(str_indent(indent) + "<Group> " + self.name + " {\n")
		for e in self.list:
			e.wr_out(indent_1, fo)
		fo.write(str_indent(indent) + "}\n")
	def add(self, it):
		self.list.append(it)
	
class UV:
	def __init__(self, u1, v1):
		self.u = u1
		self.v = v1
		self.tangent = None
		self.binormal = None
	def wr_out(self, indent, fo):
		indent_1 = indent + 1
		fo.write(str_indent(indent) + "<UV> {\n")
		fo.write(str_indent(indent_1) + "" + str(self.u) + " " + str(self.v) + "\n")
		if self.tangent != None:
			self.tangent.wr_out(indent_1, fo)
		if self.binormal != None:
			self.binormal.wr_out(indent_1, fo)
		fo.write(str_indent(indent) + "}\n")
	
class Vertex:
	def __init__(self, x, y, z):
		self.x = x
		self.y = y
		self.z = z
		self.uv = UV(0, 0)
		self.normal = Normal(0, 0, 0)
		self.rgba = RGBA(1, 1, 1, 1)
	def wr_out(self, indent, fo, idx):
		indent_1 = indent + 1
		fo.write(str_indent(indent) + "<Vertex> " + str(idx) + " {\n")
		fo.write(str_indent(indent_1) + "" + str(self.x) + " " + str(self.y) + " " + str(self.z) + "\n")
		if self.uv != None:
			self.uv.wr_out(indent_1, fo)
		if self.normal != None:
			self.normal.wr_out(indent_1, fo)
		if self.rgba != None:
			self.rgba.wr_out(indent_1, fo)
		fo.write(str_indent(indent) + "}\n")
	
class VertexPool:
	def __init__(self, nm):
		self.name = nm
		self.verts = []
	def wr_out(self, indent, fo):
		indent_1 = indent + 1
		fo.write(str_indent(indent) + "<VertexPool> " + self.name + " {\n")
		idx = 0
		for v in self.verts:
			v.wr_out(indent_1, fo, idx)
			idx = idx + 1
		fo.write(str_indent(indent) + "}\n")
	def add(self, it):
		self.verts.append(it)
		
class Ref:
	def __init__(self, cont):
		self.content = cont
	def wr_out(self, indent, fo):
		fo.write("<Ref> { " + self.content + " }")
	
		
class VertexRef:
	def __init__(self, l):
		self.list = l
		self.ref = Ref(None)
	def wr_out(self, indent, fo):
		indent_1 = indent + 1
		one_line_only = True
		if len(self.list) > 10:
			one_line_only = False
		fo.write(str_indent(indent) + "<VertexRef> {")
		if not one_line_only:
			fo.write("\n" + str_indent(indent_1))
		for v in self.list:
			fo.write(" " + str(v))
		if not one_line_only:
			fo.write("\n" + str_indent(indent_1))
		else:
			fo.write(" ")
		self.ref.wr_out(0, fo)
		if not one_line_only:
			fo.write("\n")
			fo.write(str_indent(indent) + "}\n")
		else:
			fo.write(" }\n")

class Polygon:
	def __init__(self, vlist, vlistref, texs=[]):
		self.normal = None
		self.trefs = texs
		self.vref = VertexRef(vlist)
		self.vref.ref = vlistref
	def wr_out(self, indent, fo):
		indent_1 = indent + 1
		fo.write(str_indent(indent) + "<Polygon> {\n")
		if self.normal != None:
			self.normal.wr_out(indent_1, fo)
		for tr in self.trefs:  ## TRef and MRef list
			tr.wr_out(indent_1, fo)
		self.vref.wr_out(indent_1, fo)
		fo.write(str_indent(indent) + "}\n")

class EggFile:
	def __init__(self):
		self.list = []
	def add(self, it):
		self.list.append(it)
	def write_to(self, fo):
		for it in self.list:
			it.wr_out(0, fo)
