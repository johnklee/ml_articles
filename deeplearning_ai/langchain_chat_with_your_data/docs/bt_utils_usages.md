## Preface
The `bt_utils` module provides utility functions for common Bluetooth
operations, such as enabling/disabling Bluetooth and retrieving a list of
paired devices.

## Usage
The `bttc.bt_utils.BTModule` class is loaded automatically when you retrieve a
device using the `bttc.get()` function.  For example:
```python
# Import the package `bttc`
>>> import bttc

# Retrieve your device. Please replace '36121FDJG000GR' with your device's
# serial number.
>>> dut = bttc.get('36121FDJG000GR')
```
You can access supported Bluetooth operations through the device's `bt`
attribute.

### Get Bluetooth Adapter State
The Bluetooth adapter state tells you the current condition of your device's Bluetooth radio.
Think of it like a switch for your Bluetooth: is it off, on, or somewhere in between? This state is crucial for applications that use Bluetooth, as they need to know whether Bluetooth is available and in what capacity.

Bluetooth Adapter State Values:
* `STATE_UNKNOWN` (0): The initial state, usually indicating the system hasn't yet determined the actual Bluetooth adapter state.
* `STATE_OFF` (10): Bluetooth is completely disabled. No Bluetooth functionality is available.
* `STATE_TURNING_ON` (11): The Bluetooth adapter is in the process of turning on. Bluetooth is not yet usable.
* `STATE_ON` (12): Bluetooth is fully enabled and ready for pairing and data exchange.
* `STATE_TURNING_OFF` (13): The Bluetooth adapter is shutting down. Bluetooth is no longer usable.
* `STATE_BLE_TURNING_ON` (14): The Bluetooth adapter is specifically turning on Bluetooth Low Energy (BLE) functionality.
* `STATE_BLE_ON` (15): BLE functionality is fully enabled. Your device can connect to and communicate with low-energy Bluetooth devices.
* `STATE_BLE_TURNING_OFF` (16): The BLE functionality is shutting down.

From BTTC, you could get the Bluetooth adapter state by property
`dut.bt.le_state`. e.g.:
```python
# Import the package `bttc`
>>> import bttc

# Retrieve your device. Please replace '36121FDJG000GR' with your device's
# serial number. In order to get Bluetooth Adapter state, we need to set
# argument `init_sl4a=True`:
>>> dut = bttc.get('36121FDJG000GR', init_sl4a=True)

# Get the Bluetooth Adapter state
>>> dut.bt.le_state
<BluetoothAdapterState.STATE_BLE_ON: 15>
```

If you conduct actions and would like to wait for certain Bluetooth Adapter
states, you could leverage method `dut.bt.wait_adapter_state`. e.g.:
```python
# Import package to get enumeration of Bluetooth Adapter state
>>> from bttc import constants
>>> bt_adapter_state = constants.BluetoothAdapterState

# Turn off Bluetooth
>>> dut.bt.disable()

# Wait for Bluetooth Adapter States `STATE_OFF` or `STATE_BLE_ON` for 3 seconds:
>>> dut.bt.wait_adapter_state({bt_adapter_state.STATE_OFF, bt_adapter_state.STATE_BLE_ON}, timeout_sec=3)
True
>>> dut.bt.le_state
<BluetoothAdapterState.STATE_BLE_ON: 15>
```

### Get Bluetooth status
You can call method `dut.bt.is_enabled` or access attribute `dut.bt.enabled` to
get the Bluetooth status of device. e.g.:
```python
>>> dut.bt.is_enabled()   # Checks if Bluetooth is enabled.
False
>>> dut.bt.enable()       # Enable the Bluetooth of device.
>>> dut.bt.is_enabled()   # Checks if Bluetooth is enabled.
True
>>> dut.bt.enabled        # Access the Bluetooth status.
True
```

### Get Device's Bluetooth MAC address
You can retrieve the Bluetooth MAC address of device by method
`dut.bt.get_bluetooth_mac_address`. e.g.:
```python
# Import utility `bt_utils`
>>> from bttc import bt_utils

# Retrieve your device. Please replace '36121FDJG000GR' with your device's
# serial number.
>>> dut = bt_utils.bind('36121FDJG000GR')

# Get Bluetooth MAC address
>>> dut.bt.get_bluetooth_mac_address()
'D4:3A:2C:57:D4:21'
```

### Get Device's Bluetooth name
You can get the device's Bluetooth name by method `dut.bt.get_name`. e.g.:
```python
# Import package `bttc` and retrieve DUT device `dut`.
# Please replace `36121FDJG000GR` with serial number of your drvice.
>>> import bttc
>>> dut = bttc.get('36121FDJG000GR')

# Gets the name of Bluetooth
>>> dut.bt.get_name()
'Pixel 8 Pro'

# Or you could directly access the attribute `name` to achieve
# the same purpose.
>>> dut.bt.name
'Pixel 8 Pro'
```

