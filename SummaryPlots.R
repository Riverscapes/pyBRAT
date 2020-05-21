in.shp.path = "C:/etal/Shared/Projects/USA/Idaho/BRAT/FY1819/wrk_Data/00_BRAT_Admin_Regions/Southwest_Region/01_Perennial_Network/Data_Validation/Data_Capture_Validation_Perennial_SouthwestRegion.shp"
plot.subtitle = "Idaho"

# load required packages

if (!'sf' %in% installed.packages()) install.packages('sf')
if (!'tidyverse' %in% installed.packages()) install.packages('tidyverse')


library(sf)
library(tidyverse)


# need to still code up:
#     - Existing vs. Historic Capacity sheet (note seems redundant with other sheets)
#     - Predicted vs Surveyed
#     - Electivity Index


# read in input shapefile as data frame
in.data = st_read(in.shp.path) %>% mutate(Length = as.numeric(st_length(.))) %>% st_drop_geometry(.) 


#' Order capacity estimate categories
#'
#' @param df Input data frame
#' @param cat.field Data frame column (i.e., field).  Categorical field that will be ordered as factor.
#' @param field.type Field type.  Used to apply corresponding factor levels.
#'
#' @return Input data frame with correctly ordered factor column
#' @export
#'
#' @examples
#' in.data = order_factor(in.data, "ExCategor", "Capacity")
order_factor = function(df, cat.field, field.type){
  
  if(field.type == "Capacity")
    df = df %>%
      mutate(!!sym(cat.field) := fct_relevel(!!sym(cat.field), c("None (0 dams)", "Rare (0-1 dams/km)", "Occasional (1-5 dams/km)", "Frequent (5-15 dams/km)", "Pervasive (15-40 dams/km)")))
  
  if(field.type == "Count")
    df = df %>%
      mutate(!!sym(cat.field) := fct_relevel(!!sym(cat.field), c("No dams", "Single dam", "Small complex (2-3 dams)", "Medium complex (4-5 dams)", "Large complex (> 5 dams)")))
  
  return(df)
  
}


#' Calculate summary lengths by category
#'
#' @param df Input dataframe with 'Length' field 
#' @param group.field Data frame column (i.e., field).  Categorical field used to summarize lengths.  
#'
#' @return  Dataframe with columns stream length (km), stream length (mi), percent total for each category in group field.
#' @export
#'
#' @examples
#' ex.dam.capacity = calc_length(in.data, "ExCategor") 
calc_length = function(df, group.field){
  
  total.length.km = sum(df$Length) / 1000
  
  df = df %>%
    group_by(!!sym(group.field)) %>%
    summarise(stream.length.km = round(sum(Length) / 1000)) %>%
    ungroup() %>%
    mutate(stream.length.mi = round((stream.length.km * 0.621371)),
           percent = stream.length.km / total.length.km * 100) %>%
    add_row(!!sym(group.field) := "Total",
            stream.length.km = sum(.$stream.length.km),
            stream.length.mi = sum(.$stream.length.mi),
            percent = sum(.$percent)) %>%
    # mutate(percent = round(percent)) %>%
    setNames(., c("Category", "Stream length (km)", "Stream length (mi)", "Percent"))
  
  return(df)
  
}



# ------- dam building capacity tables and plots -------


