"""Methods for plotting."""


import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np


def build_histogram_of_rating_scores(
    df: pd.DataFrame,
    path: str = None,
    x: str = "review_rating",
    xlabel: str = None,
    ylabel: str = "Frequency",
    display: bool = True,
    season: int = None,
    episode: int = None,
    show: str = None,
) -> None:
    """Build and save a histogram specific to rating scores with auto-generated text.

    Args:
        df (pd.DataFrame): source data-frame.
        path (str, optional): path where to save plot. Defaults to None.
        x (str, optional): which column to use for bar plot. Defaults to "review_rating".
        display (bool, optional): boolean to display plot or not. Defaults to True.
        season (int, optional): season number for text display.
        episode (int, optional): episode number for text display.
        show (str, optional): show name.

    Returns:
        None
    """
    sns.set(rc={"figure.figsize": (12, 6)})
    
    n_colors = df[x].nunique()  # Get number of colors for palette
    rg_palette = sns.color_palette("RdYlGn_r", n_colors=n_colors)
    rg_palette.reverse()  # reverse palette from red to green

    # Construct the cat plot
    g = sns.catplot(
        data=df,
        x=x,
        kind="count",
        palette=rg_palette,
        height=5,
        aspect=1.5,
        order=["abysmal", "bad", "average", "good", "amazing"],
    )
    ax = g.facet_axis(
        0, 0
    )  # extract the matplotlib axes_subplot objects from the FacetGrid

    # Iterate through the axes containers to assign tooltips
    for c in ax.containers:
        values = [v.get_height() for v in c]
        values_sum = sum(values)
        labels = [f"{round((v / values_sum) * 100)}%" for v in values]
        ax.bar_label(c, labels=labels, label_type="edge", fontsize=10)

    # Handle plot text according to data
    if not xlabel:
        xlabel = x
    title = f"Histogram of All {xlabel}"

    if all([show, season]):
        if (episode is None) or (episode == 0):
            title_root = f"({show}-S{season})"
        else:
            title_root = f"({show}-S{season}:E{episode})"
    elif show:
        title_root = f"({show})"
    else:
        title_root = ""

    plt.title(f"{title_root} {title}", fontsize=14)
    plt.xlabel(xlabel, fontsize=10)
    plt.ylabel(ylabel, fontsize=10)

    # Save plot
    if path:
        plt.save(path)

    # Optional show plot
    if display:
        plt.show()
    plt.clf()


def build_categorical_bot_plot(
    df: pd.DataFrame,
    x: str,
    y: str,
    path: str = None,
    xlabel: str = None,
    ylabel: str = None,
    display: bool = True,
    season: int = None,
    episode: int = None,
    show: str = None,
) -> None:
    """Constructs a chart with a series of bar plots, with granularity by a dimension.

    Args:
        df (pd.DataFrame): source data-frame.
        x (str): x axis.
        y (str): y axis.
        path (str, optional): path where to save plot. Defaults to None.
        xlabel (str, optional): plot text label for x. Defaults to None.
        ylabel (str, optional): plot text label for y. Defaults to None.
        display (bool, optional): boolean to display plot or not. Defaults to True.

    Returns:
        None
    """
    sns.set(rc={"figure.figsize": (12, 6)})
    
    # We filter in case of many outliers in a very long tail
    ylabel_95th = df[y].quantile(0.95)  # 95th percentile
    temp_df = df[df[y] < ylabel_95th]

    n_colors = df[x].nunique()  # Get number of colors for palette
    rg_palette = sns.color_palette("RdYlGn_r", n_colors=n_colors)

    # Combine a categorical plot with the stripplot function for boxes/violins/etc.
    g = sns.catplot(
        data=temp_df, x=x, y=y, kind="box", height=6, aspect=1.2, palette=rg_palette
    )
    sns.stripplot(
        data=temp_df, x=x, y=y, color="k", size=0, ax=g.ax, palette=rg_palette
    )

    # Handle plot text according to data
    if not all([xlabel, ylabel]):
        xlabel = x
        ylabel = y
    title = f"Box Plot of {ylabel} over {xlabel}"

    if all([show, season]):
        if (episode is None) or (episode == 0):
            title_root = f"({show}-S{season})"
        else:
            title_root = f"({show}-S{season}:E{episode})"
    elif show:
        title_root = f"({show})"
    else:
        title_root = ""

    plt.title(f"{title_root} {title}", fontsize=14)
    plt.ylabel(ylabel, fontsize=10)
    plt.xlabel(xlabel, fontsize=10)

    # Save plot
    if path:
        plt.save(path)

    # Optional show plot
    if display:
        plt.show()
    plt.clf()


