import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import glob
import os
import sys
def count_number_of_nat(df):
    """Count number of features for natural abundance data"""
    print('count_number_of_nat')
    print(df.columns)
    print(df[df['nat_nist_mass'] != 'NO_MASS_MATCH']['nat_nist_mass'].head())
    print(df[df['nat_nist_mass'] != 'NO_MASS_MATCH']['nat_nist_mass'].describe())
    return df[df['nat_nist_mass'] != 'NO_MASS_MATCH'].shape[0]


def count_number_of_iso_count_greater_than_zero(df):
    """Count number of features for natural abundance data"""
    print('count_number_of_nat')
    print(df.columns)
    print(df[df['nat_nist_mass'] != 'NO_MASS_MATCH']['nat_nist_mass'].head())
    print(df[df['nat_nist_mass'] != 'NO_MASS_MATCH']['nat_nist_mass'].describe())
    return df[(df['nat_nist_mass'] != 'NO_MASS_MATCH') & (df['iso_count'] >= 1)].shape[0]

def count_number_of_nat_valid(df):
    """Count number of features for natural abundance data"""
    print('count_number_of_nat_valid')
    print(df[df['nat_nist_mass'] != 'NO_MASS_MATCH']['iso_valid'].describe())
    return df[(df['nat_nist_mass'] != 'NO_MASS_MATCH') & (df['iso_valid'] >= 1)].shape[0]

# def mean_valid_isotopes_nat(df):
#     """Count total number of valid isotopes for natural abundance data"""
#     print('mean_valid_isotopes_nat')
#     print(df[df['db_nat_mass'].notna()]['iso_valid'].describe())
#     print(df[df['db_nat_mass'].notna()]['iso_valid'].mean())
#     return df[df['db_nat_mass'].notna()]['iso_valid'].mean()

# def mean_valid_isotopes_C13(df):
#     """Count total number of valid isotopes for C13 data"""
#     print('mean_valid_isotopes_C13')
#     print(df[df['db_C13_mass'].notna()]['iso_valid.1'].describe())
#     print(df[df['db_C13_mass'].notna()]['iso_valid.1'].mean())
#     return df[df['db_C13_mass'].notna()]['iso_valid.1'].mean()


def mean_isotopes_nat(df):
    """Count total number of valid isotopes for natural abundance data"""
    print('mean_isotopes_nat')
    print(df[df['nat_nist_mass'] != 'NO_MASS_MATCH']['iso_count'].describe())
    print(df[df['nat_nist_mass'] != 'NO_MASS_MATCH']['iso_count'].mean())
    return df[df['nat_nist_mass'] != 'NO_MASS_MATCH']['iso_count'].mean()

def mean_isotopes_valid_nat(df):
    """Count total number of valid isotopes for natural abundance data"""
    print('mean_isotopes_valid_nat')
    print(df[df['nat_nist_mass'] != 'NO_MASS_MATCH']['iso_valid'].describe())
    print(df[df['nat_nist_mass'] != 'NO_MASS_MATCH']['iso_valid'].mean())
    return df[df['nat_nist_mass'] != 'NO_MASS_MATCH']['iso_valid'].mean()

