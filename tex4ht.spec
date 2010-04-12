%define _texmf %{_datadir}/texmf
%define _scriptsdir %{_datadir}/tex4ht

%bcond_without java

Name:           tex4ht
Version:        1.0.2008_02_28_2058
Release:        %mkrel 4
Epoch:          1
Summary:        LaTeX and TeX for Hypertext
License:        LPPL
Group:          Publishing
URL:            http://www.cse.ohio-state.edu/~gurari/TeX4ht/
Source0:        http://www.cse.ohio-state.edu/~gurari/TeX4ht/fix/tex4ht-%{version}.tar.gz
# Source1 is only used for documentation
# renamed to tex4ht-all-YYYYMMDD.zip - based on last timestamp in directory
Source1:        tex4ht-all-20070609.zip
# unversioned upstream source, downloaded with wget -N
#Source1 http://www.cse.ohio-state.edu/~gurari/TeX4ht/tex4ht-all.zip
Source2:        tex4ht-lppl.txt
# unversioned upstream litteral source, downloaded with wget -N
#Source3:       http://www.cse.ohio-state.edu/~gurari/TeX4ht/fix/tex4ht-lit.zip
Source3:        tex4ht-lit-20080229.zip
Source4:        http://www.cse.ohio-state.edu/~gurari/tpf/ProTex.sty
Source5:        http://www.cse.ohio-state.edu/~gurari/tpf/AlProTex.sty
Source6:        http://www.cse.ohio-state.edu/~gurari/tpf/DraTex.sty
Source7:        http://www.cse.ohio-state.edu/~gurari/tpf/AlDraTex.sty
Patch0:         tex4ht-1.0.2008_02_28_2058-fix-format-errors.patch
# debian
Patch1:         http://ftp.de.debian.org/debian/pool/main/t/tex4ht/tex4ht_20080228-1.diff.gz
# debian patch rebased
#Patch2:        fix_tex4ht_env.diff
# update debian rebuild script
#Patch3:        tetex-tex4ht-1.0-rebuild.patch
Requires(post): tetex
Requires(postun): tetex
Requires:       netpbm
# ImageMagick, pstoedit depends on ghostscript and gs is in ghostscript
Requires:       imagemagick
Requires:       pstoedit
Requires:       tetex-dvips
BuildRequires:  sharutils
BuildRequires:  tetex-devel
#BuildRequires: kpathsea-devel
%if %with java
BuildRequires:  java-devel >= 0:1.5.0
%endif
BuildRoot:      %{_tmppath}/%{name}-%{version}

%description 
TeX4ht is a highly configurable TeX-based authoring system for
producing hypertext. It interacts with TeX-based applications
through style files and postprocessors, leaving the processing of
the source files to the native TeX compiler. Consequently, TeX4ht
can handle  the features of TeX-based systems in general, and of
the LaTeX and AMS style files in particular.

%prep
%setup -q
for file in bin/unix/*; do
    if ! %{__grep} '^#!' $file; then
      %{__mv} $file $file.tmp
      /bin/echo "#!/bin/sh" > $file
      %{__cat} $file.tmp >>  $file
      %{__rm} -f $file.tmp
    fi
done
%{_bindir}/find . -name '*.class' -o -name '*.jar' | %{_bindir}/xargs -t %{__rm}

%patch0 -p 1
# debian patch
%patch1 -p1
# hardcoded /usr/share
#%patch2 -p1

chmod a-x src/*.c
cp -p %{SOURCE2} lppl.txt
# unzip the all source for the doc
mkdir doc/
pushd doc/
  unzip %{SOURCE1}
  rm *.zip
popd
mkdir lit/
pushd lit
  unzip %{SOURCE3}
  chmod 0644 *.tex
popd

cp -p %{SOURCE4} %{SOURCE5} %{SOURCE6} %{SOURCE7} lit/

# avoid duplicating the debian patches
patch -p1 < debian/patches/fix_mk4ht.diff
# hardcoded /usr/share
patch -p1 < debian/patches/fix_tex4ht_env.diff
# use the debian man page
patch -p1 < debian/patches/add_manpage.diff
# Makefile used as a source of inspiration
patch -p1 < debian/patches/add_Makefile.diff
patch -p1 < debian/patches/add_xtpipes_support
patch -p1 < debian/patches/Makefile_indep_arch
# scripts and texmf.cnf excerpt for debian not used
patch -p1 < debian/patches/add_scripts_sh.diff
patch -p1 < debian/patches/add_texmf_cnf.diff

# patches for literate sources
patch -p1 < debian/lit/patches/fix_tex4ht_dir.diff
patch -p1 < debian/lit/patches/fix_tex4ht_fonts_4hf.diff
#%patch4 -p1 -b .nohome

#%patch3 -p1 -b .rebuild

chmod a+x debian/lit/rebuild.sh

(cd debian/images; for i in *.uue; do uudecode $i; done; mv *.png ../html)

find  texmf -type f -exec chmod a-x \{\} \;

%build
cd src
CFLAGS="%{optflags} -DHAVE_STRING_H -DHAVE_DIRENT_H -DHAVE_UNISTD_H \
 -DHAVE_SYS_DIR_H -DKPATHSEA -DENVFILE=\"%{_texmf}/tex4ht/base/unix/tex4ht.env\""
LDFLAGS=-lkpathsea
%{__cc} -o tex4ht $CFLAGS tex4ht.c $LDFLAGS
%{__cc} -o t4ht $CFLAGS t4ht.c $LDFLAGS
cd ..

# beware of the %% that have to be protected as %%%%
%{__sed} \
  -e "s;^i.*/ht-fonts/;i%{_texmf}/tex4ht/ht-fonts/;" \
  -e "s;^tpath/tex/;t%{_texmf}/;" \
  -e "s;%%%%~/texmf-dist/;%{_texmf}/;" \
  -e 's;^\(\.[^ ]\+\) java;\1 %{_jvmdir}/jre/bin/java;' \
 texmf/tex4ht/base/unix/tex4ht.env > tex4ht.env

