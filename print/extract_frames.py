import Image, ImageSequence
import sys
import math
#GIF File name
infile = sys.argv[1]
# Diameter of the wheel in inches
diameter = int(sys.argv[2]) if len(sys.argv) >= 3 else 8
# max frames
maxFramesPerWheel = int(sys.argv[3]) if len(sys.argv) >= 4 else 15
# DPI of the printer, 600 x 600 for HP 9050 (MITPRINT)
dpi = 600

imwidth = diameter * dpi
imheight = diameter * dpi
centerCircle = Image.open("circle.png")
centerCircle = centerCircle.resize((dpi, dpi), Image.ANTIALIAS)
def processGIF(infile):
    images =[]
    try:
        img = Image.open(infile)
    except IOError:
        print "Cant load", infile
        sys.exit(1)

    pal = img.getpalette()
    prev = img.convert('RGBA')
    prev_dispose = True
    for i, frame in enumerate(ImageSequence.Iterator(img)):
        dispose = frame.dispose

        if frame.tile:
            x0, y0, x1, y1 = frame.tile[0][1]
            if not frame.palette.dirty:
                frame.putpalette(pal)
            frame = frame.crop((x0, y0, x1, y1))
            bbox = (x0, y0, x1, y1)
        else:
            bbox = None

        if dispose is None:
            prev.paste(frame, bbox, frame.convert('RGBA'))
            #prev.save(infile[:-4]+'%02d.png' % i)
            prev_dispose = False
            images.append(prev.copy())
        else:
            if prev_dispose:
                prev = Image.new('RGBA', img.size, (0, 0, 0, 0))
            out = prev.copy()
            out.paste(frame, bbox, frame.convert('RGBA'))
            #out.save(infile[:-4]+'%02d.png' % i)
            images.append(out.copy())
    # for x in xrange(len(images)):
    #     img = images[x]
    #     img.save('debug_%02d.png' % x)
    return images

def createWheelIm(frames, imwidth, imheight):
    out=Image.new("RGBA", (imwidth, imheight))
    numFrames = len(frames)
    center=(imwidth/2, imheight/2)

    frameW, frameH = frames[0].size
    rescaleFactor = getMaxSizePerSector(min(imwidth, imheight)/2, frameW, frameH, numFrames)
    frameW *= rescaleFactor
    frameH *= rescaleFactor
    for x in xrange(numFrames):
        angle = x * 360.0/numFrames
        tempIm =frames[x].resize((int(frameW), int(frameH)), Image.ANTIALIAS)
        copyAtAngle(out, tempIm, angle)
    #Add a 1 inch circle in the middle for easy centering

    out.paste(centerCircle, (center[0] - dpi/2, center[1]-dpi/2))
    out.save(infile[:-4]+'_output.png')

def copyAtAngle(out, frame, angle):
    frameW, frameH = frame.size
    dim = math.sqrt(frameW**2 + frameH**2)
    rotatedIm = Image.new("RGBA", (int(dim), int(dim)))
    rotatedIm.paste(frame, (int((dim - frameW)/2), int((dim - frameH)/2)))
    rotatedIm=rotatedIm.rotate(-angle)
    #.paste(frame.rotate(-angle))#.transform((imwidth, imheight), Image.AFFINE, (cos(angle), sin(angle), 0, -sin(angle), cos(angle), 0))
    #rotatedIm.save(infile[:-4]+str(angle)+'_rotated.png')

    # Figure out something with placement
    center=(out.size[0]/2, out.size[1]/2)
    point = (out.size[0]/2, dim/2)
    coord = rotatePoint(center, point, angle)
    #coord is at the center of the image -> move to top left
    coord = int(coord[0] -dim/2), int(coord[1]-dim/2)

    #mask = createMask(out, rotatedIm, coord, angle)
    out.paste(rotatedIm, coord, rotatedIm.split()[-1])

    #print center, point, imwidth, imheight, dim
    #print rotatePoint(center, point, 90, int(out.size[0]-dim), int(out.size[1]-dim))


'''
this should be fine...
p'x = cos(theta) * (px-ox) - sin(theta) * (py-oy) + ox
p'y = sin(theta) * (px-ox) + cos(theta) * (py-oy) + oy
'''
def rotatePoint(centerPoint,point,angle):
    """Rotates a point around another centerPoint. Angle is in degrees.
    Rotation is counter-clockwise"""
    angle = math.radians(angle)
    temp_point = point[0]-centerPoint[0] , point[1]-centerPoint[1]
    temp_point = ( temp_point[0]*math.cos(angle)-temp_point[1]*math.sin(angle) , temp_point[0]*math.sin(angle)+temp_point[1]*math.cos(angle))
    temp_point = int(temp_point[0]+centerPoint[0]) , int(temp_point[1]+centerPoint[1])
    return temp_point

#number = num frames, everything else in pixels or whatever, same units
def getMaxSizePerSector(radius, width, height, number):
    dim = math.sqrt(width**2 + height**2)
    angle = math.pi/number
    opposite = math.cos(angle)*radius
    ans = (2 * math.tan(angle) * opposite / dim) / (1 + (2*math.tan(angle)*dim/dim))
    return ans

images = processGIF(infile)
if len(images) > maxFramesPerWheel:
    images = images[0:maxFramesPerWheel]
# print len(images), maxFramesPerWheel
createWheelIm(images, imwidth, imheight)
