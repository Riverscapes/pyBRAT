from osgeo import gdal, ogr
import numpy as np
import os
import math

class BDLoG:
    def __init__(self, brat, dem , fac, outDir, bratCap, stat = None):
        """
        Initialization of the Beaver Dam Location Generator class.

        :param brat: Path to BRAT shapefile.
        :param dem: Path to DEM for area of interest.
        :param fac: Binary raster representing the stream network with a value of 1 (generally a thresholded flow accumulation).
        :param outDir: Path to directory where output files will be generated.
        :param bratCap: Proportion (0 - 1) of capacity for which to generate beaver dams.
        :param stat: (Optional) Estimated pond volumes and prediction intervals as a function of reach slope and dam height (not yet implemented).

        """
        self.bratPath = brat
        self.demPath = dem
        self.facPath = fac
        self.outDir = outDir
        if not os.path.isdir(self.outDir):
            os.makedirs(self.outDir)
        self.bratCap = bratCap
        self.statPath = stat

    def setVariables(self):
        """
        Sets class variables for location generation.

        :return: None
        """
        self.driverShp = ogr.GetDriverByName("Esri Shapefile")
        self.bratDS = ogr.Open(self.bratPath, 1)
        self.bratLyr = self.bratDS.GetLayer()
        self.nFeat = self.bratLyr.GetFeatureCount()
        self.demDS = gdal.Open(self.demPath)
        self.dem = self.demDS.GetRasterBand(1).ReadAsArray()
        self.facDS = gdal.Open(self.facPath)
        self.fac = self.facDS.GetRasterBand(1).ReadAsArray()
        self.idOut = np.full(self.dem.shape, -9999.0, dtype=np.float32)
        self.geot = self.demDS.GetGeoTransform()
        self.prj = self.demDS.GetProjection()
        self.outDS = self.driverShp.CreateDataSource(self.outDir + "/ModeledDamPoints.shp")
        self.outLyr = self.outDS.CreateLayer("ModeledDamPoints",  self.bratLyr.GetSpatialRef(), geom_type=ogr.wkbPoint)
        self.capRank = np.empty([self.nFeat,3])
        self.driverTiff = gdal.GetDriverByName("GTiff")

    def createFields(self):
        """
        Creates fields to be populated for the output dam location shapefile

        :return: None
        """
        field = ogr.FieldDefn("brat_ID", ogr.OFTInteger)
        self.outLyr.CreateField(field)
        field.SetName("endx")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("endy")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("az_us")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("g_elev")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("slope")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("ht_max")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("damType")
        field.SetType(ogr.OFTString)
        self.outLyr.CreateField(field)
        field.SetName("ht_lo")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("ht_mid")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("ht_hi")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("ht_lo_mod")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("ht_mid_mod")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("ht_hi_mod")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("area_lo")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("area_mid")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("area_hi")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("vol_lo")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("vol_mid")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("vol_hi")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("vol_lo_lp")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("vol_mid_lp")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("vol_hi_lp")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("vol_lo_mp")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("vol_mid_mp")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("vol_hi_mp")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("vol_lo_up")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("vol_mid_up")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("vol_hi_up")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("diff_lo")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("diff_mid")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("diff_hi")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)
        field.SetName("type")
        field.SetType(ogr.OFTReal)
        self.outLyr.CreateField(field)

    def setBratFields(self):
        """
        Set values for fields derived from the input BRAT shapefile.

        :return: None
        """
        if self.bratLyr.FindFieldIndex("totdams", 1) >= 0:
            self.bratLyr.DeleteField(self.bratLyr.FindFieldIndex("totdams", 1))
        if self.bratLyr.FindFieldIndex("totcomp", 1) >= 0:
            self.bratLyr.DeleteField(self.bratLyr.FindFieldIndex("totcomp", 1))
        field = ogr.FieldDefn("totdams", ogr.OFTInteger)
        self.bratLyr.CreateField(field)
        field = ogr.FieldDefn("totcomp", ogr.OFTInteger)
        self.bratLyr.CreateField(field)

    def sortByCapacity(self):
        """
        Sort BRAT reaches by estimated dam capacity.

        :return: None

        """
        for i in range(0, self.nFeat):
            feature = self.bratLyr.GetFeature(i)
            cap = feature.GetFieldAsDouble("oCC_EX")
            geom = feature.GetGeometryRef()
            #self.capRank holds 3 variables: FID, BRAT capacity (dams/km), and number of dams to be modeled for scenario(capacity scenario * BRAT capacity)
            self.capRank[i,0] = feature.GetFID()
            self.capRank[i,1] = cap
            self.capRank[i,2] = math.ceil(geom.Length() * (cap/1000.0))
        self.capRank = self.capRank[self.capRank[:,1].argsort()[::-1]]
        self.modCap = math.ceil(self.bratCap * np.sum(self.capRank[:,2]))

    def calculateDamsPerReach(self):
        """
        Determine the number of beaver dams and beaver dam complexes to place on each BRAT reach.

        :return: None
        """
        self.setBratFields()
        go = True
        totalDams = 0

        while go:
            i = 0
            while i < self.nFeat and go:
                bratFeat = self.bratLyr.GetFeature(self.capRank[i,0])
                exDams = bratFeat.GetFieldAsInteger("totdams")
                exComp = bratFeat.GetFieldAsInteger("totcomp")

                #number of dams for BRAT segment randomly selected from empricial complex size distribution
                damCount = math.ceil(np.random.lognormal(1.5515, 0.724))
                if damCount > 0:
                    if damCount > self.capRank[i,2]:
                        damCount = self.capRank[i,2]
                    if (totalDams + damCount) > self.modCap:
                        damCount = math.ceil(self.modCap - totalDams)
                    bratFeat.SetField("totdams", exDams + damCount)
                    if damCount > 0:
                        bratFeat.SetField("totcomp", exComp + 1)
                    self.bratLyr.SetFeature(bratFeat)
                totalDams += damCount
                i += 1

                if totalDams >= math.ceil(self.modCap):
                    go = False

    def createDams(self):
        """
        Place primary and secondary dams at a specific location on stream reaches.

        :return: None
        """
        i = 0
        while i < self.nFeat:
            bratFt = self.bratLyr.GetFeature(self.capRank[i, 0])
            bratLine = bratFt.GetGeometryRef()
            length = bratLine.Length()
            #read number of dams and dam complexes from shapefile field
            nDamCt = bratFt.GetFieldAsInteger("totdams")
            nCompCt = bratFt.GetFieldAsInteger("totcomp")
            spacing = 0.0
            if nDamCt > 0:
                spacing = length / (nDamCt * 1.0)

            #create a point for each dam to be modeled
            nDamRm = nDamCt
            nCompRm = nCompCt
            for j in range(0, nDamCt):
                #determine if dam is primary or secondary and create height distribution
                damFeat = ogr.Feature(self.outLyr.GetLayerDefn())
                rnum = np.random.random()
                if rnum < ((nCompRm*1.0)/(nDamRm*1.0)) or nDamCt == 1:
                    htDist = np.random.lognormal(0.22, 0.36, 30)
                    damType = "primary"
                    nCompRm -= 1
                else:
                    htDist = np.random.lognormal(-0.21, 0.39, 30)
                    damType = "secondary"

                nDamRm -= 1
                #location of dam on stream segment
                pointDist = length - (spacing * (j * 1.0))
                damPoint = bratLine.Value(pointDist)
                #bratLine.Value will return None if called on multipart line. This will cause a crash later in the code
                if damPoint is not None:
                    #set any field values here
                    damFeat = self.setDamFieldValues(damFeat, damType)
                    #set dam heights
                    damFeat = self.setDamHeights(damFeat, np.percentile(htDist, 2.5), np.median(htDist), np.percentile(htDist, 97.5))
                    damFeat.SetGeometry(damPoint)
                    self.outLyr.CreateFeature(damFeat)
                damFeat = None

            i += 1
            bratFt = None

    def getCellAddressOfPoint(self, x, y):
        """
        Calculate the row and column of a coordinate pair (linear units) based on the input DEM. UTM projections suggested, will not work with degree units.

        :param x: X coordinate (meters).
        :param y: Y coordinate (meters).

        :return: Numpy array with row and column address (array[row, col]).
        """
        col = math.floor((x - self.geot[0]) / self.geot[1])
        row = math.floor((self.geot[3] - y) / abs(self.geot[5]))
        address = np.array([row, col])
        return address

    def getCoordinatesOfCellAddress(self, row, col):
        """
        Calculate the coordinate pair at the center of a cell address based on the input DEM. UTM projections suggested, will not work with degree units.

        :param row: Row index of raster.
        :param col: Column index of raster.

        :return: Numpy array with x and y coordinates (array[x, y]).
        """
        x = self.geot[0] + (col * self.geot[1]) + (0.5 * self.geot[1])
        y = self.geot[3] + (row * self.geot[5]) + (0.5 * self.geot[5])
        coords = np.array([x, y])
        return coords

    def getStreamCellAddresses(self):
        """
        List addresses of cells on the stream network.

        :return: Numpy array (2, n) with stream cell addresses (array[[row, col],[row, col],...]).
        """
        fac = self.facDS.GetRasterBand(1).ReadAsArray()
        streamcells = np.swapaxes(np.where(fac > 0), 0, 1)
        return streamcells

    def moveDamsToFAC(self):
        """
        Set locations of generated dams to the nearest cell on the rasterized stream network. Only one dam can be present on each network cell.

        :return: None
        """
        streamcells = self.getStreamCellAddresses()
        nDams = self.outLyr.GetFeatureCount()
        i=0

        while i < nDams:
            #print str(i) + " of " + str(nDams)
            damFt = self.outLyr.GetFeature(i)
            damPt = damFt.GetGeometryRef()
            damAddress = self.getCellAddressOfPoint(damPt.GetX(), damPt.GetY())
            dist = np.sum((streamcells - damAddress)**2, axis = 1) #distance from stream cells to dam point
            #Maybe put in a check so if distance is too far it deletes the dam
            index = np.where(dist == min(dist)) #index of closest stream cell
            damAddress = streamcells[index[0][0]] #change cell address of dam to closest stream cell
            streamcells = np.delete(streamcells, index, axis = 0) #delete stream cell so each dam is located in a different cell
            self.idOut[damAddress[0]][damAddress[1]] = float(i*1.0)
            damCoords = self.getCoordinatesOfCellAddress(damAddress[0], damAddress[1])
            ptwkt = "POINT(%f %f)" %  (damCoords[0], damCoords[1])
            damPt = ogr.CreateGeometryFromWkt(ptwkt)
            damFt.SetGeometryDirectly(damPt)
            self.outLyr.SetFeature(damFt)
            i += 1

    def setDamFieldValues(self, feat, damType):
        """
        Set attribute for dam type.

        :param feat: OGR Feature of dam.
        :param damType: String describing dam type ('primary' or 'secondary').

        :return: Updated OGR Feature of dam.
        """
        feat.SetField("damType", damType)
        return feat

    def setDamHeights(self, feat, low, mid, high):
        """
        Set dam heights to be modeled for a dam.

        :param feat: OGR Feature of dam.
        :param low: Lower interval of dam height.
        :param mid: Median dam height.
        :param high: Upper interval of dam height.

        :return: Updated OGR Feature of dam.
        """
        feat.SetField("ht_lo", low)
        feat.SetField("ht_mid", mid)
        feat.SetField("ht_hi", high)
        feat.SetField("ht_lo_mod", low)
        feat.SetField("ht_mid_mod", mid)
        feat.SetField("ht_hi_mod", high)
        #feat.SetField("ht_max", max)
        return feat

    def generateDamLocationsFromBRAT(self):
        """
        Generate dam locations on rasterized stream network.

        :return: None
        """
        self.setVariables()
        self.createFields()
        self.sortByCapacity()
        self.calculateDamsPerReach()
        self.createDams()
        self.moveDamsToFAC()

    def writeDamLocationRaster(self):
        """
        Write dam locations to raster.

        :return: None
        """
        ds = self.driverTiff.Create(self.outDir + "/damID.tif", xsize=self.demDS.RasterXSize, ysize=self.demDS.RasterYSize, bands=1,
                                    eType=gdal.GDT_Float32)
        ds.SetGeoTransform(self.geot)
        ds.SetProjection(self.prj)
        ds.GetRasterBand(1).WriteArray(self.idOut)
        ds.GetRasterBand(1).FlushCache()
        ds.GetRasterBand(1).SetNoDataValue(-9999.0)
        ds = None

    def run(self):
        """
        Generate dam locations from BRAT and output as shapefile and raster.

        :return: None
        """
        self.generateDamLocationsFromBRAT()
        self.writeDamLocationRaster()

    def close(self):
        """
        Close all OGR and GDAL layers and datasets.

        :return: None
        """
        self.bratDS = None
        self.bratLyr = None
        self.demDS = None
        self.facDS = None
        self.outDS = None
        self.outLyr = None
        del self.dem
        del self.fac
        del self.idOut
        del self.capRank

