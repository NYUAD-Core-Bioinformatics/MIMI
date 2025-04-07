import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import glob
import os
import sys
def count_number_of_nat(df):
    """Count number of features for natural abundance data"""
    print('count_number_of_nat')
    print(df[df['db_mass_nat'].notna()]['db_mass_nat'].describe())
    return df[df['db_mass_nat'].notna()].shape[0]

def count_number_of_C13(df):
    """Count number of features for C13 data"""
    print('count_number_of_C13')
    print(df[df['db_mass_C13'].notna()]['db_mass_C13'].describe())
    return df[df['db_mass_C13'].notna()].shape[0]

# def mean_valid_isotopes_nat(df):
#     """Count total number of valid isotopes for natural abundance data"""
#     print('mean_valid_isotopes_nat')
#     print(df[df['db_mass_nat'].notna()]['iso_valid'].describe())
#     print(df[df['db_mass_nat'].notna()]['iso_valid'].mean())
#     return df[df['db_mass_nat'].notna()]['iso_valid'].mean()

# def mean_valid_isotopes_C13(df):
#     """Count total number of valid isotopes for C13 data"""
#     print('mean_valid_isotopes_C13')
#     print(df[df['db_mass_C13'].notna()]['iso_valid.1'].describe())
#     print(df[df['db_mass_C13'].notna()]['iso_valid.1'].mean())
#     return df[df['db_mass_C13'].notna()]['iso_valid.1'].mean()


def mean_isotopes_nat(df):
    """Count total number of valid isotopes for natural abundance data"""
    print('mean_isotopes_nat')
    print(df[df['db_mass_nat'].notna()]['iso_count'].describe())
    print(df[df['db_mass_nat'].notna()]['iso_count'].mean())
    return df[df['db_mass_nat'].notna()]['iso_count'].mean()

def mean_isotopes_C13(df):
    """Count total number of valid isotopes for C13 data"""
    print('mean_isotopes_C13')
    print(df[df['db_mass_C13'].notna()]['iso_count.1'].describe())
    print(df[df['db_mass_C13'].notna()]['iso_count.1'].mean())
    return df[df['db_mass_C13'].notna()]['iso_count.1'].mean()

def process_results(outdir):
    """Process all result files and compile data for plotting"""
    df_cache = {}  # Cache DataFrames to avoid reading same file twice
    
    def get_df(filepath):
        if filepath not in df_cache:
            df_cache[filepath] = pd.read_csv(filepath, sep='\t', skiprows=3)
        return df_cache[filepath]
    
    # Data for top graph (varying p, fixed vp=0.5)
    p_values = [0.1, 0.5, 1.0]
    cf_counts_nat = {'testdata1': [], 'testdata2': []}
    cf_counts_C13 = {'testdata1': [], 'testdata2': []}
    
    # Data for bottom graph (varying vp, fixed p=0.5)
    vp_values = [0.1, 0.5, 1.0]
    iso_mean_nat = {'testdata1': [], 'testdata2': []}
    iso_mean_C13 = {'testdata1': [], 'testdata2': []}
    valid_iso_mean_nat = {'testdata1': [], 'testdata2': []}
    valid_iso_mean_C13 = {'testdata1': [], 'testdata2': []}
    
    # Process files for both datasets
    for dataset in [1, 2]:
        # Process files for top graph
        for p in p_values:
            p_str = str(p).replace('.', '') if p < 1 else str(int(p))
            combined_file = os.path.join(outdir, f"ntestdata{dataset}_p{p_str}_vp05_combined.tsv")
            print(combined_file)
            df = get_df(combined_file)
            # print(df.columns)
            # print(df.head(2)['CF'])
            # sys.exit()
            cf_counts_nat[f'testdata{dataset}'].append(count_number_of_nat(df))
            cf_counts_C13[f'testdata{dataset}'].append(count_number_of_C13(df))
            
        # Process files for middle graph
        for vp in vp_values:
            vp_str = str(vp).replace('.', '') if vp < 1 else str(int(vp))
            combined_file = os.path.join(outdir, f"ntestdata{dataset}_p05_vp{vp_str}_combined.tsv")
            print(combined_file)
            df = get_df(combined_file)
            iso_mean_nat[f'testdata{dataset}'].append(mean_isotopes_nat(df))
            iso_mean_C13[f'testdata{dataset}'].append(mean_isotopes_C13(df))

            
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

    return (p_values, 
        cf_counts_nat['testdata1'], cf_counts_nat['testdata2'],
        cf_counts_C13['testdata1'], cf_counts_C13['testdata2'],
        vp_values, 
        iso_mean_nat['testdata1'], iso_mean_nat['testdata2'],
        iso_mean_C13['testdata1'], iso_mean_C13['testdata2'])

