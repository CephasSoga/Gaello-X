# Development System Configurations

### OS

- Edition	Windows 11 Pro
- Version	21H2
- OS build	22000.1696
- Experience	Windows Feature Experience Pack 1000.22000.1696.0

### System

- Processor	Intel(R) Core(TM) i7-6600U CPU @ 2.60GHz   2.81 GHz
- Installed RAM	16.0 GB (15.9 GB usable)
- Device ID	4F9AEE98-DADD-47A0-AE60-B447B7F1B37F
- Product ID	00330-51287-86703-AAOEM
- System type	64-bit operating system, x64-based processor
- Pen and touch	Touch support with 10 touch points

# System Requirements

- Windows 10/11
- x64 bits
- Screen Resolution: 1920x1080
- Aspect Ratio: 16:9 ?
- CPU: 4GB RAM

# Dev Dependencies

```sh {"id":"01J4GWZKWV7AF617T8Q6N34MBB"}
# The following are third-party applications this project relies on.
FFMPEG
```

```sh {"id":"01J4C7MFR5Y7JD9XD0R3N1FGKB"}
# Leaking dependencies
pyqt5="5.15.10"
qasync=""
pyqtspinner
pyqt5-sip
pyqt5-tools
PyQtWebEngine
kaleido
```

All packages inside ./build should be installed in the virtual environment (or, at least, in the global python environment)