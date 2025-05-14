#!/usr/bin/env python
'''
BCS Hibernacula Location Buffering Script

Code block to be called within an AcrPro tool box that will take Geospatial Interface (GI) Vizualtiation 
product and create buffers based on the Bat Conservation Strategy (BCS) for Hibernaculas, Roosts, and Maternity Captures.

**Prerequisite:**
Ssers must us the GI in ArcMap to pull the WL data via BCS GI workflow to create 
two points layers, Sites and Observations.  
Those two layers will be entered into the python script toll in ArcPro for processing.  
Users will also need to select an output workspace.


**Definitions:**
MYSO = Indiana Bat (Myotis sodalis)
PESU = Tri-colored Bat (Perimyotis subflavaus) previously called Eastern Pipistrelle (Pipestrelle subflavaus)
MYLYU = Little Brown Bat (Myotis lucifugus)
MYSE = Northern Long-eared Bat (Myotis septentrionalis)


**Buffer Distance Conversion mile to feet:**
0.25 miles = 1,320 feet 
0.85 miles = 4,488 feet
2 miles =  10,560 feet
5 miles =  26,400 feet


**Species and Abundance Thresholds:**
*Primary Hibernaculum Buffer, Secondary Hibernaculum Buffer, & Tertiary Hibernaculum Buffers:
Indiana bat and/or Little brown bat (combined count)—High Abundance: (>= 5,000 bats)
500 feet, 2 miles, 5 miles

Indiana bat + Little brown bat (combined count)—Moderate Abundance: (20-4,900 bats)
500 feet, 2 miles, None

Indiana bat + Little brown bat (combined count)—Low Abundance: (1-19 bats)
500 feet, None, None

Northern long-eared bat (external count) or Tricolored bat—High Abundance: (>= 20)
500 feet, 0.25 mile, 0.85 mile

Northern long-eared bat (external count) or Tricolored bat—Moderate Abundance: (10-19 bats)
500 feet, 0.25 mile, None

Northern long-eared bat (external count) or Tricolored bat—Low Abundance: (1-9 bats)
500 feet, None, None

Northern long-eared bat (internal count)—High Abundance: (>= 5 bats)
None, 0.25 mile, 0.85 mile

Northern long-eared bat (internal count)—Moderate Abundance: (1-4 bats)
None, 0.25 mile, None

Northern long-eared bat (internal count)—Low Abundance: (NA bats)
None, None, None

Hibernaculum with Unknown Abundance:
500 feet, 0.25 mile, 0.85 mile


*Primary (Suitable) Roost & Secondary Roost Buffers:
Indiana bat and/or Little brown bat:
150 feet, 9,504 feet

Northern long-eared bat:
150 feet, 1,320 feet

Tricolored bat:
150 feet, 300 feet


*Maternity Capture Buffers:
Indiana bat and/or Little brown bat:
9,504 feet

Northern long-eared bat or Tricolored bat:
3,960 feet


**Snag TimeFrame:**
10 years = 3650 days


** Field Names in GI Output Vizualtiations ***
* Site GI Output Fields:
['OBJECTID', 'SHAPE', 'SHAPE_ORIG', 'OBJECTID_SHP', 'SITE_CN', 
'SITE_NAME', 'SITE_COMMON_NAME', 'SITE_SCIENTIFIC_NAME', 'SITE_TAXON_LEVEL', 
'ORIGINATOR_NAME', 'SITE_CATEGORY', 'SITE_ESTABLISHED_DATE', 'SITE_TYPE', 
'SITE_DATA_ORIGIN', 'SITE_ORIGIN', 'SITE_ORIGIN_METHOD', 'EXEMPT_FROM_PUBLIC', 
'SITE_LOCAL_ID', 'SITE_REFERENCE', 'SITE_COMMENTS', 'VISIT_CN', 'VISIT_START_DATE', 
'VISIT_END_DATE', 'VISIT_DATE_MMDD', 'VISITOR', 'VISIT_SITE_CONDITION', 
'VISIT_SITE_STATUS', 'BIOLOGICAL_SITE_USE', 'VISIT_LOCAL_ID', 'VISIT_COMMENTS', 
'ASSOCIATED_SURVEY_NAME', 'OBS_CN', 'OBS_METHOD_TYPE', 'OBS_COMMON_NAME', 
'OBS_SCIENTIFIC_NAME', 'CLASS_NAME', 'LEGEND_CLASS_NAME', 'OBS_COUNT', 
'INDIV_CN', 'INDIVIDUALS', 'AGE', 'GENDER', 'ACTIVITY', 'INDIV_COMMENTS', 
'SITE_GEOMETRY_TYPE', 'SITE_GIS_ACRES', 'FS_UNIT_ID', 'FS_UNIT_NAME', 
'REPRO_STATUS', 'LONGITUDE', 'LATITUDE', 'ORIG_FID']

* Capture GI Output Fields:
['OBJECTID', 'SHAPE', 'SHAPE_ORIG', 'OBJECTID_SHP', 'OBS_CN', 
'BA_SOURCE', 'TAXON_LEVEL', 'SCIENTIFIC_NAME', 'COMMON_NAME', 
'CLASS_NAME', 'LEGEND_CLASS_NAME', 'OBS_INCIDENTAL', 'SITE_NAME', 
'SITE_TYPE', 'LAST_VISIT_SITE_STATUS', 'LAST_VISIT_SITE_CONDITION', 
'YEAR_TYPE', 'OBS_YEAR', 'OBS_DATE', 'OBS_METHOD', 'GROUP_TYPE', 
'REPRODUCTIVE_STATUS', 'OBS_COMMENTS', 'OBS_COUNT', 'INDIVIDUALS', 
'AGE', 'GENDER', 'ACTIVITY', 'INDIV_COMMENTS', 'TAXA_STATUS', 
'SPATIAL_ID', 'EXEMPT_FROM_PUBLIC', 'FS_UNIT_ID', 'FS_UNIT_NAME', 
'CENTROID_LON', 'CENTROID_LAT', 'ORIG_FID']



**WorkFlow:**
1: get the Site and Capture data layer from the user, as well as workspace to put spatial products
2: create copy to the datsets to work from, maintaining integrity of parent data layers
3: add new fields to the new feature classes/feature layers
4: start processing the hiberncaula data
5: start processing the roost data
6: start processing the capture date
7: generate the buffer polygon layer

'''

#add Arc Message
arcpy.AddMessage("Starting the script")
arcpy.AddMessage("Import modules and packages")

#import modules and packages
import arcpy, arcgis, pandas as pd, os, fnmatch, re
from arcpy import env
from datetime import datetime, timedelta