### Get Bluetooth MAC address of paired BT device by name
You can get the MAC address of paired BT device by method `dut.bt.get_device_mac_by_name`:
```python
# Get the device with MBS available
>>> dut = bttc.get('36121FDJG000GR', init_mbs=True)

# List the paired BT device(s)
>>> dut.bt.list_paired_devices()
['Acrux']

# Get the MAC address of paired BT device `Acrux`
>>> dut.bt.get_device_mac_by_name('Acrux')
['7C:96:D2:87:44:75']
```

### Get the Bluetooth crash information.
We can use method `dut.bt.crash_since` to look for any Bluetooth crash
information after a certain device time. e.g.:
```python
# Get the DUT
>>> dut = bttc.get('36121FDJG000GR')

# Get the device time and starting point to search crash afterword.
>>> begin_device_time = dut.gm.device_time
>>> begin_device_time
'05-22 16:44:00.000'

# No crash in the beginning.
>>> dut.bt.crash_since(begin_device_time)
CrashInfo(total_num_crash=0, collected_crash_times=[])

# Let's use below command to force Bluetooth to crash
# $ adb shell "pgrep -f keyword 'com.google.android.bluetooth' | xargs kill -9"
# Then we could obtain the crash record now:
>>> dut.bt.crash_since(begin_device_time)
CrashInfo(total_num_crash=1, collected_crash_times=['05-22 16:48:52.396'])

# If we don't feed in device time, it will search all crash record.
>>> dut.bt.crash_since()
CrashInfo(total_num_crash=1, collected_crash_times=['05-22 16:48:52.396'])
```

### Get Bluetooth MAC address
You can retrieve the Bluetooth MAC address by method
`dut.bt.get_bluetooth_mac_address`. e.g.:
```python
>>> dut.bt.get_bluetooth_mac_address()  # Get Bluetooth MAC address
'D4:3A:2C:57:D4:21'
```

### Get bonded devices
You can get the bonded devices by method `dut.bt.get_bonded_devices`:
```python
# Get the DUT.
>>> dut = bttc.get('36121FDJG000GR')

# Get the bonded device information
>>> dut.bt.get_bonded_devices()
[BondedDeviceInfo(mac_addr='7C:96:D2:87:44:75', bt_type=<BluetoothDeviceType.DUAL: 3>, name='Acrux')]
```

### Get paired devices
We can get paired device(s) by method `dut.bt.list_paired_devices`:
```python
# Get the device with MBS available
>>> dut = bttc.get('36121FDJG000GR', init_mbs=True)

# List the paired device(s)
>>> dut.bt.list_paired_devices()
['Acrux']
```
From the output of last command, we learn that BT device with name `Acrux` is
paired with our device.

If you want to retrieve more information, please set argument `only_name=False`:
```python
>>> dut.bt.list_paired_devices(only_name=False)
[PairedDeviceInfo(mac_addr='7C:96:D2:87:44:75', bt_type=<BluetoothDeviceType.DUAL: 3>, name='Acrux', uuids=['00001107-d102-11e1-9b23-00025b00a5a5', '00001108-0000-1000-8000-00805f9b34fb', '0000110b-0000-1000-8000-00805f9b34fb', '0000110e-0000-1000-8000-00805f9b34fb', '0000111e-0000-1000-8000-00805f9b34fb', '0000180f-0000-1000-8000-00805f9b34fb', '81c2e72a-0591-443e-a1ff-05f988593351', 'f8d1fbe4-7966-4334-8024-ff96c9330e15'], bond_state=<BluetoothBondedState.BONDED: 12>)]
```
In this case, you could obtain more information of paired BT device `Acrux` such
as its bonding state, MAC address etc.

### Enable/Disable Bluetooth
To enable the Bluetooth of device, you can call method `dut.bt.enable`:
```python
>>> dut.bt.enable()  # Enable the Bluetooth of device.
>>> dut.bt.enabled   # Get the status of device's Bluetooth.
True
```

To disable the Bluetooth of device, you can call method `dut.bt.disable`:
```python
>>> dut.bt.enabled    # The Bluetooth is on for now.
True
>>> dut.bt.disable()  # Disable the Bluetooth of device.
>>> dut.bt.enabled    # Get the status of device's Bluetooth
False
```

### Dump the content of Bluetooth manager
To dump the content of Bluetooth manager, call method
`dut.bt.dump_bluetooth_manager`:
```python
>>> bluetooth_manager_output = dut.bt.dump_bluetooth_manager()
>>> print(bluetooth_manager_output[:100])
Bluetooth Status
  enabled: false
  state: BLE_ON
  address: XX:XX:XX:XX:D4:21
  name: Pixel 8 Pro
```

