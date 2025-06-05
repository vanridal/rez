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


class TestBundle(TestBase, TempdirMixin):
    @classmethod
    def setUpClass(cls):
        TempdirMixin.setUpClass()

        cls.packages_path = cls.data_path("solver", "packages")
        cls.dest_bundle_root = os.path.join(cls.root, "bundles")
        os.makedirs(cls.dest_bundle_root)

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
        context = ResolvedContext(["nada"])
        bundle_root = os.path.join(self.dest_bundle_root, 'test1')
        bundle_context(
            context=context,
            dest_dir=bundle_root,
            quiet=True,
        )
        # Check that the bundle directory exists
        self.assertTrue(os.path.exists(bundle_root))
        # Check that the context.rxt file exists in the bundle
        context_file = os.path.join(bundle_root, "context.rxt")
        self.assertTrue(os.path.isfile(context_file))
        # Check that the package repository exists
        package_repo = os.path.join(bundle_root, "packages")
        self.assertTrue(os.path.isdir(package_repo))
        # Finally load the context to be sure
        ResolvedContext.load(context_file)

    def test_update_bundle(self):
        from rez.version import Version

        bundle_root = os.path.join(self.dest_bundle_root, 'test2')
        context_file = os.path.join(bundle_root, "context.rxt")

        context = ResolvedContext(["python-2.6.8"])
        bundle_context(
            context=context,
            dest_dir=bundle_root,
            quiet=True,
        )
        old_bundle = ResolvedContext.load(context_file)
        self.assertEqual(
            old_bundle.resolved_packages[0].parent.version,
            Version('2.6.8')
        )

        context = ResolvedContext(["python-2.7.0"])
        bundle_context(
            context=context,
            dest_dir=bundle_root,
            quiet=True,
            update=True
        )

        new_bundle = ResolvedContext.load(context_file)
        self.assertEqual(
            new_bundle.resolved_packages[0].parent.version,
            Version('2.7.0')
        )

    def test_update_bundle_check_removal(self):
        # check python package is removed
        bundle_root = os.path.join(self.dest_bundle_root, 'test3')
        context_file = os.path.join(bundle_root, "context.rxt")
        # requires python-2.6.8
        context = ResolvedContext(["pysplit-6"])
        bundle_context(
            context=context,
            dest_dir=bundle_root,
            quiet=True
        )

        self.assertTrue(os.path.isdir(os.path.join(bundle_root, 'packages', 'python', '2.6.8')))
        # requires python-2.7
        context = ResolvedContext(["pysplit-7"])
        bundle_context(
            context=context,
            dest_dir=bundle_root,
            quiet=True,
            update=True
        )
        # python-2.6.8 should be removed
        self.assertFalse(os.path.isdir(os.path.join(bundle_root, 'packages', 'python', '2.6.8')))
        # python-2.7.0 should exist
        self.assertTrue(os.path.isdir(os.path.join(bundle_root, 'packages', 'python', '2.7.0')))

        # no python required
        context = ResolvedContext(["nada"])
        # python should exist from before
        self.assertTrue(os.path.isdir(os.path.join(bundle_root, 'packages', 'python')))
        bundle_context(
            context=context,
            dest_dir=bundle_root,
            quiet=True,
            update=True
        )
        # python family folder should not exist
        self.assertFalse(os.path.isdir(os.path.join(bundle_root, 'packages', 'python')))

        # python should not be in context
        new_bundle = ResolvedContext.load(context_file)
        for pkg in new_bundle.resolved_packages:
            self.assertNotEqual(pkg.parent.name, 'python')
