# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the Rez Project


"""
test package bundling
"""
import os.path
import os

from rez.resolved_context import ResolvedContext
from rez.tests.util import TestBase, TempdirMixin
from rez.bundle_context import bundle_context
from rez.bind import hello_world


class TestBundle(TestBase, TempdirMixin):
    @classmethod
    def setUpClass(cls):
        TempdirMixin.setUpClass()

        cls.packages_path = os.path.join(cls.root, "packages")
        cls.dest_bundle_root = os.path.join(cls.root, "bundle")
        cls.update_bundle_root = os.path.join(cls.root, "update_bundle")

        os.makedirs(cls.packages_path)
        hello_world.bind(cls.packages_path)

        cls.settings = dict(
            packages_path=[cls.packages_path],
            package_filter=None,
            implicit_packages=[],
            warn_untimestamped=False,
            resolve_caching=False)

    @classmethod
    def tearDownClass(cls):
        TempdirMixin.tearDownClass()

    def test_create_bundle(self):
        context = ResolvedContext(["hello_world"])
        bundle_context(
            context=context,
            dest_dir=self.dest_bundle_root,
            quiet=True,
        )
        # Check that the bundle directory exists
        self.assertTrue(os.path.exists(self.dest_bundle_root))
        # Check that the context.rxt file exists in the bundle
        context_file = os.path.join(self.dest_bundle_root, "context.rxt")
        self.assertTrue(os.path.isfile(context_file))
        # Check that the package repository exists
        package_repo = os.path.join(self.dest_bundle_root, "packages")
        self.assertTrue(os.path.isdir(package_repo))
        # Finally load the context to be sure
        ResolvedContext.load(context_file)

    def test_update_bundle(self):
        from rez.version import Version

        packages_path = self.data_path("solver", "packages")
        context_file = os.path.join(self.update_bundle_root, "context.rxt")

        context = ResolvedContext(["python-2.6.8"], package_paths=[packages_path])
        bundle_context(
            context=context,
            dest_dir=self.update_bundle_root,
            quiet=True,
        )
        old_bundle = ResolvedContext.load(context_file)
        self.assertEqual(
            old_bundle.resolved_packages[0].parent.version,
            Version('2.6.8')
        )

        new_context = ResolvedContext(["python-2.7.0"], package_paths=[packages_path])
        bundle_context(
            context=new_context,
            dest_dir=self.update_bundle_root,
            quiet=True,
            update=True
        )

        new_bundle = ResolvedContext.load(context_file)
        self.assertEqual(
            new_bundle.resolved_packages[0].parent.version,
            Version('2.7.0')
        )
