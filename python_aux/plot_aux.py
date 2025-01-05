import pandas as pd
import matplotlib.pyplot as plt
import mplcursors
from matplotlib.ticker import MaxNLocator
import matplotlib.dates as mdates
from  parse_aux import *
import numpy as np
import numpy as np
import matplotlib.pyplot as plt
import time_aux as timea
from itertools import cycle
from df_aux import *    
import seaborn as sns
import df_aux as dfa
import random
import plotly.express as px
import plotly.graph_objects as go
import tempfile
import webbrowser
import os
import subprocess
import tempfile





def get_plot_defualt_params():
    default_params = {
        'y_data': {'default': np.array([])},
        'x_data': {'default': None},
        'marker_points': {'default': None},
        'marker_points_style': {'default': 'o', 'optional': {'o', 'x', 's', 'd', 'ro'}},
        'marker_points_color':{'default': 'red', 'optional': {'blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black'}},    
        'marker_style': {'default': None, 'optional': {None, 'o', 'x', 's', 'd'}},        
        'line_style': {'default': '-', 'optional': {'-', '--', '-.', ':'}},
        'x_label': {'default': 'Index'},
        'y_label': {'default': 'Value'},
        'xlim': {'default': None},
        'ylim': {'default': None},
        'title': {'default': 'Plot of NumPy Array'},
        'legend': {'default': True, 'optional': {True, False}},
        'figsize': {'default': None},
        'color': {'default': 'blue', 'optional': {'blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black'}},
        'ax': {'default': None},
        'xlabel_fontsize': {'default': 10},
        'ylabel_fontsize': {'default': 10},
        'title_fontsize': {'default': 12},
        'tick_labelsize': {'default': 10}, 
        'legend_fontsize': {'default': 10},  
        'legend_loc': {'default': 'upper right', 'optional': {'best', 'upper right', 'upper left', 'lower left', 'lower right', 'right', 'center left', 'center right', 'lower center', 'upper center', 'center'}},
        'label': {'default': 'Data'},
        'str':''
    }        
    return default_params      




import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot(*args, **params):
    """
    Plot data using Plotly with options for subplots, line styles, and marker points.

    Parameters:
    -----------
    *args : list
        Positional arguments for x and y data. If two arguments are passed, they are considered as x_data and y_data.
        If one argument is passed, it is considered y_data.
    **params : dict
        Additional keyword arguments for plot customization.
        - fig : plotly.graph_objects.Figure, optional
            Existing figure to add subplots to. If None, a new figure will be created.
        - axes : list of tuples, optional
            Existing axes for subplots. If None, axes will be created based on num_axes and max_axes_in_row.
        - num_axes : int, default=1
            Total number of subplots.
        - max_axes_in_row : int, default=4
            Maximum number of axes in one row.
        - line_color : str or list, default='blue'
            Line color or list of colors for multiple lines.
        - line_name : str or list, optional
            Names for the legend of each line.
        - show_markers : bool, default=True
            Whether to show markers on the line.
        - line_width : int or list, default=2
            Line width or list of widths for multiple lines.
        - line_dash : str or list, default='solid'
            Line dash style or list of dash styles for multiple lines.
        - marker_points_dic : dict or list of dict, optional
            Dictionary defining marker points. Each dictionary should contain:
                - 'loc' : list of locations on x_data
                - 'color' : color of markers
                - 'symbol' : marker symbol
        - axes_title : str or list, optional
            Title for the subplot(s).
        - xlim : tuple, optional
            x-axis limits.
        - ylim : tuple, optional
            y-axis limits.
        - xlabel : str, optional
            Label for the x-axis.
        - ylabel : str, optional
            Label for the y-axis.
        - sync_xaxes : bool, default=True
            Whether to synchronize x-axes for all subplots.
        - sync_yaxes : bool, default=False
            Whether to synchronize y-axes for all subplots.
        - tick_labelsize : int, default=10
            Font size for the tick labels.
        - title_font_size : int, default=18
            Font size for the plot title.
    """    
    # Extract other parameters
    subplot_index = params.get('subplot_index', 0)
    fig = params.get('fig', None)
    axes = params.get('axes', None)
    num_axes = params.get('num_axes', 1)
    max_axes_in_row = params.get('max_axes_in_row', 4)
    line_color = params.get('line_color', 'blue')
    show_markers = params.get('show_markers', True)
    line_name = params.get('line_name', None)
    marker_points_dic = params.get('marker_points_dic', None)
    line_width = params.get('line_width', 2)
    line_dash = params.get('line_dash', 'solid')
    axes_title = params.get('axes_title', None)
    xlim = params.get('xlim', None)
    ylim = params.get('ylim', None)
    xlabel = params.get('xlabel', None)
    ylabel = params.get('ylabel', None)
    sync_xaxes = params.get('sync_xaxes', True)
    sync_yaxes = params.get('sync_yaxes', False)
    tick_labelsize = params.get('tick_labelsize', 10)
    title_font_size = params.get('title_font_size', 18)  # New parameter for title font size
    x_data_type = params.get('x_data_type','index')
    mode = params.get('mode', 'lines+markers')
    fig_name_str = params.get('fig_name_str','')    


    # Extract x_data and y_data from args or params
    if len(args) == 2:
        x_data, y_data = args
    elif len(args) == 1:
        y_data = args[0]
        x_data = params.get('x_data')
    else:
        y_data = params.get('y_data')
        x_data = params.get('x_data')

    # Raise an error if y_data is not provided
    if y_data is None:
        raise ValueError('y_data must be provided')

    # Handle pandas DataFrame/Series
    if isinstance(y_data, (pd.Series, pd.DataFrame)):
        y_data = y_data.values

    if isinstance(y_data, (list, np.ndarray)) and not isinstance(y_data[0], (list, np.ndarray)):
        y_data = [y_data]  # Convert single y_data to list of lists for consistency

    # Use index for x_data if not provided

