import os

import tskit
from pytest import fixture
from tsbrowse import model as tsb_model

from tseda import model

dirname = os.path.abspath(os.path.dirname(__file__))


@fixture(scope="module")
def treesfile():
    return os.path.join(dirname, "data/test.trees")


@fixture(scope="module")
def tszipfile():
    return os.path.join(dirname, "data/test.trees.tsz")


@fixture(scope="module")
def tsbrowsefile():
    return os.path.join(dirname, "data/test.trees.tsbrowse")


@fixture(scope="module")
def ts(treesfile):
    return tskit.load(treesfile)


@fixture(scope="module")
def tsbm(tsbrowsefile):
    return tsb_model.TSModel(tsbrowsefile)


@fixture(scope="module")
def tsm(ts):
    return model.TSEdaModel(ts)


@fixture(scope="module")
def tsmh(tsm):
    """Remove outgroup individuals from model to include only Homo
    Sapiens individuals"""
    tsm.toggle_individual(18)
    tsm.toggle_individual(19)
    tsm.toggle_individual(20)
    return tsm
