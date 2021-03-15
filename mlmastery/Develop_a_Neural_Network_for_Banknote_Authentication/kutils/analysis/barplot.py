import math
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import seaborn as sns
import matplotlib.pyplot as plt
from kutils.analysis import GeneralPlotUtils
from functools import partial


class Utils(GeneralPlotUtils):
    def __init__(self, data, figsize=(20,4)):
        super(Utils, self).__init__(figsize)
        self.data = data

    def sns_countplot(self, hue, x_list, col_num=4, figsize=None):
        figsize = self.figsize if figsize is None else figsize
        row_num = math.ceil(len(x_list) / col_num)

        if len(x_list) == 1 or isinstance(x_list, str):
            plt.rcParams['figure.figsize'] = figsize
            return sns.countplot(x=x_list, data=self.data, hue=hue)
        
        if row_num == 1:
            col_num = len(x_list)            
                    
        fig, ax = plt.subplots(row_num, col_num, figsize=figsize)
        for i, col_name in enumerate(x_list):
            ri = i // col_num
            ci = i % col_num
            if row_num > 1:
                sns.countplot(x=col_name, data=self.data, hue=hue, ax=ax[ri, ci])
            else:
                sns.countplot(x=col_name, data=self.data, hue=hue, ax=ax[ci])

        return fig, ax        

    def sns_barplot(self, y, x_list, col_num=4, figsize=None, rotation=45, horizontalalignment='right'):
        row_num = math.ceil(len(x_list) / col_num)
        figsize = self.figsize if figsize is None else figsize

        if len(x_list) == 1 or isinstance(x_list, str):
            col_name = x_list[0] if isinstance(x_list, list) else str(x_list)
            self.set_figsize(figsize)
            g = sns.barplot(x=col_name, y=y, data=self.data)
            labels = g.set_xticklabels(g.get_xticklabels(), rotation=45, horizontalalignment='right')
            return g
        
        if row_num == 1:
            col_num = len(x_list)            
                    
        fig, ax = plt.subplots(row_num, col_num, figsize=figsize)
        for i, col_name in enumerate(x_list):
            ri = i // col_num
            ci = i % col_num
            if row_num > 1:
                g = sns.barplot(x=col_name, y=y, data=self.data, ax=ax[ri, ci])            
            else:
                g = sns.barplot(x=col_name, y=y, data=self.data, ax=ax[ci])

            labels = g.set_xticklabels(g.get_xticklabels(), rotation=45, horizontalalignment='right')

        return fig, ax
            

    def stacked_bar(self, stacked_col_name, columns, col_num=4, figsize=None, rot=0):
        if len(columns) == 1:
            return self.data[[stacked_col_name, columns[0]]].groupby([columns[0], stacked_col_name]) \
                    .size().unstack().plot(kind='bar', stacked=True, rot=rot, figsize=figsize)
        
        row_num = math.ceil(len(columns) / col_num)
        if row_num == 1:
            col_num = len(columns)            
            
        figsize = self.figsize if figsize is None else figsize
        fig, ax = plt.subplots(row_num, col_num, figsize=figsize)
        for i, col_name in enumerate(columns):
            ri = i // col_num
            ci = i % col_num
            if row_num > 1:
                self.data[[stacked_col_name, col_name]].groupby([col_name, stacked_col_name]) \
                    .size().unstack().plot(kind='bar', stacked=True, ax=ax[ri, ci], rot=rot)                
            else:
                self.data[[stacked_col_name, col_name]].groupby([col_name, stacked_col_name]) \
                    .size().unstack().plot(kind='bar', stacked=True, ax=ax[ci], rot=rot)     
            
        return fig, ax
