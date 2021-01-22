# ----------------------------------------------
#GenerateDispersionData.py
#Generates a .csv file containing formatted dispersion
#diagram data for the reduced Brillouin zone path from an
#eigenmode simulation with duel phase sweeps. For square
#lattices the path is Gamma-X-M-Gamma, while for triangular 
#lattices its Gamma-M-K-Gamma. Note that there are no repeating 
#points (only one Gamma is stored). 
#
#Input format: comma seperated list, no spaces
#Inputs:
#1) Output file name base, without extension 
#       Default: blank (will be numbers only)
#2) Lattice type, with square lattices = 0, triangular = 1
#       Default: 0 (square)
#3) Name of x direction sweep variable
#       Default: px
#4) Name of y direction sweep variable
#       Default: py
#5) Number of modes to export
#       Default: 3
#6) Setup to use, as it appears in HFSS (ie, 1,2,3, scaled to 0 indexing inside)
#       Default: 0 (i.e., Setup1) 
#Output: four .csvs, the first three of which (ending in suffix path1, path2,
#and path3) correspond to the three path components, and the final being a
#.csv containing the full diagram, in correct order.
#
#Todo: 
#
#Original Script recorded by ANSYS Electronics Desktop Version 2017.2.0
#
#Written by Robert Davis
#Original: 2019-5-28
#Last updated 2020-8-18
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
if len(userArgs)==1: #user specified a filename only
    outputFileName = userArgs[0] #can be blank
    lattice = 0
    XPhaseName = "px" #blindly hope the variables are named px and py
    YPhaseName = "py"
    modeNum = 3
    setup = 0
elif len(userArgs)==2: #user specified filename and lattice
    outputFileName = userArgs[0]
    lattice = int(userArgs[1])
    XPhaseName = "px"
    YPhaseName = "py"
    modeNum = 3
    setup = 0
elif len(userArgs)==4: #user specified filename and phase names
    outputFileName = userArgs[0]
    lattice = int(userArgs[1])
    XPhaseName = userArgs[2]
    YPhaseName = userArgs[3]
    modeNum = 3
    setup = 0
elif len(userArgs)==5: #user specified filename and variable names
    outputFileName = userArgs[0]
    lattice = int(userArgs[1])
    XPhaseName = userArgs[2]
    YPhaseName = userArgs[3]
    modeNum = int(userArgs[4])
    setup = 0
elif len(userArgs)==6: #user specified filename and variable names
    outputFileName = userArgs[0]
    lattice = int(userArgs[1])
    XPhaseName = userArgs[2]
    YPhaseName = userArgs[3]
    modeNum = int(userArgs[4])
    setup = int(userArgs[5])-1
    
##Fetch the setup name to analyze##
oModule = oDesign.GetModule("AnalysisSetup")
setupNames = oModule.GetSetups() 

###Fetch the availble solved k point variations###
#HFSS internally converts to radians, but requires degrees for export
#so here the values are converted to degrees with very high precision.
#Sometimes the values are duplicated. Not sure why, so just get rid of them.
#They are listed in the order they were solved in, which is frequently 
#not in increasing order. Hence we need to sort it.
#We only want the 1st (irreducable) BZ, so only grab one half the values
oModule = oDesign.GetModule("Solutions")
kxPoints = oModule.ListValuesOfVariable(setupNames[setup]+" : LastAdaptive",XPhaseName) #get all kx
kxPoints = [float(m)*180/pi for m in kxPoints] #convert to degrees
kxPoints = list(dict.fromkeys(kxPoints)) #remove any duplicates
kxPoints.sort() #sort in ascending order
kxPoints = [k for k in kxPoints if k>=0 and k<=180.1] #get only 0 - 180 degrees
kxPoints = [str(k)+"deg" for k in kxPoints] #format into strings with deg on them
kyPoints = oModule.ListValuesOfVariable(setupNames[setup]+" : LastAdaptive",YPhaseName)
kyPoints = [float(m)*180/pi for m in kyPoints] #convert to degrees
kyPoints = list(dict.fromkeys(kyPoints)) #remove any duplicates
kyPoints.sort() #sort in ascending order
kyPoints = [k for k in kyPoints if k>=0 and k<=180.1] #get only 0 - 180 degrees
kyPoints = [str(k)+"deg" for k in kyPoints] #format into strings with deg on them

##Produce the indevidual dispersion curves##
modeNames = []
for i in range(1,modeNum+1): #generate the names of the modes in HFSS format
    modeNames.append("re(Mode("+str(i)+"))")

