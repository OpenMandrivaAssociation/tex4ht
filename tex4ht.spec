%bcond_without java
%define gcj_support 1

Name:           tex4ht
Version:        1.0.2007_10_17_1737
Release:        %mkrel 2
Epoch:          1
Summary:        LaTeX and TeX for Hypertext
License:        Distributable
Group:          Publishing
URL:            http://www.cse.ohio-state.edu/~gurari/TeX4ht/
Source0:        http://www.cse.ohio-state.edu/~gurari/TeX4ht/fix/tex4ht-%{version}.tar.gz
Patch0:         %{name}-1.0.2005_05_11_0314.path.patch
Requires(post): tetex-latex
%if %with java
%if %{gcj_support}
BuildRequires:  java-gcj-compat-devel
%else
BuildRequires:  java-devel >= 0:1.5.0
%endif
BuildRequires:  jpackage-utils
%endif
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root

%description 
TeX4ht is a highly configurable TeX-based authoring system for
producing hypertext. It interacts with TeX-based applications
through style files and postprocessors, leaving the processing of
the source files to the native TeX compiler. Consequently, TeX4ht
can handle  the features of TeX-based systems in general, and of
the LaTeX and AMS style files in particular.

%prep
%setup -q
%patch0 -p0
for file in bin/unix/*; do
    if ! %{__grep} '^#!' $file; then
      %{__mv} $file $file.tmp
      /bin/echo "#!/bin/sh" > $file
      %{__cat} $file.tmp >>  $file
      %{__rm} -f $file.tmp
    fi
done
%{_bindir}/find . -name '*.class' -o -name '*.jar' | %{_bindir}/xargs -t %{__rm}

%build
cd src
%{__cc} -o tex4ht tex4ht.c \
        %{optflags} \
        -DENVFILE='"%{_datadir}/texmf/tex4ht/base/unix/tex4ht.env"' \
        -DHAVE_DIRENT_H
%{__cc} -o t4ht t4ht.c \
        %{optflags} \
        -DENVFILE='"%{_datadir}/texmf/tex4ht/base/unix/tex4ht.env"' \
        -DHAVE_DIRENT_H
%if %with java
cd java
%{javac} -nowarn -source 1.5 -target 1.5 `%{_bindir}/find . -type f -name '*.java'`
%endif

%install
%{__rm} -rf %{buildroot}

%{__mkdir_p} %{buildroot}%{_bindir}
%{__cp} -a src/t4ht src/tex4ht %{buildroot}%{_bindir}
%{__cp} -a bin/unix/* %{buildroot}%{_bindir}
%{__perl} -pi -e 's|~/tex4ht.dir|%{_datadir}|g' %{buildroot}%{_bindir}/*

%{__mkdir_p} %{buildroot}%{_datadir}/texmf/tex/generic
%{__cp} -a texmf/tex/generic/tex4ht %{buildroot}%{_datadir}/texmf/tex/generic

%{__mkdir_p} %{buildroot}%{_datadir}/texmf/tex4ht
%{__cp} -a texmf/tex4ht/ht-fonts %{buildroot}%{_datadir}/texmf/tex4ht

%{__mkdir_p} %{buildroot}%{_datadir}/texmf/tex4ht/base/unix
%{__cp} -a texmf/tex4ht/base/unix/tex4ht.env %{buildroot}%{_datadir}/texmf/tex4ht/base/unix

%if %with java
%{__mkdir_p} %{buildroot}%{_javadir}
(cd src/java && %{jar} cf %{buildroot}%{_javadir}/%{name}-%{version}.jar `%{_bindir}/find . -type f -name '*.class'`)
%{__ln_s} %{name}-%{version}.jar %{buildroot}%{_javadir}/%{name}.jar

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif
%endif

%clean
%{__rm} -rf %{buildroot}

%post
if [ -x %{_bindir}/texhash ]; then
    %{_bindir}/texhash 2>/dev/null || :
fi
%if %with java
%{update_gcjdb}

%postun
%{clean_gcjdb}
%endif

%files
%defattr(0644,root,root,0755)
%attr(0755,root,root) %{_bindir}/*
%{_datadir}/texmf/tex/generic/%{name}
%{_datadir}/texmf/%{name}
%if %with java
%{_javadir}/*
%if %{gcj_support}
%dir %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/*.jar.*
%endif
%endif