#Common Header Information
__author__ = "Philip Marley"
__copyright__ = "R9 IM"
__credits__ = "Philip Marley, Jeff Erwin, & Walker Johnson"
__license__ = "NA"
__version__ =  "0.0.1"
__maintainer__ = " Jeffery Erwin, Philip Marley, & Walker Johnson"
__email__ = "jeffery.erwin@usda.gov, philip.marley@usda.gov, george.w.johnson@usda.gov"
__status__ = "Dev"

#add Arc Message
arcpy.AddMessage("Setting env settings")

#add Arc Message
arcpy.AddMessage("Setting hardcoded values")

''' Set/define hardcoded global values '''
#Species Variables
MYSE = "Myotis septentrionalis"
MYSO = "Myotis sodalis"
MYLU = "Myotis lucifugus"
PESU = ["Perimyotis subflavus", "Pipistrellus subflavus"] # in case the taxa list isnt updated
BATS = "Chiroptera"

#Hibernacula Buffers
hbPrimary = "500 Feet" # 500 feet
hbSecondary1 = "1320 Feet" # 1,320 feet | .25 miles
hbSecondary2 = "10560 Feet" # 10,560 feet | 2 miles
hbTertiary1 = "4488 Feet" # 4,488 feet | 0.85 miles
hbTertiary2 = "26400 Feet" # 26,400 feet | 5 miles

#Roost Buffers
rbPrimary = "150 Feet"
rbPESU = "300 Feet"
rbMYSE = "1320 Feet"
rbMYSO = rbMYLU = "3696 Feet"

#Capture Buffers
cbPESU = cbMYSE = "3960 Feet"
cbMYSO = cbMYLU = "9540 Feet"

#Determine Current Date
currentDate = datetime.now()

#Define White Nose Syndrome(WNS) Detection Dates Dictionary.  Based on BCS Document Table D-1 with addition of R8 and R9 to handle errors
wns_dict = {'0903':'2015',
            '0904':'2016',
            '0905':'2016',
            '0907':'2017',
            '0908':'2016',
            '0909':'2016',
            '0910':'2016',
            '0912':'2014',
            '0913':'2015',
            '0914':'2015',
            '0915':'2016',
            '0919':'2014',
            '0920':'2011',
            '0921':'2011',
            '0922':'2014',
            '0801':'2016',
            '0802':'2014',
            '0803':'2015',
            '0804':'2013',
            '0805':'NA',
            '0806':'NA',
            '0807':'NA',
            '0808':'2013',
            '0809':'NA',
            '0810':'NA',
            '0811':'NA',
            '0812':'NA',
            '0813':'NA',
            '0816':'NA',
            '0860':'2013',
            '09':'2021',
            '08':'ERR'
           }

#Dictionary to hold Roost Data for processing
roSpecies_dict = {}

#Set GIS Queries in hardcoded
pyqryHibernacula = "BIOLOGICAL_SITE_USE = 'Hibernating'"
pyqryRoost = "BIOLOGICAL_SITE_USE = 'Perch or Roost'"
pyqrySiteCatBio = "SITE_CATEGORY = 'Biological' and OBS_SCIENTIFIC_NAME in ('Myotis septentrionalis','Myotis sodalis', 'Myotis lucifugus', 'Perimyotis subflavus', 'Pipistrellus subflavus', 'Chiroptera')"
pyqryCapture = "SCIENTIFIC_NAME in ('Myotis septentrionalis','Myotis sodalis', 'Myotis lucifugus', 'Perimyotis subflavus', 'Pipistrellus subflavus') and OBS_METHOD in ('In Hand', 'Visual')"


''' End Global Varibles '''


''' Get Data and Make Copies '''
#Add Arc Message
arcpy.AddMessage("Setting User Inputed Values")

#Define User User Input Values from ArcPro Python Script tool parameters
roostHibDataNRM = arcpy.GetParameterAsText(0) #Roost/Site NRM GI Data Layer
captureDataNRM = arcpy.GetParameterAsText(1)  #Capture/Observation NRM GI Data Layer
workspace = arcpy.GetParameterAsText(2)       #Set FGDB to output all temp and final data output layers

#Set ArcPro Enviromental Settings
#Overwite output, add layers to the map, set workspace
arcpy.env.overwriteOutput = True
arcpy.addOutputsToMap = True
arcpy.env.workspace = workspace

#Add Arc Message
arcpy.AddMessage("Defined Workspace = {}".format(arcpy.env.workspace))

#Export User Inputed Layers to Maintain Integrity of Original Dataset
captureDataExport = str(arcpy.env.workspace + "\\captureDataLayer") #create export path
rstHibDataExport = str(arcpy.env.workspace + "\\rstHibDataLayer") #create export path
bufferDataExport = str(arcpy.env.workspace + "\\BCSBuffers_" + currentDate.strftime("%d%b%Y")) #create export path
arcpy.conversion.ExportFeatures(roostHibDataNRM, rstHibDataExport, pyqrySiteCatBio) #export Roost & Hibernacula Data to new layer
arcpy.conversion.ExportFeatures(captureDataNRM, captureDataExport, pyqryCapture)  #export capture data to new layer


#Create New Feature Layers from the newly exported data layers (from user inputed GI data)
arcpy.management.MakeFeatureLayer(rstHibDataExport,"HibData", pyqryHibernacula) #Hibernacula Layer
arcpy.management.MakeFeatureLayer(rstHibDataExport,"RoostData", pyqryRoost) #Roost Layer
arcpy.management.MakeFeatureLayer(captureDataExport,"CaptureData") #Capture Layer

#Create new feature class to store individual lines data to create poly buffers from
#get the spatial reference from the Hibernacula data layer
sR = arcpy.Describe(rstHibDataExport).spatialReference 
arcpy.management.CreateFeatureclass(arcpy.env.workspace,'ptBufferFC','POINT', spatial_reference=sR)

''' End Get Data and Make New Layers ''' 

''' Add fields to Feature Layers and Feature Classes'''
arcpy.AddMessage("Adding fields to FCs")

#Add fields to the exported data layers
#Add fields to rstHibDataLayer which replicates to the Hib and Roost Feature Layers
arcpy.management.AddFields(rstHibDataExport,[['Historic','TEXT','',10],
                                    ['VisitNum','TEXT','',5], 
                                    ['PrePostWNS','TEXT','',10],
                                    ['haMYSE','DOUBLE'],
                                    ['haPESU','DOUBLE'],
                                    ['haMYSO','DOUBLE'],
                                    ['haMYLU','DOUBLE'],
                                    ['haCOMB','DOUBLE'],
                                    ['haBATS','DOUBLE'],
                                    ['SnagDays','DOUBLE'],
                                    ['SnagProcess','TEXT', '', 5],
                                    ['Maternity', 'TEXT', '', 5]
                                    ])
                                    
#Add field to capture data layer
arcpy.management.AddFields(captureDataExport,[['PrePostWNS','TEXT','',10]
                                    ])
                                   
