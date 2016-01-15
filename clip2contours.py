#create contours for area of interest
#just change the input parameters for the inBoundary (area of interest)
#change the buffDistance to increase/decrease the buffer size. 

import arcpy, time, os
from arcpy.sa import *

tic = time.clock()
localtime = time.asctime( time.localtime(time.time()) )
print "\rGO!\rScript started at Local current time :", localtime

#inputs and parameters
inBoundary = r'J:\GIS files\CSLT.gdb\ProjectAreas\knightsInn'
inDEM = r'J:\GIS files\GIS_DATA\DEM\output_be.tif'
##outContour = r'J:\GIS files\GIS_DATA\DEM\contour_1ft_CSLT.shp'     #name created in script
contourinterval = 1             #integer, is 1ft
zFactor = 3.2808                #integer. if dem is in m and you want ft, keep this
buffDist = "100 Feet"           #must be in format: "### Unit"

#env
arcpy.env.overwriteOutput = True

#describe objects
desc = arcpy.Describe(inBoundary)
descDEM = arcpy.Describe(inDEM)

#run buffer (optional)

#creates fc in memory default is 100 ft
outBuffname = desc.name.strip(".shp") + "_buff"
#print "outBuffname is %s" % outBuffname

arcpy.Buffer_analysis(inBoundary, os.path.join("in_memory" , outBuffname), buffDist)
print "in memory buffer created\r clipping...."

#run clip

outDir = os.path.join(descDEM.path , "Clip")

if not os.path.exists(outDir):
    os.makedirs(outDir)
    print "dir {} created.".format(outDir)

descBuff = arcpy.Describe("in_memory\\" + outBuffname)

#frame is string that describes a rectangle in this order:
#X-Minimum, Y-Minimum, X-Maximum, Y-Maximum ***no commas***
#e.XMin is a parameter of the object desc.extent
frame = "{e.XMin} {e.YMin} {e.XMax} {e.YMax}".format(e=descBuff.extent)
print "frame is %s" % frame

#create unique name that is full path of output., 6 chars of DEM, 6 chars of boundary, .tif
#the name of the file is held in the second variable and used later
arcpy.env.workspace = outDir
unique_name = arcpy.CreateUniqueName("{}_{}.tif".format(descDEM.name[:6], desc.name[:6]))
unique_nameFILE = "{d[1]}".format(d=os.path.split(unique_name))

print "unique_name is %s" % unique_name

arcpy.Clip_management(inDEM,\
                      frame,\
                      unique_name,\
                      os.path.join("in_memory", outBuffname),\
                      "-3.402823e+038",\
                      "ClippingGeometry",\
                      "NO_MAINTAIN_EXTENT")
print "clipped DEM created"
print time.asctime( time.localtime(time.time()) )

#start of contour. this can take 5-15 minutes depending on file size
try:
    #check in spatial analyst, if available
    if arcpy.CheckExtension("Spatial") == "Available":
        arcpy.AddMessage("Checking out Spatial Analyst")
        arcpy.CheckOutExtension("Spatial")
        print "spatial analyst checked out"
    else:
        arcpy.AddError("could not check out spatial analyst")
        arcpy.AddMessage(arcpy.GetMessages(0))
        print "spatial analyst check out failed, is not available"

    outContDir = os.path.join(descDEM.path, "Contour")
    print "outContDir is %s" % outContDir
    
    if not os.path.exists(outContDir):
        os.makedirs(outContDir)
        print "%s dir created" % outContDir

    #unique_Cont_name = arcpy.CreateUniqueName(os.path.join(outContDir, "{}_{}".format(
    arcpy.env.workspace = outContDir
    #name of contour is based on clipped DEM
    uniqueCont_name = arcpy.CreateUniqueName("{}_{}ft.shp".format(unique_nameFILE.strip(".tif"),contourinterval))
    print "uniqeCont_name is %s" % uniqueCont_name
    print time.asctime( time.localtime(time.time()) )

    #create in memory raster for faster processing
    tempRas = arcpy.Raster(unique_name)
    #run contour tool. arcpy.sa is not needed because it was done earlier
    arcpy.sa.Contour(unique_name, uniqueCont_name, contourinterval, "", zFactor)

    del tempRas
    print "Contours created!!! at {}".format(time.asctime( time.localtime(time.time()) ))
    #print time.asctime( time.localtime(time.time()) )
except:
    print "something went wrong"
    print (arcpy.GetMessages())

#check sa back in
arcpy.CheckInExtension("Spatial")
print "--------------\rspatial analyst checked back in\r-------------"

#clear in_memory
arcpy.Delete_management("in_memory\\" + outBuffname)
arcpy.Delete_management("in_memory\\" + unique_name)
print "in_memory buffer deleted"

toc = time.clock()
elapsed = toc-tic
print "tool completed in %d seconds" % elapsed

'''

for future: label contours as being minor(5) or major (10)
add fields: minor, major, label (text, 3)

Use this functoin to populate major/minor fields. This is how it would appear in ArcMap field calculator window
For feature classes where null is OK, remove else: statement.
To change it to major contours (10) change to % 10

def class( x):
    if x % 10 == 0:
        return "major"
    elif x % 5 == 0:
        return "minor"
    else:
        return "na"
        
class = isfive(!CONTOUR!)

'''
