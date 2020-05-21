#---------------------------------------------------------#
#   BRAT Layer Correction Tool                            #
#                                                         #
#       Author: Maggie Hallerud                           #
#               maggie.hallerud@aggiemail.usu.edu         #
#       Date: 4/15/2020                                   #
#                                                         #
# Purpose: Fixes layer data sources in BRAT project by    #
#       recreating all layers. Set up for batch running.  #
#                                                         #
#---------------------------------------------------------#





# user-defined filepaths
pf_path = 'C:/Users/a02046349/Downloads' # projectwide folder
pybrat_path = 'C:/Users/a02046349/Desktop/pyBRAT' # pybrat folder
#run_folder = 'BatchRun_03' # path for run folder

# load dependencies and set up environment
import sys
import os
import arcpy
import glob
sys.path.append(pybrat_path)
from SupportingFunctions import make_layer
from Constraints_Opportunities import make_layers as ConsRest_layers
from Comb_FIS import make_layers as combFIS_layers
from Veg_FIS import make_layers as vegFIS_layers
from iHyd import make_layers as iHyd_layers
from BRAT_table import make_layers as Table_layers
from BRATProject import make_layers as input_layers

brat_symbology_dir = os.path.join(pybrat_path, "BRATSymbology")

arcpy.env.overwriteOutput=True
arcpy.CheckOutExtension('Spatial')

