%define LDAP 2
%define MYSQL 0
%define PCRE 1
%define SASL 2
%define TLS 1
%define IPV6 1
%define POSTDROP_GID 90
%define PFLOGSUMM 1

# On Redhat 8.0.1 and earlier, LDAP is compiled with SASL V1 and won't work
# if postfix is compiled with SASL V2. So we drop to SASL V1 if LDAP is
# requested but use the preferred SASL V2 if LDAP is not requested.
# Sometime soon LDAP will build agains SASL V2 and this won't be needed.

%if %{LDAP} <= 1 && %{SASL} >= 2
%undefine SASL
%define SASL 1
%endif

# Do we use db3 or db4 ? If we have db4, assume db4, otherwise db3.
%define dbver db4

# If set to 1 if official version, 0 if snapshot
%define official 1
%define ver 2.1.1
%define releasedate 20040120
%define alternatives 1
%if %{official}
Version: %{ver}
%define ftp_directory official
%else
Version: %{ver}.%{releasedate}
%define ftp_directory experimental
%endif
Release: 1
Epoch: 2

%define tlsno pfixtls-0.8.18-2.1.0-0.9.7d
%if %{PFLOGSUMM}
%define pflogsumm_ver 1.1.0
%endif

# Postfix requires one exlusive uid/gid and a 2nd exclusive gid for its own
# use.  Let me know if the second gid collides with another package.
# Be careful: Redhat's 'mail' user & group isn't unique!
%define postfix_uid    89
%define postfix_user   postfix
%define postfix_gid    89
%define postfix_group  postfix
%define postdrop_group postdrop
%define maildrop_group %{postdrop_group}
%define maildrop_gid   %{POSTDROP_GID}

%define postfix_config_dir  %{_sysconfdir}/postfix
%define postfix_daemon_dir  %{_libexecdir}/postfix
%define postfix_command_dir %{_sbindir}
%define postfix_queue_dir   %{_var}/spool/postfix
%define postfix_doc_dir     %{_docdir}/%{name}-%{version}
%define postfix_sample_dir  %{postfix_doc_dir}/samples
%define postfix_readme_dir  %{postfix_doc_dir}/README_FILES

Name: postfix
Group: System Environment/Daemons
URL: http://www.postfix.org
License: IBM Public License
PreReq: /sbin/chkconfig, /sbin/service, sh-utils
PreReq: fileutils, textutils,
%if %alternatives
PreReq: /usr/sbin/alternatives
%else
Obsoletes: sendmail exim qmail
%endif

PreReq: %{_sbindir}/groupadd, %{_sbindir}/useradd

Provides: MTA smtpd smtpdaemon /usr/bin/newaliases
Summary: Postfix Mail Transport Agent

%if %{official}
Source0: ftp://ftp.porcupine.org/mirrors/postfix-release/%{ftp_directory}/%{name}-%{version}.tar.gz
%else
Source0: ftp://ftp.porcupine.org/mirrors/postfix-release/%{ftp_directory}/%{name}-%{ver}-%{releasedate}.tar.gz
%endif
Source1: postfix-etc-init.d-postfix
Source2: postfix-aliases
Source3: README-Postfix-SASL-RedHat.txt

# Sources 50-99 are upstream [patch] contributions

# A note about the various TLS and IPV6 patch files. TLS was
# originally added to Postfix by Lutz Jaenicke, this is what is in
# Source50. In addition to the source patch it includes documentation
# and examples. Dean Strik created a patch to support IPv6, this was
# taken from the work done by Mark Huizer, and then substantially
# improved by Jun-ichiro 'itojun' Hagino (known as the KAME
# patch). Dean provides his patch in two forms, one with IPv6 only (Source52),
# and one with IPv6 and TLS (Source51). The TLS support in Dean Stick's patch
# comes from the TLS patch done by Lutz Jaenicke. However Dean Strick
# did not include the TLS documentation and examples that are in Lutz
# Jaenicke's tarball. Depending on what this RPM builds we use some
# combination of patches and files from Sources 50-52.
#
# The TLS documentation and examples always comes from Source50, the
# Lutz Jaenicke contribution. We can do this because even if we don't
# use this patch to add TLS, but rather use Dean Strik's tls+ipv6
# patch is still based on Lutz Jaenicke's contribution.
#
# If we are building with IPv6 and no TLS then Source52 is used. If we
# are building with both IPv6 and TLS then Source51 is used and we
# include the doc and examples from Source50, but not Source50's
# patch. If we are building with TLS and no IPv6 then we use the
# original Source50 patch and doc.