def process_results(outdir, datasets=None):
    """Process all result files and compile data for plotting"""
    # Auto-discover datasets if not provided
    if datasets is None:
        # Look for files matching pattern n*_p*_vp*_combined.tsv
        import glob
        pattern = os.path.join(outdir, "n*_p*_vp*_combined.tsv")
        files = glob.glob(pattern)
        datasets = set()
        for file in files:
            # Extract dataset name from filename like "nDATASET_p*_vp*_combined.tsv"
            basename = os.path.basename(file)
            if basename.startswith('n') and '_p' in basename:
                dataset_part = basename[1:]  # Remove 'n' prefix
                dataset_name = dataset_part  # Get part before '_p'
                datasets.add(dataset_name)
        datasets = sorted(list(datasets))
        print(f"Auto-discovered datasets: {datasets}")
    
    df_cache = {}  # Cache DataFrames to avoid reading same file twice
    
    def get_df(filepath):
        if filepath not in df_cache:
            try:
                df_cache[filepath] = pd.read_csv(filepath, sep='\t', skiprows=2)
            except (pd.errors.EmptyDataError, pd.errors.ParserError) as e:
                print(f"Warning: Could not read file {filepath}: {e}")
                return None
            except FileNotFoundError:
                print(f"Warning: File {filepath} not found")
                return None
        return df_cache[filepath]
    
    # Data for top graph (varying p, fixed vp=0.5)
    p_values = [0.1, 0.5, 1.0]
    cf_counts_nat = {dataset: [] for dataset in datasets}
    cf_counts_iso_count_greater_than_zero = {dataset: [] for dataset in datasets}
    cf_counts_nat_valid = {dataset: [] for dataset in datasets}
    
    # Data for bottom graph (varying vp, fixed p=0.5)
    vp_values = [0.1, 0.5, 1.0]
    iso_mean_nat = {dataset: [] for dataset in datasets}
    valid_iso_mean_nat = {dataset: [] for dataset in datasets}
    
    # Count data for vp variations (same as p variations)
    cf_counts_nat_vp = {dataset: [] for dataset in datasets}
    cf_counts_iso_count_greater_than_zero_vp = {dataset: [] for dataset in datasets}
    cf_counts_nat_valid_vp = {dataset: [] for dataset in datasets}

    # Process files for all datasets
    for dataset in datasets:
        # Process files for top graph
        for p in p_values:
            p_str = str(p).replace('.', '') if p < 1 else str(int(p))
            combined_file = os.path.join(outdir, f"n{dataset}_p{p_str}_vp05_combined.tsv")
            print(combined_file)
            df = get_df(combined_file)
            if df is None:
                print(f"Skipping {combined_file} due to read error")
                continue
            # print(df.columns)
            # print(df.head(2)['CF'])
            # sys.exit()
            cf_counts_nat[f'{dataset}'].append(count_number_of_nat(df))
            cf_counts_iso_count_greater_than_zero[f'{dataset}'].append(count_number_of_iso_count_greater_than_zero(df))
            cf_counts_nat_valid[f'{dataset}'].append(count_number_of_nat_valid(df))

            
        # Process files for middle graph
        for vp in vp_values:
            vp_str = str(vp).replace('.', '') if vp < 1 else str(int(vp))
            combined_file = os.path.join(outdir, f"n{dataset}_p05_vp{vp_str}_combined.tsv")
            print(combined_file)
            df = get_df(combined_file)
            if df is None:
                print(f"Skipping {combined_file} due to read error")
                continue
            iso_mean_nat[f'{dataset}'].append(mean_isotopes_nat(df))
            valid_iso_mean_nat[f'{dataset}'].append(mean_isotopes_valid_nat(df))
            
            # Also collect count data for vp variations
            cf_counts_nat_vp[f'{dataset}'].append(count_number_of_nat(df))
            cf_counts_iso_count_greater_than_zero_vp[f'{dataset}'].append(count_number_of_iso_count_greater_than_zero(df))
            cf_counts_nat_valid_vp[f'{dataset}'].append(count_number_of_nat_valid(df))

            
        # Process files for bottom graph
        # for vp in vp_values:
        #     vp_str = str(vp).replace('.', '') if vp < 1 else str(int(vp))
        #     combined_file = os.path.join(outdir, f"ntestdata{dataset}_p05_vp{vp_str}_combined.tsv")
        #     print(combined_file)
        #     df = get_df(combined_file)
        #     valid_iso_mean_nat[f'testdata{dataset}'].append(mean_valid_isotopes_nat(df))
        #     valid_iso_mean_C13[f'testdata{dataset}'].append(mean_valid_isotopes_C13(df))
       

    # Remove mean calculations and return individual dataset values
    # return (p_values, 
    #         cf_counts_nat['testdata1'], cf_counts_nat['testdata2'],
    #         cf_counts_C13['testdata1'], cf_counts_C13['testdata2'],
    #         vp_values, 
    #         iso_mean_nat['testdata1'], iso_mean_nat['testdata2'],
    #         iso_mean_C13['testdata1'], iso_mean_C13['testdata2'],
    #         valid_iso_mean_nat['testdata1'], valid_iso_mean_nat['testdata2'],
    #         valid_iso_mean_C13['testdata1'], valid_iso_mean_C13['testdata2'])

    # print(cf_counts_nat)
    # Filter out datasets that don't have complete data
    complete_datasets = []
    for dataset in datasets:
        has_p_data = (len(cf_counts_nat[dataset]) == len(p_values) and 
                     len(cf_counts_iso_count_greater_than_zero[dataset]) == len(p_values) and 
                     len(cf_counts_nat_valid[dataset]) == len(p_values))
        has_vp_data = (len(iso_mean_nat[dataset]) == len(vp_values) and
                      len(valid_iso_mean_nat[dataset]) == len(vp_values) and
                      len(cf_counts_nat_vp[dataset]) == len(vp_values) and
                      len(cf_counts_iso_count_greater_than_zero_vp[dataset]) == len(vp_values) and
                      len(cf_counts_nat_valid_vp[dataset]) == len(vp_values))
        
        if has_p_data and has_vp_data:
            complete_datasets.append(dataset)
        else:
            print(f"Warning: Dataset {dataset} does not have complete data, excluding from analysis")
    
    if not complete_datasets:
        raise ValueError("No datasets have complete data for analysis")
    
    # Return data for all complete datasets dynamically
    result = [p_values]
    
    # Add data for each complete dataset in order
    for dataset in complete_datasets:
        result.extend([
            cf_counts_nat[dataset],
            cf_counts_iso_count_greater_than_zero[dataset],
            cf_counts_nat_valid[dataset]
        ])
    
    result.append(vp_values)
    
    for dataset in complete_datasets:
        result.extend([
            iso_mean_nat[dataset],
            valid_iso_mean_nat[dataset],
            cf_counts_nat_vp[dataset],
            cf_counts_iso_count_greater_than_zero_vp[dataset],
            cf_counts_nat_valid_vp[dataset]
        ])
    
    # Also return the list of complete datasets so the plotting function knows what to expect
    result.append(complete_datasets)
    
    return tuple(result)

