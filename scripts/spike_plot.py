import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as patches
from matplotlib.gridspec import GridSpec

# Data for N-Sulfo-D-glucosamine isotopic masses and intensities
data = {
    "masses": [259.032266, 260.024707, 260.033156, 259.028299, 262.025097],
    "intensities": [40719460, 25647532, 12089784, 6984797, 33301546],
    "mono_isotopic_intensity": 861392640,  # Reference mono-isotopic intensity
    "formulas": [
        "[12]C5 [13]C1 [1]H13 [14]N1 [16]O8 [32]S1",
        "[12]C6 [1]H13 [14]N1 [16]O8 [34]S1", 
        "[12]C6 [1]H13 [14]N1 [16]O7 [18]O1 [32]S1",
        "[12]C6 [1]H13 [14]N1 [16]O8 [33]S1",
        "[12]C5 [13]C1 [1]H13 [15]N1 [16]O8 [34]S1"
    ],
    "valid": ["Valid", "Invalid", "Valid", "Valid", "Invalid"]
}

# Add mono-isotopic peak (assumed at base molecular formula mass)
mono_mass = 258.0289111  # Approximate mono-isotopic mass for C6H13NO8S
all_masses = [mono_mass] + data["masses"]
all_intensities = [data["mono_isotopic_intensity"]] + data["intensities"]
all_labels = ["Mono-isotopic\nC6H13NO8S"] + data["formulas"]
all_valid = ["Reference"] + data["valid"]

# Use actual m/z values as x-axis positions (continuous scale)
x_positions = all_masses  # Use actual mass values for positioning

# Define x-axis regions for splitting
def create_x_regions(masses, gap_threshold=0.1):
    """Create regions based on mass gaps"""
    sorted_masses = sorted(masses)
    regions = []
    current_region = [sorted_masses[0]]
    
    for i in range(1, len(sorted_masses)):
        gap = sorted_masses[i] - sorted_masses[i-1]
        if gap > gap_threshold:
            regions.append(current_region)
            current_region = [sorted_masses[i]]
        else:
            current_region.append(sorted_masses[i])
    
    regions.append(current_region)
    return regions

x_regions = create_x_regions(all_masses)
num_regions = len(x_regions)

# Create figure with split x-axis (regions as columns) and split y-axis (rows)
fig = plt.figure(figsize=(4 * num_regions, 10))
gs = GridSpec(2, num_regions, figure=fig, hspace=0.05, wspace=0.3)

# Create subplots: top row for mono-isotopic, bottom row for isotopic
ax_top = []    # Top row subplots (mono-isotopic range)
ax_bottom = [] # Bottom row subplots (isotopic range)

for i in range(num_regions):
    ax_top.append(fig.add_subplot(gs[0, i]))
    ax_bottom.append(fig.add_subplot(gs[1, i]))

# Define colors based on peak type (MS-style coloring)
colors = []
peak_types = []
for valid in all_valid:
    if valid == "Reference":
        colors.append('#2E4BC6')  # Deep blue for mono-isotopic
        peak_types.append('Mono-isotopic')
    elif valid == "Valid":
        colors.append('#228B22')  # Forest green for verified isotopes
        peak_types.append('Verified Isotope')
    else:
        colors.append('#DC143C')  # Crimson red for unverified
        peak_types.append('Unverified Isotope')

# Set y-axis limits for all subplots
for ax in ax_top:
    ax.set_ylim(800000000, 900000000)  # Top range for mono-isotopic
for ax in ax_bottom:
    ax.set_ylim(0, 50000000)  # Bottom range for isotopic peaks

# Create simple vertical bar peaks
def plot_ms_peak(ax, x_pos, intensity, color):
    """Plot a mass spectrometry peak as a simple vertical line"""
    ax.plot([x_pos, x_pos], [0, intensity], color=color, linewidth=3, alpha=0.9)

# Plot peaks in appropriate regions
for region_idx, region_masses in enumerate(x_regions):
    ax_t = ax_top[region_idx]
    ax_b = ax_bottom[region_idx]
    
    # Set x-axis limits for this region
    region_min = min(region_masses)
    region_max = max(region_masses)
    padding = max(0.01, (region_max - region_min) * 0.1) if len(region_masses) > 1 else 0.05
    
    ax_t.set_xlim(region_min - padding, region_max + padding)
    ax_b.set_xlim(region_min - padding, region_max + padding)
    
    # Plot peaks that belong to this region
    for mass in region_masses:
        mass_idx = all_masses.index(mass)
        intensity = all_intensities[mass_idx]
        color = colors[mass_idx]
        
        if mass_idx == 0:  # Mono-isotopic peak
            plot_ms_peak(ax_t, mass, intensity, color)
            plot_ms_peak(ax_b, mass, 50000000, color)  # Truncated in bottom
        else:  # Isotopic peaks
            plot_ms_peak(ax_b, mass, intensity, color)

