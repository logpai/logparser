#!/bin/bash

home="$(pwd)/../logparser"

echo "=== Testing AEL ==="  && cd $home/AEL && python demo.py && \
echo "=== Testing Drain ===" && cd $home/Drain && python demo.py && \
echo "=== Testing IPLoM ===" && cd $home/IPLoM && python demo.py && \
echo "=== Testing LenMa ===" && cd $home/LenMa && python demo.py && \
echo "=== Testing LFA ===" && cd $home/LFA && python demo.py && \
echo "=== Testing LKE ===" && cd $home/LKE && python demo.py && \
echo "=== Testing LogCluster ===" && cd $home/LogCluster && python demo.py && \
echo "=== Testing LogMine ===" && cd $home/LogMine && python demo.py && \
echo "=== Testing LogSig ===" && cd $home/LogSig && python demo.py && \
echo "=== Testing MoLFI ===" && cd $home/MoLFI && python demo.py && \
echo "=== Testing SHISO ===" && cd $home/SHISO && python demo.py && \
echo "=== Testing SLCT ===" && cd $home/SLCT && python demo.py && \
echo "=== Testing Spell ===" && cd $home/Spell && python demo.py && \
echo "=== Testing logmatch ===" && cd $home/logmatch && python demo.py &&\
# echo "=== Testing NuLog ===" && cd $home/NuLog && python demo.py &&\
echo "=== Testing Brain ===" && cd $home/Brain && python demo.py &&\
# echo "=== Testing DivLog ===" && cd $home/DivLog && python demo.py &&\
echo "All tests succeed!"