class BDSWEA:
    def __init__(self, dem, fdir, fac, id, outDir, modPoints):
        """
        Initialization of the Beaver Dam Surface Water Estimation Algorithm class.

        :param dem: Path of DEM for area of interest.
        :param fdir: Path to flow direction raster, should be concurrent with DEM.
        :param fac: Path to binary raster representing the stream network with a value of 1 (generally a thresholded flow accumulation).
        :param id: Path to raster of pond ID, calculated with BDLoG class.
        :param outDir: Path where output files will be generated.
        :param modPoints: Path to shapefile of modeled dam locations from BDLoG.

        """
        self.outDir = outDir
        if not os.path.isdir(self.outDir):
            os.makedirs(self.outDir)
        self.setConstants()
        self.setVars(dem, fdir, fac, id, modPoints)
        self.createOutputArrays()
        # self.origrecursion = sys.getrecursionlimit()
        # if self.origrecursion < 1500:
        #     sys.setrecursionlimit(1500)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def setConstants(self):
        """
        Set constant variables.

        :return: None
        """
        self.FLOW_DIR_ESRI = np.array([32, 64, 128, 16, 0, 1, 8, 4, 2])
        self.FLOW_DIR_TAUDEM = np.array([4, 3, 2, 5, 0, 1, 6, 7, 8])
        self.ROW_OFFSET = np.array([-1, -1, -1, 0, 0, 0, 1, 1, 1])
        self.COL_OFFSET = np.array([-1, 0, 1, -1, 0, 1, -1, 0, 1])
        self.MAX_POND_AREA = 100000 #in square meters
        self.MAX_HEIGHT = 5.0 #in meters

    def setVars(self, dem, fdir, fac, id, shp):
        """
        Set class variables.

        :param dem: Path to DEM.
        :param fdir: Path to flow direction raster.
        :param fac: Path to binary raster representing the stream network with a value of 1 (generally a thresholded flow accumulation).
        :param id: Path to dam ID raster.
        :param shp: Path to shapefile of dam locations.

        :return: None
        """
        self.count = 0
        self.demDS = gdal.Open(dem)
        self.dem = self.demDS.GetRasterBand(1).ReadAsArray()
        self.fdirDS = gdal.Open(fdir)
        self.fdir = self.fdirDS.GetRasterBand(1).ReadAsArray()
        self.facDS = gdal.Open(fac)
        self.fac = self.facDS.GetRasterBand(1).ReadAsArray()
        self.idDS = gdal.Open(id)
        self.id = self.idDS.GetRasterBand(1).ReadAsArray()
        self.pointDS = ogr.Open(shp, 1)
        self.points = self.pointDS.GetLayer()
        self.nPoints = self.points.GetFeatureCount()
        self.geot = self.demDS.GetGeoTransform()
        self.prj = self.demDS.GetProjection()
        self.MAX_COUNT = math.ceil(self.MAX_POND_AREA / abs(self.geot[1] * self.geot[5]) / 1)
        self.driverTiff = gdal.GetDriverByName("GTiff")
        max = np.max(self.fdir)
        if max > 8:
            self.FLOW_DIR = self.FLOW_DIR_ESRI
        else:
            self.FLOW_DIR = self.FLOW_DIR_TAUDEM

    def createOutputArrays(self):
        """
        Create arrays which will be written to rasters.

        :return: None
        """
        self.idOut = np.copy(self.id)
        self.htOut = np.empty(shape=[self.dem.shape[0], self.dem.shape[1]])
        self.htOut.fill(-9999.0)
        self.depLo = np.empty(shape=[self.dem.shape[0], self.dem.shape[1]])
        self.depLo.fill(-9999.0)
        self.depMid = np.empty(shape=[self.dem.shape[0], self.dem.shape[1]])
        self.depMid.fill(-9999.0)
        self.depHi = np.empty(shape=[self.dem.shape[0], self.dem.shape[1]])
        self.depHi.fill(-9999.0)

    def getDamId(self):
        """

        :return: Numpy array of original dam ID raster.
        """
        return self.id

    def getDEM(self):
        """

        :return: Numpy array of DEM.
        """
        return self.dem

    def getFlowDirection(self):
        """

        :return: Numpy array of flow direction raster.
        """
        return self.fdir

    def getHeightAbove(self):
        """

        :return: Numpy array of the height of cells above a beaver dam.
        """
        return self.htOut

    def getPondID(self):
        """

        :return: Numpy array of the dam ID associated with each beaver pond.
        """
        return self.idOut

    def drainsToMe(self, index, fdir):
        """
        Determine if a neighboring cell drains to a target cell.

        :param index: Location of flow direction value in array.
        :param fdir: Flow direction value.

        :return: True if cell drains to center of 3x3, False if it does not
        """
        if index == 4:
            return False
        elif index == 0 and fdir == self.FLOW_DIR[8]:
            return True
        elif index == 1 and fdir == self.FLOW_DIR[7]:
            return True
        elif index == 2 and fdir == self.FLOW_DIR[6]:
            return True
        elif index == 3 and fdir == self.FLOW_DIR[5]:
            return True
        elif index == 5 and fdir == self.FLOW_DIR[3]:
            return True
        elif index == 6 and fdir == self.FLOW_DIR[2]:
            return True
        elif index == 7 and fdir == self.FLOW_DIR[1]:
            return True
        elif index == 8 and fdir == self.FLOW_DIR[0]:
            return True
        else:
            return False

    def backwardHAND(self, startX, startY, startE, pondID):
        """
        Recursively identify all cells draining to a dam location and the height of each cell above the dam.

        :param startX: Column of dam location.
        :param startY: Row of dam location.
        :param startE: DEM elevation at dam location.
        :param pondID: ID number of dam.

        :return: None
        """
        if startX > 0 and startY > 0 and startX < self.demDS.RasterXSize-1 and startY < self.demDS.RasterYSize-1:
            demWin = self.dem[startY - 1:startY + 2, startX - 1:startX + 2].reshape(1, 9)
            fdirWin = self.fdir[startY - 1:startY + 2, startX - 1:startX + 2].reshape(1, 9)
            for i in range(0,9):
                newX = startX
                newY = startY
                htAbove = demWin[0, i] - startE

                if (self.drainsToMe(i, fdirWin[0,i]) and htAbove < self.MAX_HEIGHT and htAbove > -10.0) and self.count < self.MAX_COUNT:
                    newX += self.COL_OFFSET[i]
                    newY += self.ROW_OFFSET[i]
                    htOld = self.htOut[newY, newX]

                    if (htOld >= htAbove or htOld == -9999.0):
                        self.idOut[newY, newX] = pondID
                        self.htOut[newY, newX] = htAbove
                        self.count += 1

                        self.backwardHAND(newX, newY, startE, pondID)

    def heightAboveDams(self):
        """
        For each cell draining to a beaver dam, calculate the height of cell above the dam location.

        :return: None
        """
        for i in range(1, self.fdir.shape[0]):
            for j in range(1, self.fdir.shape[1]):
                idVal = self.id[i,j]

                if idVal >= 0:
                    demVal = self.dem[i,j]
                    self.count = 0
                    self.backwardHAND(j, i, demVal, idVal)

    def calculateWaterDepth(self):
        """
        Calculate the depth of each beaver pond cell for each modeled dam height.

        :return: None
        """
        self.dem[self.dem == -9999.0] = np.nan
        self.htOut[self.htOut == -9999.0] = np.nan
        for i in range(0, self.points.GetFeatureCount()):
            feature = self.points.GetFeature(i)
            self.depLo[self.idOut == i] = feature.GetFieldAsDouble("ht_lo_mod") - self.htOut[self.idOut == i]
            self.depMid[self.idOut == i] = feature.GetFieldAsDouble("ht_mid_mod") - self.htOut[self.idOut == i]
            self.depHi[self.idOut == i] = feature.GetFieldAsDouble("ht_hi_mod") - self.htOut[self.idOut == i]

        self.dem[self.dem == np.nan] = -9999.0
        self.htOut[self.htOut == np.nan] = -9999.0
        self.depLo[self.depLo == np.nan] = -9999.0
        self.depMid[self.depLo == np.nan] = -9999.0
        self.depHi[self.depLo == np.nan] = -9999.0

    def writeArrayToRaster(self, file, array, lowernd, uppernd):
        """
        Save numpy array as a GeoTiff raster concurrent with the input DEM.

        :param file: Path to save file.
        :param array: Numpy array of data.
        :param lowernd: Lowest data value.
        :param uppernd: Highest data value.

        :return: None
        """
        if array.shape == self.dem.shape:
            ds = self.driverTiff.Create(file, xsize=self.demDS.RasterXSize, ysize=self.demDS.RasterYSize, bands=1, eType=gdal.GDT_Float32)
            ds.SetGeoTransform(self.geot)
            ds.SetProjection(self.prj)
            array[np.isnan(array)] = -9999.0
            array[array < lowernd] = -9999.0
            array[array > uppernd] = -9999.0
            ds.GetRasterBand(1).WriteArray(array)
            ds.GetRasterBand(1).FlushCache()
            ds.GetRasterBand(1).SetNoDataValue(-9999.0)
            ds = None
        else:
            print "output shape different from input DEM"

    def saveOutputs(self):
        """
        Save BDSWEA results to rasters.

        :return: None
        """
        self.writeArrayToRaster(self.outDir + "/pondID.tif", self.idOut, 0.0, 50000.0)
        self.writeArrayToRaster(self.outDir + "/htAbove.tif", self.htOut, -500.0, 5000.0)
        self.writeArrayToRaster(self.outDir + "/depLo.tif", self.depLo, 0.0000001, 20.0)
        self.writeArrayToRaster(self.outDir + "/depMid.tif", self.depMid, 0.0000001, 20.0)
        self.writeArrayToRaster(self.outDir + "/depHi.tif", self.depHi, 0.0000001, 20.0)

    def run(self):
        """
        Run BDSWEA and save outputs.

        :return: None
        """

        print "running BDSWEA"
        self.heightAboveDams()
        self.calculateWaterDepth()
        self.saveOutputs()
        print "calculating pond statistics"
        self.summarizePondStatistics()

    def summarizePondStatistics(self):
        """
        Caclulate area and volume of each pond for each dam height scenario and write results to the input shapefile.

        :return: None
        """

        for i in range(0, self.nPoints):
            feature = self.points.GetFeature(i)
            fid = feature.GetFID()
            lo = np.where(self.idOut == fid, self.depLo, 0.0) #identify cells inundated by dam of FID and get pond depth
            lo[lo == -9999.0] = 0.0
            lo[lo < 0.0] = 0.0 #any pond depths less than 0 get changed to 0.0
            mid = np.where(self.idOut == fid, self.depMid, 0.0)
            mid[mid == -9999.0] = 0.0
            mid[mid < 0.0] = 0.0
            hi = np.where(self.idOut == fid, self.depHi, 0.0)
            hi[hi == -9999.0] = 0.0
            hi[hi <=0.0] = 0.0
            feature.SetField("vol_lo", math.fabs(np.nansum(lo)*self.geot[1]*self.geot[5])) #volume of pond is sum of depths multiplied by cell width and cell height
            feature.SetField("vol_mid", math.fabs(np.nansum(mid) * self.geot[1] * self.geot[5]))
            feature.SetField("vol_hi", math.fabs(np.nansum(hi) * self.geot[1] * self.geot[5]))
            feature.SetField("area_lo", math.fabs(len(np.where(lo != 0.0)[0]) * self.geot[1] * self.geot[5]))
            feature.SetField("area_mid", math.fabs(len(np.where(mid != 0.0)[0]) * self.geot[1] * self.geot[5]))
            feature.SetField("area_hi", math.fabs(len(np.where(hi != 0.0)[0]) * self.geot[1] * self.geot[5]))
            self.points.SetFeature(feature)
            self.points.SyncToDisk()


    def writeSurfaceWSE(self):
        """
        Update DEM to reflect water surface elevation of modeled beaver ponds and save as GeoTiff.

        :return: None
        """
        self.depLo[self.depLo < 0.0] = 0.0
        self.depMid[self.depMid < 0.0] = 0.0
        self.depHi[self.depHi < 0.0] = 0.0
        self.wseLo = self.depLo + self.dem
        self.wseMid = self.depMid + self.dem
        self.wseHi = self.depHi + self.dem
        self.writeArrayToRaster(self.outDir + "/WSESurf_lo.tif", self.wseLo, 0.0, 5000.0)
        self.writeArrayToRaster(self.outDir + "/WSESurf_mid.tif", self.wseMid, 0.0, 5000.0)
        self.writeArrayToRaster(self.outDir + "/WSESurf_hi.tif", self.wseHi, 0.0, 5000.0)

    def writeHead(self):
        """
        Calculate water surface elevation of cells inundated by modeld beaver ponds or represented by the rasterized stream network and save as GeoTiff.

        :return: None
        """
        stream = self.fac
        stream[stream < 1.0] = 0.0
        stream[stream > 0.0] = 1.0
        pondlo = self.depLo
        pondlo[pondlo > 0.0] = 1.0
        pondlo[pondlo < 0.0] = 0.0
        pondlo = pondlo + stream
        pondlo[pondlo > 0.0] = 1.0
        pondmid = self.depMid
        pondmid[pondmid > 0.0] = 1.0
        pondmid[pondmid < 0.0] = 0.0
        pondmid = pondmid +stream
        pondmid[pondmid > 0.0] = 1.0
        pondhi = self.depHi
        pondhi[pondhi > 0.0] = 1.0
        pondhi[pondhi < 0.0] = 0.0
        pondhi = pondhi + stream
        pondhi[pondhi > 0.0] = 1.0
        self.writeArrayToRaster(self.outDir + "/head_start.tif", self.dem*stream, 1.0, 5000.0)
        self.writeArrayToRaster(self.outDir + "/head_lo.tif", self.wseLo*pondlo, 1.0, 5000.0)
        self.writeArrayToRaster(self.outDir + "/head_mid.tif", self.wseMid*pondmid, 1.0, 5000.0)
        self.writeArrayToRaster(self.outDir + "/head_hi.tif", self.wseHi*pondhi, 1.0, 5000.0)

    def writeModflowFiles(self):
        """
        Save files to be used with BDflopy for MODFLOW parameterization.

        :return: None
        """
        self.writeSurfaceWSE()
        self.writeHead()
        del self.wseLo
        del self.wseMid
        del self.wseHi

    def close(self):
        """
        Close all GDAL and OGR datasets.

        :return: None
        """
        # sys.setrecursionlimit(self.origrecursion)
        self.demDS = None
        self.fdirDS = None
        self.idDS = None
        self.pointDS = None
        self.points = None
        del self.dem
        del self.fdir
        del self.fac
        del self.depLo
        del self.depMid
        del self.depHi
        del self.htOut
        del self.idOut