#!/usr/bin/env bash
set -o errexit
pip install -r requirements.txt
mkdir -p ffmpeg_bin
cd ffmpeg_bin
wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
tar -xf ffmpeg-release-amd64-static.tar.xz --strip-components=1
cd ..
export PATH=$PATH:$(pwd)/ffmpeg_bin
