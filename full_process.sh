sudo bash install_udev_rule.sh
python minify.py index.html
python ino_generator.py
python flash_firmware.py
python epj_neck.py