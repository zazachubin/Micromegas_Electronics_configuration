ATLAS Micromegas (MM) detectors The MMFE-8 boards front-end electronics configuration files generator

Requirements:
    OS: Linux
    THL_calib_all.py generates reference data.json file which should be in "Template" folder !
    "Template" folder and config.py, set.py should be in same directory !

Two kind configuration:
    1) configuration by parameters: FileName, Gain, Peaking_time, L0offset, Threshold
       (python ./config.py test 9 200 4095 50)
    2) configuration by reference file set.txt
       (python ./set.py test set.txt)