Source50: ftp://ftp.aet.tu-cottbus.de/pub/postfix_tls/%{tlsno}.tar.gz
Source51: ftp://ftp.stack.nl/pub/postfix/tls+ipv6/1.21/tls+ipv6-1.24-pf-2.1.1.patch.gz
Source52: ftp://ftp.stack.nl/pub/postfix/tls+ipv6/1.21/ipv6-1.24-pf-2.1.1.patch.gz
%if %{PFLOGSUMM}
Source53: http://jimsun.linxnet.com/downloads/pflogsumm-%{pflogsumm_ver}.tar.gz
%endif

# Sources >= 100 are config files

Source100: postfix-sasl.conf
Source101: postfix-pam.conf

# Patches

Patch1: postfix-2.1.1-config.patch
Patch2: postfix-smtp_sasl_proto.c.patch
Patch3: postfix-alternatives.patch
Patch4: postfix-hostname-fqdn.patch
Patch5: postfix-2.1.1-pie.patch

# Optional patches - set the appropriate environment variables to include
#                    them when building the package/spec file

BuildRoot: %{_tmppath}/%{name}-buildroot

# Determine the different packages required for building postfix
BuildRequires: gawk, perl, sed, ed, %{dbver}-devel, pkgconfig, zlib-devel

Requires: %{dbver}

%if %{LDAP}
BuildRequires: openldap >= 2.0.27, openldap-devel >= 2.0.27
Requires: openldap >= 2.0.27
%endif

%if %{SASL}
BuildRequires: cyrus-sasl >= 2.1.10, cyrus-sasl-devel >= 2.1.10
Requires: cyrus-sasl  >= 2.1.10
%endif

%if %{PCRE}
Requires: pcre
BuildRequires: pcre, pcre-devel
%endif

%if %{MYSQL}
Requires: mysql
BuildRequires: mysql, mysql-devel
%endif

%if %{TLS}
Requires: openssl
BuildRequires: openssl-devel >= 0.9.6
%endif

Provides: /usr/sbin/sendmail /usr/bin/mailq /usr/bin/rmail

%description
Postfix is a Mail Transport Agent (MTA), supporting LDAP, SMTP AUTH (SASL),
TLS

%prep
umask 022

%if %{official}
%setup -q
%else
%setup -q -n %{name}-%{ver}-%{releasedate}
%endif
#
# IPv6 and TLS are sort of hand in hand. We need to apply them in the
# following order:
# - IPv6 + TLS (if both are enabled)
# - IPv6 only
# - TLS only
# The last else block with patch fuzz factor enabled fixes master.cf
# by force if we're compiling without TLS
#
%if %{IPV6} && %{TLS}
echo "TLS and IPv6, patching with %{SOURCE51}"
gzip -dc %{SOURCE51} | patch -p1 -b -z .ipv6tls
%endif

%if %{IPV6} && !%{TLS}
echo "IPv6 Only, patching with %{SOURCE52}"
gzip -dc %{SOURCE52} | patch -p1 -b -z .ipv6
%endif

%if %{TLS}
# It does not matter which TLS patch we are using, we always need the
# doc and examples from Lutz Jaenicke tarball so unpack it now.
gzip -dc %{SOURCE50} | tar xf -
if [ $? -ne 0 ]; then
  exit $?
fi
%endif

%if %{IPV6} && %{TLS}
# TLS and IPv6
%patch1 -p1 -b .config
%endif

%if !%{IPV6} && %{TLS}
echo "TLS Only, patching with %{tlsno}/pfixtls.diff"
patch -p1 < %{tlsno}/pfixtls.diff
%patch1 -p1 -b .config
%endif

%if !%{IPV6} && !%{TLS}
# No TLS. Without the TLS patch the context lines in this patch don't
# match. Set fuzz to ignore all context lines, this is a bit
# dangerous.
patch --fuzz=3 -p1 -b -z .config < %{P:1}
%endif

# Apply obligatory patches
%patch2 -p1 -b .auth
%if %alternatives
%patch3 -p1 -b .alternatives
%endif
%patch4 -p1 -b .postfix-hostname-fqdn
%patch5 -p1 -b .pie

%if %{PFLOGSUMM}
gzip -dc %{SOURCE53} | tar xf -
%endif

# pflogsumm subpackage
%if %{PFLOGSUMM}
%package pflogsumm
Group: System Environment/Daemons
Summary: A Log Summarizer/Analyzer for the Postfix MTA
Requires: perl-Date-Calc
%description pflogsumm
Pflogsumm is a log analyzer/summarizer for the Postfix MTA.  It is
designed to provide an over-view of Postfix activity. Pflogsumm
generates summaries and, in some cases, detailed reports of mail
server traffic volumes, rejected and bounced email, and server
warnings, errors and panics.

