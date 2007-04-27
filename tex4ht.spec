%define name	tex4ht
%define version 1.0.2005_07_17_1932
%define release %mkrel 2

Name:		%{name}
Version:	%{version}
Release:	%{release}
Summary:	Translates tex (and latex) into html+gifs or xml+mathml+gifs
URL:		http://www.cse.ohio-state.edu/~gurari/
License:	Latex Project Public License
Group:		Publishing
Source:		http://www.cse.ohio-state.edu/~gurari/TeX4ht/fix/%{name}-%{version}.tar.bz2
Patch:		%{name}-1.0.2005_05_11_0314.path.patch.bz2
Requires:	tetex
BuildRoot:	%{_tmppath}/%{name}-%{version}

%description 
A translator/compiler which translates tex and latex into html+gifs or
xml+mathml+gifs.

%prep
%setup -q
%patch
for file in bin/unix/*; do
	if ! grep '^#!' $file; then
		mv $file $file.tmp
		echo "#!/bin/sh" > $file
		cat $file.tmp >>  $file
		rm -f $file.tmp
	fi
done

%build
cd src
gcc -o tex4ht tex4ht.c \
	$RPM_OPT_FLAGS \
	-DENVFILE='"%{_datadir}/texmf/tex4ht/base/unix/tex4ht.env"' \
	-DHAVE_DIRENT_H
gcc -o t4ht t4ht.c \
	$RPM_OPT_FLAGS \
	-DENVFILE='"%{_datadir}/texmf/tex4ht/base/unix/tex4ht.env"' \
	-DHAVE_DIRENT_H

%install
rm -rf %{buildroot}
install -d -m 755 %{buildroot}%{_bindir}
install -m 755 src/t4ht src/tex4ht %{buildroot}%{_bindir}
install -m 755 bin/unix/* %{buildroot}%{_bindir}

install -d -m 755 %{buildroot}%{_datadir}/texmf/tex/generic
cp -a texmf/tex/generic/tex4ht %{buildroot}%{_datadir}/texmf/tex/generic

install -d -m 755 %{buildroot}%{_datadir}/texmf/tex4ht
cp -a texmf/tex4ht/ht-fonts %{buildroot}%{_datadir}/texmf/tex4ht

install -d -m 755 %{buildroot}%{_datadir}/texmf/tex4ht/base/unix
install -m 644 texmf/tex4ht/base/unix/tex4ht.env %{buildroot}%{_datadir}/texmf/tex4ht/base/unix

find %{buildroot}%{_datadir}/texmf/ -type f -exec chmod 644 {} \;

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%{_datadir}/texmf/tex/generic/%{name}
%{_datadir}/texmf/%{name}
%{_bindir}/*

%post -p /usr/bin/texhash
