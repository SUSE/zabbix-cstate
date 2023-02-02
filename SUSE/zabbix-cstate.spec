#
# spec file for package zabbix-cstate
#
# Copyright (c) 2023 Georg Pfuetzenreuter for SUSE LLC
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via https://bugs.opensuse.org/
#


Name:           zabbix-cstate
Version:        git+c2765f9
Release:        0
Group:          System/Monitoring
Summary:        Synchronize Zabbix with cstate
License:        EUPL-1.2
URL:            https://github.com/SUSE/zabbix-cstate.git
Source:         _service
BuildRequires:  pkgconfig(systemd)
BuildRequires:  sysuser-tools
Requires:       python3-Flask
Requires:       python3-waitress
BuildArch:      noarch
%sysusers_requires

%description
Listens for Zabbix service action webhooks and updates cstate status page entries respectively.

%prep
mv %{_sourcedir}/%{name}-%{version}/* .

%build
%sysusers_generate_pre SUSE/system-user-%{name}.conf %{name} system-user-%{name}.conf

%install
install -Dm0755 %{name}.py %{buildroot}%{_bindir}/%{name}
install -Dm0644 SUSE/%{name}.sysconfig %{buildroot}%{_fillupdir}/sysconfig.%{name}

install -d %{buildroot}%{_docdir}/%{name} %{buildroot}%{_unitdir} %{buildroot}%{_sysusersdir} %{buildroot}%{_sbindir}
install -m0755 Zabbix/* %{buildroot}%{_docdir}/%{name}
install -m0644 SUSE/%{name}.service %{buildroot}%{_unitdir}
install -m0644 SUSE/system-user-%{name}.conf %{buildroot}%{_sysusersdir}
ln -s %{_sbindir}/service %{buildroot}%{_sbindir}/rc%{name}

%pre -f %{name}.pre
%service_add_pre %{name}.service

%post
%{fillup_only -n %{name}}
%service_add_post %{name}.service

%preun
%service_del_preun %{name}.service

%postun
%service_del_postun %{name}.service

%files
%license LICENSE
%doc README.md Zabbix/*
%{_bindir}/%{name}
%{_sbindir}/rc%{name}
%{_fillupdir}/sysconfig.%{name}
%{_sysusersdir}/system-user-%{name}.conf
%{_unitdir}/%{name}.service

%changelog