#Add fiels to the new pt Buffer layer
arcpy.management.AddFields('ptBufferFC',[['Site_CN', 'TEXT'],
                                ['SiteName', 'TEXT'],
                                ['ForestName', 'TEXT'],
                                ['OrgCode','TEXT','',6],
                                ['BufferClass', 'TEXT'],
                                ['BufferType','TEXT'],
                                ['BufferDistance','TEXT', '',20],
                                ['Species', 'TEXT'],
                                ['BufferComments','TEXT'],
                                ['Exempt','TEXT','',5]
                                ])

''' End Add Fields '''

''' Define Functions '''
arcpy.AddMessage("Starting to Define Functions")

#Function to loop through data and determine visit order.  Most recent visit = 1 and sequential in reverse order
def VisitSequence(featureLayer):
        #Create a dictionary to hold the unique combinations and their corresponding dates 
    visit_dict = {} 
     
    # Use a search cursor to iterate through the records and populate the visit_dict 
    with arcpy.da.SearchCursor(featureLayer, ["SITE_CN", "VISIT_START_DATE"]) as cursor: 
        for row in cursor: 
            key = (row[0]) # withCreate a unique key for SITE_CN and VISIT_CN 
            if len(row[1]) == 10:
                visit_date = row[1]
            elif len(row[1]) == 16:
                visit_date = datetime.strptime(row[1],"%Y/%m/%d %H:%M").strftime("%Y/%m/%d") # Get the visit date 
            
     
            # If the key is not in the dictionary, initialize it with an empty list 
            if key not in visit_dict: 
                visit_dict[key] = [] 
     
            if visit_date not in visit_dict[key]:
                # Append the visit date to the corresponding key 
                visit_dict[key].append(visit_date) 
            
    # Create a dictionary to hold the visit order 
    visit_order_dict = {} 

    # Determine the visit order for each unique key 
    for key, dates in visit_dict.items(): 
        # Sort dates in descending order 
        sorted_dates = sorted(dates, reverse=True) 
     
        # Assign visit order starting from 1 for the most recent date 
        for idx, date in enumerate(sorted_dates): 
            visit_order_dict[(key, date)] = idx + 1 # Start counting from 1 
     
    # Update the VisitNum field in the table 
    with arcpy.da.UpdateCursor(featureLayer, ["SITE_CN", "VISIT_START_DATE", "VisitNum"]) as cursor: 
        for row in cursor: 
            if len(row[1]) == 10:
                vsd = row[1]
            elif len(row[1]) == 16:
                vsd = datetime.strptime(row[1],"%Y/%m/%d %H:%M").strftime("%Y/%m/%d") # Get the visit date
            key = (row[0], vsd) # Create the key for the current row 
            if key in visit_order_dict: 
                row[2] = visit_order_dict[key] # Update the VisitNum field 
            cursor.updateRow(row) # Commit changes to the table 

#Function to Loop through data and determine if most recent visit is a Historic Hib or is its Active and Usable
#Inputs (input feature layer for processing)
def HistAct(featureLayer):  
    # Create a dictionary to hold the unique combinations and their corresponding statuses
    hist_dict = {}
    # Use a search cursor to iterate through the records and populate the hist_dict 
    with arcpy.da.SearchCursor(featureLayer, ["SITE_CN", "VISIT_CN", "VisitNum","VISIT_SITE_STATUS","VISIT_SITE_CONDITION"]) as cursor:
        for row in cursor:
            if row[2] == "1":  #determine if the records is the most recent visit.  only process the most recent visit, and ignore the others
                key = row[0], row[1]  #Create a unique key for SITE_CN and VISIT_CN
                if key not in hist_dict:
                    if row[3] == "Inactive" and row[4] == "Usable": # Determine if record is Historic
                        hist_dict[key] = "Hist"
                    elif row[3] == "Active" and row[4] == "Usable": # Determine if record is Active
                        hist_dict[key] = "Act"
                    elif row[4] == "Unusable": # Determine if record is Unsuable
                        hist_dict[key] = "Not"
                    else:                    #Determine if records doesnt meet above criteria
                        hist_dict[key] = "Unkn"
                        
    
    # Update the Historic field in the table 
    with arcpy.da.UpdateCursor(featureLayer, ["SITE_CN", "VISIT_CN", "VisitNum","VISIT_SITE_STATUS","VISIT_SITE_CONDITION","Historic"]) as cursor:
        for row in cursor:
            key = (row[0], row[1])  # Create the key for the current row
            if key in hist_dict:  # process records that the key is found in hist_dict
                row[5] = hist_dict[key]  # Update the Historic field 
            else:   # process records whose key is NOT in hist_dict
                row[5] = "err"  # Update the Historic field 
            cursor.updateRow(row)   # Commit changes to the table

#Function to process data to determine PrePostWNSDates
#Inputs (input feature layer for processing, date field (column) name where the date is stored)
def PrePostWNSDate(featureLayer,vDateLayer):
    
    #Loop through input feature class with update cursor
    with arcpy.da.UpdateCursor(featureLayer,["FS_UNIT_ID", vDateLayer,"PrePostWNS"]) as cursor:
        for row in cursor:
            key = row[0] #org Code
            #determine if org code is in the WNS Date Dictionary
            if key in wns_dict:
                #process if the Org Code has a WNS date
                if wns_dict[key] != "NA" or wns_dict != 'ERR':
                    visit = row[1] #date column
                    vdate = visit[:4] #Year from date column variable
                    wns = wns_dict[key]  #set varibale to year value from the wns dictionary
                    #determine if visit date variable is before the WNS year
                    if vdate < wns:
                        row[2] = "PreWNS"
                    else:
                        row[2] = "PostWNS"
                #Process id the Org Code has no WNS Date
                elif wns_dict == "NA":
                    row[2] = "NoWNS"
            else:
                row[2] = "error"
            cursor.updateRow(row)

