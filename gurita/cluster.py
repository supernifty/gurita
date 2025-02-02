'''
Module      : cluster 
Description : data clustering 
Copyright   : (c) Bernie Pope, 10 October 2021
License     : MIT 
Maintainer  : bjpope@unimelb.edu.au 
Portability : POSIX
'''

import sys
import logging
import pandas as pd
import sklearn.cluster as skcluster
from sklearn.mixture import GaussianMixture
import numpy as np
import argparse
import gurita.constants as const
from gurita.command_base import CommandBase
import gurita.utils as utils

class KMeans(CommandBase, name="kmeans"):
    description = "k-means clustering"
    category = "transformation"

    def __init__(self):
        super().__init__()
        self.optional.add_argument(
            '-c', '--columns', metavar='COLUMN', nargs="+", type=str, required=False,
            help=f'Select only these named columns')
        self.optional.add_argument(
            '--name', required=False, default=const.DEFAULT_CLUSTER_COLUMN_NAME,
            help=f'Column name for cluster labels. Default: %(default)s.')
        self.optional.add_argument(
            '-n', '--nclusters', type=int, required=False, default=const.DEFAULT_KMEANS_N_CLUSTERS,
            help=f'Number of clusters to generate. Default: %(default)s.')

    
    def run(self, df):
        options = self.options
        selected_df = df

        if options.columns is not None:
            utils.validate_columns_error(df, options.columns)
            selected_df = df[options.columns]

        # select only numeric columns for the cluster 
        selected_df = selected_df.select_dtypes(include=np.number)

        # drop rows with missing values in any column
        selected_df = selected_df.dropna()
        # Cluster the standardized data
        kmeans = skcluster.KMeans(n_clusters=options.nclusters)
        kmeans_transform = kmeans.fit_predict(selected_df)
        df[self.options.name] = pd.Series(kmeans_transform, index=selected_df.index).reindex(df.index).astype('category')
        return df


class GMM(CommandBase, name="gmm"):
    description = "Gaussian mixture model clustering."
    category = "transformation"

    def __init__(self):
        super().__init__()
        self.optional.add_argument(
            '-c', '--columns', metavar='COLUMN', nargs="+", type=str, required=False,
            help=f'Select only these named columns')
        self.optional.add_argument(
            '--name', required=False, default=const.DEFAULT_CLUSTER_COLUMN_NAME,
            help=f'Column name for cluster label. Default: %(default)s.')
        self.optional.add_argument(
            '-n', '--nclusters', type=int, required=False, default=const.DEFAULT_GMM_N_CLUSTERS,
            help=f'Number of clusters to generate. Default: %(default)s.')
        self.optional.add_argument(
            '--maxiter', type=int, required=False, default=const.DEFAULT_GMM_MAX_ITER,
            help=f'Number of expectation maximisation iterations to perform. Default: %(default)s.')

    
    def run(self, df):
        options = self.options
        selected_df = df

        if options.columns is not None:
            utils.validate_columns_error(df, options.columns)
            selected_df = df[options.columns]

        # select only numeric columns for the cluster 
        selected_df = selected_df.select_dtypes(include=np.number)

        # drop rows with missing values in any column
        selected_df = selected_df.dropna()

        gmm = GaussianMixture(n_components=options.nclusters, max_iter=options.maxiter)
        gmm_transform = gmm.fit_predict(selected_df)

        df[self.options.name] = pd.Series(gmm_transform, index=selected_df.index).reindex(df.index).astype('category')
        return df
