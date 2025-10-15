# R script to create plots equivalent to plot_results.py using ggpubr
# Author: AI Assistant
# Date: Created to replicate Python implementation

# Load required libraries
library(readr)
library(dplyr)
library(ggplot2)
library(ggpubr)
library(tidyr)
library(gridExtra)
library(cowplot)

# Function to count number of features for natural abundance data
count_number_of_nat <- function(df) {
  cat("count_number_of_nat\n")
  
  # Handle different column names for nat_nist_mass
  nat_col <- if ("nat_nist_mass" %in% colnames(df)) {
    "nat_nist_mass"
  } else if ("nat_nist" %in% colnames(df)) {
    "nat_nist"
  } else {
    stop("Cannot find nat_nist_mass or nat_nist column")
  }
  
  valid_rows <- df[[nat_col]] != 'NO_MASS_MATCH' & !is.na(df[[nat_col]])
  cat("Sample", nat_col, "values:\n")
  print(head(df[valid_rows, nat_col]))
  cat("Summary of", nat_col, ":\n")
  print(summary(df[valid_rows, nat_col]))
  return(sum(valid_rows))
}

# Function to count number of features for C13 data
count_number_of_C13 <- function(df) {
  cat("count_number_of_C13\n")
  
  # Handle different column names for C13_95_mass
  c13_col <- if ("C13_95_mass" %in% colnames(df)) {
    "C13_95_mass"
  } else if ("C13_95" %in% colnames(df)) {
    "C13_95"
  } else {
    stop("Cannot find C13_95_mass or C13_95 column")
  }
  
  valid_rows <- df[[c13_col]] != 'NO_MASS_MATCH' & !is.na(df[[c13_col]])
  cat("Summary of", c13_col, ":\n")
  print(summary(df[valid_rows, c13_col]))
  return(sum(valid_rows))
}

# Function to calculate mean isotopes for natural abundance data
mean_isotopes_nat <- function(df) {
  cat("mean_isotopes_nat\n")
  
  # Handle different column names for nat_nist_mass
  nat_col <- if ("nat_nist_mass" %in% colnames(df)) {
    "nat_nist_mass"
  } else if ("nat_nist" %in% colnames(df)) {
    "nat_nist"
  } else {
    stop("Cannot find nat_nist_mass or nat_nist column")
  }
  
  # Handle different column names for iso_count (including renamed columns from duplicate names)
  iso_count_col <- if ("iso_count" %in% colnames(df)) {
    "iso_count"
  } else {
    # Look for iso_count with numeric suffix (e.g., iso_count...15)
    iso_cols <- grep("^iso_count(\\.\\.\\.\\d+)?$", colnames(df), value = TRUE)
    if (length(iso_cols) > 0) {
      iso_cols[1]  # Take the first iso_count column for nat data
    } else {
      stop("Cannot find iso_count column")
    }
  }
  
  valid_rows <- df[[nat_col]] != 'NO_MASS_MATCH' & !is.na(df[[nat_col]])
  cat("Summary of", iso_count_col, ":\n")
  print(summary(df[valid_rows, iso_count_col]))
  mean_val <- mean(df[[iso_count_col]][valid_rows], na.rm = TRUE)
  if (is.na(mean_val) || is.nan(mean_val) || length(mean_val) == 0) mean_val <- 0
  cat("Mean", iso_count_col, ":", mean_val, "\n")
  return(mean_val)
}