def main():

    # get list of all folders in project folder
    os.chdir(pf_path)

    dir_list = filter(lambda x: os.path.isdir(x), os.listdir('.'))
    for dir in dir_list[:]:
        if dir.startswith('00_'):
            dir_list.remove(dir)

    # create layers for each huc8 folder
    for dir in dir_list:
            print "------------------------------------------------"
            print "Correcting layers for " + dir
            # this may need to be modified depending on your folder structure
            project_folder = os.path.join(pf_path, dir)#, "BRAT", run_folder)

            # find paths for BRAT outputs
            brat_table = os.path.join(project_folder, "Outputs/Output_01/01_Intermediates/BRAT_Table.shp")
            comb_cap = os.path.join(project_folder, "Outputs/Output_01/02_Analyses/Combined_Capacity_Model.shp")
            cons_rest = os.path.join(project_folder, "Outputs/Output_01/02_Analyses/Conservation_Restoration_Model.shp")
            intermediates_folder = os.path.dirname(brat_table)
            analysis_folder = os.path.dirname(comb_cap)

            # find paths for BRAT inputs
            ex_veg_files = find_file(project_folder, "Inputs/*[0-9]*_Vegetation/*[0-9]*_ExistingVegetation/Ex_Veg_*[0-9]*/*.img")
            if len(ex_veg_files) > 0:
                ex_veg = ex_veg_files
            else:
                ex_veg = None
            hist_veg_files = find_file(project_folder, "Inputs/*[0-9]*_Vegetation/*[0-9]*_HistoricVegetation/Hist_Veg_*[0-9]*/*.img")
            if len(hist_veg_files) > 0:
                hist_veg = hist_veg_files
            else:
                hist_veg = None
            network_files = find_file(project_folder, "Inputs/*[0-9]*_Network/Network_*[0-9]*/*.shp")
            if len(network_files) > 0:
                network = network_files
            else:
                network = None
            dem_files = find_file(project_folder, "Inputs/*[0-9]*_Topography/DEM_*[0-9]*/dem*.tif")
            if len(dem_files) > 0:
                dem = dem_files
            else:
                dem = None
            hillshade_files = find_file(project_folder, "Inputs/*[0-9]*_Topography/DEM_*[0-9]*/Hillshade/*.tif")
            if len(hillshade_files) > 0:
                hillshade = hillshade_files
            else:
                hillshade = None
            flow_files = find_file(project_folder, "Inputs/*[0-9]*_Topography/DEM_*[0-9]*/Flow/*.tif")
            if len(flow_files) > 0:
                flow = flow_files
            else:
                flow = None
            slope_files = find_file(project_folder, "Inputs/*[0-9]*_Topography/DEM_*[0-9]*/Slope/*.tif")
            if len(slope_files) > 0:
                slope = slope_files
            else:
                slope = None
            valley_files = find_file(project_folder, "Inputs/*[0-9]*_Anthropogenic/*[0-9]*_ValleyBottom/Valley_*[0-9]*/*.shp")
            if len(valley_files) > 0:
                valley = valley_files
            else:
                valley = None
            road_files = find_file(project_folder, "Inputs/*[0-9]*_Anthropogenic/*[0-9]*_Roads/Roads_*[0-9]*/*.shp")
            if len(road_files) >0:
                road = road_files
            else:
                road = None
            rail_files = find_file(project_folder, "Inputs/*[0-9]*_Anthropogenic/*[0-9]*_Railroads/Railroads_*[0-9]*/*.shp")
            if len(rail_files)>0:
                rail = rail_files
            else:
                rail = None
            canal_files = find_file(project_folder, "Inputs/*[0-9]*_Anthropogenic/*[0-9]*_Canals/Canals_*[0-9]*/canals.shp")
            if len(canal_files) > 0:
                canal = canal_files
            else:
                canal = None
            landuse_files = find_file(project_folder, "Inputs/*[0-9]*_Anthropogenic/*[0-9]*_LandUse/Land_Use_*[0-9]*/*.img")
            if len(landuse_files)>0:
                landuse = landuse_files
            else:
                landuse = None
            diversion_files = find_file(project_folder, "Inputs/*[0-9]*_Anthropogenic/*[0-9]*_Canals/Canals_*[0-9]*/points_of_diversion.shp")
            if len(diversion_files) > 0:
                diversion_pts = diversion_files
            else:
                diversion_pts = None
                
            # define symbology layers
            ex_veg_suit = os.path.join(brat_symbology_dir, 'Existing_Veg_Suitability.lyr')
            ex_veg_rip = os.path.join(brat_symbology_dir, 'Existing_Veg_Riparian.lyr')
            ex_veg_name = os.path.join(brat_symbology_dir, 'Existing_Veg_EVT_Name.lyr')
            ex_veg_type = os.path.join(brat_symbology_dir, 'Existing_Veg_EVT_Type.lyr')
            ex_veg_class = os.path.join(brat_symbology_dir, 'Existing_Veg_EVT_Class.lyr')
            hist_veg_suit = os.path.join(brat_symbology_dir, 'Historic_Veg_Suitability.lyr')
            hist_veg_rip = os.path.join(brat_symbology_dir, 'Historic_Veg_Riparian.lyr')
            hist_veg_name = os.path.join(brat_symbology_dir, 'Historic_Veg_BPS_Name.lyr')
            hist_veg_group = os.path.join(brat_symbology_dir, 'Historic_Veg_BPS_Type.lyr')
            network_symbology = os.path.join(brat_symbology_dir, "Network.lyr")
            landuse_symbology = os.path.join(brat_symbology_dir, "Land_Use_Raster.lyr")
            land_ownership_symbology = os.path.join(brat_symbology_dir, "SurfaceManagementAgency.lyr")
            canals_symbology = os.path.join(brat_symbology_dir, "CanalsDitches.lyr")
            roads_symbology = os.path.join(brat_symbology_dir, "Roads.lyr")
            railroads_symbology = os.path.join(brat_symbology_dir, "Railroads.lyr")
            valley_bottom_symbology = os.path.join(brat_symbology_dir, "ValleyBottom_Fill.lyr")
            valley_bottom_outline_symbology = os.path.join(brat_symbology_dir, "ValleyBottom_Outline.lyr")
            flow_direction_symbology = os.path.join(brat_symbology_dir, "FlowDirection.lyr")
            dem_symbology = os.path.join(brat_symbology_dir, "DEM.lyr")
            hs_symbology = os.path.join(brat_symbology_dir, "Hillshade.lyr")
            slope_symbology = os.path.join(brat_symbology_dir, "Slope.lyr")
            flow_symbology = os.path.join(brat_symbology_dir, "Flow_Accumulation.lyr")

            dist_to_infrastructure_symbology = os.path.join(brat_symbology_dir, "DistancetoClosestInfrastructure.lyr")
            dist_to_road_in_valley_bottom_symbology = os.path.join(brat_symbology_dir, "DistancetoRoadinValleyBottom.lyr")
            dist_to_road_crossing_symbology = os.path.join(brat_symbology_dir, "DistancetoRoadCrossing.lyr")
            dist_to_road_symbology = os.path.join(brat_symbology_dir, "DistancetoRoad.lyr")
            dist_to_railroad_in_valley_bottom_symbology = os.path.join(brat_symbology_dir, "DistancetoRailroadinValleyBottom.lyr")
            dist_to_railroad_symbology = os.path.join(brat_symbology_dir, "DistancetoRailroad.lyr")
            dist_to_canal_symbology = os.path.join(brat_symbology_dir, "DistancetoCanal.lyr")
            pts_diversion_symbology = os.path.join(brat_symbology_dir, "PointsofDiversion.lyr")
            dist_to_pts_diversion_symbology = os.path.join(brat_symbology_dir, "DistancetoPointsofDiversion.lyr")
            land_use_symbology = os.path.join(brat_symbology_dir, "LandUseIntensity.lyr")
            land_ownership_per_reach_symbology = os.path.join(brat_symbology_dir, "LandOwnershipperReach.lyr")
            priority_translocations_symbology = os.path.join(brat_symbology_dir, "PriorityBeaverTranslocationAreas.lyr")
            reach_slope_symbology = os.path.join(brat_symbology_dir, "ReachSlope.lyr")
            drain_area_symbology = os.path.join(brat_symbology_dir, "UpstreamDrainageArea.lyr")
            buffer_30m_symbology = os.path.join(brat_symbology_dir, "buffer_30m.lyr")
            buffer_100m_symbology = os.path.join(brat_symbology_dir, "buffer_100m.lyr")
            perennial_symbology = os.path.join(brat_symbology_dir, "Perennial.lyr")

            baseflow_symbology = os.path.join(brat_symbology_dir, "BaseflowStreampower.lyr")
            highflow_symbology = os.path.join(brat_symbology_dir, "HighflowStreamPower.lyr")

            ex_veg_cap = os.path.join(brat_symbology_dir, "ExistingVegDamBuildingCapacity.lyr")
            hist_veg_cap = os.path.join(brat_symbology_dir, "HistoricVegDamBuildingCapacity.lyr")
            anabranch = os.path.join(brat_symbology_dir, "AnabranchTypes.lyr")

            existing_capacity = os.path.join(brat_symbology_dir, "ExistingDamBuildingCapacity.lyr")
            historic_capacity = os.path.join(brat_symbology_dir, "HistoricDamBuildingCapacity.lyr")
            existing_complex = os.path.join(brat_symbology_dir, "ExistingDamComplexSize.lyr")
            historic_complex = os.path.join(brat_symbology_dir, "HistoricDamComplexSize.lyr")

            conservation_rest = os.path.join(brat_symbology_dir, "RestorationorConservationOpportunities.lyr")
            undesirable = os.path.join(brat_symbology_dir, "RiskofUndesirableDams.lyr")
            unsuitable = os.path.join(brat_symbology_dir, "UnsuitableorLimitedDamBuildingOpportunities.lyr")

            # make layers
            try:
                #input_layers(ex_veg_files, hist_veg_files, network_files, topo_folder, landuse_files,
                #         valley_files, road_files, rail_files, canals_files, [], []) # make input layers
                if ex_veg is not None:
                    print "............Correcting existing veg"
                    for f in ex_veg:
                        folder = os.path.dirname(f)
                        lyrs = glob.glob(os.path.join(folder, "*.lyr"))
                        if len(lyrs)>0:
                            for l in lyrs:
                                try:
                                    os.remove(l)
                                except Exception:
                                    pass
                        try:
                            make_layer(folder, f, "Existing Vegetation Suitability for Beaver Dam Building", symbology_layer=ex_veg_suit, is_raster=True, file_name='ExVegSuitability')
                        except Exception as err:
                            print "------Failed to make existing veg suitability lyr"
                            #print err    
                        try:
                            make_layer(folder, f, "Existing Riparian", symbology_layer = hist_veg_rip, is_raster=True)
                        except Exception as err:
                            print "------Failed to make existing riparian lyr"
                            #print err
                        #try:
                        #    make_layer(folder, f, "Veg Type - EVT Name", symbology_lyr = ex_veg_name, is_raster=True, symbology_field = 'EVT_Name')
                        #except Exception as err:
                        #    print "------Failed to make existing veg EVT Name layer"
                        #    #print err
                        #try:
                        #    make_layer(folder, f, "Veg Type - EVT Type", symbology_lyr = ex_veg_type, is_raster=True, symbology_field = 'E)
                        #except Exception as err:
                        #    print "------Failed to make existing veg EVT Type layer"
                        #    #print err
                        #try:
                        #    make_layer(folder, f, "Veg Type - EVT Class", symbology_lyr = ex_veg_class, is_raster=True)
                        #except Exception as err:
                        #    print "-------Failed to make existing veg EVT Class layer"
                        #    print #err
                if hist_veg is not None:
                    print "............Correcting historic veg"
                    for f in hist_veg:
                        folder = os.path.dirname(f)
                        lyrs = glob.glob(os.path.join(folder, "*.lyr"))
                        if len(lyrs) > 0:
                            for l in lyrs:
                                try:
                                    os.remove(l)
                                except Exception:
                                    pass
                        try:
                            make_layer(folder, f, "Historic Vegetation Suitability for Beaver Dam Building", symbology_layer=ex_veg_suit, is_raster=True, file_name="Historic_Veg_Suitability")
                        except Exception as err:
                            print "------Failed to make historic veg suitability lyr"
                            #print err
                        try:
                            make_layer(folder, f, "Historic Riparian", symbology_layer = hist_veg_rip, is_raster=True)
                        except Exception as err:
                            print "------Failed to make historic riparian lyr"
                            #print err
                        #try:
                        #    make_layer(folder, f, "Veg Type - BPS Name", symbology_layer = hist_veg_name, is_raster=True, file_name="Historic_Veg_BPS_Name")
                        #except Exception as err:
                        #    print "------Failed to make historic veg BPS name lyr"
                        #    #print err
                        #try:
                        #    make_layer(folder, f, "Veg Type - BPS Type", symbology_layer = hist_veg_group, is_raster=True)
                        #except Exception as err:
                        #    print "------Failed to make historic veg BPS type lyr"
                        #    #print err
                if network is not None:
                    print "............Correcting network"
                    for f in network:
                        folder = os.path.dirname(f)
                        lyrs = glob.glob(os.path.join(folder, "*.lyr"))
                        if len(lyrs) > 0:
                            for l in lyrs:
                                try:
                                    os.remove(l)
                                except Exception:
                                    pass
                        try:
                            make_layer(folder, f, "Network", symbology_layer = network_symbology)
                        except Exception as err:
                            print "------Failed to make network lyr"
                            #print err
                        try:
                            make_layer(folder, f, "Flow Direction", symbology_layer = flow_direction_symbology)
                        except Exception as err:
                            print "------Failed to make flow direction lyr"
                            #print err
                if landuse is not None:
                    print "............Correcting landuse"
                    for f in landuse:
                        folder = os.path.dirname(f)
                        lyrs = glob.glob(os.path.join(folder, "*.lyr"))
                        if len(lyrs) > 0:
                            for l in lyrs:
                                try:
                                    os.remove(l)
                                except Exception:
                                    pass
                        try:
                            make_layer(folder, f, "Land Use Raster", symbology_layer = landuse_symbology, is_raster=True)
                        except Exception as err:
                            print "------Failed to make landuse lyr"
                            #print err
                if canal is not None:
                    print "............Correcting canals"
                    for f in canal:
                        folder = os.path.dirname(f)
                        lyrs = glob.glob(os.path.join(folder, "*.lyr"))
                        if len(lyrs) > 0:
                            for l in lyrs:
                                try:
                                    os.remove(l)
                                except Exception:
                                    pass
                        try:
                            make_layer(folder, f, "Canals & Ditches", symbology_layer = canals_symbology)
                        except Exception as err:
                            print "------Failed to make canals lyr"
                            #print err
                if road is not None:
                    print "............Correcting roads"
                    for f in road:
                        folder = os.path.dirname(f)
                        lyrs = glob.glob(os.path.join(folder, "*.lyr"))
                        if len(lyrs) > 0:
                            for l in lyrs:
                                try:
                                    os.remove(l)
                                except Exception:
                                    pass
                        try:
                            make_layer(folder, f, "Roads", symbology_layer = roads_symbology)
                        except Exception as err:
                            print "------Failed to make roads lyr"
                            #print err
                if rail is not None:
                    print "............Correcting rails"
                    for f in rail:
                        folder = os.path.dirname(f)
                        lyrs = glob.glob(os.path.join(folder, "*.lyr"))
                        if len(lyrs) > 0:
                            for l in lyrs:
                                try:
                                    os.remove(l)
                                except Exception:
                                    pass
                        try:
                            make_layer(folder, f, "Railroads", symbology_layer = railroads_symbology)
                        except Exception as err:
                            print "------Failed to make railroads lyr"
                            #print err
                if valley is not None:
                    print "............Correcting valley bottom"
                    for f in valley:
                        folder = os.path.dirname(f)
                        lyrs = glob.glob(os.path.join(folder, "*.lyr"))
                        if len(lyrs) > 0:
                            for l in lyrs:
                                try:
                                    os.remove(l)
                                except Exception:
                                    pass
                        try:
                            make_layer(folder, f, "Valley Bottom Outline", symbology_layer = valley_bottom_outline_symbology)
                        except Exception as err:
                            print "------Failed to make valley bottom outline lyr"
                            #print err
                        try:
                            make_layer(folder, f, "Valley Bottom Fill", symbology_layer = valley_bottom_symbology)
                        except Exception as err:
                            print "------Failed to make valley bottom fill lyr"
                            #print err
                if dem is not None:
                    print "............Correcting DEM"
                    for f in dem:
                        folder = os.path.dirname(f)
                        lyrs = glob.glob(os.path.join(folder, "*.lyr"))
                        if len(lyrs) > 0:
                            for l in lyrs:
                                try:
                                    os.remove(l)
                                except Exception:
                                    pass
                        try:
                            make_layer(folder, f, "DEM", symbology_layer=dem_symbology, is_raster=True)
                        except Exception as err:
                            print "------Failed to make DEM lyr"
                            #print err
                if hillshade is not None:
                    print "............Correcting hillshade"
                    for f in hillshade:
                        folder = os.path.dirname(f)
                        lyrs = glob.glob(os.path.join(folder, "*.lyr"))
                        if len(lyrs) > 0:
                            for l in lyrs:
                                try:
                                    os.remove(l)
                                except Exception:
                                    pass
                        try:
                            make_layer(folder, f, "Hillshade", symbology_layer=hs_symbology, is_raster=True)
                        except Exception as err:
                            print "------Failed to make hillshade lyr"
                            #print err
                if flow is not None:
                    print "............Correcting flow accumulation"
                    for f in flow:
                        folder = os.path.dirname(f)
                        lyrs = glob.glob(os.path.join(folder, "*.lyr"))
                        if len(lyrs) > 0:
                            for l in lyrs:
                                try:
                                    os.remove(l)
                                except Exception:
                                    pass
                        try:
                            make_layer(folder, f, "Flow Accumulation", symbology_layer=flow_symbology, is_raster=True)
                        except Exception as err:
                            print "------Failed to make flow accumulation lyr"
                            #print err
                if slope is not None:
                    print "............Correcting slope"
                    for f in slope:
                        folder = os.path.dirname(f)
                        lyrs = glob.glob(os.path.join(folder, "*.lyr"))
                        if len(lyrs) > 0:
                            for l in lyrs:
                                try:
                                    os.remove(l)
                                except Exception:
                                    pass
                        try:
                            make_layer(folder, f, "Slope", symbology_layer=slope_symbology, is_raster=True)
                        except Exception as err:
                            print "------Failed to make slope lyr"
                            #print err
            except Exception as err:
                #print "----------------------------------------------------"
                print "     " + "BRAT PROJECT LAYERS CORRECTION FAILED!"
                print "     " + "Error thrown:"
                print err
            try:
                #Table_layers(brat_table, diversion_pts) # make intermediate layers
                buffer30_list = find_file(intermediates_folder, "*[0-9]*_Buffers/buffer_30m.shp")
                if len(buffer30_list)>0:
                    buffer30 = buffer30_list
                else:
                    buffer30 = None
                buffer100_list = find_file(intermediates_folder, "*[0-9]*_Buffers/buffer_100m.shp")
                if len(buffer100_list)>0:
                    buffer100 = buffer100_list
                else:
                    buffer100 = None
                topo_folder = find_file(intermediates_folder, "*[0-9]*_TopographicMetrics")[0]
                lyrs = find_file(topo_folder, "*.lyr")
                if len(lyrs)>0:
                    for l in lyrs:
                        try:
                            os.remove(l)
                        except Exception:
                            pass
                anthropogenic_metrics_folder = find_file(intermediates_folder, "*[0-9]*_AnthropogenicMetrics")[0]
                lyrs = find_file(anthropogenic_metrics_folder, "*.lyr")
                if len(lyrs)>0:
                    for l in lyrs:
                        try:
                            os.remove(l)
                        except Exception:
                            pass
                if buffer30 is not None:
                    print "............Correcting 30 m buffer"
                    for f in buffer30:
                        folder = os.path.dirname(f)
                        lyrs = find_file(folder, "*.lyr")
                        if len(lyrs) > 0:
                            for l in lyrs:
                                try:
                                    os.remove(l)
                                except Exception:
                                    pass
                        try:
                            make_layer(folder, f, "30 m Buffer", symbology_layer=buffer_30m_symbology)
                        except Exception as err:
                            print "-------Failed to make 30m buffer lyr"
                            #print err
                if buffer100 is not None:
                    print "............Correcting 100 m buffer"
                    for f in buffer100:
                        folder = os.path.dirname(f)
                        lyrs = find_file(folder, "*.lyr")
                        if len(lyrs) > 0:
                            for l in lyrs:
                                try:
                                    os.remove(l)
                                except Exception:
                                    pass
                        try:
                            make_layer(folder, f, "100 m Buffer", symbology_layer=buffer_100m_symbology)
                        except Exception as err:
                            print "-------Failed to make 100m buffer lyr"
                            #print err
                try:
                    print "............Correcting reacah slope"
                    make_layer(topo_folder, brat_table, "Reach Slope", reach_slope_symbology)
                except Exception as err:
                    print "------Failed to make reach slope lyr"
                    #print err
                try:
                    print "............Correcting upstream drainage area"
                    make_layer(topo_folder, brat_table, "Upstream Drainage Area", drain_area_symbology)
                except Exception as err:
                    print "------Failed to make upstream drainage area lyr"
                    #print err
                fields = [f.name for f in arcpy.ListFields(brat_table)]
                try:
                    if 'iPC_LU' in fields:
                        print "............Correcting land use intensity"
                        make_layer(anthropogenic_metrics_folder, brat_table, "Land Use Intensity", land_use_symbology, is_raster=False)
                except Exception as err:
                    print "------Failed to make land use intensity lyr"
                    #print err
                try:
                    if 'iPC_RoadX' in fields:
                        print "............Correcting dist to road crossing"
                        make_layer(anthropogenic_metrics_folder, brat_table, "Distance to Road Crossing", dist_to_road_crossing_symbology, is_raster=False, symbology_field ='iPC_RoadX')
                except Exception as err:
                    print "------Failed to make distance to road lyr"
                    #print err
                try:
                    if 'iPC_Road' in fields:
                        print "............Correcting dist to road"
                        make_layer(anthropogenic_metrics_folder, brat_table, "Distance to Road", dist_to_road_symbology, is_raster=False, symbology_field ='iPC_Road')
                except Exception as err:
                    print "------Failed to make distance to road lyr"
                    #print err
                try:
                    if 'iPC_RoadVB' in fields:
                        print "............Correcting dist to road in VB"
                        make_layer(anthropogenic_metrics_folder, brat_table, "Distance to Road in Valley Bottom", dist_to_road_in_valley_bottom_symbology, is_raster=False, symbology_field ='iPC_RoadVB')
                except Exception as err:
                    print "------Failed to make distance to road in valley bottom lyr"
                    #print err
                try:
                    if 'iPC_Rail' in fields:
                        print "............Correcting dist to railroad"
                        make_layer(anthropogenic_metrics_folder, brat_table, "Distance to Railroad", dist_to_railroad_symbology, is_raster=False, symbology_field ='iPC_Rail')
                except Exception as err:
                    print "------Failed to make distance railroad lyr"
                    #print err
                try:
                    if 'iPC_RailVB' in fields:
                        print "............Correcting dist to rail in VB"
                        make_layer(anthropogenic_metrics_folder, brat_table, "Distance to Railroad in Valley Bottom", dist_to_railroad_in_valley_bottom_symbology, is_raster=False, symbology_field ='iPC_RailVB')
                except Exception as err:
                    print "------Failed to make railroad in valley bottom lyr"
                    #print err
                try:
                    if 'iPC_Canal' in fields:
                        print "............Correcting dist to canal"
                        make_layer(anthropogenic_metrics_folder, brat_table, "Distance to Canal", dist_to_canal_symbology, is_raster=False, symbology_field ='iPC_Canal')
                except Exception as err:
                    print "------Failed to make distance to canal lyr"
                    #print err
                try:
                    if 'iPC_DivPts' in fields:
                        print "............Correcting dist to points of diversion"
                        make_layer(anthropogenic_metrics_folder, brat_table, "Distance to Points of Diversion", dist_to_pts_diversion_symbology, is_raster=False, symbology_field='iPC_DivPts')
                except Exception as err:
                    print "------Failed to make distance to points of diversion lyr"
                    #print err
                try:
                    if 'ADMIN_AGEN' in fields:
                        print "............Correcting land ownership per reach"
                        make_layer(anthropogenic_metrics_folder, brat_table, "Land Ownership per Reach", land_ownership_per_reach_symbology, is_raster=False, symbology_field='ADMIN_AGEN')
                except Exception as err:
                    print "------Failed to make land ownership per reach lyr"
                    #print err
                try:
                    if 'iPC_Privat' in fields:
                        print "............Correcting priority beaver translocation"
                        make_layer(anthropogenic_metrics_folder, brat_table, "Priority Beaver Translocation Areas", priority_translocations_symbology, is_raster=False, symbology_field='iPC_Privat')
                except Exception as err:
                    print "------Failed to make priority beaver translocation areas lyr"
                    #print err
                try:
                    if 'oPC_Dist' in fields:
                        print "............Correcting distance to infrastructure"
                        make_layer(anthropogenic_metrics_folder, brat_table, "Distance to Closest Infrastructure", dist_to_infrastructure_symbology, is_raster=False, symbology_field ='oPC_Dist')
                except Exception as err:
                    print "------Failed to make distance to closest infrastructure lyr"
                    #print err
                if diversion_pts is not None:
                    try:
                        print "............Correcting points of diveresion"
                        for f in diversion_pts:
                            folder = os.path.dirname(f)
                            make_layer(folder, f, "Points of Diversion", pts_diversion_symbology)
                    except Exception as err:
                        print "--------Failed to make points of diversion lyr"
                        #print err
                    
            except Exception as err:
                #print "----------------------------------------------------"
                print "     " + "BRAT TABLE LAYERS CORRECTION FAILED!"
                print "     " + "Error thrown:"
                print err
            try:
                #iHyd_layers(brat_table) # make hydrology layers
                    ihyd_folder = find_file(intermediates_folder, "*[0-9]*_Hydrology")[0]
                    lyrs = find_file(ihyd_folder, "*.lyr")
                    if len(lyrs) > 0:
                        for l in lyrs:
                            try:
                                os.remove(l)
                            except Exception:
                                pass
                    try:
                        print "............Correcting baseflow streampower"
                        make_layer(ihyd_folder, brat_table, "Baseflow Streampower", baseflow_symbology)
                    except Exception as err:
                        print "------Failed to make baseflow streampower lyr"
                        #print err
                    try:
                        print "............Correcting highflow streampower"
                        make_layer(ihyd_folder, brat_table, "Highflow Streampower", highflow_symbology)
                    except Exception as err:
                        print "------Failed to make highflow streampower lyr"
                        #print err
            except Exception as err:
                #print "----------------------------------------------------"
                print "     " + "IHYD LAYERS CORRECTION FAILED!"
                print "     " + "Error thrown:"
                print err
            try:
                #vegFIS_layers(brat_table) # make veg capacity layers
                vegfis_folder= find_file(intermediates_folder, "*[0-9]*_VegDamCapacity")[0]
                anabranch_folder =  find_file(intermediates_folder, "*[0-9]*_AnabranchHandler")[0]
                lyrs = find_file(vegfis_folder, "*.lyr")
                if len(lyrs) > 0:
                        for l in lyrs:
                            try:
                                os.remove(l)
                            except Exception:
                                pass
                lyrs = find_file(anabranch_folder, "*.lyr")
                if len(lyrs) > 0:
                        for l in lyrs:
                            try:
                                os.remove(l)
                            except Exception:
                                pass
                try:
                    print "............Correcting existing veg dam building capacity"
                    make_layer(vegfis_folder, brat_table, "Existing Veg Dam Building Capacity", ex_veg_cap)
                except Exception as err:
                    print "------Failed to make existing veg capacity lyr"
                    #print err
                try:
                    print "............Correcting historic veg dam building capacity"
                    make_layer(vegfis_folder, brat_table, "Historic Veg Dam Building Capacity", hist_veg_cap)
                except Exception as err:
                    print "------Failed to make historic veg capacity lyr"
                    #print err
                try:
                    print "............Correcting anabranch types"
                    make_layer(anabranch_folder, brat_table, "Anabranch Types", anabranch)
                except Exception as err:
                    print "------Failed to make anabranch types lyr"
                    #print err
            except Exception as err:
                #print "----------------------------------------------------"
                print "     " + "VEG CAPACITY LAYERS CORRECTION FAILED!"
                print "     " + "Error thrown:"
                print err
            try:
                #combFIS_layers(comb_cap) # make combined capacity layers
                hist_capacity_folder= find_file(analysis_folder, "*[0-9]*_Capacity/01_HistoricCapacity")[0]
                ex_capacity_folder = find_file(analysis_folder, "*[0-9]*_Capacity/02_ExistingCapacity")[0]
                lyrs = find_file(hist_capacity_folder, "*.lyr")
                if len(lyrs) > 0:
                        for l in lyrs:
                            try:
                                os.remove(l)
                            except Exception:
                                pass
                lyrs = find_file(ex_capacity_folder, "*.lyr")
                if len(lyrs) > 0:
                        for l in lyrs:
                            try:
                                os.remove(l)
                            except Exception:
                                pass
                try:
                        print "............Correcting existing capacity"
                        make_layer(ex_capacity_folder, comb_cap, "Existing Dam Building Capacity", existing_capacity)
                except Exception as err:
                        print "------Failed to make existing capacity lyr"
                        #print err
                try:
                        print "............Correcting existing complex size"
                        make_layer(ex_capacity_folder, comb_cap, "Existing Dam Complex Size", existing_complex)
                except Exception as err:
                        print "------Failed to make existing complex size lyr"
                        #print err
                try:
                        print "............Correcting historic capacity"
                        make_layer(hist_capacity_folder, comb_cap, "Historic Dam Building Capacity", historic_capacity)
                except Exception as err:
                        print "------Failed to make historic capacity lyr"
                        #print err
                try:
                        print "............Correcting historic complex size"
                        make_layer(hist_capacity_folder, comb_cap, "Historic Dam Complex Size", historic_complex)
                except Exception as err:
                        print "------Failed to make historic complex size lyr"
                        #print err
            except Exception as err:
                #print "----------------------------------------------------"
                print "     " + "COMBINED CAPACITY LAYERS CORRECTION FAILED!" + dir
                print "     " + "Error thrown:"
                print err
            try:
                #ConsRest_layers(cons_rest) # make management layers
                management_dir = find_file(analysis_folder, "*[0-9]_Management")[0]
                lyrs = find_file(management_dir, "*.lyr")
                if len(lyrs) > 0:
                        for l in lyrs:
                            try:
                                os.remove(l)
                            except Exception:
                                pass
                try:
                        print "............Correcting conservation restoration"
                        make_layer(management_dir, cons_rest, "Restoration or Conservation Opportunities", conservation_rest)
                except Exception as err:
                        print "------Failed to make conservation restoration lyr"
                        #print err
                try:
                        print "............Correcting risk of undesirable dams"
                        make_layer(management_dir, cons_rest, "Risk of Undesirable Dams", undesirable)
                except Exception as err:
                        print "------Failed to make risk of undesirable dams lyr"
                        #print err
                try:
                        print "............Correcting unsuitable or limited opportunities"
                        make_layer(management_dir, cons_rest, "Unsuitable or Limited Dam Building Opportunities", unsuitable)
                except Exception as err:
                        print "------Failed to unsuitable limited lyr"
                        #print err
            except Exception as err:
                #print "----------------------------------------------------"
                print "     " + "CONSERVATION RESTORATION LAYERS CORRECTION FAILED!" + dir
                print "     " + "Error thrown:"
                print err


def find_file(proj_path, file_pattern):

    search_path = os.path.join(proj_path, file_pattern)
    if len(glob.glob(search_path)) > 0:
        file_path = glob.glob(search_path)
    else:
        file_path = []

    return file_path


if __name__ == "__main__":
    main()
