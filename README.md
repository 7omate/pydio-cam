# pydio-cam
A small script to regularly upload pictures from a webcam to a Pydio server.

# Runs on raspberry pi
Expects a webcam in */dev/video0* (default)

```shell
git clone https://github.com/7omate/pydio-cam
git submodule init
git submodule update
pip install -r requirements.txt # Should be already satisfied
python pydiocam.py
# edit pydiocamconf.py
python pydiocam.py
```