### Enable/Disable Airplane
To enable Airplane mode, we can call method `dut.bt.enable_airplane_mode`:
```python
# Currently, Airplane mode is off
>>> dut.adb.shell(['settings', 'get', 'global', 'airplane_mode_on']).decode().strip()
'0'

# Enable the Airplane mode
>>> dut.gm.enable_airplane_mode()

# Then we have Airplane mode as on
>>> dut.adb.shell(['settings', 'get', 'global', 'airplane_mode_on']).decode().strip()
'1'
```
To disable Airplane mode, we can call method `dut.bt.disable_airplane_mode`:
```python
# Currently, Airplane mode is on
>>> dut.adb.shell(['settings', 'get', 'global', 'airplane_mode_on']).decode().strip()
'1'

# Disable the Airplane mode
>>> dut.gm.disable_airplane_mode()

# Then we have Airplane mode as off
>>> dut.adb.shell(['settings', 'get', 'global', 'airplane_mode_on']).decode().strip()
'0'
```

### Enable Snoop log
In Android 4.4 and later, you can manually collect BTSnoop logs, which resemble
the snoop format in RFC 1761. These logs capture the Host Controller Interface
(HCI) packets. For most Android devices, the logs are stored in
`data/misc/bluetooth/logs`.

You can enable the Snoop log by calling method `dut.bt.enable_snoop_log`:
```python
# In default, snoop log is not enabled.
>>> dut.gm.props['persist.bluetooth.btsnooplogmode']
''

# Enable the snoop log.
>>> dut.bt.enable_snoop_log()
True

# Confirm the snoop log is enabled.
>>> dut.gm.props['persist.bluetooth.btsnooplogmode']
'full'
```

### Enables Bluetooth Gabeldorsche (GD) verbose log
You can enable Bluetooth Gabeldorsche (GD) verbose log by method `dut.bt.enable_gd_log_verbose`:
```python
# By default, GD verbose log is off
>>> dut.gm.device_config.bluetooth['INIT_logging_debug_enabled_for_all']
DeviceConfig.Namespace.Setting(name='INIT_logging_debug_enabled_for_all', value='null', err='')

# Turn on the Gabeldorsche (GD) verbose log
>>> dut.bt.enable_gd_log_verbose()
True

# Confirm the setting is set successfully (value='true')
>>> dut.gm.device_config.bluetooth['INIT_logging_debug_enabled_for_all']
DeviceConfig.Namespace.Setting(name='INIT_logging_debug_enabled_for_all', value='true', err='')
```

Ps. For this setting to work, your `build_version_sdk` should >= 33.

