%define unmangled_name protonvpn-gui
%define logo_name protonvpn-logo.svg
%define desktop_name protonvpn.desktop
%define version 1.12.0
%define release 1

Prefix: %{_prefix}

Name: %{unmangled_name}
Version: %{version}
Release: %{release}
Summary: Official Proton VPN GUI

Group: ProtonVPN
License: GPLv3
Url: https://github.com/ProtonVPN
Vendor: Proton Technologies AG <opensource@proton.me>
Source0: %{unmangled_name}-%{version}.tar.gz
Source3: %{desktop_name}
Source4: %{logo_name}
BuildArch: noarch
BuildRoot: %{_tmppath}/%{unmangled_name}-%{version}-%{release}-buildroot

BuildRequires: python3-devel
BuildRequires: python3-setuptools
BuildRequires: desktop-file-utils
Requires: python3-protonvpn-nm-lib >= 3.4.0
Requires: python3-gobject
Requires: python3-psutil
Requires: gtk3
Requires: webkit2gtk3
Suggests: libappindicator-gtk3
Suggests: gnome-tweaks
Suggests: gnome-shell-extension-appindicator

%{?python_disable_dependency_generator}

%description
Official Proton VPN Graphical User Interface.


%prep
%setup -n %{unmangled_name}-%{version} -n %{unmangled_name}-%{version}

%build
python3 setup.py build

%install
desktop-file-install --dir=%{buildroot}%{_datadir}/applications %{SOURCE3}
desktop-file-validate %{buildroot}%{_datadir}/applications/%{desktop_name}
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/scalable/apps
cp %{SOURCE4} %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/%{logo_name}
python3 setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%{python3_sitelib}/protonvpn_gui/
%{python3_sitelib}/protonvpn_gui-%{version}*.egg-info/
%{_datadir}/applications/%{desktop_name}
%{_datadir}/icons/hicolor/scalable/apps/%{logo_name}
%defattr(-,root,root)

%changelog
* Tue Oct 18 2022 Proton Technologies AG <opensource@proton.me> 1.12.0-1
- Fix: Ensure that whenever session is invalid, user is logged out.

* Thu Sep 22 2022 Proton Technologies AG <opensource@proton.me> 1.11.0-6
- Drop F34-35 and add F37

* Thu Sep 01 2022 Proton Technologies AG <opensource@proton.me> 1.11.0-5
- Fix: If session is invalid, logout and inform the user about it.
- Fix: Stop displaying new brand dialog on new login.

* Tue May 31 2022 Proton Technologies AG <opensource@proton.me> 1.10.0-2
- Fix: New brand dialog will now only appear once after the dashboard has been loaded

* Mon May 30 2022 Proton Technologies AG <opensource@proton.me> 1.9.0-2
- Fix: Update taskbar icon

* Fri Apr 22 2022 Proton Technologies AG <opensource@proton.me> 1.9.0-1
- Introducing Proton's refreshed look. As we continue to make privacy accessible to everyone, we've updated our apps to provide you with an even better experience with our services. Proton - Privacy by default

* Tue Mar 29 2022 Proton Technologies AG <opensource@proton.me> 1.8.0-2
- Improve: Display error message if link buttons at login can not be reahced

* Thu Nov 11 2021 Proton Technologies AG <opensource@proton.me> 1.7.0-11
- Improve: Handle accounting use cases

* Thu Nov 04 2021 Proton Technologies AG <opensource@proton.me> 1.6.0-1
- Improve: Further improve memory management to avoid potential leaks

* Tue Nov 02 2021 Proton Technologies AG <opensource@proton.me> 1.5.2-1
- Hotfix: Update event dialog and fix typo

* Tue Oct 26 2021 Proton Technologies AG <opensource@proton.me> 1.5.1-1
- Hotfix: Fixed issue with search not working

* Fri Oct 15 2021 Proton Technologies AG <opensource@proton.me> 1.5.0-7
- Feature: Handle and display events
- Fix: Memory leak
- Improve: Exception handling

* Thu Oct 14 2021 Proton Technologies AG <opensource@proton.me> 1.4.1-1
- Hotfix: Add missing dependency for Webkit

* Fri Sep 24 2021 Proton Technologies AG <opensource@proton.me> 1.4.0-1
- Handle human verification