# used for formatting x_axes
    if x_data_type == 'time':
        time_data = True
    else:
        if x_data is None:
            x_data = np.arange(len(y_data[0]))  # Use index if x_data is not provided
            time_data = False
        else:
            time_data = pd.api.types.is_datetime64_any_dtype(x_data)
            x_data = np.asarray(x_data)


    # Handle figure creation
    if fig is None or axes is None:
        num_cols = min(max_axes_in_row, num_axes)
        num_rows = (num_axes + num_cols - 1) // num_cols

        if axes_title is not None:
            if not isinstance(axes_title, list):
                axes_title = [axes_title] * num_axes
        else:
            axes_title = None

        fig = make_subplots(rows=num_rows, cols=num_cols, subplot_titles=axes_title)
        axes = [(r + 1, c + 1) for r in range(num_rows) for c in range(num_cols)]
        fig_show = True
    else:
        fig_show = False

    x_data_num = x_data
    if (x_data_type == 'time'):
        x_data = timea.datenum2datetime(x_data).to_list()
        

    # Plot each line
    for i, y in enumerate(y_data):
        current_line_color = line_color[i] if isinstance(line_color, list) else line_color
        current_line_dash = line_dash[i] if isinstance(line_dash, list) else line_dash
        current_line_width = line_width[i] if isinstance(line_width, list) else line_width

        scatter_trace = go.Scatter(
            x=x_data,
            y=y,
            mode=mode,
            line=dict(color=current_line_color, width=current_line_width, dash=current_line_dash),
            showlegend=line_name is not None
        )
        
        if line_name:
            scatter_trace.name = line_name[i] if isinstance(line_name, list) else line_name

        fig.add_trace(scatter_trace, row=axes[subplot_index][0], col=axes[subplot_index][1])

        # Add marker points if provided


     # Add marker points if provided
      # Initialize a set to keep track of which names have already been added to the legend
        added_names = set()



        if marker_points_dic:
            if not isinstance(marker_points_dic, list):
                marker_points_dic = [marker_points_dic]

            for marker_points_dic_part in marker_points_dic:
                locs = marker_points_dic_part.get('loc', [])

                      
                marker_colors = marker_points_dic_part.get('color', current_line_color)  # Use line color if not explicitly set
                symbols = marker_points_dic_part.get('symbol', 'circle')
                marker_name = marker_points_dic_part.get('name', None)  # Get the name for the legend, None if not configured

                if isinstance(marker_colors, str):
                    marker_colors = [marker_colors] * len(locs)
                if isinstance(symbols, str):
                    symbols = [symbols] * len(locs)

                for j, loc in enumerate(locs):
                    # if loc in x_data_num:
                    # idx = np.argmin(np.abs(x_data_num - loc))  # Find closest index in x_data
                    idx = loc
                    # Add the marker as a separate trace
                    show_legend = marker_name is not None and marker_name not in added_names
                    if show_legend:
                        added_names.add(marker_name)  # Mark this name as added to the legend

                    
                    fig.add_trace(go.Scatter(
                        x=[x_data[idx]],
                        y=[y[idx]],
                        mode='markers',
                        marker=dict(symbol=symbols[j], size=10, color=marker_colors[j]),
                        name=marker_name if show_legend else None,  # Add the name to show in the legend only if not added yet
                        showlegend=show_legend  # Show legend only once for this name
                    ), row=axes[subplot_index][0], col=axes[subplot_index][1])

    # Update axes ranges, labels, etc.
    if xlim:
        fig.update_xaxes(range=xlim, row=axes[subplot_index][0], col=axes[subplot_index][1])
    if ylim:
        fig.update_yaxes(range=ylim, row=axes[subplot_index][0], col=axes[subplot_index][1])

    if xlabel:
        fig.update_xaxes(title_text=xlabel, row=axes[subplot_index][0], col=axes[subplot_index][1])
    if ylabel:
        fig.update_yaxes(title_text=ylabel, row=axes[subplot_index][0], col=axes[subplot_index][1])

    # Handle time formatting
    if time_data:
        # fig.update_xaxes(
        #     tickvals=x_data,  # Use the x_data positions for tick values
        #     ticktext=x_ticks,  # The string labels you want for those tick values
        #     tickangle=45,
        #     tickfont=dict(size=tick_labelsize)
        # )        
        fig.update_xaxes(tickangle=45, tickfont=dict(size=tick_labelsize))
    else:
        fig.update_xaxes(tickangle=0, tickfont=dict(size=tick_labelsize))

    if sync_xaxes:
        for ax in axes:
            fig.update_xaxes(matches='x', row=ax[0], col=ax[1])

    if sync_yaxes:
        for ax in axes:
            fig.update_yaxes(matches='y', row=ax[0], col=ax[1])

    fig.update_layout(
        title_font_size=title_font_size,  # Apply the title font size
        title_x=0.5  # Center the title
    )



    # Show the figure if it was newly created
    if fig_show:
        fig.show()
    else:
        return fig, axes

  

