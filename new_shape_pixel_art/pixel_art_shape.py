
##
##  Import Pixel Art as a shape
##  
##  Copyright 2023 Edward Blake
##
##  See the file "LICENSE" for information on usage and redistribution
##  of this file, and for a DISCLAIMER OF ALL WARRANTIES.
##

import w3d_e3d
import w3d_newshape
import sys
from os import path

TRANSPARENT_RED = 254
TRANSPARENT_GREEN = 2
TRANSPARENT_BLUE = 253

def remove_comment(ln):
	wherecomment = ln.find("#")
	if wherecomment == -1:
		return ln
	else:
		return ln[0:wherecomment]

def read_non_blank(fp):
	while True:
		ln = fp.readline().decode('ascii')
		if ln == '':
			return ""
		ln = remove_comment(ln)
		ln = ln.rstrip()
		if ln != "":
			return ln
			
class MatsList:
	def __init__(self):
		self.mats = []

class VerticesAndFaces:
	def __init__(self):
		self.vs = []
		self.fs = []
		self.tx = []

## Read PPM file
def from_ppm(filename):
	fp = open(filename, "rb")
	ppm_sig = read_non_blank(fp) # P3
	if (ppm_sig != 'P3') and (ppm_sig != 'P6'):
		fp.close()
		return (None, None, None)
	width_height_line = read_non_blank(fp) # 32 32
	width_height_line_arr = width_height_line.split(' ')
	ignored_line = read_non_blank(fp) # 255
	width = int(width_height_line_arr[0])
	height = int(width_height_line_arr[1])
	img = []
	if ppm_sig == 'P3':
		for irow in range(0, height):
			l = read_non_blank(fp)
			l2 = l.split(' ')
			row = []
			i2 = 0
			for icol in range(0, width):
				r = int(l2[i2])
				g = int(l2[i2+1])
				b = int(l2[i2+2])
				if not ((r == TRANSPARENT_RED) and (g == TRANSPARENT_GREEN) and (b == TRANSPARENT_BLUE)):
					pixel = (r, g, b)
				else:
					pixel = None
				row.append(pixel)
				i2 = i2 + 3
			img.append(row)
	elif ppm_sig == 'P6':
		for irow in range(0, height):
			row = []
			i2 = 0
			for icol in range(0, width):
				rgb = fp.read(3)
				r = rgb[0]
				g = rgb[1]
				b = rgb[2]
				if not ((r == TRANSPARENT_RED) and (g == TRANSPARENT_GREEN) and (b == TRANSPARENT_BLUE)):
					pixel = (r, g, b)
				else:
					pixel = None
				row.append(pixel)
			img.append(row)
	fp.close()
	return (width, height, img)

## Read PBM file
def from_pbm(filename):
	fp = open(filename, "rb")
	ppm_sig = read_non_blank(fp) # P3
	if (ppm_sig != 'P1'):
		fp.close()
		return (None, None, None)
	width_height_line = read_non_blank(fp) # 32 32
	width_height_line_arr = width_height_line.split(' ')
	width = int(width_height_line_arr[0])
	height = int(width_height_line_arr[1])
	img = []
	if ppm_sig == 'P1':
		for irow in range(0, height):
			l = read_non_blank(fp)
			l2 = l.split(' ')
			row = []
			i2 = 0
			for icol in range(0, width):
				bit = int(l2[i2])
				if bit == 1:
					pixel = (180, 180, 180)
				else:
					pixel = None
				row.append(pixel)
				i2 = i2 + 1
			img.append(row)
	fp.close()
	return (width, height, img)

## Read PGM file
def from_pgm(filename):
	fp = open(filename, "rb")
	ppm_sig = read_non_blank(fp) # P3
	if (ppm_sig != 'P2') and (ppm_sig != 'P5'):
		fp.close()
		return (None, None, None)
	width_height_line = read_non_blank(fp) # 32 32
	width_height_line_arr = width_height_line.split(' ')
	ignored_line = read_non_blank(fp) # 255
	width = int(width_height_line_arr[0])
	height = int(width_height_line_arr[1])
	img = []
	if ppm_sig == 'P2':
		for irow in range(0, height):
			l = read_non_blank(fp)
			l2 = l.split(' ')
			row = []
			i2 = 0
			for icol in range(0, width):
				r = int(l2[i2])
				g = int(l2[i2])
				b = int(l2[i2])
				if not ((r == TRANSPARENT_RED) and (g == TRANSPARENT_GREEN) and (b == TRANSPARENT_BLUE)):
					pixel = (r, g, b)
				else:
					pixel = None
				row.append(pixel)
				i2 = i2 + 1
			img.append(row)
	elif ppm_sig == 'P5':
		for irow in range(0, height):
			row = []
			i2 = 0
			for icol in range(0, width):
				rgb = fp.read(1)
				r = rgb[0]
				g = rgb[0]
				b = rgb[0]
				if not ((r == TRANSPARENT_RED) and (g == TRANSPARENT_GREEN) and (b == TRANSPARENT_BLUE)):
					pixel = (r, g, b)
				else:
					pixel = None
				row.append(pixel)
			img.append(row)
	fp.close()
	return (width, height, img)


