# R script to create plots equivalent to plot_results_iso_valid.py using ggpubr
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
  cat("Columns:", paste(colnames(df), collapse = ", "), "\n")
  
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

# Function to count number of features with iso_count greater than zero
count_number_of_iso_count_greater_than_zero <- function(df) {
  cat("count_number_of_iso_count_greater_than_zero\n")
  cat("Columns:", paste(colnames(df), collapse = ", "), "\n")
  
  # Handle different column names for nat_nist_mass
  nat_col <- if ("nat_nist_mass" %in% colnames(df)) {
    "nat_nist_mass"
  } else if ("nat_nist" %in% colnames(df)) {
    "nat_nist"
  } else {
    stop("Cannot find nat_nist_mass or nat_nist column")
  }
  
  # Handle different column names for iso_count
  iso_count_col <- if ("iso_count" %in% colnames(df)) {
    "iso_count"
  } else {
    stop("Cannot find iso_count column")
  }
  
  valid_rows <- df[[nat_col]] != 'NO_MASS_MATCH' & !is.na(df[[nat_col]])
  cat("Sample", nat_col, "values:\n")
  print(head(df[valid_rows, nat_col]))
  cat("Summary of", nat_col, ":\n")
  print(summary(df[valid_rows, nat_col]))
  return(sum(valid_rows & (df[[iso_count_col]] >= 1)))
}

# Function to count number of valid features
count_number_of_nat_valid <- function(df) {
  cat("count_number_of_nat_valid\n")
  
  # Handle different column names for nat_nist_mass
  nat_col <- if ("nat_nist_mass" %in% colnames(df)) {
    "nat_nist_mass"
  } else if ("nat_nist" %in% colnames(df)) {
    "nat_nist"
  } else {
    stop("Cannot find nat_nist_mass or nat_nist column")
  }
  
  # Handle different column names for iso_valid
  iso_valid_col <- if ("iso_valid" %in% colnames(df)) {
    "iso_valid"
  } else {
    stop("Cannot find iso_valid column")
  }
  
  valid_rows <- df[[nat_col]] != 'NO_MASS_MATCH' & !is.na(df[[nat_col]])
  cat("Summary of", iso_valid_col, ":\n")
  print(summary(df[valid_rows, iso_valid_col]))
  return(sum(valid_rows & (df[[iso_valid_col]] >= 1)))
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
  
  # Handle different column names for iso_count
  iso_count_col <- if ("iso_count" %in% colnames(df)) {
    "iso_count"
  } else {
    stop("Cannot find iso_count column")
  }
  
  valid_rows <- df[[nat_col]] != 'NO_MASS_MATCH' & !is.na(df[[nat_col]])
  cat("Summary of", iso_count_col, ":\n")
  print(summary(df[valid_rows, iso_count_col]))
  mean_val <- mean(df[[iso_count_col]][valid_rows], na.rm = TRUE)
  if (is.na(mean_val) || is.nan(mean_val) || length(mean_val) == 0) mean_val <- 0
  cat("Mean", iso_count_col, ":", mean_val, "\n")
  return(mean_val)
}

