## Preface
The `wifi_utils` module provides functions for basic WiFi operations, such as retrieving SSID and establishing connections.

## Usage
The `bttc.wifi_utils.WiFiModule` class isn't binded automatically when you retrieve a
device using the `bttc.get()` function. So we have to bind this utility
manually. For example:
```python
# Import the package `bttc`
>>> import bttc

# Retrieve your device. Please replace '36121FDJG000GR' with your device's
# serial number.
>>> dut = bttc.get('36121FDJG000GR')

# Binds the DUT to the WiFi utility.
>>> from bttc import wifi_utils
>>> wifi_utils.bind(dut)
<AndroidDevice|36121FDJG000GR>
>>> dut.wifi
<bttc.wifi_utils.WiFiModule object at 0x7f8f3248fe10>
```

### Get SSID of WiFi
SSID stands for Service Set Identifier. In simpler terms, it's the name of your Wi-Fi network.

With help of `bttc` package, we can retrieve this value easily. For example:
```python
# Import the necessary packages.
>>> import bttc
>>> from bttc import wifi_utils

# Retrieves DUT object and binds it to WiFi utility.
>>> dut = bttc.get('36121FDJG000GR')
>>> wifi_utils.bind(dut)
<AndroidDevice|36121FDJG000GR>

# Get SSID name
>>> dut.wifi.ssid_name
'GoogleGuest-IPv4'
```

If DUT's wifi is enabled, you will get exception when accessing SSID:
```python
# Disable the WiFi
>>> dut.wifi.disable()

# Exception will be thrown in accessing SSID when WiFi is disabled.
>>> dut.wifi.ssid_name
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/usr/local/google/home/johnkclee/Github/bt_test_common/bttc/wifi_utils.py", line 56, in ssid_name
    return get_ssid_name(self._ad)
           ^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/google/home/johnkclee/Github/bt_test_common/bttc/wifi_utils.py", line 206, in get_ssid_name
    raise errors.AdbExecutionError(
bttc.errors.AdbExecutionError: >>> Check if Wifi is enabled! <<<

    Failed in adb execution with return code=255:

# Enable the WiFi
>>> dut.wifi.enable()

# SSID name can be obtained successfully.
>>> dut.wifi.ssid_name
'GoogleGuest-IPv4'
```

### Connect WiFi
We could leverage method `dut.wifi.login` to login WiFi. For example:
```python
# Import the necessary packages.
>>> import bttc
>>> from bttc import wifi_utils

# Retrieves DUT object and binds it to WiFi utility.
>>> dut = bttc.get('36121FDJG000GR')
>>> wifi_utils.bind(dut)
<AndroidDevice|36121FDJG000GR>

# Connect WiFi `Pixel_john` with password as `john1234`
>>> dut.wifi.login('Pixel_john', 'john1234')
WARNING:root:Wifi is not connected!
WARNING:root:Under scanning...retry=1
WARNING:root:Under scanning...retry=2
WARNING:root:Under scanning...retry=3
WARNING:root:Under scanning...retry=4
WARNING:root:Under scanning...retry=5
WARNING:root:Under scanning...retry=6
WARNING:root:Under scanning...retry=7
WARNING:root:Under scanning...retry=8
True
```
