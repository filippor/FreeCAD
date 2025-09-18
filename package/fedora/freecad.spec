# Some configuration options for other environments
# rpmbuild --without=bundled_zipios: don't use bundled version of zipios++
%bcond_without  bundled_zipios
# rpmbuild --with=bundled_pycxx:  use bundled version of pycxx
%bcond_with bundled_pycxx
# rpmbuild --without=bundled_smesh:  don't use bundled version of Salome's Mesh
%bcond_without bundled_smesh
# rpmbuild --without=bundled_gtest:  don't use bundled version of gtest and gmock
%bcond_with bundled_gtest

# rpmbuild --without=tests   exclude tests in %%check
%bcond_without tests
# rpmbuild --without=debug_info don't generate package with debug info
%bcond_without debug_info


Name:           freecad
Epoch:          1
Version:        weekly.2025.09.12
Release:        1.20250918124654651240.tmp1.110.g2852d4e409%{?dist}

Summary:        A general purpose 3D CAD modeler
Group:          Applications/Engineering
License:        LGPL-2.0-or-later
URL:            https://www.freecad.org/

Source0:        freecad-sources.tar.gz


# Maintainers:  keep this list of plugins up to date
# List plugins in %%{_libdir}/%%{name}/lib, less '.so' and 'Gui.so', here
%global plugins AssemblyApp AssemblyGui CAMSimulator DraftUtils Fem FreeCAD Import Inspection MatGui Materials Measure Mesh MeshPart Part PartDesignGui Path PathApp PathSimulator Points QtUnitGui ReverseEngineering Robot Sketcher Spreadsheet Start Surface TechDraw Web _PartDesign area flatmesh libDriver libDriverDAT libDriverSTL libDriverUNV libE57Format libMEFISTO2 libSMDS libSMESH libSMESHDS libStdMeshers libarea-native

%global exported_libs libOndselSolver


# See FreeCAD-main/src/3rdParty/salomesmesh/CMakeLists.txt to find this out.
%global bundled_smesh_version 7.7.1.0
# See /src/3rdParty/PyCXX/CXX/Version.h to find this out.
%global bundled_pycxx_version 7.1.9
# See /src/3rdParty/OndselSolver/CMakeLists.txt to find this out.
%global bundled_ondsel_solver_version 1.0.1

# Utilities
BuildRequires:  cmake gcc-c++ gettext doxygen swig graphviz gcc-gfortran desktop-file-utils tbb-devel ninja-build
%if %{with tests}
BuildRequires:  xorg-x11-server-Xvfb python3-typing-extensions 
%if %{without bundled_gtest}
BuildRequires: gtest-devel gmock-devel
%endif
%endif

# Development Libraries
BuildRequires:boost-devel Coin4-devel eigen3-devel freeimage-devel fmt-devel libglvnd-devel libicu-devel libspnav-devel libXmu-devel med-devel mesa-libEGL-devel mesa-libGLU-devel netgen-mesher-devel netgen-mesher-devel-private opencascade-devel openmpi-devel python3 python3-devel python3-matplotlib python3-pivy python3-pybind11 python3-pyside6-devel python3-shiboken6-devel pyside6-tools qt6-qttools-static qt6-qtsvg-devel vtk-devel xerces-c-devel yaml-cpp-devel
#pcl-devel
%if %{without bundled_smesh}
BuildRequires:  smesh-devel
%endif
%if %{without bundled_zipios}
BuildRequires:  zipios++-devel
%endif
%if %{without bundled_pycxx}
BuildRequires:  python3-pycxx-devel
%endif
# For appdata
#%if 0%{?fedora}
#BuildRequires:  libappstream-glib
#%endif

# Packages separated because they are noarch, but not optional so require them
# here.
Requires:       %{name}-data = %{epoch}:%{version}-%{release}
# Obsolete old doc package since it's required for functionality.
Obsoletes:      %{name}-doc < 0.22-1

Requires:       hicolor-icon-theme fmt python3-matplotlib python3-pivy python3-collada python3-pyside6 python3-typing-extensions

%if %{with bundled_smesh}
Provides:       bundled(smesh) = %{bundled_smesh_version}
%endif
%if %{with bundled_pycxx}
Provides:       bundled(python-pycxx) = %{bundled_pycxx_version}
%endif
Provides:       bundled(libondselsolver) = %{bundled_ondsel_solver_version}

Recommends:     python3-pysolar IfcOpenShell-python3