#Function to process Hibernacula Data and populate a dictionary with individual counts per species for orgs with no post wns date
def haCountIndividuals():        
    haSpecies_dict = {}     #highest abundance (for orgs with no WNS dates)
    l3Species_dict = {}     #Last 3 visits (for orgs with a WNS date)
    
    value1 = value2 = ''
    #loops through and populate dictionary with species counts
    with arcpy.da.SearchCursor('HibData',["SITE_CN", "VISIT_CN", "OBS_COUNT","OBS_SCIENTIFIC_NAME","FS_UNIT_ID","VisitNum"]) as cursor:
        for row in cursor:
            key = (row[0], row[1])  # Site Cn number & Visit CN number
            if row[2]:
                #process if org code has no wns date.
                if wns_dict[row[4]] == "NA" and len(row[4]) >= 4:
                    #is the key in the haSpecies Dict?
                    if key in haSpecies_dict:
                        if row[3] in PESU:
                            if "PESU" in haSpecies_dict[key]:
                                haSpecies_dict[key]["PESU"] += row[2]
                            else:
                                haSpecies_dict[key]["PESU"] = row[2]
                        elif row[3] == MYSE:
                            if "MYSE" in haSpecies_dict[key]:
                                haSpecies_dict[key]["MYSE"] += row[2]
                            else:
                                haSpecies_dict[key]["MYSE"] = row[2]
                        elif row[3] == MYSO:
                            if "MYSO" in haSpecies_dict[key]:
                                haSpecies_dict[key]["MYSO"] += row[2]
                            else:
                                haSpecies_dict[key]["MYSO"] = row[2]
                        elif row[3] == MYLU:
                            if "MYLU" in haSpecies_dict[key]:
                                haSpecies_dict[key]["MYLU"] += row[2]
                            else:
                                haSpecies_dict[key]["MYLU"] = row[2]
                        elif row[3] == BATS:
                            if "BATS" in haSpecies_dict[key]:
                                haSpecies_dict[key]["BATS"] += row[2]
                            else:
                                haSpecies_dict[key]["BATS"] = row[2]   
                    else:
                        if row[3] in PESU:
                            value1 = {"PESU":row[2]}
                        elif row[3] == MYSE:
                            value1 = {"MYSE":row[2]}
                        elif row[3] == MYSO:
                            value1 = {"MYSO":row[2]}
                        elif row[3] == MYLU:
                            value1 = {"MYLU":row[2]}
                        elif row[3] == BATS:
                            value1 = {"BATS":row[2]}
                                                    
                        if "value1" in locals():
                            haSpecies_dict[key] = value1
                        
                elif wns_dict[row[4]] != "NA" and len(row[4]) >= 4:
                    #print("key:{} | Starting WNS Date process".format(key))
                    if key in l3Species_dict:
                        if row[3] in PESU:
                            if "PESU" in l3Species_dict[key]:
                                if l3Species_dict[key]["PESU"]:
                                    l3Species_dict[key]["PESU"] += row[2]
                            else:
                                l3Species_dict[key]["PESU"] = row[2]
                        elif row[3] == MYSE:
                            if "MYSE" in l3Species_dict[key]:
                                if l3Species_dict[key]["MYSE"]:
                                    l3Species_dict[key]["MYSE"] += row[2]
                            else:
                                l3Species_dict[key]["MYSE"] = row[2]
                        elif row[3] in MYSO:
                            if "MYSO" in l3Species_dict[key]:
                                if l3Species_dict[key]["MYSO"]:
                                    l3Species_dict[key]["MYSO"] += row[2]
                            else:
                                l3Species_dict[key]["MYSO"] = row[2]
                        elif row[3] == MYLU:
                            if "MYLU" in l3Species_dict[key]:
                                if l3Species_dict[key]["MYLU"]:
                                    l3Species_dict[key]["MYLU"] += row[2]
                            else:
                                l3Species_dict[key]["MYLU"] = row[2]  
                        elif row[3] == BATS:
                            if "BATS" in l3Species_dict[key]:
                                if l3Species_dict[key]["BATS"]:
                                    l3Species_dict[key]["BATS"] += row[2]
                            else:
                                 l3Species_dict[key]["BATS"] = row[2]   
                    else:
                        if row[3] in PESU:
                            value2 = {"PESU":row[2]}
                        elif row[3] == MYSE:
                            value2 = {"MYSE":row[2]}
                        elif row[3] == MYSO:
                            value2 = {"MYSO":row[2]}
                        elif row[3] == MYLU:
                            value2 = {"MYLU":row[2]}
                        elif row[3] == BATS:
                            value2 = {"BATS":row[2]}
                            
                        if "value2" in locals():
                            l3Species_dict[key] = value2

   #update cursor           
    with arcpy.da.UpdateCursor('HibData',["SITE_CN", "VISIT_CN", "haMYSE","haPESU","haCOMB","haMYSO","haMYLU","haBATS","PrePostWNS", "FS_UNIT_ID","VisitNum"]) as cursor:
        for row in cursor:
            key = (row[0], row[1])
            if key in haSpecies_dict:
                if 'MYSE' in haSpecies_dict[key]:
                    row[2] = haSpecies_dict[key]['MYSE']
                if 'PESU' in haSpecies_dict[key]:
                    row[3] = haSpecies_dict[key]['PESU']
                if 'MYSO' in haSpecies_dict[key]:
                    row[5] = haSpecies_dict[key]['MYSO']
                if 'MYLU' in haSpecies_dict[key]:
                    row[6] = haSpecies_dict[key]['MYLU']
                if 'BATS' in haSpecies_dict[key]:
                    row[7] = haSpecies_dict[key]['BATS']    
                    
                if 'MYSO' in haSpecies_dict[key] or 'MYLU' in haSpecies_dict[key]:
                    value1C=0
                    if 'MYSO' in haSpecies_dict[key]: 
                        value1C += row[5]
                    if 'MYLU' in haSpecies_dict[key]:
                        value1C += row[6]
                    if value1C >0:
                        row[4] = value1C
                    
                cursor.updateRow(row)  
            elif key in l3Species_dict:
                if 'MYSE' in l3Species_dict[key]:
                    row[2] = l3Species_dict[key]['MYSE']
                if 'PESU' in l3Species_dict[key]:
                    row[3] = l3Species_dict[key]['PESU']
                if 'MYSO' in l3Species_dict[key]:
                    row[5] = l3Species_dict[key]['MYSO']
                if 'MYLU' in l3Species_dict[key]:
                    row[6] = l3Species_dict[key]['MYLU']
                if 'BATS' in l3Species_dict[key]:
                    row[7] = l3Species_dict[key]['BATS'] 
                    
                if 'MYSO' in l3Species_dict[key] or 'MYLU' in l3Species_dict[key]:
                    value2C=0
                    if 'MYSO' in l3Species_dict[key]: 
                        value2C += row[5]
                    if 'MYLU' in l3Species_dict[key]:
                        value2C += row[6]
                    if value2C >0:
                        row[4] = value2C
                    
                cursor.updateRow(row)

