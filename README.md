# AnIGAV
### ANalog-Input-Generated Audio Visuals

This project aims to create a RPiZero-powered OpenGL visualizer controllable by Eurorack CVs.

My goal is not to create some complex FT-based visualisation. I pretty much just want to adjust the parameters of a pre-programmed visualization with control voltage values.

## Features

* obj loading with automatic line indices generation
* Adjustable downscaling

## What's missing

* circuit for the actual input reading, but I have some wip
* routing the values to python

## Requirements
* `adafruit-blinka`
* `adafruit-circuitpython-mcp3xxx`
* `numpy`
* `pygame`
* `pyglm`
* `pyopengl`
* `pyopengl-accelerate`
* `pywavefront`
## Some images
![00](https://github.com/webik150/Anigav/blob/master/readme/img01.png)
![01](https://github.com/webik150/Anigav/blob/master/readme/img02.png)
