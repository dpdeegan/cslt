import arcpy, datetime, os
print "starting Parcel Update"

arcpy.env.overwriteOutput = True

#this environment is very important because it makes sure the names of the output fields dont contain the name of
#to origin table. 
arcpy.env.qualifiedFieldNames = False

from datetime import datetime
##returns a string of day, Month, second to be added to file to make a unique name
## returns _DDMMMss. as file + addMDs() to add timestamp to item. ex _16Dec195509
def addMDs():
    today = datetime.today()
    return today.strftime("_%d%b%H%M%S")
def timeStamp():
    today = datetime.today()
    return today.strftime("time is: %H:%M.%S")
print timeStamp()

#input feature classes. this can be changed to getparametersastext if needed
#new variables to hold dirs and names will be needed for toolbox
#
#update the following fields
#
coreParcels = r'J:\GIS files\GIS_DATA\Parcels\Parcel.gdb\county\EDC_dec15_1'    #core parcels from county 
existParcels = r'J:\GIS files\GIS_DATA\Parcels\Parcel.gdb\current\Parcels_Sept2015'    #existing parcels in use by the city
#updatedParcels = r'J:\GIS files\GIS_DATA\Parcels\Parcel.gdb\current\slt_EDCprcl2015Aug'  #name of outputFC that has new core parcels. not currently used
boundary = r'J:\GIS files\GIS_DATA\Parcels\Parcel.gdb\CSLTboundary'             #city boundary

backupdir = r'J:\GIS files\GIS_DATA\Parcels\Parcel.gdb\backup'     #for retaining old FC's
outputdir = r'J:\GIS files\GIS_DATA\Parcels\Parcel.gdb\output'      #location of outputs
final = r'J:\GIS files\GIS_DATA\Parcels\Parcel.gdb\results'     #location of final updated parcel layer
joinfield = "PRCL_ID"                                           #this will probably never change

# make lists of field name for input fc's
coreList = [f.name for f in arcpy.ListFields(coreParcels)]
parcelList = [f.name for f in arcpy.ListFields(existParcels)]

#for testing to see the number of fields in both inputs
print len(coreList)
print len(parcelList)

#create a fieldinfo object for all the of field in the city input layer
cityfieldinfo = arcpy.FieldInfo()

#if the fieldname is unique to the city, i don't want to hide it
for field in parcelList:
    if field == "PRCL_ID":
        cityfieldinfo.addField(field, field, "VISIBLE", "")  #keep the PRCL_ID field for the join later
    elif field in coreList:
        cityfieldinfo.addField(field, field, "HIDDEN", "")  #if it is a field in the core parcel, hide it
    else:
        cityfieldinfo.addField(field, field, "VISIBLE", "") #otherwise it is unique and need to be kept.

#time to make feature layers, join, and featureclasstofeatureclass
##first create new coreparcels in city
print "starting parcel update..."
sql = "PRCL_ID = '990' OR PRCL_ID = '991'"   #this will remove features with PRCL_IDs that indicate roads and are repeated IDs
sqlnot = "PRCL_ID <> '990' OR PRCL_ID <> '991'" #this is used on the existing parcel to select everything other than the above
desc = arcpy.Describe(coreParcels)      #kept for now
timeCore = addMDs()                     #stores the time code for the start of this process, used later

#create new coreParcels: selecting by location
arcpy.MakeFeatureLayer_management(coreParcels, "coreParcels_lyr")
arcpy.MakeFeatureLayer_management(boundary, "boundary_lyr")
arcpy.SelectLayerByLocation_management("coreParcels_lyr", "HAVE_THEIR_CENTER_IN", "boundary_lyr")
print len("coreParcels_lyr")
arcpy.SelectLayerByAttribute_management ("coreParcels_lyr", "REMOVE_FROM_SELECTION", sql )#removes features we don't need
#export result, we might want just the core city parcels later
#
#new data created below
#
arcpy.CopyFeatures_management("coreParcels_lyr", outputdir + "\\Parcels_CSLTcore" + timeCore)
##might want to make name of output a variable
print "new EDC parcels in CSLT boundary have been created"

#create table of old CSLT fields, using field info to make only city fields visible
arcpy.MakeFeatureLayer_management(existParcels, "existParcels_lyr", "", "", cityfieldinfo)

arcpy.SelectLayerByAttribute_management ("existParcels_lyr", "ADD_TO_SELECTION", sqlnot )#removes features we don't need, type changes to 'ADD_TO_SELECTION'
#arcpy.FeatureClassToFeatureClass_conversion("existParcels_lyr", backupdir, "CSLTexist"+timeCore)   #i tried this with field maps and it failed
#
#new data created below
#
arcpy.TableToTable_conversion("existParcels_lyr", r'J:\GIS files\GIS_DATA\Parcels\Parcel.gdb', "CSLT_Parcel"+timeCore)
print "existing parcels with unique fields only have been backed up"

#arcpy.MakeFeatureLayer_management(backupdir + "\\CSLTexist" + timeCore, "CSLTexist_lyr", "", "", fieldinfoHidden)      #deleted for field map fail
arcpy.AddJoin_management("coreParcels_lyr", "PRCL_ID", r'J:\GIS files\GIS_DATA\Parcels\Parcel.gdb'+ "\\CSLT_Parcel"+timeCore, "PRCL_ID")

#new data created below: if you want to change the name of the output or its location, do it here

arcpy.CopyFeatures_management("coreParcels_lyr", final + "\\Parcels_CSLT_new" + "_final")
#arcpy.FeatureClassToFeatureClass_conversion("coreParcels_lyr", outputdir + "\\Parcels_CSLT_new" + timeCore, fieldmappings)
print "CSLT parcels have been updated with new EDC parcel core"
print len("coreParcels_lyr")
updatefieldslist = [f.name for f in arcpy.ListFields("coreParcels_lyr")]
print "updated parcels field count:  " +str(len(updatefieldslist))
final = final + "\\Parcels_CSLT_new" + "_final"
print int(arcpy.GetCount_management(final).getOutput(0))
#clean up output

print "script finished"
print "You can find your new parcel layer in J:\GIS files\GIS_DATA\Parcels\Parcel.gdb\results' as Parcels_CSLT_new_final"
print "---------------------------------------------------------------------------"
print timeStamp()