%if %with java
cd src/java
mkdir classes
javac -d classes -source 1.5 *.java */*.java */*/*.java
jar cfm tex4ht.jar manifest -C classes .
cd ..
%endif

%install
%{__rm} -rf %{buildroot}

mkdir -p $RPM_BUILD_ROOT%{_bindir} $RPM_BUILD_ROOT%{_scriptsdir}
install -m755 src/tex4ht $RPM_BUILD_ROOT%{_bindir}
install -m755 src/t4ht $RPM_BUILD_ROOT%{_bindir}
#install -m755 bin/ht/unix/* $RPM_BUILD_ROOT%{_bindir}
install -p -m755 bin/unix/* $RPM_BUILD_ROOT%{_scriptsdir}
for script in httex htlatex httexi htcontext htxetex htxelatex mk4ht; do
  install -p -m755 bin/unix/$script $RPM_BUILD_ROOT%{_bindir}
done
install -p -m755 bin/unix/ht $RPM_BUILD_ROOT%{_bindir}/tex4ht-ht
##install -p -m644 src/tex4ht.jar $RPM_BUILD_ROOT%{_scriptsdir}

mkdir -p $RPM_BUILD_ROOT%{_texmf}/tex4ht/base/unix
cp tex4ht.env $RPM_BUILD_ROOT%{_texmf}/tex4ht/base/unix

pushd texmf
cp -pr tex4ht/ht-fonts $RPM_BUILD_ROOT%{_texmf}/tex4ht
cp -pr tex4ht/xtpipes $RPM_BUILD_ROOT%{_texmf}/tex4ht

mkdir -p $RPM_BUILD_ROOT%{_texmf}/tex/generic
cp -pr tex/generic/tex4ht $RPM_BUILD_ROOT%{_texmf}/tex/generic
popd

cp -pr debian/html tutorial

sed 's/Debian packaged/Debian and Fedora packaged/' debian/README.kpathsea \
   > README.kpathsea

mkdir -p $RPM_BUILD_ROOT%{_mandir}/man1
sed -e 's;@SCRIPTSDIR@;%{_scriptsdir};' \
 -e 's;@TEX4HTDIR@;%{_texmf}/tex4ht/base/unix;' \
 -e 's;@TEXMFCNF@;%{_texmf}/web2c/texmf.cnf;' \
 -e 's;@HTFDIR@;%{_texmf}/tex4ht/ht-fonts;' \
 -e 's;@TEXDIR@;%{_texmf}/tex/generic/tex4ht;g' \
 src/tex4ht.man > $RPM_BUILD_ROOT%{_mandir}/man1/tex4ht.1

%if %with java
%{__mkdir_p} %{buildroot}%{_javadir}
%{__cp} -a src/java/tex4ht.jar %{buildroot}%{_javadir}/%{name}-%{version}.jar
%{__ln_s} %{_javadir}/%{name}.jar $RPM_BUILD_ROOT%{_scriptsdir}
%{__ln_s} %{name}-%{version}.jar %{buildroot}%{_javadir}/%{name}.jar

%endif

%clean
%{__rm} -rf %{buildroot}

%post
if [ -x %{_bindir}/texhash ]; then
    %{_bindir}/texhash 2>/dev/null || :
fi

%if %with java
%{update_gcjdb}
%endif

%postun
if [ -x %{_bindir}/texhash ]; then
    %{_bindir}/texhash 2>/dev/null || :
fi

%if %with java
%{clean_gcjdb}
%endif

%files
%defattr(0644,root,root,0755)
%doc lppl.txt doc tutorial README.kpathsea
%attr(0755,root,root) %{_bindir}/*
%{_datadir}/texmf/tex/generic/%{name}
%{_datadir}/texmf/%{name}
%{_mandir}/man1/tex4ht.1*
%{_scriptsdir}/
%if %with java
%{_javadir}/*
%endif
