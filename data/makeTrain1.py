import os, glob, random;
from PIL import Image
from skimage import img_as_float,color
import numpy as np
import scipy.io as sio
from matplotlib import pyplot as plt

dirName = 'raw/train';
outFolder = 'random/train';

if not os.path.exists('random/train'):
    os.makedirs('random/train')
listOfFolders = os.listdir(dirName)
i =0
for folder in listOfFolders:
	f = os.path.join(dirName,folder)
	# print(f)
	names = []

	for file in os.listdir(f):
		if file.endswith("jpg"):
			if file!='thumb.jpg':
				names.append(file)	

	randomNums = random.sample(range(0,24), 2)
		# print(randomNums)
								
	while randomNums[0] == randomNums[1]:
		randomNums[1] = random.sample(range(0,24))
	image1 = os.path.join(f, names[randomNums[0]])
	image2 = os.path.join(f, names[randomNums[1]])
	image1 = Image.open(image1)
	image2 = Image.open(image2)
	image1 = image1.resize((256, 256))
	image2 = image2.resize((256, 256))
	
	im1 = color.rgb2xyz(image1)
	im2 = color.rgb2xyz(image2)

	imag = (im1 + im2)/2
	imag = color.xyz2rgb(imag)
	imag = img_as_float(imag)

	matName = str(i)+".mat"
	width , height = image1.size
	im1 = np.zeros([width,height,3],dtype=np.float)
	im2 = np.zeros([width,height,3],dtype=np.float)
	chrom = np.zeros([width,height,3],dtype=np.float)
	mask = np.zeros([width,height,3],dtype=np.float)
	mask.fill(1)

	completeName = os.path.join(outFolder, matName)   
	sio.savemat(completeName , {'img1':img1,'img2':img2, 'imag':imag, 'im1': im1, 'im2':im2, 'chrom':chrom, 'mask':mask})
	i = i+1
	print(i)		
