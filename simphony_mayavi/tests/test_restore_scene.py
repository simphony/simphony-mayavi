import os
import shutil
import tempfile
import unittest
from contextlib import closing
from collections import Iterable

from PIL import Image

import numpy
from mayavi.sources.vtk_data_source import VTKDataSource
from mayavi.modules.iso_surface import IsoSurface
from mayavi.modules.text3d import Text3D
from mayavi.tests import datasets

from mayavi import mlab

from simphony_mayavi.restore_scene import restore_scene


def finally_mlab_close(func):
    ''' Ensure that at the end of calling a function
    any mayavi scene opened are closed '''
    def new_func(*args, **kwargs):
        try:
            func(*args, **kwargs)
        finally:
            mlab.close(all=True)
    return new_func


class TestRestoreScene(unittest.TestCase):

    @finally_mlab_close
    def setUp(self):
        # set up source
        sgrid = datasets.generateStructuredGrid()
        source = VTKDataSource(data=sgrid)

        self.engine = mlab.get_engine()

        # set up scene, first scene is empty
        # second scene has the settings we want to restore
        self.engine.new_scene()
        self.engine.new_scene()

        # add source
        self.engine.add_source(source)

        # add more modules
        self.engine.add_module(IsoSurface())
        self.engine.add_module(Text3D())
        self.modules = source.children[0].children

        # set camera
        self.view = (25., 14., 20., [0., 0., 2.5])
        mlab.view(*self.view)

        # save the visualisation
        self.temp_dir = tempfile.mkdtemp()
        self.filename = os.path.join(self.temp_dir, "test_vis.mv2")
        self.engine.save_visualization(self.filename)

        # save the scene as an image for comparison later
        self.ref_saved_filename = os.path.join(self.temp_dir, "ref_saved.png")
        mlab.savefig(self.ref_saved_filename)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    @finally_mlab_close
    def test_restore_scene(self):
        # create a new scene with new data source
        self.engine.new_scene()
        sgrid_2 = datasets.generateStructuredGrid()
        source = VTKDataSource(data=sgrid_2)
        self.engine.add_source(source)

        # when
        restore_scene(self.filename, scene_index=1)

        # then
        modules = source.children[0].children

        self.check_items_same_types(modules, self.modules)
        self.check_items_not_same_object(modules, self.modules)
        self.check_camera_view(mlab.view(), self.view)

        # save the scene to a file
        saved_filename = os.path.join(self.temp_dir, "test_restore.png")
        mlab.savefig(saved_filename)

        # compare the pixels to the desired one
        self.check_images_almost_identical(saved_filename,
                                           self.ref_saved_filename)

    @finally_mlab_close
    def test_pass_restore_scene_with_extra_sources(self):
        # create a new scene
        self.engine.new_scene()

        # add two data sources
        for _ in range(2):
            sgrid_2 = datasets.generateStructuredGrid()
            source = VTKDataSource(data=sgrid_2)
            self.engine.add_source(source)

        # when
        restore_scene(self.filename, scene_index=1)

        # then
        # only the first source is restored
        source = self.engine.current_scene.children[0]
        modules = source.children[0].children

        self.check_items_same_types(modules, self.modules)
        self.check_items_not_same_object(modules, self.modules)
        self.check_camera_view(mlab.view(), self.view)

        # save the scene to a file
        saved_filename = os.path.join(self.temp_dir, "test_extra.png")
        mlab.savefig(saved_filename)

        # compare the pixels to the desired one
        self.check_images_almost_identical(saved_filename,
                                           self.ref_saved_filename)

    @finally_mlab_close
    def test_pass_restore_scene_with_different_source(self):
        # create a new scene
        self.engine.new_scene()

        # add two data sources
        sgrid_2 = datasets.generateUnstructuredGrid_mixed()
        source = VTKDataSource(data=sgrid_2)
        self.engine.add_source(source)

        # when
        restore_scene(self.filename, scene_index=1)

        # then
        modules = source.children[0].children

        # the data content is different
        # but the modules should be there anyway
        self.check_items_same_types(modules, self.modules)
        self.check_items_not_same_object(modules, self.modules)
        self.check_camera_view(mlab.view(), self.view)

    @finally_mlab_close
    def test_pass_restore_empty_scene(self):
        # create a new scene
        self.engine.new_scene()
        sgrid_2 = datasets.generateStructuredGrid()
        source = VTKDataSource(data=sgrid_2)
        self.engine.add_source(source)

        # when
        # first scene is empty
        restore_scene(self.filename, scene_index=0)

        # then
        # save the scene to a file
        saved_filename = os.path.join(self.temp_dir, "test_extra.png")
        mlab.savefig(saved_filename)

        # compare the pixels to the desired one
        self.check_images_empty(saved_filename)

    def check_camera_view(self, actual_view, desired_view):
        for this_view, ref_view in zip(actual_view, desired_view):
            if isinstance(this_view, Iterable):
                self.assertItemsEqual(this_view, ref_view)
            else:
                self.assertEqual(this_view, ref_view)

    def check_items_same_types(self, actual_items, desired_items):
        for actual, desired in zip(actual_items, desired_items):
            self.assertEqual(type(actual), type(desired))

    def check_items_not_same_object(self, actual_items, other_items):
        for actual, other in zip(actual_items, other_items):
            self.assertNotEqual(actual, other)

    def check_images_empty(self, image_file):
        '''Check if the image in `image_file` is blank'''

        with closing(Image.open(image_file)) as image_fp:
            image = numpy.array(image_fp)

            msg = "Image is not empty, min:{}, max:{}"
            self.assertAlmostEqual(image.min(), image.max(), places=3,
                                   msg=msg.format(image.min(), image.max()))

    def check_images_almost_identical(self, actual_file, desired_file):
        ''' Check if two images are almost identical (within 5% error)'''
        with closing(Image.open(actual_file)) as actual_fp, \
             closing(Image.open(desired_file)) as desired_fp:  # noqa

            actual = numpy.array(actual_fp)
            desired = numpy.array(desired_fp)
            err = float(numpy.abs(actual-desired).sum())/desired.sum()*100.

            message = "Actual image is not close to the desired, error: {}%"
            self.assertTrue(err < 5., message.format(err))
