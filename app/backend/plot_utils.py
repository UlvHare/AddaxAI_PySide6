## backend/plot_utils.py
"""
This file will contain utilities for creating plots and visualizations
based on the detection and classification results. It focuses on implementing
core plotting functionality that's compatible with PySide6 and the Qt environment.
"""
import os
import json
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

# Configure matplotlib to use Qt6 backend
matplotlib.use('QtAgg')

# Set style
plt.style.use('ggplot')
colors = plt.rcParams['axes.prop_cycle'].by_key()['color']


class PlotCanvas(FigureCanvasQTAgg):
    """Canvas for rendering matplotlib plots in Qt6 applications."""

    def __init__(self, width=5, height=4, dpi=100):
        """Initialize the canvas.

        Args:
            width: Width of the figure in inches
            height: Height of the figure in inches
            dpi: Dots per inch for the figure
        """
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)

def produce_plots(results_folder, progress_callback=None):
    """Create standard plots based on CSV results.

    Args:
        results_folder: Path to the folder with results CSV files
        progress_callback: Function to call with progress updates

    Returns:
        bool: True if plots were created successfully
    """
    print(f"EXECUTED: produce_plots({results_folder})")

    # Check if data files exist
    detections_csv = os.path.join(results_folder, "results_detections.csv")
    files_csv = os.path.join(results_folder, "results_files.csv")

    if not (os.path.isfile(detections_csv) and os.path.isfile(files_csv)):
        print("Results CSV files not found")
        return False

    # Update progress
    if progress_callback:
        progress_callback(status="preparing")

    # Load data
    try:
        detections_df = pd.read_csv(detections_csv, low_memory=False)
        files_df = pd.read_csv(files_csv, low_memory=False)
    except Exception as e:
        print(f"Error loading CSV data: {str(e)}")
        return False

    # Create plots folder
    plots_folder = os.path.join(results_folder, "plots")
    Path(plots_folder).mkdir(exist_ok=True)

    # Generate standard plots
    plot_functions = [
        plot_detection_counts,
        plot_confidence_distribution,
        plot_confidence_by_class,
        plot_temporal_distribution,
        plot_spatial_distribution,
        plot_size_distribution
    ]

    total_plots = len(plot_functions)

    for i, plot_func in enumerate(plot_functions):
        try:
            # Update progress
            if progress_callback:
                progress_callback(
                    status="plotting",
                    plot_name=plot_func.__name__.replace("plot_", "").replace("_", " ").title(),
                    progress=int((i / total_plots) * 100)
                )

            # Generate plot
            plot_func(detections_df, files_df, plots_folder)
        except Exception as e:
            print(f"Error creating plot {plot_func.__name__}: {str(e)}")

    # Final progress update
    if progress_callback:
        progress_callback(status="complete")

    return True

def plot_detection_counts(detections_df, files_df, plots_folder):
    """Create plots showing detection counts by class.

    Args:
        detections_df: DataFrame of detections
        files_df: DataFrame of files
        plots_folder: Path to save plots
    """
    # Count detections by class
    class_counts = detections_df['label'].value_counts()

    # Plot as bar chart
    plt.figure(figsize=(10, 6))
    class_counts.plot(kind='bar', color=colors[0])
    plt.title('Detection Counts by Class')
    plt.xlabel('Class')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig(os.path.join(plots_folder, "detection_counts.png"), dpi=300)
    plt.close()

    # Plot as pie chart if there are 10 or fewer classes
    if len(class_counts) <= 10:
        plt.figure(figsize=(8, 8))
        class_counts.plot(kind='pie', autopct='%1.1f%%')
        plt.title('Detection Distribution by Class')
        plt.ylabel('')  # Hide ylabel
        plt.tight_layout()
        plt.savefig(os.path.join(plots_folder, "detection_distribution_pie.png"), dpi=300)
        plt.close()


