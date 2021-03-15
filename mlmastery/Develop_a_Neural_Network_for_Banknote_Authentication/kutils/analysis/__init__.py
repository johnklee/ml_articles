import math
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import seaborn as sns
import matplotlib.pyplot as plt
import itertools
from heatmap import heatmap, corrplot  
from functools import partial


def corr(data, target_column, top_n=20):
    corr_df = data.corr().abs()
    s = corr_df.unstack()
    so = s.sort_values(kind="quicksort", ascending=False).reset_index()
    top_df = so[(so['level_0']!=so['level_1']) & (so['level_1'] == target_column)][:top_n]
    top_df = top_df.rename(columns={'level_0':'feature', 'level_1':'target', 0:'corr'})
    return top_df


def corr_heatmap(data, figsize=(10, 10)):
    # medium/Better_Heatmaps_and_Correlation_Matrix_Plots_in_Python
    plt.figure(figsize=figsize)  
    corrplot(data.corr())


def plot_confusion_matrix(cm,
                          target_names,
                          title='Confusion matrix',
                          cmap=None,
                          normalize=True):
    """
    given a sklearn confusion matrix (cm), make a nice plot

    Arguments
    ---------
    cm:           confusion matrix from sklearn.metrics.confusion_matrix

    target_names: given classification classes such as [0, 1, 2]
                  the class names, for example: ['high', 'medium', 'low']

    title:        the text to display at the top of the matrix

    cmap:         the gradient of the values displayed from matplotlib.pyplot.cm
                  see http://matplotlib.org/examples/color/colormaps_reference.html
                  plt.get_cmap('jet') or plt.cm.Blues

    normalize:    If False, plot the raw numbers
                  If True, plot the proportions

    Usage
    -----
    plot_confusion_matrix(cm           = cm,                  # confusion matrix created by
                                                              # sklearn.metrics.confusion_matrix
                          normalize    = True,                # show proportions
                          target_names = y_labels_vals,       # list of names of the classes
                          title        = best_estimator_name) # title of graph

    Citiation
    ---------
    http://scikit-learn.org/stable/auto_examples/model_selection/plot_confusion_matrix.html

    """
    accuracy = np.trace(cm) / float(np.sum(cm))
    misclass = 1 - accuracy

    if cmap is None:
        cmap = plt.get_cmap('Blues')

    plt.figure(figsize=(8, 6))
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()

    if target_names is not None:
        tick_marks = np.arange(len(target_names))
        plt.xticks(tick_marks, target_names, rotation=45)
        plt.yticks(tick_marks, target_names)

    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]


    thresh = cm.max() / 1.5 if normalize else cm.max() / 2
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        if normalize:
            plt.text(j, i, "{:0.4f}".format(cm[i, j]),
                     horizontalalignment="center",
                     color="white" if cm[i, j] > thresh else "black")
        else:
            plt.text(j, i, "{:,}".format(cm[i, j]),
                     horizontalalignment="center",
                     color="white" if cm[i, j] > thresh else "black")


    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label\naccuracy={:0.4f}; misclass={:0.4f}'.format(accuracy, misclass))
    plt.show()
    

def sns_pairplot(
    data,
    hue_column,
    drop_columns=[],
    colors=[
        'xkcd:goldenrod', 'xkcd:orange','xkcd:sienna','xkcd:violet',
        'xkcd:olive','xkcd:turquoise', "xkcd:yellowgreen", 'xkcd:indigo', 'xkcd:blue'
    ],
    hue_color_map=None):
    if hue_color_map is None:
        hue_color_map = {}
        for i, label in enumerate(list(data[hue_column].unique())):
            hue_color_map[label] = colors[i]

    sns_plot = sns.pairplot(
        data,
        hue=hue_column,
        palette=hue_color_map)
    return sns_plot


class GeneralPlotUtils:
    def __init__(self, figsize=(20,4)):
        self.set_figsize(figsize)

    def set_figsize(self, figsize):
        plt.rcParams['figure.figsize'] = figsize
        self.figsize = figsize