# plugins and private shared libs in %%{_libdir}/freecad/lib are private;
# prevent private capabilities being advertised in Provides/Requires
%global plugin_exclude %( for i in %{plugins}; do  echo -n "\|$i\(Gui\)\?"; done )
# prevent declaring Requires for internal FreeCAD libraries
%global lib_exclude %( for i in %{exported_libs}; do echo -n "\|$i"; done )
%global __requires_exclude_from ^%{_libdir}/%{name}/(lib|Mod)/.*
%global __provides_exclude_from ^%{_libdir}/%{name}/Mod/.*
%global __provides_exclude ^(libFreeCAD.*%{plugin_exclude})\.so.*
%global __requires_exclude ^(libFreeCAD.*%{plugin_exclude}%{lib_exclude})\.so.*



%description
FreeCAD is a general purpose Open Source 3D CAD/MCAD/CAx/CAE/PLM modeler, aimed
directly at mechanical engineering and product design but also fits a wider
range of uses in engineering, such as architecture or other engineering
specialities. It is a feature-based parametric modeler with a modular software
architecture which makes it easy to provide additional functionality without
modifying the core system.


%package data
Summary:        Data files for FreeCAD
BuildArch:      noarch
Requires:       %{name} = %{epoch}:%{version}-%{release}

%description data
Data files for FreeCAD

%package libondselsolver-devel
Summary:        Development file for OndselSolver
BuildArch:      noarch
Requires:       %{name} = %{epoch}:%{version}-%{release}

%description libondselsolver-devel
Development file for OndselSolver


#path that contain main FreeCAD sources for cmake
%global tests_resultdir %{_datadir}/%{name}/tests_result/%{_arch}

%if %{without debug_info}
%global debug_package %{nil}
%global _enable_debug_packages 0
%endif

%prep
    %setup -T -a 0 -q -c -n FreeCAD-1.0.2

%build
     # Deal with cmake projects that tend to link excessively.
    LDFLAGS='-Wl,--as-needed -Wl,--no-undefined'; export LDFLAGS

#         -DCMAKE_INSTALL_DATADIR=%{_datadir}/%{name} \
#         -DCMAKE_INSTALL_DATAROOTDIR=%{_datadir} \

    %cmake \
        -DCMAKE_INSTALL_PREFIX=%{_libdir}/%{name} \
        -DCMAKE_INSTALL_DOCDIR=%{_docdir}/%{name} \
        -DCMAKE_INSTALL_INCLUDEDIR=%{_includedir} \
        -DRESOURCEDIR=%{_datadir}/%{name} \
        -DFREECAD_USE_EXTERNAL_PIVY=TRUE \
        -DFREECAD_USE_EXTERNAL_FMT=TRUE \
        -DFREECAD_USE_PCL:BOOL=OFF \
        -DFREECAD_QT_VERSION:STRING=6 \
        -DOpenGL_GL_PREFERENCE=GLVND \
        -DUSE_OCC=TRUE \
    %if %{without bundled_pycxx}
        -DPYCXX_INCLUDE_DIR=$(pkg-config --variable=includedir PyCXX) \
        -DPYCXX_SOURCE_DIR=$(pkg-config --variable=srcdir PyCXX) \
    %endif
    %if %{without bundled_smesh}
        -DFREECAD_USE_EXTERNAL_SMESH=TRUE \
    %endif
    %if %{without bundled_zipios}
        -DFREECAD_USE_EXTERNAL_ZIPIOS=TRUE \
    %endif
    %if %{with tests}
        -DENABLE_DEVELOPER_TESTS=TRUE \
    %if %{without bundled_gtest}
        -DFREECAD_USE_EXTERNAL_GTEST=TRUE \
    %else
        -DINSTALL_GTEST=OFF \
        -DINSTALL_GMOCK=OFF \
    %endif
    %else
        -DENABLE_DEVELOPER_TESTS=FALSE \
    %endif
        -DONDSELSOLVER_BUILD_EXE=TRUE \
        -DBUILD_GUI=TRUE \
        -G Ninja

    %cmake_build