# vessels.PlotVesselsData(df,vessel_names=ana5_vessels,columns=[['lon','lat'],['Vr','ground_speed'],['altitude'],['time']],
#                         sub_plots=True,x_data_type='index',mark_events=True,events_df=events_df_filt,len_limit=2)
def plot_df_columns(
    df, 
    columns=None,  # Now a list of lists where each list of columns will be plotted on a dedicated axis
    **params  # All other parameters will be part of **params
):
    if columns is None:
        raise ValueError("You must provide columns as a list of lists.")
    
    if isinstance(columns, str):
        columns = [columns]
        
    # Extract parameters from **params, providing default values if not given
    x_column = params.get('x_column', None)  
    sub_plots = params.get('sub_plots', True)
    line_color = params.get('line_color', None)  
    axes_size = params.get('axes_size', None)
    max_axes_in_row = params.get('max_axes_in_row', 2)
    axes_title = params.get('axes_title', None)
    show_markers = params.get('show_markers', True)
    line_width = params.get('line_width', 2)
    line_dash = params.get('line_dash', 'solid')
    xlim = params.get('xlim', None)
    ylim = params.get('ylim', None)
    xlabel = params.get('xlabel', None)
    ylabel = params.get('ylabel', None)
    sync_xaxes = params.get('sync_xaxes', True)
    sync_yaxes = params.get('sync_yaxes', False)
    marker_points_dic = params.get('marker_points_dic', None)
    x_data_type = params.get('x_data_type', 'index')
    time_column = params.get('time_column', 'timestamp')
    fig_name = params.get('fig_name', None)  # Add global title parameter
    title_font_size = params.get('title_font_size', 18)  # New parameter for title font size
    save_fig = params.get('save_fig', False)
    out_dir = params.get('out_dir', './figures/')
    show_in_browser = params.get('show_in_browser', True)
    new_window = params.get('new_window', True) 
    fig_name_str = params.get('fig_name_str','')

    # Determine x_data based on x_data_type
    if x_data_type == 'index':
        x_data = range(df.shape[0])
        xlabel = 'index'

    elif x_data_type == 'time':        
        x_data = df[time_column]
        xlabel = 'time'

    elif x_data_type == 'df_index':
        x_data = df.index
        xlabel = 'df_index'

    elif x_data_type == 'x_column':
        x_data = df[x_column]
        xlabel = x_column

    if sub_plots:
        if isinstance(columns[0], str):
            columns = [[column] for column in columns]    

    # Check if columns is a list of lists, if not, convert it to list of lists
    if not isinstance(columns[0], list):
        columns = [columns]  # Treat single list as one group for one axis


    dfa.CheckColumnsInDF(df, columns)  # Check if all columns exist in the DataFrame

    num_axes = len(columns)  # Each list in columns will be plotted on one axis

    # Determine axes_size based on the number of axes in a row if axes_size is None
    num_cols = min(num_axes, max_axes_in_row)
    if axes_size is None:
        if num_cols == 1:
            axes_size = (800, 600)
        elif num_cols == 2:
            axes_size = (400, 400)
        elif num_cols == 3:
            axes_size = (300, 300)
        elif num_cols == 4:
            axes_size = (250, 250)

    # Handle color settings
    pc = px.colors
    unique_colors = pc.qualitative.Plotly  # Automatically assign unique colors to each signal
    line_color_idx = 0  # Keep track of the color index across all signals

    # Create subplot titles by joining column names in each group
    subplot_titles = [", ".join(group) for group in columns]

    # Create the subplot scheme with the relevant configurations
    fig, axes, num_cols, num_rows = create_subplot_scheme(
        num_axes=num_axes,
        axes_size=axes_size,
        max_axes_in_row=max_axes_in_row,
        axes_title=subplot_titles  # Set titles for subplots
    )

    # Plot each group of columns on its dedicated subplot
    for i, col_group in enumerate(columns):
        for col_name in col_group:
            # Assign a unique color to each signal
            current_color = unique_colors[line_color_idx % len(unique_colors)]
            line_color_idx += 1

            plot_params = params
            plot_params['line_color'] = current_color
            plot_params['line_width'] = line_width if isinstance(line_width, (int, float)) else line_width[i]
            plot_params['line_dash'] = line_dash if isinstance(line_dash, str) else line_dash[i]

            fig, axes = plot(
                x_data=x_data,
                y_data=[df[col_name].tolist()],
                subplot_index=i if params.get('sub_plots', False) else 0,
                fig=fig,
                xlabel=xlabel,
                axes=axes,
                num_axes=num_axes,
                line_name=col_name,
                **params  # Pass **params directly to plot
            )            

    # Add a global title for the entire figure (above axes titles)
    if fig_name:
        fig_name = fig_name + fig_name_str
        fig.update_layout(
            title_text=fig_name,  # Add global title
            title_x=0.5,
            title_y=0.95,  # Position the title higher
            title_font_size=20  # Adjust font size
        )

    # Add a title to the entire figure when sub_plots=False
    if not sub_plots and axes_title is not None:
        fig.update_layout(title_text=axes_title, title_x=0.5, title_y=0.95, title_font_size=18)

    fig.update_layout(showlegend=True)

    # Automatically show the figure


    if (not fig_name):
        fig_name = 'fig'


    if (show_in_browser):
        OpenFigureInBrowser(fig, fig_name=fig_name,new_window=new_window,out_dir=out_dir)
    else:
        fig.show()  

    # if save_fig:        
    #     fig.write_html(f'{out_dir}/{fig_name}.html')

    # return fig, axes