def plot_confidence_distribution(detections_df, files_df, plots_folder):
    """Create plots showing confidence score distributions.

    Args:
        detections_df: DataFrame of detections
        files_df: DataFrame of files
        plots_folder: Path to save plots
    """
    # Filter out manually verified entries
    auto_detections = detections_df[detections_df['human_verified'] == False]

    if len(auto_detections) == 0:
        # No automatic detections to plot
        return

    # Plot histogram of confidence scores
    plt.figure(figsize=(10, 6))
    plt.hist(auto_detections['confidence'], bins=20, color=colors[1], alpha=0.7)
    plt.title('Distribution of Confidence Scores')
    plt.xlabel('Confidence Score')
    plt.ylabel('Count')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_folder, "confidence_distribution.png"), dpi=300)
    plt.close()

    # Create cumulative distribution
    plt.figure(figsize=(10, 6))
    plt.hist(auto_detections['confidence'], bins=20, cumulative=True, density=True,
             histtype='step', color=colors[2], linewidth=2)
    plt.title('Cumulative Distribution of Confidence Scores')
    plt.xlabel('Confidence Score')
    plt.ylabel('Cumulative Probability')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_folder, "confidence_cumulative.png"), dpi=300)
    plt.close()

def plot_confidence_by_class(detections_df, files_df, plots_folder):
    """Create plots showing confidence distributions by class.

    Args:
        detections_df: DataFrame of detections
        files_df: DataFrame of files
        plots_folder: Path to save plots
    """
    # Filter out manually verified entries
    auto_detections = detections_df[detections_df['human_verified'] == False]

    if len(auto_detections) == 0:
        # No automatic detections to plot
        return

    # Get top classes (up to 10)
    top_classes = auto_detections['label'].value_counts().index[:10]

    # Create box plot of confidence by class
    plt.figure(figsize=(12, 7))
    box_data = [auto_detections[auto_detections['label'] == cls]['confidence'] for cls in top_classes]
    plt.boxplot(box_data, labels=top_classes, vert=True, patch_artist=True)
    plt.title('Confidence Score Distribution by Class')
    plt.xlabel('Class')
    plt.ylabel('Confidence Score')
    plt.xticks(rotation=45, ha="right")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_folder, "confidence_by_class_box.png"), dpi=300)
    plt.close()

    # Create violin plot for more detailed distribution visualization
    plt.figure(figsize=(12, 7))
    plt.violinplot(box_data, showmeans=True, showextrema=True)
    plt.title('Confidence Score Distribution by Class (Violin Plot)')
    plt.xlabel('Class')
    plt.ylabel('Confidence Score')
    plt.xticks(range(1, len(top_classes) + 1), top_classes, rotation=45, ha="right")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_folder, "confidence_by_class_violin.png"), dpi=300)
    plt.close()


def plot_temporal_distribution(detections_df, files_df, plots_folder):
    """Create plots showing detection distribution over time.

    Args:
        detections_df: DataFrame of detections
        files_df: DataFrame of files
        plots_folder: Path to save plots
    """
    # Check if datetime columns are available
    datetime_cols = ['DateTimeOriginal', 'DateTime', 'DateTimeDigitized']
    available_cols = [col for col in datetime_cols if col in files_df.columns]

    if not available_cols:
        # No datetime information available
        return

    # Use the first available datetime column
    datetime_col = available_cols[0]

    # Convert to datetime format if it's not already
    try:
        # Try parsing with default format
        files_df['capture_time'] = pd.to_datetime(files_df[datetime_col], errors='coerce')

        # If too many NaT values, try alternative format
        if files_df['capture_time'].isna().sum() > len(files_df) * 0.7:
            files_df['capture_time'] = pd.to_datetime(files_df[datetime_col],
                                                     format='%d/%m/%y %H:%M:%S',
                                                     errors='coerce')
    except Exception:
        # If datetime conversion fails, skip temporal plots
        return

    # Remove rows with missing datetime
    files_with_time = files_df.dropna(subset=['capture_time'])

    if len(files_with_time) < 10:
        # Not enough temporal data to create meaningful plots
        return

    # Create hourly distribution chart
    plt.figure(figsize=(12, 6))
    files_with_time['hour'] = files_with_time['capture_time'].dt.hour
    hourly_counts = files_with_time['hour'].value_counts().sort_index()
    hourly_counts.plot(kind='bar', color=colors[3])
    plt.title('Hourly Distribution of Detections')
    plt.xlabel('Hour of Day')
    plt.ylabel('Number of Detections')
    plt.xticks(range(0, 24), range(0, 24))
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_folder, "hourly_distribution.png"), dpi=300)
    plt.close()

    # Create daily distribution chart
    plt.figure(figsize=(12, 6))
    files_with_time['day'] = files_with_time['capture_time'].dt.day_name()
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_counts = files_with_time['day'].value_counts().reindex(day_order)
    daily_counts.plot(kind='bar', color=colors[4])
    plt.title('Daily Distribution of Detections')
    plt.xlabel('Day of Week')
    plt.ylabel('Number of Detections')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_folder, "daily_distribution.png"), dpi=300)
    plt.close()

