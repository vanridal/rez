# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the Rez Project


"""
Test package repository plugin.
"""
import unittest
import os

from rezplugins.package_repository import filesystem
from rez.packages import create_package
from rez.tests.util import TestBase, TempdirMixin
from rez.utils.platform_ import platform_


class TestFilesystemPackageRepository(TestBase, TempdirMixin):
    @classmethod
    def setUpClass(cls):
        TempdirMixin.setUpClass()

        cls.settings = dict()

    @classmethod
    def tearDownClass(cls):
        TempdirMixin.tearDownClass()

    @unittest.skipIf(platform_.name != "windows",
                     "Skipping because this issue only affects case-insensitive platforms.")
    def test_mismatching_case(self):
        """Test that we get a caught PackageRepositoryError on case-insensitive platforms."""
        pool = filesystem.ResourcePool(cache_size=None)
        pkg_repository = filesystem.FileSystemPackageRepository(self.root, pool)

        package = create_package("myTestPackage", data={})
        variant = next(package.iter_variants())
        case_mismatch_package = create_package("MyTestPackage", data={})
        case_mismatch_variant = next(case_mismatch_package.iter_variants())

        pkg_repository._create_variant(variant, overrides={})
        with self.assertRaises(filesystem.PackageRepositoryError):
            pkg_repository._create_variant(case_mismatch_variant, overrides={})

    def test_copy_variant_payload(self):
        '''Test copy_variant_payload copies a variant payload to path'''
        repo_path = os.path.join(self.root, 'repo')
        copy_target = os.path.join(self.root, 'copy_target')

        pool = filesystem.ResourcePool(cache_size=None)
        pkg_repository = filesystem.FileSystemPackageRepository(repo_path, pool)

        package = create_package("copy_test1", data={})
        variant = next(package.iter_variants())

        fs_variant = variant.install(repo_path)
        with open(os.path.join(fs_variant.root, 'payload.txt'), 'w'):
            pass

        pkg_repository.copy_variant_payload(fs_variant.resource, copy_target)

        assert os.path.isfile(os.path.join(copy_target, 'payload.txt'))

    def test_copy_variant_payload_wrong_resource(self):
        '''Test copy_variant_payload failure
        when a different repo variant resource is passed
        '''
        repo_path = os.path.join(self.root, 'repo')
        copy_target = os.path.join(self.root, 'copy_target')

        pool = filesystem.ResourcePool(cache_size=None)
        pkg_repository = filesystem.FileSystemPackageRepository(repo_path, pool)

        mem_package = create_package("copy_test2", data={})
        mem_variant = next(mem_package.iter_variants())

        with self.assertRaises(filesystem.PackageRepositoryError):
            pkg_repository.copy_variant_payload(mem_variant.resource, copy_target)

    def test_copy_variant_payload_missing_root(self):
        '''Test copy_variant_payload failure when a variant has missing root'''
        repo_path = os.path.join(self.root, 'repo')
        copy_target = os.path.join(self.root, 'copy_target')

        pool = filesystem.ResourcePool(cache_size=None)
        pkg_repository = filesystem.FileSystemPackageRepository(repo_path, pool)

        package = create_package("copy_test3", data={'variants': [['python']]})
        variant = next(package.iter_variants())

        fs_variant = variant.install(repo_path)
 
        with self.assertRaises(filesystem.PackageRepositoryError):
            pkg_repository.copy_variant_payload(fs_variant.resource, copy_target)