def build_percent_histogram(
    df: pd.DataFrame,
    x: str,
    bins: int=50,
    xlabel: str = None,
    ylabel: str = None,
    weights: str = None,
    display: bool = True,
    season: int = None,
    episode: int = None,
    show: str = None,
    path: str = None,
) -> None:
    """_summary_

    Args:
        df (pd.DataFrame): source dataframe.
        x (str): x axis.
        bins (int, optional): number of bins to build for histogram. Defaults to 50.
        path (str, optional): path where to save plot. Defaults to None.
        xlabel (str, optional): plot text label for x. Defaults to None.
        ylabel (str, optional): plot text label for y. Defaults to None.
        weights (str, optional): column by witch to weight the frequencies. Defaults to None.
        display (bool, optional): boolean to display plot or not. Defaults to True.
        season: int = None,
        episode: int = None,
        show: str = None.
        
    Returns:
        None
    """
    sns.set(rc={"figure.figsize": (12, 6)})
    sns.histplot(
        data=df,
        x=x,
        weights=weights,
        stat="percent",
        bins=bins,
        kde=True,
        discrete=False,
    )
    
    # Handle plot title according to data
    if not xlabel:
        xlabel = x
        
    title = f"Distribution of {xlabel}"

    if all([show, season]):
        if (episode is None) or (episode == 0):
            title_root = f"({show}-S{season})"
        else:
            title_root = f"({show}-S{season}:E{episode})"
    elif show:
        title_root = f"({show})"
    else:
        title_root = ""

    plt.title(f"{title_root} {title}", fontsize=16)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    
    # Save plot
    if path:
        plt.save(path)

    # Optional show plot
    if display:
        plt.show()
    plt.clf()
    
    


def build_categorical_violin_plot(
    df: pd.DataFrame,
    x: str,
    y: str,
    path: str = None,
    xlabel: str = None,
    ylabel: str = None,
    display: bool = True,
    season: int = None,
    episode: int = None,
    show: str = None,
) -> None:
    """Build a series of violin plots with granularity after x.

    Args:
        df (pd.DataFrame): source dataframe.
        x (str): x axis.
        y (str): y axis.
        path (str, optional): path where to save plot. Defaults to None.
        xlabel (str, optional): plot text label for x. Defaults to None.
        ylabel (str, optional): plot text label for y. Defaults to None.
        display (bool, optional): boolean to display plot or not. Defaults to True.
        season: int = None,
        episode: int = None,
        show: str = None,
    """
    sns.set(rc={"figure.figsize": (12, 6)})
    
    g = sns.catplot(
        data=df,
        x=x,
        y=y,
        kind="violin",
        height=6,
        aspect=3,
        cut=0,
        bw=0.18,
        linewidth=1.5,
        palette="muted",
    )

    # Handle y axis ticks
    min_y = df[y].min()
    max_y = df[y].max()
    plt.yticks(np.arange(min_y, max_y + 1, 1.0))

    # Handle plot title according to data
    if not all([xlabel, ylabel]):
        xlabel = x
        ylabel = y
        
    title = f"Distribution of {xlabel}"

    if all([show, season]):
        if (episode is None) or (episode == 0):
            title_root = f"({show}-S{season})"
        else:
            title_root = f"({show}-S{season}:E{episode})"
    elif show:
        title_root = f"({show})"
    else:
        title_root = ""

    plt.title(f"{title_root} {title}", fontsize=16)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)

    # Save plot
    if path:
        plt.save(path)

    # Optional show plot
    if display:
        plt.show()
    plt.clf()
