import os
import sys
from contextlib import contextmanager
from io import StringIO
from unittest import TestCase
from unittest.mock import (
    MagicMock,
    patch,
)
from util.rate_limit import rate_limit


@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


@contextmanager
def set_env(**environ):
    old_environ = dict(os.environ)
    os.environ.update(environ)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old_environ)


class RateLimitTests(TestCase):
    START_TIME = 1511561555.138444

    @patch('util.rate_limit.time.time')
    def test_rate_limiting(self, time_mock: MagicMock) -> None:
        @rate_limit('_f', once_every=3600)
        def _f():
            _f.counter += 1
        _f.counter = 0

        time_mock.return_value = self.START_TIME
        _f()
        self.assertEquals(_f.counter, 1)
        _f()
        self.assertEquals(_f.counter, 1)

        time_mock.return_value += 1800
        _f()
        self.assertEquals(_f.counter, 1)

        time_mock.return_value += 1800
        _f()
        self.assertEquals(_f.counter, 2)

