##------------------------------------------------------------------------##
## Name: Batch KMZ Creator                                                ##
## Purpose: Creates KMZ files for each of the major BRAT outputs for each ##
##           BRAT project in a BRAT directory.                            ##
## Note: To run properly, the project folder must match previously        ##
##         specified project folder formats                               ##
##                                                                        ##
## Author: Maggie Hallerud                                                ##
##         maggie.hallerud@aggiemail.usu.edu                              ##
##                                                                        ##
## Date Created: 07/2019                                                  ##
##------------------------------------------------------------------------##


# set file paths
pf_path = 'C:/Users/a02046349/Desktop/GYE_BRAT/wrk_Data'
run_folder = 'BatchRun_03'
symbology_folder = 'C:/Users/a02046349/Desktop/pyBRAT/BRATSymbology'
make_full_kmzs = False

# load dependencies
import arcpy
import os
import sys
import glob
sys.path.append(os.path.dirname(symbology_folder))
from SupportingFunctions import find_folder, make_layer


def main():
        arcpy.env.overwriteOutput=True
        
        #make list of watersheds in project folder
        os.chdir(pf_path)
        dir_list = filter(lambda x: os.path.isdir(x), os.listdir('.'))
        
        # remove folders in the list that start with '00_' since these aren't our huc8 folders
        for dir in dir_list[:]:
                if dir.startswith('00_'):
                        dir_list.remove(dir)

        for dir in dir_list:
                # find proper output/project folder for each watershed
                proj_path = os.path.join(pf_path, dir, 'BRAT', run_folder)
                output_folder = os.path.join(proj_path, 'Outputs/Output_01')  

                print 'Making KMZs for ' + dir

                # find summary products KMZ folder
                kmz_folder = os.path.join(proj_path, 'SummaryProducts/KMZ')
                if not os.path.exists(kmz_folder):
                        os.mkdir(kmz_folder)
                full_kmz_folder = os.path.join(kmz_folder, 'FullNetwork')
                if not os.path.exists(full_kmz_folder):
                        os.mkdir(full_kmz_folder)
                peren_kmz_folder = os.path.join(kmz_folder, 'PerennialNetwork')
                if not os.path.exists(peren_kmz_folder):
                        os.mkdir(peren_kmz_folder)

                # find all needed shapefiles	
                perennial = os.path.join(pf_path, dir, 'NHD/NHD_24k_Perennial_CanalsDitches.shp')
                brat_table = os.path.join(output_folder, '01_Intermediates/BRAT_Table.shp')
                capacity = os.path.join(output_folder, '02_Analyses/Combined_Capacity_Model.shp')
                conservation = os.path.join(output_folder, '02_Analyses/Conservation_Restoration_Model.shp')
                validation = os.path.join(output_folder, '02_Analyses/Data_Capture_Validation.shp')
                # find all needed layers
                existing_capacity = os.path.join(output_folder, '02_Analyses/01_Capacity/02_ExistingCapacity/ExistingDamBuildingCapacity.lyr')
                existing_complex = os.path.join(output_folder, '02_Analyses/01_Capacity/02_ExistingCapacity/ExistingDamComplexSize.lyr')
                historic_capacity = os.path.join(output_folder, '02_Analyses/01_Capacity/01_HistoricCapacity/HistoricDamBuildingCapacity.lyr')
                historic_complex = os.path.join(output_folder, '02_Analyses/01_Capacity/01_HistoricCapacity/HistoricDamComplexSize.lyr')
                cons_rest = os.path.join(output_folder, '02_Analyses/02_Management/RestorationorConservationOpportunities.lyr')
                risk = os.path.join(output_folder, '02_Analyses/02_Management/RiskofUndesirableDams.lyr')
                #strategies = os.path.join(output_folder, '02_Analyses/02_Management/StrategiestoPromoteDamBuilding.lyr')
                unsuitable = os.path.join(output_folder, '02_Analyses/02_Management/UnsuitableorLimitedDamBuildingOpportunities.lyr')
                remaining = os.path.join(output_folder, '02_Analyses/03_Validation/PercentofHistoricDamCapacityRemaining.lyr')
                predvsurv = os.path.join(output_folder, '02_Analyses/03_Validation/PredictedDamCountvs.SurveyedDamCount.lyr')
                dam_strats = os.path.join(output_folder, '02_Analyses/03_Validation/CurrentBeaverDamManagementStrategies.lyr')
                occ_dams = os.path.join(output_folder, '02_Analyses/03_Validation/PercentofExistingCapacityOccupiedbySurveyedDams.lyr')
                dams = glob.glob(os.path.join(proj_path, 'Inputs/*[0-9]*_BeaverDams/Beaver_Dam_01/*.lyr'))
                
                # make KMZs for all capacity layers
                if os.path.exists(capacity):
                        # make full network capacity layers
                        if make_full_kmzs == True:
                                print '.....Making full network capacity outputs'
                                make_kmz(existing_capacity, 'Existing_Dam_Building_Capacity', full_kmz_folder)
                                make_kmz(historic_capacity, 'Historic_Dam_Building_Capacity', full_kmz_folder)
                                make_kmz(existing_complex, 'Existing_Dam_Complex_Size', full_kmz_folder)
                                make_kmz(historic_complex, 'Historic_Dam_Complex_Size', full_kmz_folder)

                        print '.....Making perennial capacity outputs'
                        try:
                                # make capacity clip if needed
                                capacity_clip = capacity.split('.')[0] + "_Perennial.shp"
                                if not os.path.exists(capacity_clip):
                                        arcpy.Clip_analysis(capacity, perennial, capacity_clip)
                                # make perennial layer for each capacity output then convert to KMZ
                                peren_existing_capacity = make_layer(output_folder=os.path.dirname(existing_capacity), layer_base=capacity_clip, new_layer_name='Existing Dam Building Capacity',
                                           symbology_layer=existing_capacity, file_name="ExistingDamBuildingCapacity_Perennial")
                                make_kmz(peren_existing_capacity, "Existing_Dam_Building_Capacity", peren_kmz_folder)
                                peren_historic_capacity = make_layer(output_folder=os.path.dirname(historic_capacity), layer_base=capacity_clip, new_layer_name='Historic Dam Building Capacity',
                                           symbology_layer=historic_capacity, file_name="HistoricDamBuildingCapacity_Perennial")
                                make_kmz(peren_historic_capacity, "Historic_Dam_Building_Capacity", peren_kmz_folder)
                                peren_existing_complex = make_layer(output_folder=os.path.dirname(existing_complex), layer_base=capacity_clip, new_layer_name='Existing Dam Complex Size',
                                           symbology_layer=existing_complex, file_name="ExistingDamComplexSize_Perennial")
                                make_kmz(peren_existing_complex, "Existing_Dam_Complex_Size", peren_kmz_folder)
                                peren_historic_complex = make_layer(output_folder=os.path.dirname(historic_complex), layer_base=capacity_clip, new_layer_name='Historic Dam Complex Size',
                                           symbology_layer=historic_complex, file_name="HistoricDamComplexSize_Perennial")
                                make_kmz(peren_historic_complex, "Historic_Dam_Complex_Size", peren_kmz_folder)
                        except Exception as err:
                                print err
                else:
                        print '.....ERROR! Combined capacity output not found. No capacity KMZs made.'

                # make KMZs for all conservation/restoration layers
                if os.path.exists(conservation):
                        #make full network management outputs
                        if make_full_kmzs == True:
                                print '.....Making full network management outputs.....'
                                make_kmz(cons_rest, 'Restoration_or_Conservation_Opportunities', full_kmz_folder)
                                make_kmz(risk, 'Risk_of_Undesirable_Dams', full_kmz_folder)
                                #make_kmz(strategies, 'Stragegies_to_Promote_Dam_Building', full_kmz_folder)
                                make_kmz(unsuitable, 'Unsuitable_or_Limited_Dam_Building_Opportunities', full_kmz_folder)

                        print '.....Making perennial network management outputs.....'
                        try:
                                # make conservation restoration clip if needed
                                conservation_clip = conservation.split('.')[0]+"_Perennial.shp"
                                if not os.path.exists(conservation_clip):
                                        arcpy.Clip_analysis(conservation, perennial, conservation_clip)
                                # make perennial layer for each management output then convert to KMZ
                                peren_cons_rest = make_layer(output_folder=os.path.dirname(cons_rest), layer_base=conservation_clip, new_layer_name='Conservation Restoration Opportunities',
                                           symbology_layer=cons_rest, file_name="ConservationRestorationOpportunities_Perennial")
                                make_kmz(peren_cons_rest, 'Restoration_or_Conservation_Opportunities', peren_kmz_folder)
                                peren_risk = make_layer(output_folder=os.path.dirname(risk), layer_base=conservation_clip, new_layer_name='Risk of Undesirable Dams',
                                           symbology_layer=risk, file_name="RiskofUndesirableDams_Perennial")
                                make_kmz(peren_risk, 'Risk_of_Undesirable_Dams', peren_kmz_folder)
                                #peren_strategies = make_layer(output_folder=os.path.dirname(strategies), layer_base=conservation_clip, new_layer_name='Strategies to Promote Dam Building',
                                #           symbology_layer=strategies, file_name="StrategiestoPromoteDamBuilding_Perennial")
                                #make_kmz(peren_strategies, 'Stragegies_to_Promote_Dam_Building', peren_kmz_folder)
                                peren_unsuitable = make_layer(output_folder=os.path.dirname(unsuitable), layer_base=conservation, new_layer_name='Unsuitable or Limited Dam Building Opportunities',
                                           symbology_layer=unsuitable, file_name="UnsuitableorLimitedOpportunities_Perennial")
                                make_kmz(peren_unsuitable, 'Unsuitable_or_Limited_Dam_Building_Opportunities', peren_kmz_folder)
                        except Exception as err:
                                print err
                else:
                        print '.....ERROR! Conservation restoration output not found. No management KMZs made.'

                
                if os.path.exists(validation):
                        #make full network validation outputs
                        if make_full_kmzs == True:
                                print '.....Making full network validation outputs.....'
                                make_kmz(remaining, 'Percent_of_Historic_Capacity_Remaining', full_kmz_folder)
                                make_kmz(predvsurv, 'Predicted_Dam_Density_vs_Surveyed_Dam_Density', full_kmz_folder)
                                make_kmz(dam_strats, 'Current_Beaver_Dam_Management_Strategies', full_kmz_folder)
                                make_kmz(occ_dams, 'Percent_Existing_Capacity_Occupied_by_Surveyed_Dams', full_kmz_folder)
                                

                        print '.....Making perennial network validation outputs.....'
                        try:
                                # make validation clip if needed
                                validation_clip = validation.split('.')[0]+"_Perennial.shp"
                                if not os.path.exists(validation_clip):
                                        arcpy.Clip_analysis(validation, perennial, validation_clip)
                                # make perennial layer for each validation output then convert to KMZ
                                peren_remaining = make_layer(output_folder=os.path.dirname(remaining), layer_base=validation_clip, new_layer_name='Percent of Historic Dam Capacity Remaining',
                                           symbology_layer=remaining, file_name="PercentofHistoricDamCapacityRemaining_Perennial")
                                make_kmz(peren_remaining, 'Percent_of_Historic_Capacity_Remaining', peren_kmz_folder)
                                peren_predvsurv = make_layer(output_folder=os.path.dirname(predvsurv), layer_base=validation_clip, new_layer_name='Predicted Dam Density vs. Surveyed Dam Density',
                                           symbology_layer=risk, file_name="PredictedDamDensityvs.SurveyedDamDensity_Perennial")
                                make_kmz(peren_predvsurv, 'Predicted_Dam_Density_vs_Surveyed_Dam_Density', peren_kmz_folder)
                                peren_dam_strats = make_layer(output_folder=os.path.dirname(dam_strats), layer_base=validation_clip, new_layer_name='Current Beaver Dam Management Strategies',
                                           symbology_layer=dam_strats, file_name="CurrentBeaverDamManagementStrategies_Perennial")
                                make_kmz(peren_dam_strats, 'Current_Beaver_Dam_Management_Strategies', peren_kmz_folder)
                                peren_occ_dams = make_layer(output_folder=os.path.dirname(occ_dams), layer_base=validation_clip, new_layer_name='Percent of Existing Capacity Occupied By Surveyed Dams',
                                           symbology_layer=dam_strats, file_name="PercentofExistingCapacityOccupied_Perennial")
                                make_kmz(peren_occ_dams, 'Percent_Existing_Capacity_Occupied_by_Surveyed_Dams', peren_kmz_folder)
                                make_kmz(dams, 'Surveyed_Beaver_Dam_Locations', kmz_folder)
                        except Exception as err:
                                print err
                else:
                        print '.....ERROR! Validation output not found. No KMZs made.'
                


