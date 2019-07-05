#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import rospy
from location.msg import Location
from location.srv import *
from std_msgs.msg import String, Header, ColorRGBA
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Pose, Vector3, Point, Quaternion
import csv
import os

class Data:
    def __init__(self, location, markers):
        # type: (Location, Marker) -> None
        self.location = location
        self.markers = markers


class RvizMarker:

    def __init__(self):
        # type: (dict) -> None
        self.locations = {}
        self.marker_id = 0
        self.frame_id = "odom"
        self.ns = "location_markers"

        self.publisher = rospy.Publisher("location/marker", Marker, queue_size=10)

    def create_marker(self, message):
        # type: (Location) -> (Marker, Marker)
        """
        Rvizで表示するマーカーの作成を行う
        :param message:
        :return:
        """
        r = random.random()
        g = random.random()
        b = random.random()
        scale = Vector3(0.5, 0.5, 0.5)

        marker_str = Marker()
        marker_str.header.stamp = rospy.Time.now()
        marker_str.header.frame_id = self.frame_id
        marker_str.ns = self.ns
        marker_str.id = self.marker_id
        marker_str.type = Marker.TEXT_VIEW_FACING
        marker_str.text = message.name
        marker_str.action = Marker.ADD
        marker_str.pose.position = Point(message.x, message.y, 0.5)
        marker_str.scale = scale
        marker_str.color = ColorRGBA(r, g, b, 1)
        self.marker_id += 1

        marker_sphere = Marker()
        marker_sphere.header.stamp = rospy.Time.now()
        marker_sphere.header.frame_id = self.frame_id
        marker_sphere.ns = self.ns
        marker_sphere.id = self.marker_id
        marker_sphere.type = Marker.SPHERE
        marker_sphere.action = Marker.ADD
        marker_sphere.pose.position = Point(message.x, message.y, 0)
        marker_sphere.scale = scale
        marker_sphere.color = ColorRGBA(r, g, b, 0.5)
        self.marker_id += 1
        print(self.marker_id)

        return [marker_sphere, marker_str]

    def register(self, message):
        # type: (Location) -> None
        """
        Rvizに表示するデータを保存し、Rvizにも認識出来る形でPublishする
        :param message: 場所データ
        :return: なし
        """
        print("[Register] %s (%s %s)" % (message.name, message.x, message.y))
        markers = self.create_marker(message)
        self.locations[message.name] = Data(message, markers)
        for marker in markers:
            self.publisher.publish(marker)

    def delete(self, message):
        # type: (String) -> None
        """
        登録されたデータを消す
        ただし、保存されていない場合は警告だけして無視
        :param message: 場所名
        :return: なし
        """
        if message.data in self.locations:
            data = self.locations.get(message.data)
            if data is None:
                print("[UNREGISTERED] {}".format(data.location.name))
                return
            print("[Delete] {} ({}, {})".format(data.location.name, data.x, data.y))
            for marker in data.markers:
                marker.action = Marker.DELETE
                self.publisher.publish(marker)
