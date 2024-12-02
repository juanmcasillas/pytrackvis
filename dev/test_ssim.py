import cv2
#import numpy as np
#from skimage.metrics import structural_similarity

import sys

# https://forum.opencv.org/t/using-opencv-for-image-similarity/6444/12
# https://stackoverflow.com/questions/11541154/checking-images-for-similarity-with-opencv

# same tracks
# Similarity Score: 99.159%
#first = cv2.imread('ssim/5E/B5/5eb58f600fb9dc31731ca9847de11e5e.png', cv2.IMREAD_GRAYSCALE)
#second = cv2.imread('ssim/19/CD/19cdbc746fc63a8a3a4a31269eca796b.png', cv2.IMREAD_GRAYSCALE) # 0

files = [
    'ssim/5E/B5/5eb58f600fb9dc31731ca9847de11e5e.png',
    'ssim//19/CD/19cdbc746fc63a8a3a4a31269eca796b.png',
    'ssim//30/2C/302c834a206c355d9bbebcec290d87e8.png',
    'ssim//33/77/3377a4675696eaa6baa5e0f4e4053fb1.png',
    'ssim//59/E0/59e0b8e4bc17a35b12edd844f0f02556.png',
    'ssim//AB/AD/abad55d5a513175ba71ff01681a245c7.png',
    'ssim//B1/0E/b10eb17ba74f7467aeceb369a927c966.png',
    'ssim//B1/4E/b14e9b3c487a4a268f4716cb54101d22.png',
    'ssim//BC/65/bc65956fe0ca247075daf1e681fed219.png',
    'ssim//C0/D3/c0d341a80f52f7ce439dc180d158d562.png',
    'ssim//CD/EF/cdef2ee7d9a67535fd973f3fe0832f4f.png',
    'ssim//DC/2D/dc2db22527f309a1b4bd5c11dc80c3aa.png',
    'ssim//EA/B6/eab65c2c7bb21651154ffecee9fd59f4.png'
]

first = cv2.imread( files[0], cv2.IMREAD_GRAYSCALE )
for i in range(1,len(files)):
    second = cv2.imread( files[i], cv2.IMREAD_GRAYSCALE )
    pts_a = cv2.findNonZero(first)
    pts_b = cv2.findNonZero(second)
    hd = cv2.createHausdorffDistanceExtractor()
    d1 = hd.computeDistance(pts_a, pts_b)
    print("error (lower, better): %3.2f  f1:%s / f2:%s" % (d1,files[0], files[i]))

sys.exit(0)

# different tracks
# Similarity Score: 88.583%
#second = cv2.imread('ssim/59/E0/59e0b8e4bc17a35b12edd844f0f02556.png', cv2.IMREAD_GRAYSCALE) # 55.71355438232422
#second = cv2.imread('ssim/AB/AD/abad55d5a513175ba71ff01681a245c7.png', cv2.IMREAD_GRAYSCALE) # 2
# second = cv2.imread('ssim/CD/EF/cdef2ee7d9a67535fd973f3fe0832f4f.png', cv2.IMREAD_GRAYSCALE) # 60.16643524169922
#second = cv2.imread('ssim/EA/B6/eab65c2c7bb21651154ffecee9fd59f4.png', cv2.IMREAD_GRAYSCALE) # 27.294687271118164
# Convert images to grayscale
#first_gray = cv2.cvtColor(first, cv2.COLOR_BGR2GRAY)
#second_gray = cv2.cvtColor(second, cv2.COLOR_BGR2GRAY)

pts_a = cv2.findNonZero(first)
pts_b = cv2.findNonZero(second)

hd = cv2.createHausdorffDistanceExtractor()
d1 = hd.computeDistance(pts_a, pts_b)
print(d1)
sys.exit(0)


# Compute SSIM between two images
score, diff = structural_similarity(first_gray, second_gray, full=True)
print("Similarity Score: {:.3f}%".format(score * 100))

# The diff image contains the actual image differences between the two images
# and is represented as a floating point data type so we must convert the array 
# to 8-bit unsigned integers in the range [0,255] before we can use it with OpenCV
diff = (diff * 255).astype("uint8")

# Threshold the difference image, followed by finding contours to
# obtain the regions that differ between the two images
thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
contours = contours[0] if len(contours) == 2 else contours[1]

# Highlight differences
mask = np.zeros(first.shape, dtype='uint8')
filled = second.copy()

for c in contours:
    area = cv2.contourArea(c)
    if area > 100:
        x,y,w,h = cv2.boundingRect(c)
        cv2.rectangle(first, (x, y), (x + w, y + h), (36,255,12), 2)
        cv2.rectangle(second, (x, y), (x + w, y + h), (36,255,12), 2)
        cv2.drawContours(mask, [c], 0, (0,255,0), -1)
        cv2.drawContours(filled, [c], 0, (0,255,0), -1)

#cv2.imshow('first', first)
#cv2.imshow('second', second)
#cv2.imshow('diff', diff)
cv2.imshow('mask', mask)
#cv2.imshow('filled', filled)
cv2.waitKey()