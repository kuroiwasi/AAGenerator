import sys, os, cv2
import numpy as np

def makeWeightMatrix(alpha):
	arr = np.array([[0 for i in range(16)] for j in range(16)])
	arr = np.array(arr, dtype=np.float32)
	for y in range(0,16):
		for x in range(0,16):
			b = int(np.sqrt(x**2.0+y**2.0))
			c = 1.0/(np.sqrt(2.0*np.pi))*np.exp(-(b*alpha)**2.0/2.0)
			arr[y,x] = c

	arr = arr/np.max(arr)
	return arr

def makeEdgeImage(src):
	img = ~cv2.Canny(src, 100, 200)
	return img

#kernprof.py -l -v aa.py [input] [output]
#python -m line_profiler hoge.py.lprof
#@profile
def processing():
	# make project directory
	os.mkdir("projects\\"+sys.argv[2])
	# load character image
	chartable = np.load("data\\mspgothic_800.npy")
	# load space of each characters
	spaces = np.load("data\\mspgothic_space_800.npy")
	# load base image and copy
	inputimg = cv2.imread("img\\"+sys.argv[1])
	cv2.imwrite("projects\\"+sys.argv[2]+"\\"+sys.argv[2]+".png", inputimg)
	# convert to grayscale
	inputimg = cv2.cvtColor(inputimg, cv2.COLOR_RGB2GRAY)
	# convert to edge image and write
	if len(sys.argv) > 3 and int(sys.argv[3]) > 0 :
		inputimg = makeEdgeImage(inputimg)
		cv2.imwrite("projects\\"+sys.argv[2]+"\\"+sys.argv[2]+"_edge.png", inputimg)

	height, width = inputimg.shape
	# weighting matrix
	weightmat = makeWeightMatrix(0.1)

	for coordY in range(0,(int)(height/16)):
		coordX = 0
		while coordX < width:
			okx=0
			oky=0
			mindeference = 1e+45
			for numy in range(0,spaces.shape[0]):
				for numx in range(0,spaces.shape[1]):
					space = spaces[numy,numx]
					offset = spaces[numy:numy+1,0:numx].sum()

					# clipping
					imgfrag = inputimg[coordY*16:(coordY+1)*16, coordX:coordX+space]
					charimg = chartable[numy*16:(numy+1)*16, offset:offset+space]

					# GaussianBlur
					csize = np.int32(np.sqrt(space)) + 1
					csize += 1 - csize % 2
					imgfrag =  cv2.GaussianBlur(imgfrag,(csize,csize),0)
					charimg = cv2.GaussianBlur(charimg,(csize,csize),0)

					# padding
					a = np.array([[255]*(16-charimg.shape[1])]*16)
					b = np.array([[255]*(16-imgfrag.shape[1])]*16)
					charimg = np.concatenate((charimg, a), axis=1)
					imgfrag = np.concatenate((imgfrag, b), axis=1)

					# DCT
					imgfrag = cv2.dct(np.float32(imgfrag))
					charimg = cv2.dct(np.float32(charimg))

					# update
					#deference = (np.abs(imgfrag - charimg)).sum()
					deference = ((((imgfrag - charimg)*weightmat)**2.0)).sum()
					if deference <= mindeference:
						mindeference = deference
						oky = numy
						okx = numx

			okspace = spaces[oky,okx]
			okoffset = spaces[oky:oky+1,0:okx].sum()
			if coordX + okspace > width:
				break
			inputimg[coordY*16:(coordY+1)*16, coordX:(coordX+okspace)] = chartable[oky*16:(oky+1)*16, okoffset:okoffset+okspace]
			coordX += okspace

	cv2.imwrite("projects\\"+sys.argv[2]+"\\"+sys.argv[2]+"_result.png", inputimg)

def main():
	if len(sys.argv) < 3:
		print ('Usage: # python %s input_file project_name [edge_switch(>0)]' % os.path.basename(sys.argv[0]))
		quit()

	processing()

if __name__ == '__main__':
    main()