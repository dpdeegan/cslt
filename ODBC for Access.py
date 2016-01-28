##import arcpy
##
##accessdb = r'C:\GIS\InspectionForm.accdb'
##
##arcpy.env.workspace = accessdb
##
##print arcpy.ListTables()
#you must have pyodbc for python 2.7 32 bit
import pyodbc

print "start"

#for connection string help see: http://www.connectionstrings.com/access/
#note: some of their capitalization is not correct. directory does not need to be in its of quotes
#this is a single string

dbloc = 'C:\GIS\InspectionForm.accdb'

cnxn = pyodbc.connect('Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s'% (dbloc))
print "connected"
cursor = cnxn.cursor()
print "cursor created"

## table testing
#list tables
#for row in cursor.tables(): print row.table_name
#for row in cursor.tables(): print "table {s.table_name} is type {s.table_type}".format(s=row)
#use tables(table_type = TABLE) to get only non system tables
#https://code.google.com/archive/p/pyodbc/wikis/Cursor.wiki

### this creates a dictionary of order of field in access DB, with a tuple of (field name, type, length, alias)
### to be used later to AddField
dict = {}

#examine columns in row cursor
#skip tables that are system, or directly enter the name of the table you are interested in (ideal)

for row in cursor.columns(table='InspectionForm'):
    #print "field name {s.column_name}, data type name is {s.type_name}, size is {s.column_size} order is {s.ordinal_position}".format(s=row)   ##for testing
    key = row.ordinal_position
    remark = row.remarks
    #print remark   #not sure if row.remarks needs to be a variable... but i am attempting to remove unicode shit later, which might not matter
    ##skip auto generated ID field in DB. We just want to get field names. GIS has OBJECTID
    if row.type_name == 'COUNTER': alias = ""
    else:
        #enc = remark
        #alias = enc.encode('ascii', 'ignore').decode('ascii')
        alias = row.remarks.split(chr(0), 1)[0]
    #print alias    #for testing
    vals = (row.column_name , row.type_name , row.column_size, alias)
    dict[key] = vals

##print output as key (values tuple)
##for testing stop here and call values as dict[key] for your tuple testing
for key in dict:
    print key, dict[key]
#AddField needs "Name", "Type", field_length="" (for text), 

##for key in dict:
##    tup = dict[key]
##    for i in range(4):
##        print tup[i]

##
#cleaned = row and row.remarks.split(chr(0), 1)[0] or None
    #https://code.google.com/archive/p/pyodbc/issues/56


