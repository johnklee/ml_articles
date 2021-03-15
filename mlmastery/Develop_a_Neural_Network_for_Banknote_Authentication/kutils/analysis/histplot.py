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

    def hist(self, columns, col_num=4):
        row_num = math.floor(len(columns) / col_num)
        return self.data.hist(column=columns, figsize=self.figsize, layout=(row_num,col_num))


    def sns_hist(self, columns, col_num=4, kde=True, figsize=None):
        # plot hist with kernal density edstimation to get an average line
        row_num = math.ceil(len(columns) / col_num)
        figsize = self.figsize if figsize is None else figsize
        fig, ax = plt.subplots(row_num, col_num, figsize=figsize)
        for i, col_name in enumerate(columns):
            ri = i // col_num
            ci = i % col_num
            if row_num > 1:
                sns.histplot(data=self.data, x=col_name, kde=kde, ax=ax[ri, ci])
            else:
                sns.histplot(data=self.data, x=col_name, kde=kde, ax=ax[ci])
            
        return fig, ax
    
    def plot_overlap_hist(self, outer_col, inner_col, bin_width, ylabel='Frequency', alpha=0.5):
        '''
        data: DataFrame
            data to draw overlap hist gram
        outer_col: String
            Column of data as x-axis
        inner_col: String
            Column of data as category of y-axis        
        bin_width: int
            Bin width
        ylabel: str
            Label of y-axis
        '''
        min_amt = self.data[outer_col].min()
        max_amt = self.data[outer_col].max()
        first_bin=min_amt//bin_width*bin_width
        bins=[first_bin+i*bin_width for i in range(math.ceil((max_amt-min_amt)/bin_width)+1)]
        for idx, (g_name, g) in enumerate(self.data.groupby(inner_col)): 
            plt.hist(g[outer_col].values, alpha=alpha, label=g_name, bins=bins)
        
        plt.legend()
        plt.xlabel(outer_col)
        plt.ylabel('Frequency')
        
        return plt