# Function to calculate mean valid isotopes for natural abundance data
mean_isotopes_valid_nat <- function(df) {
  cat("mean_isotopes_valid_nat\n")
  
  # Handle different column names for nat_nist_mass
  nat_col <- if ("nat_nist_mass" %in% colnames(df)) {
    "nat_nist_mass"
  } else if ("nat_nist" %in% colnames(df)) {
    "nat_nist"
  } else {
    stop("Cannot find nat_nist_mass or nat_nist column")
  }
  
  # Handle different column names for iso_valid
  iso_valid_col <- if ("iso_valid" %in% colnames(df)) {
    "iso_valid"
  } else {
    stop("Cannot find iso_valid column")
  }
  
  valid_rows <- df[[nat_col]] != 'NO_MASS_MATCH' & !is.na(df[[nat_col]])
  cat("Summary of", iso_valid_col, ":\n")
  print(summary(df[valid_rows, iso_valid_col]))
  mean_val <- mean(df[[iso_valid_col]][valid_rows], na.rm = TRUE)
  if (is.na(mean_val) || is.nan(mean_val) || length(mean_val) == 0) mean_val <- 0
  cat("Mean", iso_valid_col, ":", mean_val, "\n")
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
      df <- read_tsv(filepath, skip = 2, show_col_types = FALSE)
      # Remove duplicate rows based on first column (CF)
      df <- df[!duplicated(df[,1]), ]
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
  # Auto-discover datasets if not provided
  if (is.null(datasets)) {
    pattern <- file.path(outdir, "n*_p*_vp*_combined.tsv")
    files <- Sys.glob(pattern)
    datasets <- character(0)
    for (file in files) {
      basename <- basename(file)
      if (startsWith(basename, 'n') && grepl('_p', basename)) {
        # Extract dataset name from filename like "nDATASET_p*_vp*_combined.tsv"
        # Remove 'n' prefix and '_p' suffix to get dataset name
        dataset_part <- substring(basename, 2)  # Remove 'n' prefix
        # Find the position of '_p' to extract just the dataset name
        p_pos <- regexpr('_p', dataset_part)
        if (p_pos > 0) {
          dataset_name <- substring(dataset_part, 1, p_pos - 1)
          datasets <- c(datasets, dataset_name)
        }
      }
    }
    datasets <- sort(unique(datasets))
    cat("Auto-discovered datasets:", paste(datasets, collapse = ", "), "\n")
  }
  
  df_cache <- list()
  
  # Data for top graph (varying p, fixed vp=0.5)
  p_values <- c(0.1, 0.5, 1.0)
  cf_counts_nat <- list()
  cf_counts_iso_count_greater_than_zero <- list()
  cf_counts_nat_valid <- list()
  
  # Data for bottom graph (varying vp, fixed p=0.5)
  vp_values <- c(0.1, 0.5, 1.0)
  iso_mean_nat <- list()
  valid_iso_mean_nat <- list()
  
  # Count data for vp variations (same as p variations)
  cf_counts_nat_vp <- list()
  cf_counts_iso_count_greater_than_zero_vp <- list()
  cf_counts_nat_valid_vp <- list()
  
  # Initialize lists for each dataset
  for (dataset in datasets) {
    cf_counts_nat[[dataset]] <- numeric(0)
    cf_counts_iso_count_greater_than_zero[[dataset]] <- numeric(0)
    cf_counts_nat_valid[[dataset]] <- numeric(0)
    iso_mean_nat[[dataset]] <- numeric(0)
    valid_iso_mean_nat[[dataset]] <- numeric(0)
    cf_counts_nat_vp[[dataset]] <- numeric(0)
    cf_counts_iso_count_greater_than_zero_vp[[dataset]] <- numeric(0)
    cf_counts_nat_valid_vp[[dataset]] <- numeric(0)
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
      cf_counts_iso_count_greater_than_zero[[dataset]] <- c(cf_counts_iso_count_greater_than_zero[[dataset]], 
                                                           count_number_of_iso_count_greater_than_zero(df))
      cf_counts_nat_valid[[dataset]] <- c(cf_counts_nat_valid[[dataset]], count_number_of_nat_valid(df))
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
      valid_iso_mean_nat[[dataset]] <- c(valid_iso_mean_nat[[dataset]], mean_isotopes_valid_nat(df))
      
      # Also collect count data for vp variations
      cf_counts_nat_vp[[dataset]] <- c(cf_counts_nat_vp[[dataset]], count_number_of_nat(df))
      cf_counts_iso_count_greater_than_zero_vp[[dataset]] <- c(cf_counts_iso_count_greater_than_zero_vp[[dataset]], 
                                                              count_number_of_iso_count_greater_than_zero(df))
      cf_counts_nat_valid_vp[[dataset]] <- c(cf_counts_nat_valid_vp[[dataset]], count_number_of_nat_valid(df))
    }
  }
  
  # Filter out datasets that don't have complete data
  complete_datasets <- character(0)
  for (dataset in datasets) {
    has_p_data <- (length(cf_counts_nat[[dataset]]) == length(p_values) && 
                   length(cf_counts_iso_count_greater_than_zero[[dataset]]) == length(p_values) && 
                   length(cf_counts_nat_valid[[dataset]]) == length(p_values))
    has_vp_data <- (length(iso_mean_nat[[dataset]]) == length(vp_values) &&
                    length(valid_iso_mean_nat[[dataset]]) == length(vp_values) &&
                    length(cf_counts_nat_vp[[dataset]]) == length(vp_values) &&
                    length(cf_counts_iso_count_greater_than_zero_vp[[dataset]]) == length(vp_values) &&
                    length(cf_counts_nat_valid_vp[[dataset]]) == length(vp_values))
    
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
    cf_counts_iso_count_greater_than_zero = cf_counts_iso_count_greater_than_zero[complete_datasets],
    cf_counts_nat_valid = cf_counts_nat_valid[complete_datasets],
    iso_mean_nat = iso_mean_nat[complete_datasets],
    valid_iso_mean_nat = valid_iso_mean_nat[complete_datasets],
    cf_counts_nat_vp = cf_counts_nat_vp[complete_datasets],
    cf_counts_iso_count_greater_than_zero_vp = cf_counts_iso_count_greater_than_zero_vp[complete_datasets],
    cf_counts_nat_valid_vp = cf_counts_nat_valid_vp[complete_datasets]
  )
  
  return(result)
}

