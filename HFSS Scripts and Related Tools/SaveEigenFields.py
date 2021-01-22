# ----------------------------------------------
#SaveEigenFields.py
#Saves the desired field quantity over a given set of points
#for all k points to a .csv file
#
#Input format: comma seperated list, no spaces
#Inputs:
#1) Output file name base, without extension 
#		Default: blank (will be called ".csv")
#2) Points file name, without extension
#		Default: grid
#3) Desired field ("E" or "H")
#		Default: E
#4) Desired solution setup to use
#		Default: Setup1: LastAdaptive
#Output: a .csv file containing all field data over the points file
#        where each row is a spacial point and each column is ordered
#		 as: re(Ez,kx,ky), im(Ez,kx,ky),..
#		 and repeats. So each k point corresponds to the a set 
#		 of 2 columns containing the real and imaginary parts of the 
#		 field, in increasing k. Here k first runs through kx, then ky
#
#Known issues: For unknown reasons, if you first open HFSS and run the 
#script, sometimes a "Failed to open file" error will be thrown when 
#it tries to save.
#This can be fixed by saving any file manually (using the calculator). 
#Every subsequent run of the script should then work.
#
#Todo: remove hardcoded solution setup names, and phase variable names.
#Also, incorperate hexagonal cell options.
#
#Original Script recorded by ANSYS Electronics Desktop Version 2017.2.0
#
#Written by Robert Davis
#Original: 2020-4-14
#Last updated: 2020-5-8
# ----------------------------------------------

###Required setup code###
import ScriptEnv
ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
oDesktop.RestoreWindow()
import os
import csv
pi = 3.1415926535897 #it actually needs this many digits

###Configure settings for the current project###
oProject = oDesktop.GetActiveProject()
oDesign = oProject.GetActiveDesign()
filepath = os.path.dirname(os.path.abspath(__file__))
os.chdir(filepath)

###Define helper function to print messages to the console###
def message(mess):
	oDesktop.AddMessage(oDesktop.GetActiveProject().GetName()
						,oProject.GetActiveDesign().GetName(),0,str(mess))

###Fetch user arguments###
userArgs = ScriptArgument.split(',')
if len(userArgs)==1: #user specified a filename only (or nothing)
	outputFileName = userArgs[0] #can be blank
	pointsFileName = "grid.pts" #blindly hope they named it grid
	fieldRequested = "E" #assume they want E field
	setup = "Setup1: LastAdaptive" #assume they want the nominal setup
elif len(userArgs)==2: #user gave a name and a pts file
	outputFileName = userArgs[0] 
	pointsFileName = userArgs[1]+".pts"
	fieldRequested = "E" 
	setup = "Setup1: LastAdaptive" 
elif len(userArgs)==3:
	outputFileName = userArgs[0] 
	pointsFileName = userArgs[1]+".pts"
	fieldRequested = userArgs[2]
	setup = "Setup1: LastAdaptive" 
elif len(userArgs)==4:
	outputFileName = userArgs[0] 
	pointsFileName = userArgs[1]+".pts"
	fieldRequested = userArgs[2]
	setup = userArgs[3]

###Fetch the availble solved k point variations###
#HFSS internally converts to radians, but requires degrees for export
#so here the values are converted to degrees with very high precision.
#Sometimes the values are duplicated. Not sure why, so just get rid of them.
#They are listed in the order they were solved in, which is frequently 
#not in increasing order. Hence we need to sort it.
oModule = oDesign.GetModule("Solutions")
kxPoints = oModule.ListValuesOfVariable(setup,"px") #get all kx
kxPoints = [float(m)*180/pi for m in kxPoints] #convert to degrees
kxPoints = list(dict.fromkeys(kxPoints)) #remove any duplicates
kxPoints.sort() #sort in ascending order
kyPoints = oModule.ListValuesOfVariable(setup,"py")
kyPoints = [float(m)*180/pi for m in kyPoints] #convert to degrees
kyPoints = list(dict.fromkeys(kyPoints)) #remove any duplicates
kyPoints.sort() #sort in ascending order

message("Begining verification...")

