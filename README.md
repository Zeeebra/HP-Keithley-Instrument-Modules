# HP-Keithley-Instrument-Modules
Python device modules control HP and Keithley semiconductor testers through GPIB and PyVisa.

# Instrument Control Scripts for Semiconductor Testing Automation

This repository contains Python modules for controlling various laboratory instruments via GPIB or serial communication, supporting I–V sweeping, sampling, and LED control operations. These scripts are part of a broader automation toolkit used in lab environments.

## 📦 Included Modules

| File            | Instrument            | Functionality                            |
|-----------------|------------------------|-------------------------------------------|
| `B1500.py`      | Keysight B1500         | I–V sweep and sampling support            |
| `HP4155.py`     | HP 4155B               | I–V sweeps, sampling, multi-SMU support   |
| `HP4156.py`     | HP 4156C               | Advanced I–V and sampling with timestamp  |
| `Keithley2450.py` | Keithley 2450 SMU    | Basic I–V sweep using SCPI                |
| `Mightex.py`    | Mightex LED Controller | LED control (mode switching, current control) via serial port |

## ⚙️ Requirements

- Python 3.6+
- [PyVISA](https://pyvisa.readthedocs.io/)
- NI-VISA runtime (for GPIB communication)
- `matplotlib`, `numpy` for data visualization
- `serial_device2.py` for Mightex (must be available in the same directory or in PYTHONPATH)

### Installation

```bash
pip install pyvisa matplotlib numpy

