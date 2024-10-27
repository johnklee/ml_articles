## Preface
The `general_utils` module provides utility functions for common opersations on
device such as dump the bugreport file, take snapshoot of screen etc. Below are
some key functionalities supported in this module:
* **Device configuration**: Manipulating device settings such as airplane mode and volume levels.
* **System properties**: Reading and modifying system properties (e.g., SIM operator).
* **Logcat filtering**: Extracting relevant logcat entries based on timestamps or keywords.
* **Analysis operations**: Bugreport generation, screenshots, file transfer (push/pull).

## Usage
The `bttc.general_utils.GModule` class is automatically loaded when you connect
to a device using the `bttc.get()` function.  This provides a convenient way to
interact with your device's general utilities.  For example:

```python
# Import the package `bttc`
>>> import bttc

# Retrieve your device. Please replace '36121FDJG000GR' with your device's
# serial number.
>>> dut = bttc.get('36121FDJG000GR')

>>> dut.gm
<bttc.general_utils.GModule object at 0x7f0692ce5c90>
```

Then You can execute supported operations through the device's `gm` attribute to
dump bugreport, access device's properties etc.

### Enable/disable Airplane mode
There are two ways to disable/enable Airplane mode. The first approach is to
setup this setting by attribute `dut.gm.airplane_mode`. e.g.:
```python
# Current Airplane mode is off
>>> dut.gm.airplane_mode
False

# Enable Airplane mode
>>> dut.gm.airplane_mode = True
>>> dut.gm.airplane_mode
True

# Disable Airplane mode
>>> dut.gm.airplane_mode = False
>>> dut.gm.airplane_mode
False
```

Another way to do the setup of Airplane mode, is by methods
`dut.gm.enable_airplane_mode` and `dut.gm.disable_airplane_mode`. For example:
```python
# Current Airplane mode is off
>>> dut.gm.airplane_mode
False

# Enable Airplane mode
>>> dut.gm.enable_airplane_mode()
>>> dut.gm.airplane_mode
True

# Disable Airplane mode
>>> dut.gm.disable_airplane_mode()
>>> dut.gm.airplane_mode
False
```

