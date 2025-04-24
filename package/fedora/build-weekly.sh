#! /bin/sh -x
curl -O --location --retry 3 https://github.com/FreeCAD/FreeCAD-Bundle/releases/download/weekly-builds/freecad_version.txt
curl -O --location --retry 3 https://github.com/FreeCAD/FreeCAD-Bundle/releases/download/weekly-builds/freecad_source.tar.gz
curl -O --location --retry 3 https://raw.githubusercontent.com/filippor/FreeCAD/refs/heads/copr/package/fedora/freecad-weekly.spec
COMMIT_DATE=`grep commit_date: freecad_version.txt | sed 's/commit_date: //g'`
REVISION_NUMBER=`grep rev_number:  freecad_version.txt | sed 's/^rev_number: //g'`
COMMIT_HASH=`grep commit_hash: freecad_version.txt | sed 's/^commit_hash: //g'`
REMOTE_URL=`grep remote_url:  freecad_version.txt | sed 's/^remote_url: //g'`

sed -i -e 's@%%COMMIT_DATE%%@'"$COMMIT_DATE"'@g' -e 's@%%REVISION_NUMBER%%@'"$REVISION_NUMBER"'@g'  -e 's@%%COMMIT_HASH%%@'"$COMMIT_HASH"'@g'  -e 's@%%REMOTE_URL%%@'"$REMOTE_URL"'@g' freecad-weekly.spec