# Break line functions removed - cleaner appearance without internal break lines

# Apply formatting to all subplots (remove internal break lines)
for i, (ax_t, ax_b) in enumerate(zip(ax_top, ax_bottom)):
    # Remove appropriate spines to show breaks only at edges
    ax_t.spines['bottom'].set_visible(False)
    ax_b.spines['top'].set_visible(False)
    
    if i > 0:  # Not leftmost
        ax_t.spines['left'].set_visible(False)
        ax_b.spines['left'].set_visible(False)
        ax_t.tick_params(left=False, labelleft=False)
        ax_b.tick_params(left=False, labelleft=False)
    
    if i < num_regions - 1:  # Not rightmost
        ax_t.spines['right'].set_visible(False)
        ax_b.spines['right'].set_visible(False)
    
    # Tick configuration
    ax_t.xaxis.tick_top()
    ax_t.tick_params(labeltop=False)
    ax_b.xaxis.tick_bottom()

# Center the axis labels using figure-level positioning
fig.text(0.02, 0.5, 'Intensity', fontsize=12, fontweight='bold', 
         rotation=0, ha='center', va='center')
fig.text(0.5, 0.02, 'm/z', fontsize=12, fontweight='bold', 
         ha='center', va='center')

# Add chemical formula labels above peaks
for region_idx, region_masses in enumerate(x_regions):
    ax_t = ax_top[region_idx]
    ax_b = ax_bottom[region_idx]
    
    for mass in region_masses:
        mass_idx = all_masses.index(mass)
        intensity = all_intensities[mass_idx]
        formula = all_labels[mass_idx] if mass_idx == 0 else data["formulas"][mass_idx - 1]
        
        if mass_idx == 0:  # Mono-isotopic peak
            # Chemical formula above peak
            ax_t.text(mass, intensity + 5000000, formula, 
                     ha='center', va='bottom', fontsize=12, fontweight='normal')
        else:  # Isotopic peaks
            # Chemical formula above peak
            ax_b.text(mass, intensity + 2000000, formula, 
                     ha='center', va='bottom', fontsize=12, fontweight='normal')

# Configure ticks for each region
for region_idx, region_masses in enumerate(x_regions):
    ax_b = ax_bottom[region_idx]
    
    # Set ticks at peak positions
    ax_b.set_xticks(region_masses)
    ax_b.set_xticklabels([f"{mass:.3f}" for mass in region_masses], 
                        rotation=45, ha='right', fontsize=11)

# Add title and subtitle
fig.suptitle('Mass Spectrum: N-Sulfo-D-glucosamine Isotopic Pattern Analysis', 
             fontsize=16, fontweight='bold', y=0.95)
fig.text(0.5, 0.91, 'Split X-Y Axis Mass Spectrum showing Isotopic Peak Verification', 
         ha='center', fontsize=12, style='italic')

# Add legend with updated terminology (on the rightmost top subplot)
legend_elements = [
    plt.Line2D([0], [0], color='#2E4BC6', linewidth=3, alpha=0.8, label='Mono-isotopic peak'),
    plt.Line2D([0], [0], color='#228B22', linewidth=3, alpha=0.8, label='Minor isotopic variant, ratio verified'),
    plt.Line2D([0], [0], color='#DC143C', linewidth=3, alpha=0.8, label='Minor isotopic variant')
]
ax_top[-1].legend(handles=legend_elements, loc='upper right', fontsize=12)

# Format y-axis to show values in scientific notation and increase tick font size
for ax in ax_top + ax_bottom:
    ax.ticklabel_format(style='scientific', axis='y', scilimits=(0,0))
    ax.tick_params(axis='y', labelsize=11, rotation=0)
    ax.tick_params(axis='x', labelsize=11)

# Adjust layout manually (tight_layout doesn't work well with custom gridspec)
plt.subplots_adjust(left=0.08, right=0.95, top=0.88, bottom=0.12, hspace=0.05, wspace=0.3)

# Save the plot in both PNG and PDF formats with high resolution
plt.savefig("ms_spectrum_plot.png", dpi=300, bbox_inches="tight", pad_inches=0.1)
plt.savefig("ms_spectrum_plot.pdf", dpi=800, bbox_inches="tight", pad_inches=0.1)
plt.close()
print("Mass spectrum plot saved as 'ms_spectrum_plot.png' and 'ms_spectrum_plot.pdf'")
