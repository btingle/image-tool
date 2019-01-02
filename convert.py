import argparse, re, math
from PIL import Image

# scale : (%X, %Y)
# pixels : (X, Y)
# area : (A)
def get_mode(r_str):
	resize = r_str.split("x")
	xmode = None
	ymode = None
	xmod = None
	ymod = None
	if len(resize) == 1:
		if "%" in resize[0]:
			xmode = "scale"
			xmod  = int(resize[0].strip("%")) / 100
			ymode = xmode
			ymod  = xmod
		else:
			xmode = "area"
			xmod  = int(resize[0])
			ymode = xmode
			ymod  = xmod
	elif len(resize) == 2:
		if "%" in resize[0]:
			xmode = "scale"
			xmod  = int(resize[0].strip("%")) / 100
		else:
			xmode = "pixels"
			xmod  = int(resize[0])
		if "%" in resize[1]:
			ymode = "scale"
			ymod  = int(resize[1].strip("%")) / 100
		else:
			ymode = "pixels"
			ymod  = int(resize[1])
	else:
		print("Too many arguments!")
	return xmode, xmod, ymode, ymod

ext_dict = {".jpg":"JPEG", ".png":"PNG", ".gif":"GIF", ".ppm":"PPM", ".tiff":"TIFF", ".tif":"TIFF"}
def get_extension_type(filename):
	ext_search = re.match(".*(?P<ext>\.\w+)$", filename)
	if ext_search:
		ext = ext_search.group(1)
		return ext_dict[ext]
	else:
		return "JPEG"

if __name__ == "__main__":
	parser = argparse.ArgumentParser(prog="PROG", description="Resize and convert images", add_help=True)
	parser.add_argument("infile")
	parser.add_argument("outfile")
	parser.add_argument("-r", "--resize", metavar="WxH, N%, W%xH%, AREA", dest="r",
			    help="Resize image, specify dimensions, percentage, or desired area. Pixels and percentage can be mixed, e.g: H%%xW.")
	parser.add_argument("--preserve", action="store_true", default=False, help="Preserve image aspect ratio, pads image if this is not possible. Defaults to false.")
	parser.add_argument("-p", metavar="WxH", default=False, help="Pad out image to specified size.")
	parser.add_argument("-c", metavar="0xFFFFFF", default="0x000000", help="Sets padding color. Defaults to black")
	args = parser.parse_args()
	if not (args.r or args.p):
		print("Please select an image operation")
		exit(0)
	image = None
	try:
		image = Image.open(args.infile)
	except Exception as e:
		print(str(e))
		exit(0)
	ext = get_extension_type(args.outfile)
	if args.r:
		xmode, xmod, ymode, ymod = None, None, None, None
		try:
			xmode, xmod, ymode, ymod = get_mode(args.r)
		except:
			print("Invalid dimensions syntax")
			exit(0)
		xdim = image.size[0]
		ydim = image.size[1]
		if xmode == "scale":
			xdim *= xmod
		if xmode == "pixels":
			xdim  = xmod
		if ymode == "scale":
			ydim *= ymod
		if ymode == "pixels":
			ydim  = ymod
		if xmode == "area":
			scale = math.sqrt((xdim * ydim) / xmod)
			xdim /= scale
			ydim /= scale
		# expands the image as much as it can into transformed canvas, while preserving aspect ratio
		if(args.preserve):
			# constrained by which component needs to be scaled down the most to fit the canvas
			origx = image.size[0]
			origy = image.size[1]
			scale = xdim / origx if (xdim / origx) < (ydim / origy) else ydim / origy
			newx  = int(origx * scale)
			newy  = int(origy * scale)
			image = image.resize((newx, newy), Image.ANTIALIAS)
			# finally, converts original dimensions to int (size only accepts integer parameters)
			xdim  = int(xdim)
			ydim  = int(ydim)
			padim = Image.new("RGB", size=(xdim, ydim), color=int(args.c, 16))
			padim.paste(image, box=(int((xdim - newx)/2), int((ydim - newy)/2)))
			image = padim
		else:
			xdim  = int(xdim)
			ydim  = int(ydim)
			image = image.resize((xdim, ydim), Image.ANTIALIAS)
	if(args.p):
		# creates a padding canvas to paste image into, pastes into the center no matter what, ignoring if edges get cropped
		padx  = int(args.p.split("x")[0])
		pady  = int(args.p.split("x")[1])
		padim = Image.new("RGB", size=(padx, pady), color=int(args.c, 16))
		padim.paste(image, box=(int((padx - xdim)/2), int((pady - ydim)/2)))
		image = padim
	image.save(args.outfile, format=ext)