#Function to process Hibernacula data to the pt Feature Layer
def ptBufferLayerHib():
    #Define in function variables
    bfHib_dict = {} #Dict to store Hib Buffer Data
    processedList =[] # List to hold unique keys of what has been processed so we arnt double buffering
    row_values=[] # list to store the physical records which will be added to the ptBuffer Layer

    #Search Cursor to loop through Hib data for hibernacula
    with arcpy.da.SearchCursor('HibData',["SITE_CN", "VISIT_CN","VISIT_START_DATE","FS_UNIT_ID",
                                   "EXEMPT_FROM_PUBLIC","VisitNum","Historic","PrePostWNS","haMYSE",
                                   "haPESU","haCOMB","haMYSO","haMYLU","haBATS", "OBS_METHOD_TYPE", 
                                   "VISIT_COMMENTS", "SHAPE@XY", "SITE_NAME", "FS_UNIT_NAME",
                                   "VISIT_SITE_CONDITION", "VISIT_SITE_STATUS"]) as cursor:
        #loop through HibData and populate  dictionary with the site_cn and visit_cn as key, and then values as items from the FC
        for row in cursor:
            key = row[0] #Site Num
            orgC = row[3]
            xy = row[16] #XY Coord Token
            sName = row[17] #SiteName
            forest = row[18]
            
            #loop through records that havnt been processed yet (looking at processedList list)
            if key not in processedList:
            
                #process the historic hib records 
                #where historic records and the visit is most recent 
                if row[6] == "Hist" and row[5] == 1:
                    
                    #SiteCN, SiteName, Forest, OrgCode, BlufferClass, BufferType, BufferDistance, Species, Comments, Exempt, XY Coords(Token)
                    #add row datato the row value list 
                    row_values.append((key, sName, forest, orgC, "Hibernacula", "Historical", 500, "BCS", "", row[4], xy))   
                    
                    #add SiteCN number to the process list
                    processList.append(key)


    #Search Cursor to loop through Hib data of non hibernacula data
    with arcpy.da.SearchCursor('HibData',["SITE_CN", "VISIT_CN","VISIT_START_DATE","FS_UNIT_ID",
                                   "EXEMPT_FROM_PUBLIC","VisitNum","Historic","PrePostWNS","haMYSE",
                                   "haPESU","haCOMB","haMYSO","haMYLU","haBATS", "OBS_METHOD_TYPE", 
                                   "VISIT_COMMENTS", "SHAPE@XY", "SITE_NAME", "FS_UNIT_NAME",
                                   "VISIT_SITE_CONDITION", "VISIT_SITE_STATUS"]) as cursor:
        #loop through HibData and populate  dictionary with the site_cn and visit_cn as key, and then values as items from the FC
        for row in cursor:
            key = row[0] #Site Num
            orgC = row[3]
            xy = row[16] #XY Coord Token
            sName = row[17] #SiteName
            forest = row[18]
            
            #loop through records that havnt been processed yet (looking at processedList list)
            if key not in processedList:
            
                if row[19] == "Usable" and row[20] == "Active":
                                
                    if len(row[3]) >=4 and row[7] != "PreWNS":
                        if key in bfHib_dict:
                            if row[7] == "NoWNS":
                                
                                '''??? should the following elifs under this if statement and the next elif statment be if statements?'''
                                if row[9] is not None:
                                    if 'PESU' in bfHib_dict[key]:
                                        if row[9] > bfHib_dict[key]['PESU']:
                                            bfHib_dict[key]['PESU'] = row[9]
                                    else:
                                        bfHib_dict[key]['PESU'] = row[9]
                                
                                if row[8] is not None:
                                    if 'MYSE' in bfHib_dict[key]: 
                                        if row[8] > bfHib_dict[key]['MYSE']:
                                            bfHib_dict[key]['MYSE'] = row[8]
                                    else:
                                        bfHib_dict[key]['MYSE'] = row[8]
                                if row[10] is not None:
                                    if 'COMB' in bfHib_dict[key]: 
                                        if row[10] > bfHib_dict[key]['COMB']:
                                            bfHib_dict[key]['COMB'] = row[10]
                                    else:
                                        bfHib_dict[key]['COMB'] = row[10]
                                if row[13] is not None:
                                    if 'BATS' in bfHib_dict[key]:
                                        if row[13] > bfHib_dict[key]['BATS']:
                                            bfHib_dict[key]['BATS'] = row[13]
                                    else:
                                        bfHib_dict[key]['BATS'] = row[13]
                            elif row[7] == "PostWNS" and int(row[5]) <= 3:
                                
                                if row[9] is not None:
                                    if 'PESU' in bfHib_dict[key]:
                                        if row[9] > bfHib_dict[key]['PESU']:
                                            bfHib_dict[key]['PESU'] = row[9]
                                    else:
                                        bfHib_dict[key]['PESU'] = row[9]
                                
                                if row[8] is not None:
                                    if 'MYSE' in bfHib_dict[key]: 
                                        if row[8] > bfHib_dict[key]['MYSE']:
                                            bfHib_dict[key]['MYSE'] = row[8]
                                    else:
                                        bfHib_dict[key]['MYSE'] = row[8]
                                if row[10] is not None:
                                    if 'COMB' in bfHib_dict[key]: 
                                        if row[10] > bfHib_dict[key]['COMB']:
                                            bfHib_dict[key]['COMB'] = row[10]
                                    else:
                                        bfHib_dict[key]['COMB'] = row[10]
                                if row[13] is not None:
                                    if 'BATS' in bfHib_dict[key]:
                                        if row[13] > bfHib_dict[key]['BATS']:
                                            bfHib_dict[key]['BATS'] = row[13]
                                    else:
                                        bfHib_dict[key]['BATS'] = row[13]
                        else:
                            
                            if row[2]:
                                bfHib_dict[key] = {'date':row[2]}
                            if row[3]:
                                bfHib_dict[key]['org'] = row[3]                                           
                            if row[4]:
                                bfHib_dict[key]['exempt'] = row[4]
                            if row[5]:
                                bfHib_dict[key]['vnum'] = row[5]
                            if row[6]:
                                bfHib_dict[key]['hist'] = row[6]
                            if row[7]:
                                bfHib_dict[key]['wns'] = row[7]
                            if row[8]:
                                bfHib_dict[key]['MYSE'] = row[8]
                            if row[9]:
                                bfHib_dict[key]['PESU'] = row[9]
                            if row[10]:
                                bfHib_dict[key]['COMB'] = row[10]
                            if row[11]:
                                bfHib_dict[key]['MYSO'] = row[11]
                            if row[12]:
                                bfHib_dict[key]['MYLU'] = row[12]
                            if row[13]:
                                bfHib_dict[key]['BATS'] = row[13]
                            if row[14]:
                                bfHib_dict[key]['OMT'] = row[14] # OBS_METHOD_TYPE field
                            if row[15]:
                                bfHib_dict[key]['VLID'] = row[15] # VISIT_LOCAL_ID field
                            if row[17]:
                                bfHib_dict[key]['name'] = row[17]
                            if row[18]:
                                bfHib_dict[key]['forest'] = row[18]
                            
                            bfHib_dict[key]['XY'] = xy
                            
    #loop through bfHib_dict (which should be a record per site) and process the key values into rews and 
    #append to the row_values list to be proceessed into the new FC    
    for d in bfHib_dict:
        key = d
        orgC = bfHib_dict[d]['org']
        sName = bfHib_dict[d]['name']
        forest = bfHib_dict[key]['forest']
        if 'exempt' in bfHib_dict[d]:
            exempt = bfHib_dict[d]['exempt']
        else:
            exempt = "N"
        #if bfHib_dict[d]['hist']=='Act':
        if 'PESU' in bfHib_dict[d]:
            count = bfHib_dict[d]['PESU']
            if count == 0:
                #SiteCN, SiteName, OrgCode, BlufferClass, BufferType, BufferDistance, Species, Comments, Exempt, XY Coords(Token)
                row_values.append((key, sName, forest, orgC, "Hibernacula", "Primary", hbPrimary, "PESU","", exempt, bfHib_dict[d]['XY']))
                row_values.append((key, sName, forest, orgC, "Hibernacula", "Secondary", hbSecondary1, "PESU", "", exempt, bfHib_dict[d]['XY']))
                row_values.append((key, sName, forest, orgC, "Hibernacula", "Tertiary", hbTertiary1, "PESU", "", exempt, bfHib_dict[d]['XY']))
            if count >= 1:
                row_values.append((key, sName, forest, orgC, "Hibernacula", "Primary", hbPrimary, "PESU","", exempt, bfHib_dict[d]['XY']))
            if count >= 10:
                row_values.append((key, sName, forest, orgC, "Hibernacula", "Secondary", hbSecondary1, "PESU", "", exempt, bfHib_dict[d]['XY']))
            if count >= 20:
                row_values.append((key, sName, forest, orgC, "Hibernacula", "Tertiary", hbTertiary1, "PESU", "", exempt, bfHib_dict[d]['XY']))
            
        if 'MYSE' in bfHib_dict[d]:
            count = bfHib_dict[d]['MYSE']
            if 'VLID' in bfHib_dict[d] and re.search(r'\b' + re.escape("internal") + r'\b',bfHib_dict[d]['VLID'], re.IGNORECASE):#internal count
                if count == 0:
                    #SiteCN, SiteName, OrgCode, BlufferClass, BufferType, BufferDistance, Species, Comments, Exempt, XY Coords(Token)
                    row_values.append((key, sName, forest, orgC, "Hibernacula", "Primary", hbPrimary, "MYSE","", exempt, bfHib_dict[d]['XY']))
                    row_values.append((key, sName, forest, orgC, "Hibernacula", "Secondary", hbSecondary1, "MYSE", "", exempt, bfHib_dict[d]['XY']))
                    row_values.append((key, sName, forest, orgC, "Hibernacula", "Tertiary", hbTertiary1, "MYSE", "", exempt, bfHib_dict[d]['XY']))
            
                if count >= 1:
                    row_values.append((key, sName, forest, orgC, "Hibernacula", "Secondary", hbSecondary1, "MYSE", "", exempt, bfHib_dict[d]['XY']))
                if count >= 5:
                    row_values.append((key, sName, forest, orgC, "Hibernacula", "Tertiary", hbTertiary1, "MYSE", "", exempt, bfHib_dict[d]['XY']))
            else: #external count
                if count == 0:
                    #SiteCN, SiteName, OrgCode, BlufferClass, BufferType, BufferDistance, Species, Comments, Exempt, XY Coords(Token)
                    row_values.append((key, sName, forest, orgC, "Hibernacula", "Primary", hbPrimary, "MYSE","", exempt, bfHib_dict[d]['XY']))
                    row_values.append((key, sName, forest, orgC, "Hibernacula", "Secondary", hbSecondary1, "MYSE", "", exempt, bfHib_dict[d]['XY']))
                    row_values.append((key, sName, forest, orgC, "Hibernacula", "Tertiary", hbTertiary1, "MYSE", "", exempt, bfHib_dict[d]['XY']))
                
                if count >= 1:
                    row_values.append((key, sName, forest, orgC, "Hibernacula", "Primary", hbPrimary, "MYSE","", exempt, bfHib_dict[d]['XY']))
                if count >= 10:
                    row_values.append((key, sName, forest, orgC, "Hibernacula", "Secondary", hbSecondary1, "MYSE", "", exempt, bfHib_dict[d]['XY']))
                if count >= 20:
                    row_values.append((key, sName, forest, orgC, "Hibernacula", "Tertiary", hbTertiary1, "MYSE", "", exempt, bfHib_dict[d]['XY']))
        
        if 'COMB' in bfHib_dict[d]:
            count = bfHib_dict[d]['COMB']
            if count == 0:
                #SiteCN, SiteName, OrgCode, BlufferClass, BufferType, BufferDistance, Species, Comments, Exempt, XY Coords(Token)
                row_values.append((key, sName, forest, orgC, "Hibernacula", "Primary", hbPrimary, "MYSO/MYLU","", exempt, bfHib_dict[d]['XY']))
                row_values.append((key, sName, forest, orgC, "Hibernacula", "Secondary", hbSecondary2, "MYSO/MYLU", "", exempt, bfHib_dict[d]['XY']))
                row_values.append((key, sName, forest, orgC, "Hibernacula", "Tertiary", hbTertiary2, "MYSO/MYLU", "", exempt, bfHib_dict[d]['XY']))
            if count >= 1:
                row_values.append((key, sName, forest, orgC, "Hibernacula", "Primary", hbPrimary, "MYSO/MYLU","", exempt, bfHib_dict[d]['XY']))
            if count >= 20:
                row_values.append((key, sName, forest, orgC, "Hibernacula", "Secondary", hbSecondary2, "MYSO/MYLU", "", exempt, bfHib_dict[d]['XY']))
            if count >= 5000:
                row_values.append((key, sName, forest, orgC, "Hibernacula", "Tertiary", hbTertiary2, "MYSO/MYLU", "", exempt, bfHib_dict[d]['XY']))
            
                
    #insert data from row_values list into the new line feature class
    with arcpy.da.InsertCursor('ptBufferFC', ['Site_CN', 'SiteName', 'ForestName', 'OrgCode', 'BufferClass', 'BufferType', 'BufferDistance', 'Species', 'BufferComments', 'Exempt', 'SHAPE@XY']) as cursor:
        for row in row_values:
            cursor.insertRow(row)

