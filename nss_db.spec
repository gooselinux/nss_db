# 4.8 makes libpthread a hard requirement
# 4.7 has a heavier footprint
%define db_version 4.6.21.NC
Summary: An NSS library for the Berkeley DB
Name: nss_db
Version: 2.2.3
Release: 0.3.pre1%{?dist}
Source: ftp://sources.redhat.com/pub/glibc/old-releases/nss_db-%{version}pre1.tar.gz
Source1: http://download.oracle.com/berkeley-db/db-%{db_version}.tar.gz
Source2: db-getent-Makefile
Source3: fail-setfscreatecon.c
URL: http://sources.redhat.com/glibc/
Patch0: nss_db-2.2.3-external.patch
Patch1: nss_db-2.2.3-automake.patch
Patch2: nss_db-2.2-uniqdb.patch
Patch4: nss_db-2.2.3-selinux.patch
Patch5: nss_db-2.2-db-4.3.patch
Patch6: nss_db-2.2-enoent.patch
Patch7: nss_db-2.2-initialize.patch
Patch8: nss_db-2.2-order.patch
Patch9: nss_db-2.2-lib64.patch
Patch10: nss_db-2.2-glibc.patch
Patch11: nss_db-2.2-makedb-atomic.patch
Patch12: 200-set-db-environment.patch
Patch100: db-4.6.18-glibc.patch
Patch101: http://www.oracle.com/technology/products/berkeley-db/db/update/4.6.21/patch.4.6.21.1
Patch102: http://www.oracle.com/technology/products/berkeley-db/db/update/4.6.21/patch.4.6.21.2
Patch103: http://www.oracle.com/technology/products/berkeley-db/db/update/4.6.21/patch.4.6.21.3
Patch104: http://www.oracle.com/technology/products/berkeley-db/db/update/4.6.21/patch.4.6.21.4
# DB is under the Sleepycat (Oracle) license.
# nss_db is under the LGPLv2+ license.
License: Sleepycat and LGPLv2+
Group: System Environment/Libraries
BuildRequires: autoconf, automake15, ed, gettext-devel, libtool, libselinux-devel
Conflicts: glibc < 2.2
Requires: glibc >= 2.3.3-52
Requires: make
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Obsoletes: %{name}-compat < 2.2-34

%define _filter_GLIBC_PRIVATE 1

%description
Nss_db is a set of C library extensions which allow Berkeley Databases
to be used as a primary source of aliases, ethers, groups, hosts,
networks, protocol, users, RPCs, services, and shadow passwords
(instead of or in addition to using flat files or NIS). Install nss_db
if your flat name service files are too large and lookups are slow.

%prep
%setup -q -a 1 -n nss_db-%{version}pre1
cp %{SOURCE2} .
%patch0 -p1 -b .external
%patch1 -p1 -b .automake
%patch2 -p1 -b .uniqdb
%patch4 -p1 -b .selinux
pushd src
%patch5 -p1 -b .db-4.3
%patch6 -p1 -b .enoent
%patch7 -p1 -b .initialize
%patch8 -p1 -b .order
popd
%patch9 -p1 -b .lib64
pushd src
%patch10 -p1 -b .glibc
%patch11 -p1 -b .makedb-atomic
popd
%patch12 -p1 -b .set-db-environment
cp %{_datadir}/gettext/config.rpath .
rm -f config.guess config.sub ltmain.sh
autoreconf -i

pushd db-%{db_version}
%patch100 -p1 -b .glibc
%patch101 -p0 -b .1
%patch102 -p0 -b .2
%patch103 -p0 -b .3
%patch104 -p0 -b .4
popd

mkdir db-build

%build
dbdir=`pwd`/db-instroot
CFLAGS="$RPM_OPT_FLAGS -fno-strict-aliasing" ; export CFLAGS

pushd db-build
echo db_cv_mutex=UNIX/fcntl > config.cache
../db-%{db_version}/dist/configure -C \
	--disable-compat185 \
	--disable-cryptography \
	--disable-cxx \
	--disable-diagnostic \
	--disable-dump185 \
	--disable-hash \
	--disable-java \
	--disable-queue \
	--disable-replication \
	--disable-rpc \
	--disable-shared \
	--disable-tcl \
	--with-pic \
	--with-uniquename=_nssdb \
	--prefix=$dbdir \
	--libdir=$dbdir/lib
make all install
popd

CPPFLAGS=-I${dbdir}/include ; export CPPFLAGS
LDFLAGS=-L${dbdir}/lib ; export LDFLAGS
%configure --with-db=${dbdir} --with-selinux
make

