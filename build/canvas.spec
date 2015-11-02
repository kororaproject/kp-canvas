Name:           canvas
Version:        0.1
Release:        1%{?dist}
Summary:        User level profile and system management

Group:          System Environment/Base
License:        AGPLv3
URL:            https://github.com/kororaproject/kp-canvas
Source0:        %{name}-%{version}.tar.gz

BuildRequires:  python3-devel
Requires:       python3


%description
%{summary}.


%prep
%setup -q


%install
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{python3_sitelib}/canvas

install -m 0755 client/cnvs %{buildroot}%{_bindir}/
install -m 0755 client/cnvsd %{buildroot}%{_bindir}/

install -m 0644 client/lib/canvas/* %{buildroot}%{python3_sitelib}/canvas/


%clean
rm -rf %{buildroot}


%files
%{_bindir}/cnvs
%{_bindir}/cnvsd
%{python3_sitelib}/canvas/


%changelog
* Tue Nov  3 2015 Ian Firns <firnsy@kororaproject.org> - 0.1-1
- Initial spec.

