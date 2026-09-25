"""Shared fixtures: a duck-typed fake CurrentField (no survey-currents dep)."""

import datetime as dt
import types

import numpy as np
import pytest


def make_fake_current_field(nt=3, ny=12, nx=16, seed=7, with_land=True,
                            with_temperature=True):
    """Gyre + warm core on a lat/lon grid, duck-typed like CurrentField."""
    rng = np.random.default_rng(seed)
    lats = np.linspace(41.5, 46.5, ny)
    lons = np.linspace(-92.5, -84.5, nx)
    yy, xx = np.meshgrid(np.linspace(-1, 1, ny), np.linspace(-1, 1, nx),
                         indexing="ij")
    land = (xx ** 2 + yy ** 2) > 0.86 if with_land else np.zeros((ny, nx), bool)
    u = np.empty((nt, ny, nx))
    v = np.empty((nt, ny, nx))
    t = np.empty((nt, ny, nx))
    t0 = dt.datetime(2026, 9, 16, tzinfo=dt.timezone.utc)
    times = []
    for k in range(nt):
        uk = -yy * 0.35 + rng.normal(0, 0.02, (ny, nx))
        vk = xx * 0.35 + rng.normal(0, 0.02, (ny, nx))
        tk = 18.0 - 4.0 * (xx ** 2 + yy ** 2) + 0.2 * k
        u[k] = np.where(land, np.nan, uk)
        v[k] = np.where(land, np.nan, vk)
        t[k] = np.where(land, np.nan, tk)
        times.append((t0 + dt.timedelta(hours=k)).isoformat())
    ns = types.SimpleNamespace()
    ns.u, ns.v = u, v
    ns.temperature = t if with_temperature else None
    ns.times, ns.lats, ns.lons = times, lats, lons
    ns.crs, ns.source = "EPSG:4326", "test/fake"
    return ns


@pytest.fixture
def fake_cf():
    return make_fake_current_field()