### Enable or Disable Fast pair (Fastpair)
Fast Pair is a feature by Google that simplifies the pairing process between your Android device and Bluetooth accessories like headphones, earbuds, or speakers. When you bring a compatible accessory close to your phone, a notification pops up, allowing you to quickly connect with a single tap. This eliminates the need to manually navigate through Bluetooth settings, making pairing much faster and more convenient. ([more](https://developers.google.com/nearby/fast-pair/specifications/introduction))

To enable Fast pair from UI, several settings must be enabled for Fast Pair device discovery to be active in GMS Core:
1. General location setting (Settings > Location)
  * Only required on Android below S.
2. "Scan for nearby devices" (Settings > Google > Devices & sharing > Devices)
  * This is a GMS Core setting enabled by default.
3. General Bluetooth (Settings > Connected Devices > Connection preferences > Bluetooth) and/or "Bluetooth scanning" (Settings > Location > Location services)
  * At least one of these two must be enabled.

From BTTC, you can use below sample code to disable Fast pair:
```python
# Import BTTC package and get the DUT instance.
>>> import bttc
>>> dut = bttc.get('36121FDJG000GR')

# Disable the Fast pair.
>>> dut.bt.set_fast_pair_halfsheet(False)
```

Or below code will do the same thing to disable the Fast pair:
```
>>> dut.bt.disable_fastpair()
```

On the contrary, the sample code to enable Fast pair:
```python
# Import BTTC package and get the DUT instance.
>>> import bttc
>>> dut = bttc.get('36121FDJG000GR')

# Enable the Fast pair.
>>> dut.bt.set_fast_pair_halfsheet(True)
```

Or below sample code will do the same thing to enable the Fast pair:
```python
>>> dut.bt.enable_fastpair()
```

### Factory reset
You can do Bluetooth factory reset by method `dut.bt.factory_reset` which will:
* Remove bonded devices from the DUT.
* Conduct Bluetooth factory reset
* Ensure the Bluetooth is enabled

Below is the sample code:
```python
# Import BTTC package
>>> import bttc

# Connects to a DUT (Device Under Test) specified by its serial number.
# SL4A is necessary for `dut.bt.factory_reset` method.
>>> bttc.get('07311JECB08252', init_sl4a=True)

# Conduct Bluetooth factory reset.
>>> dut.bt.factory_reset()
```

### Unbonded devices
Unbonding a Bluetooth device, also known as unpairing or forgetting, removes the saved connection between your device and the Bluetooth accessory. This means they will no longer automatically connect when in range.

In BTTC, the `dut.bt.unbond_device` method allows you to unbond a Bluetooth
device using its name or MAC address. Here's an example:
```python
# Import BTTC package
>>> import bttc

# Connects to a DUT (Device Under Test) specified by its serial number.
# SL4A is necessary for `dut.bt.unbond_device` method.
>>> dut = bttc.get('36121FDJG000GR', init_sl4a=True)

# Retrieves a list of currently bonded Bluetooth devices on the DUT.
>>> dut.bt.get_bonded_devices()
[BondedDeviceInfo(mac_addr='98:0D:6F:4D:94:90', bt_type=<BluetoothDeviceType.UNKNOWN: 0>, name='Galaxy Buds2 Pro'), BondedDeviceInfo(mac_addr='98:0D:6F:54:F9:1E', bt_type=<BluetoothDeviceType.UNKNOWN: 0>, name='Galaxy Buds2 Pro'), BondedDeviceInfo(mac_addr='08:9E:08:36:F1:BF', bt_type=<BluetoothDeviceType.UNKNOWN: 0>, name='BDS-07311JECB08252')]

# Unbonds a specific device by its name ("Galaxy Buds2 Pro" in this case).
>>> dut.bt.unbond_device(name_or_mac='Galaxy Buds2 Pro')
True

# Confirms that the device has been successfully unbonded by checking the updated list of bonded devices.
>>> dut.bt.get_bonded_devices()
[BondedDeviceInfo(mac_addr='08:9E:08:36:F1:BF', bt_type=<BluetoothDeviceType.UNKNOWN: 0>, name='BDS-07311JECB08252')]
```

### Verified if a BT device is connected or not
We could leverage `dut.bt.is_paired_with` API to confirm if a BT device is connected
or not either by its name or MAC address. Below is the sample code:
```python
# Import package bttc and instantiate the DUT object:
>>> import bttc
>>> dut= bttc.get('36121FDJG000GR')

# Gets the bonded device list from the DUT:
>>> dut.bt.bonded_devices
[BondedDeviceInfo(mac_addr='7C:96:D2:87:44:75', bt_type=<BluetoothDeviceType.DUAL: 3>, name='Acrux', connect_state=''), BondedDeviceInfo(mac_addr='08:9E:08:36:F1:BF', bt_type=<BluetoothDeviceType.DUAL: 3>, name='Bluetooth Device Simulator', connect_state='Disconnected'), BondedDeviceInfo(mac_addr='E0:06:35:95:46:95', bt_type=<BluetoothDeviceType.LE: 2>, name='INZONE Buds', connect_state=''), BondedDeviceInfo(mac_addr='EE:E8:41:66:78:E8', bt_type=<BluetoothDeviceType.LE: 2>, name='INZONE Buds', connect_state='')]

# Confirm if BT device `Bluetooth Device Simulator` is connected or not.
>>> dut.bt.is_paired_with('Bluetooth Device Simulator')
False

# Connected BDS manually here.

# Confirm if BT device `Bluetooth Device Simulator` is connected as expected.
>>> dut.bt.is_paired_with('Bluetooth Device Simulator')
True

# Use MAC address of BT device `Bluetooth Device Simulator` to confirm again.
>>> dut.bt.is_paired_with('08:9E:08:36:F1:BF')
True

# Disconnected BDS here.

# Confirm that BT device with MAC address `08:9E:08:36:F1:BF` is disconnected
# with return value as False.
>>> dut.bt.is_paired_with('08:9E:08:36:F1:BF')
False
```

### Bet BRCM (Broadcom) Firmware Version
BRCM stands for Broadcom. It is a major semiconductor company that designs and manufactures a wide range of chips, including those used for Bluetooth communication. To get the version of BRCM firmware (fw) version by BTTC, below is the sample code:
```python
# Import package bttc and instantiate the DUT object:
>>> import bttc
>>> dut= bttc.get('36121FDJG000GR')

# Get the BRCM fw version:
>>> dut.bt.get_brcm_fw_version()
'0284'
>>> dut.bt.brcm_fw_version
'0284'
```
