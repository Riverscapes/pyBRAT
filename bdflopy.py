import flopy
import flopy.utils.binaryfile as bf
import os
import numpy as np
from osgeo import gdal

class BDflopy:
    def __init__(self, modflowexe, indir, modeldir, outdir, demfilename):
        """
        Initialize BDflopy class.

        :param modflowexe: Path to MODFLOW executable file.
        :param indir: Path to directory of raster inputs for BDSWEA.
        :param modeldir: Path to directory of outputs from BDSWEA.
        :param outdir: Path to directory where output files will be genearted.
        :param demfilename: Name of DEM file in the input directory (e.g. 'dem.tif').

        """
        self.modflowexe = modflowexe
        self.indir = indir
        self.modeldir = modeldir
        self.outdir = outdir
        if not os.path.isdir(self.outdir):
            os.makedirs(self.outdir)
        self.setVariables(demfilename)
        self.setPaths()
        self.loadBdsweaData()

    def createDatasets(self, filelist):
        """
        Create GDAL raster datasets.

        :param filelist: List of paths where raster datasets will be created.

        :return: List of GDAL datasets
        """
        datasetlist = []
        for file in filelist:
            #create raster dataset
            datasetlist.append(self.driver.Create(file, self.xsize, self.ysize, 1, gdal.GDT_Float32))
            #set projection to match input dem
            datasetlist[-1].SetProjection(self.prj)
            #set geotransform to match input dem
            datasetlist[-1].SetGeoTransform(self.geot)
        return datasetlist

    def createIboundData(self):
        """
        Create ibound arrays for MODFLOW parameterization.

        :return: None
        """
        self.iboundData = []
        for i in range(0, len(self.iboundds)):
            ibound = np.zeros(self.wseData[i].shape, dtype = np.int32)
            ibound[self.wseData[i] > self.zbot] = 1
            ibound[self.headData[i] > 0.0] = -1
            ibound[self.wseData[i] < 0.0] = 0
            self.iboundData.append(ibound)
            self.iboundds[i].GetRasterBand(1).WriteArray(ibound)

    def createModflowDatasets(self):
        """
        Create GDAL raster datasets for MODFLOW inputs and outputs.

        :return: None
        """
        #create starting head datasets
        self.sheadds = self.createDatasets(self.sheadPaths)
        #create ending head datasets
        self.eheadds = self.createDatasets(self.eheadPaths)
        #create ibound datasets
        self.iboundds = self.createDatasets(self.iboundPaths)
        #create head change datasets
        self.hdchds = self.createDatasets(self.hdchPaths)
        self.hdchFracDs = self.createDatasets(self.hdchFracPaths)

    def createStartingHeadData(self):
        """
        Calculate starting head arrays.

        :return: None
        """
        self.sheadData = []
        for i in range(0, len(self.sheadds)):
            self.headData[i][self.headData[i] <np.nanmin(self.wseData[i])] = self.stats[0]
            data = np.where(self.headData[i] < self.stats[0], self.wseData[i], self.headData[i])
            self.sheadds[i].GetRasterBand(1).WriteArray(data)
            self.sheadds[i].GetRasterBand(1).FlushCache()
            self.sheadData.append(data)

    def loadData(self, filelist):
        """
        Read data from input rasters as numpy arrays.

        :param filelist: List of raster files to read as numpy arrays.

        :return: List of numpy arrays
        """
        datalist = []
        for file in filelist:
            ds = gdal.Open(file)
            datalist.append(ds.GetRasterBand(1).ReadAsArray())
            ds = None
        return datalist

    def loadBdsweaData(self):
        """
        Load data from BDSWEA.

        :return: None
        """
        self.wseData = self.loadData(self.wsePaths) # initial DEM and water surface elevation from BDSWEA
        self.zbot = self.wseData[0] - 10.0 # set bottom of the model domain
        self.headData = self.loadData(self.headPaths) # head data from BDSWEA
        self.pondData = self.loadData(self.pondPaths) # pond depths from BDSWEA

    def setPaths(self):
        """
        Set file paths for input and output data.

        :return: None
        """
        self.setWsePaths()
        self.setPondDepthPaths()
        self.setHeadPaths()
        self.setIBoundPaths()

    def setVariables(self, demfilename):
        """
        Set class variables.

        :param demfilename: Name of DEM raster file.

        :return: None
        """
        self.driver = gdal.GetDriverByName('GTiff')
        self.dempath = self.indir + "/" + demfilename
        demds = gdal.Open(self.dempath)
        self.geot = demds.GetGeoTransform()
        self.prj = demds.GetProjection()
        self.xsize = demds.RasterXSize
        self.ysize = demds.RasterYSize
        self.stats = demds.GetRasterBand(1).GetStatistics(0, 1)
        demds = None
        self.nlay = 1
        self.mf = []
        self.mfnames = ["start", "lo", "mid", "hi"]
        for mfname in self.mfnames:
            self.mf.append(flopy.modflow.Modflow(mfname, exe_name = self.modflowexe))

    def setHeadPaths(self):
        """
        Set file names for head data to be read and written.

        :return: None
        """
        #head files from BDSWEA
        self.headPaths = []
        for name in self.mfnames:
            self.headPaths.append(self.modeldir + "/head_" + name + ".tif")
        #files for ending/modeled head
        self.eheadPaths = []
        for name in self.mfnames:
            self.eheadPaths.append(self.outdir + "/ehead_" + name + ".tif")
        #files for starting head
        self.sheadPaths = []
        for name in self.mfnames:
            self.sheadPaths.append(self.outdir + "/shead_" + name + ".tif")
        #files for head change
        self.hdchPaths = []
        for i in range(1, len(self.mfnames)):
            self.hdchPaths.append(self.outdir + "/hdch_" + self.mfnames[i] + ".tif")
        # files for head change accounting for soil fraction
        self.hdchFracPaths = []
        for i in range(1, len(self.mfnames)):
            self.hdchFracPaths.append(self.outdir + "/hdch_frac_" + self.mfnames[i] + ".tif")

    def setIBoundPaths(self):
        """
        Set file names for output ibound rasters.

        :return: None
        """
        self.iboundPaths = []
        for name in self.mfnames:
            self.iboundPaths.append(self.outdir + "/ibound_" + name + ".tif")

    def setPondDepthPaths(self):
        """
        Set file paths for pond depth rasters created by BDSWEA.

        :return: None
        """
        self.pondPaths = []
        self.pondPaths.append(self.modeldir + "/depLo.tif")
        self.pondPaths.append(self.modeldir + "/depMid.tif")
        self.pondPaths.append(self.modeldir + "/depHi.tif")

    def setWsePaths(self):
        """
        Set file paths for water surface elevation rasters created by BDSWEA.

        :return: None
        """
        self.wsePaths = []
        self.wsePaths.append(self.dempath)
        self.wsePaths.append(self.modeldir + "/WSESurf_lo.tif")
        self.wsePaths.append(self.modeldir + "/WSESurf_mid.tif")
        self.wsePaths.append(self.modeldir + "/WSESurf_hi.tif")

    def setLpfVariables(self, hksat, vksat, kconv):
        """
        Set variables required for MODFLOW LPF package. This function is called internally.

        :param khsat: Horizontal hydraulic conductivity.
        :param kvsat: Vertical hydraulic conductivity.
        :param kconv: Factor to convert hksat and vksat to meters per second.

        :return: None
        """
        self.hksat = self.loadSoilData(hksat)*kconv
        self.vksat = self.loadSoilData(vksat)*kconv

    def writeModflowInput(self):
        """
        Add MODFLOW packages and write input files for baseline, low dam height, median dam height, and high dam height scenarios.

        :return: None
        """
        os.chdir(self.outdir)
        for i in range(0, len(self.mf)):
            flopy.modflow.ModflowDis(self.mf[i], self.nlay, self.ysize, self.xsize, delr = self.geot[1],
                                     delc = abs(self.geot[5]), top = self.wseData[i], botm = self.zbot,
                                     itmuni = 1, lenuni = 2)
            flopy.modflow.ModflowBas(self.mf[i], ibound = self.iboundData[i], strt = self.sheadData[i])
            flopy.modflow.ModflowLpf(self.mf[i], hk = self.hksat, vka = self.vksat)
            flopy.modflow.ModflowOc(self.mf[i])
            flopy.modflow.ModflowPcg(self.mf[i])
            self.mf[i].write_input()
            print "MODFLOW " + self.mfnames[i] + " input written"

    def runModflow(self):
        """
        Run MODFLOW for baseline, low dam height, median dam height, and high dam height scenarios.

        :return: None
        """
        for i in range(0, len(self.mf)):
            success, buff = self.mf[i].run_model()
            print self.mfnames[i] + " model done"

    def saveResultsToRaster(self):
        """
        Read modeled head values and write to GDAL rasters.

        :return: None
        """
        self.eheadData = []
        self.ModSuccess = []
        for i in range(0, len(self.mfnames)):
            if os.path.getsize(self.mfnames[i] + ".hds") > 1000:
                hds = bf.HeadFile(self.mfnames[i] + ".hds")
                head = hds.get_data(totim = 1.0)
                head = head[0,:,:]
                head[head < 0.0] = -9999.0
                self.eheadds[i].GetRasterBand(1).WriteArray(head)
                self.eheadds[i].GetRasterBand(1).FlushCache()
                self.eheadds[i].GetRasterBand(1).SetNoDataValue(-9999.0)
                head[head == np.min(head)] = np.nan
                self.eheadData.append(head)
                self.ModSuccess.append(True)
            else:
                self.ModSuccess.append(False)

    def loadSoilData(self, data):
        """
        Load/create data for hydraulic conductivity and fraction of soil that holds water. This function is called internally.

        :param data: Float, numpy.ndarray, or file path to raster.

        :return: Numpy array
        """
        if os.path.isfile(self.indir + "/" + str(data)):
            ds = gdal.Open(self.indir + "/" + str(data))
            outdata = ds.GetRasterBand(1).ReadAsArray()
        elif type(data) == float:
            outdata = np.ones(self.wseData[0].shape, dtype = np.float32)
            outdata = outdata * data
        elif type(data) == np.ndarray:
            outdata = data
        else:
            outdata = np.ones(self.wseData[0].shape, dtype=np.float32)
        if outdata.shape != self.wseData[0].shape:
            outdata = np.ones(self.wseData[0].shape, dtype=np.float32)
        outdata[outdata < 0.0] = np.nan
        return outdata

    def calculateHeadDifference(self, frac = 1.0, fconv = 1.0):
        """
        Calculate the head difference between MODFLOW runs.

        :param frac: Fraction of the soil that can hold water (e.g. field capacity, porosity). For calculating volumetric groundwater changes. Represented as numpy array concurrent with the input DEM. Default array is a single value of 1.0.
        :param fconv: Factor to convert frac to a proportion. Default = 1.0.

        :return: None
        """
        frac = self.loadSoilData(frac)
        fracconv = frac*fconv
        frac[frac > 0.0] = fracconv[frac > 0.0]
        for i in range(0, len(self.pondData)):
            self.pondData[i][self.pondData[i] < 0.0] = 0.0
        for i in range(0, len(self.pondData)):
            if self.ModSuccess[i] and self.ModSuccess[i+1]:
                diff = self.eheadData[i+1] - self.eheadData[0]
                diff = diff - self.pondData[i]
                diff = np.where(np.isnan(diff), -9999.0, diff)
                diff[diff < -10.0] = -9999.0
                diff_frac = np.multiply(frac, diff)
                diff_frac[diff_frac < -10.0] = -9999.0
                self.hdchds[i].GetRasterBand(1).WriteArray(diff)
                self.hdchds[i].GetRasterBand(1).FlushCache()
                self.hdchds[i].GetRasterBand(1).SetNoDataValue(-9999.0)
                self.hdchFracDs[i].GetRasterBand(1).WriteArray(diff_frac)
                self.hdchFracDs[i].GetRasterBand(1).FlushCache()
                self.hdchFracDs[i].GetRasterBand(1).SetNoDataValue(-9999.0)

    def run(self, hksat, vksat, kconv = 1.0, frac = 1.0, fconv = 1.0):
        """
        Run MODFLOW to calculate water surface elevation changes from beaver dam construction.

        :param hksat: Horizontal saturated hydraulic conductivity value(s). Single value, numpy array, or name of raster from input directory. Numpy arrays and rasters must be concurrent with input DEM.
        :param vksat: Vertical saturated hydraulic conductivity value(s). Single value, numpy array, or name of raster from input directory. Numpy arrays and rasters must be concurrent with input DEM.
        :param kconv: Factor to convert khsat and kvsat to meters per second. Default = 1.0.
        :param frac: Fraction of the soil (0-1) that can hold water (e.g. field capacity, porosity). Single value, numpy array, or name of raster from input directory. Numpy arrays and rasters must be concurrent with input DEM. Default = 1.0.
        :param fconv: Factor to convert frac to a proportion. Default = 1.0.

        :return: None
        """
        self.setLpfVariables(hksat, vksat, kconv)
        self.createModflowDatasets()
        self.createIboundData()
        self.createStartingHeadData()
        self.writeModflowInput()
        self.runModflow()
        self.saveResultsToRaster()
        self.calculateHeadDifference(frac, fconv)

    def close(self):
        """
        Close GDAL datasets.
        
        :return: None
        """

        self.eheadds = None
        self.sheadds = None
        self.iboundds = None
        self.hdchds = None
        self.hdchFracDs = None