summarize_capacity = function(in.data){
  
  # -- historic (oCC_HPE)
  
  in.data = in.data %>%
    mutate(HpeDensCat = cut(oCC_HPE, breaks = c(-Inf, 0, 1, 5, 15, Inf), labels = c("None (0 dams)", "Rare (0-1 dams/km)", "Occasional (1-5 dams/km)", "Frequent (5-15 dams/km)", "Pervasive (15-40 dams/km)"))) %>%
    order_factor("HpeDensCat", "Capacity")
  
  hist.dam.capacity = calc_length(in.data, "HpeDensCat") %>% mutate(model = "Capacity", type = "Historic", field = "oCC_HPE")
  
  # -- existing (oCC_EX)
  
  in.data = in.data %>%
    mutate(ExDensCat = cut(oCC_EX, breaks = c(-Inf, 0, 1, 5, 15, Inf), labels =c("None (0 dams)", "Rare (0-1 dams/km)", "Occasional (1-5 dams/km)", "Frequent (5-15 dams/km)", "Pervasive (15-40 dams/km)"))) %>%
    order_factor("ExDensCat", "Capacity")
  
  ex.dam.capacity = calc_length(in.data, "ExDensCat") %>% mutate(model = "Capacity", type = "Existing", field = "oCC_EX")
  
  # -- create output plot
  
  # combine tables
  dam.capacity = hist.dam.capacity %>% rbind(ex.dam.capacity) %>% filter(!grepl('Total', Category)) %>% order_factor("Category", "Capacity")
    
  
  # set capacity category fill colors
  capacity.fill = c('None (0 dams)' = '#F50000', 'Rare (0-1 dams/km)' = '#FFAA00', 'Occasional (1-5 dams/km)' = '#F5F500', 'Frequent (5-15 dams/km)' = "#4CE600", 'Pervasive (15-40 dams/km)' = '#005CE6')
  
  # plot
  capacity.plot = ggplot(dam.capacity, aes(x = Category, y = Percent, fill = Category)) +
    geom_col(alpha = 0.8) +
    geom_text(aes(label = round(Percent, 1)), vjust = -0.5, color = "darkgrey", position = position_dodge(0.9), size = 2.5) +
    ylab("% Stream Network Length") + xlab("Capacity Category") +
    facet_wrap(~ type) +
    scale_fill_manual(values = capacity.fill) +
    theme_bw() +
    theme(legend.position = "none",
          strip.background = element_blank(),
          plot.subtitle = element_text(face="italic")) +
    scale_x_discrete(labels = function(x) gsub(" ", "\n", x)) +
    ggtitle("BRAT: Existing vs Historic Dam Density Capacity", subtitle = plot.subtitle)
  # 
  # ggsave(file.path(dirname(in.shp.path), 'Dam_Density_Capacity_Plot_OptionA.png'), plot = capacity.plot, width = 7, height = 6, units = "in", dpi = 500)
  
  capacity.plot.b = ggplot(dam.capacity, aes(x = Category, y = Percent, fill = type)) +
    geom_col(position = position_dodge(), alpha = 0.8) +
    geom_text(aes(label = round(Percent, 1)), vjust = -0.5, color="darkgrey", position = position_dodge(0.9), size = 2.5) +
    scale_fill_brewer(palette = "Paired") +
    ylab("% Stream Network Length") + xlab("Capacity Category") +
    theme_bw() +
    theme(legend.position = "bottom",
          plot.subtitle = element_text(face="italic")) +
    ggtitle("BRAT: Existing vs Historic Dam Density Capacity", subtitle = plot.subtitle) +
    scale_x_discrete(labels = function(x) gsub(" ", "\n", x))

  
  ggsave(file.path(dirname(in.shp.path), 'Dam_Density_Capacity_Plot.png'), plot = capacity.plot.b, width = 7, height = 6, units = "in", dpi = 500)
  ggsave(file.path(dirname(in.shp.path), 'Dam_Density_Capacity_Plot.pdf'), plot = capacity.plot.b, width = 7, height = 6, units = "in")

  }


if(all(c("oCC_HPE", "oCC_HPE") %in% names(in.data))){summarize_capacity(in.data = in.data)}



# ------- dam complex size tables -------


