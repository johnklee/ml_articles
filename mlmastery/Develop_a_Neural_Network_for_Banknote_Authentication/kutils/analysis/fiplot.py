import math
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import seaborn as sns
import matplotlib.pyplot as plt
from kutils.analysis import GeneralPlotUtils
from functools import partial
from sklearn.inspection import permutation_importance


class Utils(GeneralPlotUtils):
    def __init__(self, X, y, figsize=(20,4)):
        super(Utils, self).__init__(figsize)
        self.X = X
        self.y = y


    def treelike_fi(self, model, top_n=20, figsize=None, ytick_fontsize=None, xtick_fontsize=None):
        if figsize is not None:
            self.set_figsize(figsize)
            
        feat_importances = pd.Series(model.feature_importances_, index=self.data.columns)        
        ax = feat_importances.nlargest(top_n).plot(kind='barh')
        if ytick_fontsize:
            ax.set_yticklabels(ax.get_yticklabels(), fontsize=ytick_fontsize)

        if xtick_fontsize:
            ax.set_xticklabels(ax.get_xticklabels(), fontsize=xtick_fontsize)

        return ax

    def permutation_fi(self, model, X=None, y=None, top_n=20, figsize=None, ytick_fontsize=None, xtick_fontsize=None, n_repeats=30, random_state=0):
        X = self.X if X is None else X
        y = self.y if y is None else y
        r = permutation_importance(model, X, y, n_repeats=n_repeats, random_state=random_state)
        fi_list = []
        for i in r.importances_mean.argsort()[::-1]:
            #if r.importances_mean[i] - 2 * r.importances_std[i] > 0:
            fi_list.append((X.columns[i], r.importances_mean[i]))            
                
        feat_importances = pd.Series(
            list(map(lambda t: t[1], fi_list)), 
            index=list(map(lambda t: t[0], fi_list))
        )
    
        ax = feat_importances.nlargest(top_n).plot(kind='barh')
        if ytick_fontsize:
            ax.set_yticklabels(ax.get_yticklabels(), fontsize=ytick_fontsize)

        if xtick_fontsize:
            ax.set_xticklabels(ax.get_xticklabels(), fontsize=xtick_fontsize)

        return ax

        
