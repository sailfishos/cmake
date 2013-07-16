# spec file for package cmake

%define build_with_qt 1

%if 0%{?build_with_qt}
%define cmake_name cmake-gui
%define curses_dialog FALSE
%define qt_dialog TRUE
%else
%define cmake_name cmake
%define curses_dialog TRUE
%define qt_dialog FALSE
%endif

Name:           %{cmake_name}
Version:        2.8.11.2
Release:        1
License:        BSD
%if 0%{?build_with_qt}
Summary:        Qt based user interface for CMake (%{name})
%else
Summary:        Cross-platform make system
%endif
Url:            http://www.cmake.org
Group:          Development/Tools
Source0:        http://www.cmake.org/files/v2.8/cmake-2.8.11.2.tar.gz
Source1:        macros.cmake
Patch0:		cmake-2.8.11-tinfo.patch
BuildRequires:  expat-devel
BuildRequires:  pkgconfig(libarchive) >= 2.8.0
BuildRequires:  pkgconfig(libcurl)
BuildRequires:  pkgconfig(zlib)
BuildRequires:  procps
%if 0%{?build_with_qt}
BuildRequires:  desktop-file-utils
BuildRequires:  pkgconfig(QtGui)
BuildRequires:  pkgconfig(x11)
Requires:       cmake = %{version}
%else
BuildRequires:  pkgconfig(ncurses)
Requires:       procps
%endif

%description
CMake is used to control the software compilation process using simple platform
and compiler independent configuration files. CMake generates native makefiles
and workspaces that can be used in the compiler environment of your choice.
CMake is quite sophisticated: it is possible to support complex environments
requiring system configuration, pre-processor generation, code generation, and
template instantiation.

%if 0%{?build_with_qt}
This package provides the CMake Qt based GUI. Project configuration settings
may be specified interactively. Brief instructions are provided at the bottom
of the window when the program is running. The main executable file for this
GUI is "%{name}".
%endif

%prep
%setup -q -n %{name}-%{version}
%patch0 -p1
# Fixup permissions
find -name \*.h -o -name \*.cxx -print0 | xargs -0 chmod -x

%build
cat > %{buildroot}build-flags.cmake << EOF
set(CMAKE_SKIP_RPATH YES CACHE BOOL "Skip rpath" FORCE)
set(CMAKE_USE_RELATIVE_PATHS YES CACHE BOOL "Use relative paths" FORCE)
set(CMAKE_VERBOSE_MAKEFILE ON CACHE BOOL "Verbose build" FORCE)
set(CMAKE_C_FLAGS "%{optflags}" CACHE STRING "C flags" FORCE)
set(CMAKE_CXX_FLAGS "%{optflags}" CACHE STRING "C++ flags" FORCE)
set(CMAKE_SKIP_BOOTSTRAP_TEST ON CACHE BOOL "Skip BootstrapTest" FORCE)
set(BUILD_CursesDialog %{curses_dialog} CACHE BOOL "Build curses GUI" FORCE)
set(BUILD_QtDialog %{qt_dialog} CACHE BOOL "Build Qt4 GUI" FORCE)
set(MINGW_CC_LINUX2WIN_EXECUTABLE "" CACHE FILEPATH "Never detect mingw" FORCE)
set(CMAKE_USE_SYSTEM_LIBARCHIVE YES CACHE BOOL "" FORCE)
EOF
rm -rf %{_target_platform} && mkdir %{_target_platform}
cd %{_target_platform} && ../bootstrap \
                          --prefix=%{_prefix} \
                          --docdir=/share/doc/cmake-%{version} \
                          --mandir=/share/man \
                          --datadir=/share/cmake \
			  --system-libs \
                          --parallel=`/usr/bin/getconf _NPROCESSORS_ONLN` \
                          --init=%{buildroot}build-flags.cmake \
                          --system-libs

make VERBOSE=1 %{?_smp_mflags}

%install
%makeinstall -C %{_target_platform} DESTDIR=%{buildroot}
%if 0%{?build_with_qt}
# Remove unpackaged files
rm -f %{buildroot}%{_bindir}/cmake
rm -f %{buildroot}%{_bindir}/cpack
rm -f %{buildroot}%{_bindir}/ctest
rm -rf %{buildroot}%{_datadir}/cmake
rm -rf %{buildroot}%{_datadir}/doc/cmake-%{version}
rm -rf %{buildroot}%{_mandir}/man1
# Install desktop file
desktop-file-install \
  --delete-original \
  --dir=%{buildroot}%{_datadir}/applications \
  %{buildroot}%{_datadir}/applications/CMake.desktop
%else
find %{buildroot}%{_datadir}/%{name}/Modules -name '*.sh*' -type f | xargs chmod -x
mkdir -p %{buildroot}%{_datadir}/emacs/site-lisp
cp -a Example %{buildroot}%{_datadir}/doc/%{name}-%{version}/
install -m 0644 Docs/cmake-mode.el %{buildroot}%{_datadir}/emacs/site-lisp/
# Install cmake rpm macros
install -D -p -m 0644 %{_sourcedir}/macros.cmake \
  %{buildroot}%{_sysconfdir}/rpm/macros.cmake
%endif

%if 0%{?build_with_qt}
%post
update-desktop-database &> /dev/null || :
update-mime-database %{_datadir}/mime &> /dev/null || :

%postun
update-desktop-database &> /dev/null || :
update-mime-database %{_datadir}/mime &> /dev/null || :
%endif

%if 0%{?build_with_qt}
%files
%defattr(-,root,root,-)
%{_bindir}/%{name}
%{_datadir}/applications/CMake.desktop
%{_datadir}/mime/packages/cmakecache.xml
%{_datadir}/pixmaps/CMakeSetup32.png
%else
%files
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/rpm/macros.cmake
%{_datadir}/aclocal/cmake.m4
%{_datadir}/doc/%{name}-%{version}/
%{_bindir}/ccmake
%{_bindir}/cmake
%{_bindir}/cpack
%{_bindir}/ctest
%{_datadir}/%{name}/
%{_mandir}/man1/*.1*
%{_datadir}/emacs/
%endif