%endif

%build
umask 022

CCARGS=-fPIC
AUXLIBS=

%ifarch s390 s390x ppc
CCARGS="${CCARGS} -fsigned-char"
%endif

%if %{LDAP}
  CCARGS="${CCARGS} -DHAS_LDAP"
  AUXLIBS="${AUXLIBS} -L%{_libdir} -lldap -llber"
%endif
%if %{PCRE}
  # -I option required for pcre 3.4 (and later?)
  CCARGS="${CCARGS} -DHAS_PCRE -I/usr/include/pcre"
  AUXLIBS="${AUXLIBS} -lpcre"
%endif
%if %{MYSQL}
  CCARGS="${CCARGS} -DHAS_MYSQL -I/usr/include/mysql"
  AUXLIBS="${AUXLIBS} -L%{_libdir}/mysql -lmysqlclient -lm"
%endif
%if %{SASL}
  %define sasl_v1_lib_dir %{_libdir}/sasl
  %define sasl_v2_lib_dir %{_libdir}/sasl2
  CCARGS="${CCARGS} -DUSE_SASL_AUTH"
  %if %{SASL} <= 1
    %define sasl_lib_dir %{sasl_v1_lib_dir}
    AUXLIBS="${AUXLIBS} -L%{sasl_lib_dir} -lsasl"
  %else
    %define sasl_lib_dir %{sasl_v2_lib_dir}
    CCARGS="${CCARGS} -I/usr/include/sasl"
    AUXLIBS="${AUXLIBS} -L%{sasl_lib_dir} -lsasl2"
  %endif
%endif
%if %{TLS}
  if pkg-config openssl ; then
    CCARGS="${CCARGS} -DHAS_SSL `pkg-config --cflags openssl`"
    AUXLIBS="${AUXLIBS} `pkg-config --libs openssl`"
  else
    CCARGS="${CCARGS} -DHAS_SSL -I/usr/include/openssl"
    AUXLIBS="${AUXLIBS} -lssl -lcrypto"
  fi
%endif

export CCARGS AUXLIBS
make -f Makefile.init makefiles

unset CCARGS AUXLIBS
make DEBUG="" OPT="$RPM_OPT_FLAGS"

%install
umask 022
/bin/rm -rf   $RPM_BUILD_ROOT
/bin/mkdir -p $RPM_BUILD_ROOT

# install postfix into $RPM_BUILD_ROOT

# Move stuff around so we don't conflict with sendmail
mv man/man1/mailq.1      man/man1/mailq.postfix.1
mv man/man1/newaliases.1 man/man1/newaliases.postfix.1
mv man/man1/sendmail.1   man/man1/sendmail.postfix.1
mv man/man5/aliases.5    man/man5/aliases.postfix.5

sh postfix-install -non-interactive \
       install_root=$RPM_BUILD_ROOT \
       config_directory=%{postfix_config_dir} \
       daemon_directory=%{postfix_daemon_dir} \
       command_directory=%{postfix_command_dir} \
       queue_directory=%{postfix_queue_dir} \
       sendmail_path=%{postfix_command_dir}/sendmail.postfix \
       newaliases_path=%{_bindir}/newaliases.postfix \
       mailq_path=%{_bindir}/mailq.postfix \
       mail_owner=%{postfix_user} \
       setgid_group=%{maildrop_group} \
       manpage_directory=%{_mandir} \
       sample_directory=%{postfix_sample_dir} \
       readme_directory=%{postfix_readme_dir} || exit 1