# Function to calculate mean isotopes for C13 data
mean_isotopes_C13 <- function(df) {
  cat("mean_isotopes_C13\n")
  
  # Handle different column names for C13_95_mass
  c13_col <- if ("C13_95_mass" %in% colnames(df)) {
    "C13_95_mass"
  } else if ("C13_95" %in% colnames(df)) {
    "C13_95"
  } else {
    stop("Cannot find C13_95_mass or C13_95 column")
  }
  
  # Handle different column names for iso_count.1 (including renamed columns from duplicate names)
  iso_count_col <- if ("iso_count.1" %in% colnames(df)) {
    "iso_count.1"
  } else if ("iso_count_C13" %in% colnames(df)) {
    "iso_count_C13"
  } else {
    # Look for iso_count with numeric suffix (e.g., iso_count...19)
    # Take the second iso_count column for C13 data
    iso_cols <- grep("^iso_count(\\.\\.\\.\\d+)?$", colnames(df), value = TRUE)
    if (length(iso_cols) >= 2) {
      iso_cols[2]  # Take the second iso_count column for C13 data
    } else if (length(iso_cols) == 1) {
      # If only one iso_count column found, check if there's a pattern match
      iso_cols[1]
    } else {
      stop("Cannot find iso_count.1 or iso_count_C13 column")
    }
  }
  
  valid_rows <- df[[c13_col]] != 'NO_MASS_MATCH' & !is.na(df[[c13_col]])
  cat("Summary of", iso_count_col, ":\n")
  print(summary(df[valid_rows, iso_count_col]))
  mean_val <- mean(df[[iso_count_col]][valid_rows], na.rm = TRUE)
  if (is.na(mean_val) || is.nan(mean_val) || length(mean_val) == 0) mean_val <- 0
  cat("Mean", iso_count_col, ":", mean_val, "\n")
  return(mean_val)
}

# Function to get DataFrame from file with caching
get_df <- function(filepath, df_cache) {
  if (!file.exists(filepath)) {
    cat("Warning: File", filepath, "not found\n")
    return(NULL)
  }
  
  if (!filepath %in% names(df_cache)) {
    tryCatch({
      df <- read_tsv(filepath, skip = 3, show_col_types = FALSE)
      # Remove duplicate rows based on first column (CF)
      if (ncol(df) > 0) {
        df <- df[!duplicated(df[,1]), ]
      }
      df_cache[[filepath]] <- df
    }, error = function(e) {
      cat("Warning: Could not read file", filepath, ":", e$message, "\n")
      return(NULL)
    })
  }
  
  return(df_cache[[filepath]])
}

