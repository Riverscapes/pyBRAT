library(raster)

pf_path = 'C:/Users/Maggie/Desktop/Idaho/wrk_Data'
setwd(pf_path)

dir_list <- list.files()
dir_list <- dir_list[3:85]

evt_200 <- '00_Projectwide/LANDFIRE/LANDFIRE_200EVT.tif'
evt_140 <- '00_Projectwide/LANDFIRE/LANDFIRE_140EVT.tif'
bps_200 <- evt_200 <- '00_Projectwide/LANDFIRE/LANDFIRE_200BPS.tif'
bps_140 <- '00_Projectwide/LANDFIRE/LANDFIRE_140BPS.tif'

evt_200_ras <- raster(evt_200)
evt_140_ras <- raster(evt_140)
bps_200_ras <- raster(bps_200)
bps_140_ras <- raster(bps_140)

out_evt <- 'C:/Users/Maggie/Desktop/Idaho/wrk_Data/00_Projectwide/LANDFIRE/LANDFIRE_EVT_Merge.tif'
out_bps <- 'C:/Users/Maggie/Desktop/Idaho/wrk_Data/00_Projectwide/LANDFIRE/LANDFIRE_BPS_Merge.tif'

evt_shp <- rasterToPolygons(evt_200_ras)
bps_shp <- rasterToPoints(bps_200_ras)

evt_mask <- raster::mask(x=evt_140_ras, mask=evt_shp, 'LANDFIRE_140EVT_Mask.tif', inverse=TRUE)
bps_mask <- raster::mask(x=bps_140_ras, mask=bps_shp, 'LANDFIRE_140BPS_Mask.tif', inverse=TRUE)

raster::merge(x=evt_200_ras, y=evt_mask, filename=out_evt, overlap=FALSE)
raster::merge(x=bps_200_ras, y=bps_mask, filename=out_bps, overlap=FALSE) 