# Move around the TLS docs
%if %{TLS}
mkdir -p $RPM_BUILD_ROOT%{postfix_doc_dir}/TLS
cp %{tlsno}/doc/* $RPM_BUILD_ROOT%{postfix_doc_dir}/TLS
for i in ACKNOWLEDGEMENTS CHANGES INSTALL README TODO; do
  cp %{tlsno}/$i $RPM_BUILD_ROOT%{postfix_doc_dir}/TLS
done
mkdir -p $RPM_BUILD_ROOT%{postfix_doc_dir}/TLS/contributed
for i in 00README loadCAcert.pl Postfix_SSL-HOWTO.pdf SSL_CA-HOWTO.pdf fp.csh make-postfix-cert.sh; do
  cp %{tlsno}/contributed/$i $RPM_BUILD_ROOT%{postfix_doc_dir}/TLS/contributed
done
# fix path to perl
perl -pi -e "s,/usr/local/bin/perl,/usr/bin/perl,g" $RPM_BUILD_ROOT%{postfix_doc_dir}/TLS/contributed/loadCAcert.pl
%endif

# Change alias_maps and alias_database default directory to %{postfix_config_dir}
bin/postconf -c $RPM_BUILD_ROOT%{postfix_config_dir} -e \
	"alias_maps = hash:%{postfix_config_dir}/aliases" \
	"alias_database = hash:%{postfix_config_dir}/aliases" \
|| exit 1

# This installs into the /etc/rc.d/init.d directory
/bin/mkdir -p $RPM_BUILD_ROOT/etc/rc.d/init.d
install -c %{_sourcedir}/postfix-etc-init.d-postfix \
                  $RPM_BUILD_ROOT/etc/rc.d/init.d/postfix

install -c auxiliary/rmail/rmail $RPM_BUILD_ROOT%{_bindir}/rmail.postfix

# copy new aliases files and generate a ghost aliases.db file
cp -f %{_sourcedir}/postfix-aliases $RPM_BUILD_ROOT%{postfix_config_dir}/aliases
chmod 644 $RPM_BUILD_ROOT%{postfix_config_dir}/aliases

touch $RPM_BUILD_ROOT/%{postfix_config_dir}/aliases.db

for i in active bounce corrupt defer deferred flush incoming private saved maildrop public pid; do
    mkdir -p $RPM_BUILD_ROOT%{postfix_queue_dir}/$i
done

# install performance benchmark tools by hand
for i in smtp-sink smtp-source ; do
  install -c -m 755 bin/$i $RPM_BUILD_ROOT%{postfix_command_dir}/
  install -c -m 755 man/man1/$i.1 $RPM_BUILD_ROOT%{_mandir}/man1/
done

# RPM compresses man pages automatically.
# - Edit postfix-files to reflect this, so post-install won't get confused
#   when called during package installation.
ed $RPM_BUILD_ROOT%{postfix_config_dir}/postfix-files <<EOF || exit 1
%s/\(\/man[158]\/.*\.[158]\):/\1.gz:/
w
q
EOF

cat $RPM_BUILD_ROOT%{postfix_config_dir}/postfix-files
# Install the smtpd.conf file for SASL support.
# See README-Postfix-SASL-RedHat.txt for why we need to set saslauthd_version
# in the v1 version of smtpd.conf
mkdir -p $RPM_BUILD_ROOT%{sasl_v1_lib_dir}
install -m 644 %{SOURCE100} $RPM_BUILD_ROOT%{sasl_v1_lib_dir}/smtpd.conf
echo "saslauthd_version: 2" >> $RPM_BUILD_ROOT%{sasl_v1_lib_dir}/smtpd.conf

mkdir -p $RPM_BUILD_ROOT%{sasl_v2_lib_dir}
install -m 644 %{SOURCE100} $RPM_BUILD_ROOT%{sasl_v2_lib_dir}/smtpd.conf

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/pam.d
install -m 644 %{SOURCE101} $RPM_BUILD_ROOT%{_sysconfdir}/pam.d/smtp.postfix

# Install Postfix Red Hat HOWTO.
mkdir -p $RPM_BUILD_ROOT%{postfix_doc_dir}
install -c %{SOURCE3} $RPM_BUILD_ROOT%{postfix_doc_dir}

%if %{PFLOGSUMM}
install -c pflogsumm-%{pflogsumm_ver}/pflogsumm-faq.txt $RPM_BUILD_ROOT%{postfix_doc_dir}/pflogsumm-faq.txt
install -c pflogsumm-%{pflogsumm_ver}/pflogsumm.1 $RPM_BUILD_ROOT%{_mandir}/man1/pflogsumm.1
install -c pflogsumm-%{pflogsumm_ver}/pflogsumm.pl $RPM_BUILD_ROOT%{postfix_command_dir}/pflogsumm
%endif

mkdir -p $RPM_BUILD_ROOT%{postfix_sample_dir}
%if %{IPV6}
	install -c conf/sample-ipv6.cf $RPM_BUILD_ROOT%{postfix_sample_dir}/sample-ipv6.cf
%endif
%if %{TLS}
	install -c conf/sample-tls.cf $RPM_BUILD_ROOT%{postfix_sample_dir}/sample-tls.cf
%endif


mkdir -p $RPM_BUILD_ROOT/usr/lib
pushd $RPM_BUILD_ROOT/usr/lib
ln -sf ../sbin/sendmail.postfix .
popd

%post
umask 022

/sbin/chkconfig --add postfix

# upgrade configuration files if necessary
sh %{postfix_config_dir}/post-install \
	config_directory=%{postfix_config_dir} \
	daemon_directory=%{postfix_daemon_dir} \
	command_directory=%{postfix_command_dir} \
	mail_owner=%{postfix_user} \
	setgid_group=%{maildrop_group} \
	manpage_directory=%{_mandir} \
	sample_directory=%{postfix_sample_dir} \
	readme_directory=%{postfix_readme_dir} \
	upgrade-package

%if %alternatives
/usr/sbin/alternatives --install %{postfix_command_dir}/sendmail mta %{postfix_command_dir}/sendmail.postfix 30 \
        --slave %{_bindir}/mailq mta-mailq %{_bindir}/mailq.postfix \
        --slave %{_bindir}/newaliases mta-newaliases %{_bindir}/newaliases.postfix \
        --slave %{_sysconfdir}/pam.d/smtp mta-pam %{_sysconfdir}/pam.d/smtp.postfix \
        --slave %{_bindir}/rmail mta-rmail %{_bindir}/rmail.postfix \
	--slave /usr/lib/sendmail mta-sendmail /usr/lib/sendmail.postfix \
        --slave %{_mandir}/man1/mailq.1.gz mta-mailqman %{_mandir}/man1/mailq.postfix.1.gz \
        --slave %{_mandir}/man1/newaliases.1.gz mta-newaliasesman %{_mandir}/man1/newaliases.postfix.1.gz \
        --slave %{_mandir}/man8/sendmail.8.gz mta-sendmailman %{_mandir}/man1/sendmail.postfix.1.gz \
        --slave %{_mandir}/man5/aliases.5.gz mta-aliasesman %{_mandir}/man5/aliases.postfix.5.gz \
	--initscript postfix
%endif

%pre
# Add user and groups if necessary
%{_sbindir}/groupadd -g %{maildrop_gid} -r %{maildrop_group} 2>/dev/null
%{_sbindir}/groupadd -g %{postfix_gid} -r %{postfix_group} 2>/dev/null
%{_sbindir}/groupadd -g 12 -r mail 2>/dev/null
%{_sbindir}/useradd -d %{postfix_queue_dir} -s /sbin/nologin -g %{postfix_group} -G mail -M -r -u %{postfix_uid} %{postfix_user} 2>/dev/null
exit 0

%preun
umask 022

if [ "$1" = 0 ]; then
    # stop postfix silently, but only if it's running
    /sbin/service postfix stop &>/dev/null
    /sbin/chkconfig --del postfix
%if %alternatives
    /usr/sbin/alternatives --remove mta %{postfix_command_dir}/sendmail.postfix
%endif

fi

exit 0

%postun
if [ "$1" != 0 ]; then
	/sbin/service postfix condrestart 2>&1 > /dev/null
fi
exit 0

%clean
/bin/rm -rf $RPM_BUILD_ROOT


%files

# For correct directory permissions check postfix-install script.
# It reads the file postfix-files which defines the ownership
# and permissions for all files postfix installs, we avoid explicitly
# setting anything in the %files sections that is handled by
# the upstream install script so we don't have an issue with keeping
# the spec file and upstream in sync.

%defattr(-, root, root)

# Config files not part of upstream

%config(noreplace) %{sasl_v1_lib_dir}/smtpd.conf
%config(noreplace) %{sasl_v2_lib_dir}/smtpd.conf
%config(noreplace) %{_sysconfdir}/pam.d/smtp.postfix
%config(noreplace) %{postfix_config_dir}/aliases.db
%attr(0755, root, root) %config /etc/rc.d/init.d/postfix

# Misc files

%attr(0755, root, root) %{_bindir}/rmail.postfix

%attr(0755, root, root) %{postfix_command_dir}/smtp-sink
%attr(0755, root, root) %{postfix_command_dir}/smtp-source
%attr(0755, root, root) /usr/lib/sendmail.postfix

%doc %{postfix_doc_dir}/README-Postfix-SASL-RedHat.txt

%dir %attr(0755, root, root) %{postfix_sample_dir}
%doc %attr(0644, root, root) %{postfix_sample_dir}/*

%dir %attr(0755, root, root) %{postfix_config_dir}
%dir %attr(0755, root, root) %{postfix_daemon_dir}
%dir %attr(0755, root, root) %{postfix_queue_dir}
%dir %attr(0700, %{postfix_user}, root) %{postfix_queue_dir}/active
%dir %attr(0700, %{postfix_user}, root) %{postfix_queue_dir}/bounce
%dir %attr(0700, %{postfix_user}, root) %{postfix_queue_dir}/corrupt
%dir %attr(0700, %{postfix_user}, root) %{postfix_queue_dir}/defer
%dir %attr(0700, %{postfix_user}, root) %{postfix_queue_dir}/deferred
%dir %attr(0700, %{postfix_user}, root) %{postfix_queue_dir}/flush
%dir %attr(0700, %{postfix_user}, root) %{postfix_queue_dir}/hold
%dir %attr(0700, %{postfix_user}, root) %{postfix_queue_dir}/incoming
%dir %attr(0730, %{postfix_user}, %{maildrop_group}) %{postfix_queue_dir}/maildrop
%dir %attr(0755, root, root) %{postfix_queue_dir}/pid
%dir %attr(0700, %{postfix_user}, root) %{postfix_queue_dir}/private
%dir %attr(0710, %{postfix_user}, %{maildrop_group}) %{postfix_queue_dir}/public
%dir %attr(0755, root, root) %{postfix_doc_dir}

%doc %attr(0644, root, root) %{_mandir}/man1/*
%doc %attr(0644, root, root) %{_mandir}/man5/*
%doc %attr(0644, root, root) %{_mandir}/man8/*
%doc %attr(0644, root, root) %{postfix_doc_dir}/*

%attr(0755, root, root) %{postfix_command_dir}/postalias
%attr(0755, root, root) %{postfix_command_dir}/postcat
%attr(0755, root, root) %{postfix_command_dir}/postconf
%attr(2755, root, %{maildrop_group}) %{postfix_command_dir}/postdrop
%attr(0755, root, root) %{postfix_command_dir}/postfix
%attr(0755, root, root) %{postfix_command_dir}/postkick
%attr(0755, root, root) %{postfix_command_dir}/postlock
%attr(0755, root, root) %{postfix_command_dir}/postlog
%attr(0755, root, root) %{postfix_command_dir}/postmap
%attr(2755, root, %{maildrop_group}) %{postfix_command_dir}/postqueue
%attr(0755, root, root) %{postfix_command_dir}/postsuper
%attr(0644, root, root) %{postfix_config_dir}/LICENSE
%attr(0644, root, root) %config(noreplace) %{postfix_config_dir}/access
%attr(0644, root, root) %config(noreplace) %{postfix_config_dir}/aliases
%attr(0644, root, root) %config(noreplace) %{postfix_config_dir}/canonical
%attr(0644, root, root) %config(noreplace) %{postfix_config_dir}/header_checks
%attr(0644, root, root) %config(noreplace) %{postfix_config_dir}/main.cf
%attr(0644, root, root) %{postfix_config_dir}/main.cf.default
%attr(0644, root, root) %config(noreplace) %{postfix_config_dir}/makedefs.out
%attr(0644, root, root) %config(noreplace) %{postfix_config_dir}/master.cf
%attr(0755, root, root) %{postfix_config_dir}/post-install
%attr(0644, root, root) %{postfix_config_dir}/postfix-files
%attr(0755, root, root) %{postfix_config_dir}/postfix-script
%attr(0644, root, root) %config(noreplace) %{postfix_config_dir}/relocated
%attr(0644, root, root) %config(noreplace) %{postfix_config_dir}/transport
%attr(0644, root, root) %config(noreplace) %{postfix_config_dir}/virtual
%attr(0755, root, root) %{postfix_daemon_dir}/*
%attr(0755, root, root) %{_bindir}/mailq.postfix
%attr(0755, root, root) %{_bindir}/newaliases.postfix
%attr(0755, root, root) %{_sbindir}/sendmail.postfix

%if %{PFLOGSUMM}
%files pflogsumm
%defattr(-, root, root)
    %doc  %{postfix_doc_dir}/pflogsumm-faq.txt
    %doc  %{_mandir}/man1/pflogsumm.1.gz
    %attr(0755, root , root) %{postfix_command_dir}/pflogsumm
%endif


%changelog
* Fri Jun  4 2004 Thomas Woerner <twoerner@redhat.com> 2:2.1.1-1
- new version 2.1.1
- compiling postfix PIE
- new alternatives slave for /usr/lib/sendmail

* Wed Mar 31 2004 John Dennis <jdennis@redhat.com> 2:2.0.18-4
- remove version from pflogsumm subpackage, it was resetting the
  version used in the doc directory, fixes bug 119213

* Tue Mar 30 2004 Bill Nottingham <notting@redhat.com> 2:2.0.18-3
- add %%defattr for pflogsumm package

* Tue Mar 16 2004 John Dennis <jdennis@finch.boston.redhat.com> 2:2.0.18-2
- fix sendmail man page (again), make pflogsumm a subpackage

* Mon Mar 15 2004 John Dennis <jdennis@finch.boston.redhat.com> 2:2.0.18-1
- bring source up to upstream release 2.0.18
- include pflogsumm, fixes bug #68799
- include smtp-sink, smtp-source man pages, fixes bug #118163

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Feb 24 2004 John Dennis <jdennis@finch.boston.redhat.com> 2:2.0.16-14
- fix bug 74553, make alternatives track sendmail man page

* Tue Feb 24 2004 John Dennis <jdennis@finch.boston.redhat.com> 2:2.0.16-13
- remove /etc/sysconfig/saslauthd from rpm, fixes bug 113975

* Wed Feb 18 2004 John Dennis <jdennis@porkchop.devel.redhat.com>
- set sasl back to v2 for mainline, this is good for fedora and beyond,
  for RHEL3, we'll branch and set set sasl to v1 and turn off ipv6

* Tue Feb 17 2004 John Dennis <jdennis@porkchop.devel.redhat.com>
- revert back to v1 of sasl because LDAP still links against v1 and we can't 
- bump revision for build
  have two different versions of the sasl library loaded in one load image at
  the same time. How is that possible? Because the sasl libraries have different 
  names (libsasl.so & libsasl2.so) but export the same symbols :-(
  Fixes bugs 115249 and 111767

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed Jan 21 2004 John Dennis <jdennis@finch.boston.redhat.com> 2:2.0.16-7
- fix bug 77216, support snapshot builds

* Tue Jan 20 2004 John Dennis <jdennis@finch.boston.redhat.com> 2:2.0.16-6
- add support for IPv6 via Dean Strik's patches, fixes bug 112491

* Tue Jan 13 2004 John Dennis <jdennis@finch.boston.redhat.com> 2:2.0.16-4
- remove mysqlclient prereq, fixes bug 101779
- remove md5 verification override, this fixes bug 113370. Write parse-postfix-files
  script to generate explicit list of all upstream files with ownership, modes, etc.
  carefully add back in all other not upstream files, files list is hopefully
  rock solid now.

* Mon Jan 12 2004 John Dennis <jdennis@finch.boston.redhat.com> 2:2.0.16-3
- add zlib-devel build prereq, fixes bug 112822
- remove copy of resolve.conf into chroot jail, fixes bug 111923

* Tue Dec 16 2003 John Dennis <jdennis@porkchop.devel.redhat.com>
- bump release to build 3.0E errata update

* Sat Dec 13 2003 Jeff Johnson <jbj@jbj.org> 2:2.0.16-2
- rebuild against db-4.2.52.
 
* Mon Nov 17 2003 John Dennis <jdennis@finch.boston.redhat.com> 2:2.0.16-1
- sync up with current upstream release, 2.0.16, fixes bug #108960

* Thu Sep 25 2003 Jeff Johnson <jbj@jbj.org> 2.0.11-6
- rebuild against db-4.2.42.

* Tue Jul 22 2003 Nalin Dahyabhai <nalin@redhat.com> 2.0.11-5
- rebuild

* Thu Jun 26 2003 John Dennis <jdennis@finch.boston.redhat.com>
- bug 98095, change rmail.postfix to rmail for uucp invocation in master.cf

* Wed Jun 25 2003 John Dennis <jdennis@finch.boston.redhat.com>
- add missing dependency for db3/db4

* Thu Jun 19 2003 John Dennis <jdennis@finch.boston.redhat.com>
- upgrade to new 2.0.11 upstream release
- fix authentication problems
- rewrite SASL documentation
- upgrade to use SASL version 2
- Fix bugs 75439, 81913 90412, 91225, 78020, 90891, 88131

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Mar  7 2003 John Dennis <jdennis@finch.boston.redhat.com>
- upgrade to release 2.0.6
- remove chroot as this is now the preferred installation according to Wietse Venema, the postfix author

* Mon Feb 24 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Feb 18 2003 Bill Nottingham <notting@redhat.com> 2:1.1.11-10
- don't copy winbind/wins nss modules, fixes #84553

* Sat Feb 01 2003 Florian La Roche <Florian.LaRoche@redhat.de>
- sanitize rpm scripts a bit

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Sat Jan 11 2003 Karsten Hopp <karsten@redhat.de> 2:1.1.11-8
- rebuild to fix krb5.h issue

* Tue Jan  7 2003 Nalin Dahyabhai <nalin@redhat.com> 2:1.1.11-7
- rebuild

* Fri Jan  3 2003 Nalin Dahyabhai <nalin@redhat.com>
- if pkgconfig knows about openssl, use its cflags and linker flags

* Thu Dec 12 2002 Tim Powers <timp@redhat.com> 2:1.1.11-6
- lib64'ize
- build on all arches

* Wed Jul 24 2002 Karsten Hopp <karsten@redhat.de>
- make aliases.db config(noreplace) (#69612)

* Tue Jul 23 2002 Karsten Hopp <karsten@redhat.de>
- postfix has its own filelist, remove LICENSE entry from it (#69069)

* Tue Jul 16 2002 Karsten Hopp <karsten@redhat.de>
- fix shell in /etc/passwd (#68373)
- fix documentation in /etc/postfix (#65858)
- Provides: /usr/bin/newaliases (#66746)
- fix autorequires by changing /usr/local/bin/perl to /usr/bin/perl in a
  script in %%doc (#68852), although I don't think this is necessary anymore

* Mon Jul 15 2002 Phil Knirsch <pknirsch@redhat.com>
- Fixed missing smtpd.conf file for SASL support and included SASL Postfix
  Red Hat HOWTO (#62505).
- Included SASL2 support patch (#68800).

* Mon Jun 24 2002 Karsten Hopp <karsten@redhat.de>
- 1.1.11, TLS 0.8.11a
- fix #66219 and #66233 (perl required for %%post)

* Fri Jun 21 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Sun May 26 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Thu May 23 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.1.10-1
- 1.1.10, TLS 0.8.10
- Build with db4
- Enable SASL

* Mon Apr 15 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.1.7-2
- Fix bugs #62358 and #62783
- Make sure libdb-3.3.so is in the chroot jail (#62906)

* Mon Apr  8 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.1.7-1
- 1.1.7, fixes 2 critical bugs
- Make sure there's a resolv.conf in the chroot jail

* Wed Mar 27 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.1.5-3
- Add Provides: lines for alternatives stuff (#60879)

* Tue Mar 26 2002 Nalin Dahyabhai <nalin@redhat.com> 1.1.5-2
- rebuild

* Tue Mar 26 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.1.5-1
- 1.1.5 (bugfix release)
- Rebuild with current db

* Thu Mar 14 2002 Bill Nottingham <notting@redhat.com> 1.1.4-3
- remove db trigger, it's both dangerous and pointless
- clean up other triggers a little

* Wed Mar 13 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.1.4-2
- Some trigger tweaks to make absolutely sure /etc/services is in the
  chroot jail

* Mon Mar 11 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.1.4-1
- 1.1.4
- TLS 0.8.4
- Move postalias run from %%post to init script to work around
  anaconda being broken.

* Fri Mar  8 2002 Bill Nottingham <notting@redhat.com> 1.1.3-5
- use alternatives --initscript support

* Thu Feb 28 2002 Bill Nottingham <notting@redhat.com> 1.1.3-4
- run alternatives --remove in %%preun
- add various prereqs

* Thu Feb 28 2002 Nalin Dahyabhai <nalin@redhat.com> 1.1.3-3
- adjust the default postfix-files config file to match the alternatives setup
  by altering the arguments passed to post-install in the %%install phase
  (otherwise, it might point to sendmail's binaries, breaking it rather rudely)
- adjust the post-install script so that it silently uses paths which have been
  modified for use with alternatives, for upgrade cases where the postfix-files
  configuration file isn't overwritten
- don't forcefully strip files -- that's a build root policy
- remove hard requirement on openldap, library dependencies take care of it
- redirect %%postun to /dev/null
- don't remove the postfix user and group when the package is removed

* Wed Feb 20 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.1.3-2
- listen on 127.0.0.1 only by default (#60071)
- Put config samples in %{_docdir}/%{name}-%{version} rather than
  /etc/postfix (#60072)
- Some spec file cleanups

* Tue Feb 19 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.1.3-1
- 1.1.3, TLS 0.8.3
- Fix updating
- Don't run the statistics cron job
- remove requirement on perl Date::Calc

* Thu Jan 31 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.1.2-3
- Fix up alternatives stuff

* Wed Jan 30 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.1.2-2
- Use alternatives

* Sun Jan 27 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.1.2-1
- Initial Red Hat Linux packaging, based on spec file from
  Simon J Mudd <sjmudd@pobox.com>
- Changes from that:
  - Set up chroot environment in triggers to make sure we catch glibc errata
  - Remove some hacks to support building on all sorts of distributions at
    the cost of specfile readability
  - Remove postdrop group on deletion