# Function to create plots using ggpubr with faceting by VP settings and category as x-axis
create_plots <- function(outdir, datasets = NULL) {
  # Get data dynamically
  results <- process_results(outdir, datasets)
  
  p_values <- results$p_values
  vp_values <- results$vp_values
  complete_datasets <- results$complete_datasets
  
  # Generate colors dynamically based on number of datasets
  colors <- c('#E69F00', '#56B4E9', '#009E73', '#F0E442', '#0072B2', '#D55E00', '#CC79A7')[1:length(complete_datasets)]
  
  # Prepare data for plotting - p variations
  plot_data_p <- data.frame()
  for (i in seq_along(complete_datasets)) {
    dataset <- complete_datasets[i]
    dataset_label <- paste0('nat_nist_', dataset)
    
    for (j in seq_along(p_values)) {
      p_val <- p_values[j]
      total_cf <- results$cf_counts_nat[[dataset]][j]
      iso_count_cf <- results$cf_counts_iso_count_greater_than_zero[[dataset]][j]
      valid_cf <- results$cf_counts_nat_valid[[dataset]][j]
      
      plot_data_p <- rbind(plot_data_p, data.frame(
        p_setting = p_val,
        dataset = dataset_label,
        Total_CF = total_cf,
        Has_isotopes = iso_count_cf,
        Valid = valid_cf,
        color = colors[i]
      ))
    }
  }
  
  # Prepare data for plotting - vp variations
  plot_data_vp <- data.frame()
  for (i in seq_along(complete_datasets)) {
    dataset <- complete_datasets[i]
    dataset_label <- paste0('nat_nist_', dataset)
    
    for (j in seq_along(vp_values)) {
      vp_val <- vp_values[j]
      total_cf_vp <- results$cf_counts_nat_vp[[dataset]][j]
      iso_count_cf_vp <- results$cf_counts_iso_count_greater_than_zero_vp[[dataset]][j]
      valid_cf_vp <- results$cf_counts_nat_valid_vp[[dataset]][j]
      
      plot_data_vp <- rbind(plot_data_vp, data.frame(
        vp_setting = vp_val,
        dataset = dataset_label,
        Total_CF = total_cf_vp,
        Has_isotopes = iso_count_cf_vp,
        Valid = valid_cf_vp,
        color = colors[i]
      ))
    }
  }
  
  # Convert to long format for faceted plots - facet by p/vp settings, x by category
  plot_data_p_long <- plot_data_p %>%
    pivot_longer(cols = c(Total_CF, Has_isotopes, Valid), 
                 names_to = "category", 
                 values_to = "count") %>%
    mutate(category = factor(category, levels = c("Total_CF", "Has_isotopes", "Valid"),
                           labels = c("Matched monoisotopic mass", "Has isotopes at least one", "Valid isotope at least one")),
           p_facet = paste0("p=", p_setting),
           # Create a combined grouping variable for custom ordering
           group_order = paste0(dataset, "_", category)) %>%
    select(-p_setting)  # Remove p_setting column
  
  plot_data_vp_long <- plot_data_vp %>%
    pivot_longer(cols = c(Total_CF, Has_isotopes, Valid), 
                 names_to = "category", 
                 values_to = "count") %>%
    mutate(category = factor(category, levels = c("Total_CF", "Has_isotopes", "Valid"),
                           labels = c("Matched monoisotopic mass", "Has isotopes at least one", "Valid isotope at least one")),
           vp_facet = paste0("vp=", vp_setting)) %>%
    select(-vp_setting)  # Remove vp_setting column
  
  # Create plots using ggpubr with faceting by p/vp settings
  # Plot 1: p variations (faceted by p settings)
  # For p=0.1, we want to group bars by dataset (color) first, then by category
  p1 <- ggplot(plot_data_p_long, aes(x = category, y = count, fill = dataset)) +
    geom_bar(stat = "identity", position = position_dodge(0.8), width = 0.7) +
    facet_wrap(~p_facet, ncol = 3, scales = "free_x") +
    scale_fill_manual(values = colors, name = "Datasets") +
    labs(title = "a - CF Analysis by Category (p variation)",
         x = "Category",
         y = "Number of CF") +
    theme_pubr() +
    theme(
      plot.title = element_text(hjust = 0, face = "bold", size = 16),
      axis.title = element_text(size = 14),
      axis.text = element_text(size = 12),
      axis.text.x = element_text(angle = 45, hjust = 1),
      legend.title = element_text(size = 14),
      legend.text = element_text(size = 12),
      strip.text = element_text(size = 12)
    ) +
    geom_text(aes(label = round(count, 0)), 
              position = position_dodge(0.8), 
              vjust = -0.5, 
              size = 3)
  
  # Plot 2: vp variations (faceted by vp settings)
  p2 <- ggplot(plot_data_vp_long, aes(x = category, y = count, fill = dataset)) +
    geom_bar(stat = "identity", position = position_dodge(0.8), width = 0.7) +
    facet_wrap(~vp_facet, ncol = 3, scales = "free_x") +
    scale_fill_manual(values = colors, name = "Datasets") +
    labs(title = "b - CF Analysis by Category (vp variation)",
         x = "Category",
         y = "Number of CF") +
    theme_pubr() +
    theme(
      plot.title = element_text(hjust = 0, face = "bold", size = 16),
      axis.title = element_text(size = 14),
      axis.text = element_text(size = 12),
      axis.text.x = element_text(angle = 45, hjust = 1),
      legend.title = element_text(size = 14),
      legend.text = element_text(size = 12),
      strip.text = element_text(size = 12)
    ) +
    geom_text(aes(label = round(count, 0)), 
              position = position_dodge(0.8), 
              vjust = -0.5, 
              size = 3)
  
  # Combine plots
  combined_plot <- ggarrange(p1, p2, 
                           ncol = 1, nrow = 2,
                           common.legend = TRUE, 
                           legend = "right",
                           labels = c("a", "b"),
                           font.label = list(size = 16, face = "bold"),
                           hjust = -0.1, vjust = 1.2)
  
  # Save plot
  ggsave(file.path(outdir, "analysis_results_iso_valid_R.pdf"), 
         combined_plot, 
         width = 16, height = 12, 
         dpi = 300)
  
  return(combined_plot)
}

