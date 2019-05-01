pf_path = 'C:/Users/Maggie/Desktop/TNC_BRAT/TNC_BRAT/wrk_Data'
evt_path = 'C:/Users/Maggie/Desktop/EPA_Ecoregions_Level3/CAFoothillsCoastMts/CAFoothillsCoastMts_140EVT.tif'
bps_path = 'C:/Users/Maggie/Desktop/EPA_Ecoregions_Level3/CAFoothillsCoastMts/CAFoothillsCoastMts_140BPS.tif'
evt_name = 'LANDFIRE_140EVT'
bps_name = 'LANDFIRE_140BPS'

dir_list = [] # list of directories pertaining to ecoregion

def main(dir_list, evt_path, bps_path):
	for dir in dir_list:
		evt = os.path.join(pf_path, dir, 'LANDFIRE', evt_name + '.tif')
		bps = os.path.join(pf_path, dir, 'LANDFIRE', bps_name + '.tif')
		
		
		print 'Joining EVT fields for ' + dir
		try:
			arcpy.DeleteField_management(evt, 'VEG_CODE')
			arcpy.JoinField_management(evt, 'Value', evt_path, 'Value', 'VEG_CODE')
		except Exception as err:
			print err
		print 'Joining BPS fields for ' + dir
		try:
			arcpy.DeleteField_management(bps, 'VEG_CODE')
			arcpy.JoinField_management(bps, 'Value', bps_path, 'Value', 'VEG_CODE')
		except Exception as err:
			print err

			
if __name__ == "__main__":
        main()