def make_kmz(layer, kmz_name, kmz_folder):
        if os.path.exists(layer):
                output_kmz = os.path.join(kmz_folder, kmz_name+'.kmz')
                if not os.path.exists(output_kmz):
                        try:
                                arcpy.LayerToKML_conversion(layer, output_kmz)
                        except Exception as err:
                                print err
                else:
                        print '...Skipping ' + kmz_name + ': Already exists.'
        else:
                print '...Missing layer: ' + layer


        #make_layer(output_folder=os.path.dirname(layer), layer_base=clipped_shapefile, new_layer_name=title, symbology_layer=layer, file_name=out_layer)


def clipping_perennial(brat_folder):
    clip = os.path.join(brat_folder, 'Inputs/05_PerennialStream_01/NHD_24k_Perennial_CanalsDitches.shp')
    table = os.path.join(brat_folder, 'Outputs/Output_01/01_Intermediates/BRAT_Table.shp')
    cap = os.path.join(brat_folder, 'Outputs/Output_01/02_Analyses/Combined_Capacity.shp')
    cons = os.path.join(brat_folder, 'Outputs/Output_01/02_Analyses/Conservation_Restoration.shp')
    validation = os.path.join(brat_folder, 'Outputs/Output_01/02_Analyses/Validation.shp')
    arcpy.Clip_analysis(table, clip, table.split('.')[0] + "_Perennial.shp")    
    arcpy.Clip_analysis(cap, clip, cap.split('.')[0] + "_Perennial.shp")    
    arcpy.Clip_analysis(cons, clip, cons.split('.')[0] + "_Perennial.shp")
    arcpy.Buffer_analysis(clip, os.path.join(brat_folder, 'Outputs/Output_01/01_Intermediates/01_Buffers/buffer_30m_Perennial.shp'), '30 Meters', '', 'ROUND')
    arcpy.Buffer_analysis(clip, os.path.join(brat_folder, 'Outputs/Output_01/01_Intermediates/01_Buffers/buffer_100m_Perennial.shp'), '100 Meters', '', 'ROUND')
    make_kmz(cons, 'risk')
    make_kmz(cons, 'limits')
    make_kmz(cons, 'management')
    make_kmz(cap, 'existing_capacity')
    make_kmz(cap, 'existing_complex')
    make_kmz(cap, 'historic_capacity')
    make_kmz(cap, 'historic_complex')
    make_kmz(validation, 'validation')
    