def plot_spatial_distribution(detections_df, files_df, plots_folder):
    """Create plots showing spatial distribution of detections.

    Args:
        detections_df: DataFrame of detections
        files_df: DataFrame of files
        plots_folder: Path to save plots
    """
    # Check if GPS coordinates are available
    if 'Latitude' not in files_df.columns or 'Longitude' not in files_df.columns:
        return

    # Convert to numeric and filter out missing values
    files_df['Latitude'] = pd.to_numeric(files_df['Latitude'], errors='coerce')
    files_df['Longitude'] = pd.to_numeric(files_df['Longitude'], errors='coerce')
    files_with_gps = files_df.dropna(subset=['Latitude', 'Longitude'])

    if len(files_with_gps) < 5:
        # Not enough GPS data to create meaningful plots
        return

    try:
        # Attempt to import optional mapping libraries
        import matplotlib.pyplot as plt
        from mpl_toolkits.basemap import Basemap
        has_basemap = True
    except ImportError:
        has_basemap = False

    # If Basemap is available, create map-based plot
    if has_basemap:
        plt.figure(figsize=(12, 10))
        # Calculate map boundaries with some padding
        lat_min, lat_max = files_with_gps['Latitude'].min() - 0.5, files_with_gps['Latitude'].max() + 0.5
        lon_min, lon_max = files_with_gps['Longitude'].min() - 0.5, files_with_gps['Longitude'].max() + 0.5

        # Create basemap
        m = Basemap(projection='merc', resolution='i',
                   llcrnrlat=lat_min, urcrnrlat=lat_max,
                   llcrnrlon=lon_min, urcrnrlon=lon_max)

        # Add map features
        m.drawcoastlines()
        m.drawcountries()
        m.drawmapboundary(fill_color='aqua')
        m.fillcontinents(color='coral', lake_color='aqua')

        # Plot points
        x, y = m(files_with_gps['Longitude'].tolist(), files_with_gps['Latitude'].tolist())
        m.scatter(x, y, marker='o', color='blue', s=30, alpha=0.7)

        plt.title('Spatial Distribution of Detections')
        plt.savefig(os.path.join(plots_folder, "spatial_distribution_map.png"), dpi=300)
        plt.close()

    # Create simple scatter plot (works without Basemap)
    plt.figure(figsize=(12, 10))
    plt.scatter(files_with_gps['Longitude'], files_with_gps['Latitude'],
               s=30, alpha=0.7, c=files_with_gps['n_detections'], cmap='viridis')
    plt.colorbar(label='Number of Detections')
    plt.title('Spatial Distribution of Detections')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_folder, "spatial_distribution.png"), dpi=300)
    plt.close()


