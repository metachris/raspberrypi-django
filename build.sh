#!/bin/bash

cd /tmp
rm -rf rp1dpl
mkdir rp1dpl
cd rp1dpl

echo "Copying Project to /tmp/rp1dpl ..."
cp -pvr /Users/chris/Projects/private/raspberrypi/projects/django .

echo "Cleaning Up..."
cd django
rm -rf env
rm -rf .git*
rm -rf .idea
rm -rf .DS_Store
rm GPIODummy.py
rm fabfile.*
rm build.sh

echo "Packing..."
cd ..
tar -czf pack.tar.gz django
