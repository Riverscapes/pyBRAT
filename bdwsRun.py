from bdws import BDLoG, BDSWEA
from bdflopy import BDflopy
import arcpy
import os

def main(projectRoot, bratPath, demPath, flowAcc, flowDir, horizontalKFN, verticalKFN, fieldCapacity, modflowexe):
    arcpy.AddMessage("start")
    projectFolder = makeFolder(projectRoot, "BDWS_Project")
    inputsFolder = makeFolder(projectFolder, "Inputs")
    outDir = makeFolder(projectFolder, "Output")
    bratCap = 1.0 #proportion (0-1) of maximum estimted dam capacity (from BRAT) for scenario
    bratPath = copyIntoFolder(bratPath, inputsFolder, "BRAT")
    demPath = copyIntoFolder(demPath, inputsFolder, "DEM")
    flowAcc = copyIntoFolder(flowAcc, inputsFolder, "FlowAccumulation")
    flowDir = copyIntoFolder(flowDir, inputsFolder, "FlowDir")
    if horizontalKFN:
        horizontalKFN = copyIntoFolder(horizontalKFN, inputsFolder, "HorizontalKSAT")
    if verticalKFN:
        verticalKFN = copyIntoFolder(verticalKFN, inputsFolder, "VerticalKSAT")
    if fieldCapacity:
        fieldCapacity = copyIntoFolder(fieldCapacity, inputsFolder, "FieldCapacity")


    model = BDLoG(bratPath, demPath, flowAcc, outDir, bratCap) #initialize BDLoG, sets varibles and loads inputs
    model.run() #run BDLoG algorithms
    model.close() #close any files left open by BDLoG
    arcpy.AddMessage("bdlog done")

    #run surface water storage estimation (BDSWEA)
    idPath = os.path.join(outDir, "damID.tif")#ouput from BDLoG
    modPoints = os.path.join(outDir, "ModeledDamPoints.shp") #output from BDLoG

    model = BDSWEA(demPath, flowDir, flowAcc, idPath, outDir, modPoints) #initialize BDSWEA object, sets variables and loads inputs
    model.run() #run BDSWEA algorithm
    model.writeModflowFiles() #generate files needed to parameterize MODFLOW
    model.close() #close any files left open by BDLoG
    arcpy.AddMessage("bdswea done")

    if horizontalKFN and verticalKFN and fieldCapacity:
        #run groundwater storage estimation (MODFLOW)
        arcpy.AddMessage("Running BDflopy")
        modflowexe = r"C:\Users\A02150284\Downloads\MF2005.1_11\MF2005.1_11\bin\mf2005" #path to MODFLOW-2005 executable
        indir = projectFolder + "/inputs" #location of input raste files
        modflowOutput = os.path.join(projectFolder, "modflow") #directory to output MODFLOW results
        kconv = 0.000001 #conversion of hkfn and vkfn to meters per second
        fconv = 0.01 #conversion of fracfn to a proportion
        gwmodel = BDflopy(modflowexe, indir, outDir, modflowOutput, demPath) #initialize BDflopy, sets variables and loads inputs
        gwmodel.run(horizontalKFN, verticalKFN, kconv, fieldCapacity, fconv) #run BDflopy, this will write inputs for MODFLOW and then run MODFLOW
        gwmodel.close() #close any open files
        arcpy.AddMessage("done")


def copyIntoFolder(thingToCopy, copyFolderRoot, copyFolderName):
    copyFolder = makeFolder(copyFolderRoot, findAvailableNum(copyFolderRoot) + '_' + copyFolderName)
    copyPath = os.path.join(copyFolder, os.path.basename(thingToCopy))
    arcpy.Copy_management(thingToCopy, copyPath)
    return copyPath


def makeFolder(pathToLocation, newFolderName):
    """
    Makes a folder and returns the path to it
    :param pathToLocation: Where we want to put the folder
    :param newFolderName: What the folder will be called
    :return: String
    """
    newFolder = os.path.join(pathToLocation, newFolderName)
    if not os.path.exists(newFolder):
        os.mkdir(newFolder)
    return newFolder


def findAvailableNum(folderRoot):
    """
    Tells us the next number for a folder in the directory given
    :param folderRoot: Where we want to look for a number
    :return: A string, containing a number
    """
    takenNums = [fileName[0:2] for fileName in os.listdir(folderRoot)]
    POSSIBLENUMS = range(1, 100)
    for i in POSSIBLENUMS:
        stringVersion = str(i)
        if i < 10:
            stringVersion = '0' + stringVersion
        if stringVersion not in takenNums:
            return stringVersion
    arcpy.AddWarning("There were too many files at " + folderRoot + " to have another folder that fits our naming convention")
    return "100"