def plot_size_distribution(detections_df, files_df, plots_folder):
    """Create plots showing size distribution of detections.

    Args:
        detections_df: DataFrame of detections
        files_df: DataFrame of files
        plots_folder: Path to save plots
    """
    # Calculate bounding box sizes
    try:
        detections_df['bbox_width'] = pd.to_numeric(detections_df['bbox_right'], errors='coerce') - \
                                      pd.to_numeric(detections_df['bbox_left'], errors='coerce')
        detections_df['bbox_height'] = pd.to_numeric(detections_df['bbox_bottom'], errors='coerce') - \
                                       pd.to_numeric(detections_df['bbox_top'], errors='coerce')
        detections_df['bbox_area'] = detections_df['bbox_width'] * detections_df['bbox_height']

        # Remove invalid entries
        valid_detections = detections_df.dropna(subset=['bbox_area'])

        if len(valid_detections) == 0:
            return

        # Normalize by image size
        valid_detections['normalized_area'] = valid_detections['bbox_area'] / \
                                              (pd.to_numeric(valid_detections['file_width'], errors='coerce') * \
                                               pd.to_numeric(valid_detections['file_height'], errors='coerce'))

        # Plot size distribution
        plt.figure(figsize=(10, 6))
        plt.hist(valid_detections['normalized_area'], bins=30, color=colors[5], alpha=0.7)
        plt.title('Distribution of Normalized Detection Sizes')
        plt.xlabel('Normalized Bounding Box Area (relative to image size)')
        plt.ylabel('Count')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(plots_folder, "size_distribution.png"), dpi=300)
        plt.close()

        # Plot size distribution by class
        top_classes = valid_detections['label'].value_counts().index[:5]
        plt.figure(figsize=(12, 7))

        for i, cls in enumerate(top_classes):
            cls_data = valid_detections[valid_detections['label'] == cls]['normalized_area']
            plt.hist(cls_data, bins=20, alpha=0.5, label=cls, color=colors[i % len(colors)])

        plt.title('Size Distribution by Class')
        plt.xlabel('Normalized Bounding Box Area (relative to image size)')
        plt.ylabel('Count')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(plots_folder, "size_distribution_by_class.png"), dpi=300)
        plt.close()

    except Exception as e:
        print(f"Error creating size distribution plots: {str(e)}")

def create_custom_plot(data, plot_type, title, xlabel, ylabel, output_path, **kwargs):
    """Create a custom plot with the specified parameters.

    Args:
        data: Data to plot (DataFrame or Series)
        plot_type: Type of plot to create ('bar', 'line', 'scatter', etc.)
        title: Plot title
        xlabel: X-axis label
        ylabel: Y-axis label
        output_path: Path to save the plot
        **kwargs: Additional keyword arguments for plotting function

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        plt.figure(figsize=(10, 6))

        # Call the appropriate plot function based on plot_type
        if hasattr(data, plot_type) and callable(getattr(data, plot_type)):
            getattr(data, plot_type)(**kwargs)
        elif plot_type == 'histogram':
            plt.hist(data, **kwargs)
        elif plot_type == 'scatter':
            plt.scatter(data.iloc[:, 0], data.iloc[:, 1], **kwargs)
        else:
            print(f"Unsupported plot type: {plot_type}")
            return False

        # Set labels and title
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        # Save the plot
        plt.savefig(output_path, dpi=300)
        plt.close()

        return True

    except Exception as e:
        print(f"Error creating custom plot: {str(e)}")
        return False


def get_plot_preview(plot_func, data, size=(400, 300)):
    """Create a plot for preview in the GUI.

    Args:
        plot_func: Function to create the plot
        data: Data to plot
        size: Size tuple for the plot (width, height)

    Returns:
        PlotCanvas: Canvas with the rendered plot
    """
    try:
        # Create a canvas with the specified size
        width, height = size
        dpi = 100
        canvas = PlotCanvas(width=width/dpi, height=height/dpi, dpi=dpi)

        # Apply the plot function to the canvas
        plot_func(data, ax=canvas.axes)

        # Adjust layout
        canvas.fig.tight_layout()
        canvas.draw()

        return canvas

    except Exception as e:
        print(f"Error creating plot preview: {str(e)}")
        return None