# # ship_df.sort_values('time',inplace=True,ascending=True)
# # plot(ship_df['time'])
# plot_df_columns(ship_df,columns=['longitude'],sub_plots=True,
#                 axes_title='kuku',marker_points_dic={'loc':ship_df['time'].iloc[[2,114]],'color':'black','symbol':'star'},x_data_type='time')




# plot_df_columns(ship_data, columns=['latitude', 'longitude'],
#  line_styles=['--', '-.'],
#   y_label='Values', legend=True, figsize=(10, 5),
#   color=['red', 'blue',],marker_points=[10, 20, 30],
#   marker_points_style='o',title='Ship Data',
#   ylim=(0, 100), legend_loc='upper right',x_data_type='time')

def create_color_vector(num_colors):
    colors = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black']
    color_cycle = cycle(colors)
    color_vector = [next(color_cycle) for _ in range(num_colors)]
    return color_vector


# def create_subplot_scheme(axes_size=None, num_axes=1, max_axes_in_row=4):
#     """
#     Creates a subplot scheme and returns an array of axes.

#     Parameters:
#     ----------
#     axes_size : tuple
#         Size of each individual subplot (width, height).

#     num_axes : int
#         Total number of subplots to create.

#     max_axes_in_row : int, optional
#         Maximum number of subplots in a row. Default is 4.

