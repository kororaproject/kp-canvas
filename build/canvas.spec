Name:           canvas
Version:        0.5.6
Release:        1%{?dist}
Summary:        User level profile and system management

Group:          System Environment/Base
License:        AGPLv3
URL:            https://github.com/kororaproject/kp-canvas
Source0:        %{name}-%{version}.tar.gz

BuildRequires:  python3-devel gzip
Requires:       python3
Requires:       python3-argcomplete
Requires:       python3-PyYAML
Requires:       python3-kickstart

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
* Wed Oct  4 2017 Ian Firns <firnsy@kororaproject.org> - 0.5.6-1
- Latest upstream version

* Mon Aug 14 2017 Ian Firns <firnsy@kororaproject.org> - 0.5.5-1
- Latest upstream version

* Sun Aug 13 2017 Ian Firns <firnsy@kororaproject.org> - 0.5.4-1
- Latest upstream version

* Wed Aug 10 2017 Ian Firns <firnsy@kororaproject.org> - 0.5.3-1
- Latest upstream version

* Wed Jul 26 2017 Ian Firns <firnsy@kororaproject.org> - 0.5.2-1
- Latest upstream version

* Fri Nov 21 2016 Ian Firns <firnsy@kororaproject.org> - 0.5.1-1
- Latest upstream version

* Fri Sep 23 2016 Ian Firns <firnsy@kororaproject.org> - 0.5-1
- Latest upstream version

* Sat Apr 16 2016 Chris Smart <csmart@kororaproject.org> - 0.2-2
- Latest upstream version

* Tue Feb  2 2016 Ian Firns <firnsy@kororaproject.org> - 0.2-1
- Initial kickstart import and export support

* Wed Jan 13 2016 Chris Smart <csmart@kororaproject.org> - 0.1-3
- Support client session

* Sun Jan 10 2016 Chris Smart <csmart@kororaproject.org> - 0.1-2
- Rename binaries from cnvs to canvas, to make it easier
- Add basic man pages

* Tue Nov  3 2015 Ian Firns <firnsy@kororaproject.org> - 0.1-1
- Initial spec.

