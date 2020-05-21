library(foreign)

pf_path = 'C:/Users/Maggie/Desktop/Idaho/wrk_Data'
setwd(pf_path)

dir_list <- list.files()
dir_list <- dir_list[3:85]

output <- as.data.frame(matrix(NA, nrow=length(dir_list),ncol=3))
names(output) <- c('Watershed', 'Forest', 'Total')

for (i in 1:length(dir_list)){
  file <- paste(dir_list[i], '/LANDFIRE/LANDFIRE_200EVT.tif.vat.dbf', sep='')
  landfire <- read.dbf(file)
  count <- 0
  for (j in 1:length(landfire$Value)){
    if(landfire$EVT_PHYS_1[j] == 'Conifer')  count <- count + landfire$Count[j]
    if(landfire$EVT_PHYS_1[j] == 'Hardwood') count <- count + landfire$Count[j]
    if(landfire$EVT_PHYS_1[j] == 'Conifer-Hardwood') count <- count + landfire$Count[j]
    }
  total <- sum(landfire$Count, na.rm = T)
  output[i,1:3] <- c(dir_list[i], count, total)
}

output$Forest <- as.numeric(output$Forest)
output$Total <- as.numeric(output$Total)
output$PercentForest <- output$Forest/output$Total


## Find proportion of slopes > 30%
file <- 'C:/Users/Maggie/Desktop/Idaho/wrk_Data/UpperMFSalmon_17060205/BRAT/PrelimRun_01/Inputs/03_Topography/DEM_01/Slope/Slope.tif'
slope <- raster(file)
#slope30 <- reclassify(slope, cbind(0, 30, 90))
freq <- freq(slope)
a <- sum(freq[1:31,2])
b <- sum(freq[32:83,2])
b/(a+b)

#average basin slope
cellStats(slope, 'mean', na.rm=TRUE)