#     Returns:
#     -------
#     fig : matplotlib.figure.Figure
#         The created figure.

#     axes : array-like of matplotlib.axes.Axes
#         Array of created subplot axes.
#     """
#     # Calculate the number of rows and columns
#     num_cols = min(max_axes_in_row, num_axes)
#     num_rows = (num_axes + num_cols - 1) // num_cols  # Ceiling division to ensure all axes fit

#     if (axes_size is None):
#         if (num_cols==1):
#             axes_size=(6, 6/3*2)
#         elif (num_cols==2):
#             axes_size = (4, 4/3*2)
#         elif (num_cols==3):
#             axes_size=(3.5, 3.5/3*2)
#         elif (num_cols==4):
#             axes_size = (3, 2)




#     # Calculate figure size based on individual axes size
#     fig_width = axes_size[0] * num_cols
#     fig_height = axes_size[1] * num_rows

#     fig, axes = plt.subplots(num_rows, num_cols, figsize=(fig_width, fig_height), constrained_layout=True)
    
#     # Flatten the axes array if there are multiple rows or columns
#     if num_rows * num_cols > 1:
#         axes = axes.flatten()
#     else:
#         axes = [axes]

#     # Hide any unused subplots
#     for i in range(num_axes, len(axes)):
#         axes[i].set_visible(False)

#     return fig, axes[:num_axes],num_cols,num_rows