### Dump information of system services
`dumpsys` is a powerful tool on Android devices that provides detailed information about various system services. You can access this information using the Android Debug Bridge (ADB) from the command line. For more details, refer to [the Android developer documentation on dumpsys](https://developer.android.com/tools/dumpsys)

The `bttc` library simplifies `dumpsys` access for Bluetooth diagnostics. You can use the `dut.gm.dumpsys()` method to retrieve information about the Bluetooth service on your device.

#### Example: Previewing Bluetooth Information
Since the full Bluetooth dump can be quite lengthy, you can preview a portion of it to get an overview:
```python
# Dump information of Bluetooth service and get front most 100 characters.
>>> dut.gm.dumpsys()[:100]
# Output (example):
# Bluetooth Status
#   enabled: true
#   state: ON
#   address: XX:XX:XX:XX:D4:21
#   name: Pixel 8 Pro
#   time...
...
```


#### Example: Retrieving Bluetooth SCO Status
To determine the status of Bluetooth SCO (Synchronous Connection Oriented) on your device, you can use the method `dut.gm.dumpsys` command combined with the `grep_argument` parameter. For example:
```python
>>> dut.gm.dumpsys(grep_argument='isBluetoothScoOn')
'  AudioManager.isBluetoothScoOn(): false\n'
```
The output indicates whether SCO is on (`true`) or off (`false`).

#### Dump information of other service
For default value of input argument `service` is `bluetooth_manager`. You can
change this argument to dump information of other service.

### Logcat message search
Logcat is a command-line tool on Android devices that continuously outputs system messages, including stack traces when the device throws an error and messages explicitly written from applications or parts of the system ([more](https://developer.android.com/tools/logcat)).

#### Example: Capturing Logcat Output for a Specific Duration
The `dut.gm.follow_logcat_within` method allows you to capture a continuous stream of logcat messages for a specified duration. The following example demonstrates how to collect logcat messages for 5 seconds:
```python
# Import the package BTTC and retrieve the device `dut`.
>>> import bttc; dut = bttc.get('36121FDJG000GR')

# Collect logcat message for 5 seconds.
>>> logcat_5s_messages = []
>>> for line in dut.gm.follow_logcat_within(time_sec=5):
...   logcat_5s_messages.append(line)
...

# Print the front five lines of collected logcat message.
>>> print('\n'.join(logcat_5s_messages[:5]))
05-25 16:18:57.200   934 10125 I WifiHAL : Creating message to get link statistics; iface = 47
05-25 16:18:57.221 32660 24478 I NearbyConnections: Found BleAdvertisement [ 0x23 0x38 0x4d 0x55 0x43 0x11 0x32 0x62 0xdf 0x20 0x08 0x1c 0x64 0xd7 0x51 0x43 0x9a 0x0f 0x58 0xd3 0x9e 0x25 0xc3 ] (with EndpointId 8MUC and EndpointInfo [ 0x32 0x62 0xdf 0x20 0x08 0x1c 0x64 0xd7 0x51 0x43 0x9a 0x0f 0x58 0xd3 0x9e 0x25 0xc3 ])
05-25 16:18:57.222 32660 24478 I NearbyConnections: Unable to record discovered endpoint due to null currentDiscoveryPhase
05-25 16:18:57.222 32660 24478 I NearbyConnections: ClientProxy(150399881) reporting onEndpointFound(8MUC)
05-25 16:18:57.226 32660 24478 I NearbyConnections: ClientProxy(150399881) reporting onEndpointDistanceChanged(8MUC, UNKNOWN)
```

#### Example: Capturing Logcat Output Until Meeting Certain Criteria
If you define a method to decide when to terminate the collection of logcat
message. To demonstrate this feature, below we define a method to detect if the
message of logcat contains keyword `Bluetooth is disabled` or not:
```python
>>> def stop_when_bt_disabled(line):
...   return line is not None and'Bluetooth is disabled' in line
...
>>> line = r'05-25 16:33:25.076 32660 26029 I NearbySharing: Bluetooth is disabled [CONTEXT service_id=194 ]'
>>> stop_when_bt_disabled(line)
True
>>> stop_when_bt_disabled('other line')
False
```

Then we could start collect logcat message until we see the line contains
keyword `Bluetooth is disabled`:
```python
# Show the logcat message continuously until we encounter the line which
# contains keyword `Bluetooth is disabled`
>>> for line in dut.gm.follow_logcat(stop_callback=stop_when_bt_disabled):
...     print(line)
```

Then you will start seeing that the logcat message is printing on the console
continuously. Next, you could enable and disable the Bluetooth of DUT as below:
```shell
husky:/ # cmd bluetooth_manager enable
BluetoothShellCommand: Exec enable
enable: Success
husky:/ # cmd bluetooth_manager disable
BluetoothShellCommand: Exec disable
disable: Success
```

Then you should observe that the printing is stopped and so for the logcat
message collection. Below is one of the execution example:
```
05-25 16:53:18.295 18474 18534 E headsetCtxPrv: isBluetoothCarDevice(): Null device
05-25 16:53:18.296 18474 18534 I BrdcstRcvrMsgr: sendMessage(): received broadcast id:61 with action:android.bluetooth.adapter.action.STATE_CHANGED
05-25 16:53:18.297 32660 28250 I NearbySharing: Bluetooth is disabled [CONTEXT service_id=194 ]
>>>
```
As expected, the liast line contains the keyword `Bluetooth is disabled` which
trigger the logcat message collection to stop.

#### Example: Capture the connection failure reason
When the DUT failed to pair with BT device, we could use below sample code to
extract the reason of connection failure:

```python
# Import BTTC package and obtain the DUT instance.
>>> import bttc
>>> dut = bttc.get('36121FDJG000GR', init_sl4a=True)

# In the beginning, ensure we don't have any connection failure record.
>>> start_time = dut.gm.device_time
>>> dut.gm.logcat_filter(start_time, 'OnConnectFail')
''

# Try to pair HS which won't succeed
>>> dut.gm.logcat_filter(start_time, 'OnConnectFail')
'07-09 10:37:28.876 29777 29802 W droid.bluetooth: system/main/shim/acl.cc:1693 OnConnectFail: Connection failed classic remote:xx:xx:xx:xx:bb:33 reason:PAGE_TIMEOUT(0x04)\n'

# Get failed reason
>>> from bttc.utils import logcat
>>> logcat.get_connection_fail_reason(dut, start_time)
'PAGE_TIMEOUT(0x04)'
```
The reason `PAGE_TIMEOUT` means that the DUT (phone) sent the pairing request
and got no reponse from the BT device. For more about it, refer to b/302407684

* **`PAGE_TIMEOUT`**: Page timeout indicates the remote is not connectable after repeated link layer requests within the timeframe set forth by the Android phone.
```
2.4 PAGE TIMEOUT (0x04)
The Page Timeout error code indicates that a page timed out because of the
Page Timeout configuration parameter. This error code may occur only with the
HCI_Remote_Name_Request and HCI_Create_Connection commands.
```

#### Example: Update logcat service with desired launched arguments
By default, the [Mobly logcat service](https://github.com/google/mobly/blob/master/mobly/controllers/android_device_lib/services/logcat.py) outputs logcat messages to the file path specified by `dut.adb_logcat_file_path`. However, the default arguments for the logcat command do not include UI events. To capture these events, you can provide custom arguments to the logcat command, as shown in the following example:

```python
# Initialize the Android device (`dut`):
>>> import bttc
>>> dut = bttc.get('36121FDJG000GR', init_tl4a=True)

# Display the file path where logcat messages are saved:
>>> dut.adb_logcat_file_path
'/tmp/logs/AndroidDevice36121FDJG000GR/logcat,36121FDJG000GR,husky,10-16-2024_14-03-06-796.txt'

# Get the current device time to use as the search start time:
>>> logcat_search_start_device_time = dut.gm.device_time

# Perform some UI actions. By default, the output logcat messages
# will not include UI events:
>>> dut.gm.logcat_filter(logcat_search_start_device_time, 'sysui_multi_action')
''

# Update the logcat arguments to include UI events. The `-b` option
# specifies which buffers to read:
>>> dut.gm.update_logcat_service(logcat_params='-b system -b events -b main')

# Perform some UI actions. This time, the logcat output will include
# the UI events:
>>> dut.gm.logcat_filter(logcat_search_start_device_time, 'sysui_multi_action')
'10-16 13:48:34.783  2093  2093 I sysui_multi_action: [757,803,799,panel_open,802,1]\n...'
```


### Get the current UI activity class
You can determine the active Android activity using ADB shell commands or the bttc library.

From adb, we could leverage below command to get the current UI activity class:
```shell
$ adb shell "dumpsys activity activities | grep ResumedActivity"
    topResumedActivity=ActivityRecord{c8e7d1a u0 com.google.devtools.mobileharness.platform.android.app.binary.devicedaemon.v2/.DaemonActivity t637}
  ResumedActivity: ActivityRecord{c8e7d1a u0 com.google.devtools.mobileharness.platform.android.app.binary.devicedaemon.v2/.DaemonActivity t637}
```

The bttc library offers two convenient ways to access the current activity.

Firstly, we can call method `dut.gm.get_current_activity()` to get it. e.g.:
```python
>>> dut.gm.get_current_activity()
ActivityRecord(full_activity_path='com.google.devtools.mobileharness.platform.android.app.binary.devicedaemon.v2/.DaemonActivity')
```

Alternatively, use the `dut.gm.current_activity` property to directly access the current activity:
```python
>>> dut.gm.current_activity
ActivityRecord(full_activity_path='com.google.devtools.mobileharness.platform.android.app.binary.devicedaemon.v2/.DaemonActivity')
```

### Get the SIM loaded status
You can obtain the SIM loaded status in bttc library through method `is_sim_state_loaded`:
```python
# Please replace `36121FDJG000GR` with the serial number of your device.
>>> import bttc; dut = bttc.get('36121FDJG000GR')
>>> dut.gm.is_sim_state_loaded()
False
```
The returned `False` indicates that DUT isn't loaded with SIM card.

Even more convenient way is that you can access the property `sim_loaded` to achieve
same purpose:
```python
>>> dut.gm.sim_loaded
False
```

### Capturing Device Screenshots
You can easily take screenshots of your device's screen using the `dut.gm.take_screenshot` method. This method saves the screenshot to a file and provides options for specifying the file name and location. e.g.:

```python
# Take screenshot of device and save it in path `/tmp/test.png`
>>> dut.gm.take_screenshot(host_destination='/tmp/', file_name='test.png')
'/tmp/test.png'

# Take screenshot and let method to pickup a random name to save.
# The file name will be returned for reference.
>>> dut.gm.take_screenshot(host_destination='/tmp/')
'/tmp/screenshot_05-25-2024_20-27-42.png'
```

### Get the device time
We can call method `dut.gm.get_device_time()` to get the current device time.
e.g.:
```python
>>> dut.gm.get_device_time()
'05-25 19:29:34.000'
```

Alternatively, access the `dut.gm.device_time` property can work the same way:
```python
>>> dut.gm.device_time
'05-25 19:31:56.000'
```

### Retrieving the current UI Layout as XML
To dump the xml descriptor of current UI activity, you could call method `dut.gm.get_ui_xml`. e.g.:

You can obtain the XML layout descriptor of the currently active Android UI using the `dut.gm.get_ui_xml` method. This method retrieves the XML content and saves it to a file. e.g.:
```python
# Dump the UI xml descriptor to file `/tmp/test.xml`
>>> xml_content = dut.gm.get_ui_xml(xml_out_file_path='/tmp/test.xml')

# Preview the first 50 characters
>>> print(xml_content[:50])
<?xml version='1.0' encoding='UTF-8' standalone='y

# Verify file contents (optional)
>>> with open('/tmp/test.xml', 'r') as fo:
...   print(fo.read()[:50])
...
<?xml version='1.0' encoding='UTF-8' standalone='y
```

### Verify if an apk package is installed or not
We could use adb command to get installed packages. Below command will get the
installed packages with keyword `mobly` in it:
```shell
$ adb shell pm list packages | grep 'mobly'
package:com.google.android.mobly.snippet.bundled
package:com.google.android.mobly.snippet.uiautomator
```

The `bttc` library provides a convenient method to check for APK installation. To verify if an apk package is installed or not, we can leverage the method `dut.gm.is_apk_installed`. e.g.:
```python
# Checks if MBS (Mobly Bundled Snippets) package is installed or not.
>>> dut.gm.is_apk_installed('com.google.android.mobly.snippet.bundled')
True
```
This method returns `True` if the specified package is installed on the device and `False` if it isn't.

### Managing Device Properties
Through adb command, we could use `getprop` to get device's property and
`setprop` to set device's property ([more](https://source.android.com/docs/core/architecture/configuration/add-system-properties#shell-commands)). For example:
```shell
# Get the value of property `ro.product.system.brand`.
$ adb shell getprop ro.product.system.brand
google

# Set the value `prop_val` into property `test.prop.key`
$ adb shell setprop test.prop.key prop_val

# Confirm the setting is correct.
$ adb shell getprop test.prop.key
prop_val
```

The `bttc` library simplifies property management through the `dut.gm.props` attribute, which acts like a dictionary:
```
# Access the value of property `ro.product.system.brand`
>>> dut.gm.props['ro.product.system.brand']
'google'

# Set the new value of property `test.prop.key` as "new_value"
>>> dut.gm.props['test.prop.key'] = 'new_value'

# Confirm the property `test.prop.key` is correctly set up.
>>> dut.gm.props['test.prop.key']
```

### Managing Device Config
Through adb command, we could use `device_config` to handle device's
configuration. For example:
```shell
# Grep the Bluetooth configuration settings with keyword `flags.a2dp`
$ adb shell device_config list bluetooth | grep 'flags.a2dp'
com.android.bluetooth.flags.a2dp_async_allow_low_latency=false
com.android.bluetooth.flags.a2dp_concurrent_source_sink=true
com.android.bluetooth.flags.a2dp_ignore_started_when_responder=false
com.android.bluetooth.flags.a2dp_offload_codec_extensibility=true
com.android.bluetooth.flags.a2dp_service_looper=false
```

The `bttc` library simplifies device configuration management through the `dut.gm.device_config` attribute, which acts like a dictionary:
```python
# Get Bluetooth configurations containing 'flags.a2dp' in their name
>>> [device_config_info for device_config_info in dut.gm.device_config.bluetooth if 'flags.a2dp' in device_config_info.name]
[DeviceConfig.Namespace.Setting(name='com.android.bluetooth.flags.a2dp_async_allow_low_latency', value='false', err=''), ...]

# Set Bluetooth configuration 'le_audio_enabled_by_default' to 'false'
>>> dut.gm.device_config.bluetooth['le_audio_enabled_by_default'] = 'false'

# Get the value of Bluetooth configuration 'le_audio_enabled_by_default'
>>> dut.gm.device_config.bluetooth['le_audio_enabled_by_default']
DeviceConfig.Namespace.Setting(name='le_audio_enabled_by_default', value='false', err='')
```

### Managing Device Settings
Through adb command, we could use `settings` to handle device's settings. For
example:
```shell
# Get global settings containing 'wifi_' in their name
$ adb shell settings list global | grep 'wifi_'
adb_wifi_enabled=0
alt_bypass_wifi_requirement_time_millis=0
wifi_always_requested=0
wifi_display_on=0
...
```

The `bttc` library simplifies device settings management through the `dut.gm.settings` attribute, which acts like a dictionary:
```
# Get global settings containing 'wifi_' in their name.
>>> [setting_info for setting_info in dut.gm.settings.g if 'wifi_' in setting_info.name]
[Settings.Namespace.Setting(name='adb_wifi_enabled', value='0', err=''), ...]

# Set global setting 'airplane_mode_on' to '0'
>>> dut.gm.settings.g['airplane_mode_on'] = '0'

# Get the value of global setting 'airplane_mode_on'
>>> dut.gm.settings.g['airplane_mode_on']
Settings.Namespace.Setting(name='airplane_mode_on', value='0', err='')
```

### Execute shell command in device
You can directly execute shell commands on your Android device using the dut.gm.shell method. This method returns the standard output (stdout), standard error (stderr), and the return code of the command. For example:
```python
# Get the device's Bluetooth address
>>> stdout, stderr, return_code = dut.gm.shell('settings get secure bluetooth_address')
>>> stdout
'D4:3A:2C:57:D4:21\n'
>>> stderr
''
>>> return_code
0
```

### Managing Do Not Disturb (DnD)
Android's "Do Not Disturb" (DnD) silences notifications, calls, and other interruptions to help you focus or rest.
 1  Use it during meetings, sleep, study sessions, or anytime you want uninterrupted time.
 2  You can customize DnD to allow exceptions for important contacts or apps, ensuring you never miss a critical alert.

For testing purpose, in order to reduce the flakiness or interruption from other
apps or system notification, you may want to turn on this setting. To do so, you can refer to below sample code:

```python
# Import the package `bttc` and instantiate DUT instance which we have to
# initialize uiautomator while the setting is turned on/off by UI operations.
>>> import bttc
>>> dut = bttc.get('36121FDJG000GR', init_snippet_uiautomator=True)

# Import the package `system_ui` to turn on/off DnD setting:
>>> from bttc.utils.ui_pages import system as system_ui

# Turn of `Do not Disturb` (DnD):
>>> system_ui.set_do_not_disturb(dut, True)

# Confirm that the global setting `zen_mode` reflects the setting:
>>> dut.gm.settings.g['zen_mode']
Settings.Namespace.Setting(name='zen_mode', value='1', err='')
```

If you want to turn if off, it is straight forward too:
```python
# Turn off `Do not Disturb` (DnD):
>>> system_ui.set_do_not_disturb(dut, False)    # Turn off DnD

# Confirm that the global setting `zen_mode` reflects the setting:
>>> dut.gm.settings.g['zen_mode']
Settings.Namespace.Setting(name='zen_mode', value='0', err='')
```

More conveniently, we could leverage `dut.gm.setting_dnd` to achieve the same
purpose. For example:
```python
>>> import bttc

# Argument `init_snippet_uiautomator=True` is necessary if
# you want to operate on the setting `Do not Disturb` (DnD)!
>>> dut = bttc.get('36121FDJG000GR', init_snippet_uiautomator=True)

# Check current `Do not Disturb` (DnD) setting:
>>> dut.gm.setting_dnd
Settings.Namespace.Setting(name='zen_mode', value='0', err='')

# Turn on `Do not Disturb` (DnD):
>>> dut.gm.setting_dnd = True
>>> dut.gm.setting_dnd
Settings.Namespace.Setting(name='zen_mode', value='1', err='')

# Turn off `Do not Disturb` (DnD):
>>> dut.gm.setting_dnd = False
>>> dut.gm.setting_dnd
Settings.Namespace.Setting(name='zen_mode', value='0', err='')
```

For the values of global setting `zen_model`:
* 0: DnD is off.
* 1: DnD is on in Priority mode (only allows priority notifications through).
* 2: DnD is on in Total silence mode (blocks all notifications).
* 3: DnD is on in Alarms only mode (only allows alarms through).


### How to dump the bugreport of device
A bugreport is a snapshot of your Android device's current state, including system logs, app data, and other relevant information.
It's helpful for developers to troubleshoot and diagnose issues.

To dump the bugreport, we could leverage method `dut.gm.dump_bugreport` which takes
two parameters, `host_destination` argument is used to tell where in the host to save the
bugreport; `file_name` argument is used to name the file name of bugreport.

Sample code is as below:
```python
# Import package `bttc` and get DUT instance.
>>> import bttc
>>> dut = bttc.get('36121FDJG000GR')

# Dump the bugreport to folder `/tmp/` and save it as name `test_bugreport.zip`.
>>> dut.gm.dump_bugreport(host_destination='/tmp/', file_name='test_bugreport.zip')
'/tmp/test_bugreport.zip'
```
From above example, we want bugreport to save in directory `/tmp/` and use file
name as `test_bugreport.zip`.

Another way to dump bugreport is through Cli module. e.g.:
```shell
# Enter Cli prompt
$ python -m 'bttc.cli.main'

# Select DUT
bttc> select
Connected device(s):
        - 07311JECB08252
        - 36121FDJG000GR

Select? 36121FDJG000GR
You select DUT with serial=36121FDJG000GR

# Dump bugreport to /tmp/my_bugreport.zip
bttc/36121FDJG000GR> dump_bugreport -d /tmp/ -n my_bugreport.zip
Start dumping bugreport to "/tmp/" with report name as "my_bugreport.zip"...
The final bugreport path is "/tmp/my_bugreport.zip"!
```

### How to show seconds on clock
To see seconds on the clock during testing (helpful for precise timekeeping), use this code:
```python
# Import package `bttc` and get DUT instance.
>>> import bttc
>>> dut = bttc.get('36121FDJG000GR')

# Enable second on clock
>>> dut.gm.enable_second_on_clock()

# Disable second on clock
>>> dut.gm.disable_second_on_clock()
```
