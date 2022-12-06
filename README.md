# Dead Drop Attacks With Microcontrollers (Proof of Concept)

![alt text](https://github.com/notcos/notcos.github.io/blob/master/mcu.png)

## TLDR:
Walk into wifi range of your home network with a battery powered microcontroller in your pocket. This code flashed on it will run automatically and spawn reverse shells from vulnerable hosts on the network, connecting back to your command and control server.

## What:
This project is proof of concept for turning microcontrollers into automated pentesting devices.
I refer to this type of attack as a "dead drop attack".
This PoC performs a pentest on an entire target network for an authenticated Wing FTP Server remote command execution vulnerability. The python3 version of the exploit used in this PoC can be found here:
https://github.com/notcos/Wing-FTP-RCE

The code in this project is capable of spawning reverse shells on multiple different hosts in a short period of time.
The code for this project was written in Circuitpython.
The code was written for and tested on a FeatherS2 which has an ESP32-S2 MCU:
https://feathers2.io/

This code will, however, run on most microcontollers capable of running Circuitpython that possess wifi capabilities.
You can find a list of microcontrollers capable of running Circuitpython at the following URL:
https://circuitpython.org/downloads

## How:
* This code will make a microcontroller scan for wifi networks in the area.
* After connecting to the target network it will perform host discovery on a 192.168.0.0/24 network via http requests. While a ping sweep could be utilized here, a webserver may be configured to ignore ICMP requests.
* The live hosts will then be fingerprinted to see if they are running a vulnerable Wing FTP service.
* An attempt to authenticate to the Wing FTP admin login panel will be made with the user supplied credentials in the secrets.py file. If these credentials are invalid, a brute force attack will execute in order to try to discover valid credentials.
* In my example code, a Nishang PowerShell reverse TCP shell payload will then be executed on every vulnerable host on the target network, but you can write any payload you want in the secrets.py file. The code also supports a list of commands that can be executed one after the other on different hosts. This is useful for catching multiple reverse shells throughout the network, each on a unique port.
* The RCE payload firing part of the code is an infinite loop. This code will continuously send payloads to the vulnerable hosts. This enables you to connect to a new reverse shell if your shell dies.

## Why:
Microcontrollers introduce an interesting attack vector to networks. A standard microcontroller sold by a retailer that is capable of running this sort of attack can be bought for around $3.00. They consume very little power. They can run off of a battery for weeks to months depending on the battery size that is chosen. During that time it can run on its own without any need for user input. They can also be smaller than a US quarter.

A network can be as hardened as possible from outside attacks, but if it is running a vulnerable internal wifi network, it can be subject to this type of attack. All a malicious actor would need to do is slip a quarter-sized microcontroller into the belongings of someone traveling to a target network and they would have an attack vector opened up to them. The point being, an attacker does not need to be present to attack you through your local wifi.

## Future Possibilities:
This is a simple proof of concept. It can be expanded upon greatly. There are plenty of exploits written in python that could be ported over to this type of platform without too much effort.

If the target network is password protected, a malicious actor could program the microcontoller to perform a PMKID wifi attack in order to get a wifi password hash. These microcontrollers are not built for intensive wifi password cracking. This issue could be resolved by adding a LoRa module to the microcontroller. LoRa is a relatively new radio communication protocol that consumes very little power and can transfer data 12 kilometers away. One could radio the wifi password hash to a command and control server, crack the hash, then radio the wifi network's cracked password back to the microcontroller. This could potentially allow the microcontroller to connect to any wifi network it encounters.

While the code in the proof of concept does perform a conditional brute force attack against a login panel, a malicious actor could also utilize the same LoRa technology to perform brute force attacks on various parts of the network that require larger lists. A microcontoller may only possess 16mb of flash memory, but nothing is stopping someone from piping over 16gb of passwords/usernames in chunks via LoRa.

Another interesting addition would be to add a GPS module to the microcontroller. This would enable geofencing. One could program the microcontroller to run in a low power mode until it comes close enough to a designated area. After arriving at a set of designated coordinates it could then wake from sleep and start running recon code.

These microcontrollers can also be programmed to be difficult or impossible to reverse engineer, even with phsyical access to the device. They can be programmed to wipe their own memory if they are tampered with or if a battery/time threshold has been met.

## Risk Reduction:
Segregating sensitive parts of your network from your wifi network would be advisable. MAC addresses for microcontrollers from major manufacturers are publicly available. Networks that consider this type of attack a risk should create alerts anytime these MAC addresses are seen connecting to their network. This is not a reliable method of detection, as MAC addresses can be altered, but it is a start. A more effective risk reduction method would be to protect your wifi network with a very long and complex wifi password, or employ other methods of user verification.

## Test Environment:
You can build a lab environment to test this code out yourself. All you need is a Windows machine connected to your home network. The vulnerable Wing FTP Server software can be downloaded from the following URL:
https://www.exploit-db.com/apps/482625f61c2fcebfd6f7f2c10e705e01-WingFtpServer.exe

Just keep in mind that this code was written for a 192.168.0.0/24 network. If you are running another type of home network, you will need to modify the code.