numKPoints = len(kxPoints)*len(kyPoints)

message("Verifing field data for all "+str(numKPoints)+" solved k values")
errors = 0
for i in kxPoints:
	for j in kyPoints:
		valid = oModule.HasFields(setup, "px="+str(i)+"deg, py="+str(j)+"deg")
		if not valid:
			message("Error: field data not found for solved variation "+
					"px="+str(i)+"deg, py="+str(j)+"deg")
			errors += 1

if errors:
	message("There were "+str(errors)+" solved variations without field data."+
			" Try resimulating these variations and rerunning script.")
	message("Exiting script with error...")
	raise SystemExit
else:
	message("All field data verified. Begining data extraction...")

maxSize = 5 #number of ky (columns) to have per file
if len(kyPoints) > maxSize:
	numFiles = len(kyPoints)//maxSize + (len(kyPoints) % maxSize > 0) #break into 10 ky segments
	message("Warning: there are too many k points to save in one file. "+
			"Going to save to "+str(numFiles)+ " files instead.")
else:
	numFiles = 1


##Configure the fields calculator to output the desired property###
oModule = oDesign.GetModule("FieldsReporter")
oModule.EnterQty(fieldRequested)
oModule.CalcOp("ScalarZ")
###Fetch the data for eaqch k and add to a variable###

#define how many ky points to use for each file (all but last are same)
numPoints = [maxSize]*numFiles
numPoints[-1] = len(kyPoints)-maxSize*(numFiles-1)

for file in range(numFiles):
	outputData = []

	for ky in kyPoints[file*numPoints[file-1]:file*numPoints[file-1]+numPoints[file]]:
		for kx in kxPoints:
			message("Exporting field: kx = "+str(kx)+"deg, ky = "+str(ky)+"deg")
			oModule.ExportToFile(filepath+"/"+"temp.fld",
	                             filepath+"/"+pointsFileName,
	                             setup,
	                             ["px:=", str(kx)+"deg",
	                             "py:=", str(ky)+"deg"], True) #export one kx,ky
			with open("temp.fld","rb") as datafile:
				#reopen the file immediately
				data = csv.reader(datafile)
				index = 0
				header = 1
				for row in data:
					if header: #ignore the header
						header = 0
					else:
						if kx == min(kxPoints) and ky == min(kyPoints[file*numPoints[file-1]:file*numPoints[file-1]+numPoints[file]]): #for the first value, create the rows
							outputData.append(str(row[0]).split()[3:5])
						else: #for all others, add to the rows
							outputData[index].extend(str(row[0]).split()[3:5])
							index += 1

	os.remove("temp.fld") #remove the leftover temp file


	###Save the variable to a .csv###
	with open(outputFileName+str(file)+".csv","wb") as f:
	    writer = csv.writer(f)
	    for row in outputData:
	        writer.writerow(row)
message("Finished extracting all k points.")

###extract the material parameters###

message("Begining extraction of model material parameters...")

oModule.CalcStack("clear")
oModule.EnterQty("E")
oModule.ClcMaterial("Permittivity (epsi)", "mult")
oModule.CalcOp("ScalarZ")
oModule.EnterQty("E")
oModule.CalcOp("ScalarZ")
oModule.CalcOp("/")
oModule.EnterScalar(8.854187817E-012)
oModule.CalcOp("/")
oModule.CalcOp("Real")
oModule.ExportToFile(filepath+"/"+"epsi.fld",filepath+"/"+pointsFileName,
	                    setup,[], True)

message("Permittivity data exported.")

oModule.CalcStack("clear")
oModule.EnterQty("E")
oModule.ClcMaterial("Permeability (mu)", "mult")
oModule.CalcOp("ScalarZ")
oModule.EnterQty("E")
oModule.CalcOp("ScalarZ")
oModule.CalcOp("/")
oModule.EnterScalar(1.25663706143592E-006)
oModule.CalcOp("/")
oModule.CalcOp("Real")
oModule.ExportToFile(filepath+"/"+"mu.fld",filepath+"/"+pointsFileName,
						setup,[], True)

message("Permeability data exported.")

message("All data have been exported. Ending Script.")