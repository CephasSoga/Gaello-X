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

```sh {"id":"01J4GYNXV4NP69XHQWCC2DQQZB"}
### Better install this package's dist with:
poetry && poetry run pip install --force-reinstall dist\pygaello_gui-0.1.0-py3-none-any.whl \
   && run pip install -e .

```