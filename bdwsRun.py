from bdws import BDLoG, BDSWEA
from bdflopy import BDflopy

def main(project):
    print "start"
    basedir = "tutorials/tutorial1" #folder containing inputs, and where output directories will be created
    bratPath = basedir + "/inputs/brat.shp" #shapefile of beaver dam capacities from BRAT
    demPath = basedir + "/inputs/dem.tif" #DEM of study area (ideally clipped to valley-bottom)
    facPath = basedir + "/inputs/fac.tif" #Thresholded flow accumulation raster representing stream network
    outDir = basedir + "/outputs" #directory where BDLoG outputs will be generated
    bratCap = 1.0 #proportion (0-1) of maximum estimted dam capacity (from BRAT) for scenario

    model = BDLoG(bratPath, demPath, facPath, outDir, bratCap) #initialize BDLoG, sets varibles and loads inputs
    model.run() #run BDLoG algorithms
    model.close() #close any files left open by BDLoG
    print "bdlog done"

    #run surface water storage estimation (BDSWEA)
    fdirPath = basedir + "/inputs/fdir.tif" #flow direction raster
    idPath = basedir + "/outputs/damID.tif" #ouput from BDLoG
    modPoints = basedir + "/outputs/ModeledDamPoints.shp" #output from BDLoG

    model = BDSWEA(demPath, fdirPath, facPath, idPath, outDir, modPoints) #initialize BDSWEA object, sets variables and loads inputs
    model.run() #run BDSWEA algorithm
    model.writeModflowFiles() #generate files needed to parameterize MODFLOW
    model.close() #close any files left open by BDLoG
    print "bdswea done"

    #run groundwater storage estimation (MODFLOW)
    modflowexe = r"C:\Users\A02150284\Documents\MF2005.1_11\bin\mf2005" #path to MODFLOW-2005 executable
    indir = basedir + "/inputs" #location of input raste files
    modeldir = "tutorials/tutorial1/outputs" #BDSWEA output directory
    outdir = basedir + "/modflow" #directory to output MODFLOW results
    demfilename = "dem.tif" #name of input DEM
    hkfn = "/inputs/ksat.tif" #horizontal ksat in micrometers per second
    vkfn = "/inputs/kv.tif" #vertical ksat in micrometers per second
    fracfn = "/inputs/fc.tif" #field capacity as percentage
    kconv = 0.000001 #conversion of hkfn and vkfn to meters per second
    fconv = 0.01 #conversion of fracfn to a proportion
    gwmodel = BDflopy(modflowexe, indir, modeldir, outdir, demfilename) #initialize BDflopy, sets variables and loads inputs
    gwmodel.run(hkfn, vkfn, kconv, fracfn, fconv) #run BDflopy, this will write inputs for MODFLOW and then run MODFLOW
    gwmodel.close() #close any open files
    print "done"