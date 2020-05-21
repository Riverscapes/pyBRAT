library(foreign) #required module

#ENTER PARAMETERS
file <- 'C:/Users/Maggie/Desktop/Idaho_BRAT/BearLake/LANDFIRE/LANDFIRE_EVT_merge.tif.vat.dbf'
huc_name <- 'BearLake'

#RUN THESE LINES FOR PERCENT FOREST IN WATERSHED
output <- as.data.frame(matrix(NA, nrow=1,ncol=4))
names(output) <- c('Watershed', 'ForestArea', 'TotalArea','PercentForest')  
landfire <- read.dbf(file)
count <- 0
for (j in 1:length(landfire$Value)){
  if(landfire$EVT_PHYS[j] == 'Conifer')  count <- count + landfire$Count[j]
  if(landfire$EVT_PHYS[j] == 'Hardwood') count <- count + landfire$Count[j]
  if(landfire$EVT_PHYS[j] == 'Conifer-Hardwood') count <- count + landfire$Count[j]
  }
total <- sum(landfire$Count, na.rm = T)
output[,1:3] <- c(huc_name, count, total)
output$ForestArea <- as.numeric(output$ForestArea)
output$TotalArea <- as.numeric(output$TotalArea)
output$PercentForest <- (output$Forest/output$Total)*100
output


##################
##### SLOPE ######
##################
library(raster) #required module

#ENTER PARAMETER
file <- 'C:/Users/Maggie/Desktop/TNC_BRAT/TNC_BRAT/wrk_Data/AntelopeFremontValleys_18090206/BRAT/BatchRun_02/Inputs/03_Topography/DEM_01/Slope/Slope.tif'

#RUN THESE LINES FOR PERCENT SLOPES > 30%
slope <- raster(file)
#slope30 <- reclassify(slope, cbind(0, 30, 90))
freq <- freq(slope)
a <- sum(freq[1:31,2])
b <- sum(freq[32:nrow(freq),2])
(b/(a+b))*100


#average basin slope
cellStats(slope, 'mean', na.rm=TRUE)