summarize_complex = function(in.data){
  # -- historic (mCC_HPE_CT)
  in.data = in.data %>%
    mutate(HpeCountCat = cut(mCC_HPE_CT, breaks = c(-Inf, 0, 1, 3, 5, Inf),
                            labels = c("No dams", "Single dam", "Small complex (2-3 dams)", "Medium complex (4-5 dams)", "Large complex (> 5 dams)"))) %>%
    order_factor("HpeCountCat", "Count")
  
  hist.dam.count = calc_length(in.data, "HpeCountCat") %>% mutate(model = "Capacity", type = "Historic", field = "mCC_HPE_CT")
  
  # -- existing (mCC_EX_CT)
  in.data = in.data %>%
    mutate(ExCountCat = cut(mCC_EX_CT, breaks = c(-Inf, 0, 1, 3, 5, Inf),
                            labels = c("No dams", "Single dam", "Small complex (2-3 dams)", "Medium complex (4-5 dams)", "Large complex (> 5 dams)"))) %>%
    order_factor("ExCountCat", "Count")
  
  ex.dam.count = calc_length(in.data, "ExCountCat") %>% mutate(model = "Capacity", type = "Existing", field = "mCC_EX_CT")
  
  # -- create output plot
  
  # combine tables
  dam.count = hist.dam.count %>% bind_rows(ex.dam.count) %>% filter(!grepl('Total', Category))
  
  # plot
  count.plot = ggplot(dam.count, aes(x = Category, y = Percent, fill = type)) +
    geom_col(position = position_dodge(), alpha = 0.8) +
    geom_text(aes(label = round(Percent, 1)), vjust = -0.5, color="darkgrey", position = position_dodge(0.9), size = 2.5) +
    scale_fill_brewer(palette = "Paired") +
    ylab("% Stream Network Length") + xlab("Dam Complex Category") +
    theme_bw() +
    theme(legend.position = "bottom",
          plot.subtitle = element_text(face="italic")) +
    scale_x_discrete(labels = function(x) str_wrap(x, width = 8)) +
    ggtitle("BRAT: Existing vs Historic Dam Complex Capacity", subtitle = plot.subtitle)
  
  ggsave(file.path(dirname(in.shp.path), 'Dam_Complex_Capacity_Plot.png'), plot = count.plot, width = 7, height = 6, units = "in", dpi = 500)
  ggsave(file.path(dirname(in.shp.path), 'Dam_Complex_Capacity_Plot.pdf'), plot = count.plot, width = 7, height = 6, units = "in")
  
  }

if(all(c("mCC_HPE_CT", "mCC_EX_CT") %in% names(in.data))){summarize_complex(in.data = in.data)}



# ------- conservation restoration tables -------