%install
    %cmake_install

    # Symlink binaries to /usr/bin
    mkdir -p %{buildroot}%{_bindir}
    ln -s ../%{_lib}/%{name}/bin/FreeCAD %{buildroot}%{_bindir}/FreeCAD
    ln -s ../%{_lib}/%{name}/bin/FreeCADCmd %{buildroot}%{_bindir}/FreeCADCmd

    # Remove header from external library that's erroneously installed
    rm -rf %{buildroot}%{_libdir}/%{name}/include/E57Format
    rm -rf %{buildroot}%{_includedir}/gmock
    rm -rf %{buildroot}%{_includedir}/gtest

    rm -rf %{buildroot}%{_libdir}/%{name}/%{_lib}/cmake
    rm -rf %{buildroot}%{_libdir}/%{name}/%{_lib}/pkgconfig

    #Move files using `-DCMAKE_INSTALL_DATAROOTDIR=%%{_datadir}` break ctest
    mkdir -p %{buildroot}%{_datadir}
    mv %{buildroot}%{_libdir}/freecad/share/applications %{buildroot}%{_datadir}/
    mkdir -p %{buildroot}%{_metainfodir}
    mv %{buildroot}%{_libdir}/freecad/share/metainfo/* %{buildroot}%{_metainfodir}/
    mkdir -p %{buildroot}%{_datadir}
    mv %{buildroot}%{_libdir}/freecad/share/icons %{buildroot}%{_datadir}/
    mv %{buildroot}%{_libdir}/freecad/share/pixmaps %{buildroot}%{_datadir}/
    mv %{buildroot}%{_libdir}/freecad/share/mime %{buildroot}%{_datadir}/
    mv %{buildroot}%{_libdir}/freecad/share/thumbnailers %{buildroot}%{_datadir}/
    mv %{buildroot}%{_libdir}/freecad/share/pkgconfig %{buildroot}%{_datadir}/

%check


%if %{with tests}
    mkdir -p %{buildroot}%tests_resultdir
    if %ctest -E '^QuantitySpinBox_Tests_run$' &> %{buildroot}%tests_resultdir/ctest.result ; then
        echo "ctest OK"
    else
        echo "**** Failed ctest ****"
        touch %{buildroot}%tests_resultdir/ctest.failed
    fi

    if xvfb-run \%ctest -R '^QuantitySpinBox_Tests_run$' &>> %{buildroot}%tests_resultdir/ctest_gui.result ; then
        echo "ctest gui OK"
    else
        echo "**** Failed ctest gui ****"
        touch %{buildroot}%tests_resultdir/ctest_gui.failed
    fi
%endif

    desktop-file-validate %{buildroot}%{_datadir}/applications/org.freecad.FreeCAD.desktop
    %{?fedora:appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/*.metainfo.xml}

    # Bug maintainers to keep %%{plugins} macro up to date.
    #
    # Make sure there are no plugins that need to be added to plugins macro
    %define plugin_regexp /^\\\(libFreeCAD.*%(for i in %{plugins};       do echo -n "\\\|$i"; done)\\\)\\\(\\\|Gui\\\)\\.so/d
    %define exported_libs_regexp      /^\\\(%(for i in %{exported_libs}; do echo -n "\\\|$i"; done)\\\)\\.so/d

    new_plugins=`ls %{buildroot}%{_libdir}/%{name}/%{_lib} | sed -e  '%{plugin_regexp}' -e '%exported_libs_regexp'`
    if [ -n "$new_plugins" ]; then
        echo -e "\n\n\n**** ERROR:\n" \
            "\nPlugins not caught by regexps:" \
            "\n" $new_plugins \
            "\n\nPlugins in %{_libdir}/%{name}/lib do not exist in" \
            "\nspecfile %%{plugins} or %%{exported_libs_regexp} macro." \
            "\nPlease add these to %%{plugins} or %%{exported_libs}" \
            "\nmacro at top of specfile" \
            "\nand rebuild.\n****\n" 1>&2
        exit 1
    fi
    # Make sure there are no entries in the plugins macro that don't match plugins
    for p in %{plugins}; do
        if [ -z "`ls %{buildroot}%{_libdir}/%{name}/%{_lib}/$p*.so`" ]; then
            set +x
            echo -e "\n\n\n**** ERROR:\n" \
                "\nExtra entry in %%{plugins} macro with no matching plugin:" \
                "'$p'.\n\nPlease remove from %%{plugins} macro at top of" \
                "\nspecfile and rebuild.\n****\n" 1>&2
            exit 1
        fi
    done
    # Make sure there are no entries in the exported_libs_regexp macro that don't match plugins
    for d in %{exported_libs}; do
        if [ -z "`ls %{buildroot}%{_libdir}/%{name}/%{_lib}/$d*.so`" ]; then
            set +x
            echo -e "\n\n\n**** ERROR:\n" \
                "\nExtra entry in %%{exported_libs} macro with no matching lib:" \
                "'$d'.\n\nPlease remove from %%{exported_libs} macro at top of" \
                "\nspecfile and rebuild.\n****\n" 1>&2
            exit 1
        fi
    done

%post
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :
    /usr/bin/update-mime-database %{_datadir}/mime &> /dev/null || :


%postun
    if [ $1 -eq 0 ] ; then
        /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    fi
    /usr/bin/update-desktop-database &> /dev/null || :
    /usr/bin/update-mime-database %{_datadir}/mime &> /dev/null || :


%posttrans
    /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor/scalable/apps &>/dev/null || :


%files
    %{_bindir}/*
    %{_metainfodir}/*
    %dir %{_libdir}/%{name}
    %{_libdir}/%{name}/bin/
    %{_libdir}/%{name}/%{_lib}/
    %{_libdir}/%{name}/Ext/
    %{_libdir}/%{name}/Mod/
    %{_libdir}/%{name}/share/
    %{_datadir}/applications/*
    %{_datadir}/icons/hicolor/*
    %{_datadir}/pixmaps/*
    %{_datadir}/mime/packages/*
    %{_datadir}/thumbnailers/*
    #find a way to configure in cmake with %%name to avoid conflict with different package name
    %{python3_sitelib}/freecad/*
%if %{with tests}
    %tests_resultdir/*
%endif


%files data
    %{_datadir}/%{name}/
    %{_docdir}/%{name}/LICENSE.html
    %{_docdir}/%{name}/ThirdPartyLibraries.html

%files libondselsolver-devel
    %{_datadir}/pkgconfig/OndselSolver.pc
    %{_includedir}/OndselSolver/*

%changelog
* Thu Sep 18 2025 Filippo Rossoni <filippo.rossoni@gmail.com> - 1:weekly.2025.09.12-1.20250918124654651240.tmp1.110.g2852d4e409
- add git information (github-actions[bot])
- cleanup (Filippo Rossoni)
- authomatic build (Filippo Rossoni)
- fix ctest command (github-actions[bot])
- use xvfb-run for QuantitySpinBox test (github-actions[bot])
- add qt6-assistant deps (Filippo Rossoni)
- update tests (Filippo Rossoni)
- add rpm cmake preset (filippor)
- restore version (filippor)
- Update freecad.spec (FilippoR)
- Update .packit.yaml (FilippoR)
- Update plan.fmf add IfcOpenShell-python3 (FilippoR)
- Remove error file if 2 time is successful (FilippoR)
- fix ctest (github-actions[bot])
- add verbose failed tests (filippor)
- tentative fix test (filippor)
- add github action (filippor)
- add tests in test-farm (filippor)
- add packit configuration (filippor)
- Update spec file (filippor)
- add github action (filippor)
- add tests in test-farm (filippor)
- add packit configuration (filippor)
- Update spec file (filippor)
- PartDesign: fix crash when creating new sketch (jffmichi)
- Fixes #23015 (sliptonic)
- Tests: Update to match new behavior (Chris Hennes)
- Gui: Fix segfault DlgPropertyLink (Pieter Hijma)
- Sketcher: Use the right delete flag for delConstraints (theo-vt)
- App: Remove manual PCH entries (Chris Hennes)
- App: Address reviewer comments (Chris Hennes)
- Material PMMA generic (#24006) (Pascal de Bruijn)
- Materials: Update Aluminum-6061-T6 (#23977) (Pascal de Bruijn)
- Gui: refactor gizmo attachment code (captain0xff)
- Materials: Add Aluminum-7075-T6 (#23976) (Pascal de Bruijn)
- Sketcher: fix some prefs texts (#23992) (Roy-043)
- TechDraw: Update missed UI strings to Title Case (Ryan Kembrey)
- Sketcher: context menu of Elements section in task panel to Title Case (Roy-043)
- Sketcher: titles of parameter sections to Title Case (#23936) (Roy-043)
- Update translations 2025-09-15 (Chris Hennes)
- Fix typos in the strings reported in Crowdin (#23956) (FEA-eng)
- Sketcher: Add 'Toggle' to 'Construction Geometry' menu texts (#23944) (Roy-043)
- Sketcher: Change "By control points" and "By knots" texts (#23943) (Roy-043)
- Gui: Remove internal prop types Add Prop dialog (Pieter Hijma)
- BIM: fix material handling of component (Roy-043)
- BIM: fix double click both editing label and opening task panel (Furgo)
- BIM: fix issues with T-slot profile (#23813) (Roy-043)
- BIM: fix double click both editing label and opening task panel (Furgo)
- [Arch]  Fix makeStairs Move & Addition Behaviour Consistency (Paul Lee)
- TechDraw: Fix projection groups not recursively deleting (Ryan Kembrey)
- also add qt5 compatibility for checkbox state change signal (David Kaufman)
- TechDraw: Add number decimals and reference dimension options to dimension task panel (#23501) (Ryan K)
- Materials: Add POM-(Homopolymer|Copolymer)-Generic followup (#23922) (Pascal de Bruijn)
- Materials: Add PEEK-Generic (#23779) (Pascal de Bruijn)
- TechDraw: Fix selections not clearing (Ryan Kembrey)
- Sketcher: QMessageBox titles to Title Case (#23925) (Roy-043)
- Sketcher change "don't attach" (#23924) (Roy-043)
- Sketcher: Update text in prefs (Title Case related) (Roy-043)
- Sketcher: QInputDialog titles to Title Case (#23920) (Roy-043)
- Gui: use CMake to generate precompiled headers on all platforms (Markus Reitböck)
- App: use CMake to generate precompiled headers on all platforms (Markus Reitböck)
- Base: use CMake to generate precompiled headers on all platforms (Markus Reitböck)
- [CAM] replace python uses of QSignalBlocker (David Kaufman)
- CAM: fix library import in postprocessor (Matthias Deimbacher)
- Materials: Add POM-(Homopolymer|Copolymer)-Generic (#23820) (Pascal de Bruijn)
- CMake: fix disable msvc warning on wrong target (Markus Reitböck)
- Gui: Make Report View properly claim Select All (Ctrl+A) shortcut (tetektoza)
- Sketcher: Coin resize when screen change. Fix #23267 (#23865) (PaddleStroke)
- PartDesign: remove duplicate scale during sketch creation with attach task (PaddleStroke)
- CAM: Consistently rename "Tool" to "Toolbit" in UI and code (Billy)
- Part: Add deprecation warning for import/export (Pieter Hijma)
- Sketcher: Fix ctrl A (#23866) (PaddleStroke)
- App: Add Python interface to ApplicationDirectories (Chris Hennes)
- Ensure Qt5 compatibility with enums (sliptonic)
- Fix B-spline keyboard focus issue (#23859) (#23860) (George Peden)
- Update src/Mod/CAM/Gui/Resources/panels/LibraryProperties.ui (sliptonic)
- fixes fix duplicate toolbits add tools to 'all tools' context menus and deletion /CamAssets/Tool/  directory structure Assets and preferences (sliptonic)
- CAM: Remove hardcoded style for Tool Number, Fix TestPathToolBitSerializer Fix issue with toolshapes Renamed fillet to radius Added Tool Type Filter to library Fix units so that they honor user preference Remove the QToolBox widget from the Shape Selector page and combine into a single page. Fix issue with PropertyBag so that CustomPropertyGroups as a string is converted to enum and enums are handled correctly. Update TestPathPropertyBag test for enum changes. Update TestPathToolBitListWidget Update TestPathToolLibrarySerializer to match new LinuxCNC output Fix LinuxCNC export too handle ALL tool types, use user preferences for units, and include all lcnc fields (Billy)
- Sketcher: Fix Select all with BSplines and clean up selection logic (Matthias Danner)
- Sketcher: Bspline tool: prevent double click failure (#23872) (PaddleStroke)
- Sketcher: Fix arc double click bug (#23873) (PaddleStroke)
- Gui: Fix disabling editing Property View (Pieter Hijma)
- Sketcher: Fix Freeze in Offset with too large negative value (#23467) (matthiasdanner)
- CAM: Clean DogboneDressup after PR#22250 (#23752) (tarman3)
- CAM: Improve SelectLoop (#23275) (tarman3)
- CAM: Reorder the Clearance height and Safe Height spinners in task panel (#23727) (Connor9220)
- Sketcher: Fix use after free Bug when commiting value with enter in OVP (#23853) (matthiasdanner)
- Bump github/issue-metrics from 3.23.1 to 3.23.2 (dependabot[bot])
- Gui: Small refactor of Tree.cpp selecting docs (Pieter Hijma)
- Gui: Process minor review comments (Pieter Hijma)
- CAM: Add AssetManager.copy() and .deepcopy() (Samuel Abels)
- [CAM] migrate old tools to new system (David Kaufman)
- [CAM] re-enable adaptive profile mode (David Kaufman)
- Gui: Adjust size of the Add Property dialog (Pieter Hijma)
- Gui: Select the VarSet when clicking Std_VarSet (Pieter Hijma)
- Gui: Improve adding multiple properties (Pieter Hijma)
- Gui: Move DlgAddPropertyVarSet -> DlgAddProperty (Pieter Hijma)
- Gui: Disallow adding props to multiple objects (Pieter Hijma)
- Gui: Generalize add property VarSet dialog (Pieter Hijma)
- Gui: Simplify title Add Property VarSet dialog (Pieter Hijma)
- CAM: select rows instead of cells in drilling panel (jffmichi)