def make_kmz_old(shapefile, type):
    analyses_folder = os.path.dirname(shapefile)
    capacity_folder = find_folder(analyses_folder, "Capacity")
    existing_capacity_folder = find_folder(capacity_folder, "ExistingCapacity")
    historic_capacity_folder = find_folder(capacity_folder, "HistoricCapacity")
    management_folder = find_folder(analyses_folder, "Management")
    validation_folder = find_folder(analyses_folder, "Validation")
    if type == 'risk':
        layer = os.path.join(management_folder, 'RiskofUndesirableDams.lyr')
        if not os.path.exists(layer):
            print 'Risk layer not found; attempting to re-create...'
            make_layer(management_folder, shapefile, "Risk of Undesirable Dams", symbology_layer=os.path.join(symbology_folder, "Areas_Beavers_Can_Build_Dams_but_could_be_Undesirable.lyr"))
    elif type == 'limits':
        layer = os.path.join(management_folder, 'UnsuitableorLimitedOpportunities.lyr')
        if not os.path.exists(layer):
            print 'Unsuitable layer not found; attempting to re-create...'
            make_layer(management_folder, shapefile, "Unsuitable or Limited Opportunities", symbology_layer=os.path.join(symbology_folder, "Unsuitable_Limited_Dam_Building_Opportunities.lyr"))
    elif type == 'management':
        layer = os.path.join(management_folder, 'RestorationorConservationOpportunities.lyr')
        if not os.path.exists(layer):
            print 'Conservation layer not found; attempting to re-create...'
            make_layer(management_folder, shapefile, "Restoration or Conservation Opportunities", symbology_layer=os.path.join(symbology_folder, "Possible_Beaver_Dam_Conservation_Restoration_Opportunities.lyr"))
            
    elif type == 'existing_capacity':
        layer = os.path.join(existing_capacity_folder, 'ExistingDamBuildingCapacity.lyr')
        if not os.path.exists(layer):
            print 'Existing capacity layer not found; attempting to re-create...'
            make_layer(existing_capacity_folder, shapefile, "Existing Dam Building Capacity", symbology_layer=os.path.join(symbology_folder, "Existing_Capacity.lyr"))
    elif type == 'existing_complex':
        layer = os.path.join(existing_capacity_folder, 'ExistingDamComplexSize.lyr')
        if not os.path.exists(layer):
            print 'Existing complex layer not found; attempting to re-create...'
            make_layer(existing_capacity_folder, shapefile, "Existing Dam Complex Size", symbology_layer=os.path.join(symbology_folder, "Existing_Capacity_Count.lyr"))
    elif type == 'historic_capacity':
        layer = os.path.join(historic_capacity_folder, 'HistoricDamBuildingCapacity.lyr')
        if not os.path.exists(layer):
            print 'Historic capacity layer not found; attempting to re-create...'
            make_layer(historic_capacity_folder, shapefile, "Historic Dam Building Capacity", symbology_layer=os.path.join(symbology_folder, "Historic_Capacity.lyr"))
    elif type == 'historic_complex':
        layer = os.path.join(historic_capacity_folder, 'HistoricDamComplexSize.lyr')
        if not os.path.exists(layer):
            print 'Existing capacity layer not found; attempting to re-create...'
            make_layer(historic_capacity_folder, shapefile, "Historic Dam Complex Size", symbology_layer=os.path.join(symbology_folder, "Historic_Capacity_Count.lyr"))



if __name__ == '__main__':
    main()
                          