summarize_mgmt = function(in.data){

  # -- conservation restoration (oPBRC_CR)
  in.data = in.data %>% 
    mutate(oPBRC_CR = fct_other(oPBRC_CR, drop = "NA", other_level = "Other"),
           oPBRC_CR = fct_relevel(oPBRC_CR, c("Easiest - Low-Hanging Fruit", "Straight Forward - Quick Return", "Strategic - Long-Term Investment", "Other")))
  con.rest = calc_length(in.data, "oPBRC_CR") %>% mutate(model = "Conservation Restoration", type = "Conservation and Restoration Opportunities", field = "oPBRC_CR")
  
  # -- unsuitable or limited
  # todo: check if Potential Reservoir or Landuse Change is actually part of model or not -- omitting for now
  in.data = in.data %>% 
    mutate(oPBRC_UD = fct_recode(oPBRC_UD, "Stream Size Limited" = "...TBD..."),
           oPBRC_UD = fct_relevel(oPBRC_UD, c("Anthropogenically Limited", "Naturally Vegetation Limited", "Potential Reservoir or Landuse", "Slope Limited", "Stream Power Limited", "Stream Size Limited", "Dam Building Possible")))
  unsuit.limited = calc_length(in.data, "oPBRC_UD") %>% mutate(model = "Conservation Restoration", type = "Unsuitable or Limited Opportunities", field = "oPBRC_UD")
  
  # -- undesirable dams  
  in.data = in.data %>% mutate(oPBRC_UI = fct_relevel(oPBRC_UI, c("Considerable Risk", "Some Risk", "Minor Risk", "Negligible Risk")))
  undesirable.dams = calc_length(in.data, "oPBRC_UI") %>% mutate(model = "Conservation Restoration", type = "Risk of Undesirable Dams", field = "oPBRC_UI")
  
  # -- management strategies
  # todo - determine actually category names (differs from table that tyler sent)
  in.data = in.data %>% mutate(ConsVRest = fct_relevel(ConsVRest, c("Immediate - Beaver Conservation", "Immediate - Potential Beaver Translocation",
                                                                        "Mid Term - Process-based Riparian Vegetation Restoration", "Long Term - Riparian Vegetation Reestablishment",
                                                                        "Low Capacity Habitat")))
  mgmt.strat = calc_length(in.data, "ConsVRest") %>% mutate(model = "Conservation Restoration", type = "Current Beaver Dam Management Strategies", field = "ConsVRest")
  
  # -- create output plot
  
  # set plot category colors
  mgmt.fill = c("Easiest - Low-Hanging Fruit" = "#38A800", "Straight Forward - Quick Return" = "#2892C7", "Strategic - Long-Term Investment" = "#00FFC5", "Other" = "#CCCCCC",
                "Anthropogenically Limited" = "#FA8D34", "Naturally Vegetation Limited" = "#38A800", "Slope Limited" = "#FA3411", "Stream Power Limited" = "#00A9E6", 
                "Stream Size Limited" = "#2892C7", "Dam Building Possible" = "#CCCCCC", "Potential Reservoir or Landuse" = "#FF00FF",
                "Considerable Risk" = "#E60000", "Some Risk" = "#FFAA00", "Minor Risk" = "#00C5FF", "Negligible Risk" = "#CCCCCC",
                "Immediate - Beaver Conservation" = "#A900E6", "Immediate - Potential Beaver Translocation" = "#005CE6", 
                "Mid Term - Process-based Riparian Vegetation Restoration" = "#38A800", "Long Term - Riparian Vegetation Reestablishment" = "#E6E600",
                "Low Capacity Habitat" = "#CCCCCC")
  
  # combine tables
  mgmt.df = rbind(mgmt.strat, con.rest, unsuit.limited, undesirable.dams) %>% filter(!Category == "Total")
  
  # filter to separate dfs for 2 separate plots
  mgmt.a = mgmt.df %>% filter(type == "Current Beaver Dam Management Strategies" | type == "Conservation and Restoration Opportunities")
  mgmt.b = mgmt.df %>% filter(type == "Unsuitable or Limited Opportunities" | type == "Risk of Undesirable Dams")
  
  # plot data
  mgmt.a.plot = ggplot(mgmt.a, aes(x = Category, y = Percent, fill = Category)) +
    geom_col(alpha = 0.8) +
    geom_text(aes(label = round(Percent, 1)), hjust = -0.5, color="darkgrey", position = position_dodge(0.9), size = 4) +
    scale_fill_manual(values = mgmt.fill) +
    ylab("% Stream Network Length") + xlab("Category") +
    facet_grid(type ~ ., scales = "free", space = "free") +
    theme_bw() +
    theme(legend.position = "none",
          strip.background = element_blank(),
          strip.text = element_text(size = 10),
          plot.subtitle = element_text(face="italic")) + 
    scale_y_continuous(limits = c(0, 100)) +
    coord_flip() +
    ggtitle("BRAT: Restoration and Conservation Models", subtitle = plot.subtitle)
  
  mgmt.b.plot = ggplot(mgmt.b, aes(x = Category, y = Percent, fill = Category)) +
    geom_col(alpha = 0.8) +
    geom_text(aes(label = round(Percent, 1)), hjust = -0.5, color="darkgrey", position = position_dodge(0.9), size = 4) +
    scale_fill_manual(values = mgmt.fill) +
    ylab("% Stream Network Length") + xlab("Category") +
    facet_grid(type ~ ., scales = "free", space = "free") +
    theme_bw() +
    theme(legend.position = "none",
          strip.background = element_blank(),
          strip.text = element_text(size = 10),
          plot.subtitle = element_text(face="italic")) + 
    scale_y_continuous(limits = c(0, 100)) +
    coord_flip() +
    ggtitle("BRAT: Restoration and Conservation Models", subtitle = plot.subtitle)
  
  ggsave(file.path(dirname(in.shp.path), 'Restoration_Conservation_Model_PlotA.png'), plot = mgmt.a.plot, width = 11, height = 8, units = "in", dpi = 500)
  ggsave(file.path(dirname(in.shp.path), 'Restoration_Conservation_Model_PlotB.png'), plot = mgmt.b.plot, width = 11, height = 8, units = "in", dpi = 500)
  ggsave(file.path(dirname(in.shp.path), 'Restoration_Conservation_Model_PlotA.pdf'), plot = mgmt.a.plot, width = 11, height = 8, units = "in")
  ggsave(file.path(dirname(in.shp.path), 'Restoration_Conservation_Model_PlotB.pdf'), plot = mgmt.b.plot, width = 11, height = 8, units = "in")

  
  # split out further for report
  mgmt.cr = mgmt.df %>% filter(type == "Conservation and Restoration Opportunities")
  mgmt.ui = mgmt.df %>% filter(type == "Unsuitable or Limited Opportunities")
  mgmt.ud = mgmt.df %>% filter (type == "Risk of Undesirable Dams")
  
  # plot data
  mgmt.cr.plot = ggplot(mgmt.cr, aes(x = Category, y = Percent, fill = Category)) +
    geom_col(alpha = 0.8) +
    geom_text(aes(label = round(Percent, 1)), hjust = -0.5, color="darkgrey", position = position_dodge(0.9), size = 4) +
    scale_fill_manual(values = mgmt.fill) +
    ylab("% Stream Network Length") + xlab("Category") +
    theme_bw() +
    theme(legend.position = "none",
          strip.background = element_blank(),
          strip.text = element_text(size = 10),
          plot.subtitle = element_text(face="italic")) + 
    scale_y_continuous(limits = c(0, 100)) +
    coord_flip()
  
  mgmt.ud.plot = ggplot(mgmt.ud, aes(x = Category, y = Percent, fill = Category)) +
    geom_col(alpha = 0.8) +
    geom_text(aes(label = round(Percent, 1)), hjust = -0.5, color="darkgrey", position = position_dodge(0.9), size = 4) +
    scale_fill_manual(values = mgmt.fill) +
    ylab("% Stream Network Length") + xlab("Category") +
    theme_bw() +
    theme(legend.position = "none",
          strip.background = element_blank(),
          strip.text = element_text(size = 10),
          plot.subtitle = element_text(face="italic")) + 
    scale_y_continuous(limits = c(0, 100)) +
    coord_flip()
  
  mgmt.ui.plot = ggplot(mgmt.ui, aes(x = Category, y = Percent, fill = Category)) +
    geom_col(alpha = 0.8) +
    geom_text(aes(label = round(Percent, 1)), hjust = -0.5, color="darkgrey", position = position_dodge(0.9), size = 4) +
    scale_fill_manual(values = mgmt.fill) +
    ylab("% Stream Network Length") + xlab("Category") +
    theme_bw() +
    theme(legend.position = "none",
          strip.background = element_blank(),
          strip.text = element_text(size = 10),
          plot.subtitle = element_text(face="italic")) + 
    scale_y_continuous(limits = c(0, 100)) +
    coord_flip()
  
  ggsave(file.path(dirname(in.shp.path), 'Restoration_Conservation_Plot_ForReport.png'), plot = mgmt.cr.plot, width = 8, height = 2, units = "in", dpi = 500)
  ggsave(file.path(dirname(in.shp.path), 'Undesirable_Dams_Plot_ForReport.png'), plot = mgmt.ud.plot, width = 8, height = 2, units = "in", dpi = 500)
  ggsave(file.path(dirname(in.shp.path), 'Limited_Opportunities_Plot_ForReport.png'), plot = mgmt.ui.plot, width = 8, height = 4, units = "in", dpi = 500)
}

