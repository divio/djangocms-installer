# -*- coding: utf-8 -*-
import os
import sys
import shutil
import tempfile
import subprocess

if sys.version_info[:2] < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from six import StringIO


SYSTEM_ACTIVATE = os.path.join(os.path.dirname(sys.executable), 'activate_this.py')


class BaseTestClass(unittest.TestCase):
    stdout = None
    stderr = None
    project_dir = None

    def _remove_project_dir(self):
        if self.project_dir and os.path.exists(self.project_dir):
            shutil.rmtree(self.project_dir)
            self.project_dir = None

    def _create_project_dir(self):
        if os.environ.get('USE_SHM', 'no') == 'yes':
            if os.path.exists('/run/shm'):
                self.project_dir = tempfile.mkdtemp(dir='/run/shm')
            elif os.path.exists('/dev/shm'):
                self.project_dir = tempfile.mkdtemp(dir='/dev/shm')
            else:
                self.project_dir = tempfile.mkdtemp()
        else:
            self.project_dir = tempfile.mkdtemp()

    def tearDown(self):
        self._remove_project_dir()
        self.stdout = None
        self.stderr = None

    def setUp(self):
        self.stdout = StringIO()
        self.stderr = StringIO()
        self._create_project_dir()


class IsolatedTestClass(BaseTestClass):
    virtualenv_dir = None
    activate_this = ''

    def _remove_project_dir(self):
        super(IsolatedTestClass, self)._remove_project_dir()
        if self.virtualenv_dir:
            shutil.rmtree(self.virtualenv_dir)
            self.virtualenv_dir = None

    def _create_project_dir(self):
        super(IsolatedTestClass, self)._create_project_dir()
        self.virtualenv_dir = tempfile.mkdtemp()

    def tearDown(self):
        super(IsolatedTestClass, self).tearDown()
        if os.path.exists(SYSTEM_ACTIVATE):
            try:
                execfile(SYSTEM_ACTIVATE, dict(__file__=SYSTEM_ACTIVATE))
            except NameError:
                with open(SYSTEM_ACTIVATE) as f:
                    code = compile(f.read(), SYSTEM_ACTIVATE, 'exec')
                exec(code, dict(__file__=SYSTEM_ACTIVATE))
            sys.executable = os.path.join(os.path.dirname(SYSTEM_ACTIVATE), 'python')

    def setUp(self):
        super(IsolatedTestClass, self).setUp()
        if os.path.exists(SYSTEM_ACTIVATE):
            subprocess.check_call(['virtualenv', '--python=%s' % sys.executable, self.virtualenv_dir])
            activate_temp = os.path.join(self.virtualenv_dir, 'bin', 'activate_this.py')
            try:
                execfile(activate_temp, dict(__file__=activate_temp))
            except NameError:
                with open(activate_temp) as f:
                    code = compile(f.read(), activate_temp, 'exec')
                exec(code, dict(__file__=activate_temp))
            sys.executable = os.path.join(self.virtualenv_dir, 'bin', 'python')