oModule = oDesign.GetModule("ReportSetup")
if lattice==0: #square lattice
    message("Generating square lattice plots...")
    oModule.CreateReport("Gamma to X",
                         "Eigenmode Parameters",
                         "Rectangular Plot",
                         setupNames[setup]+" : LastAdaptive", [],
                         [XPhaseName+":=", kxPoints,
                          ["NAME:VariableValues",
    			           YPhaseName+":=", "0deg"]],
                         ["X Component:=", XPhaseName,
                          "Y Component:=",modeNames], [])

    oModule.CreateReport("X to M",
                         "Eigenmode Parameters",
                         "Rectangular Plot",
                         setupNames[setup]+" : LastAdaptive", [],
                         [YPhaseName+":=", [k for k in kyPoints if float(k[0:-3])!=0],
                         ["NAME:VariableValues",
                            XPhaseName+":=", "180deg"]],
                         ["X Component:=", YPhaseName,
                          "Y Component:=",modeNames], [])

    oModule.CreateReport("M to Gamma",
                         "Eigenmode Parameters",
                         "Rectangular Plot",
                         setupNames[setup]+" : LastAdaptive", [],
                         [XPhaseName+":=", [k for k in kxPoints if float(k[0:-3])!=0],
                          YPhaseName+":=", [k for k in kyPoints if float(k[0:-3])!=0],],
                         ["X Component:=", XPhaseName,
                          "Y Component:=",modeNames], [])

    ##Export the curves to .csv files for later use##
    oModule.ExportToFile("Gamma to X",filepath+"/"+outputFileName+"path1.csv")
    oModule.ExportToFile("X to M",filepath+"/"+outputFileName+"path2.csv")
    oModule.ExportToFile("M to Gamma",filepath+"/"+outputFileName+"path3.csv")

elif lattice==1: #triangular lattice
    message("Generating triangular lattice plots...")
    oModule.CreateReport("Gamma to M",
                         "Eigenmode Parameters",
                         "Rectangular Plot",
                         setupNames[setup]+" : LastAdaptive", [],
                         [XPhaseName+":=", kxPoints,
                          ["NAME:VariableValues",
                           YPhaseName+":=", "0deg"]],
                         ["X Component:=", XPhaseName,
                          "Y Component:=",modeNames], [])
    oModule.CreateReport("M to K",
                         "Eigenmode Parameters",
                         "Rectangular Plot",
                         setupNames[setup]+" : LastAdaptive", [],
                         [XPhaseName+":=", [k for k in kxPoints if float(k[0:-3])>= 138.6 and float(k[0:-3]) != 0],
                          YPhaseName+":=", [k for k in kyPoints if float(k[0:-3])<= 138.6 and float(k[0:-3]) != 0],],
                         ["X Component:=", XPhaseName,
                          "Y Component:=",modeNames], [])

    oModule.CreateReport("K to Gamma",
                         "Eigenmode Parameters",
                         "Rectangular Plot",
                         setupNames[setup]+" : LastAdaptive", [],
                         [XPhaseName+":=", [k for k in kxPoints if float(k[0:-3])< 138.6 and float(k[0:-3]) != 0],
                          YPhaseName+":=", [k for k in kyPoints if float(k[0:-3])< 138.6 and float(k[0:-3]) != 0],],
                         ["X Component:=", XPhaseName,
                          "Y Component:=",modeNames], [])

    ##Export the curves to .csv files for later use##
    oModule.ExportToFile("Gamma to M",filepath+"/"+outputFileName+"path1.csv")
    oModule.ExportToFile("M to K",filepath+"/"+outputFileName+"path2.csv")
    oModule.ExportToFile("K to Gamma",filepath+"/"+outputFileName+"path3.csv")



##Preallocate the output variables##
eigenFreqs = [[] for _ in range(modeNum)] #builds columns
firstrow = 1

##Place the data for the first k-space path file into the output variable##
with open(outputFileName+"path1.csv","rb") as datafile:
    data = csv.reader(datafile)
    for row in data:
        if firstrow == True:
            firstrow = 0;
        else:
            for col in range(len(row)-1):
                eigenFreqs[col].append(row[col+1])
firstrow = 1;

if lattice == 0: #square lattice
    ##Place the data from the x to m point file into the output variables##
    with open(outputFileName+"path2.csv","rb") as datafile:
        data = csv.reader(datafile)
        for row in data:
            if firstrow:
                firstrow = 0;
            else:
                for mode in range(modeNum):
                    eigenFreqs[mode].append(row[mode+1])
                
elif lattice == 1: #triangular lattice
    ##Place the data from the m to k point file into the output variables##
    index = 0
    temps = [[] for _ in range(modeNum)] #builds temp columns
    with open(outputFileName+"path2.csv","rb") as datafile:
        data = csv.reader(datafile)
        for row in data:
            if firstrow:
                firstrow = 0;
            else:
                for mode in range(modeNum):
                    temps[mode].append(row[index+1+((len(row)-1)//modeNum)*mode])
                index+=1
        for mode in range(modeNum):
            eigenFreqs[mode].extend(reversed(temps[mode]))
                
##Place the data from the last k-space path file into the output variables##
#Note that all the added lines are there to ensure that the points are placed
#in the correct order, which requires some manipulation (going along diagonals
#in reverse order is complicated).
index = 0
firstrow = 1
temps = [[] for _ in range(modeNum)] #builds temp columns

with open(outputFileName+"path3.csv","rb") as datafile:
    data = csv.reader(datafile)
    for row in data:
        if firstrow:
            firstrow = 0;
        else:
            for mode in range(modeNum):
                temps[mode].append(row[index+1+((len(row)-1)//modeNum)*mode])
            index+=1

    for mode in range(modeNum):
        eigenFreqs[mode].extend(reversed(temps[mode]))

##Place the variables into .csv form and save for viewing##
rows = zip(*eigenFreqs) #wizardry to turn columns to rows

with open(outputFileName+"dispersionData.csv","wb") as f:
    writer = csv.writer(f)
    for row in rows:
        writer.writerow(row)

message("All data have been exported. Ending Script.")