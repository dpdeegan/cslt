'''
plan area update script
'''

import arcpy, time
tic = time.clock()
arcpy.env.overwriteOutput = True

#input FCs:
parcels = r'J:\GIS files\CSLT.gdb\parcelTEST\Parcels_Aug2015_backup'
planAreaFC = r'J:\GIS files\CSLT.gdb\PlanArea\CSLT_Plan_Areas_2014'

#dictionary:
planDict = {
    "PAS_NAME" : "Plan_Area",
    "PAS" : "PAS",
    "SPEC_AREA" : "Spec_Area",
    "CSLT_LU" : "CSLT_LU",
    "TRPA_LU" : "TRPA_LU",
    "ZONING_Dis" : "Zoning_Dis",
    "ZONING_Nam" : "Zoning_Name"
}

rowsupdated = 0
totaldiff = 0

arcpy.MakeFeatureLayer_management(planAreaFC, "planArea_lyr")
arcpy.MakeFeatureLayer_management(parcels, "parcels_lyr")

planFields = list(planDict.keys())
parcelFields = list(planDict.values())
print planFields

with arcpy.da.SearchCursor("planArea_lyr", planFields) as cursor:
    c = 0
    field_counted = 0
    parcel_counted = 0
    #fieldcount = len(planFields)
    for row in cursor:
        print "_" * 10
        c += 1
        arcpy.MakeFeatureLayer_management("planArea_lyr", "planAreaCursor_lyr")
        arcpy.SelectLayerByLocation_management("parcels_lyr", "HAVE_THEIR_CENTER_IN", "planAreaCursor_lyr")
        parcelCount = arcpy.GetCount_management("parcels_lyr")
        print "plan area row %s has %s parcels" % (c, parcelCount)
        parcel_counted += int(parcelCount.getOutput(0))
        for i in range(len(planFields)):
            field_counted += 1
            print "%s : %s  has value %s" % (planFields[i], parcelFields[i], row[i])
    totalrows = c
del cursor, row
toc = time.clock()
elapsed = toc - tic

print "\r---------\r%d rows %d fields for %d parcels in %d seconds\rDONE" % (totalrows, field_counted, parcel_counted, elapsed)