def read_emboss_icon(filename):
	ext = filename[-4:]
	if ext == '.ppm':
		(width, height, img) = from_ppm(filename)
	elif ext == '.pgm':
		(width, height, img) = from_pgm(filename)
	elif ext == '.pbm':
		(width, height, img) = from_pbm(filename)
	else:
		raise Exception("Unknown format")
	mats = MatsList()
	emit_poly_materials(mats)
	ply = VerticesAndFaces()
	ply.offset = 0
	
	on_base = False
	
	for irow in range(0, height):
		for icol in range(0, width):
			emit_poly_pixel(icol,irow,img[irow][icol], on_base, ply)
	
	return (ply, mats)
	
def rv(l):
	l.reverse()
	return l
	
def plp(xo, yo, x, y, z):
	return ((xo * 2.0 + 1.0 * x, 1.0 * y, -(yo * 2.0 + 1.0 * z)))


def emit_poly_pixel(x, y, color, on_base, ply):
	if color == None:
		if on_base:
			ply.vs.append(plp(x, y, -1.0, -1.0, -1.0))
			ply.vs.append(plp(x, y, 1.0, -1.0, -1.0))
			ply.vs.append(plp(x, y, 1.0, -1.0, 1.0))
			ply.vs.append(plp(x, y, -1.0, -1.0, 1.0))
			## If it is on a base, fill in something here
			ply.fs.append((None, [ply.offset + 0, ply.offset + 1, ply.offset + 2, ply.offset + 3]))
			ply.offset += 4
	else:
		(r, g, b) = color
		r0 = r / 255.0
		g0 = g / 255.0
		b0 = b / 255.0
		ir = int(r0 * 3)
		ig = int(g0 * 3)
		ib = int(b0 * 3)
		p = (ib * 3 * 3 + ig * 3 + ir)
		mname = "Material0" + str(p)
		
		ply.vs.append(plp(x, y, -1.0, 1.0, -1.0))
		ply.vs.append(plp(x, y, 1.0, 1.0, -1.0))
		ply.vs.append(plp(x, y, 1.0, 1.0, 1.0))
		ply.vs.append(plp(x, y, -1.0, 1.0, 1.0))
		ply.vs.append(plp(x, y, -1.0, -1.0, -1.0))
		ply.vs.append(plp(x, y, 1.0, -1.0, -1.0))
		ply.vs.append(plp(x, y, 1.0, -1.0, 1.0))
		ply.vs.append(plp(x, y, -1.0, -1.0, 1.0))
		ply.fs.append((mname, [ply.offset + 0, ply.offset + 1, ply.offset + 2, ply.offset + 3]))
		ply.fs.append((mname, [ply.offset + 7, ply.offset + 6, ply.offset + 5, ply.offset + 4]))
		ply.fs.append((mname, [ply.offset + 0, ply.offset + 0+4, ply.offset + 1+4, ply.offset + 1]))
		ply.fs.append((mname, [ply.offset + 1, ply.offset + 1+4, ply.offset + 2+4, ply.offset + 2]))
		ply.fs.append((mname, [ply.offset + 2, ply.offset + 2+4, ply.offset + 3+4, ply.offset + 3]))
		if not on_base:
			## If it is not on a base, make a bottom face for the box
			ply.fs.append((mname, [ply.offset + 3, ply.offset + 3+4, ply.offset + 0+4, ply.offset + 0]))
		
		ply.offset += 8


def emit_poly_materials(mats):
	for ib in range(0, 3):
		for ig in range(0, 3):
			for ir in range(0, 3):
				p = (ib * 3 * 3 + ig * 3 + ir)
				newmat = w3d_e3d.Material()
				newmat_gl = w3d_e3d.MaterialOpenGLAttributes()
				newmat_gl.ambient = [ir * 0.5, ig * 0.5, ib * 0.5, 1.0]
				newmat_gl.specular = [0.2, 0.2, 0.2, 0.7]
				newmat_gl.shininess = 0.4
				newmat_gl.diffuse = [ir * 0.5, ig * 0.5, ib * 0.5, 1.0]
				newmat_gl.emission = [0.0,0.0,0.0,1.0]
				newmat_gl.metallic = 0.1
				newmat_gl.roughness = 0.8
				newmat_gl.vertex_colors = 'set'
				newmat.attrs['opengl'] = newmat_gl
				newmat.name = "Material0" + str(p)
				mats.mats.append(newmat)

def emboss_icon(filename, attr):
	objname = path.splitext(path.basename(filename))[0]
	
	(ply, mats) = read_emboss_icon(filename)
	vs = ply.vs
	faces = ply.fs
	
	efs = []
	for (mname, indices) in faces:
		face = w3d_e3d.E3DFace()
		face.vs = indices
		if mname != None:
			face.mat.append(mname)
		efs.append(face)
	
	mesh = w3d_e3d.E3DMesh()
	mesh.type="polygon"
	mesh.vs=vs
	mesh.fs=efs
	
	e3d_o = w3d_e3d.E3DObject()
	e3d_o.obj = mesh
	
	print("")
	nshp = w3d_newshape.NewShape()
	nshp.prefix = objname
	nshp.obj = e3d_o
	for m in mats.mats:
		nshp.mat.append(m)
	o = nshp.as_output_list()
	o.write_list_out(sys.stdout)


filename = extra_params["icon"]
emboss_icon(filename, {})
