# location
## Overview
場所情報を管理するパッケージ。

## Usage

```
roslaunch location location.launch
```

## Node
**`name` location**

### Service

* **`/location/register_current_location`** 現在位置の登録 ( location/RegisterLocation )

* **`/location/request_location`** 登録場所の要求 ( location/RequestLocation )

* **`/location/request_current_location`** 現在の場所を要求 ( location/RequestCurrentLocation )

* **`/location/request_location_list`** 登録されているすべての場所の情報を要求 ( location/RequestLocationList )


### msg
Location.msg

    string name
    float64 x
    float64 y
    float64 z

### srv
RegisterLocation.srv

    string name
    ---
RequestLocation.srv

    string name
    ---
    Location location
RequestCurrentLocation.srv

    ---
    Location location
RequestLocationList.srv

    ---
    Location[] locations