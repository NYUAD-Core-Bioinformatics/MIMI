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

def process_results(outdir):
    """Process all result files and compile data for plotting"""
    df_cache = {}  # Cache DataFrames to avoid reading same file twice
    
    def get_df(filepath):
        if filepath not in df_cache:
            df_cache[filepath] = pd.read_csv(filepath, sep='\t', skiprows=2)
        return df_cache[filepath]
    
    # Data for top graph (varying p, fixed vp=0.5)
    p_values = [0.1, 0.5, 1.0]
    cf_counts_nat = {'AA3H0': [], 'AA6H0': [], 'AA9H0': []}
    cf_counts_nat_valid = {'AA3H0': [], 'AA6H0': [], 'AA9H0': []}
    
    
    # Data for bottom graph (varying vp, fixed p=0.5)
    vp_values = [0.1, 0.5, 1.0]
    iso_mean_nat = {'AA3H0': [], 'AA6H0': [], 'AA9H0': []}
    valid_iso_mean_nat = {'AA3H0': [], 'AA6H0': [], 'AA9H0': []}

    
    # Process files for both datasets
    for dataset in ['AA3H0', 'AA6H0', 'AA9H0']:
        # Process files for top graph
        for p in p_values:
            p_str = str(p).replace('.', '') if p < 1 else str(int(p))
            combined_file = os.path.join(outdir, f"n{dataset}_p{p_str}_vp05_combined.tsv")
            print(combined_file)
            df = get_df(combined_file)
            # print(df.columns)
            # print(df.head(2)['CF'])
            # sys.exit()
            cf_counts_nat[f'{dataset}'].append(count_number_of_nat(df))
            cf_counts_nat_valid[f'{dataset}'].append(count_number_of_nat_valid(df))

            
        # Process files for middle graph
        for vp in vp_values:
            vp_str = str(vp).replace('.', '') if vp < 1 else str(int(vp))
            combined_file = os.path.join(outdir, f"n{dataset}_p05_vp{vp_str}_combined.tsv")
            print(combined_file)
            df = get_df(combined_file)
            iso_mean_nat[f'{dataset}'].append(mean_isotopes_nat(df))
            valid_iso_mean_nat[f'{dataset}'].append(mean_isotopes_valid_nat(df))

            
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
    return (p_values, 
        cf_counts_nat['AA3H0'], cf_counts_nat['AA6H0'], cf_counts_nat['AA9H0'],
        cf_counts_nat_valid['AA3H0'], cf_counts_nat_valid['AA6H0'], cf_counts_nat_valid['AA9H0'],
        vp_values, 
        iso_mean_nat['AA3H0'], iso_mean_nat['AA6H0'], iso_mean_nat['AA9H0'],
        valid_iso_mean_nat['AA3H0'], valid_iso_mean_nat['AA6H0'], valid_iso_mean_nat['AA9H0'])

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
     cf_counts_nat_3,
     cf_counts_nat_valid_1, cf_counts_nat_valid_2, cf_counts_nat_valid_3,
     vp_values,
     iso_mean_nat_1, iso_mean_nat_2,
     iso_mean_nat_3,
     valid_iso_mean_nat_1, valid_iso_mean_nat_2, valid_iso_mean_nat_3) = process_results(outdir)
    
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
    
    # Create figure with three subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(24, 15))
    
    # Data for top plot
    df_top_1 = pd.DataFrame({
        'p setting (ppm)': p_values * 3,
        'Number of CF': (cf_counts_nat_1 + cf_counts_nat_2 + 
                        cf_counts_nat_3),
        'Type_Dataset': (['nat_nist_AA3H0']*len(p_values) + ['nat_nist_AA6H0']*len(p_values) +
                        ['nat_nist_AA9H0']*len(p_values))
    })

        # Data for top plot
    df_top_2 = pd.DataFrame({
        'p setting (ppm)': p_values * 3,
       
        'Number of valid CF': (cf_counts_nat_valid_1 + cf_counts_nat_valid_2 + 
                        cf_counts_nat_valid_3),
        'Type_Dataset': (['nat_nist_AA3H0']*len(p_values) + ['nat_nist_AA6H0']*len(p_values) +
                        ['nat_nist_AA9H0']*len(p_values))
    })
    
    # Data for middle plot
    df_middle_1 = pd.DataFrame({
        'vp setting (ppm)': vp_values * 3,
        'Avg. number of isotopes': (iso_mean_nat_1 + iso_mean_nat_2 +
                             iso_mean_nat_3),
        'Type_Dataset': (['nat_nist_AA3H0']*len(vp_values) + ['nat_nist_AA6H0']*len(vp_values) +
                        ['nat_nist_AA9H0']*len(vp_values))
    })


     # Data for middle plot
    df_middle_2 = pd.DataFrame({
        'vp setting (ppm)': vp_values * 3,
        'Avg. number of valid isotopes': (valid_iso_mean_nat_1 + valid_iso_mean_nat_2 +
                             valid_iso_mean_nat_3),
        'Type_Dataset': (['nat_nist_AA3H0']*len(vp_values) + ['nat_nist_AA6H0']*len(vp_values) +
                        ['nat_nist_AA9H0']*len(vp_values))
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
    sns.barplot(data=df_top_1, x='p setting (ppm)', y='Number of CF',
                hue='Type_Dataset', 
                palette=['#E69F00', '#56B4E9', '#009E73'],  # Colorblind-friendly palette
                ax=ax1,
                width=0.8,  # Reduce bar width
                dodge=True)  # Enable bar grouping
    ax1.set_title('a', loc='left', fontweight='bold', fontsize=16)
    ax1.legend(loc='upper left', frameon=True, framealpha=0.9)
    
    sns.barplot(data=df_top_2, x='p setting (ppm)', y='Number of valid CF',
                hue='Type_Dataset',
                palette=['#E69F00', '#56B4E9', '#009E73'],  # Colorblind-friendly palette
                ax=ax2,
                width=0.8,  # Reduce bar width
                dodge=True)  # Enable bar grouping
    ax2.set_title('b', loc='left', fontweight='bold', fontsize=16)
    ax2.legend(loc='upper left', frameon=True, framealpha=0.9)

    sns.barplot(data=df_middle_1, x='vp setting (ppm)', y='Avg. number of isotopes',
                hue='Type_Dataset',
                palette=['#E69F00', '#56B4E9', '#009E73'],  # Colorblind-friendly palette
                ax=ax3,
                width=0.8,  # Reduce bar width
                dodge=True)  # Enable bar grouping
    ax3.set_title('c', loc='left', fontweight='bold', fontsize=16)
    ax3.legend(loc='upper left', frameon=True, framealpha=0.9)

    sns.barplot(data=df_middle_2, x='vp setting (ppm)', y='Avg. number of valid isotopes',
                hue='Type_Dataset',
                palette=['#E69F00', '#56B4E9', '#009E73'],  # Colorblind-friendly palette
                ax=ax4,
                width=0.8,  # Reduce bar width
                dodge=True)  # Enable bar grouping
    ax4.set_title('d', loc='left', fontweight='bold', fontsize=16)
    ax4.legend(loc='upper left', frameon=True, framealpha=0.9)

   
    # Add value labels
    for ax in [ax1, ax2, ax3, ax4]:
        for container in ax.containers:
            if ax == ax1:
                ax.bar_label(container, fmt='%d', fontsize=12)
            else:
                ax.bar_label(container, fmt='%.1f', fontsize=12)
        # Increase axis label font sizes
        ax.xaxis.label.set_fontsize(14)
        ax.yaxis.label.set_fontsize(14)
        # Make tick labels more visible
        ax.tick_params(axis='both', which='major', labelsize=12)
    
    # Adjust layout and save
    plt.tight_layout(pad=3.0)  # Add more padding between subplots
    # Save both formats before closing
    fig.savefig(os.path.join(outdir, 'analysis_results_iso_valid.png'), dpi=300, bbox_inches='tight')
    fig.savefig(os.path.join(outdir, 'analysis_results_iso_valid.pdf'), dpi=300, bbox_inches='tight')
    plt.close(fig)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Plot analysis results')
    parser.add_argument('outdir', help='Directory containing the analysis output files')
    args = parser.parse_args()
    
    create_plots(args.outdir) 