def create_plots(outdir, datasets=None):
    """Create the plots using seaborn"""
    # Get data dynamically
    results = process_results(outdir, datasets)
    
    # Auto-discover datasets if not provided (same logic as process_results)
    if datasets is None:
        import glob
        pattern = os.path.join(outdir, "n*_p*_vp*_combined.tsv")
        files = glob.glob(pattern)
        datasets = set()
        for file in files:
            basename = os.path.basename(file)
            if basename.startswith('n') and '_p' in basename:
                dataset_part = basename[1:]  # Remove 'n' prefix
                dataset_name = dataset_part  # Get part before '_p'
                datasets.add(dataset_name)
        datasets = sorted(list(datasets))
    
    # Parse dynamic results - the last element is the list of complete datasets
    complete_datasets = results[-1]
    results = results[:-1]  # Remove the complete_datasets from results
    
    idx = 0
    p_values = results[idx]
    idx += 1
    
    # Extract CF counts data for each complete dataset
    cf_counts_nat_list = []
    cf_counts_iso_count_greater_than_zero_list = []
    cf_counts_nat_valid_list = []
    
    for dataset in complete_datasets:
        cf_counts_nat_list.append(results[idx])
        cf_counts_iso_count_greater_than_zero_list.append(results[idx + 1])
        cf_counts_nat_valid_list.append(results[idx + 2])
        idx += 3
    
    vp_values = results[idx]
    idx += 1
    
    # Extract isotope means and vp data for each complete dataset
    iso_mean_nat_list = []
    valid_iso_mean_nat_list = []
    cf_counts_nat_vp_list = []
    cf_counts_iso_count_greater_than_zero_vp_list = []
    cf_counts_nat_valid_vp_list = []
    
    for dataset in complete_datasets:
        iso_mean_nat_list.append(results[idx])
        valid_iso_mean_nat_list.append(results[idx + 1])
        cf_counts_nat_vp_list.append(results[idx + 2])
        cf_counts_iso_count_greater_than_zero_vp_list.append(results[idx + 3])
        cf_counts_nat_valid_vp_list.append(results[idx + 4])
        idx += 5
    
    # Use complete_datasets instead of datasets for plotting
    datasets = complete_datasets
    
    # Set BMC publication style
    plt.rcParams.update({
        'font.size': 16,
        'axes.titlesize': 18,
        'axes.labelsize': 16,
        'xtick.labelsize': 16,
        'ytick.labelsize': 16,
        'legend.fontsize': 16,
        'figure.titlesize': 20,
        'pdf.fonttype': 42,
        'ps.fonttype': 42,
        'svg.fonttype': 'none'
    })
    
    # Create figure with two subplots  
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(24, 20))
    
    # Create dynamic DataFrames for plotting
    num_datasets = len(datasets)
    
    # df_top1 is Number of CF
    df_top_1 = pd.DataFrame({
        'p setting (ppm)': p_values * num_datasets,
        'Number of CF': [item for sublist in cf_counts_nat_list for item in sublist],
        'Type_Dataset': [f'nat_nist_{dataset}' for dataset in datasets for _ in p_values]
    })

    # df_top2 Number of CF with cf_counts_iso_count_greater_than_zero greater than 1
    df_top_2 = pd.DataFrame({
        'p setting (ppm)': p_values * num_datasets,
        'Number of CF with iso_count greater than 1': [item for sublist in cf_counts_iso_count_greater_than_zero_list for item in sublist],
        'Type_Dataset': [f'nat_nist_{dataset}' for dataset in datasets for _ in p_values]
    })

    # df_top3 Number of CF with cf_counts_nat_valid greater than 1
    df_top_3 = pd.DataFrame({
        'p setting (ppm)': p_values * num_datasets,
        'Number of valid CF': [item for sublist in cf_counts_nat_valid_list for item in sublist],
        'Type_Dataset': [f'nat_nist_{dataset}' for dataset in datasets for _ in p_values]
    })

   

    # # df_top3 with cf_counts_nat_valid greater than 1
    # df_top_4 = pd.DataFrame({
    #     'vp setting (ppm)': vp_values * 3,
    #     'Avg. number of isotopes': (iso_mean_nat_1 + iso_mean_nat_2 +
    #                          iso_mean_nat_3),
    #     'Type_Dataset': (['nat_nist_AA3H0']*len(vp_values) + ['nat_nist_AA6H0']*len(vp_values) +
    #                     ['nat_nist_AA9H0']*len(vp_values))
    # })


    # # df_top4 and df_top5 follows
    # df_top_5 = pd.DataFrame({
    #     'vp setting (ppm)': vp_values * 3,
    #     'Avg. number of valid isotopes': (valid_iso_mean_nat_1 + valid_iso_mean_nat_2 +
    #                          valid_iso_mean_nat_3),
    #     'Type_Dataset': (['nat_nist_AA3H0']*len(vp_values) + ['nat_nist_AA6H0']*len(vp_values) +
    #                     ['nat_nist_AA9H0']*len(vp_values))
    # })

    # Data for bottom plot
    # df_bottom = pd.DataFrame({
    #     'vp setting (ppm)': vp_values * 4,
    #     'Avg. number of valid isotopes': (valid_iso_mean_nat_1 + valid_iso_mean_nat_2 +
    #                               valid_iso_mean_C13_1 + valid_iso_mean_C13_2),
    #     'Type_Dataset': (['testdata1_nat']*len(vp_values) + ['testdata2_nat']*len(vp_values) +
    #                     ['testdata1_C13']*len(vp_values) + ['testdata2_C13']*len(vp_values))
    # })

    # Create stacked bar chart combining df_top_1, df_top_2, and df_top_3
    # Prepare data for stacked bars
    stacked_data = []
    for i, p_val in enumerate(p_values):
        for j, dataset_name in enumerate(datasets):
            dataset_label = f'nat_nist_{dataset_name}'
            # Get values for this p_value and dataset
            total_cf = df_top_1[(df_top_1['p setting (ppm)'] == p_val) & 
                               (df_top_1['Type_Dataset'] == dataset_label)]['Number of CF'].iloc[0]
            iso_count_cf = df_top_2[(df_top_2['p setting (ppm)'] == p_val) & 
                                   (df_top_2['Type_Dataset'] == dataset_label)]['Number of CF with iso_count greater than 1'].iloc[0]
            valid_cf = df_top_3[(df_top_3['p setting (ppm)'] == p_val) & 
                                   (df_top_3['Type_Dataset'] == dataset_label)]['Number of valid CF'].iloc[0]
            
            # Store actual counts for each category (not differences)
            # Each category shows its actual count, all starting from y=0
            
            stacked_data.append({
                'p_setting': p_val,
                'dataset': dataset_label,       # Use the label, not the raw dataset name
                'Total CF': total_cf,           # Monoisotopic mass matches
                'Has isotopes': iso_count_cf,   # CF with isotope mass match count > 0
                'Valid': valid_cf,              # CF with iso_valid count > 0
                'total': total_cf
            })
    
    stacked_df = pd.DataFrame(stacked_data)
    
    # Create stacked bar plot
    # Generate dataset labels for plotting
    dataset_labels = [f'nat_nist_{dataset}' for dataset in datasets]
    # Generate colors dynamically based on number of datasets
    colors = ['#E69F00', '#56B4E9', '#009E73', '#F0E442', '#0072B2', '#D55E00', '#CC79A7'][:len(datasets)]
    
    # Set up the positions for grouped stacked bars
    x_pos = range(len(p_values))
    width = 0.25
    
    for i, dataset_label in enumerate(dataset_labels):
        dataset_data = stacked_df[stacked_df['dataset'] == dataset_label]
        
        # Calculate positions for this dataset group
        positions = [x + width * i for x in x_pos]
        
        # Create separate bars for each category, all starting from y=0
        # Adjust positions so bars don't overlap within each dataset group
        pos_offset = width / 3
        
        # Total CF bars (monoisotopic mass matches)
        pos_total = [p - pos_offset for p in positions]
        bar1 = ax1.bar(pos_total, dataset_data['Total CF'], 
                       width=pos_offset, label=f'{dataset_label} - Total CF' if i == 0 else "",
                       color=colors[i], alpha=0.4)
        
        # Has isotopes bars (CF with isotope mass match count > 0)
        pos_has_iso = positions
        bar2 = ax1.bar(pos_has_iso, dataset_data['Has isotopes'], 
                       width=pos_offset, label=f'{dataset_label} - Has isotopes' if i == 0 else "",
                       color=colors[i], alpha=0.7)
        
        # Valid bars (CF with iso_valid count > 0)
        pos_valid = [p + pos_offset for p in positions]
        bar3 = ax1.bar(pos_valid, dataset_data['Valid'], 
                       width=pos_offset, label=f'{dataset_label} - Valid' if i == 0 else "",
                       color=colors[i], alpha=1.0)
    
    # Customize the stacked plot
    ax1.set_xlabel('p setting (ppm)')
    ax1.set_ylabel('Number of CF')
    ax1.set_title('a - CF Analysis by Category', loc='left', fontweight='bold', fontsize=16)
    ax1.set_xticks([x + width for x in x_pos])
    ax1.set_xticklabels(p_values)
    
    # Create custom legend with better organization
    from matplotlib.patches import Patch
    
    # Create legend for datasets (colors)
    dataset_legend = []
    for i, dataset in enumerate(datasets):
        dataset_name = dataset  # Extract AA3H0, AA6H0, AA9H0
        dataset_legend.append(Patch(facecolor=colors[i], alpha=1.0, label=dataset_name))
    
    # Create legend for validation status (transparency levels)
    status_legend = [
        Patch(facecolor='gray', alpha=0.4, label='Matched monoisotopic mass'),
        Patch(facecolor='gray', alpha=0.7, label='Has isotopes at least one'), 
        Patch(facecolor='gray', alpha=1.0, label='Valid isotope at least one')
    ]
    
    # Create common legends positioned adjacent to each other between the figures
    legend1 = fig.legend(handles=dataset_legend, loc='center', frameon=True, framealpha=0.9, 
                        title='Datasets', title_fontsize=16, fontsize=14, bbox_to_anchor=(0.35, 0.5))
    
    legend2 = fig.legend(handles=status_legend, loc='center', frameon=True, framealpha=0.9,
                        title='CF Categories', title_fontsize=16, fontsize=14, bbox_to_anchor=(0.65, 0.5))
    
    # Add value labels to bars
    for i, dataset_label in enumerate(dataset_labels):
        dataset_data = stacked_df[stacked_df['dataset'] == dataset_label]
        positions = [x + width * i for x in x_pos]
        pos_offset = width / 3
        
        for j, pos in enumerate(positions):
            row = dataset_data.iloc[j]
            
            # Label for Total CF bar
            if row['Total CF'] > 0:
                ax1.text(pos - pos_offset, row['Total CF'] + 5, 
                        f"{int(row['Total CF'])}", ha='center', va='bottom', fontsize=12, fontweight='bold')
            
            # Label for Has isotopes bar
            if row['Has isotopes'] > 0:
                ax1.text(pos, row['Has isotopes'] + 5, 
                        f"{int(row['Has isotopes'])}", ha='center', va='bottom', fontsize=12, fontweight='bold')
            
            # Label for Valid bar
            if row['Valid'] > 0:
                ax1.text(pos + pos_offset, row['Valid'] + 5, 
                        f"{int(row['Valid'])}", ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    # Create similar grouped bar chart for vp variations (fixed p=0.5) on ax2
    # Prepare data for vp analysis
    stacked_data_vp = []
    for i, vp_val in enumerate(vp_values):
        for j, dataset_label in enumerate(dataset_labels):
            # Get values for this vp_value and dataset
            total_cf_vp = cf_counts_nat_vp_list[j][i]
            iso_count_cf_vp = cf_counts_iso_count_greater_than_zero_vp_list[j][i]
            valid_cf_vp = cf_counts_nat_valid_vp_list[j][i]
            
            stacked_data_vp.append({
                'vp_setting': vp_val,
                'dataset': dataset_label,
                'Total CF': total_cf_vp,           # Monoisotopic mass matches
                'Has isotopes': iso_count_cf_vp,   # CF with isotope mass match count > 0
                'Valid': valid_cf_vp,              # CF with iso_valid count > 0
                'total': total_cf_vp
            })
    
    stacked_df_vp = pd.DataFrame(stacked_data_vp)
    
    # Create grouped bars for vp analysis on ax2
    x_pos_vp = range(len(vp_values))
    width_vp = 0.25
    
    for i, dataset_label in enumerate(dataset_labels):
        dataset_data_vp = stacked_df_vp[stacked_df_vp['dataset'] == dataset_label]
        
        # Calculate positions for this dataset group
        positions_vp = [x + width_vp * i for x in x_pos_vp]
        
        # Create separate bars for each category, all starting from y=0
        pos_offset_vp = width_vp / 3
        
        # Total CF bars
        pos_total_vp = [p - pos_offset_vp for p in positions_vp]
        ax2.bar(pos_total_vp, dataset_data_vp['Total CF'], 
               width=pos_offset_vp, color=colors[i], alpha=0.4)
        
        # Has isotopes bars
        pos_has_iso_vp = positions_vp
        ax2.bar(pos_has_iso_vp, dataset_data_vp['Has isotopes'], 
               width=pos_offset_vp, color=colors[i], alpha=0.7)
        
        # Valid bars
        pos_valid_vp = [p + pos_offset_vp for p in positions_vp]
        ax2.bar(pos_valid_vp, dataset_data_vp['Valid'], 
               width=pos_offset_vp, color=colors[i], alpha=1.0)
    
    # Customize the vp plot
    ax2.set_xlabel('vp setting (ppm)')
    ax2.set_ylabel('Number of CF')
    ax2.set_title('b - CF Analysis by Category (vp variation)', loc='left', fontweight='bold', fontsize=16)
    ax2.set_xticks([x + width_vp for x in x_pos_vp])
    ax2.set_xticklabels(vp_values)
    
    # Add value labels to vp bars
    for i, dataset_label in enumerate(dataset_labels):
        dataset_data_vp = stacked_df_vp[stacked_df_vp['dataset'] == dataset_label]
        positions_vp = [x + width_vp * i for x in x_pos_vp]
        pos_offset_vp = width_vp / 3
        
        for j, pos in enumerate(positions_vp):
            row_vp = dataset_data_vp.iloc[j]
            
            # Label for Total CF bar
            if row_vp['Total CF'] > 0:
                ax2.text(pos - pos_offset_vp, row_vp['Total CF'] + 5, 
                        f"{int(row_vp['Total CF'])}", ha='center', va='bottom', fontsize=12, fontweight='bold')
            
            # Label for Has isotopes bar
            if row_vp['Has isotopes'] > 0:
                ax2.text(pos, row_vp['Has isotopes'] + 5, 
                        f"{int(row_vp['Has isotopes'])}", ha='center', va='bottom', fontsize=12, fontweight='bold')
            
            # Label for Valid bar
            if row_vp['Valid'] > 0:
                ax2.text(pos + pos_offset_vp, row_vp['Valid'] + 5, 
                        f"{int(row_vp['Valid'])}", ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    # # Keep the original plots for comparison in other axes
    # sns.barplot(data=df_top_3, x='p setting (ppm)', y='Number of CF',
    #             hue='Type_Dataset',
    #             palette=['#E69F00', '#56B4E9', '#009E73'],  # Colorblind-friendly palette
    #             ax=ax5,
    #             width=0.8,  # Reduce bar width
    #             dodge=True)  # Enable bar grouping
    # ax5.set_title('e', loc='left', fontweight='bold', fontsize=16)
    # ax5.legend(loc='upper left', frameon=True, framealpha=0.9)

    # sns.barplot(data=df_top_2, x='p setting (ppm)', y='Number of valid CF',
    #             hue='Type_Dataset',
    #             palette=['#E69F00', '#56B4E9', '#009E73'],  # Colorblind-friendly palette
    #             ax=ax2,
    #             width=0.8,  # Reduce bar width
    #             dodge=True)  # Enable bar grouping
    # ax2.set_title('b', loc='left', fontweight='bold', fontsize=16)
    # ax2.legend(loc='upper left', frameon=True, framealpha=0.9)

    # sns.barplot(data=df_top_4, x='vp setting (ppm)', y='Avg. number of isotopes',
    #             hue='Type_Dataset',
    #             palette=['#E69F00', '#56B4E9', '#009E73'],  # Colorblind-friendly palette
    #             ax=ax3,
    #             width=0.8,  # Reduce bar width
    #             dodge=True)  # Enable bar grouping
    # ax3.set_title('c', loc='left', fontweight='bold', fontsize=16)
    # ax3.legend(loc='upper left', frameon=True, framealpha=0.9)

    # sns.barplot(data=df_top_5, x='vp setting (ppm)', y='Avg. number of valid isotopes',
    #             hue='Type_Dataset',
    #             palette=['#E69F00', '#56B4E9', '#009E73'],  # Colorblind-friendly palette
    #             ax=ax4,
    #             width=0.8,  # Reduce bar width
    #             dodge=True)  # Enable bar grouping
    # ax4.set_title('d', loc='left', fontweight='bold', fontsize=16)
    # ax4.legend(loc='upper left', frameon=True, framealpha=0.9)



   
    # # Add value labels
    # for ax in [ax1, ax2, ax3, ax4, ax5]:
    #     for container in ax.containers:
    #         if ax == ax1:
    #             ax.bar_label(container, fmt='%d', fontsize=12)
    #         else:
    #             ax.bar_label(container, fmt='%.1f', fontsize=12)
    #     # Increase axis label font sizes
    #     ax.xaxis.label.set_fontsize(14)
    #     ax.yaxis.label.set_fontsize(14)
    #     # Make tick labels more visible
    #     ax.tick_params(axis='both', which='major', labelsize=12)
    
    # Adjust layout and save
    plt.tight_layout(pad=3.0)  # Normal layout since legends are on the sides
    # Save both formats before closing
    fig.savefig(os.path.join(outdir, 'analysis_results_iso_valid.png'), dpi=300, bbox_inches='tight')
    fig.savefig(os.path.join(outdir, 'analysis_results_iso_valid.pdf'), dpi=300, bbox_inches='tight')
    plt.close(fig)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Plot analysis results')
    parser.add_argument('outdir', help='Directory containing the analysis output files')
    args = parser.parse_args()
    
    create_plots(args.outdir, datasets=[ 'combined_N-metabolites_std', 'testdata1']) 
