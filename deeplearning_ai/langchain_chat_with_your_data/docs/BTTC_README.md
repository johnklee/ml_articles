## Common utilities used in BT testing
This package is used to hold common utilities for BT testing.

## Installation
You can install the released package from pip:

```shell
$ pip install bttc
```

or download the source then run command below to use the latest version:

```shell
$ git clone https://github.com/johnklee/bt_test_common.git
$ cd bt_test_common
$ pip install .
```

You may need `sudo` for the above commands if your system has certain permission restrictions.

## Basic Usage

### Retrieve device
You can use function `get_all` to retrieve all local connected adb devices:

```shell
$ adb devices
List of devices attached
07311JECB08252  device
36121FDJG000GR  device

$ python
>>> import bttc
>>> devices = bttc.get_all()
>>> devices['07311JECB08252'].gm.sdk
34
```

Or use function `get` to retrieve a specific device by its serial number:

```shell
>>> import bttc
>>> dut = bttc.get('07311JECB08252', {'wifi'})
>>> dut.wifi.status()
<WifiStatus.ENABLED: 'enabled'>
```

### `dut.gm`: Utility used in general operations of device.
The `dut.gm` utility, loaded automatically when you access your device, streamlines common actions like:
- Getting/setting device properties
- Searching logcat messages
- Managing airplane mode
- Taking screenshots
- Dumping system information (build number, model, etc.)
- And more!


### `dut.mc`: Utility to support common Media control operations/methods.
The `dut.mc` utility, loaded automatically when you access your device, lets you control music playback and get its current state.


## Release info
* Release v0.0.96: #425, #423, #419, #417, #407
* Release v0.0.95: #411, #409, #408, #405
* Release v0.0.94: #401, #399, #396
* Release v0.0.93: #392, #388, #389, #386, #345
* Release v0.0.92: #377, #374, #372, #370, #336
* Release v0.0.91: #356, #354
* Release v0.0.90: #346, #342, #339, #337
* Release v0.0.89: #320, #118
* Release v0.0.88: #325, #322, #319, #297
* Release v0.0.87: #314, #313, #309, #307, #304, #301, #298
* Release v0.0.86: #291, #290, #283
* Release v0.0.85: #285, #284, #280
* Release v0.0.84: #270, #274, #188
* Release v0.0.83: #266, #264, #260, #259
* Release v0.0.82: #251, #248, #245, #187
* Release v0.0.81: #237, #238, #240
* Release v0.0.80: #230