#Function to process Roost data and snags to determine if active snag's most recent visit is less than 10 years, and update FC only if younger than 
def SnagTime():
    
    with arcpy.da.UpdateCursor('RoostData',["VISIT_SITE_CONDITION", "VISIT_START_DATE", "SITE_TYPE", "VISIT_SITE_STATUS", "PrePostWNS", "SnagDays", "SnagProcess"]) as cursor:
        for row in cursor:
            
            if row[0] == "Usable" and row[3] == "Active" and row[2] == "Snag":
                if len(row[1]) == 10:
                    vDate = datetime.strptime(row[1], "%Y/%m/%d")
                elif len(row[1]) == 16:
                    vDate = datetime.strptime(row[1], "%Y/%m/%d %H:%M")
                    
                timeDiff = currentDate - vDate
                
                row[5] = timeDiff.days
                
                if timeDiff <= timedelta(days = 3650):
                    row[6] = "Yes"
                    
                cursor.updateRow(row)

#Function to process Roost data to determine counts
def roCountIndividuals():

    with arcpy.da.SearchCursor('RoostData',["SITE_CN", "VISIT_CN", "OBS_COUNT","OBS_SCIENTIFIC_NAME","FS_UNIT_ID","Historic", "PrePostWNS", "SnagProcess", "SITE_TYPE", "REPRO_STATUS", "VISIT_SITE_CONDITION","VISIT_SITE_STATUS"]) as cursor:
        for row in cursor:
            key = (row[0], row[1])
            if ((row[10] == "Usable" and row[11] == "Active") and row[6] != "PreWNS" and row[8] != "Snag") or ((row[10] == "Usable" and row[11] == "Active") and row[6] != "PreWNS" and row[8] == "Snag" and row[7] == "Yes"):
                
                if key in roSpecies_dict:
                    if row[3] in PESU:
                        if "PESU" in roSpecies_dict[key]:
                            roSpecies_dict[key]["PESU"] += row[2]
                        else:
                            roSpecies_dict[key]["PESU"] = row[2]
                    elif row[3] == MYSE:
                        if "MYSE" in roSpecies_dict[key]:
                            roSpecies_dict[key]["MYSE"] += row[2]
                        else:
                            roSpecies_dict[key]["MYSE"] = row[2]
                    elif row[3] in MYSO:
                        if "MYSO" in roSpecies_dict[key]:
                            roSpecies_dict[key]["MYSO"] += row[2]
                        else:
                            roSpecies_dict[key]["MYSO"] = row[2]
                    elif row[3] == MYLU:
                        if "MYLU" in roSpecies_dict[key]:
                            roSpecies_dict[key]["MYLU"] += row[2]
                        else:
                            roSpecies_dict[key]["MYLU"] = row[2]
                    elif row[3] == BATS:
                        if "BATS" in roSpecies_dict[key]:
                            roSpecies_dict[key]["BATS"] += row[2]
                        else:
                            roSpecies_dict[key]["BATS"] = row[2]   
                else:
                    if row[3] in PESU:
                        value1 = {"PESU":row[2]}
                    elif row[3] == MYSE:
                        value1 = {"MYSE":row[2]}
                    elif row[3] == MYSO:
                        value1 = {"MYSO":row[2]}
                    elif row[3] == MYLU:
                        value1 = {"MYLU":row[2]}
                    elif row[3] == BATS:
                        value1 = {"BATS":row[2]}
                                                
                    if "value1" in locals():
                        roSpecies_dict[key] = value1
                        
                    if row[9] == "Reproducing":
                        roSpecies_dict[key]['Repro'] = "Yes"
                        
    #           
    with arcpy.da.UpdateCursor('RoostData',["SITE_CN", "VISIT_CN", "haMYSE","haPESU","haCOMB","haMYSO","haMYLU","haBATS","PrePostWNS", "FS_UNIT_ID","VisitNum"]) as cursor:
        for row in cursor:
            key = (row[0], row[1])
            if key in roSpecies_dict:
                if 'MYSE' in roSpecies_dict[key]:
                    row[2] = roSpecies_dict[key]['MYSE']
                if 'PESU' in roSpecies_dict[key]:
                    row[3] = roSpecies_dict[key]['PESU']
                if 'MYSO' in roSpecies_dict[key]:
                    row[5] = roSpecies_dict[key]['MYSO']
                if 'MYLU' in roSpecies_dict[key]:
                    row[6] = roSpecies_dict[key]['MYLU']
                if 'BATS' in roSpecies_dict[key]:
                    row[7] = roSpecies_dict[key]['BATS']    
                    
                if 'MYSO' in roSpecies_dict[key] or 'MYLU' in roSpecies_dict[key]:
                    value1C=0
                    if 'MYSO' in roSpecies_dict[key]: 
                        value1C += row[5]
                    if 'MYLU' in roSpecies_dict[key]:
                        value1C += row[6]
                    if value1C >0:
                        row[4] = value1C
                    
                cursor.updateRow(row)  