def create_plots(outdir):
    """Create the plots using seaborn"""
    # Get data
    # (p_values, 
    #  cf_counts_nat_1, cf_counts_nat_2,
    #  cf_counts_C13_1, cf_counts_C13_2,
    #  vp_values,
    #  iso_mean_nat_1, iso_mean_nat_2,
    #  iso_mean_C13_1, iso_mean_C13_2,
    #  valid_iso_mean_nat_1, valid_iso_mean_nat_2,
    #  valid_iso_mean_C13_1, valid_iso_mean_C13_2) = process_results(outdir)

    (p_values, 
     cf_counts_nat_1, cf_counts_nat_2,
     cf_counts_C13_1, cf_counts_C13_2,
     vp_values,
     iso_mean_nat_1, iso_mean_nat_2,
     iso_mean_C13_1, iso_mean_C13_2) = process_results(outdir)
    
    # Set BMC publication style
    plt.rcParams.update({
        'font.size': 14,
        'axes.titlesize': 16,
        'axes.labelsize': 14,
        'xtick.labelsize': 12,
        'ytick.labelsize': 12,
        'legend.fontsize': 12,
        'figure.titlesize': 18,
        'pdf.fonttype': 42,
        'ps.fonttype': 42,
        'svg.fonttype': 'none'
    })
    
    # Create figure with three subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 15))
    
    # Data for top plot
    df_top = pd.DataFrame({
        'p setting (ppm)': p_values * 4,
        'Number of CF': (cf_counts_nat_1 + cf_counts_nat_2 + 
                        cf_counts_C13_1 + cf_counts_C13_2),
        'Type_Dataset': (['nat_testdata1']*len(p_values) + ['nat_testdata2']*len(p_values) +
                        ['C13_testdata1']*len(p_values) + ['C13_testdata2']*len(p_values))
    })
    
    # Data for middle plot
    df_middle = pd.DataFrame({
        'vp setting (ppm)': vp_values * 4,
        'Avg. number of isotopes': (iso_mean_nat_1 + iso_mean_nat_2 +
                             iso_mean_C13_1 + iso_mean_C13_2),
        'Type_Dataset': (['testdata1_nat']*len(vp_values) + ['testdata2_nat']*len(vp_values) +
                        ['testdata1_C13']*len(vp_values) + ['testdata2_C13']*len(vp_values))
    })

    # Data for bottom plot
    # df_bottom = pd.DataFrame({
    #     'vp setting (ppm)': vp_values * 4,
    #     'Avg. number of valid isotopes': (valid_iso_mean_nat_1 + valid_iso_mean_nat_2 +
    #                               valid_iso_mean_C13_1 + valid_iso_mean_C13_2),
    #     'Type_Dataset': (['testdata1_nat']*len(vp_values) + ['testdata2_nat']*len(vp_values) +
    #                     ['testdata1_C13']*len(vp_values) + ['testdata2_C13']*len(vp_values))
    # })

    # Create plots with grouped bars
    sns.barplot(data=df_top, x='p setting (ppm)', y='Number of CF',
                hue='Type_Dataset', 
                palette=['skyblue', 'lightblue', 'coral', 'lightcoral'],
                ax=ax1,
                width=0.8,  # Reduce bar width
                dodge=True)  # Enable bar grouping
    ax1.set_title('a', loc='left', fontweight='bold', fontsize=16)
    ax1.legend(loc='upper left', frameon=True, framealpha=0.9)
    
    sns.barplot(data=df_middle, x='vp setting (ppm)', y='Avg. number of isotopes',
                hue='Type_Dataset',
                palette=['skyblue', 'lightblue', 'coral', 'lightcoral'],
                ax=ax2,
                width=0.8,  # Reduce bar width
                dodge=True)  # Enable bar grouping
    ax2.set_title('b', loc='left', fontweight='bold', fontsize=16)
    ax2.legend(loc='upper left', frameon=True, framealpha=0.9)

    # Add value labels
    for ax in [ax1, ax2]:
        for container in ax.containers:
            ax.bar_label(container, fmt='%.1f', fontsize=10)
        # Increase axis label font sizes
        ax.xaxis.label.set_fontsize(14)
        ax.yaxis.label.set_fontsize(14)
        # Make tick labels more visible
        ax.tick_params(axis='both', which='major', labelsize=12)
    
    # Adjust layout and save
    plt.tight_layout(pad=3.0)  # Add more padding between subplots
    # Save both formats before closing
    fig.savefig(os.path.join(outdir, 'analysis_results.png'), dpi=300, bbox_inches='tight')
    fig.savefig(os.path.join(outdir, 'analysis_results.pdf'), dpi=300, bbox_inches='tight')
    plt.close(fig)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Plot analysis results')
    parser.add_argument('outdir', help='Directory containing the analysis output files')
    args = parser.parse_args()
    
    create_plots(args.outdir) 
