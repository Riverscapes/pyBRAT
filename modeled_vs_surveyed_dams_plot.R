#################################################################
### BRAT DAM CAPACITY COUNT VS. OBSERVED DAM COUNTS PER REACH ###
#################################################################

# user-defined input: 
# path to shapefile output from data capture validation tool
validation_file <- 'C:/Users/Maggie/Desktop/BigWood_PreliminaryRun2_iVeg30Explus1/Et_Al_17040219_BRAT_PrelimRun2/02_Analyses/Output_2/Data_Validation_17040219.shp'
# huc name (to be used as subtitle in plots)
huc_name <- 'Big Wood'
# previously created intercomparison folder
intercomparison_folder <- 'C:/Users/Maggie/Desktop'

create_validation_plots <- function(validation_file, huc_name, intercomparison_folder){

  # load required packages
  options(warn=-1) # turn warnings off
  library(rgdal)
  library(raster)
  library(ggplot2)
  library(quantreg)  

  # import data capture validation shapefile
  validation <- shapefile(validation_file)
  
  #######################
  ### BUILD BASE PLOT ###
  #######################
  
  # clean x and y values
  a <- which(names(validation@data)=="mCC_EX_CT")
  b <- which(names(validation@data)=="e_DamCt")
  mCC_EX_CT = validation@data[,a]
  e_DamCt = validation@data[,b]
  # pull out NA values
  x = mCC_EX_CT[which(!is.na(e_DamCt))]
  x <- as.numeric(x)
  y = e_DamCt[which(!is.na(e_DamCt))]
  y <- as.numeric(y)
  # pull out values where observed dams > 0, or observed dams = 0 and predicted dams = 0
  X1 = x[which(y!=0 | (x==0 & y==0))]
  Y1 = y[which(y!=0 | (x==0 & y==0))]
  
  
  # create base plot aesthetics
  base_plot <- ggplot()+
    labs(subtitle=huc_name) + # subtitle is huc_name specified
    theme_bw() +              # simple theme coloration
    xlab("Predicted number of dams")+ # x-axis title
    ylab("Observed number of dams")   # y-axis title
  # axis limits equivalent, 0 to largest of either x or y
  if(max(X1) > max(Y1)){
    base_plot <- base_plot + 
      scale_x_continuous(breaks = seq(0,max(X1)+2,by=2), limits=c(0, round(max(X1)+2)))+
      scale_y_continuous(breaks = seq(0,max(X1)+2,by=2), limits=c(0, round(max(X1)+2)))
  } else{
    base_plot <- base_plot +
      scale_x_continuous(breaks = seq(0,max(Y1)+2,by=2), limits=c(0, round(max(Y1)+2)))+
      scale_y_continuous(breaks = seq(0,max(Y1)+2,by=2), limits=c(0, round(max(Y1)+2)))
  }
  
  # group points into inaccurate (red) values and "good" (blue) values
  red_x <- vector()
  red_y <- vector()
  blue_x <- vector()
  blue_y <- vector()
  for (i in 1:length(X1)){
    if(Y1[i]>X1[i]){
      red_x <- rbind(red_x, X1[i])
      red_y <- rbind(red_y, Y1[i])
    } else{
      blue_x <- rbind(blue_x, X1[i])
      blue_y <- rbind(blue_y, Y1[i])
    }
  }
  
  # plot points with jitter (slight variation in actual values) to avoid direct overlap of equivalent points
  if(length(X1)>0 && sd(X1)!=0){
    base_plot <- base_plot+
      geom_jitter(aes(red_x, red_y), color="red", alpha=0.5, width=0.1, height=0.01) +
      geom_jitter(aes(blue_x, blue_y), color="blue", alpha=0.5, width=0.1, height=0.01)
  }
  
  #####################################################
  ### OBSERVED VS. PREDICTED REGRESSION LINEAR PLOT ###
  #####################################################
  
  # create simple linear regression and 95% prediction intervals for observed follows predicted capacity
  regression <- lm(Y1~X1)
  sum <- summary(regression)
  n=length(X1)
  s=sum$sigma
  error <- qt(0.975,df=n-1)*s/sqrt(n)
  pred_x = -10:100
  pred_y <- pred_x*regression$coefficients[2]+regression$coefficients[1]
  upper_ci <- pred_y + error
  lower_ci <- pred_y - error
  limits <- layer_scales(base_plot)$x$limits[2]
  # add regression line, one-to-one line, confidence intervals, and regression equations + r-squared to plot
  regression_plot <- base_plot +
    ggtitle("Predicted vs. Observed Dam Counts Per Reach")+
    geom_abline(aes(slope=1, intercept=0), color= "purple", linetype="dotted",lwd=1.2)+
    geom_abline(aes(intercept=regression$coefficients[1], slope=regression$coefficients[2]), color="black")+
    geom_ribbon(aes(x=pred_x, ymin=lower_ci, ymax=upper_ci), color='pink', fill="red", alpha=0.1)+
    annotate('text', x=limits-2, y=limits/2, label=paste('R-squared = ', round(summary(regression)$r.squared,2)))+
    annotate('text', x=limits-2, y=limits/2+1, label=paste('y = ', round(coef(regression)[2],2), 'x + ', round(coef(regression)[1],2)))+
    annotate('text', x=limits-2, y=limits/2+2, label='Regression')
  # save plot
  ggsave(filename='regression_plot.png', plot=regression_plot, path=intercomparison_folder, limitsize=FALSE)
  
  #################################
  ### QUANTILE REGRESSION PLOTS ###
  #################################
  
  # create quantile regression model
  qrfit <- rq(Y1~X1, tau=c(0.50, 0.75,0.9))
  
  # add regression lines to baseplot
  qr_plot <- base_plot+
    ggtitle('Quantile Regressions of Observed vs. Predicted Dam Capacity')+
    geom_abline(mapping=aes(slope=coef(qrfit)[2,1], intercept=coef(qrfit)[1,1]), linetype='dotdash')+
    geom_abline(mapping=aes(slope=coef(qrfit)[2,2], intercept=coef(qrfit)[1,2]), linetype='longdash')+
    geom_abline(mapping=aes(slope=coef(qrfit)[2,3], intercept=coef(qrfit)[1,3]), linetype='solid')
  # save plot
  ggsave(filename='quantile_regression_plot.png', plot=qr_plot, path=intercomparison_folder, limitsize=FALSE)

  
  # calculate and return percent correct
  percent_correct = length(which(blue_y>0))/(length(red_y>0)+length(which(blue_y>0)))
  
  # turn warnings back on
  options(warn=0)
  
  results <- list()
  results$regression_plot_path <- paste(intercomparison_folder, '/regression_plot.png', sep='')
  results$quantile_regression_plot_path <- paste(intercomparison_folder, '/quantile_regression_plot.png', sep='')
  results$percent_correct <- paste("Percent of reaches correctly estimated: ",  round(percent_correct*100, 2), '%')
      
  return(results)
  }

create_validation_plots(validation_file, huc_name, intercomparison_folder)