#Function to process Roost data and populate the maternity field in the roost data layer
def maternityRoost():
    with arcpy.da.UpdateCursor('RoostData',["SITE_CN", "VISIT_CN", "Maternity"]) as cursor:
        for row in cursor:
            key = (row[0], row[1])
            if key in roSpecies_dict and 'Repro' in roSpecies_dict[key]:
                row[2] = "Yes"
                
            cursor.updateRow(row)

#Function to process Roost data to the pt Feature Layer
def ptBufferLayerRoost():
    processedList = [] #list to hold unique processed records
    mList = [] #list to hold which records have reproducing
    row_values = []  #list to hold values to be added to the pt buffer layer

    with arcpy.da.SearchCursor('RoostData', ["SITE_CN", "FS_UNIT_ID", "EXEMPT_FROM_PUBLIC", 
                                            "Historic", "PrePostWNS", "haMYSE", "haPESU", 
                                            "haMYSO", "haMYLU", "SnagProcess", 
                                            "REPRO_STATUS", "SHAPE@XY", "OBS_SCIENTIFIC_NAME", 
                                            "SITE_NAME", "FS_UNIT_NAME", "SITE_TYPE",
                                            "VISIT_SITE_CONDITION", "VISIT_SITE_STATUS"]) as cursor:
        for row in cursor:
            key = row[0]
            key2 = (row[0], row[12])
            orgC = row[1]
            if row[2] is not None:
                if row[2] == "Y":
                    exempt = "Y"
                else:
                    exempt = "N"
            else:
                exempt = "N"
            xy = row[11]
            sName = row[13]
            forest =row[14]
            
            if row[3] == "Act" and row[4] == "PostWNS" and (row[15] != "Snag" or (row[15] == "Snag" and row[9] == "Yes")):
                if key not in processedList:
                    row_values.append((key, sName, forest, orgC, "Roost", "Primary", rbPrimary, "", "", exempt, xy))
                    processedList.append(key)
            
            
            
            
            if any(item is not None for item in (row[5], row[6], row[7], row[8])) and row[16] == "Usable" and row[17] == "Active" and row[4] == "PostWNS" and (row[15] != "Tree" or (row[15] == "Tree" and row[9] == "Yes")):         
                
                if row[10] == "Reproducing" and key2 not in mList:
                    if row[6] is not None:
                        row_values.append((key, sName, forest, orgC, "Roost", "Maternity", rbPESU, 'PESU', '', exempt, xy))                    
                    if row[5] is not None:
                        row_values.append((key, sName, forest, orgC, "Roost", "Maternity", rbMYSE, 'MYSE', '', exempt, xy))                    
                    if row[7] is not None:
                        row_values.append((key, sName, forest, orgC, "Roost", "Maternity", rbMYSO, 'MYSO', '', exempt, xy))                    
                    if row[8] is not None:
                        row_values.append((key, sName, forest, orgC, "Roost", "Maternity", rbMYLU, 'MYLU', '', exempt, xy))                    
                    mList.append(key2)



    with arcpy.da.InsertCursor('ptBufferFC', ['Site_CN', 'SiteName', 'ForestName', 'OrgCode', 
                                'BufferClass', 'BufferType', 'BufferDistance', 'Species', 'BufferComments', 'Exempt', 'SHAPE@XY']) as cursor:
            for row in row_values:
                cursor.insertRow(row)      