* Mon Aug 09 2021 Proton Technologies AG <opensource@proton.me> 1.3.0-7
- Feature: Add troubleshooting dialog, including support for alternative routing
- Imprving server list switching UX to/from Secure Core

* Fri Jul 30 2021 Proton Technologies AG <opensource@proton.me> 1.2.0-1
- Fix: Logs should be using UTC time
- Fix: Display window icons (minimize, maximize and close)
- Fix: Unable to update server list after 15min (crash report would appear on certain distros)

* Fri Jul 30 2021 Proton Technologies AG <opensource@proton.me> 1.1.1-1
- Hotfix: Fix Gio.Task.run_in_thread issue

* Thu Jul 01 2021 Proton Technologies AG <opensource@proton.me> 1.1.0-7
- Enhancement: Improve GUI responsiveness; prevent the GUI from resizing on X axis

* Tue Jun 22 2021 Proton Technologies AG <opensource@proton.me> 1.0.1-1
- Hotfix: Display force disable connectivity check message in case of failure

* Mon May 24 2021 Proton Technologies AG <opensource@proton.me> 1.0.0-1
- Update package to stable

* Mon May 24 2021 Proton Technologies AG <opensource@proton.me> 0.8.0-2
- Feature: Add button to get logs

* Mon May 24 2021 Proton Technologies AG <opensource@proton.me> 0.7.3-3
- Add support for python3-protonvpn-nm-lib 3.2.0

* Tue May 11 2021 Proton Technologies AG <opensource@proton.me> 0.7.2-1
- Fix crash when dummy indicator is used in the absence of tray dependency

* Tue May 11 2021 Proton Technologies AG <opensource@proton.me> 0.7.1-4
- Fix quick settings invisible blocking overlay, preventing from pressing on quick setting buttons
- Fix tray quick connect and disconnect buttons, so that they're contextually aware of VPN status
- Display incompatibility dialog on systems that GUI dependencies can not be met
- Hide quick connect tray item on login window
- Update GUI and tray after reconnecting to VPN from suspend or network change

* Mon May 10 2021 Proton Technologies AG <opensource@proton.me> 0.7.0-3
- Feature: add sys-tray icon
- Add missing indicator dependency
- Add extra packages that are needed for indicator/tray to work on fedora

* Thu May 06 2021 Proton Technologies AG <opensource@proton.me> 0.6.2-2
- Add warning message if kill switch is blocking all connections
- Display only countries when connected to secure core, on dashboard
- Display streaming icons if present
- Add space to secure core sub-servers flags and label

* Wed May 05 2021 Proton Technologies AG <opensource@proton.me> 0.6.1-2
- Fix connect button glitch
- Add info icon hover effect
- Add timetout to when fetching IP
- Improve dashboard UI after disconnecting
- Fix quick connect/disconnect glitch

* Tue May 04 2021 Proton Technologies AG <opensource@proton.me> 0.6.0-1
- Fix quick connect loop
- Add possibility to login upon pressing Enter after filling in credentials on login window
- Make possibile to add extra content to dialog via a method
- Modify connecting overlay message display
- Display an appropriate error on failed login
- Other color and styling changes 

* Wed Apr 21 2021 Proton Technologies AG <opensource@proton.me> 0.5.0-1
- Add new server list headers
- Feature: Add streaming information for servers that provide streaming services
- Update server list styling

* Wed Apr 21 2021 Proton Technologies AG <opensource@proton.me> 0.4.0-2
- Add about dialog; display current version
- Add .desktop file

* Fri Apr 16 2021 Proton Technologies AG <opensource@proton.me> 0.3.0-1
- Adjust and displays server load colour
- Implement server multi-features aka feature bitmap
- Disable permanent Kill Switch from login window if it is enabled

* Wed Apr 14 2021 Proton Technologies AG <opensource@proton.me> 0.2.0-1
- Implement logout and quit
- Feature: filter countries

* Fri Apr 2 2021 Proton Technologies AG <opensource@proton.me> 0.1.0-2
- Add quick-settings buttons
- Add reconnetion logic after clicking on quick-settings buttons
- Fix secure core server list reload
- Fix issue when connecting to servers with long names

* Mon Feb 22 2021 Proton Technologies AG <opensource@proton.me> 0.0.3-1
- First package

