# Flir_lepton
Read image from Flir Lepton with FT232x

## Requier
* [libmpsse](https://github.com/devttys0/libmpsse)
* matplotlib

## Connection
| FT232x        | Flir Lepton Breakout  |
| ------------- |:-------------:|
| VCCD(3.3V)      | Vin |
| GND      | GND     | 
| ADBUS0(TCK/SK) | CLK      |
| ADBUS1(TDI/DO) | MOSI |
| ADBUS2(TDO/DI) | MISO     | 
| ADBUS3(TMS/CS) | CS      |
| ADBUS4(GPIO0) | SCL |
| ADBUS5(GPIO1) | SDA    | 
| ADBUS6(GPIO2) | SDA      |