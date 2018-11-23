# -*- coding: utf-8 -*-
"""
@author: Vladimir Shteyn
@email: vladimir.shteyn@googlemail.com

Copyright Vladimir Shteyn, 2018

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
# https://docs.pytest.org/en/latest/example/simple.html
import pytest


def pytest_runtest_makereport(item, call):
    """
    https://docs.pytest.org/en/2.7.3/plugins.html?highlight=re#well-specified-hooks

    Arguments
    ----------
    item : _pytest.runner.TestReport
    _pytest.runner.TestReport object for the given pytest.Item

    call : _pytest.runner.TestReport
    _pytest.runner.TestReport object for the given _pytest.runner.CallInfo.
    """
    if "incremental" in item.keywords:
        if call.excinfo is not None:
            parent = item.parent
            parent._previousfailed = item


def pytest_runtest_setup(item):
    if "incremental" in item.keywords:
        previousfailed = getattr(item.parent, "_previousfailed", None)
        if previousfailed is not None:
            pytest.xfail("previous test failed (%s)" % previousfailed.name)

# also see this for tests with dependencies:
# https://stackoverflow.com/questions/50584294/how-to-control-the-incremental-test-case-in-pytest
