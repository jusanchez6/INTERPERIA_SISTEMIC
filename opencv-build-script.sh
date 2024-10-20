#!/bin/bash

# Set OpenCV version
OPENCV_VER="master"

# Create a temporary directory
TMPDIR=$(mktemp -d)

# Build and install OpenCV from source
cd "${TMPDIR}"

# Clone the repository
git clone --branch ${OPENCV_VER} --depth 1 --recurse-submodules --shallow-submodules https://github.com/opencv/opencv-python.git opencv-python-${OPENCV_VER}

# Change to the cloned directory
cd opencv-python-${OPENCV_VER}

# Set environment variables
export ENABLE_CONTRIB=0
export ENABLE_HEADLESS=1
export CMAKE_ARGS="-DWITH_GSTREAMER=ON"

# Build the wheel
python3 -m pip wheel . --verbose

# Install OpenCV
python3 -m pip install opencv_python*.whl

# Clean up
cd
rm -rf "${TMPDIR}"

echo "OpenCV installation complete."