%install
rm -rf ${RPM_BUILD_ROOT}
install -m755 -d ${RPM_BUILD_ROOT}/{%{_lib},/var/db,%{_bindir}}
install -m644 -p db-Makefile ${RPM_BUILD_ROOT}/var/db/Makefile
make install DESTDIR=$RPM_BUILD_ROOT MKINSTALLDIRS='$(srcdir)/mkinstalldirs'
/sbin/ldconfig -n $RPM_BUILD_ROOT/%{_lib} $RPM_BUILD_ROOT/%{_libdir}

%{find_lang} %{name}

%clean
rm -rf ${RPM_BUILD_ROOT}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files -f %{name}.lang
%defattr(-,root,root)
%doc AUTHORS COPYING* ChangeLog NEWS README THANKS db-getent-Makefile
/%{_lib}/libnss_db-%{version}.so
/%{_lib}/libnss_db.so.?
%{_libdir}/libnss_db.so
%{_bindir}/makedb
%config(noreplace) /var/db/Makefile

%changelog
* Wed Apr  7 2010 Nalin Dahyabhai <nalin@redhat.com> - 2.2.3-0.3.pre1
- import Kees Cook's patch to fix accidental leakage of part of ./DB_CONFIG
  (#580192, CVE-2010-0826)

* Fri Feb  5 2010 Nalin Dahyabhai <nalin@redhat.com> - 2.2.3-0.2.pre1
- correct some tests in the patch for detecting SELinux support (#562052)

* Mon Jan 25 2010 Nalin Dahyabhai <nalin@redhat.com> - 2.2.3-0.1.pre1
- update to 2.2.3pre1, which you can still get from upstream
- build with -fno-strict-aliasing to avoid problems triggered by strict aliasing
- package the translations

* Mon Jan 25 2010 Nalin Dahyabhai <nalin@redhat.com> - 2.2-46
- update to DB 4.6.21, which you can still get from upstream

* Mon Nov 30 2009 Dennis Gregorovic <dgregor@redhat.com> - 2.2-45.1
- Rebuilt for RHEL 6

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.2-45
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.2-44
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Aug 11 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 2.2-43
- fix license tag

* Thu Aug  7 2008 Nalin Dahyabhai <nalin@redhat.com> - 2.2-42%{?dist}
- turn off crypto, hash, queue, and replication support, which aren't used,
  reduces the package size, and sidesteps needing to patch anything for #347741
- create and populate new db files, moving them in place afterward so that we
  never have a partially-built db file "live" (patch from Kelsey Cummings,
  CentOS #1987)

* Tue Jul 22 2008 Nalin Dahyabhai <nalin@redhat.com> - 2.2-41%{?dist}
- fix an error in the db-getent-Makefile which kept it from working at all

* Mon Mar  3 2008 Nalin Dahyabhai <nalin@redhat.com> - 2.2-40%{?dist}
- add a dist tag to make pushing this same package as an update easier

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 2.2-40
- Autorebuild for GCC 4.3

* Tue Nov  6 2007 Nalin Dahyabhai <nalin@redhat.com> - 2.2-39
- when setting file contexts for creation of new files, only fail outright
  if we were in enforcing mode and the file needed to be given a specific
  label (#368501)

* Tue Aug 14 2007 Nalin Dahyabhai <nalin@redhat.com> - 2.2-38
- adapt to open-is-a-macro cases

* Mon Aug 13 2007 Nalin Dahyabhai <nalin@redhat.com> - 2.2-37
- update to use DB 4.6.18, swiping needed patches from the db4 package
- clarify license tag

* Mon Feb 19 2007 Nalin Dahyabhai <nalin@redhat.com> - 2.2-36
- update to use DB 4.5.20
- make our obsoletion of nss_db-compat a versioned one
- mark the makefile %%config(noreplace)
- change buildroot to the prescribed value
- change buildprereq to buildrequires to make rpmlint happy

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 2.2-35.1
- rebuild

* Fri Feb 17 2006 Nalin Dahyabhai <nalin@redhat.com> - 2.2-35
- add missing 'ed' builddep
- set LDFLAGS and CPPFLAGS so that our local copy of DB is more likely to be
  found by the configure script

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 2.2-34.2.1
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 2.2-34.2
- rebuilt for new gcc4.1 snapshot and glibc changes

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Wed Sep 28 2005 Nalin Dahyabhai <nalin@redhat.com> 2.2-34
- own the soname symlink which we provide in /%%{_lib} (#169288)
- drop compat subpackage completely

* Tue Aug 30 2005 Nalin Dahyabhai <nalin@redhat.com> 2.2-33
- update to db 4.3.28
- correct a use of uninitialized memory in the bundled libdb (Arjan van de Ven)
- obsolete the compat package, which is useless because current glibc wouldn't
  use it anyway

* Tue Apr 26 2005 Nalin Dahyabhai <nalin@redhat.com>
- set errno to ENOENT by default so that we don't leave stale errno values
  around in error cases (#152467)
- clear the entire key DBT before handing it to a get() function

* Tue Mar 29 2005 Nalin Dahyabhai <nalin@redhat.com> 2.2-32
- set errno to ENOENT when returning NSS_STATUS_NOTFOUND (#152467, Dave Lehman)

* Wed Mar 16 2005 Nalin Dahyabhai <nalin@redhat.com> 2.2-31
- rebuild with new gcc, missed it by that much

* Mon Feb 28 2005 Nalin Dahyabhai <nalin@redhat.com> 2.2-30
- update to DB 4.3 (#140094)
- add sample getent-based makefile as a doc file
- pass S_IFREG to matchpathcon() to properly match contexts which are earmarked
  for only files

* Wed Oct 20 2004 Nalin Dahyabhai <nalin@redhat.com> 2.2-29
- give makedb support for setting labels on files, and use it (#136522)

* Thu Jul 29 2004 Nalin Dahyabhai <nalin@redhat.com> 2.2-28
- set _filter_GLIBC_PRIVATE instead of overriding findrequires, so that file
  colors get marked correctly (originally #128436)

* Tue Jul  6 2004 Nalin Dahyabhai <nalin@redhat.com> 2.2-27
- only provide a -compat subpackage on platforms where glibc provides
  compat NSS modules (%%{ix86})
- make -compat depend on the same version of the non-compat package

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Mon Jan  5 2004 Nalin Dahyabhai <nalin@redhat.com> 2.2-24
- disable use of RPM's internal dependency generator, which was preventing
  the filtering out of glibc private dependencies (#112849)

* Tue Dec  2 2003 Nalin Dahyabhai <nalin@redhat.com> 2.2-23
- find bundled libdb again (#111004)

* Tue Aug 12 2003 Nalin Dahyabhai <nalin@redhat.com> 2.2-21.1
- rebuild

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed Jun  4 2003 Nalin Dahyabhai <nalin@redhat.com> 2.2-21
- disable mutex locking

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Tue Jan 14 2003 Nalin Dahyabhai <nalin@redhat.com> 2.2-19
- force use of assembly mutexes on %%{ix86} to avoid dependency on libpthread

* Thu Nov 14 2002 Nalin Dahyabhai <nalin@redhat.com> 2.2-18
- disable various language bindings when building the bundled DB library
- remove unpackaged files from the buildroot in %%install
- don't install the compat version on arches where if we don't need one

* Fri Jun 21 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Sun May 26 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Fri May 17 2002 Nalin Dahyabhai <nalin@redhat.com> 2.2-15
- rebuild in new environment

* Mon Apr 15 2002 Nalin Dahyabhai <nalin@redhat.com> 2.2-14
- rebuild

* Mon Apr 15 2002 Nalin Dahyabhai <nalin@redhat.com> 2.2-13
- whoops, __set_errno() is a glibc-internal symbol as well (#63373)

* Wed Apr  3 2002 Nalin Dahyabhai <nalin@redhat.com> 2.2-12
- filter out dependency on glibc private symbols

* Tue Apr  2 2002 Nalin Dahyabhai <nalin@redhat.com> 2.2-11
- don't use libc-internal symbols and interfaces

* Mon Mar 25 2002 Nalin Dahyabhai <nalin@redhat.com> 2.2-10
- rebuild

* Fri Feb 22 2002 Nalin Dahyabhai <nalin@redhat.com> 2.2-9
- rebuild

* Mon Feb 18 2002 Nalin Dahyabhai <nalin@redhat.com> 2.2-8
- build using a bundled Berkeley DB with a unique name to avoid possible symbol
  collisions with binaries using different versions (mix multiple versions of
  any shared library in a single process, observe as wackiness ensues)

* Wed Jan 23 2002 Nalin Dahyabhai <nalin@redhat.com> 2.2-7
- rebuild against db4-devel

* Mon Aug  6 2001 Nalin Dahyabhai <nalin@redhat.com> 2.2-6
- require db3-devel at build-time, not db3 (#49544)

* Tue May 25 2001 Nalin Dahyabhai <nalin@redhat.com>
- don't include copies of the shared libraries with the soname for their names

* Thu May 24 2001 Nalin Dahyabhai <nalin@redhat.com>
- rebuild in new environment

* Tue Feb 27 2001 Nalin Dahyabhai <nalin@redhat.com>
- don't own /var/db, the filesystem package does

* Tue Feb 13 2001 Nalin Dahyabhai <nalin@redhat.com>
- require make (#27313)
- add the docs to the package

* Tue Dec 19 2000 Nalin Dahyabhai <nalin@redhat.com>
- update to 2.2

* Thu Sep 14 2000 Jakub Jelinek <jakub@redhat.com>
- separate from db3
