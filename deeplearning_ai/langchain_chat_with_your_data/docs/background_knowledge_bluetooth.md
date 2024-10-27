## Terminology

### Piconet
A piconet in Bluetooth is a small network consisting of one master device and up to seven active slave devices. The master device controls the communication within the piconet, while slave devices follow its instructions. Piconets are the basic building blocks of larger Bluetooth networks.

How piconets work:
1. Piconet Formation: A master device initiates a piconet by broadcasting its presence and inviting other devices to join.
2. Device Roles: Once a device joins, it becomes a slave and synchronizes its clock and frequency hopping pattern with the master.
3. Communication: The master controls when each device can transmit and receive data, ensuring orderly communication.
4. Scatternet Formation: If a device is within range of multiple piconets, it can participate in multiple piconets simultaneously, forming a scatternet.

## Abbreviation List

### BDA (Bluetooth Device Address)
BDA stands for Bluetooth Device Address. It is a unique 48-bit identifier assigned to every Bluetooth-enabled device. This address is essential for identifying and establishing connections between devices.

The BDA is usually represented as a 12-digit hexadecimal number, separated into six pairs by colons (e.g., 00:11:22:33:44:55). Each pair of digits corresponds to a byte of the address.

### FHS (Frequency Hopping Spread Spectrum)
FHS stands for Frequency Hopping Spread Spectrum. It is a radio transmission technique used by Bluetooth to minimize interference and improve the reliability of wireless communications.

How FHS works in Bluetooth:
1. Frequency Hopping: Bluetooth devices rapidly switch between different frequencies within a designated range (the 2.4 GHz ISM band). This hopping pattern is pseudo-random and known to both the transmitting and receiving devices.
2. Spread Spectrum: The transmitted signal is spread across a wider bandwidth than necessary, making it more resilient to narrowband interference.
3. Reduced Interference:  By hopping frequencies, Bluetooth avoids staying on any single channel for long, reducing the likelihood of colliding with other wireless devices operating on the same frequencies.

### LMP (Link Manager Protocol.)
[**LMP**](https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/Core-54/out/en/br-edr-controller/link-manager-protocol-specification.html) in Bluetooth stands for Link Manager Protocol. It is a key protocol within the Bluetooth stack that is responsible for the establishment, management, and control of connections between Bluetooth devices

### RNR (Remote Name Request)
* When a Bluetooth device discovers another device, it initially only knows its Bluetooth Device Address (BDA). To get the human-readable name of the device, it sends a Remote Name Request.
* The remote device responds with its name, which can then be displayed to the user.
