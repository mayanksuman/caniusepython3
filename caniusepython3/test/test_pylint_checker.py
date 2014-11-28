# Copyright 2014 Google Inc. All rights reserved.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import absolute_import, unicode_literals

from caniusepython3.test import unittest
import sys

if sys.version_info[0] == 2 and sys.version_info[1] <= 6:
    raise unittest.SkipTest('Pylint requires Python 2.7 or Python 3')

import io
import tokenize

from astroid import test_utils
from pylint import testutils

from caniusepython3 import pylint_checker as checker

def python2_only(test):
    """Decorator for any tests that will fail under Python 3."""
    return unittest.skipIf(sys.version_info[0] > 2, 'Python 2 only')(test)


class StrictPython3CheckerTest(testutils.CheckerTestCase):

    CHECKER_CLASS = checker.StrictPython3Checker

    def check_not_builtin(self, builtin_name, message):
        node = test_utils.extract_node(builtin_name + '  #@')
        with self.assertAddsMessages(testutils.Message(message, node=node)):
            self.checker.visit_name(node)

    @python2_only
    def test_map_builtin(self):
        self.check_not_builtin('map', 'map-builtin')

    @python2_only
    def test_range_builtin(self):
        self.check_not_builtin('range', 'range-builtin')

    @python2_only
    def test_zip_builtin(self):
        self.check_not_builtin('zip', 'zip-builtin')

    @python2_only
    def test_round_builtin(self):
        self.check_not_builtin('round', 'round-builtin')

    @python2_only
    def test_open_builtin(self):
        self.check_not_builtin('open', 'open-builtin')


class UnicodeCheckerTest(testutils.CheckerTestCase):

    CHECKER_CLASS = checker.UnicodeChecker

    def tokenize(self, source):
        return tokenize.generate_tokens(io.StringIO(source).readline)

    def test_bytes_okay(self):
        tokens = self.tokenize("b'abc'")
        with self.assertNoMessages():
            self.checker.process_tokens(tokens)

    def test_unicode_okay(self):
        tokens = self.tokenize("u'abc'")
        with self.assertNoMessages():
            self.checker.process_tokens(tokens)

    def test_native_string(self):
        arg = "val = 'abc'"
        tokens = self.tokenize(arg)
        with self.assertAddsMessages(testutils.Message('native-string', line=1)):
            self.checker.process_tokens(tokens)

    def test_future_unicode(self):
        arg = "from __future__ import unicode_literals; val = 'abc'"
        tokens = self.tokenize(arg)
        with self.assertNoMessages():
            self.checker.process_tokens(tokens)

    def test_future_unicode_after_module_docstring(self):
        module = '"""Module docstring"""\nfrom __future__ import unicode_literals'
        tokens = self.tokenize(module)
        with self.assertNoMessages():
            self.checker.process_tokens(tokens)

    def test_future_unicode_after_shebang_and_module_docstring(self):
        module = '#! /usr/bin/python2.7\n"""Module docstring"""\nfrom __future__ import unicode_literals'
        tokens = self.tokenize(module)
        with self.assertNoMessages():
            self.checker.process_tokens(tokens)


if __name__ == '__main__':
    import unittest
    unittest.main()