if(all(c("oPBRC_CR", "oPBRC_UD", "oPBRC_UI") %in% names(in.data))){summarize_mgmt(in.data = in.data)}

# ------- validation plots -------

summarize_val = function(in.data){
  
  # subset to reaches where have observed data
  val.data = in.data %>% 
    filter(e_DamCt > 0.0)  %>%
    mutate(model.pred = ifelse(oCC_EX > e_DamDens, "Within Capacity Estimate", "Above Capacity Estimate"))
  
  dens.cor = cor.test(val.data$oCC_EX, val.data$e_DamDens, method = "pearson")
  count.cor = cor.test(val.data$oCC_EX, val.data$e_DamDens, method = "pearson")
  
  print(dens.cor)
  print(count.cor)
  
  # get 'pretty' axis limits
  dens.axis.max = ifelse(max(val.data$oCC_EX) > max(val.data$e_DamDens), round(max(val.data$oCC_EX)), round(max(val.data$e_DamDens)))
  count.axis.max = ifelse(max(val.data$mCC_EX_CT) > max(val.data$e_DamCt), round(max(val.data$mCC_EX_CT)), round(max(val.data$e_DamCt)))

  # xy.plot = ggplot(val.data, aes(x = mCC_EX_CT, y = e_DamCt)) +  
  xy.density = ggplot(val.data, aes(x = oCC_EX, y = e_DamDens)) +
    geom_abline(intercept = 0, slope = 1, linetype = 2, color = "darkgrey") +
    geom_point(aes(colour = factor(model.pred)), alpha = 0.6) +
    scale_colour_brewer(palette = "Set1", direction = -1) +
    xlab("Predicted Dam Density (dams/km)") + ylab("Observed Dam Density (dams/km)") +
    xlim(0, dens.axis.max) + ylim(0, dens.axis.max) +
    theme_bw() + 
    theme(legend.position = "bottom",
          legend.title = element_blank(),
          plot.subtitle = element_text(face="italic")) +
    ggtitle("Predicted vs. Observed Dam Density Per Reach", subtitle = plot.subtitle)

  
  xy.count = ggplot(val.data, aes(x = mCC_EX_CT, y = e_DamCt)) + 
    geom_abline(intercept = 0, slope = 1, linetype = 2, color = "darkgrey") +
    geom_point(aes(colour = factor(model.pred)), alpha = 0.6) +
    scale_colour_brewer(palette = "Set1", direction = -1) +
    xlab("Predicted Number of Dams") + ylab("Observed Number of Dams") +
    xlim(0, count.axis.max) + ylim(0, count.axis.max) +
    theme_bw() + 
    theme(legend.position = "bottom",
          legend.title = element_blank(),
          plot.subtitle = element_text(face="italic")) +
    ggtitle("Predicted vs. Observed Dam Counts Per Reach", subtitle = plot.subtitle)
  
  ggsave(file.path(dirname(in.shp.path), 'Observed_vs_Predicted_Density_Plot.png'), plot = xy.density, width = 10, height = 6, units = "in", dpi = 500)
  ggsave(file.path(dirname(in.shp.path), 'Observed_vs_Predicted_Count_Plot.png'), plot = xy.count, width = 10, height = 6, units = "in", dpi = 500)
  ggsave(file.path(dirname(in.shp.path), 'Observed_vs_Predicted_Density_Plot.pdf'), plot = xy.density, width = 10, height = 6, units = "in")
  ggsave(file.path(dirname(in.shp.path), 'Observed_vs_Predicted_Count_Plot.pdf'), plot = xy.count, width = 10, height = 6, units = "in")
  
  
}

if(all(c("e_DamDens", "iPC_HighLU", "iPC_VLowLU") %in% names(in.data))){summarize_val(in.data = in.data)}

