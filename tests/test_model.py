import json

import numpy as np
import pytest

from tseda import model


def test_individual(ts):
    ind = model.Individual(individual=ts.individual(0))
    assert ind is not None
    assert ind.id == 0
    assert ind.population == 1
    assert ind.metadata is not None
    np.testing.assert_equal(ind.samples, [0, 1])
    with pytest.raises(TypeError):
        ind = model.Individual()


def test_sample_set_init(ts):
    for pop in ts.populations():
        ss = model.SampleSet(pop.id, population=pop)
        assert ss is not None
        assert ss.id == pop.id
        assert ss.name == json.loads(pop.metadata.decode())["population"]
        assert ss.color == ss.colormap[pop.id]
    ss = model.SampleSet(0, name="test")
    assert ss is not None
    assert ss.id == 0
    assert ss.name == "test"
    assert ss.population is None


def test_update_individual_sample_set(ds):
    pass


def test_toggle_individual(ds):
    pass


def test_gnn(ds):
    pass


def test_get_samples(ds):
    pass


def test_get_individuals(ds):
    pass


def test_sample_sets_view(ds):
    pass


def test_make_sample_sets(ds):
    pass


def test_get_sample_sets(ds):
    pass