# Main function to process results
process_results <- function(outdir, datasets = NULL) {
  # Default datasets
  if (is.null(datasets)) {
    datasets <- c('testdata1', 'testdata2')
    cat("Using default datasets:", paste(datasets, collapse = ", "), "\n")
  }
  
  df_cache <- list()
  
  # Data for top graph (varying p, fixed vp=0.5)
  p_values <- c(0.1, 0.5, 1.0)
  cf_counts_nat <- list()
  cf_counts_C13 <- list()
  
  # Data for bottom graph (varying vp, fixed p=0.5)
  vp_values <- c(0.1, 0.5, 1.0)
  iso_mean_nat <- list()
  iso_mean_C13 <- list()
  
  # Initialize lists for each dataset
  for (dataset in datasets) {
    cf_counts_nat[[dataset]] <- numeric(0)
    cf_counts_C13[[dataset]] <- numeric(0)
    iso_mean_nat[[dataset]] <- numeric(0)
    iso_mean_C13[[dataset]] <- numeric(0)
  }
  
  # Process files for all datasets
  for (dataset in datasets) {
    # Process files for top graph
    for (p in p_values) {
      p_str <- if (p < 1) gsub("\\.", "", as.character(p)) else as.character(as.integer(p))
      combined_file <- file.path(outdir, paste0("n", dataset, "_p", p_str, "_vp05_combined.tsv"))
      cat(combined_file, "\n")
      
      df <- get_df(combined_file, df_cache)
      if (is.null(df)) {
        cat("Skipping", combined_file, "due to read error\n")
        next
      }
      
      cf_counts_nat[[dataset]] <- c(cf_counts_nat[[dataset]], count_number_of_nat(df))
      cf_counts_C13[[dataset]] <- c(cf_counts_C13[[dataset]], count_number_of_C13(df))
    }
    
    # Process files for middle graph
    for (vp in vp_values) {
      vp_str <- if (vp < 1) gsub("\\.", "", as.character(vp)) else as.character(as.integer(vp))
      combined_file <- file.path(outdir, paste0("n", dataset, "_p05_vp", vp_str, "_combined.tsv"))
      cat(combined_file, "\n")
      
      df <- get_df(combined_file, df_cache)
      if (is.null(df)) {
        cat("Skipping", combined_file, "due to read error\n")
        next
      }
      
      iso_mean_nat[[dataset]] <- c(iso_mean_nat[[dataset]], mean_isotopes_nat(df))
      iso_mean_C13[[dataset]] <- c(iso_mean_C13[[dataset]], mean_isotopes_C13(df))
    }
  }
  
  # Filter out datasets that don't have complete data
  complete_datasets <- character(0)
  for (dataset in datasets) {
    has_p_data <- (length(cf_counts_nat[[dataset]]) == length(p_values) && 
                   length(cf_counts_C13[[dataset]]) == length(p_values))
    has_vp_data <- (length(iso_mean_nat[[dataset]]) == length(vp_values) &&
                    length(iso_mean_C13[[dataset]]) == length(vp_values))
    
    if (has_p_data && has_vp_data) {
      complete_datasets <- c(complete_datasets, dataset)
    } else {
      cat("Warning: Dataset", dataset, "does not have complete data, excluding from analysis\n")
    }
  }
  
  if (length(complete_datasets) == 0) {
    stop("No datasets have complete data for analysis")
  }
  
  # Return structured data
  result <- list(
    p_values = p_values,
    vp_values = vp_values,
    complete_datasets = complete_datasets,
    cf_counts_nat = cf_counts_nat[complete_datasets],
    cf_counts_C13 = cf_counts_C13[complete_datasets],
    iso_mean_nat = iso_mean_nat[complete_datasets],
    iso_mean_C13 = iso_mean_C13[complete_datasets]
  )
  
  return(result)
}