# Alternative implementation with grouped bars (closer to Python version)
create_plots_grouped <- function(outdir, datasets = NULL) {
  # Get data dynamically
  results <- process_results(outdir, datasets)
  
  p_values <- results$p_values
  vp_values <- results$vp_values
  complete_datasets <- results$complete_datasets
  
  # Generate colors dynamically based on number of datasets
  colors <- c('#E69F00', '#56B4E9', '#009E73', '#F0E442', '#0072B2', '#D55E00', '#CC79A7')[1:length(complete_datasets)]
  
  # Prepare data for plotting - p variations (grouped bars like Python)
  plot_data_p <- data.frame()
  for (i in seq_along(complete_datasets)) {
    dataset <- complete_datasets[i]
    dataset_label <- paste0('nat_nist_', dataset)
    
    for (j in seq_along(p_values)) {
      p_val <- p_values[j]
      total_cf <- results$cf_counts_nat[[dataset]][j]
      iso_count_cf <- results$cf_counts_iso_count_greater_than_zero[[dataset]][j]
      valid_cf <- results$cf_counts_nat_valid[[dataset]][j]
      
      # Create separate rows for each category
      plot_data_p <- rbind(plot_data_p, data.frame(
        p_setting = p_val,
        dataset = dataset_label,
        category = "Total CF",
        count = total_cf,
        color = colors[i],
        alpha = 0.4
      ))
      
      plot_data_p <- rbind(plot_data_p, data.frame(
        p_setting = p_val,
        dataset = dataset_label,
        category = "Has isotopes",
        count = iso_count_cf,
        color = colors[i],
        alpha = 0.7
      ))
      
      plot_data_p <- rbind(plot_data_p, data.frame(
        p_setting = p_val,
        dataset = dataset_label,
        category = "Valid",
        count = valid_cf,
        color = colors[i],
        alpha = 1.0
      ))
    }
  }
  
  # Prepare data for plotting - vp variations
  plot_data_vp <- data.frame()
  for (i in seq_along(complete_datasets)) {
    dataset <- complete_datasets[i]
    dataset_label <- paste0('nat_nist_', dataset)
    
    for (j in seq_along(vp_values)) {
      vp_val <- vp_values[j]
      total_cf_vp <- results$cf_counts_nat_vp[[dataset]][j]
      iso_count_cf_vp <- results$cf_counts_iso_count_greater_than_zero_vp[[dataset]][j]
      valid_cf_vp <- results$cf_counts_nat_valid_vp[[dataset]][j]
      
      # Create separate rows for each category
      plot_data_vp <- rbind(plot_data_vp, data.frame(
        vp_setting = vp_val,
        dataset = dataset_label,
        category = "Total CF",
        count = total_cf_vp,
        color = colors[i],
        alpha = 0.4
      ))
      
      plot_data_vp <- rbind(plot_data_vp, data.frame(
        vp_setting = vp_val,
        dataset = dataset_label,
        category = "Has isotopes",
        count = iso_count_cf_vp,
        color = colors[i],
        alpha = 0.7
      ))
      
      plot_data_vp <- rbind(plot_data_vp, data.frame(
        vp_setting = vp_val,
        dataset = dataset_label,
        category = "Valid",
        count = valid_cf_vp,
        color = colors[i],
        alpha = 1.0
      ))
    }
  }
  
  # Create custom grouped bar plots with proper alpha ordering
  # Plot 1: p variations
  # Ensure proper ordering: Total CF (alpha 0.4) first, then Has isotopes (alpha 0.7), then Valid (alpha 1.0)
  plot_data_p$category_order <- factor(plot_data_p$category, 
                                     levels = c("Total CF", "Has isotopes", "Valid"),
                                     labels = c("Matched monoisotopic mass", "Has isotopes at least one", "Valid isotope at least one"))
  
  p1 <- ggplot(plot_data_p, aes(x = factor(p_setting), y = count, fill = dataset, alpha = category_order)) +
    geom_bar(stat = "identity", position = position_dodge(width = 0.8), width = 0.7) +
    scale_fill_manual(values = colors, name = "Datasets") +
    scale_alpha_manual(
      values = c("Matched monoisotopic mass" = 0.4, 
                 "Has isotopes at least one" = 0.7, 
                 "Valid isotope at least one" = 1.0),
      name = "CF Categories",
      guide = guide_legend(override.aes = list(label = ""))
    ) +
    labs(x = "p setting (ppm)",
         y = "Number of CF") +
    theme_pubr() +
    theme(
      axis.title = element_text(size = 14),
      axis.text = element_text(size = 14),
      legend.title = element_text(size = 14),
      legend.text = element_text(size = 14),
      legend.position = "right"
    ) +
    geom_text(aes(label = round(count, 0)), 
              position = position_dodge(width = 0.8), 
              vjust = -0.5, color = "black",
              size = 4)
  
  # Plot 2: vp variations with proper alpha ordering
  # Ensure proper ordering: Total CF (alpha 0.4) first, then Has isotopes (alpha 0.7), then Valid (alpha 1.0)
  plot_data_vp$category_order <- factor(plot_data_vp$category, 
                                      levels = c("Total CF", "Has isotopes", "Valid"),
                                      labels = c("Matched monoisotopic mass", "Has isotopes at least one", "Valid isotope at least one"))
  
  p2 <- ggplot(plot_data_vp, aes(x = factor(vp_setting), y = count, fill = dataset, alpha = category_order)) +
    geom_bar(stat = "identity", position = position_dodge(width = 0.8), width = 0.7) +
    scale_fill_manual(values = colors, name = "Datasets") +
    scale_alpha_manual(
      values = c("Matched monoisotopic mass" = 0.4, 
                 "Has isotopes at least one" = 0.7, 
                 "Valid isotope at least one" = 1.0),
      name = "CF Categories",
      guide = guide_legend(override.aes = list(label = ""))
    ) +
    labs(x = "vp setting (ppm)",
         y = "Number of CF") +
    theme_pubr() +
    theme(
      axis.title = element_text(size = 14),
      axis.text = element_text(size = 14),
      legend.title = element_text(size = 14),
      legend.text = element_text(size = 14),
      legend.position = "right"
    ) +
    geom_text(aes(label = round(count, 0)), 
              position = position_dodge(width = 0.8), 
              vjust = -0.5,  color = "black",
              size = 4)
  
  # Create publication-ready legends
  # Legend 1: CF Categories (alpha levels) - Create a proper legend with alpha representation
  legend_data_categories <- data.frame(
    category = factor(c("Matched monoisotopic mass", "Has isotopes at least one", "Valid isotope at least one"),
                     levels = c("Matched monoisotopic mass", "Has isotopes at least one", "Valid isotope at least one")),
    value = c(1, 1, 1),
    fill_color = "#2E86AB"  # Use a consistent color
  )
  
  legend_plot_categories <- ggplot(legend_data_categories, aes(x = category, y = value, fill = fill_color, alpha = category)) +
    geom_bar(stat = "identity", width = 0.6) +
    scale_alpha_manual(
      values = c("Matched monoisotopic mass" = 0.4, 
                 "Has isotopes at least one" = 0.7, 
                 "Valid isotope at least one" = 1.0),
      name = "CF Categories",
      guide = guide_legend(override.aes = list(fill = "black"))
    ) +
    scale_fill_manual(values = "#2E86AB", guide = "none") +
    theme_void() +
    theme(
      legend.title = element_text(size = 12, face = "bold"),
      legend.text = element_text(size = 12),
      legend.key.size = unit(0.4, "cm"),
      legend.margin = margin(2, 2, 2, 2),
      legend.box.margin = margin(2, 2, 2, 2),
      legend.position = "right"
    )
  
  # Legend 2: Datasets (colors) - Clean up dataset names
  dataset_labels <- gsub("nat_nist_", "", complete_datasets)
  dataset_labels <- gsub("_", " ", dataset_labels)
  dataset_labels <- tools::toTitleCase(dataset_labels)
  
  legend_data_datasets <- data.frame(
    dataset = factor(paste0('nat_nist_', complete_datasets), 
                    levels = paste0('nat_nist_', complete_datasets),
                    labels = dataset_labels),
    value = rep(1, length(complete_datasets))
  )
  
  legend_plot_datasets <- ggplot(legend_data_datasets, aes(x = dataset, y = value, fill = dataset)) +
    geom_bar(stat = "identity", width = 0.6) +
    scale_fill_manual(values = colors, name = "Datasets") +
    theme_void() +
    theme(
      legend.title = element_text(size = 12, face = "bold"),
      legend.text = element_text(size = 12),
      legend.key.size = unit(0.4, "cm"),
      legend.margin = margin(2, 2, 2, 2),
      legend.box.margin = margin(2, 2, 2, 2),
      legend.position = "right"
    )
  
  # Extract legends
  legend_grob_categories <- get_legend(legend_plot_categories)
  legend_grob_datasets <- get_legend(legend_plot_datasets)
  
  # Remove legends from individual plots
  p1_no_legend <- p1 + theme(legend.position = "none")
  p2_no_legend <- p2 + theme(legend.position = "none")
  
  # Combine plots first
  combined_plot <- ggarrange(p1_no_legend, p2_no_legend, 
                           ncol = 1, nrow = 2,
                           labels = c("a", "b"),
                           font.label = list(size = 20, face = "bold"),
                           hjust = -0.1, vjust = 1.2)
  
  # Add both legends as insets to the combined plot
  combined_plot_with_legend <- ggdraw(combined_plot) +
    draw_plot(legend_grob_categories, x = 0.02, y = 0.85, width = 0.25, height = 0.15) +
    draw_plot(legend_grob_datasets, x = 0.02, y = 0.78, width = 0.25, height = 0.15)
  
  # Save plot
  ggsave(file.path(outdir, "analysis_results_iso_valid_R_grouped.pdf"), 
         combined_plot_with_legend, 
         width = 16, height = 12, 
         dpi = 600)
  
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
  datasets <- c('combined_N-metabolites_std', 'testdata1')
  
  cat("Creating plots using ggpubr...\n")
  
  # Create both versions of plots
  cat("Creating faceted version...\n")
  plot1 <- create_plots(outdir, datasets)
  
  cat("Creating grouped version...\n")
  plot2 <- create_plots_grouped(outdir, datasets)
  
  cat("Plots saved successfully!\n")
  cat("- analysis_results_iso_valid_R.pdf (faceted version)\n")
  cat("- analysis_results_iso_valid_R_grouped.pdf (grouped version)\n")
}

# Run main function if script is executed directly
if (!interactive() && length(commandArgs(trailingOnly = TRUE)) > 0) {
  main()
}