#Function to process Capture data to the pt Feature layer
def ptBufferLayerCapture():
    row_values = []  #List to hold values to be added to the ptBuffer Layer
    cList = [] #List that will hold which uniques values were processed

    #loop thorugh the Capture Data with the search cursor
    with arcpy.da.SearchCursor('CaptureData',['OBS_CN', 'OBS_DATE', 'PrePostWNS', 
                                        'REPRODUCTIVE_STATUS', 'SCIENTIFIC_NAME', 'EXEMPT_FROM_PUBLIC', 
                                        'SHAPE@XY', 'FS_UNIT_ID', 'SITE_NAME', 'FS_UNIT_NAME', 
                                        'AGE', 'OBS_METHOD', 'SITE_TYPE']) as cursor:
        for row in cursor:

            key = row[0] #Observation Number
            key2 = (row[8], row[4]) #Combination of Observation Number & Scientific Name
            #determine if record is exempt from public distribution or not
            if row[5] is not None:
                if row[5] == "Y":
                    exempt = "Y"
                else:
                    exempt = "N"
            else:
                exempt = "N"
            xy = row[6] #XY Coords Token
            orgC =row[7] #Org Code
            sName = row[8] #Site Name
            forest = row[9] #Forest Name

            #Determine the Visit Date
            #is the length of the value is 10 then there is no time in the value
            if len(row[1]) == 10:
                vDate = datetime.strptime(row[1], "%Y/%m/%d")
            #if the length of the row is 16 there there is time in the value
            elif len(row[1]) == 16:
                vDate = datetime.strptime(row[1], "%Y/%m/%d %H:%M")
            #For the next 3 variables, the year (2000) is irrelevant but has to be added for the process to work.
            targetDate = datetime(2000, vDate.month, vDate.day)  #this is the visit date from the data
            startDate = datetime(2000, 4, 15) #start date from the BCS
            endDate = datetime(2000, 8, 15)  #end date from the BCS

            #if records has not been processed, and visit date falls within date range, and the visit is not PreWNS or error, and is reproductive or a juvenile, and a BCS species
            if key2 not in cList and (startDate <= targetDate <= endDate) and row[2] not in ("PreWNS", "error") and (row[3] == "Reproducing" or row[10] == "Juvenile" )and row[4] in ('Myotis septentrionalis','Myotis sodalis', 'Myotis lucifugus', 'Perimyotis subflavus', 'Pipistrellus subflavus') and row[11] == 'In Hand' and row[12] == 'Sample Point':
                
                if row[4] in PESU:
                    row_values.append((key, sName, forest, orgC, "Capture", "Maternity", cbPESU, 'PESU', '', exempt, xy))
                elif row[4] == MYSE:
                    row_values.append((key, sName, forest, orgC, "Capture", "Maternity", cbMYSE, 'MYSE', '', exempt, xy))
                elif row[4] == MYSO:
                    row_values.append((key, sName, forest, orgC, "Capture", "Maternity", cbMYSO, 'MYSO', '', exempt, xy))
                elif row[4] == MYLU:
                    row_values.append((key, sName, forest, orgC, "Capture", "Maternity", cbMYLU, 'MYLU', '', exempt, xy))
                    
                cList.append(key2)
    # with the insert cursor loop through the list of row values and add each item as a record in the pt buffer layer            
    with arcpy.da.InsertCursor('ptBufferFC', ['Site_CN', 'SiteName', 'ForestName', 'OrgCode', 'BufferClass', 'BufferType', 'BufferDistance', 'Species', 'BufferComments', 'Exempt', 'SHAPE@XY']) as cursor:
                for row in row_values:
                    cursor.insertRow(row) 

''' End Functions '''


''' Start Workflow for Hibernacula '''
arcpy.AddMessage("Starting thre Hibernacula Data Process")

#Process Hibernacula data to determine visit sequence
VisitSequence('HibData')

#Process Hibernacula data to determine if sites are historic or not
HistAct('HibData')

#Process Hibernacula Data to determine PrePostWNSDates
PrePostWNSDate('HibData',"VISIT_START_DATE")

#Process Hibernacula data individual counts
haCountIndividuals()

#Process Hibernacula data and load the unique buffers as individual records in the pt Buffer Layer
ptBufferLayerHib()

''' End Workflow for Hibernacula Data '''


''' Start Workflow for Roost Data '''
arcpy.AddMessage("Starting the Roost Data Process")

#Process the Roost data to determine visit sequence
VisitSequence('RoostData') #run the function

#Process Roost data to determine if the roosts are historic 
HistAct('RoostData')

#Process Roost data to determine PrePostWNSDates
PrePostWNSDate('RoostData',"VISIT_START_DATE")

#Process Roost data to determine if snags are 10 years old or not
SnagTime()

#Process Roost data individual counts
roCountIndividuals()

#Process roosts with maternity records in the roost data layer
maternityRoost()

#Process Roost data and load the unique buffers as individual records in the pt Buffer Layer
ptBufferLayerRoost()

''' End Workflow for Roost Data'''


''' Start Workflow for Capture Data '''
arcpy.AddMessage("Starting the Capture Data Process")

#Process capture data and determine where the dates fall in regards to the WNS Detection Date table and dictionary.
#Populate results in the Capture Data layer
PrePostWNSDate('CaptureData', 'OBS_DATE')

#Process the capture data and load the unique buffers as indivdual records in the pt Buffer Layer
ptBufferLayerCapture()

''' End Workflor for Capture Data '''


''' Start Workflow for Buffer '''
arcpy.AddMessage("Starting the Buffering Process")

#create the physical buffers from the ptBuffer layer
arcpy.analysis.Buffer('ptBufferFC', bufferDataExport, 'BufferDistance')

#delete fields created by buffer tool
arcpy.management.DeleteField(bufferDataExport,['BUFF_DIST','ORIG_FID'])

''' End Workflow for Buffer '''