# Function to create plots using ggpubr (matching plot_results_iso_valid.R style)
create_plots <- function(outdir, datasets = NULL) {
  # Get data dynamically
  results <- process_results(outdir, datasets)
  
  p_values <- results$p_values
  vp_values <- results$vp_values
  complete_datasets <- results$complete_datasets
  
  # Define colors - use distinct colors for each replicate
  colors <- c('#E69F00', '#56B4E9')  # Orange and blue for the two datasets
  
  # Prepare data for plotting - p variations with type categories
  plot_data_p <- data.frame()
  for (i in seq_along(complete_datasets)) {
    dataset <- complete_datasets[i]
    
    for (j in seq_along(p_values)) {
      p_val <- p_values[j]
      nat_count <- results$cf_counts_nat[[dataset]][j]
      c13_count <- results$cf_counts_C13[[dataset]][j]
      
      # Add nat_nist data
      plot_data_p <- rbind(plot_data_p, data.frame(
        p_setting = p_val,
        dataset = paste0('rep', i),
        type = 'nat_nist',
        count = nat_count,
        color = colors[i]
      ))
      
      # Add C13 data
      plot_data_p <- rbind(plot_data_p, data.frame(
        p_setting = p_val,
        dataset = paste0('rep', i),
        type = 'C13_95',
        count = c13_count,
        color = colors[i]
      ))
    }
  }
  
  # Prepare data for plotting - vp variations with type categories
  plot_data_vp <- data.frame()
  for (i in seq_along(complete_datasets)) {
    dataset <- complete_datasets[i]
    
    for (j in seq_along(vp_values)) {
      vp_val <- vp_values[j]
      nat_mean <- results$iso_mean_nat[[dataset]][j]
      c13_mean <- results$iso_mean_C13[[dataset]][j]
      
      # Add nat_nist data
      plot_data_vp <- rbind(plot_data_vp, data.frame(
        vp_setting = vp_val,
        dataset = paste0('rep', i),
        type = 'nat_nist',
        mean_iso = nat_mean,
        color = colors[i]
      ))
      
      # Add C13 data
      plot_data_vp <- rbind(plot_data_vp, data.frame(
        vp_setting = vp_val,
        dataset = paste0('rep', i),
        type = 'C13_95',
        mean_iso = c13_mean,
        color = colors[i]
      ))
    }
  }
  
  # Create alpha levels for types
  plot_data_p$type_order <- factor(plot_data_p$type, 
                                   levels = c("nat_nist", "C13_95"),
                                   labels = c("nat_nist", "C13_95"))
  
  plot_data_vp$type_order <- factor(plot_data_vp$type, 
                                    levels = c("nat_nist", "C13_95"),
                                    labels = c("nat_nist", "C13_95"))
  
  # Create plot 1: Number of CF vs p settings with alpha for types
  p1 <- ggplot(plot_data_p, aes(x = factor(p_setting), y = count, fill = dataset, alpha = type_order)) +
    geom_bar(stat = "identity", position = position_dodge(width = 0.8), width = 0.7) +
    scale_fill_manual(values = colors, name = "Datasets",
                     labels = complete_datasets) +
    scale_alpha_manual(
      values = c("nat_nist" = 0.5, "C13_95" = 1.0),
      name = "Type",
      labels = c("nat_nist", "C13_95"),
      guide = guide_legend(override.aes = list(fill = "black"))
    ) +
    labs(x = "p setting (ppm)",
         y = "Number of unique CFs") +
    theme_pubr() +
    theme(
      axis.title.x = element_text(size = 20),
      axis.title.y = element_text(size = 20),
      axis.text.x = element_text(size = 18),
      axis.text.y = element_text(size = 18),
      legend.title = element_text(size = 16),
      legend.text = element_text(size = 14),
      legend.position = "right",
      plot.margin = margin(20, 5.5, 20, 5.5, "pt")
    ) +
    geom_text(aes(label = round(count, 0)), 
              position = position_dodge(width = 0.8), 
              vjust = -0.5, color = "black",
              size = 6)
  
  # Create plot 2: Average number of isotopes vs vp settings with alpha for types
  p2 <- ggplot(plot_data_vp, aes(x = factor(vp_setting), y = mean_iso, fill = dataset, alpha = type_order)) +
    geom_bar(stat = "identity", position = position_dodge(width = 0.8), width = 0.7) +
    scale_fill_manual(values = colors, name = "Datasets",
                     labels = complete_datasets) +
    scale_alpha_manual(
      values = c("nat_nist" = 0.5, "C13_95" = 1.0),
      name = "Type",
      labels = c("nat_nist", "C13_95"),
      guide = guide_legend(override.aes = list(fill = "black"))
    ) +
    labs(x = "vp setting (ppm)",
         y = "Avg. number of isotopes") +
    theme_pubr() +
    theme(
      axis.title.x = element_text(size = 20),
      axis.title.y = element_text(size = 20),
      axis.text.x = element_text(size = 18),
      axis.text.y = element_text(size = 18),
      legend.title = element_text(size = 16),
      legend.text = element_text(size = 14),
      legend.position = "right",
      plot.margin = margin(20, 5.5, 20, 5.5, "pt")
    ) +
    geom_text(aes(label = sprintf("%.1f", mean_iso)), 
              position = position_dodge(width = 0.8), 
              vjust = -0.5, color = "black",
              size = 6)
  
  # Create publication-ready legends
  # Legend 1: Type (alpha levels) - Create a proper legend with alpha representation
  legend_data_types <- data.frame(
    type = factor(c("nat_nist", "C13_95"),
                 levels = c("nat_nist", "C13_95")),
    value = c(1, 1),
    fill_color = "#2E86AB"  # Use a consistent color
  )
  
  legend_plot_types <- ggplot(legend_data_types, aes(x = type, y = value, fill = fill_color, alpha = type)) +
    geom_bar(stat = "identity", width = 0.6) +
    scale_alpha_manual(
      values = c("nat_nist" = 0.5, "C13_95" = 1.0),
      name = "Type",
      guide = guide_legend(override.aes = list(fill = "black"))
    ) +
    scale_fill_manual(values = "#2E86AB", guide = "none") +
    theme_void() +
    theme(
      legend.title = element_text(size = 18, face = "bold"),
      legend.text = element_text(size = 16),
      legend.key.size = unit(1.0, "cm"),
      legend.margin = margin(5, 5, 5, 5),
      legend.box.margin = margin(5, 5, 5, 5),
      legend.position = "right"
    )
  
  # Legend 2: Datasets (colors)
  legend_data_datasets <- data.frame(
    dataset = factor(complete_datasets, 
                    levels = complete_datasets),
    value = rep(1, length(complete_datasets))
  )
  
  legend_plot_datasets <- ggplot(legend_data_datasets, aes(x = dataset, y = value, fill = dataset)) +
    geom_bar(stat = "identity", width = 0.6) +
    scale_fill_manual(values = colors, name = "Datasets") +
    theme_void() +
    theme(
      legend.title = element_text(size = 18, face = "bold"),
      legend.text = element_text(size = 16),
      legend.key.size = unit(1.0, "cm"),
      legend.margin = margin(5, 5, 5, 5),
      legend.box.margin = margin(5, 5, 5, 5),
      legend.position = "right"
    )
  
  # Extract legends
  legend_grob_types <- get_legend(legend_plot_types)
  legend_grob_datasets <- get_legend(legend_plot_datasets)
  
  # Remove legends from individual plots
  p1_no_legend <- p1 + theme(legend.position = "none")
  p2_no_legend <- p2 + theme(legend.position = "none")
  
  # Combine plots first with vertical alignment and spacing
  combined_plot <- ggarrange(p1_no_legend, p2_no_legend, 
                           ncol = 1, nrow = 2,
                           labels = c("a", "b"),
                           font.label = list(size = 25, face = "bold"),
                           hjust = -0.1, vjust = 1.2,
                           align = "v",
                           heights = c(1, 1))
  
  # Add both legends as insets to the combined plot
  combined_plot_with_legend <- ggdraw(combined_plot) +
    draw_plot(legend_grob_types, x = 0.02, y = 0.88, width = 0.28, height = 0.11) +
    draw_plot(legend_grob_datasets, x = 0.02, y = 0.79, width = 0.28, height = 0.09)
  
  # Save plots
  ggsave(file.path(outdir, "analysis_results.pdf"), 
         combined_plot_with_legend, 
         width = 16, height = 14, 
         dpi = 600)
  
  ggsave(file.path(outdir, "analysis_results.png"), 
         combined_plot_with_legend, 
         width = 16, height = 14, 
         dpi = 300)
  
  cat("Plots saved successfully!\n")
  cat("- analysis_results.pdf\n")
  cat("- analysis_results.png\n")
  
  return(combined_plot_with_legend)
}

# Main execution function
main <- function() {
  # Parse command line arguments
  args <- commandArgs(trailingOnly = TRUE)
  if (length(args) == 0) {
    stop("Please provide the output directory path")
  }
  
  outdir <- args[1]
  
  # Check if outdir exists
  if (!dir.exists(outdir)) {
    stop("Output directory does not exist: ", outdir)
  }
  
  # Create plots with default datasets
  datasets <- c('testdata1', 'testdata2')
  
  cat("Creating plots using ggpubr...\n")
  plot <- create_plots(outdir, datasets)
  
  cat("Plot creation complete!\n")
}

# Run main function if script is executed directly
if (!interactive() && length(commandArgs(trailingOnly = TRUE)) > 0) {
  main()
}