import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_subplot_scheme(axes_size=None, num_axes=1, max_axes_in_row=4, axes_title=None, title_font_size=None):
    # Calculate the number of rows and columns
    num_cols = min(num_axes, max_axes_in_row)
    num_rows = (num_axes + num_cols - 1) // num_cols  # Ceiling division to ensure all axes fit

    # Default subplot size if not provided (in pixels)
    if axes_size is None:
        axes_size = (300, 300)  # Approx. size in pixels (width, height)

    # Calculate figure size based on individual axes size
    fig_width = axes_size[0] * num_cols
    fig_height = axes_size[1] * num_rows

    # Calculate font size based on axes size if not provided by user
    if title_font_size is None:
        title_font_size = min(axes_size) * 0.05  # Example: 10% of the smallest dimension

    # Handle titles
    if axes_title is None:
        axes_title = [None] * num_axes  # No titles if none are provided
    elif len(axes_title) < num_axes:
        axes_title.extend([None] * (num_axes - len(axes_title)))  # Fill missing titles with None

    # Create a subplot figure with the specified titles
    fig = make_subplots(
        rows=num_rows,
        cols=num_cols,
        subplot_titles=axes_title
    )

    # Adjust title font size for each subplot
    for annotation in fig['layout']['annotations']:
        annotation['font'] = dict(size=title_font_size)

    # Store axes (subplots) references
    axes = []

    for i in range(num_axes):
        row = (i // num_cols) + 1
        col = (i % num_cols) + 1
        axes.append((row, col))

    # Update layout to adjust size
    fig.update_layout(height=fig_height, width=fig_width, showlegend=True)

    return fig, axes, num_cols, num_rows


def plot_multiple_y_axes(df, columns=None, axes=None, x_column='index', fig_size=(5, 3)):
    """
    Plots multiple columns of a DataFrame with separate Y-axes on a single plot.

    Parameters:
    ----------
    df : pd.DataFrame
        The input DataFrame containing the data to plot.

    columns : list
        List of column names in the DataFrame to be plotted on the Y-axes.

    axes : list, optional
        List of labels for the Y-axes corresponding to each column. 
        If None, will use column names as labels.

    x_column : str, optional
        Specifies the X-axis data. Options are:
        - 'index': uses the DataFrame index as the X-axis.
        - 'time': uses the 'time' column in the DataFrame as the X-axis.

    fig_size : tuple, optional
        Size of the figure. Default is (5, 3).

    Raises:
    ------
    ValueError:
        If the length of columns and axes are not the same.

    Example:
    --------
    plot_multiple_y_axes(df, columns=['col1', 'col2'], axes=['Column 1', 'Column 2'], x='time')
    """

    if axes is None:
        axes = columns

    if len(columns) != len(axes):
        raise ValueError("Length of columns and axes must be the same")

    fig, ax1 = plt.subplots(figsize=fig_size)

    color_map = plt.cm.get_cmap('tab10')
    lines = []
    labels = []

    if x_column == 'index':
        x = df.index
    else:
        x = df[x_column]

    ax1.plot(x, df[columns[0]], color=color_map(0), marker='o', label=axes[0])
    ax1.set_xlabel('Index')
    ax1.set_ylabel(axes[0], color=color_map(0))
    ax1.tick_params(axis='y', labelcolor=color_map(0))

# if it's a datetime
    # if pd.api.types.is_datetime64_any_dtype(df[x_column]):
    #     plt.xticks(rotation=45, ha='right', fontsize=8)

    lines.append(ax1.lines[-1])
    labels.append(axes[0])

    axes_list = [ax1]
    for i in range(1, len(columns)):
        ax = ax1.twinx()
        ax.spines['right'].set_position(('outward', 60 * i))
        ax.plot(x, df[columns[i]], color=color_map(i), marker='x', label=axes[i])
        ax.set_ylabel(axes[i], color=color_map(i))
        ax.tick_params(axis='y', labelcolor=color_map(i))

        lines.append(ax.lines[-1])
        labels.append(axes[i])
        axes_list.append(ax)

    # Rotate x-axis labels
# if it's a datetime
    # if pd.api.types.is_datetime64_any_dtype(df[x_column]):
    #     ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    #     plt.xticks(rotation=45, ha='right', fontsize=8)

    # Use MaxNLocator to reduce the number of ticks
    # ax1.xaxis.set_major_locator(MaxNLocator(nbins=5))

    ax1.legend(lines, labels)
    plt.title('Multiple Columns with Separate Y-Axes')
    fig.tight_layout()

    plt.show()



def plot_hist(series, bins=10, ax=None, title='Histogram', xlabel='Value', ylabel='Frequency', color='blue', kde=False):
    """
    Plots a histogram of the given series using Seaborn.

    Parameters:
    - series: pandas Series or list of values to plot
    - bins: number of bins for the histogram
    - ax: matplotlib Axes object, if None, a new figure and axis will be created
    - title: title of the histogram
    - xlabel: label for the x-axis
    - ylabel: label for the y-axis
    - color: color of the histogram bars
    - kde: whether to plot a kernel density estimate
    """
    if ax is None:
        fig, ax = plt.subplots()

    sns.histplot(series, bins=bins, kde=kde, ax=ax, color=color)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    # Show the plot if a new figure was created
    if ax is None:
        plt.show()
    
    return ax

def get_colors(N):
    random.seed(0)
    colors = [f'#{random.randint(0, 0xFFFFFF):06x}' for _ in range(N)]
    return colors
    

class Cursor:
    def __init__(self, ax, x, y, color='red', annotation_color='blue'):
        self.ax = ax
        self.x = x
        self.y = y
        self.cursor_index = 0
        self.cursor, = ax.plot(x[self.cursor_index], y[self.cursor_index], 'o', color=color)  # Initial cursor
        self.annotation = ax.annotate(f"x={x[self.cursor_index]:.2f}, y={y[self.cursor_index]:.2f}", 
                                      xy=(x[self.cursor_index], y[self.cursor_index]), 
                                      xytext=(10, 10), 
                                      textcoords='offset points',
                                      fontsize=10, color=annotation_color)
        self.fig = ax.figure
        self.fig.canvas.mpl_connect('key_press_event', self.update_cursor)
    
    def update_cursor(self, event):
        if event.key == 'left':
            self.cursor_index = max(0, self.cursor_index - 1)
        elif event.key == 'right':
            self.cursor_index = min(len(self.x) - 1, self.cursor_index + 1)
        
        # Update cursor position
        self.cursor.set_data(self.x[self.cursor_index], self.y[self.cursor_index])
        
        # Update annotation
        self.annotation.set_text(f"x={self.x[self.cursor_index]:.2f}, y={self.y[self.cursor_index]:.2f}")
        self.annotation.set_position((self.x[self.cursor_index], self.y[self.cursor_index]))
        
        # Redraw the plot with updated cursor and annotation
        self.fig.canvas.draw()





explorer_pids = []





def OpenFigureInBrowser(fig, fig_name="Plotly Figure", new_window=False, 
                        window_size=(1200, 800), 
                        browser_path="C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
                        out_dir='./figures/'):
    """
    Opens a Plotly figure in a specified browser window. If 'new_window' is True,
    opens in a new browser window. Otherwise, it opens in the current browser tab.

    Parameters:
    - fig: Plotly figure object to display.
    - fig_name: Custom name for the browser tab (default is 'Plotly Figure').
    - new_window: If True, opens the figure in a new browser window. Default is False.
    - window_size: Tuple specifying the window size (width, height). Default is (1200, 800).
    - browser_path: Path to the browser executable. Default is Microsoft Edge.
    - file_name: Optional name for the HTML file. Default is None (temporary file).
    """
    global explorer_pids

    # Generate the complete HTML content with full_html=True
    html_content = fig.to_html(full_html=True, include_plotlyjs='cdn')
    
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # Determine the file path
    file_name = out_dir+fig_name
    if file_name:
        # Use specified file name in the current directory
        file_path = os.path.abspath(file_name + ".html")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)
    else:
        # Use a temporary file if no file name is provided
        temp_file = tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8")
        temp_file.write(html_content)
        temp_file.close()
        file_path = temp_file.name

    # Construct the URL to the file
    file_url = f"file://{file_path}"

    try:
        if new_window:
            # Open a new window with the specified browser and capture the process
            proc = subprocess.Popen([
                browser_path, 
                "--new-window", 
                f"--window-size={window_size[0]},{window_size[1]}", 
                file_url
            ])
            # Store the process ID (PID)
            explorer_pids.append(proc.pid)
        else:
            # Open in the default browser (fallback to the webbrowser module)
            subprocess.Popen([browser_path, file_url])

    except FileNotFoundError:
        print(f"Browser not found at {browser_path}. Opening in the default browser tab instead.")
        webbrowser.open(file_url)


def CloseBrowserWindows():
    """Closes only the Browser windows that were opened by this script."""
    global explorer_pids

    for pid in explorer_pids:
        try:
            # Terminate the specific Browser process
            subprocess.run(["taskkill", "/F", "/PID", str(pid)], check=True)
            print(f"Closed Browser window with PID: {pid}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to close Browser window with PID {pid}: {e}")

    # Clear the stored PIDs after closing
    explorer_pids.clear()
