#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
from location.srv import *
from location.msg import Location
from tf.msg import tfMessage
import time
from rviz_marker import RvizMarker
import os
import rospkg
from std_msgs.msg import String


class LocationManager:

    def __init__(self):
        rospy.init_node('navigation', anonymous=False)

        rospy.Service("/location/register_current_location", RegisterLocation, self.register_current_location)
        rospy.Service("/location/request_location", RequestLocation, self.request_location)
        rospy.Service("/location/request_current_location", RequestCurrentLocation, self.request_current_location)
        rospy.Service("/location/request_location_list", RequestLocationList, self.request_location_list)
        rospy.Subscriber("/tf", tfMessage, self.subscribe_location_tf)
        rospy.Subscriber("/location/save_location", String, self.save_location)
        rospy.Subscriber("/location/load_location", String, self.load_location)

        self.location = None
        self.locations = {}
        info_file = rospy.get_param("{}/info_file".format(rospy.get_name()), None)
        self.rviz = RvizMarker()

        rospy.sleep(0.5)

        if info_file is not None:
            path = "{}/location/{}".format(rospkg.RosPack().get_path("location"), info_file)
            if os.path.exists(path):
                self.load_info_file(path)
        rospy.spin()

    def save_location(self, message):
        # type: (String) -> None
        """
        ROS Subscriber関数
        Subscriberで送られてきたテキストファイル名で場所情報を保存する
        :param message: Stringメッセージ
        :return:
        """
        file_name = "{}/location/{}".format(rospkg.RosPack().get_path("location"), message.data)
        print("***** Save Location *****")
        print("-> {}".format(file_name))
        with open(file_name, "w") as f:
            for key in self.locations.keys():
                print(key, self.locations[key])
                location = self.locations[key]
                f.write("{}:{},{},{}\n".format(location.name, location.x, location.y, location.z))

    def load_location(self, message):
        # type: (String) -> None
        """
        場所情報のファイルからデータを読み込む
        :return:
        """
        file_name = "{}/location/{}".format(rospkg.RosPack().get_path("location"), message.data)
        self.load_info_file(file_name)

    def load_info_file(self, path):
        # type: (str) -> None
        """
        場所情報のファイルからデータを読み込む
        :return:
        """
        print("***** Load Location *****")
        print("<- {}".format(path))
        with open(path, "r") as f:
            for line in f:
                datas = line.split(":")
                name = datas[0]
                data = list(map(float, datas[1].split(",")))
                location = Location(name, data[0], data[1], data[2])
                self.locations[name] = location
                self.rviz.register(location)

    def subscribe_location_tf(self, message):
        # type: (tfMessage) -> None
        """
        現在位置を取得し続ける
        :param message:
        :return:
        """
        for transform in message.transforms:
            if transform.header.frame_id == "odom" and transform.child_frame_id == "base_footprint":
                translation = transform.transform.translation
                self.location = (translation.x, translation.y, translation.z)


    def register_current_location(self, message):
        # type: (RegisterLocationRequest) -> RegisterLocationResponse
        """
        ROSサービスサーバー関数
        送られてきた名前で現在位置を登録
        :param message: Stringサービスメッセージ
        :return: サービスレスポンス
        """
        for i in range(10):
            if self.location is not None:
                self.register_location(message.name, self.location)
                break
            time.sleep(0.5)
        return RegisterLocationResponse()

    def register_location(self, name, location):
        # type: (str, (float, float, float)) -> None
        """
        指定の名前と座標で登録処理を行う
        :param name: 座標名
        :param location: 座標
        :return:
        """
        print("Register: {} {}".format(name, location))
        data = Location(name, location[0], location[1], location[2])
        self.locations[name] = data
        self.rviz.register(data)

    def request_location(self, request):
        # type: (RequestLocationRequest) -> RequestLocationResponse
        """
        ROSサービスサーバー関数
        送られてきた名前の座標を返す
        :param request: 座標の登録名
        :return: 指定の名前の座標が存在しない場合はNONEで返す
        """
        result = self.locations.get(request.name)
        return RequestLocationResponse(result)

    def request_current_location(self, request):
        # type: (RequestCurrentLocationRequest) -> RequestCurrentLocationResponse
        """
        ROSサービスサーバー関数
        現在の場所を返す
        :param request:
        :return:
        """
        if self.location is not None:
            return RequestCurrentLocationResponse(
                Location("Current_location", self.location[0], self.location[1], self.location[2]))
        else:
            return RequestCurrentLocationResponse()

    def request_location_list(self, request):
        # type: (RequestLocationListRequest) -> RequestLocationListResponse
        """
        ROSサービスサーバー関数
        登録されているすべての場所情報を送る
        :param request: 引数指定ないのでゴミ
        :return: すべての場所情報
        """
        result = list(self.locations.values())
        return RequestLocationListResponse(result)


if __name__ == "__main__":
    LocationManager()
