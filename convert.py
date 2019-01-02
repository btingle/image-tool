import argparse, re, math
from PIL import Image

HEIGHT = None
WIDTH = None

# breaks down expression string into a number string
def do_math(exp_string):
	operators = ["+","-","*","/"]
	exp_string = exp_string.replace("H", str(HEIGHT))
	exp_string = exp_string.replace("W", str(WIDTH))
	level = 0
	maxlv = 0
	number = True
	if exp_string[0] == "(" and exp_string[-1] == ")":
		exp_string = exp_string[1:-1]
	for i in range(len(exp_string)):
		level += 1 if exp_string[i] == "(" else 0
		level -= 1 if exp_string[i] == ")" else 0
		maxlv = level if level > maxlv else maxlv
		if level == 0 and exp_string[i] in operators:
			number = False
			left = do_math(exp_string[:i])
			right = do_math(exp_string[i+1:])
			exp_string = left + exp_string[i] + right
			break
	op = None
	oi = None
	exp_string = exp_string.strip("()")
	for i in range(len(exp_string)):
		if exp_string[i] in operators:
			op = exp_string[i]
			oi = i
			break
	exp_string = exp_string.strip(op)
	if not op:
		return exp_string
	L = int(exp_string[:oi])
	R = int(exp_string[oi+1:])
	if op == "+":
		return str(L + R)
	if op == "*":
		return str(L * R)
	if op == "/":
		return str(L // R)
	if op == "-":
		return str(L - R)

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
			xmod  = int(do_math(resize[0].strip("%"))) / 100
			ymode = xmode
			ymod  = xmod
		else:
			xmode = "area"
			xmod  = int(do_math(resize[0]))
			ymode = xmode
			ymod  = xmod
	elif len(resize) == 2:
		if "%" in resize[0]:
			xmode = "scale"
			xmod  = int(do_math(resize[0].strip("%"))) / 100
		else:
			xmode = "pixels"
			xmod  = int(do_math(resize[0]))
		if "%" in resize[1]:
			ymode = "scale"
			ymod  = int(do_math(resize[1].strip("%"))) / 100
		else:
			ymode = "pixels"
			ymod  = int(do_math(resize[1]))
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
	parser = argparse.ArgumentParser(prog="PROG", 
		description="Resize and convert images.\n"
			   +"Numerical parameters can take the form of basic mathematical expressions, with single arithmetical operators, parentheses, and builtin variables H and W for Height and Width of input image.", add_help=True)
	parser.add_argument("infile")
	parser.add_argument("outfile", nargs="?")
	parser.add_argument("-r", "--resize", metavar="WxH, N%, W%xH%, AREA", dest="r", help="Resize image, specify dimensions, percentage, or desired area. Pixels and percentage can be mixed, e.g: H%%xW.")
	parser.add_argument("-s", "--preserve", action="store_true", default=False, help="Preserve image aspect ratio, pads image if this is not possible. Defaults to false.")
	parser.add_argument("-p", "--pad", metavar="WxH", default=False, dest="p", help="Pad out image to specified size.")
	parser.add_argument("-d", "--dimensions", action="store_true", default=False, dest="d", help="Print dimensions of image file")
	parser.add_argument("-x", "--crop", metavar="X:Y", nargs=2, help="Specify top left and bottom right corners of the bounding box you want to crop to.", dest="x")
	parser.add_argument("-c", "--color", metavar="0xFFFFFF", default="0x000000", help="Sets padding color. Defaults to black")
	args = parser.parse_args()

	image = None
	try:
		image = Image.open(args.infile)
	except Exception as e:
		print(str(e))
		exit(0)
	if args.d:
		print("Dimensions, X:" + str(image.size[0]) + ", Y:" + str(image.size[1]))
		exit(0)
	if not (args.r or args.p or args.x):
		print("Please select an image operation")
		exit(0)
	ext = get_extension_type(args.outfile)
	print("Starting dimensions, X:" + str(image.size[0])+ ", Y:" + str(image.size[1]))
	WIDTH  = image.size[0]
	HEIGHT = image.size[1]
	if args.r:
		xmode, xmod, ymode, ymod = None, None, None, None
		try:
			xmode, xmod, ymode, ymod = get_mode(args.r)
		except Exception as e:
			print("Invalid dimensions syntax!")
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
	if args.p:
		# creates a padding canvas to paste image into, pastes into the center no matter what, ignoring if edges get cropped
		padx  = int(do_math(args.p.split("x")[0]))
		pady  = int(do_math(args.p.split("x")[1]))
		padim = Image.new("RGB", size=(padx, pady), color=int(args.c, 16))
		padim.paste(image, box=(int((padx - xdim)/2), int((pady - ydim)/2)))
		image = padim
	if args.x:
		left  = int(do_math(args.x[0].split(":")[0]))
		upper = int(do_math(args.x[0].split(":")[1]))
		right = int(do_math(args.x[1].split(":")[0]))
		lower = int(do_math(args.x[1].split(":")[1]))
		image = image.crop(box=(left, upper, right, lower))
	print("Changed dimensions, X:" + str(image.size[0]) + ", Y:" + str(image.size[1]))
	image.save(args.outfile, format=ext)
