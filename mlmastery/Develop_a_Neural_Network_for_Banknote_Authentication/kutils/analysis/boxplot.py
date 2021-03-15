import math
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import seaborn as sns
import matplotlib.pyplot as plt
from kutils.analysis import GeneralPlotUtils
from functools import partial


class Utils(GeneralPlotUtils):
    def __init__(self, data, figsize=(20,4), sns_style='whitegrid'):
        super(Utils, self).__init__(figsize)
        self.data = data
        self.sns_style = sns_style        

    def s_boxplot(self, column, title=None):
        sns.set_theme(style=self.sns_style)
        g = sns.boxplot(x=self.data[column])
        if title:
            g.set_title(title)
            
        return g        

    def sns_boxplot(self, x, y_list, titles, col_num=4, figsize=None):
        sns.set_theme(style=self.sns_style)
        figsize = self.figsize if figsize is None else figsize
        
        if len(y_list) == 1 or isinstance(y_list, str):
            y = y_list if isinstance(y_list, str) else y_list[0]
            g = sns.boxplot(x=x, y=y)
            title = titles[0] if isinstance(titles, list) else str(titles)
            g.set_title(title)
            return g
        
        row_num = math.ceil(len(y_list) / col_num)
        if row_num == 1:
            col_num = len(y_list)            
            
        fig, ax = plt.subplots(row_num, col_num, figsize=figsize)
        for i, col_name in enumerate(y_list):
            ri = i // col_num
            ci = i % col_num
            if row_num > 1:
                sns.boxplot(x=x, y=col_name, data=self.data, ax=ax[ri, ci])
                if titles[i]:
                    ax[ri, ci].set_title(titles[i])
            else:
                sns.boxplot(x=x, y=col_name, data=self.data, ax=ax[ci])
                if titles[i]:
                    ax[ci].set_title(titles[i])

        return fig, ax
