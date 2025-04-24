#! /bin/sh -x
curl -O --location --retry 3 https://github.com/FreeCAD/FreeCAD-Bundle/releases/download/1.0.0/freecad_source.tar.gz
curl -O --location --retry 3 https://raw.githubusercontent.com/filippor/FreeCAD/refs/heads/copr/package/fedora/freecad.spec
