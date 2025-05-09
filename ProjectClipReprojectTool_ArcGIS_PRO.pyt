#V1.2 Updated 9/1/2023 by D.Hood
import arcpy
import os
import re
from arcpy import metadata as md


class Toolbox(object):
	def __init__(self):
		"""Define the toolbox (the name of the toolbox is the name of the
		.pyt file)."""
		self.label = "Project clip and reproject tool - ArcGIS Pro ONLY"
		self.alias = ""

		# List of tool classes associated with this toolbox
		self.tools = [ProjectClipReproject]


class ProjectClipReproject(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "Project Clip and Reproject - ArcGIS Pro ONLY"
		self.description = "Clip and reproject SDE and EDW .lyr files contained in MXD to a user defined boundary and output to a consistant .gdb and file structure"
		self.canRunInBackground = False


	def getParameterInfo(self):
		"""Define parameter definitions"""

		# First parameter
		param0 = arcpy.Parameter(
		    displayName="Clip Feature",
		    name="bndry",
		    datatype= "GPFeatureLayer",
		    parameterType="Required",
		    direction="Input")

		# Second parameter
		param1 = arcpy.Parameter(
		    displayName="Layer Output directory",
		    name="output_dir",
		    datatype="DEFolder",
		    parameterType="Required",
		    direction="Input")

		# third parameter
		param2 = arcpy.Parameter(
		    displayName="Output geodatabase",
		    name="output_gdb",
		    datatype="DEWorkspace",
		    parameterType="Required",
		    direction="Input")
		param2.filter.list = ['Local Database', 'gdb']

		# fourth param checkbox
		param3 = arcpy.Parameter(
		    displayName="Group Naming",
		    name="group_naming",
		    datatype="GPBoolean",
		    parameterType="Optional",
		    direction="Input")
		param3.value = "False"

		params = [param0, param1, param2, param3]
		return params

	def isLicensed(self):
		"""Set whether tool is licensed to execute."""
		return True

	def updateParameters(self, parameters):
		"""Modify the values and properties of parameters before internal
		validation is performed.  This method is called whenever a parameter
		has been changed."""
		return

	def updateMessages(self, parameters):
		"""Modify the messages created by internal validation for each tool
		parameter.  This method is called after internal validation."""
		return

	def execute(self, parameters, messages):
		#Input user variables
		bndry = parameters[0].valueAsText

		#Input second variable
		output_dir = parameters[1].valueAsText

		#Input third variable
		output_gdb = parameters[2].valueAsText

		group_naming = parameters[3].valueAsText

		#Use current map doc - Script tools that use the current keyword must be run within arcmap to run properly
		aprx = arcpy.mp.ArcGISProject("CURRENT")
		mapdoc = aprx.activeMap
		#mapdoc = arcpy.mapping.MapDocument("CURRENT")
		#for mapdoc in aprx.listMaps():
                        #arcpy.AddMessage("Clipping data from map: " + mapdoc.name)

		#Background processing MUST be dissabled to use current map document
		#set to always run in foreground in tool setting to override background processing.
		arcpy.env.overwriteOutput = True
		arcpy.env.addOutputsToMap = 0

		try:
			#Processing
			arcpy.AddMessage("\n")
			out_sr = arcpy.Describe(bndry).spatialReference
			bndry_datum = out_sr.GCS.datumName[2:]

			#List lyrs
			#lyrs = arcpy.mapping.ListLayers(mapdoc)
			lyrs = mapdoc.listLayers()

			# remove boundary from the list
			lyrs_filter = [i for i in lyrs if i.name != bndry]

			#build lists of raster and vector layers that are broken or without spatial reference
			broken_lyrs = [i for i in lyrs_filter if i.isBroken]
			no_sr_lyrs = [i for i in lyrs_filter if not i.isBroken if i.isFeatureLayer == True or i.isRasterLayer == True if arcpy.Describe(i).spatialReference.name == "Unknown"]

			#build lists of rasters, and vector layers that aren't broken, have spatial reference for processing
			vctrs = [i for i in lyrs_filter if i.isFeatureLayer == True if i not in broken_lyrs if i not in no_sr_lyrs]
			rstrs = [i for i in lyrs_filter if i.isRasterLayer == True]

			#Create list of query layers to print later in script. Query layers don't work with the import metadata currently. So we are skipping those layers in import metatdata step. An "%" in name indicates whether they are a query layer.
			qry_lyr_names = [i for i in vctrs if "%" in i.name]

			#Warn user of layers that aren't suitable for processing
			if len(no_sr_lyrs) > 0:
				arcpy.AddMessage("The following layers do not have a spatial reference, and they will not be processed:\n")
				for i in no_sr_lyrs:
					arcpy.AddMessage("{}".format(i))
				arcpy.AddMessage("-----------------------------------------\n")

			#warn of broken paths and that the script won't use the bad layers
			if len(broken_lyrs) > 0:
				arcpy.AddMessage("The connections for the following layers are broken, and they will not be processed:\n")
				for i in broken_lyrs:
					arcpy.AddMessage("{}".format(i))
				arcpy.AddMessage("-----------------------------------------\n")

			#warn of unsupported rasters
			if len(rstrs) > 0:
				arcpy.AddMessage("Rasters are not supported by this tool. The following layers will not be processed:\n")
				for i in rstrs:
					arcpy.AddMessage("{}".format(i))
				arcpy.AddMessage("-----------------------------------------\n")

		#######################################################
		# Process Vectors
		#######################################################
			if len(vctrs) > 0:
				for i in vctrs:
					v = i #make copy of vector for symbology later
					desc = arcpy.Describe(i)
					path = desc.path
					src = i.dataSource
					sr = desc.spatialReference

					#Get output name
					#We need to check for definition queries. If there are queries the names will get overwritten if we just use the orig FC name. In the case of definition queries just use the layer name

					#if i.definitionQuery != "":
					#	outName = arcpy.ValidateTableName(i.name)

					#else:
					#	if arcpy.Describe(i).dataElementType == "DEFeatureClass":
   					#		outName = src.rsplit('\\', 1)[-1] #get orig Feature name. FS names are all whacky so use the index rather than describe
					#	else:
                                        #               outName = arcpy.ValidateTableName(i.name)


					outName = arcpy.ValidateTableName(i.name)

					#Get dataset name
					#Function to check for the existance of feature dataset and get name. Some layers aren't at their original location in source,
					#so just use an index and assume that is the original feature dataset
					def GetFDS(FC):
						""" Returns the feature dataset for a feature class
						or feature layer FC.

						If the feature class is not within a feature dataset,
						returns None."""
						# get the path to the feature class
						fcPath = arcpy.Describe(FC).catalogPath
						# get the path to its container
						fcHome = os.path.dirname(fcPath)
						dataset = fcHome.rsplit('\\', 1)[-1]
						return dataset
					FDS_test = GetFDS(i)

					#If Vertical Coordinate System exists make it go straight to gdb, and not go into a feature data set. Else make it go based on the following criteria
					if desc.hasZ:
						arcpy.AddMessage("*" + i.name + " coordinates have Z values and will be placed directly in the .gdb rather than a feature dataset.")
						#output FC structure
						fc_outname = os.path.join(output_gdb, outName) # ftr_cls
						#create layer forlder structure
						out_lyr_fldr = (output_dir)
						out_fds = None

					else:
						if group_naming == "true": #If user selects group naming then prioritize the group names in output
							if i.name != i.longName:
								source_fds = i.longName.rsplit('\\')[0]
								arcpy.AddMessage("Source FDS: " + source_fds)
								arcpy.AddMessage("name: " + i.name)
								arcpy.AddMessage("longName: " + i.longName)
							elif "edw_sde_default_as_myself.sde" in FDS_test.lower():
								source_fds = "EDW"
							elif ".gdb" in FDS_test.lower():
								source_fds = "Other"
							elif arcpy.Describe(i).dataElementType == "DEFeatureClass":
								if "." in FDS_test:
									source_fds = FDS_test.rsplit('.', 1)[1]
								else:
									source_fds = "Other"
							else:
								source_fds = "Other"

						else:
							if "edw_sde_default_as_myself.sde" in FDS_test.lower():
								source_fds = "EDW"
							elif ".gdb" in FDS_test.lower():
								source_fds = "Other"
							elif arcpy.Describe(i).dataElementType == "DEFeatureClass":
								if "." in FDS_test:
									source_fds = FDS_test.rsplit('.', 1)[1]
								else:
									source_fds = "Other"
							else:
								source_fds = "Other"

						source_fds = arcpy.ValidateTableName(source_fds)

						#output FC structure
						out_fds = os.path.join(output_gdb, source_fds)
						fc_outname = os.path.join(out_fds, outName)

						#create layer forlder structure
						out_lyr_fldr = os.path.join(output_dir, source_fds)

					#Format layer name. Replace any slashes in .lyr name
					if "\\" in i.name:
						i.name = i.name.replace("\\","")
					if "/" in i.name:
						i.name = i.name.replace("/","")
					lyr_disp = i.name + "_clip"
					lyr_outname = os.path.join(out_lyr_fldr, i.name + ".lyrx")

					#Check for joined features and build list of vectors that have a join
					def joinCheck(lyr):
						fList = arcpy.Describe(lyr).fields
						for f in fList:
							if f.name.find(lyr.name + ".") > -1:
								return True
						return False

					hasJoin = joinCheck(i)
					if hasJoin:
						arcpy.AddMessage("copying {} to retain the join data.".format(i))
						i = arcpy.CopyFeatures_management(i, r"in_memory\joinCopy")

					#Check for OID
					if not desc.hasOID:
						i = arcpy.CopyFeatures_management(i, r"in_memory\OIDlyr")
						print (i)

					#Processing: Clip and reproject
					if arcpy.Exists(fc_outname) and arcpy.Exists(lyr_outname):
						arcpy.AddMessage("{} has been previously processed, and exists in output location.\n".format(i))
						continue

					#Reproject layer
					#Check for datum transformation requirement, and get transform if necessary.
					in_datum = sr.GCS.datumName[2:]
					outlist = arcpy.ListTransformations(sr, out_sr)
					if len(outlist) > 0:
						transform = outlist[0]

					#Clip/ Reproject
					if not arcpy.Exists(fc_outname):

						#Clip layer
						arcpy.AddMessage("clipping layer: {}".format(i))
						clipped = arcpy.Clip_analysis(i, bndry, r"in_memory\clip")

						#Check if the clipped feature has features, and if not, omit from further processing
						records = arcpy.GetCount_management(clipped)
						if records[0] == "0":
							arcpy.AddMessage("{} has zero features after clip, and will not be further processed or included in the output.\n".format(i))
							continue

						#create feature dataset
						if out_fds is not None:
							if not arcpy.Exists(out_fds):
								arcpy.AddMessage("Creating feature dataset: {}".format(source_fds))
								arcpy.CreateFeatureDataset_management(output_gdb, source_fds, out_sr)

						if sr.name != out_sr.name:
							if in_datum == bndry_datum:
								arcpy.AddMessage("Creating feature class and projecting layer: {}".format(fc_outname))
								arcpy.Project_management(clipped, fc_outname, out_sr)

							else:
								arcpy.AddMessage("Creating feature class and projecting layer: {}".format(fc_outname))
								arcpy.Project_management(clipped, fc_outname, out_sr, transform)

						else:
							arcpy.AddMessage("Creating feature class: {}".format(fc_outname))
							arcpy.CopyFeatures_management(clipped, fc_outname)

						#import metadata from original layer
						if "%" not in v.name:
                                                        src_item_md = v.metadata
                                                        fc_outnamePath = r"{}".format(fc_outname)
                                                        tgt_item_md = md.Metadata(fc_outnamePath)
                                                        tgt_item_md.copy(src_item_md)
                                                        tgt_item_md.save()

						#Populate area or length of new feature class
						def addAreaField(feature, fieldName):
							if arcpy.Describe(feature).shapeType == "Polygon":
								field_names = [i.name for i in arcpy.ListFields(feature)]

								if not fieldName in field_names:
									arcpy.AddField_management(feature, fieldName, "Float")

									arcpy.CalculateField_management(feature, fieldName, "!SHAPE.area@ACRES!", "PYTHON_9.3")
								else:
									arcpy.CalculateField_management(feature, fieldName, "!SHAPE.area@ACRES!", "PYTHON_9.3")


						def addLengthField(feature, fieldName):
							if arcpy.Describe(feature).shapeType == "Polyline":
								field_names = [i.name for i in arcpy.ListFields(feature)]

								if not fieldName in field_names:
									arcpy.AddField_management(feature, fieldName, "Float")

									arcpy.CalculateField_management(feature, fieldName, "!SHAPE.length@MILES!", "PYTHON_9.3")
								else:
									arcpy.CalculateField_management(feature, fieldName, "!SHAPE.length@MILES!", "PYTHON_9.3")

						addAreaField(fc_outname, "Acres_Calc")
						addLengthField(fc_outname, "Miles_Calc")

					#Create .lyrx file
					#Check to make sure that the original layer and the new feature are of the same type before proceeding
					#This is necessary because some errors have been thrown were geometric network datatypes were used and the new ones are simple type
					if desc.featureType != arcpy.Describe(fc_outname).featureType:
						arcpy.AddMessage("*New feature class and original map layer are different feature types. Layer file will not be created because symbology can't be imported.*\n")
						continue

					else:
						if not arcpy.Exists(lyr_outname):
							if not os.path.exists(out_lyr_fldr):
								os.makedirs(out_lyr_fldr)
							arcpy.AddMessage("Creating .lyrx file: {}\n".format(lyr_outname))
							lyr = arcpy.MakeFeatureLayer_management(fc_outname, lyr_disp)
							arcpy.ApplySymbologyFromLayer_management(lyr, v)
							arcpy.SaveToLayerFile_management(lyr, lyr_outname)

							desc = arcpy.Describe(lyr_outname)

							if "_clip" in desc.nameString[-5:]:
								lyr_in = arcpy.mp.LayerFile(lyr_outname)
								lyr_in.name = desc.nameString[:-5]
								lyr_in.save()

					arcpy.Delete_management("in_memory")

			else:
				arcpy.AddMessage("No suitable vectors for processing.")


			if qry_lyr_names:
				arcpy.AddMessage("The following layer(s) failed to import metadata:\n")
				for i in qry_lyr_names:
					arcpy.AddMessage(i)

		except arcpy.ExecuteError:
			arcpy.AddError(arcpy.GetMessages(2))

		except Exception:
			e = sys.exc_info()[1]
			arcpy.AddError(e.args[0])

		except:
			# Get the traceback object
			tb = sys.exc_info()[2]
			tbinfo = traceback.format_tb(tb)[0]
			pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
			msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"
			arcpy.AddError(pymsg)
			arcpy.AddError(msgs)

		#Clean up
		# release locks
		del mapdoc
		arcpy.Delete_management("in_memory")
		arcpy.AddMessage("-----------------------------------------")

		return
