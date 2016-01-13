Name:           canvas
Version:        0.1
Release:        3%{?dist}
Summary:        User level profile and system management

Group:          System Environment/Base
License:        AGPLv3
URL:            https://github.com/kororaproject/kp-canvas
Source0:        %{name}-%{version}.tar.gz

BuildRequires:  python3-devel gzip
Requires:       python3 python3-argcomplete python3-prettytable


%description
%{summary}.


%prep
%setup -q


%install
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{python3_sitelib}/canvas
mkdir -p %{buildroot}%{_mandir}/man1

install -m 0755 client/canvas %{buildroot}%{_bindir}/
install -m 0755 client/canvasd %{buildroot}%{_bindir}/
install -m 0644 client/man/canvas %{buildroot}%{_mandir}/man1/canvas.1
install -m 0644 server/man/canvasd %{buildroot}%{_mandir}/man1/canvasd.1

cp -a client/lib/canvas/* %{buildroot}%{python3_sitelib}/canvas/

gzip %{buildroot}%{_mandir}/man1/canvas.1
gzip %{buildroot}%{_mandir}/man1/canvasd.1

%clean
rm -rf %{buildroot}


%files
%{_bindir}/canvas
%{_bindir}/canvasd
%{python3_sitelib}/canvas/
%{_mandir}/man1/canvas*


%changelog
* Wed Jan 13 2016 Chris Smart <csmart@kororaproject.org> - 0.1-3
- Support client session

* Sun Jan 10 2016 Chris Smart <csmart@kororaproject.org> - 0.1-2
- Rename binaries from cnvs to canvas, to make it easier
- Add basic man pages

* Tue Nov  3 2015 Ian Firns <firnsy@kororaproject.org> - 0.1-1
- Initial spec.

