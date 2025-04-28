#!/bin/sh
rm -rf packit
mkdir -p packit
PREP_MACRO="rm -rf %{git_name}\n   %setup -T -a 0 -q -c -D -n %{git_name}"
sed \
-e 's@{{{ git_name }}}@FreeCAD@g' \
-e 's@{{{ build_version }}}@packit@g' \
-e 's@{{{ package_name }}}@freecad@g' \
-e 's@{{{ git_wcdate }}}@2025/04/28@g' \
-e 's@{{{ git_wcrev }}}@0000@g' \
-e 's@{{{ git_commit_hash }}}@0000000@g' \
-e 's@{{{ git_repo_pack_with_submodules }}}@freecad.tar.gz@g' \
-e 's@{{{ git_repo_setup_macro }}}@'"$PREP_MACRO"'@g' \
package/fedora/freecad.spec.rpkg > packit/freecad.spec
