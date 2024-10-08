%global major_version 3

Name:           cmake
Version:        3.30.3
Release:        1
License:        BSD
Summary:        Cross-platform make system
Url:            http://www.cmake.org
Source0:        %{name}-%{version}.tar.gz
Source1:        macros.cmake.in
Source2:        %{name}.attr
Source3:        %{name}.prov
Patch0:         0001-Revert-Autogen-Reenable-passing-compiler-implicit-in.patch
Patch1:         0002-cmFileAPI-Allow-to-control-the-file-API-path.patch
BuildRequires:  expat-devel
BuildRequires:  bzip2-devel
BuildRequires:  xz-devel
BuildRequires:  pkgconfig(libarchive) >= 2.8.0
BuildRequires:  pkgconfig(libcurl)
BuildRequires:  pkgconfig(zlib)
BuildRequires:  pkgconfig(ncurses)
BuildRequires:  libstdc++-devel

%define cmake_version %(echo %{version} | cut -d '+' -f 1)

%description
CMake is used to control the software compilation process using simple platform
and compiler independent configuration files. CMake generates native makefiles
and workspaces that can be used in the compiler environment of your choice.
CMake is quite sophisticated: it is possible to support complex environments
requiring system configuration, pre-processor generation, code generation, and
template instantiation.

%prep
%autosetup -p1 -n %{name}-%{version}/%{name}

%build

cat > %{buildroot}build-flags.cmake << EOF
set(CMAKE_SKIP_RPATH YES CACHE BOOL "Skip rpath" FORCE)
set(CMAKE_USE_RELATIVE_PATHS YES CACHE BOOL "Use relative paths" FORCE)
set(CMAKE_VERBOSE_MAKEFILE ON CACHE BOOL "Verbose build" FORCE)
set(CMAKE_C_FLAGS "%{optflags}" CACHE STRING "C flags" FORCE)
set(CMAKE_CXX_FLAGS "%{optflags}" CACHE STRING "C++ flags" FORCE)
set(CMAKE_SKIP_BOOTSTRAP_TEST ON CACHE BOOL "Skip BootstrapTest" FORCE)
set(BUILD_CursesDialog TRUE CACHE BOOL "Build curses GUI" FORCE)
set(BUILD_QtDialog FALSE CACHE BOOL "Build Qt4 GUI" FORCE)
set(MINGW_CC_LINUX2WIN_EXECUTABLE "" CACHE FILEPATH "Never detect mingw" FORCE)
set(CMAKE_USE_SYSTEM_LIBARCHIVE YES CACHE BOOL "" FORCE)
EOF

rm -rf %{_target_platform} && mkdir %{_target_platform}

cd %{_target_platform} && ../bootstrap \
                          --prefix=%{_prefix} \
                          --docdir=/share/doc/cmake-%{version} \
                          --mandir=/share/man \
                          --datadir=/share/cmake \
                          --parallel=`/usr/bin/getconf _NPROCESSORS_ONLN` \
                          --init=%{buildroot}build-flags.cmake \
                          --system-curl \
                          --system-expat \
                          --system-zlib \
                          --system-bzip2 \
                          --system-libarchive \
                          --no-system-jsoncpp
# jsoncpp is not in mer-core so must use bundled version

%make_build

%install

%makeinstall -C %{_target_platform} DESTDIR=%{buildroot}

find %{buildroot}%{_datadir}/%{name}/Modules -name '*.sh*' -type f | xargs chmod -x

mkdir -p %{buildroot}%{_datadir}/emacs/site-lisp
install -m 0644 Auxiliary/cmake-mode.el %{buildroot}%{_datadir}/emacs/site-lisp/

# Install cmake rpm macros
install -D -p -m 0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/rpm/macros.cmake
sed -i -e "s|@@CMAKE_VERSION@@|%{cmake_version}|" -e "s|@@CMAKE_MAJOR_VERSION@@|%{major_version}|" %{buildroot}%{_sysconfdir}/rpm/macros.cmake

# RPM auto provides
install -p -m0644 -D %{SOURCE2} %{buildroot}%{_prefix}/lib/rpm/fileattrs/%{name}.attr
install -p -m0755 -D %{SOURCE3} %{buildroot}%{_prefix}/lib/rpm/%{name}.prov

# Remove useless bash-completion and vim files
rm -Rf %{buildroot}%{_datadir}/bash-completion
rm -Rf %{buildroot}%{_datadir}/vim

%files
%config %{_sysconfdir}/rpm/macros.cmake
%{_rpmconfigdir}/fileattrs/%{name}.attr
%{_rpmconfigdir}/%{name}.prov
%{_datadir}/aclocal/cmake.m4
%{_datadir}/doc/%{name}-%{version}/
%{_bindir}/ccmake
%{_bindir}/cmake
%{_bindir}/cpack
%{_bindir}/ctest
%{_datadir}/%{name}/
%{_datadir}/emacs/

