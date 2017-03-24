# -*- coding: utf-8 -*-

import os.path

from PyQt5.QtCore import QTimer
from PyQt5.Qt3DCore import QEntity, QTransform
from PyQt5.Qt3DRender import QPointLight
from PyQt5.Qt3DExtras import Qt3DWindow, QCuboidMesh, QSphereMesh, QPhongMaterial
from PyQt5.QtQml import QQmlComponent, QQmlEngine

from . import util


class Animation(object):
    """
    Abstract class for setting up a 3D scene and animating it.
    """

    def __init__(self, title, frame_rate, run_time):
        """
        Create a new Animation.

        Arguments:
            title: str, the window title
            frame_rate: float, the number of frames to display per second
            run_time: float, the number of seconds to run the animation
        """
        self.title = title
        assert 0 < frame_rate < 1000
        self.frame_rate = frame_rate
        assert run_time > 0
        self.run_time = run_time

        self.frame = 0
        self.prev_update_time = None

        # import OpenGL so Qt can use it for rendering
        from OpenGL import GL
        # create the 3D window
        self.view = Qt3DWindow()

        self.view.setTitle(self.title)

        self.qml_engine = QQmlEngine(self.view)

    def load_qml(self, path, parent):
        component = QQmlComponent(self.qml_engine, path, parent)
        obj = component.create()
        if obj is None:
            print('Error loading {}'.format(path))
            for error in component.errors():
                print(error.toString())
            exit()
        return obj

    def add_light(self, position, intensity=1.0, color=util.hsl(0, 0, 100)):
        """
        Helper method to add a simple point light to the scene.

        Arguments:
            position: QVector3D, the position of the light in the scene
            intensity: float, the intensity of the light
            color: QColor, the color of the light
        """
        light_entity = QEntity(self.scene)
        light = QPointLight(light_entity)
        light.setColor(color)
        light.setIntensity(intensity)
        light_transform = QTransform(self.scene)
        light_transform.setTranslation(position)
        light_entity.addComponent(light)
        light_entity.addComponent(light_transform)

    def add_rgb_cube(self, w, h, d):
        cube_entity = QEntity(self.scene)
        cube_mesh = QCuboidMesh()
        cube_mesh.setXExtent(w)
        cube_mesh.setYExtent(h)
        cube_mesh.setZExtent(d)
        cube_entity.addComponent(cube_mesh)
        cube_transform = QTransform(self.scene)
        cube_entity.addComponent(cube_transform)
        if not hasattr(self, 'rgb_cube_material'):
            self.rgb_cube_material = self.load_qml(os.path.join(os.path.dirname(__file__), 'RGBCubeMaterial.qml'), self.scene)
        cube_entity.addComponent(self.rgb_cube_material)

        return cube_transform

    def add_sphere(self, r):
        sphere_entity = QEntity(self.scene)
        sphere_mesh = QSphereMesh()
        sphere_mesh.setRadius(r)
        sphere_entity.addComponent(sphere_mesh)
        sphere_transform = QTransform(self.scene)
        sphere_entity.addComponent(sphere_transform)
        if not hasattr(self, 'sphere_material'):
            self.sphere_material = QPhongMaterial(self.scene)
            self.sphere_material.setAmbient(util.hsl(0, 0, 50))
        sphere_entity.addComponent(self.sphere_material)

        return sphere_transform

    def setup_scene(self, background_color, camera_position, camera_lookat):
        """
        Sets up the scene. Should be called before running the animation.

        Arguments:
            background_color: QColor, background color of the scene
            camera_position: QVector3D, the position of the camera in the scene
            camera_lookat: QVector3D, the point that the camera should be pointing at in the scene
        """
        # clear color is the background color
        self.view.defaultFrameGraph().setClearColor(background_color)

        self.scene = QEntity()

        # let subclass populate scene
        self.make_scene()

        # set up camera
        camera = self.view.camera()
        camera.setPosition(camera_position)
        camera.setViewCenter(camera_lookat)

        self.view.setRootEntity(self.scene)

    def make_scene(self):
        """
        Abstract method. Populates the scene with objects.
        """
        raise NotImplementedError()

    def _update(self):
        """
        Updates the animation, rendering the next frame.
        """
        # current animation time in seconds
        t = util.lerp(self.frame, 0, self.frame_rate, 0, 1)
        # change in time since the last frame
        dt = 1 / self.frame_rate if self.prev_update_time is None else t - self.prev_update_time
        # call subclass's frame update
        self.update(self.frame, t, dt)

        # stop the animation and close the window if run past run_time
        if t >= self.run_time:
            self.animation_timer.stop()
            self.view.close()

        self.prev_update_time = t
        self.frame += 1

    def update(self, frame, t, dt):
        """
        Abstract method. Updates one frame of the animation.

        Arguments:
            frame: int, the current frame number
            t: float, the current animation time in seconds
            dt: float, the number of seconds since the last update
        """
        raise NotImplementedError()

    def run(self):
        """
        Runs the animation asynchronously. The animation runs in the background for self.run_time seconds.
        """
        self.animation_timer = QTimer(self.view)
        # timer interval in msecs
        self.animation_timer.setInterval(1000 / self.frame_rate)
        # call update on each timeout of the timer
        self.animation_timer.timeout.connect(self._update)
        self.animation_timer.start()

        # show the main window
        self.view.show()
