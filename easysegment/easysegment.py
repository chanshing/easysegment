import warnings
import numpy as np
import pandas as pd
from scipy.stats import rankdata
from sklearn.cluster import KMeans
from sklearn.preprocessing import power_transform

__all__ = ['segment', 'kmeans', 'quantiles']


def segment(x, labels, n_init=100, max_iter=1000, random_state=42, ascending=True, min_samples=50):
    """ Segment `x` using KMeans, or quantiles if not enough data. """

    if isinstance(x, pd.Series):
        x = x.to_numpy()

    if len(x) < min_samples:
        warnings.warn(
            f"Not enough data for KMeans ({len(x)}). Using quantiles...",
            NotEnoughDataWarning
        )
        return quantiles(x, labels)

    else:
        return kmeans(
            x, labels,
            n_init=n_init,
            max_iter=max_iter,
            random_state=random_state,
            ascending=ascending
        )


def kmeans(x, labels, n_init=100, max_iter=1000, random_state=42, ascending=True):
    x = x.reshape(len(x), 1)
    k = len(labels)
    y = KMeans(
        k, n_init=n_init, max_iter=max_iter, random_state=random_state
    ).fit_predict(power_transform(x))
    y_map_rank = pd.Series(x.ravel()).groupby(y).mean().argsort().reset_index(drop=True)
    y_map_rank = pd.Series(y_map_rank.index.to_numpy(), index=y_map_rank)  # swap index-value
    if not ascending:  # reverse ranking
        y_map_rank[:] = y_map_rank.to_numpy()[::-1]
    y = pd.Series(y).replace(y_map_rank).replace(dict(enumerate(labels)))
    y = y.to_numpy()
    return y


def quantiles(x, labels, q=None):

    if q is None:
        q = len(labels)
        nq = q
    else:
        nq = len(q)

    if len(np.unique(x)) <= nq:
        y = rankdata(x, method='dense')
        y = pd.Series(y).replace(dict(enumerate(labels, start=1)))
        y = y.to_numpy()

    else:
        y = pd.Categorical(pd.qcut(x, q, duplicates='drop'))
        ncat = len(y.categories)
        y = y.rename_categories(labels[:ncat])
        y = y.to_numpy()

    return y


class NotEnoughDataWarning(UserWarning, ValueError):
    pass


class EmptyDataError(Exception):
    pass
