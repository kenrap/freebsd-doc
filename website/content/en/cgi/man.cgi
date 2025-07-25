#!/usr/local/bin/perl -T
#
# Copyright (c) 1996-2025 Wolfram Schneider <wosch@FreeBSD.org>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#
# man.cgi - HTML hypertext FreeBSD man page interface
#
# based on bsdi-man.pl,v 2.17 1995/10/05 16:48:58 sanders Exp
# bsdi-man -- HTML hypertext BSDI man page interface
# based on bsdi-man.pl,v 2.10 1993/10/02 06:13:23 sanders Exp
# by polk@BSDI.COM 1/10/95
#	BSDI	Id: bsdi-man,v 1.2 1995/01/11 02:30:01 polk Exp
# Dual CGI/Plexus mode and new interface by sanders@bsdi.com 9/22/1995
#

############################################################################
# !!! man.cgi is stale perl4 code !!!
############################################################################

# run `perltidy -b man.cgi' to indent the code

# Use standard FreeBSD CGI Style if available.
# Otherwise print simple HTML design.
package cgi_style;
use constant HAS_FREEBSD_CGI_STYLE => eval { require "./cgi-style.pl"; };

package main;

$debug        = 2;
$www{'title'} = 'FreeBSD Manual Pages';
$www{'home'}  = 'https://www.FreeBSD.org';
$www{'home_man'}  = 'https://man.FreeBSD.org';
$www{'cgi_man'}  = '/cgi/man.cgi';
$www{'head'}  = $www{'title'};

# set to zero if your front-end cache has low memory
my $download_streaming_caching = 0;

# enable to download the manual pages as a tarball
my $enable_download = 1;

#$command{'man'} = '/usr/bin/man';    # 8Bit clean man
$command{'man'} = '/usr/local/www/bin/man.wrapper';    # set CPU limits

# First look in the FreeBSD base manual pages (aka /usr/share/man) and then
# in FreeBSD ports (aka /usr/local/man). This avoids confusion when manual pages have
# have the same name, but are in different sections. In this case, a ports manual
# pages would win because of the higher section priority. Now, searching for "socket"
# will always show socket(2) from the base system and not socket(1) from ports
my $freebsd_base_manpages_first = 1;

# Config Options
# map sections to their man command argument(s)
%sections = (
    '',    '',
    'All', '',
    '0',   '',

    '1',   '-S1',
    '1c',  '-S1',
    '1C',  '-S1',
    '1g',  '-S1',
    '1m',  '-S1',
    '2',   '-S2',
    '2j',  '-S2',
    '3',   '-S3',
    '3S',  '-S3',
    '3f',  '-S3',
    '3j',  '-S3',
    '3m',  '-S3',
    '3n',  '-S3',
    '3p',  '-S3',
    '3pm', '-S3',
    '3r',  '-S3',
    '3s',  '-S3',
    '3x',  '-S3',
    '4',   '-S4',
    '5',   '-S5',
    '6',   '-S6',
    '7',   '-S7',
    '8',   '-S8',
    '8c',  '-S8',
    '9',   '-S9',
    'l',   '-Sl',
    'n',   '-Sn',
);

$sectionpath = {
    'HP-UX 11.22' => { 'path' => '1:1m:2:3:4:5:7:9' },
    'HP-UX 11.20' => { 'path' => '1:1m:2:3:4:5:7:9' },
    'HP-UX 11.11' => { 'path' => '1:1m:2:3:4:5:7:9' },
    'HP-UX 11.00' => { 'path' => '1:1m:2:3:4:5:7:9' },
    'HP-UX 10.20' => { 'path' => '1:1m:2:3:4:5:7:9' },
    'HP-UX 10.10' => { 'path' => '1:1m:2:3:4:5:7:9' },
    'HP-UX 10.01' => { 'path' => '1:1m:2:3:4:5:7:9' },
    'HP-UX 9.07'  => { 'path' => '1:1m:2:3:4:5:7:9' },
    'HP-UX 8.07'  => { 'path' => '1:1m:2:3:4:5:7:9' },

    'IRIX 6.5.30' => { 'path' => '1:1m:2:3:3c:3dm:3n:3x:4:5:7:9' },


    'OpenIndiana 2024.10'  => {
        'path' =>
'1:1m:1s:1t:2:3:3c:3malloc:3nsl:3socket:3ldap:3resolv:3rpc:3sip:3slp:3proc:3c_db:3elf:3kvm:3kstat:3m:3mp:3mvec:3pam:3bsm:3tsol:3contract:3cpc:3sec:3secdb:3cfgadm:3devid:3devinfo:3lib:3nvpair:7:7d:7i:9:9e:9f:9p:9s:4:5:3gen:3exacct:3stmf:3sysevent:3uuid:3volmgt:3mail:3ext:3fstyp:3picl:3picltree:3pool:3project:3perl:3lgrp:3sasl:3scf:3tecla:3mpapi:3fcoe:3xnet:3curses:3xcurses:3dlpi:3dns_sd:3gss:3tcl:3tk:8:1openssl:3openssl:5openssl:7openssl'
    },

    'OpenIndiana 2022.10'  => {
        'path' =>
'1:1m:1s:1t:2:3:3c:3malloc:3nsl:3socket:3ldap:3resolv:3rpc:3sip:3slp:3proc:3c_db:3elf:3kvm:3kstat:3m:3mp:3mvec:3pam:3bsm:3tsol:3contract:3cpc:3sec:3secdb:3cfgadm:3devid:3devinfo:3lib:3nvpair:7:7d:7i:9:9e:9f:9p:9s:4:5:3gen:3exacct:3stmf:3sysevent:3uuid:3volmgt:3mail:3ext:3fstyp:3picl:3picltree:3pool:3project:3perl:3lgrp:3sasl:3scf:3tecla:3mpapi:3fcoe:3xnet:3curses:3xcurses:3dlpi:3dns_sd:3gss:3tcl:3tk:8:1openssl:3openssl:5openssl:7openssl'
    },

    'OpenIndiana 2020.10'  => {
        'path' =>
'1:1m:1s:1t:2:3:3c:3malloc:3nsl:3socket:3ldap:3resolv:3rpc:3sip:3slp:3proc:3c_db:3elf:3kvm:3kstat:3m:3mp:3mvec:3pam:3bsm:3tsol:3contract:3cpc:3sec:3secdb:3cfgadm:3devid:3devinfo:3lib:3nvpair:7:7d:7fs:7i:7m:7p:9:9e:9f:9p:9s:4:5:3gen:3exacct:3stmf:3sysevent:3uuid:3volmgt:3mail:3ext:3fstyp:3picl:3picltree:3pool:3project:3perl:3lgrp:3sasl:3scf:3tecla:3mpapi:3fcoe:3xnet:3curses:3xcurses:3dlpi:3dns_sd:3gss:3tiff:3tcl:3tk:8:1openssl:3openssl:5openssl:7openssl'
    },

    'OpenIndiana 2017.10'  => {
        'path' =>
'1:1m:1s:1t:2:3:3c:3malloc:3nsl:3socket:3ldap:3resolv:3rpc:3sip:3slp:3proc:3c_db:3elf:3kvm:3kstat:3m:3mp:3mvec:3pam:3bsm:3tsol:3contract:3cpc:3sec:3secdb:3cfgadm:3devid:3devinfo:3lib:3nvpair:7:7d:7fs:7i:7m:7p:9:9e:9f:9p:9s:4:5:3gen:3exacct:3stmf:3sysevent:3uuid:3volmgt:3mail:3ext:3fstyp:3picl:3picltree:3pool:3project:3perl:3lgrp:3sasl:3scf:3tecla:3mpapi:3fcoe:3xnet:3curses:3xcurses:3dlpi:3dns_sd:3gss:3tiff:3tcl:3tk:8:1openssl:3openssl:5openssl:7openssl'
    },

    'OpenIndiana 2015.10'  => {
        'path' =>
'1:1m:1s:1t:2:3:3c:3malloc:3nsl:3socket:3ldap:3resolv:3rpc:3sip:3slp:3proc:3c_db:3elf:3kvm:3kstat:3m:3mp:3mvec:3pam:3papi:3bsm:3tsol:3contract:3cpc:3sec:3secdb:3cfgadm:3devid:3devinfo:3lib:3nvpair:7:7d:7fs:7i:7m:7p:9:9e:9f:9p:9s:4:5:3gen:3exacct:3stmf:3sysevent:3uuid:3volmgt:3mail:3ext:3fstyp:3picl:3picltree:3pool:3project:3perl:3lgrp:3sasl:3scf:3tecla:3mpapi:3fcoe:3xnet:3curses:3xcurses:3dlpi:3dns_sd:3gss:3tiff:3tcl:3tk:8:1openssl:3openssl:5openssl:7openssl'
    },

    'OpenIndiana 2013.08'  => {
        'path' =>
'1:1m:1t:2:3:3c:3malloc:3nsl:3socket:3ldap:3resolv:3rpc:3sip:3slp:3proc:3c_db:3elf:3kvm:3kstat:3mp:3pam:3papi:3bsm:3tsol:3contract:3cpc:3sec:3secdb:3cfgadm:3devid:3devinfo:3lib:3nvpair:7:7d:7fs:7i:7m:7p:9:9e:9f:9p:9s:4:5:3gen:3exacct:3stmf:3sysevent:3uuid:3volmgt:3mail:3ext:3fstyp:3picl:3picltree:3pool:3project:3perl:3lgrp:3sasl:3scf:3tecla:3mpapi:3fcoe:3xnet:3curses:3xcurses:3dlpi:3dns_sd:3gss:3tiff:3tcl:3tk:8:1openssl:3openssl:5openssl:7openssl'
    },

    'OpenSolaris 2010.03'  => {
        'path' =>
'1:1m:1s:1as:1t:2:3:3c:3malloc:3nsl:3socket:3ldap:3nisdb:3resolv:3rpc:3sip:3slp:3proc:3c_db:3elf:3kvm:3kstat:3m:3mp:3mvec:3pam:3papi:3bsm:3tsol:3contract:3cpc:3sec:3secdb:3cfgadm:3crypt:3devid:3devinfo:3lib:3head:3nvpair:3rsm:7:7d:7fs:7i:7ipp:7m:7p:9:9e:9f:9p:9s:4:5:4b:3gen:3exacct:3stmf:3iscsit:3sysevent:3uuid:3wsreg:3reparse:3dmi:3snmp:3tnf:3volmgt:3mail:3layout:3ext:3fm:3fstyp:3picl:3picltree:3pool:3project:3perl:3lgrp:3sasl:3scf:3dat:3hbaapi:3tecla:3mpapi:3fcoe:1b:1c:1f:3xnet:3curses:3plot:3xcurses:3dlpi:3dns_sd:3gss:6:3tiff:3fontconfig:3tcl:3tk:3xtsol:3mms:3mlib:3c++:3cc4:3f:3p:3pi:3rtc:8:1erl:3erl:4erl:1openssl:3openssl:5openssl:7openssl:l:n',
    },

    'OpenSolaris 2009.06'  => {
        'path' =>
'1:1m:1s:1as:1t:2:3:3c:3malloc:3nsl:3socket:3ldap:3nisdb:3resolv:3rpc:3sip:3slp:3proc:3c_db:3elf:3kvm:3kstat:3m:3mp:3mvec:3pam:3papi:3bsm:3tsol:3contract:3cpc:3sec:3secdb:3smartcard:3cfgadm:3crypt:3devid:3devinfo:3lib:3libucb:3head:3nvpair:3rsm:7:7d:7fs:7i:7ipp:7m:7p:9:9e:9f:9p:9s:4:5:4b:3gen:3exacct:3stmf:3iscsit:3sysevent:3uuid:3wsreg:3dmi:3snmp:3tnf:3volmgt:3mail:3layout:3ext:3fstyp:3picl:3picltree:3pool:3project:3perl:3lgrp:3sasl:3scf:3dat:3hbaapi:3tecla:3mpapi:3commputil:1b:1c:1f:3ucb:3xnet:3curses:3plot:3xcurses:3dlpi:3dns_sd:3gss:6:3tiff:3fontconfig:3tcl:3tk:3xtsol:3mms:3mlib:3c++:3cc4:3f:3p:3pi:3rtc:8:1erl:3erl:4erl:1openssl:3openssl:5openssl:7openssl:l:n',
    },

    'SunOS 5.10'  => {
        'path' =>
'1:1m:1s:1as:2:3:3c:3malloc:3nsl:3socket:3ldap:3nisdb:3rac:3resolv:3rpc:3slp:3proc:3rt:3c_db:3elf:3kvm:3kstat:3m:3mp:3mvec:3pam:3aio:3bsm:3tsol:3contract:3cpc:3sec:3secdb:3smartcard:3cfgadm:3crypt:3devid:3devinfo:3door:3lib:3libucb:3head:3nvpair:3rsm:7:7d:7fs:7i:7ipp:7m:7p:9:9e:9f:9p:9s:4:5:4b:3gen:3exacct:3sysevent:3uuid:3wsreg:3dmi:3snmp:3tnf:3volmgt:3mail:3layout:3ext:3picl:3picltree:3pool:3project:3perl:3lgrp:3sasl:3scf:3dat:3hbaapi:3tecla:1b:1c:1f:3ucb:3xnet:3curses:3plot:3xcurses:3gss:6:3tiff:3fontconfig:3mlib:l:n',
    },
    'SunOS 5.9' => {
        'path' =>
'1:1m:1s:2:3:3c:3malloc:3dl:3nsl:3socket:3ldap:3nisdb:3rac:3resolv:3rpc:3slp:3xfn:3proc:3rt:3thr:3elf:3kvm:3kstat:3m:3mp:3pam:3sched:3aio:3bsm:3cpc:3sec:3secdb:3cfgadm:3crypt:3devid:3devinfo:3door:3lib:3libucb:3head:3nvpair:3rsm:7:7d:7fs:7i:7m:7p:9:9e:9f:9p:9s:4:5:4b:3gen:3exacct:3sysevent:3wsreg:3dmi:3snmp:3tnf:3volmgt:3mail:3layout:3ext:3picl:3picltree:3pool:3project:1b:1c:1f:3ucb:3xnet:3curses:3plot:3xcurses:3gss:6:l:n',
    },
    'SunOS 5.8' => {
        'path' =>
'1:1m:1s:2:3:3c:3malloc:3dl:3nsl:3socket:3ldap:3krb:3nisdb:3rac:3resolv:3rpc:3slp:3xfn:3proc:3rt:3thr:3elf:3kvm:3kstat:3m:3mp:3pam:3sched:3aio:3bsm:3cpc:3sec:3secdb:3cfgadm:3crypt:3devid:3devinfo:3door:3lib:3libucb:3head:7:7d:7fs:7i:7m:7p:9:9e:9f:9s:4:5:4b:3gen:3dmi:3snmp:3tnf:3volmgt:3mail:3layout:3ext:1b:1c:1f:3ucb:3xnet:3curses:3plot:3xcurses:6:l:n',
    },
    'SunOS 5.7' => {
        'path' =>
'1:1m:1c:1f:1s:1b:2:3:3c:3s:3x:3xc:3n:3r:3t:3xn:3m:3k:3g:3e:3b:9f:9s:9e:9:4:5:7:7d:7i:7m:7p:7fs:4b:6:l:n',
    },
    'SunOS 5.6' => {
        'path' =>
'1:1m:1c:1f:1s:1b:2:3:3c:3s:3x:3xc:3xn:3r:3t:3n:3m:3k:3g:3e:3b:9f:9s:9e:9:4:5:7:7d:7i:7m:7p:7fs:4b:6:l:n',
    },
    'SunOS 5.5.1' => {
        'path' =>
'1:1m:1c:1f:1s:1b:2:3:3c:3s:3x:3xc:3xn:3r:3t:3n:3m:3k:3g:3e:3b:9f:9s:9e:9:4:5:7:7d:7i:7m:7p:7fs:4b:6:l:n',
    },
    'OpenBSD 3.0' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 3.1' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 3.2' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 3.3' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 3.4' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 3.5' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 3.6' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 3.7' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 3.8' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 3.9' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 4.0' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 4.1' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 4.2' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 4.3' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 4.4' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 4.5' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 4.6' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 4.7' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 4.8' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 4.9' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 5.0' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 5.1' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 5.2' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 5.3' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 5.4' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 5.5' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 5.6' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 5.7' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 5.8' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 5.9' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 6.0' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 6.1' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 6.2' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 6.3' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 6.4' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 6.5' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 6.6' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 6.7' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 6.8' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 6.9' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 7.0' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 7.1' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 7.2' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 7.3' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 7.4' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 7.5' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 7.6' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },
    'OpenBSD 7.7' => { 'path' => '1:2:3:3p:4:5:6:7:8:9', },

    'CentOS 3.9' => { 'path' => '1:2:3:3p:4:5:6:7:8:9:n', },
    'CentOS 4.8' => { 'path' => '1:1p:2:3:3p:4:5:6:7:8:9:n:0p', },

    'CentOS 5.3' => { 'path' => '0p:1:1p:1x:2:2x:3:3p:3x:4:4x:5:5x:6:6x:7:7x:8:8x:9:9x:l:n' },
    'CentOS 5.4' => { 'path' => '0p:1:1p:1x:2:2x:3:3p:3x:4:4x:5:5x:6:6x:7:7x:8:8x:9:9x:l:n' },
    'CentOS 5.5' => { 'path' => '0p:1:1p:1x:2:2x:3:3p:3x:4:4x:5:5x:6:6x:7:7x:8:8x:9:9x:l:n' },
    'CentOS 5.6' => { 'path' => '0p:1:1p:1x:2:2x:3:3p:3x:4:4x:5:5x:6:6x:7:7x:8:8x:9:9x:l:n' },
    'CentOS 5.7' => { 'path' => '0p:1:1p:1x:2:2x:3:3p:3x:4:4x:5:5x:6:6x:7:7x:8:8x:9:9x:l:n' },
    'CentOS 5.8' => { 'path' => '0p:1:1p:1x:2:2x:3:3p:3x:4:4x:5:5x:6:6x:7:7x:8:8x:9:9x:l:n' },
    'CentOS 5.9' => { 'path' => '0p:1:1p:1x:2:2x:3:3p:3x:4:4x:5:5x:6:6x:7:7x:8:8x:9:9x:l:n' },
    'CentOS 5.10' => { 'path' => '0p:1:1p:1x:2:2x:3:3p:3x:4:4x:5:5x:6:6x:7:7x:8:8x:9:9x:l:n' },
    'CentOS 5.11' => { 'path' => '0p:1:1p:1x:2:2x:3:3p:3x:4:4x:5:5x:6:6x:7:7x:8:8x:9:9x:l:n' },

    'CentOS 6.0' => { 'path' => '0p:1:1p:1x:2:2x:3:3p:3x:4:4x:5:5x:6:6x:7:7x:8:8x:9:9x:l:n' },
    'CentOS 6.1' => { 'path' => '0p:1:1p:1x:2:2x:3:3p:3x:4:4x:5:5x:6:6x:7:7x:8:8x:9:9x:l:n' },
    'CentOS 6.2' => { 'path' => '0p:1:1p:1x:2:2x:3:3p:3x:4:4x:5:5x:6:6x:7:7x:8:8x:9:9x:l:n' },
    'CentOS 6.3' => { 'path' => '0p:1:1p:1x:2:2x:3:3p:3x:4:4x:5:5x:6:6x:7:7x:8:8x:9:9x:l:n' },
    'CentOS 6.4' => { 'path' => '0p:1:1p:1x:2:2x:3:3p:3x:4:4x:5:5x:6:6x:7:7x:8:8x:9:9x:l:n' },
    'CentOS 6.5' => { 'path' => '0p:1:1p:1x:2:2x:3:3p:3x:4:4x:5:5x:6:6x:7:7x:8:8x:9:9x:l:n' },
    'CentOS 6.6' => { 'path' => '0p:1:1p:1x:2:2x:3:3p:3x:4:4x:5:5x:6:6x:7:7x:8:8x:9:9x:l:n' },
    'CentOS 6.7' => { 'path' => '0p:1:1p:2:3:3p:3t:4:5:6:7:8:9:n' },
    'CentOS 6.8' => { 'path' => '0p:1:1p:2:3:3p:3t:4:5:6:7:8:9:n' },
    'CentOS 6.9' => { 'path' => '0p:1:1p:2:3:3p:3t:4:5:6:7:8:9:n' },
    'CentOS 6.10' => { 'path' => '0p:1:1p:2:3:3p:3t:4:5:6:7:8:9:n' },

    'CentOS 7.0' => { 'path' => '0p:1:1p:1x:2:2x:3:3p:3t:3x:4:4x:5:5x:6:6x:7:7x:8:8x:9:9x:n' },
    'CentOS 7.1' => { 'path' => '0p:1:1p:2:3:3p:3t:4:5:6:7:8:9:n' },
    'CentOS 7.2' => { 'path' => '0p:1:1p:2:3:3p:3t:4:5:6:7:8:9:n' },
    'CentOS 7.3' => { 'path' => '0p:1:1p:2:3:3p:3t:4:5:6:7:8:9:n' },
    'CentOS 7.4' => { 'path' => '0p:1:1p:2:3:3p:3t:4:5:6:7:8:9:n' },
    'CentOS 7.5' => { 'path' => '0p:1:1p:2:3:3p:3t:4:5:6:7:8:9:n' },
    'CentOS 7.6' => { 'path' => '0p:1:1p:2:3:3p:3t:4:5:6:7:8:9:n' },
    'CentOS 7.7' => { 'path' => '0p:1:1p:2:3:3p:3t:4:5:6:7:8:9:n' },
    'CentOS 7.8' => { 'path' => '0p:1:1p:2:3:3p:3t:4:5:6:7:8:9:n' },
    'CentOS 7.9' => { 'path' => '0p:1:1p:2:3:3p:3t:4:5:6:7:8:9:n' },

    'Rocky 10.0' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:n', },
    'Rocky 9.6' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:n', },
    'Rocky 9.5' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:n', },
    'Rocky 9.4' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:n', },
    'Rocky 9.3' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:n', },
    'Rocky 9.2' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:n', },
    'Rocky 9.1' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:n', },
    'Rocky 9.0' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:n', },
    'Rocky 8.10' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:n', },
    'Rocky 8.9' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:n', },
    'Rocky 8.8' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:n', },
    'Rocky 8.7' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:n', },
    'Rocky 8.6' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:n', },
    'Rocky 8.5' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:n', },
    'Rocky 8.4' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:n', },
    'Rocky 8.3' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:n', },

    'SuSE 4.3'  => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:n:s', },
    'SuSE 5.0'  => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:n:s', },
    'SuSE 5.2'  => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:n:s', },
    'SuSE 5.3'  => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:n:s', },
    'SuSE 6.0'  => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:n:s', },
    'SuSE 6.1'  => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:n:s', },
    'SuSE 6.3'  => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:n:s', },
    'SuSE 6.4'  => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:n:s', },
    'SuSE 7.0'  => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:n:s', },
    'SuSE 7.1'  => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:n:s', },
    'SuSE 7.2'  => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:n:s', },
    'SuSE 7.3'  => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:n:s', },
    'SuSE 8.0'  => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:n:s', },
    'SuSE 8.1'  => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:n:s', },
    'SuSE 8.2'  => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:n:s', },
    'SuSE 9.2'  => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:n:s', },
    'SuSE 9.3'  => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:n:s', },
    'SuSE 10.0' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:n:s', },
    'SuSE 10.1' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:n:s', },
    'SuSE 10.2' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:n:s', },
    'SuSE 10.3' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:n:s', },
    'SuSE 11.0' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:n:s', },
    'SuSE 11.1' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:n:s', },
    'SuSE 11.2' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:n:s', },
    'SuSE 11.3' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:n:s', },

    'openSUSE 10.2' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:g:n' },
    'openSUSE 10.3' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:g:n' },
    'openSUSE 11.0' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:g:n' },
    'openSUSE 11.1' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:g:n' },
    'openSUSE 11.2' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:g:n' },
    'openSUSE 11.3' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:g:n' },
    'openSUSE 11.4' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:g:n' },
    'openSUSE 12.1' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:g:n' },
    'openSUSE 12.2' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:g:n' },
    'openSUSE 12.3' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:g:n' },
    'openSUSE 13.1' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:g:n' },
    'openSUSE 13.2' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:g:n' },
    'openSUSE 42.1' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:g:n' },
    'openSUSE 42.2' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:g:n' },
    'openSUSE 42.3' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:g:n' },
    'openSUSE 15.0' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:g:n' },
    'openSUSE 15.1' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:g:n' },
    'openSUSE 15.2' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:g:n' },
    'openSUSE 15.3' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:g:n' },
    'openSUSE 15.4' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:g:n' },
    'openSUSE 15.5' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:g:n' },
    'openSUSE 15.6' => { 'path' => '0p:1:1p:2:3:3p:4:5:6:7:8:9:g:n' },
};

foreach my $os ( keys %$sectionpath ) {
    foreach my $section ( split( /:/, $sectionpath->{$os}{'path'} ) ) {
        $section =~ /(.)(.*)/;
        $sectionpath->{$os}{$1} .=
          ( $sectionpath->{$os}{$1} ? ':' : '' ) . $section;
    }
}

%sectionName = (
    '0', 'All Sections',             '1', '1 - General Commands',
    '2', '2 - System Calls',         '3', '3 - Subroutines',
    '4', '4 - Special Files',        '5', '5 - File Formats',
    '6', '6 - Games',                '7', '7 - Macros and Conventions',
    '8', '8 - Maintenance Commands', '9', '9 - Kernel Interface',
    'n', 'n - New Commands',
);

$manLocalDir    = '/usr/local/www/bsddoc/man';
# this should be the latest "release and ports"
$manPathDefault = 'FreeBSD 14.3-RELEASE and Ports';

%manPath = (
    # supported RELEASES / STABLE / CURRENT 
    'FreeBSD 14.3-RELEASE and Ports',
"$manLocalDir/FreeBSD-14.3-RELEASE/man:$manLocalDir/FreeBSD-14.3-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-14.quarterly-RELEASE/man:$manLocalDir/FreeBSD-ports-14.quarterly-RELEASE/misc",
    'FreeBSD 14.2-RELEASE and Ports',
"$manLocalDir/FreeBSD-14.2-RELEASE/man:$manLocalDir/FreeBSD-14.2-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-14.2-RELEASE/man:$manLocalDir/FreeBSD-ports-14.2-RELEASE/misc",
    'FreeBSD 14.1-RELEASE and Ports',
"$manLocalDir/FreeBSD-14.1-RELEASE/man:$manLocalDir/FreeBSD-14.1-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-14.1-RELEASE/man:$manLocalDir/FreeBSD-ports-14.1-RELEASE/misc",
    'FreeBSD 14.0-RELEASE and Ports',
"$manLocalDir/FreeBSD-14.0-RELEASE/man:$manLocalDir/FreeBSD-14.0-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-14.0-RELEASE/man:$manLocalDir/FreeBSD-ports-14.0-RELEASE/misc",

    'FreeBSD 13.5-RELEASE and Ports',
"$manLocalDir/FreeBSD-13.5-RELEASE/man:$manLocalDir/FreeBSD-13.5-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-13.5-RELEASE/man:$manLocalDir/FreeBSD-ports-13.5-RELEASE/misc",
    'FreeBSD 13.4-RELEASE and Ports',
"$manLocalDir/FreeBSD-13.4-RELEASE/man:$manLocalDir/FreeBSD-13.4-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-13.4-RELEASE/man:$manLocalDir/FreeBSD-ports-13.4-RELEASE/misc",
    'FreeBSD 13.3-RELEASE and Ports',
"$manLocalDir/FreeBSD-13.3-RELEASE/man:$manLocalDir/FreeBSD-13.3-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-13.3-RELEASE/man:$manLocalDir/FreeBSD-ports-13.3-RELEASE/misc",
    'FreeBSD 13.2-RELEASE and Ports',
"$manLocalDir/FreeBSD-13.2-RELEASE/man:$manLocalDir/FreeBSD-13.2-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-13.2-RELEASE/man:$manLocalDir/FreeBSD-ports-13.2-RELEASE/misc",
    'FreeBSD 13.1-RELEASE and Ports',
"$manLocalDir/FreeBSD-13.1-RELEASE/man:$manLocalDir/FreeBSD-13.1-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-13.1-RELEASE/man:$manLocalDir/FreeBSD-ports-13.1-RELEASE/misc",
    'FreeBSD 13.0-RELEASE and Ports',
"$manLocalDir/FreeBSD-13.0-RELEASE/man:$manLocalDir/FreeBSD-13.0-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-13.0-RELEASE/man:$manLocalDir/FreeBSD-ports-13.0-RELEASE/misc",

    'FreeBSD 12.4-RELEASE and Ports',
"$manLocalDir/FreeBSD-12.4-RELEASE/man:$manLocalDir/FreeBSD-12.4-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-12.4-RELEASE/man:$manLocalDir/FreeBSD-ports-12.4-RELEASE/misc",
    'FreeBSD 12.3-RELEASE and Ports',
"$manLocalDir/FreeBSD-12.3-RELEASE/man:$manLocalDir/FreeBSD-12.3-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-12.3-RELEASE/man:$manLocalDir/FreeBSD-ports-12.3-RELEASE/misc",
    'FreeBSD 12.2-RELEASE and Ports',
"$manLocalDir/FreeBSD-12.2-RELEASE/man:$manLocalDir/FreeBSD-12.2-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-12.2-RELEASE/man:$manLocalDir/FreeBSD-ports-12.2-RELEASE/misc",
    'FreeBSD 12.1-RELEASE and Ports',
"$manLocalDir/FreeBSD-12.1-RELEASE/man:$manLocalDir/FreeBSD-12.1-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-12.1-RELEASE/man:$manLocalDir/FreeBSD-ports-12.1-RELEASE/misc",
    'FreeBSD 12.0-RELEASE and Ports',

"$manLocalDir/FreeBSD-12.0-RELEASE/man:$manLocalDir/FreeBSD-12.0-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-12.0-RELEASE/man:$manLocalDir/FreeBSD-ports-12.0-RELEASE/misc",
    'FreeBSD 11.4-RELEASE and Ports',
"$manLocalDir/FreeBSD-11.4-RELEASE/man:$manLocalDir/FreeBSD-11.4-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-11.4-RELEASE/man:$manLocalDir/FreeBSD-ports-11.4-RELEASE/misc",
    'FreeBSD 11.3-RELEASE and Ports',
"$manLocalDir/FreeBSD-11.3-RELEASE/man:$manLocalDir/FreeBSD-11.3-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-11.3-RELEASE/man:$manLocalDir/FreeBSD-ports-11.3-RELEASE/misc",
    'FreeBSD 11.2-RELEASE and Ports',
"$manLocalDir/FreeBSD-11.2-RELEASE/man:$manLocalDir/FreeBSD-11.2-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-11.2-RELEASE/man:$manLocalDir/FreeBSD-ports-11.2-RELEASE/misc",
    'FreeBSD 11.1-RELEASE and Ports',
"$manLocalDir/FreeBSD-11.1-RELEASE/man:$manLocalDir/FreeBSD-11.1-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-11.1-RELEASE/man:$manLocalDir/FreeBSD-ports-11.1-RELEASE/misc",
    'FreeBSD 11.0-RELEASE and Ports',
"$manLocalDir/FreeBSD-11.0-RELEASE/man:$manLocalDir/FreeBSD-11.0-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-11.0-RELEASE/man:$manLocalDir/FreeBSD-ports-11.0-RELEASE/misc",
    'FreeBSD 10.4-RELEASE and Ports',
"$manLocalDir/FreeBSD-10.4-RELEASE/man:$manLocalDir/FreeBSD-10.4-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-10.4-RELEASE/man:$manLocalDir/FreeBSD-ports-10.4-RELEASE/misc",
    'FreeBSD 10.3-RELEASE and Ports',
"$manLocalDir/FreeBSD-10.3-RELEASE/man:$manLocalDir/FreeBSD-10.3-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-10.3-RELEASE/man:$manLocalDir/FreeBSD-ports-10.3-RELEASE/misc",
    'FreeBSD 10.2-RELEASE and Ports',
"$manLocalDir/FreeBSD-10.2-RELEASE/man:$manLocalDir/FreeBSD-10.2-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-10.2-RELEASE/man:$manLocalDir/FreeBSD-ports-10.2-RELEASE/misc",
    'FreeBSD 10.1-RELEASE and Ports',
"$manLocalDir/FreeBSD-10.1-RELEASE/man:$manLocalDir/FreeBSD-10.1-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-10.1-RELEASE/man:$manLocalDir/FreeBSD-ports-10.1-RELEASE/misc",
    'FreeBSD 10.0-RELEASE and Ports',
"$manLocalDir/FreeBSD-10.0-RELEASE/man:$manLocalDir/FreeBSD-10.0-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-10.0-RELEASE/man:$manLocalDir/FreeBSD-ports-10.0-RELEASE/misc",

    'FreeBSD 9.3-RELEASE and Ports',
"$manLocalDir/FreeBSD-9.3-RELEASE/man:$manLocalDir/FreeBSD-9.3-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-9.3-RELEASE/man:$manLocalDir/FreeBSD-ports-9.3-RELEASE/misc",
    'FreeBSD 9.2-RELEASE and Ports',
"$manLocalDir/FreeBSD-9.2-RELEASE/man:$manLocalDir/FreeBSD-9.2-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-9.2-RELEASE/man:$manLocalDir/FreeBSD-ports-9.2-RELEASE/misc",
    'FreeBSD 9.0-RELEASE and Ports',
"$manLocalDir/FreeBSD-9.0-RELEASE/man:$manLocalDir/FreeBSD-9.0-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-9.0-RELEASE/man:$manLocalDir/FreeBSD-ports-9.0-RELEASE/lib-perl5-perl-5.12.4-man:$manLocalDir/FreeBSD-ports-9.0-RELEASE/misc",
    'FreeBSD 8.4-RELEASE and Ports',
"$manLocalDir/FreeBSD-8.4-RELEASE/man:$manLocalDir/FreeBSD-8.4-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-8.4-RELEASE/man:$manLocalDir/FreeBSD-ports-8.4-RELEASE/misc",
    'FreeBSD 8.3-RELEASE and Ports',
"$manLocalDir/FreeBSD-8.3-RELEASE/man:$manLocalDir/FreeBSD-8.3-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-8.3-RELEASE",
    'FreeBSD 8.2-RELEASE and Ports',
"$manLocalDir/FreeBSD-8.2-RELEASE/man:$manLocalDir/FreeBSD-8.2-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-8.2-RELEASE",
    'FreeBSD 8.1-RELEASE and Ports',
"$manLocalDir/FreeBSD-8.1-RELEASE/man:$manLocalDir/FreeBSD-8.1-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-8.1-RELEASE",
    'FreeBSD 8.0-RELEASE and Ports',
"$manLocalDir/FreeBSD-8.0-RELEASE/man:$manLocalDir/FreeBSD-8.0-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-8.0-RELEASE",
    'FreeBSD 7.4-RELEASE and Ports',
"$manLocalDir/FreeBSD-7.4-RELEASE/man:$manLocalDir/FreeBSD-7.4-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-7.4-RELEASE",
    'FreeBSD 7.3-RELEASE and Ports',
"$manLocalDir/FreeBSD-7.3-RELEASE/man:$manLocalDir/FreeBSD-7.3-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-7.3-RELEASE",
    'FreeBSD 6.4-RELEASE and Ports',
"$manLocalDir/FreeBSD-6.4-RELEASE/man:$manLocalDir/FreeBSD-6.4-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-6.2-RELEASE",

    'FreeBSD 15.0-CURRENT',
"$manLocalDir/FreeBSD-15.0-CURRENT/man:$manLocalDir/FreeBSD-15.0-CURRENT/openssl/man",

    'FreeBSD 14.3-STABLE',
"$manLocalDir/FreeBSD-14.3-STABLE/man:$manLocalDir/FreeBSD-14.3-STABLE/openssl/man",
    'FreeBSD 14.3-RELEASE',
"$manLocalDir/FreeBSD-14.3-RELEASE/man:$manLocalDir/FreeBSD-14.3-RELEASE/openssl/man",
    'FreeBSD 14.2-RELEASE',
"$manLocalDir/FreeBSD-14.2-RELEASE/man:$manLocalDir/FreeBSD-14.2-RELEASE/openssl/man",
    'FreeBSD 14.1-RELEASE',
"$manLocalDir/FreeBSD-14.1-RELEASE/man:$manLocalDir/FreeBSD-14.1-RELEASE/openssl/man",
    'FreeBSD 14.0-RELEASE',
"$manLocalDir/FreeBSD-14.0-RELEASE/man:$manLocalDir/FreeBSD-14.0-RELEASE/openssl/man",

    'FreeBSD 13.5-STABLE',
"$manLocalDir/FreeBSD-13.5-STABLE/man:$manLocalDir/FreeBSD-13.5-STABLE/openssl/man",
    'FreeBSD 13.5-RELEASE',
"$manLocalDir/FreeBSD-13.5-RELEASE/man:$manLocalDir/FreeBSD-13.5-RELEASE/openssl/man",
    'FreeBSD 13.4-RELEASE',
"$manLocalDir/FreeBSD-13.4-RELEASE/man:$manLocalDir/FreeBSD-13.4-RELEASE/openssl/man",
    'FreeBSD 13.3-RELEASE',
"$manLocalDir/FreeBSD-13.3-RELEASE/man:$manLocalDir/FreeBSD-13.3-RELEASE/openssl/man",
    'FreeBSD 13.2-RELEASE',
"$manLocalDir/FreeBSD-13.2-RELEASE/man:$manLocalDir/FreeBSD-13.2-RELEASE/openssl/man",
    'FreeBSD 13.1-RELEASE',
"$manLocalDir/FreeBSD-13.1-RELEASE/man:$manLocalDir/FreeBSD-13.1-RELEASE/openssl/man",
    'FreeBSD 13.0-RELEASE',
"$manLocalDir/FreeBSD-13.0-RELEASE/man:$manLocalDir/FreeBSD-13.0-RELEASE/openssl/man",

    'FreeBSD 12.4-RELEASE',
"$manLocalDir/FreeBSD-12.4-RELEASE/man:$manLocalDir/FreeBSD-12.4-RELEASE/openssl/man",
    'FreeBSD 12.3-RELEASE',
"$manLocalDir/FreeBSD-12.3-RELEASE/man:$manLocalDir/FreeBSD-12.3-RELEASE/openssl/man",
    'FreeBSD 12.2-RELEASE',
"$manLocalDir/FreeBSD-12.2-RELEASE/man:$manLocalDir/FreeBSD-12.2-RELEASE/openssl/man",
    'FreeBSD 12.1-RELEASE',
"$manLocalDir/FreeBSD-12.1-RELEASE/man:$manLocalDir/FreeBSD-12.1-RELEASE/openssl/man",
    'FreeBSD 12.0-RELEASE',
"$manLocalDir/FreeBSD-12.0-RELEASE/man:$manLocalDir/FreeBSD-12.0-RELEASE/openssl/man",

    'FreeBSD 11.4-RELEASE',
"$manLocalDir/FreeBSD-11.4-RELEASE/man:$manLocalDir/FreeBSD-11.4-RELEASE/openssl/man",
    'FreeBSD 11.3-RELEASE',
"$manLocalDir/FreeBSD-11.3-RELEASE/man:$manLocalDir/FreeBSD-11.3-RELEASE/openssl/man",
    'FreeBSD 11.2-RELEASE',
"$manLocalDir/FreeBSD-11.2-RELEASE/man:$manLocalDir/FreeBSD-11.2-RELEASE/openssl/man",
    'FreeBSD 11.1-RELEASE',
"$manLocalDir/FreeBSD-11.1-RELEASE/man:$manLocalDir/FreeBSD-11.1-RELEASE/openssl/man",
    'FreeBSD 11.0-RELEASE',
"$manLocalDir/FreeBSD-11.0-RELEASE/man:$manLocalDir/FreeBSD-11.0-RELEASE/openssl/man",
    'FreeBSD 10.4-RELEASE',
"$manLocalDir/FreeBSD-10.4-RELEASE/man:$manLocalDir/FreeBSD-10.4-RELEASE/openssl/man",
    'FreeBSD 10.3-RELEASE',
"$manLocalDir/FreeBSD-10.3-RELEASE/man:$manLocalDir/FreeBSD-10.3-RELEASE/openssl/man",
    'FreeBSD 10.2-RELEASE',
"$manLocalDir/FreeBSD-10.2-RELEASE/man:$manLocalDir/FreeBSD-10.2-RELEASE/openssl/man",
    'FreeBSD 10.1-RELEASE',
"$manLocalDir/FreeBSD-10.1-RELEASE/man:$manLocalDir/FreeBSD-10.1-RELEASE/openssl/man",
    'FreeBSD 10.0-RELEASE',
"$manLocalDir/FreeBSD-10.0-RELEASE/man:$manLocalDir/FreeBSD-10.0-RELEASE/openssl/man",

    'FreeBSD 9.3-RELEASE',
"$manLocalDir/FreeBSD-9.3-RELEASE/man:$manLocalDir/FreeBSD-9.3-RELEASE/openssl/man",
    'FreeBSD 9.2-RELEASE',
"$manLocalDir/FreeBSD-9.2-RELEASE/man:$manLocalDir/FreeBSD-9.2-RELEASE/openssl/man",
    'FreeBSD 9.1-RELEASE',
"$manLocalDir/FreeBSD-9.1-RELEASE/man:$manLocalDir/FreeBSD-9.1-RELEASE/openssl/man",
    'FreeBSD 9.0-RELEASE',
"$manLocalDir/FreeBSD-9.0-RELEASE/man:$manLocalDir/FreeBSD-9.0-RELEASE/openssl/man",

    'FreeBSD 8.4-RELEASE',
"$manLocalDir/FreeBSD-8.4-RELEASE/man:$manLocalDir/FreeBSD-8.4-RELEASE/openssl/man",
    'FreeBSD 8.3-RELEASE',
"$manLocalDir/FreeBSD-8.3-RELEASE/man:$manLocalDir/FreeBSD-8.3-RELEASE/openssl/man",
    'FreeBSD 8.2-RELEASE',
"$manLocalDir/FreeBSD-8.2-RELEASE/man:$manLocalDir/FreeBSD-8.2-RELEASE/openssl/man",

    'FreeBSD 8.1-RELEASE',
"$manLocalDir/FreeBSD-8.1-RELEASE/man:$manLocalDir/FreeBSD-8.1-RELEASE/openssl/man",
    'FreeBSD 8.0-RELEASE',
"$manLocalDir/FreeBSD-8.0-RELEASE/man:$manLocalDir/FreeBSD-8.0-RELEASE/openssl/man",


    # FreeBSD Ports
    'FreeBSD Ports 2.2.8', "$manLocalDir/FreeBSD-ports-2.2.8-RELEASE/man:$manLocalDir/FreeBSD-ports-2.2.8-RELEASE/misc",
    'FreeBSD Ports 3.4', "$manLocalDir/FreeBSD-ports-3.4-RELEASE/man:$manLocalDir/FreeBSD-ports-3.4-RELEASE/misc",
    'FreeBSD Ports 3.5', "$manLocalDir/FreeBSD-ports-3.5-RELEASE/man:$manLocalDir/FreeBSD-ports-3.5-RELEASE/misc",
    'FreeBSD Ports 3.5.1', "$manLocalDir/FreeBSD-ports-3.5.1-RELEASE/man:$manLocalDir/FreeBSD-ports-3.5.1-RELEASE/misc",
    'FreeBSD Ports 4.1.1', "$manLocalDir/FreeBSD-ports-4.1.1-RELEASE/man:$manLocalDir/FreeBSD-ports-4.1.1-RELEASE/misc",
    'FreeBSD Ports 4.10', "$manLocalDir/FreeBSD-ports-4.10-RELEASE/man:$manLocalDir/FreeBSD-ports-4.10-RELEASE/misc",
    'FreeBSD Ports 4.11', "$manLocalDir/FreeBSD-ports-4.11-RELEASE/man:$manLocalDir/FreeBSD-ports-4.11-RELEASE/misc",
    'FreeBSD Ports 4.2', "$manLocalDir/FreeBSD-ports-4.2-RELEASE/man:$manLocalDir/FreeBSD-ports-4.2-RELEASE/misc",
    'FreeBSD Ports 4.3', "$manLocalDir/FreeBSD-ports-4.3-RELEASE/man:$manLocalDir/FreeBSD-ports-4.3-RELEASE/misc",
    'FreeBSD Ports 4.5', "$manLocalDir/FreeBSD-ports-4.5-RELEASE/man:$manLocalDir/FreeBSD-ports-4.5-RELEASE/misc",
    'FreeBSD Ports 4.6', "$manLocalDir/FreeBSD-ports-4.6-RELEASE/man:$manLocalDir/FreeBSD-ports-4.6-RELEASE/misc",
    'FreeBSD Ports 4.6.2', "$manLocalDir/FreeBSD-ports-4.6.2-RELEASE/man:$manLocalDir/FreeBSD-ports-4.6.2-RELEASE/misc",
    'FreeBSD Ports 4.7', "$manLocalDir/FreeBSD-ports-4.7-RELEASE",
    'FreeBSD Ports 4.8', "$manLocalDir/FreeBSD-ports-4.8-RELEASE/man:$manLocalDir/FreeBSD-ports-4.8-RELEASE/misc",
    'FreeBSD Ports 4.9', "$manLocalDir/FreeBSD-ports-4.9-RELEASE/man:$manLocalDir/FreeBSD-ports-4.9-RELEASE/misc",
    'FreeBSD Ports 5.1', "$manLocalDir/FreeBSD-ports-5.1-RELEASE",
    'FreeBSD Ports 5.2', "$manLocalDir/FreeBSD-ports-5.2-RELEASE/man:$manLocalDir/FreeBSD-ports-5.2-RELEASE/misc",
    'FreeBSD Ports 5.2.1', "$manLocalDir/FreeBSD-ports-5.2.1-RELEASE/man:$manLocalDir/FreeBSD-ports-5.2.1-RELEASE/misc",
    'FreeBSD Ports 5.3', "$manLocalDir/FreeBSD-ports-5.3-RELEASE/man:$manLocalDir/FreeBSD-ports-5.3-RELEASE/misc",
    'FreeBSD Ports 5.4', "$manLocalDir/FreeBSD-ports-5.4-RELEASE/man:$manLocalDir/FreeBSD-ports-5.4-RELEASE/misc",
    'FreeBSD Ports 5.5', "$manLocalDir/FreeBSD-ports-5.5-RELEASE/man:$manLocalDir/FreeBSD-ports-5.5-RELEASE/misc",
    'FreeBSD Ports 6.0', "$manLocalDir/FreeBSD-ports-6.0-RELEASE/man:$manLocalDir/FreeBSD-ports-6.0-RELEASE/misc",
    'FreeBSD Ports 6.2', "$manLocalDir/FreeBSD-ports-6.2-RELEASE",
    'FreeBSD Ports 6.3', "$manLocalDir/FreeBSD-ports-6.3-RELEASE/man:$manLocalDir/FreeBSD-ports-6.3-RELEASE/misc",
    'FreeBSD Ports 6.4', "$manLocalDir/FreeBSD-ports-6.4-RELEASE/man:$manLocalDir/FreeBSD-ports-6.4-RELEASE/misc",
    'FreeBSD Ports 7.0', "$manLocalDir/FreeBSD-ports-7.0-RELEASE",
    'FreeBSD Ports 7.1', "$manLocalDir/FreeBSD-ports-7.1-RELEASE/man:$manLocalDir/FreeBSD-ports-7.1-RELEASE/misc",
    'FreeBSD Ports 7.2', "$manLocalDir/FreeBSD-ports-7.2-RELEASE/man:$manLocalDir/FreeBSD-ports-7.2-RELEASE/misc",
    'FreeBSD Ports 7.3', "$manLocalDir/FreeBSD-ports-7.3-RELEASE",
    'FreeBSD Ports 7.4', "$manLocalDir/FreeBSD-ports-7.4-RELEASE/man:$manLocalDir/FreeBSD-ports-7.4-RELEASE/misc",
    'FreeBSD Ports 8.0', "$manLocalDir/FreeBSD-ports-8.0-RELEASE",
    'FreeBSD Ports 8.1', "$manLocalDir/FreeBSD-ports-8.1-RELEASE",
    'FreeBSD Ports 8.2', "$manLocalDir/FreeBSD-ports-8.2-RELEASE/man:$manLocalDir/FreeBSD-ports-8.2-RELEASE/misc",
    'FreeBSD Ports 8.3', "$manLocalDir/FreeBSD-ports-8.3-RELEASE/man:$manLocalDir/FreeBSD-ports-8.3-RELEASE/misc",
    'FreeBSD Ports 8.4', "$manLocalDir/FreeBSD-ports-8.4-RELEASE/man:$manLocalDir/FreeBSD-ports-8.4-RELEASE/misc",
    'FreeBSD Ports 9.0', "$manLocalDir/FreeBSD-ports-9.0-RELEASE/man:$manLocalDir/FreeBSD-ports-9.0-RELEASE/lib-perl5-perl-5.12.4-man:$manLocalDir/FreeBSD-ports-9.0-RELEASE/misc",
    'FreeBSD Ports 9.1', "$manLocalDir/FreeBSD-ports-9.1-RELEASE/man:$manLocalDir/FreeBSD-ports-9.1-RELEASE/misc",
    'FreeBSD Ports 9.2', "$manLocalDir/FreeBSD-ports-9.2-RELEASE/man:$manLocalDir/FreeBSD-ports-9.2-RELEASE/misc",
    'FreeBSD Ports 9.3', "$manLocalDir/FreeBSD-ports-9.3-RELEASE/man:$manLocalDir/FreeBSD-ports-9.3-RELEASE/misc",
    'FreeBSD Ports 10.0', "$manLocalDir/FreeBSD-ports-10.0-RELEASE/man:$manLocalDir/FreeBSD-ports-10.0-RELEASE/misc",
    'FreeBSD Ports 10.1', "$manLocalDir/FreeBSD-ports-10.1-RELEASE/man:$manLocalDir/FreeBSD-ports-10.1-RELEASE/misc",
    'FreeBSD Ports 10.2', "$manLocalDir/FreeBSD-ports-10.2-RELEASE/man:$manLocalDir/FreeBSD-ports-10.2-RELEASE/misc",
    'FreeBSD Ports 10.3', "$manLocalDir/FreeBSD-ports-10.3-RELEASE/man:$manLocalDir/FreeBSD-ports-10.3-RELEASE/misc",
    'FreeBSD Ports 10.4', "$manLocalDir/FreeBSD-ports-10.4-RELEASE/man:$manLocalDir/FreeBSD-ports-10.4-RELEASE/misc",
    'FreeBSD Ports 11.0', "$manLocalDir/FreeBSD-ports-11.0-RELEASE/man:$manLocalDir/FreeBSD-ports-11.0-RELEASE/misc",
    'FreeBSD Ports 11.1', "$manLocalDir/FreeBSD-ports-11.1-RELEASE/man:$manLocalDir/FreeBSD-ports-11.1-RELEASE/misc",
    'FreeBSD Ports 11.2', "$manLocalDir/FreeBSD-ports-11.2-RELEASE/man:$manLocalDir/FreeBSD-ports-11.2-RELEASE/misc",
    'FreeBSD Ports 11.3', "$manLocalDir/FreeBSD-ports-11.3-RELEASE/man:$manLocalDir/FreeBSD-ports-11.3-RELEASE/misc",
    'FreeBSD Ports 11.4', "$manLocalDir/FreeBSD-ports-11.4-RELEASE/man:$manLocalDir/FreeBSD-ports-11.4-RELEASE/misc",
    'FreeBSD Ports 12.0', "$manLocalDir/FreeBSD-ports-12.0-RELEASE/man:$manLocalDir/FreeBSD-ports-12.0-RELEASE/misc",
    'FreeBSD Ports 12.1', "$manLocalDir/FreeBSD-ports-12.1-RELEASE/man:$manLocalDir/FreeBSD-ports-12.1-RELEASE/misc",
    'FreeBSD Ports 12.2', "$manLocalDir/FreeBSD-ports-12.2-RELEASE/man:$manLocalDir/FreeBSD-ports-12.2-RELEASE/misc",
    'FreeBSD Ports 12.3', "$manLocalDir/FreeBSD-ports-12.3-RELEASE/man:$manLocalDir/FreeBSD-ports-12.3-RELEASE/misc",
    'FreeBSD Ports 12.4', "$manLocalDir/FreeBSD-ports-12.4-RELEASE/man:$manLocalDir/FreeBSD-ports-12.4-RELEASE/misc",
    'FreeBSD Ports 13.0', "$manLocalDir/FreeBSD-ports-13.0-RELEASE/man:$manLocalDir/FreeBSD-ports-13.0-RELEASE/misc",
    'FreeBSD Ports 13.1', "$manLocalDir/FreeBSD-ports-13.1-RELEASE/man:$manLocalDir/FreeBSD-ports-13.1-RELEASE/misc",
    'FreeBSD Ports 13.2', "$manLocalDir/FreeBSD-ports-13.2-RELEASE/man:$manLocalDir/FreeBSD-ports-13.2-RELEASE/misc",
    'FreeBSD Ports 13.3', "$manLocalDir/FreeBSD-ports-13.3-RELEASE/man:$manLocalDir/FreeBSD-ports-13.3-RELEASE/misc",
    'FreeBSD Ports 13.4', "$manLocalDir/FreeBSD-ports-13.4-RELEASE/man:$manLocalDir/FreeBSD-ports-13.4-RELEASE/misc",
    'FreeBSD Ports 13.5', "$manLocalDir/FreeBSD-ports-13.5-RELEASE/man:$manLocalDir/FreeBSD-ports-13.5-RELEASE/misc",
    'FreeBSD Ports 14.0', "$manLocalDir/FreeBSD-ports-14.0-RELEASE/man:$manLocalDir/FreeBSD-ports-14.0-RELEASE/misc",
    'FreeBSD Ports 14.1', "$manLocalDir/FreeBSD-ports-14.1-RELEASE/man:$manLocalDir/FreeBSD-ports-14.1-RELEASE/misc",
    'FreeBSD Ports 14.2', "$manLocalDir/FreeBSD-ports-14.2-RELEASE/man:$manLocalDir/FreeBSD-ports-14.2-RELEASE/misc",
    'FreeBSD Ports 14.3', "$manLocalDir/FreeBSD-ports-14.3-RELEASE/man:$manLocalDir/FreeBSD-ports-14.3-RELEASE/misc",
    'FreeBSD Ports 14.3.quarterly', "$manLocalDir/FreeBSD-ports-14.quarterly-RELEASE/man:$manLocalDir/FreeBSD-ports-14.quarterly-RELEASE/misc",


    # FreeBSD Releases + Ports
    'FreeBSD 2.2.8-RELEASE and Ports', "$manLocalDir/FreeBSD-2.2.8-RELEASE:$manLocalDir/FreeBSD-ports-2.2.8-RELEASE/man:$manLocalDir/FreeBSD-ports-2.2.8-RELEASE/misc",
    'FreeBSD 3.4-RELEASE and Ports', "$manLocalDir/FreeBSD-3.4-RELEASE:$manLocalDir/FreeBSD-ports-3.4-RELEASE/man:$manLocalDir/FreeBSD-ports-3.4-RELEASE/misc",
    'FreeBSD 3.5-RELEASE and Ports', "$manLocalDir/FreeBSD-3.5-RELEASE:$manLocalDir/FreeBSD-ports-3.5-RELEASE/man:$manLocalDir/FreeBSD-ports-3.5-RELEASE/misc",
    'FreeBSD 3.5.1-RELEASE and Ports', "$manLocalDir/FreeBSD-3.5.1-RELEASE:$manLocalDir/FreeBSD-ports-3.5.1-RELEASE/man:$manLocalDir/FreeBSD-ports-3.5.1-RELEASE/misc",
    'FreeBSD 4.1.1-RELEASE and Ports', "$manLocalDir/FreeBSD-4.1.1-RELEASE:$manLocalDir/FreeBSD-ports-4.1.1-RELEASE/man:$manLocalDir/FreeBSD-ports-4.1.1-RELEASE/misc",
    'FreeBSD 4.2-RELEASE and Ports', "$manLocalDir/FreeBSD-4.2-RELEASE:$manLocalDir/FreeBSD-ports-4.2-RELEASE/man:$manLocalDir/FreeBSD-ports-4.2-RELEASE/misc",
    'FreeBSD 4.3-RELEASE and Ports', "$manLocalDir/FreeBSD-4.3-RELEASE:$manLocalDir/FreeBSD-ports-4.3-RELEASE/man:$manLocalDir/FreeBSD-ports-4.3-RELEASE/misc",
    'FreeBSD 4.5-RELEASE and Ports', "$manLocalDir/FreeBSD-4.5-RELEASE:$manLocalDir/FreeBSD-ports-4.5-RELEASE/man:$manLocalDir/FreeBSD-ports-4.5-RELEASE/misc",
    'FreeBSD 4.6-RELEASE and Ports', "$manLocalDir/FreeBSD-4.6-RELEASE:$manLocalDir/FreeBSD-ports-4.6-RELEASE/man:$manLocalDir/FreeBSD-ports-4.6-RELEASE/misc",
    'FreeBSD 4.6.2-RELEASE and Ports', "$manLocalDir/FreeBSD-4.6.2-RELEASE:$manLocalDir/FreeBSD-ports-4.6.2-RELEASE/man:$manLocalDir/FreeBSD-ports-4.6.2-RELEASE/misc",
    'FreeBSD 4.8-RELEASE and Ports', "$manLocalDir/FreeBSD-4.8-RELEASE:$manLocalDir/FreeBSD-4.8-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-4.8-RELEASE/man:$manLocalDir/FreeBSD-ports-4.8-RELEASE/misc",
    'FreeBSD 4.9-RELEASE and Ports', "$manLocalDir/FreeBSD-4.9-RELEASE:$manLocalDir/FreeBSD-4.9-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-4.9-RELEASE/man:$manLocalDir/FreeBSD-ports-4.9-RELEASE/misc",
    'FreeBSD 4.10-RELEASE and Ports', "$manLocalDir/FreeBSD-4.10-RELEASE/man:$manLocalDir/FreeBSD-4.10-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-4.10-RELEASE/man:$manLocalDir/FreeBSD-ports-4.10-RELEASE/misc",
    'FreeBSD 4.11-RELEASE and Ports', "$manLocalDir/FreeBSD-4.11-RELEASE/man:$manLocalDir/FreeBSD-4.11-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-4.11-RELEASE/man:$manLocalDir/FreeBSD-ports-4.11-RELEASE/misc",
    'FreeBSD 5.2-RELEASE and Ports', "$manLocalDir/FreeBSD-5.2-RELEASE/man:$manLocalDir/FreeBSD-5.2-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-5.2-RELEASE/man:$manLocalDir/FreeBSD-ports-5.2-RELEASE/misc",
    'FreeBSD 5.2.1-RELEASE and Ports', "$manLocalDir/FreeBSD-5.2.1-RELEASE/man:$manLocalDir/FreeBSD-5.2.1-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-5.2.1-RELEASE/man:$manLocalDir/FreeBSD-ports-5.2.1-RELEASE/misc",
    'FreeBSD 5.3-RELEASE and Ports', "$manLocalDir/FreeBSD-5.3-RELEASE/man:$manLocalDir/FreeBSD-5.3-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-5.3-RELEASE/man:$manLocalDir/FreeBSD-ports-5.3-RELEASE/misc",
    'FreeBSD 5.4-RELEASE and Ports', "$manLocalDir/FreeBSD-5.4-RELEASE/man:$manLocalDir/FreeBSD-5.4-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-5.4-RELEASE/man:$manLocalDir/FreeBSD-ports-5.4-RELEASE/misc",
    'FreeBSD 5.5-RELEASE and Ports', "$manLocalDir/FreeBSD-5.5-RELEASE/man:$manLocalDir/FreeBSD-5.5-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-5.5-RELEASE/man:$manLocalDir/FreeBSD-ports-5.5-RELEASE/misc",
    'FreeBSD 6.0-RELEASE and Ports', "$manLocalDir/FreeBSD-6.0-RELEASE/man:$manLocalDir/FreeBSD-6.0-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-6.0-RELEASE/man:$manLocalDir/FreeBSD-ports-6.0-RELEASE/misc",
    'FreeBSD 6.3-RELEASE and Ports', "$manLocalDir/FreeBSD-6.3-RELEASE/man:$manLocalDir/FreeBSD-6.3-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-6.3-RELEASE/man:$manLocalDir/FreeBSD-ports-6.3-RELEASE/misc",
    'FreeBSD 6.4-RELEASE and Ports', "$manLocalDir/FreeBSD-6.4-RELEASE/man:$manLocalDir/FreeBSD-6.4-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-6.4-RELEASE/man:$manLocalDir/FreeBSD-ports-6.4-RELEASE/misc",
    'FreeBSD 7.1-RELEASE and Ports', "$manLocalDir/FreeBSD-7.1-RELEASE/man:$manLocalDir/FreeBSD-7.1-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-7.1-RELEASE/man:$manLocalDir/FreeBSD-ports-7.1-RELEASE/misc",
    'FreeBSD 7.2-RELEASE and Ports', "$manLocalDir/FreeBSD-7.2-RELEASE/man:$manLocalDir/FreeBSD-7.2-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-7.2-RELEASE/man:$manLocalDir/FreeBSD-ports-7.2-RELEASE/misc",
    'FreeBSD 7.4-RELEASE and Ports', "$manLocalDir/FreeBSD-7.4-RELEASE/man:$manLocalDir/FreeBSD-7.4-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-7.4-RELEASE/man:$manLocalDir/FreeBSD-ports-7.4-RELEASE/misc",
    'FreeBSD 8.2-RELEASE and Ports', "$manLocalDir/FreeBSD-8.2-RELEASE/man:$manLocalDir/FreeBSD-8.2-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-8.2-RELEASE/man:$manLocalDir/FreeBSD-ports-8.2-RELEASE/misc",
    'FreeBSD 8.3-RELEASE and Ports', "$manLocalDir/FreeBSD-8.3-RELEASE/man:$manLocalDir/FreeBSD-8.3-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-8.3-RELEASE/man:$manLocalDir/FreeBSD-ports-8.3-RELEASE/misc",
    'FreeBSD 9.1-RELEASE and Ports', "$manLocalDir/FreeBSD-9.1-RELEASE/man:$manLocalDir/FreeBSD-9.1-RELEASE/openssl/man:$manLocalDir/FreeBSD-ports-9.1-RELEASE/man:$manLocalDir/FreeBSD-ports-9.1-RELEASE/misc",

    'FreeBSD 7.4-RELEASE',
"$manLocalDir/FreeBSD-7.4-RELEASE/man:$manLocalDir/FreeBSD-7.4-RELEASE/openssl/man",

    'FreeBSD 7.3-RELEASE',
"$manLocalDir/FreeBSD-7.3-RELEASE/man:$manLocalDir/FreeBSD-7.3-RELEASE/openssl/man",

    'FreeBSD 7.2-RELEASE',
"$manLocalDir/FreeBSD-7.2-RELEASE/man:$manLocalDir/FreeBSD-7.2-RELEASE/openssl/man",
    'FreeBSD 7.1-RELEASE',
"$manLocalDir/FreeBSD-7.1-RELEASE/man:$manLocalDir/FreeBSD-7.1-RELEASE/openssl/man",
#    'FreeBSD Ports 7.1-RELEASE', "$manLocalDir/FreeBSD-ports-7.1-RELEASE",

    'FreeBSD 7.0-RELEASE',
"$manLocalDir/FreeBSD-7.0-RELEASE/man:$manLocalDir/FreeBSD-7.0-RELEASE/openssl/man",

    'FreeBSD 6.4-RELEASE',
"$manLocalDir/FreeBSD-6.4-RELEASE/man:$manLocalDir/FreeBSD-6.4-RELEASE/openssl/man",
    'FreeBSD 6.3-RELEASE',
"$manLocalDir/FreeBSD-6.3-RELEASE/man:$manLocalDir/FreeBSD-6.3-RELEASE/openssl/man",

    'FreeBSD 6.2-RELEASE',
"$manLocalDir/FreeBSD-6.2-RELEASE/man:$manLocalDir/FreeBSD-6.2-RELEASE/openssl/man",

    'FreeBSD 6.1-RELEASE',
"$manLocalDir/FreeBSD-6.1-RELEASE/man:$manLocalDir/FreeBSD-6.1-RELEASE/openssl/man",
    'FreeBSD 6.0-RELEASE',
"$manLocalDir/FreeBSD-6.0-RELEASE/man:$manLocalDir/FreeBSD-6.0-RELEASE/openssl/man",

    'FreeBSD 5.5-RELEASE',
"$manLocalDir/FreeBSD-5.5-RELEASE/man:$manLocalDir/FreeBSD-5.5-RELEASE/openssl/man",

    'FreeBSD 5.4-RELEASE',
"$manLocalDir/FreeBSD-5.4-RELEASE/man:$manLocalDir/FreeBSD-5.4-RELEASE/openssl/man",
    'FreeBSD 5.3-RELEASE',
"$manLocalDir/FreeBSD-5.3-RELEASE/man:$manLocalDir/FreeBSD-5.3-RELEASE/openssl/man",
    'FreeBSD 5.2.1-RELEASE',
"$manLocalDir/FreeBSD-5.2-RELEASE/man:$manLocalDir/FreeBSD-5.2-RELEASE/openssl/man",
    'FreeBSD 5.2-RELEASE',
"$manLocalDir/FreeBSD-5.2-RELEASE/man:$manLocalDir/FreeBSD-5.2-RELEASE/openssl/man",
    'FreeBSD 5.1-RELEASE',
"$manLocalDir/FreeBSD-5.1-RELEASE/man:$manLocalDir/FreeBSD-5.1-RELEASE/openssl/man",
    'FreeBSD 5.0-RELEASE', "$manLocalDir/FreeBSD-5.0-RELEASE",

    'FreeBSD 4.11-RELEASE',
"$manLocalDir/FreeBSD-4.11-RELEASE/man:$manLocalDir/FreeBSD-4.11-RELEASE/openssl/man:$manLocalDir/FreeBSD-4.11-RELEASE/perl/man",

    'FreeBSD 4.10-RELEASE',
"$manLocalDir/FreeBSD-4.10-RELEASE/man:$manLocalDir/FreeBSD-4.10-RELEASE/openssl/man:$manLocalDir/FreeBSD-4.10-RELEASE/perl/man",
    'FreeBSD 4.9-RELEASE',     "$manLocalDir/FreeBSD-4.9-RELEASE",
    'FreeBSD 4.8-RELEASE',     "$manLocalDir/FreeBSD-4.8-RELEASE",
    'FreeBSD 4.7-RELEASE',     "$manLocalDir/FreeBSD-4.7-RELEASE",
    'FreeBSD 4.6.2-RELEASE',   "$manLocalDir/FreeBSD-4.6.2-RELEASE",
    'FreeBSD 4.6-RELEASE',     "$manLocalDir/FreeBSD-4.6-RELEASE",
    'FreeBSD 4.5-RELEASE',     "$manLocalDir/FreeBSD-4.5-RELEASE",
    'FreeBSD 4.4-RELEASE',     "$manLocalDir/FreeBSD-4.4-RELEASE",
    'FreeBSD 4.3-RELEASE',     "$manLocalDir/FreeBSD-4.3-RELEASE",
    'FreeBSD 4.2-RELEASE',     "$manLocalDir/FreeBSD-4.2-RELEASE",
    'FreeBSD 4.1.1-RELEASE',   "$manLocalDir/FreeBSD-4.1.1-RELEASE",
    'FreeBSD 4.1-RELEASE',     "$manLocalDir/FreeBSD-4.1-RELEASE",
    'FreeBSD 4.0-RELEASE',     "$manLocalDir/FreeBSD-4.0-RELEASE",
    'FreeBSD 3.5.1-RELEASE',   "$manLocalDir/FreeBSD-3.5.1-RELEASE",
    'FreeBSD 3.4-RELEASE',     "$manLocalDir/FreeBSD-3.4-RELEASE",
    'FreeBSD 3.3-RELEASE',     "$manLocalDir/FreeBSD-3.3-RELEASE",
    'FreeBSD 3.2-RELEASE',     "$manLocalDir/FreeBSD-3.2-RELEASE",
    'FreeBSD 3.1-RELEASE',     "$manLocalDir/FreeBSD-3.1-RELEASE",
    'FreeBSD 3.0-RELEASE',     "$manLocalDir/FreeBSD-3.0-RELEASE",
    'FreeBSD 2.2.5-RELEASE',   "$manLocalDir/FreeBSD-2.2.5-RELEASE",
    'FreeBSD 2.2.6-RELEASE',   "$manLocalDir/FreeBSD-2.2.6-RELEASE",
    'FreeBSD 2.2.7-RELEASE',   "$manLocalDir/FreeBSD-2.2.7-RELEASE",
    'FreeBSD 2.2.8-RELEASE',   "$manLocalDir/FreeBSD-2.2.8-RELEASE",
    'FreeBSD 2.2.2-RELEASE',   "$manLocalDir/FreeBSD-2.2.2-RELEASE",
    'FreeBSD 2.2.1-RELEASE',   "$manLocalDir/FreeBSD-2.2.1-RELEASE",
    'FreeBSD 2.1.7.1-RELEASE', "$manLocalDir/FreeBSD-2.1.7.1-RELEASE",
    'FreeBSD 2.1.6.1-RELEASE', "$manLocalDir/FreeBSD-2.1.6.1-RELEASE",
    'FreeBSD 2.1.5-RELEASE',   "$manLocalDir/FreeBSD-2.1.5-RELEASE",
    'FreeBSD 2.1.0-RELEASE',   "$manLocalDir/FreeBSD-2.1.0-RELEASE",
    'FreeBSD 2.0.5-RELEASE',   "$manLocalDir/FreeBSD-2.0.5-RELEASE",
    'FreeBSD 2.0-RELEASE',     "$manLocalDir/FreeBSD-2.0-RELEASE",
    'FreeBSD 1.1.5.1-RELEASE', "$manLocalDir/FreeBSD-1.1.5.1-RELEASE",
    'FreeBSD 1.1-RELEASE',     "$manLocalDir/FreeBSD-1.1-RELEASE",
    'FreeBSD 1.0-RELEASE',     "$manLocalDir/FreeBSD-1.0-RELEASE",

    'OpenBSD 2.0', "$manLocalDir/OpenBSD-2.0",
    'OpenBSD 2.1', "$manLocalDir/OpenBSD-2.1",
    'OpenBSD 2.2', "$manLocalDir/OpenBSD-2.2",
    'OpenBSD 2.3', "$manLocalDir/OpenBSD-2.3",
    'OpenBSD 2.4', "$manLocalDir/OpenBSD-2.4",
    'OpenBSD 2.5', "$manLocalDir/OpenBSD-2.5",
    'OpenBSD 2.6', "$manLocalDir/OpenBSD-2.6",
    'OpenBSD 2.7', "$manLocalDir/OpenBSD-2.7",
    'OpenBSD 2.8', "$manLocalDir/OpenBSD-2.8",
    'OpenBSD 2.9', "$manLocalDir/OpenBSD-2.9",
    'OpenBSD 3.0', "$manLocalDir/OpenBSD-3.0",
    'OpenBSD 3.1', "$manLocalDir/OpenBSD-3.1",
    'OpenBSD 3.2', "$manLocalDir/OpenBSD-3.2",
    'OpenBSD 3.3', "$manLocalDir/OpenBSD-3.3",
    'OpenBSD 3.4',
    "$manLocalDir/OpenBSD-3.4/share/man:$manLocalDir/OpenBSD-3.4/X11R6/man",
    'OpenBSD 3.5',
    "$manLocalDir/OpenBSD-3.5/share/man:$manLocalDir/OpenBSD-3.5/X11R6/man",
    'OpenBSD 3.6',
    "$manLocalDir/OpenBSD-3.6/share/man:$manLocalDir/OpenBSD-3.6/X11R6/man",
    'OpenBSD 3.7', "$manLocalDir/OpenBSD-3.7",
    'OpenBSD 3.8', "$manLocalDir/OpenBSD-3.8",
    'OpenBSD 3.9', "$manLocalDir/OpenBSD-3.9",
    'OpenBSD 4.0', "$manLocalDir/OpenBSD-4.0",
    'OpenBSD 4.1', "$manLocalDir/OpenBSD-4.1",
    'OpenBSD 4.2', "$manLocalDir/OpenBSD-4.2",
    'OpenBSD 4.3', "$manLocalDir/OpenBSD-4.3",
    'OpenBSD 4.4', "$manLocalDir/OpenBSD-4.4",
    'OpenBSD 4.5', "$manLocalDir/OpenBSD-4.5",
    'OpenBSD 4.6', "$manLocalDir/OpenBSD-4.6",
    'OpenBSD 4.7', "$manLocalDir/OpenBSD-4.7",
    'OpenBSD 4.8', "$manLocalDir/OpenBSD-4.8",
    'OpenBSD 4.9', "$manLocalDir/OpenBSD-4.9",
    'OpenBSD 5.0', "$manLocalDir/OpenBSD-5.0",
    'OpenBSD 5.1', "$manLocalDir/OpenBSD-5.1",
    'OpenBSD 5.2', "$manLocalDir/OpenBSD-5.2",
    'OpenBSD 5.3', "$manLocalDir/OpenBSD-5.3",
    'OpenBSD 5.4', "$manLocalDir/OpenBSD-5.4",
    'OpenBSD 5.5', "$manLocalDir/OpenBSD-5.5",
    'OpenBSD 5.6', "$manLocalDir/OpenBSD-5.6",
    'OpenBSD 5.7', "$manLocalDir/OpenBSD-5.7",
    'OpenBSD 5.8', "$manLocalDir/OpenBSD-5.8",
    'OpenBSD 5.9', "$manLocalDir/OpenBSD-5.9",
    'OpenBSD 6.0', "$manLocalDir/OpenBSD-6.0",
    'OpenBSD 6.1', "$manLocalDir/OpenBSD-6.1",
    'OpenBSD 6.2', "$manLocalDir/OpenBSD-6.2",
    'OpenBSD 6.3', "$manLocalDir/OpenBSD-6.3",
    'OpenBSD 6.4', "$manLocalDir/OpenBSD-6.4",
    'OpenBSD 6.5', "$manLocalDir/OpenBSD-6.5",
    'OpenBSD 6.6', "$manLocalDir/OpenBSD-6.6",
    'OpenBSD 6.7', "$manLocalDir/OpenBSD-6.7",
    'OpenBSD 6.8', "$manLocalDir/OpenBSD-6.8",
    'OpenBSD 6.9', "$manLocalDir/OpenBSD-6.9",
    'OpenBSD 7.0', "$manLocalDir/OpenBSD-7.0",
    'OpenBSD 7.1', "$manLocalDir/OpenBSD-7.1",
    'OpenBSD 7.2', "$manLocalDir/OpenBSD-7.2",
    'OpenBSD 7.3', "$manLocalDir/OpenBSD-7.3",
    'OpenBSD 7.4', "$manLocalDir/OpenBSD-7.4",
    'OpenBSD 7.5', "$manLocalDir/OpenBSD-7.5",
    'OpenBSD 7.6', "$manLocalDir/OpenBSD-7.6",
    'OpenBSD 7.7', "$manLocalDir/OpenBSD-7.7",

    #'NetBSD 0.9',            "$manLocalDir/NetBSD-0.9",
    'NetBSD 1.0',   "$manLocalDir/NetBSD-1.0",
    'NetBSD 1.1',   "$manLocalDir/NetBSD-1.1",
    'NetBSD 1.2',   "$manLocalDir/NetBSD-1.2",
    'NetBSD 1.2.1', "$manLocalDir/NetBSD-1.2.1",
    'NetBSD 1.3',   "$manLocalDir/NetBSD-1.3",
    'NetBSD 1.3.1', "$manLocalDir/NetBSD-1.3.1",
    'NetBSD 1.3.2', "$manLocalDir/NetBSD-1.3.2",
    'NetBSD 1.3.3', "$manLocalDir/NetBSD-1.3.3",
    'NetBSD 1.4',   "$manLocalDir/NetBSD-1.4",
    'NetBSD 1.4.1', "$manLocalDir/NetBSD-1.4.1",
    'NetBSD 1.4.2', "$manLocalDir/NetBSD-1.4.2",
    'NetBSD 1.4.3', "$manLocalDir/NetBSD-1.4.3",
    'NetBSD 1.5',   "$manLocalDir/NetBSD-1.5",
    'NetBSD 1.5.1', "$manLocalDir/NetBSD-1.5.1",
    'NetBSD 1.5.2', "$manLocalDir/NetBSD-1.5.2",
    'NetBSD 1.5.3', "$manLocalDir/NetBSD-1.5.3",
    'NetBSD 1.6',   "$manLocalDir/NetBSD-1.6",
    'NetBSD 1.6.1', "$manLocalDir/NetBSD-1.6.1",
    'NetBSD 1.6.2', "$manLocalDir/NetBSD-1.6.2",
    'NetBSD 2.0',   "$manLocalDir/NetBSD-2.0",
    'NetBSD 2.0.2', "$manLocalDir/NetBSD-2.0.2",
    'NetBSD 2.1',   "$manLocalDir/NetBSD-2.1",
    'NetBSD 3.0',   "$manLocalDir/NetBSD-3.0",
    'NetBSD 3.1',   "$manLocalDir/NetBSD-3.1",
    'NetBSD 4.0',   "$manLocalDir/NetBSD-4.0",
    'NetBSD 4.0.1', "$manLocalDir/NetBSD-4.0.1",
    'NetBSD 5.0',   "$manLocalDir/NetBSD-5.0",
    'NetBSD 5.1',   "$manLocalDir/NetBSD-5.1",
    'NetBSD 6.0',   "$manLocalDir/NetBSD-6.0",
    'NetBSD 6.1.5', "$manLocalDir/NetBSD-6.1.5",
    'NetBSD 7.0',   "$manLocalDir/NetBSD-7.0",
    'NetBSD 7.1',   "$manLocalDir/NetBSD-7.1",
    'NetBSD 8.0',   "$manLocalDir/NetBSD-8.0",
    'NetBSD 8.1',   "$manLocalDir/NetBSD-8.1",
    'NetBSD 8.2',   "$manLocalDir/NetBSD-8.2",
    'NetBSD 9.0',   "$manLocalDir/NetBSD-9.0",
    'NetBSD 9.1',   "$manLocalDir/NetBSD-9.1",
    'NetBSD 9.2',   "$manLocalDir/NetBSD-9.2",
    'NetBSD 9.3',   "$manLocalDir/NetBSD-9.3",
    'NetBSD 9.4',   "$manLocalDir/NetBSD-9.4",
    'NetBSD 10.0',  "$manLocalDir/NetBSD-10.0",
    'NetBSD 10.1',  "$manLocalDir/NetBSD-10.1",

    '2.8 BSD',      "$manLocalDir/2.8BSD",
    '2.9.1 BSD',    "$manLocalDir/2.9.1BSD",
    '2.10 BSD',     "$manLocalDir/2.10BSD",
    '2.11 BSD',     "$manLocalDir/2.11BSD",
    '386BSD 0.0',   "$manLocalDir/386BSD-0.0",
    '386BSD 0.1',   "$manLocalDir/386BSD-0.1",
    '4.3BSD Reno',  "$manLocalDir/4.3BSD-Reno",
    '4.3BSD NET/2', "$manLocalDir/net2",
    '4.4BSD Lite2', "$manLocalDir/4.4BSD-Lite2",

    'Linux Slackware 3.1',    "$manLocalDir/Slackware-3.1",
    'Red Hat 4.2', "$manLocalDir/RedHat-4.2",
    'Red Hat 5.0', "$manLocalDir/RedHat-5.0",
    'Red Hat 5.2', "$manLocalDir/RedHat-5.2-i386",
    'Red Hat 6.1', "$manLocalDir/RedHat-6.1-i386",
    'Red Hat 6.2', "$manLocalDir/RedHat-6.2-i386",
    'Red Hat 7.0', "$manLocalDir/RedHat-7.0-i386",
    'Red Hat 7.1', "$manLocalDir/RedHat-7.1-i386",
    'Red Hat 7.2', "$manLocalDir/RedHat-7.2-i386",
    'Red Hat 7.3', "$manLocalDir/RedHat-7.3-i386",
    'Red Hat 8.0', "$manLocalDir/RedHat-8.0-i386",
    'Red Hat 9.0', "$manLocalDir/RedHat-9.0-i386",

    'CentOS 3.9', "$manLocalDir/CentOS-3.9",
    'CentOS 4.8', "$manLocalDir/CentOS-4.8",

    'CentOS 5.4', "$manLocalDir/CentOS-5.4",
    'CentOS 5.5', "$manLocalDir/CentOS-5.5",
    'CentOS 5.6', "$manLocalDir/CentOS-5.6",
    'CentOS 5.7', "$manLocalDir/CentOS-5.7",
    'CentOS 5.8', "$manLocalDir/CentOS-5.8",
    'CentOS 5.9', "$manLocalDir/CentOS-5.9",
    'CentOS 5.10', "$manLocalDir/CentOS-5.10",
    'CentOS 5.11', "$manLocalDir/CentOS-5.11",

    'CentOS 6.0', "$manLocalDir/CentOS-6.0",
    'CentOS 6.1', "$manLocalDir/CentOS-6.1",
    'CentOS 6.2', "$manLocalDir/CentOS-6.2",
    'CentOS 6.3', "$manLocalDir/CentOS-6.3",
    'CentOS 6.4', "$manLocalDir/CentOS-6.4",
    'CentOS 6.5', "$manLocalDir/CentOS-6.5",
    'CentOS 6.6', "$manLocalDir/CentOS-6.6",
    'CentOS 6.7', "$manLocalDir/CentOS-6.7",
    'CentOS 6.8', "$manLocalDir/CentOS-6.8",
    'CentOS 6.9', "$manLocalDir/CentOS-6.9",
    'CentOS 6.10', "$manLocalDir/CentOS-6.10",

    'CentOS 7.0', "$manLocalDir/CentOS-7.0",
    'CentOS 7.1', "$manLocalDir/CentOS-7.1",
    'CentOS 7.2', "$manLocalDir/CentOS-7.2",
    'CentOS 7.3', "$manLocalDir/CentOS-7.3",
    'CentOS 7.4', "$manLocalDir/CentOS-7.4",
    'CentOS 7.5', "$manLocalDir/CentOS-7.5",
    'CentOS 7.6', "$manLocalDir/CentOS-7.6",
    'CentOS 7.7', "$manLocalDir/CentOS-7.7",
    'CentOS 7.8', "$manLocalDir/CentOS-7.8",
    'CentOS 7.9', "$manLocalDir/CentOS-7.9",

    'Rocky 10.0', "$manLocalDir/Rocky-10.0",
    'Rocky 9.6', "$manLocalDir/Rocky-9.6",
    'Rocky 9.5', "$manLocalDir/Rocky-9.5",
    'Rocky 9.4', "$manLocalDir/Rocky-9.4",
    'Rocky 9.3', "$manLocalDir/Rocky-9.3",
    'Rocky 9.2', "$manLocalDir/Rocky-9.2",
    'Rocky 9.1', "$manLocalDir/Rocky-9.1",
    'Rocky 9.0', "$manLocalDir/Rocky-9.0",
    'Rocky 8.10', "$manLocalDir/Rocky-8.10",
    'Rocky 8.9', "$manLocalDir/Rocky-8.9",
    'Rocky 8.8', "$manLocalDir/Rocky-8.8",
    'Rocky 8.7', "$manLocalDir/Rocky-8.7",
    'Rocky 8.6', "$manLocalDir/Rocky-8.6",
    'Rocky 8.5', "$manLocalDir/Rocky-8.5",
    'Rocky 8.4', "$manLocalDir/Rocky-8.4",
    'Rocky 8.3', "$manLocalDir/Rocky-8.3",

    'SuSE 4.3',  "$manLocalDir/SuSE-4.3-i386",
    'SuSE 5.0',  "$manLocalDir/SuSE-5.0-i386",
    'SuSE 5.2',  "$manLocalDir/SuSE-5.2-i386",
    'SuSE 5.3',  "$manLocalDir/SuSE-5.3-i386",
    'SuSE 6.0',  "$manLocalDir/SuSE-6.0-i386",
    'SuSE 6.1',  "$manLocalDir/SuSE-6.1-i386",
    'SuSE 6.3',  "$manLocalDir/SuSE-6.3-i386",
    'SuSE 6.4',  "$manLocalDir/SuSE-6.4-i386",
    'SuSE 7.0',  "$manLocalDir/SuSE-7.0-i386",
    'SuSE 7.1',  "$manLocalDir/SuSE-7.1-i386",
    'SuSE 7.2',  "$manLocalDir/SuSE-7.2-i386",
    'SuSE 7.3',  "$manLocalDir/SuSE-7.3-i386",
    'SuSE 8.0',  "$manLocalDir/SuSE-8.0-i386",
    'SuSE 8.1',  "$manLocalDir/SuSE-8.1-i386",
    'SuSE 8.2',  "$manLocalDir/SuSE-8.2-i386",
    'SuSE 9.2',  "$manLocalDir/SuSE-9.2-i386",
    'SuSE 9.3',  "$manLocalDir/SuSE-9.3-i386",
    'SuSE 10.0', "$manLocalDir/SuSE-10.0",
    'SuSE 10.1', "$manLocalDir/SuSE-10.1",
    'SuSE 10.2', "$manLocalDir/SuSE-10.2",
    'SuSE 10.3', "$manLocalDir/SuSE-10.3",
    'SuSE 11.0', "$manLocalDir/SuSE-11.0",
    'SuSE 11.1', "$manLocalDir/SuSE-11.1",
    'SuSE 11.2', "$manLocalDir/SuSE-11.2",
    'SuSE 11.3', "$manLocalDir/SuSE-11.3",

    'SuSE ES 10 SP1', "$manLocalDir/SLES-10-SP1-i386",

    'openSUSE 10.2', "$manLocalDir/openSUSE-10.2",
    'openSUSE 10.3', "$manLocalDir/openSUSE-10.3",
    #'openSUSE 11.0', "$manLocalDir/openSUSE-11.0",
    #'openSUSE 11.1', "$manLocalDir/openSUSE-11.1",
    'openSUSE 11.2', "$manLocalDir/openSUSE-11.2",
    'openSUSE 11.3', "$manLocalDir/openSUSE-11.3",
    'openSUSE 11.4', "$manLocalDir/openSUSE-11.4",
    'openSUSE 13.1', "$manLocalDir/openSUSE-13.1",
    'openSUSE 13.2', "$manLocalDir/openSUSE-13.2",
    'openSUSE 42.1', "$manLocalDir/openSUSE-42.1",
    'openSUSE 42.2', "$manLocalDir/openSUSE-42.2",
    'openSUSE 42.3', "$manLocalDir/openSUSE-42.3",
    'openSUSE 15.0', "$manLocalDir/openSUSE-15.0",
    'openSUSE 15.1', "$manLocalDir/openSUSE-15.1",
    'openSUSE 15.2', "$manLocalDir/openSUSE-15.2",
    'openSUSE 15.3', "$manLocalDir/openSUSE-15.3-3",
    'openSUSE 15.4', "$manLocalDir/openSUSE-15.4",
    'openSUSE 15.5', "$manLocalDir/openSUSE-15.5",
    'openSUSE 15.6', "$manLocalDir/openSUSE-15.6",

    'Debian 2.0.0', "$manLocalDir/Debian-2.0r0/man:$manLocalDir/Debian-2.0r0/misc",
    'Debian 2.2.7', "$manLocalDir/Debian-2.2r7/man:$manLocalDir/Debian-2.2r7/misc",
    'Debian 3.1.8', "$manLocalDir/Debian-31r8/man:$manLocalDir/Debian-31r8/misc",
    'Debian 4.0.9', "$manLocalDir/Debian-40r9/man:$manLocalDir/Debian-40r9/misc",
    'Debian 5.0.10', "$manLocalDir/Debian-5010/man:$manLocalDir/Debian-5010/misc",
    'Debian 6.0.10', "$manLocalDir/Debian-6.0.10/man:$manLocalDir/Debian-6.0.10/misc",
    'Debian 7.11.0', "$manLocalDir/Debian-7.11.0/man:$manLocalDir/Debian-7.11.0/misc",
    'Debian 8.11.1', "$manLocalDir/Debian-8.11.1/man:$manLocalDir/Debian-8.11.1/misc",
    'Debian 9.13.0', "$manLocalDir/Debian-9.13.0/man:$manLocalDir/Debian-9.13.0/misc",
    'Debian 10.13.0', "$manLocalDir/Debian-10.13.0/man:$manLocalDir/Debian-10.13.0/misc",
    'Debian 11.11.0', "$manLocalDir/Debian-11.11.0/man:$manLocalDir/Debian-11.11.0/misc",
    'Debian 12.11.0', "$manLocalDir/Debian-12.11.0/man:$manLocalDir/Debian-12.11.0/misc",
    'Debian 13.0 unstable', "$manLocalDir/Debian-unstable/man:$manLocalDir/Debian-unstable/misc",

    'Ubuntu 23.10 mantic', "$manLocalDir/Ubuntu-mantic-23.10/man:$manLocalDir/Ubuntu-mantic-23.10/misc",

    'Ubuntu 24.04 noble', "$manLocalDir/Ubuntu-noble-24.04/man:$manLocalDir/Ubuntu-noble-24.04/misc",
    'Ubuntu 22.04 jammy', "$manLocalDir/Ubuntu-jammy-22.04/man:$manLocalDir/Ubuntu-jammy-22.04/misc",
    'Ubuntu 20.04 focal', "$manLocalDir/Ubuntu-focal-20.04/man:$manLocalDir/Ubuntu-focal-20.04/misc",
    'Ubuntu 18.04 bionic', "$manLocalDir/Ubuntu-bionic-18.04/man:$manLocalDir/Ubuntu-bionic-18.04/misc",
    'Ubuntu 16.04 xenial', "$manLocalDir/Ubuntu-xenial-16.04/man:$manLocalDir/Ubuntu-xenial-16.04/misc",
    'Ubuntu 14.04 trusty', "$manLocalDir/Ubuntu-trusty-14.04/man:$manLocalDir/Ubuntu-trusty-14.04/misc",

    'DragonFly 6.4.0',  "$manLocalDir/DragonFly-6.4.0",
    'DragonFly 5.8.3',  "$manLocalDir/DragonFly-5.8.3",
    'DragonFly 4.8.1',  "$manLocalDir/DragonFly-4.8.1",
    'DragonFly 3.8.2',  "$manLocalDir/DragonFly-3.8.2",
    'DragonFly 2.10.1', "$manLocalDir/DragonFly-2.10.1",
    'DragonFly 1.12.1', "$manLocalDir/DragonFly-1.12.1",
    'DragonFly 1.0A',   "$manLocalDir/DragonFly-1.0A",

    'Dell UNIX SVR4 2.2', "$manLocalDir/Dell-SVR4-2.2",

    'HP-UX 11.22', "$manLocalDir/HP-UX-11.22",
    'HP-UX 11.20', "$manLocalDir/HP-UX-11.20",
    'HP-UX 11.11', "$manLocalDir/HP-UX-11.11",
    'HP-UX 11.00', "$manLocalDir/HP-UX-11.00",
    'HP-UX 10.20', "$manLocalDir/HP-UX-10.20",
    'HP-UX 10.10', "$manLocalDir/HP-UX-10.10",
    'HP-UX 10.01', "$manLocalDir/HP-UX-10.01",
    'HP-UX 9.07',  "$manLocalDir/HP-UX-9.07",
    'HP-UX 8.07',  "$manLocalDir/HP-UX-8.07",

    'IRIX 6.5.30',  "$manLocalDir/IRIX-6.5.30/catman/a_man:$manLocalDir/IRIX-6.5.30/catman/p_man:$manLocalDir/IRIX-6.5.30/catman/u_man:$manLocalDir/IRIX-6.5.30/dt",

    'OpenIndiana 2024.10',  "$manLocalDir/OpenIndiana-2024.10/share/man",
    'OpenIndiana 2022.10',  "$manLocalDir/OpenIndiana-2022.10/share/man",
    'OpenIndiana 2020.10',  "$manLocalDir/OpenIndiana-2020.10/share/man",
    'OpenIndiana 2017.10',  "$manLocalDir/OpenIndiana-2017.10/share/man",
    'OpenIndiana 2015.10',  "$manLocalDir/OpenIndiana-2015.10/share/man",
    'OpenIndiana 2013.08',  "$manLocalDir/OpenIndiana-2013.08/share/man",

    'OpenSolaris 2010.03',  "$manLocalDir/OpenSolaris-2010.03-snv_134/share/man:$manLocalDir/OpenSolaris-2010.03-snv_134/sfw/share/man",
    'OpenSolaris 2009.06',  "$manLocalDir/OpenSolaris-2009.06-snv_111b/share/man:$manLocalDir/OpenSolaris-2009.06-snv_111b/sfw/share/man",

    'SunOS 5.10',  "$manLocalDir/SunOS-5.10",
    'SunOS 5.9',   "$manLocalDir/SunOS-5.9",
    'SunOS 5.8',   "$manLocalDir/SunOS-5.8",
    'SunOS 5.7',   "$manLocalDir/SunOS-5.7",
    'SunOS 5.6',   "$manLocalDir/SunOS-5.6",
    'SunOS 5.5.1', "$manLocalDir/SunOS-5.5.1",
    'SunOS 4.1.3', "$manLocalDir/SunOS-4.1.3",

    # full name: Sun UNIX 4.2* Software Release 0.4 (*Berkeley Beta Release)
    # 1/2'' Boot Tape 700-0586-01
    # alias SunOS 0.4, apparently released in April 1983 based on 4.2BSD beta
    'Sun UNIX 0.4', "$manLocalDir/Sun-UNIX-0.4",

    'macOS 15.5.0',   "$manLocalDir/macOS-15.5.0/man:$manLocalDir/macOS-15.5.0/developer-man:$manLocalDir/macOS-15.5.0/developer-platform-sdk-man:$manLocalDir/macOS-15.5.0/xctoolchain-man",  
    'macOS 14.7.5', "$manLocalDir/macOS-14.7.5/man:$manLocalDir/macOS-14.7.5/developer-man:$manLocalDir/macOS-14.7.5/developer-platform-man:$manLocalDir/macOS-14.7.5/developer-platform-sdk-man:$manLocalDir/macOS-14.7.5/xctoolchain-man",  
    'macOS 13.6.5', "$manLocalDir/macOS-13.6.5/man:$manLocalDir/macOS-13.6.5/developer-man:$manLocalDir/macOS-13.6.5/developer-platform-man:$manLocalDir/macOS-13.6.5/developer-platform-sdk-man:$manLocalDir/macOS-13.6.5/xctoolchain-man",  
    'macOS 12.7.3', "$manLocalDir/macOS-12.7.3/man:$manLocalDir/macOS-12.7.3/developer-man:$manLocalDir/macOS-12.7.3/developer-platform-man:$manLocalDir/macOS-12.7.3/developer-platform-sdk-man:$manLocalDir/macOS-12.7.3/xctoolchain-man",
    'macOS 11.1',    "$manLocalDir/macOS-11.1",
    'macOS 10.15.0', "$manLocalDir/macOS-10.15.0",
    'macOS 10.13.6', "$manLocalDir/macOS-10.13.6",
    'macOS 10.12.0', "$manLocalDir/macOS-10.12.0",

    #'XFree86 3.2',      "$manLocalDir/XFree86-3.2",
    'XFree86 2.1',      "$manLocalDir/XFree86-2.1",
    'XFree86 3.3',      "$manLocalDir/XFree86-3.3",
    'XFree86 3.3.6',    "$manLocalDir/XFree86-3.3.6",
    'XFree86 4.0',      "$manLocalDir/XFree86-4.0",
    'XFree86 4.0.1',    "$manLocalDir/XFree86-4.0.1",
    'XFree86 4.0.2',    "$manLocalDir/XFree86-4.0.2",
    'XFree86 4.1.0',    "$manLocalDir/XFree86-4.1.0",
    'XFree86 4.2.0',    "$manLocalDir/XFree86-4.2.0",
    'XFree86 4.2.99.3', "$manLocalDir/XFree86-4.2.99.3",
    'XFree86 4.3.0',    "$manLocalDir/XFree86-4.3.0",
    'XFree86 4.4.0',    "$manLocalDir/XFree86-4.4.0",
    'XFree86 4.5.0',    "$manLocalDir/XFree86-4.5.0",
    'XFree86 4.6.0',    "$manLocalDir/XFree86-4.6.0",
    'XFree86 4.7.0',    "$manLocalDir/XFree86-4.7.0",
    'XFree86 4.8.0',    "$manLocalDir/XFree86-4.8.0",

    'X11R6.7.0', "$manLocalDir/X11R6.7.0",
    'X11R6.8.2', "$manLocalDir/X11R6.8.2",
    'X11R6.9.0', "$manLocalDir/X11R6.9.0",
    'X11R7.2',   "$manLocalDir/X11R7.2",
    'X11R7.3.2', "$manLocalDir/X11R7.3.2",
    'X11R7.4',   "$manLocalDir/X11R7.4",

    'ULTRIX 4.2',      "$manLocalDir/ULTRIX-4.2",
    'Ultrix-32 2.0/VAX', "$manLocalDir/Ultrix-32-2.0-VAX",
    'OSF1 V1.0/mips', "$manLocalDir/OSF1-V1.0-mips/os",
    'OSF1 V4.0/alpha', "$manLocalDir/OSF1-V4.0-alpha",
    'OSF1 V5.1/alpha', "$manLocalDir/OSF1-V5.1-alpha",

    'Inferno 4th Edition',         "$manLocalDir/Inferno",
    'Plan 9',                      "$manLocalDir/plan9",
    'Minix 2.0.0',                 "$manLocalDir/Minix-2.0.0",
    'Minix 3.1.5',                 "$manLocalDir/Minix-3.1.5",
    'Minix 3.1.6',                 "$manLocalDir/Minix-3.1.6",
    'Minix 3.1.7',                 "$manLocalDir/Minix-3.1.7",
    'Minix 3.1.7',                 "$manLocalDir/Minix-3.1.8",
    'Minix 3.2.0',                 "$manLocalDir/Minix-3.2.0",
    'Minix 3.2.1',                 "$manLocalDir/Minix-3.2.1",
    'Minix 3.3.0',                 "$manLocalDir/Minix-3.3.0",
    'Unix Seventh Edition',        "$manLocalDir/v7man",

    "Darwin 1.3.1/x86",            "$manLocalDir/Darwin-1.3.1-x86",
    "Darwin 1.4.1/x86",            "$manLocalDir/Darwin-1.4.1-x86",
    "Darwin 6.0.2/x86",            "$manLocalDir/Darwin-6.0.2-x86",
    "Darwin 7.0.1",                "$manLocalDir/Darwin-7.0.1",
    "Darwin 8.0.1/ppc",            "$manLocalDir/Darwin-8.0.1-ppc",
    "OpenDarwin 20030208pre4/ppc", "$manLocalDir/OpenDarwin-20030208pre4-ppc",
    "OpenDarwin 6.6.1/x86",        "$manLocalDir/OpenDarwin-6.6.1-x86",
    "OpenDarwin 6.6.2/x86",        "$manLocalDir/OpenDarwin-6.6.2-x86",
    "OpenDarwin 7.2.1",            "$manLocalDir/OpenDarwin-7.2.1",

    'NeXTSTEP 3.3',  "$manLocalDir/NeXTSTEP-3.3",
    'OpenStep 4.2',  "$manLocalDir/OpenStep-4.2",
    'Rhapsody DR1',  "$manLocalDir/Rhapsody-DR1",
    'Rhapsody DR2',  "$manLocalDir/Rhapsody-DR2",
    'MACH 2.5/i386', "$manLocalDir/MACH-2.5-i386",
);

my @no_html_output = (
    'IRIX 6.5.30'
);

my @no_pdf_output = (
    '386BSD 0.0',
    '386BSD 0.1',
    '4.4BSD Lite2',
    'NetBSD 0.9',
    'NetBSD 1.0',
    'NetBSD 1.1',
    'NetBSD 1.2',
    'NetBSD 1.2.1',
    'OpenBSD 2.0',
    'OpenBSD 2.1',
    'OpenBSD 2.2',
    'OpenBSD 2.3',
    'OpenBSD 2.4',
    'OpenBSD 2.5',
    'OpenBSD 2.6',
    'OpenBSD 2.7',
    'OpenBSD 2.8',
    'OpenBSD 2.9',
    'OpenBSD 3.0',
    'OpenBSD 3.1',
    'OpenBSD 3.2',
    'OpenBSD 3.3',
    'OpenBSD 3.4',
    'OpenBSD 3.5',
    'OpenBSD 3.6',
    'OpenBSD 3.7',
    'OpenBSD 3.8',
    'OpenBSD 3.9',
    'OpenBSD 4.0',
    'OpenBSD 4.1',
    'OpenBSD 4.2',
    'OpenBSD 4.3',
    'OpenBSD 4.4',
    'OpenBSD 4.5',
    'OpenBSD 4.6',
    'OpenBSD 4.7',
    'OpenBSD 4.8',
    'OpenBSD 4.9',
    'IRIX 6.5.30',
    'Dell UNIX SVR4 2.2',
);

my %no_pdf_output = map { $_ => 1 } @no_pdf_output;
my %no_html_output = map { $_ => 1 } @no_html_output;

my %valid_arch = map { $_ => 1 }
  qw/aarch64 acorn26 acorn32 algor alpha amd64 amiga arc arm arm26 arm32 arm64 armish atari aviion bebox cats cesfic cobalt dreamcast evbarm evbmips evbppc evbsh3 evbsh5 hp300 hp700 hpcarm hpcmips hpcsh hppa hppa64 i386 ibmnws landisk loongson luna68k luna88k mac68k macppc mipsco mmeye mvme68k mvme88k mvmeppc netwinder news68k newsmips next68k ofppc palm pc532 pegasos playstation2 pmax pmppc powerpc prep sandpoint sbmips sgi sgimips shark socppc sparc sparc64 sun2 sun3 sun3x tahoe vax walnut wgrisc x68k zaurus/;

my $default_arch = '';
my %arch_names = ('default' => 'All Architectures');

my %arch = ( 
'FreeBSD 11.3-RELEASE' => { 'default' => 'i386', 'arch' => [qw/amd64 arm i386 powerpc sparc64 aarch64/] } ,
'FreeBSD 11.2-RELEASE' => { 'default' => 'i386', 'arch' => [qw/amd64 arm i386 powerpc sparc64 aarch64/] } ,
'FreeBSD 11.1-RELEASE' => { 'default' => 'i386', 'arch' => [qw/amd64 arm i386 powerpc sparc64 aarch64/] } ,
'FreeBSD 11.0-RELEASE' => { 'default' => 'i386', 'arch' => [qw/amd64 arm i386 powerpc sparc64 aarch64/] } ,
'FreeBSD 10.4-RELEASE' => { 'default' => 'i386', 'arch' => [qw/amd64 arm i386 powerpc sparc64/] } ,
'FreeBSD 10.3-RELEASE' => { 'default' => 'i386', 'arch' => [qw/amd64 arm i386 powerpc sparc64/] } ,
'FreeBSD 10.2-RELEASE' => { 'default' => 'i386', 'arch' => [qw/amd64 arm i386 powerpc sparc64/] } ,
'FreeBSD 10.1-RELEASE' => { 'default' => 'i386', 'arch' => [qw/amd64 arm i386 powerpc sparc64/] } ,
'FreeBSD 10.0-RELEASE' => { 'default' => 'i386', 'arch' => [qw/amd64 arm i386 powerpc sparc64/] } ,
'FreeBSD 9.3-RELEASE' => { 'default' => 'i386', 'arch' => [qw/amd64 arm i386 powerpc sparc64/] } ,
'FreeBSD 9.2-RELEASE' => { 'default' => 'i386', 'arch' => [qw/amd64 arm i386 powerpc sparc64/] } ,
'FreeBSD 9.1-RELEASE' => { 'default' => 'i386', 'arch' => [qw/amd64 arm i386 powerpc sparc64/] } ,
'FreeBSD 9.0-RELEASE' => { 'default' => 'i386', 'arch' => [qw/amd64 arm i386 powerpc sparc64/] } ,
'FreeBSD 8.4-RELEASE' => { 'default' => 'i386', 'arch' => [qw/amd64 arm i386 powerpc sparc64/] } ,
'FreeBSD 8.3-RELEASE' => { 'default' => 'i386', 'arch' => [qw/amd64 arm i386 powerpc sparc64/] } ,
'FreeBSD 8.2-RELEASE' => { 'default' => 'i386', 'arch' => [qw/amd64 arm i386 powerpc sparc64/] } ,
'NetBSD 5.1' => { 'arch' => [qw/acorn26 acorn32 alpha amiga arc atari cobalt dreamcast evbarm evbmips evbppc hp300 hp700 hpcarm hpcmips hpcsh i386 mac68k macppc mvme68k pmax prep sgimips sparc sparc64 sun2 sun3 vax x68k/] } ,
'NetBSD 6.0' => { 'arch' => [qw/acorn26 acorn32 alpha amiga arc atari cobalt dreamcast evbarm evbmips evbppc hp300 hp700 hpcarm hpcmips hpcsh i386 mac68k macppc mvme68k pmax prep sgimips sparc sparc64 sun2 sun3 vax x68k/] } ,
'NetBSD 6.1.5' => { 'arch' => [qw/acorn26 acorn32 algor alpha amd64 amiga arc atari bebox cats cesfic cobalt dreamcast emips evbarm evbmips evbppc evbsh3 hp300 hp700 hpcarm hpcmips hpcsh i386 ibmnws luna68k mac68k macppc mipsco mmeye mvme68k mvmeppc netwinder news68k newsmips next68k ofppc pmax prep sandpoint sbmips sgimips shark sparc sparc64 sun2 sun3 vax x68k x86/] } ,
'NetBSD 7.0' => { 'arch' => [qw/acorn26 acorn32 algor alpha amd64 amiga arc atari bebox cats cesfic cobalt dreamcast emips evbarm evbmips evbppc evbsh3 hp300 hp700 hpcarm hpcmips hpcsh i386 ibmnws luna68k mac68k macppc mipsco mmeye mvme68k mvmeppc netwinder news68k newsmips next68k ofppc pmax prep sandpoint sbmips sgimips shark sparc sparc64 sun2 sun3 vax x68k x86/] } ,
'NetBSD 7.1' => { 'arch' => [qw/acorn26 acorn32 algor alpha amd64 amiga arc atari bebox cats cesfic cobalt dreamcast emips evbarm evbmips evbppc evbsh3 hp300 hpcarm hpcmips hpcsh hppa i386 ibmnws luna68k mac68k macppc mipsco mmeye mvme68k mvmeppc netwinder news68k newsmips next68k ofppc playstation2 pmax prep sandpoint sbmips sgimips shark sparc sparc64 sun2 sun3 vax x68k x86/] } ,
'NetBSD 8.0' => { 'arch' => [qw/acorn26 acorn32 algor alpha amd64 amiga arc atari bebox cats cesfic cobalt dreamcast emips evbarm evbmips evbppc evbsh3 hp300 hpcarm hpcmips hpcsh hppa i386 ibmnws luna68k mac68k macppc mipsco mmeye mvme68k mvmeppc netwinder news68k newsmips next68k ofppc playstation2 pmax prep sandpoint sbmips sgimips shark sparc sparc64 sun2 sun3 vax x68k x86/] } ,
'NetBSD 8.1' => { 'arch' => [qw/acorn26 acorn32 algor alpha amd64 amiga arc atari bebox cats cesfic cobalt dreamcast emips evbarm evbmips evbppc evbsh3 hp300 hpcarm hpcmips hpcsh hppa i386 ibmnws luna68k mac68k macppc mipsco mmeye mvme68k mvmeppc netwinder news68k newsmips next68k ofppc playstation2 pmax prep sandpoint sbmips sgimips shark sparc sparc64 sun2 sun3 vax x68k x86/] } ,
'NetBSD 8.2' => { 'arch' => [qw/acorn26 acorn32 algor alpha amd64 amiga arc atari bebox cats cesfic cobalt dreamcast emips evbarm evbmips evbppc evbsh3 hp300 hpcarm hpcmips hpcsh hppa i386 ibmnws luna68k mac68k macppc mipsco mmeye mvme68k mvmeppc netwinder news68k newsmips next68k ofppc playstation2 pmax prep sandpoint sbmips sgimips shark sparc sparc64 sun2 sun3 vax x68k x86/] } ,
'NetBSD 9.0' => { 'arch' => [qw/acorn26 acorn32 algor alpha amd64 amiga arc atari bebox cats cesfic cobalt dreamcast emips evbarm evbmips evbppc evbsh3 hp300 hpcarm hpcmips hpcsh hppa i386 ibmnws luna68k mac68k macppc mipsco mmeye mvme68k mvmeppc netwinder news68k newsmips next68k ofppc playstation2 pmax prep sandpoint sbmips sgimips shark sparc sparc64 sun2 sun3 vax x68k x86/] } ,
'NetBSD 9.1' => { 'arch' => [qw/acorn26 acorn32 algor alpha amd64 amiga arc atari bebox cats cesfic cobalt dreamcast emips evbarm evbmips evbppc evbsh3 hp300 hpcarm hpcmips hpcsh hppa i386 ibmnws luna68k mac68k macppc mipsco mmeye mvme68k mvmeppc netwinder news68k newsmips next68k ofppc playstation2 pmax prep sandpoint sbmips sgimips shark sparc sparc64 sun2 sun3 vax x68k x86/] } ,
'NetBSD 9.2' => { 'arch' => [qw/acorn26 acorn32 algor alpha amd64 amiga arc atari bebox cats cesfic cobalt dreamcast emips evbarm evbmips evbppc evbsh3 hp300 hpcarm hpcmips hpcsh hppa i386 ibmnws luna68k mac68k macppc mipsco mmeye mvme68k mvmeppc netwinder news68k newsmips next68k ofppc playstation2 pmax prep sandpoint sbmips sgimips shark sparc sparc64 sun2 sun3 vax x68k x86/] } ,
'NetBSD 9.3' => { 'arch' => [qw/acorn26 acorn32 algor alpha amd64 amiga arc atari bebox cats cesfic cobalt dreamcast emips evbarm evbmips evbppc evbsh3 hp300 hpcarm hpcmips hpcsh hppa i386 ibmnws luna68k mac68k macppc mipsco mmeye mvme68k mvmeppc netwinder news68k newsmips next68k ofppc playstation2 pmax prep sandpoint sbmips sgimips shark sparc sparc64 sun2 sun3 vax x68k x86/] } ,
'NetBSD 9.4' => { 'arch' => [qw/acorn26 acorn32 algor alpha amd64 amiga arc atari bebox cats cesfic cobalt dreamcast emips evbarm evbmips evbppc evbsh3 hp300 hpcarm hpcmips hpcsh hppa i386 ibmnws luna68k mac68k macppc mipsco mmeye mvme68k mvmeppc netwinder news68k newsmips next68k ofppc playstation2 pmax prep sandpoint sbmips sgimips shark sparc sparc64 sun2 sun3 vax x68k x86/] } ,
'NetBSD 10.0' => { 'arch' => [qw/acorn26 acorn32 algor alpha amd64 amiga arc atari bebox cats cesfic cobalt dreamcast emips evbarm evbmips evbppc evbsh3 hp300 hpcarm hpcmips hpcsh hppa i386 ibmnws luna68k mac68k macppc mipsco mmeye mvme68k mvmeppc netwinder news68k newsmips next68k ofppc playstation2 pmax prep sandpoint sbmips sgimips shark sparc sparc64 sun2 sun3 vax x68k x86/] } ,
'NetBSD 10.1' => { 'arch' => [qw/acorn26 acorn32 algor alpha amd64 amiga arc atari bebox cats cesfic cobalt dreamcast emips evbarm evbmips evbppc evbsh3 hp300 hpcarm hpcmips hpcsh hppa i386 ibmnws luna68k mac68k macppc mipsco mmeye mvme68k mvmeppc netwinder news68k newsmips next68k ofppc playstation2 pmax prep sandpoint sbmips sgimips shark sparc sparc64 sun2 sun3 vax x68k x86/] } ,
'OpenBSD 4.7' => { 'arch' => [qw/alpha amd64 armish aviion hp300 hppa hppa64 i386 landisk loongson luna88k mac68k macppc mvme68k mvme88k mvmeppc palm sgi socppc sparc sparc64 vax zaurus/] }, 
'OpenBSD 4.8' => { 'arch' => [qw/alpha amd64 armish aviion hp300 hppa hppa64 i386 landisk loongson luna88k mac68k macppc mvme68k mvme88k mvmeppc palm sgi socppc sparc sparc64 vax zaurus/] }, 
'OpenBSD 4.9' => { 'arch' => [qw/alpha amd64 armish aviion hp300 hppa hppa64 i386 landisk loongson luna88k mac68k macppc mvme68k mvme88k mvmeppc palm sgi socppc sparc sparc64 vax zaurus/] }, 
'OpenBSD 5.0' => { 'arch' => [qw/alpha amd64 armish aviion hp300 hppa hppa64 i386 landisk loongson luna88k mac68k macppc mvme68k mvme88k mvmeppc palm sgi socppc sparc sparc64 vax zaurus/] }, 
'OpenBSD 5.1' => { 'arch' => [qw/alpha amd64 armish aviion hp300 hppa hppa64 i386 landisk loongson luna88k mac68k macppc mvme68k mvme88k mvmeppc palm sgi socppc sparc sparc64 vax zaurus/] }, 
'OpenBSD 5.2' => { 'arch' => [qw/alpha amd64 armish aviion hp300 hppa hppa64 i386 landisk loongson luna88k mac68k macppc mvme68k mvme88k mvmeppc palm sgi socppc sparc sparc64 vax zaurus/] }, 
'OpenBSD 5.3' => { 'arch' => [qw/alpha amd64 armish aviion hp300 hppa hppa64 i386 landisk loongson luna88k mac68k macppc mvme68k mvme88k mvmeppc palm sgi socppc sparc sparc64 vax zaurus/] }, 
'OpenBSD 5.4' => { 'arch' => [qw/alpha amd64 armish aviion beagle hp300 hppa hppa64 i386 landisk loongson luna88k macppc mvme68k mvme88k octeon sgi socppc sparc sparc64 vax zaurus/] }, 
'OpenBSD 5.5' => { 'arch' => [qw/alpha amd64 armish armv7 aviion hp300 hppa hppa64 i386 landisk loongson luna88k macppc mvme68k mvme88k octeon sgi socppc sparc sparc64 vax zaurus/] }, 
'OpenBSD 5.6' => { 'arch' => [qw/alpha amd64 armish armv7 aviion hppa hppa64 i386 landisk loongson luna88k macppc octeon sgi socppc sparc sparc64 vax zaurus/] }, 
'OpenBSD 5.7' => { 'arch' => [qw/alpha amd64 armish armv7 aviion hppa hppa64 i386 landisk loongson luna88k macppc octeon sgi socppc sparc sparc64 vax zaurus/] }, 
'OpenBSD 5.8' => { 'arch' => [qw/alpha amd64 armish armv7 aviion hppa hppa64 i386 landisk loongson luna88k macppc octeon sgi socppc sparc sparc64 vax zaurus/] }, 
'OpenBSD 5.9' => { 'arch' => [qw/alpha amd64 armish armv7 hppa hppa64 i386 landisk loongson luna88k macppc octeon sgi socppc sparc sparc64 vax zaurus/] }, 
'OpenBSD 6.0' => { 'arch' => [qw/alpha amd64 armish armv7 hppa i386 landisk loongson luna88k macppc octeon sgi socppc sparc sparc64 zaurus/] }, 
'OpenBSD 6.1' => { 'arch' => [qw/alpha amd64 armv7 hppa i386 landisk loongson luna88k macppc octeon sgi socppc sparc64/] }, 
'OpenBSD 6.2' => { 'arch' => [qw/alpha amd64 armv7 hppa i386 landisk loongson luna88k macppc octeon sgi socppc sparc64/] }, 
'OpenBSD 6.3' => { 'arch' => [qw/alpha amd64 armv7 hppa i386 landisk loongson luna88k macppc octeon sgi socppc sparc64/] }, 
'OpenBSD 6.4' => { 'arch' => [qw/alpha amd64 armv7 hppa i386 landisk loongson luna88k macppc octeon sgi socppc sparc64/] }, 
'OpenBSD 6.5' => { 'arch' => [qw/alpha amd64 armv7 hppa i386 landisk loongson luna88k macppc octeon sgi socppc sparc64/] }, 
'OpenBSD 6.6' => { 'arch' => [qw/alpha amd64 armv7 hppa i386 landisk loongson luna88k macppc octeon sgi socppc sparc64/] }, 
'OpenBSD 6.7' => { 'arch' => [qw/alpha amd64 armv7 hppa i386 landisk loongson luna88k macppc octeon sgi socppc sparc64/] }, 
'OpenBSD 6.8' => { 'arch' => [qw/alpha amd64 arm64 armv7 hppa i386 landisk loongson luna88k macppc octeon powerpc64 sgi sparc64/] }, 
'OpenBSD 6.9' => { 'arch' => [qw/alpha amd64 arm64 armv7 hppa i386 landisk loongson luna88k macppc octeon powerpc64 sgi sparc64/] }, 
'OpenBSD 7.0' => { 'arch' => [qw/alpha amd64 arm64 armv7 hppa i386 landisk loongson luna88k macppc octeon powerpc64 riscv64 sparc64/] }, 
'OpenBSD 7.1' => { 'arch' => [qw/alpha amd64 arm64 armv7 hppa i386 landisk loongson luna88k macppc octeon powerpc64 riscv64 sparc64/] }, 
'OpenBSD 7.2' => { 'arch' => [qw/alpha amd64 arm64 armv7 hppa i386 landisk loongson luna88k macppc octeon powerpc64 riscv64 sparc64/] }, 
'OpenBSD 7.3' => { 'arch' => [qw/alpha amd64 arm64 armv7 hppa i386 landisk loongson luna88k macppc octeon powerpc64 riscv64 sparc64/] }, 
'OpenBSD 7.4' => { 'arch' => [qw/alpha amd64 arm64 armv7 hppa i386 landisk loongson luna88k macppc octeon powerpc64 riscv64 sparc64/] }, 
'OpenBSD 7.5' => { 'arch' => [qw/alpha amd64 arm64 armv7 hppa i386 landisk loongson luna88k macppc octeon powerpc64 riscv64 sparc64/] }, 
'OpenBSD 7.6' => { 'arch' => [qw/alpha amd64 arm64 armv7 hppa i386 landisk loongson luna88k macppc octeon powerpc64 riscv64 sparc64/] }, 
'OpenBSD 7.7' => { 'arch' => [qw/alpha amd64 arm64 armv7 hppa i386 landisk loongson luna88k macppc octeon powerpc64 riscv64 sparc64/] }, 
);

# delete not existing releases
while ( ( $key, $val ) = each %manPath ) {
    my $counter = 0;

    # if the manpath contains colons, at least one directory must exists
    foreach ( split( /:/, $val ) ) {
        $counter++ if -d;
    }

    # give up and delete release
    if ( !$counter && $key ne $manPathDefault ) {
        delete $manPath{"$key"};
        warn qq{man.cgi Remove release "$key"\n} if $debug >= 2;
    }
}

# keywords must be in lower cases.
%manPathAliases = (
    'freebsd',         'FreeBSD 14.3-RELEASE',
    'freebsd-release', 'FreeBSD 14.3-RELEASE',

    'freebsd-stable',   'FreeBSD 14.3-STABLE',
    'freebsd-stable14', 'FreeBSD 14.3-STABLE',
    'freebsd-stable13', 'FreeBSD 13.5-STABLE',

    'freebsd-current',       'FreeBSD 15.0-CURRENT',
    'freebsd-release-ports', 'FreeBSD 14.3-RELEASE and Ports',
    'freebsd-ports', 'FreeBSD Ports 14.3.quarterly',

    'slackware',  'Linux Slackware 3.1',
    'redhat',     'Red Hat 9',
    'suse',       'SuSE 11.3',
    'debian',     'Debian 12.11.0',
    'ubuntu',     'Ubuntu 24.04 noble',
    'dragonfly',  'DragonFly 6.4.0',
    'centos',     'CentOS 7.9',
    'rocky',      'Rocky 10.0',
    'linux',      'Debian 12.11.0',
    'darwin',     'Darwin 8.0.1/ppc',
    'opendarwin', 'OpenDarwin 7.2.1',
    'macosx',     'Darwin 8.0.1/ppc',

    'netbsd',        'NetBSD 10.1',
    'openbsd',       'OpenBSD 7.7',
    'opensuse',      'openSUSE 15.6',
    'openindiana',   'OpenIndiana 2024.10',
    'v7',            'Unix Seventh Edition',
    'v7man',         'Unix Seventh Edition',
    'x11',           'X11R7.4',
    'xfree86',       'XFree86 4.8.0',
    'ultrix',        'ULTRIX 4.2',
    'hpux',          'HP-UX 11.22',
    'irix',          'IRIX 6.5.30',
    'solaris',       'SunOS 5.10',
    'sunos5',        'SunOS 5.10',
    'sunos4',        'SunOS 4.1.3',
    'sunos',         'SunOS 4.1.3',
    'macos',         'macOS 15.5.0',
    'plan9',         'Plan 9',
    'osf1',          'OSF1 V5.1/alpha',
    'true64',        'OSF1 V5.1/alpha',
    'minix',         'Minix 3.3.0',
);

# pre-build a hash to get relevant information for sorting
my $sort_manpath_hash;
sub sort_manpath {
    my $manpath = shift;
    my @list = keys %$manpath;

    $sort_manpath_hash = {};
    foreach my $name (@list) {
        my $name_lc = lc($name);
        my $os_lc;

        # a release has at least 2 numbers seperated by a dot:
        # FreeBSD 11.1-RELEASE ports
        # X11R7.4
        my ($os, $version, $ports) = ( $name =~ m,^(.*?)(\d+\.[\d\.]+)(.*)$, );
        $os //= $name;
        $os_lc = lc($os);
        $version //= "0.0";
        $ports //= "";

        $sort_manpath_hash->{$name} = { 'os' => $os, 'os_lc' => $os_lc, 'version' => $version, 'ports' => $ports };
    } 

    return sort { &sort_versions } keys %$manpath;
}

#
# sort by OS release number, highest version first
#
# e.g.:
#
# XFree86 4.0
# XFree86 3.3.6
# XFree86 3.3
# XFree86 2.1
# ...
# XFree86 11
# XFree86 10.0.1
# XFree86 10.0
#
sub sort_versions {
   my $h = $sort_manpath_hash;
  
   return 
     $h->{$a}->{'os_lc'} cmp $h->{$b}->{'os_lc'} ||            # freebsd <=> irix
     $h->{$a}->{'os'} cmp $h->{$b}->{'os'} ||                  # FreeBSD <=> freebsd
     &version($h->{$a}->{'version'}, $h->{$b}->{'version'}) || # 6.5.30 <=> 6.5.31  
     $h->{$a}->{'ports'} cmp $h->{$b}->{'ports'} ||            # RELEASE <=> ports (release first)
     $a cmp $b;                                                # for the rest: basic string compare
}

# reverse order, newest release first
sub version {
    return &version_compare(@_) * -1;
}

# compare two versions, e.g.: 5.1.1 <> 5.2.2
sub version_compare {
    my $a = shift;
    my $b = shift;

    my @a = split( '\.', $a );
    my @b = split( '\.', $b );

    my $max = @a >= @b ? @a : @b;

    for ( my $i = 0 ; $i < $max ; $i++ ) {

        # 5.1 <=> 5.1.1
        return -1 if !defined $a[$i];

        # 5.1.1 <=> 5.1
        return +1 if !defined $b[$i];

        if ( ( $a[$i] <=> $b[$i] ) != 0 ) {
            return $a[$i] <=> $b[$i];
        }
    }

    return 0;
}

# FreeBSD manual pages first before any other manual pages
sub freebsd_first {
    my @list = @_;
    my @data;
    push @data, grep { /^FreeBSD/ } @list;
    push @data, grep { !/^FreeBSD/ } @list;

    return @data;
}

foreach ( &sort_manpath(\%manPathAliases) ) {

    # delete non-existing aliases
    if ( !defined( $manPath{ $manPathAliases{$_} } ) ) {
        undef $manPathAliases{$_};
        next;
    }

    # add aliases, replases spaces with dashes
    if (/\s/) {
        local ($key) = $_;
        $key =~ s/\s+/-/g;
        $manPathAliases{$key} = $manPathAliases{$_};
    }
}

@sections = keys %sections;
shift @sections;    # all but the "" entry
$sections = join( "|", @sections );    # sections regexp

# mailto - Author
# webmaster - who run this service
$mailto                    = 'wosch@FreeBSD.org';
$mailtoURL                 = 'https://wolfram.schneider.org';
$mailtoURL                 = "mailto:$mailto" if !$mailtoURL;
$full_url                  = 'https://man.freebsd.org/cgi/man.cgi';
$want_to_link_to_this_page = 1;

&secure_env;

# CGI Interface -- runs at load time
&do_man( &env('SCRIPT_NAME'), &env('PATH_INFO'), &env('QUERY_STRING') )
  unless defined($main::plexus_configured);

#
# end of config
#######################################################################################

sub html_footer {
    my %args = @_;

    print qq[<span class="footer_links">\n];
    print qq[  <a href="$www{'cgi_man'}">home</a>\n] if !$args{'no_home_link'};
    print qq[| <a href="$www{'cgi_man'}/help.html">help</a>\n] if !$args{'no_help_link'};
    print qq[</span>\n\n];

    if (cgi_style::HAS_FREEBSD_CGI_STYLE) {
        print q{<hr noshade="noshade" />};
        print &cgi_style::html_footer;
    }
    else {
        print "</body>\n</html>\n";
    }
}

sub html_header {
    my ( $title, $base ) = @_;

    my $html_meta = q|
<meta name="robots" content="nofollow" />
<meta content="text/html; charset=iso-8859-1" http-equiv="Content-Type" />
<link rel="search" type="application/opensearchdescription+xml" href="https://www.freebsd.org/opensearch/man.xml" title="FreeBSD Man" />
<link rel="search" type="application/opensearchdescription+xml" href="https://www.freebsd.org/opensearch/man-freebsd-release-ports.xml" title="FreeBSD Man+P" />

<style type="text/css">
span.footer_links { font-size: small; }
span.space { font-size: xx-small; }
form#man > input, form#man > button { font-size: large; }
form#man > input[name='query'] { text-align: center; }
p#section_links, div#footer { max-width: 50em; }
hr { margin-left: 0em; max-width: 50em; }

@media only screen and (max-height: 640px), (max-width: 760px) {
  /* hide logo color top */
  body { background: #fff !important; } 

  /* hide menu top */
  div#header, div#menu { display: none !important; }
  // div#content { padding-top: 4.9em; }
  span.spaces { display: none; }

  /* larger search form */
  form#man > input, button { font-size: 200%; }
  form#man > button { font-size: 200%; }
  form#man > input[name='query'] { width: 12em; }
  form#man > select { font-size: 140%; }
}
</style>
|;

    return &html_header2( $title, $html_meta )
      if !cgi_style::HAS_FREEBSD_CGI_STYLE;

    ( my $header = &cgi_style::short_html_header( $title, 1 ) ) =~
      s,<head>,<head>\n$html_meta,s;

    $header =~ s,^Content-type:\s+\S+\s+,,s;
    $header =~ s,<head>,<head>\n<base href="$base" />,s if $base;
    return $header;
}

# Plexus Native Interface
sub do_man {
    local ( $BASE, $path, $form ) = @_;
    local ( $_, %form, $query, $name, $section, $apropos );

    local ($u) = $BASE;

    return &faq_output($u)  if ( $path =~ /\/(faq|help)\.html$/ );
    return &get_the_sources if ( $path =~ /source$/ );

    return &indexpage if ( $form eq "" );

    &decode_form( $form, *form, 0 );

    $format = $form{'format'};
    $format = 'html' if $format !~ /^(ps|pdf|ascii|latin1)$/;

    $arch = $form{'arch'} || "";
    $arch = '' if $arch eq 'none' || $arch eq 'default';
    if ( $arch =~ /^([a-zA-Z0-9]+)$/ && $valid_arch{$arch} ) {
        $arch = $1;
    }
    elsif ($arch) {
        warn "Unknown arch: '$arch', ignored\n";
        $arch = "";
    }
    else {
        $arch = "";
    }

    # remove trailing spaces for dumb users
    $form{'query'} =~ s/\s+$//;
    $form{'query'} =~ s/^\s+//;

    # not supported query characters
    $form{'query'} =~ s/"//g;
    $form{'query'} =~ s/=//g;

    # Firefox opensearch autocomplete workaround
    if ($form{'sourceid'} eq 'opensearch') {
        # remove space between double colon
        $form{'query'} =~ s/: :/::/g;
        # remove space before a dot 
        $form{'query'} =~ s/ \./\./g;
    }

    $name = $query = $form{'query'};
    $section  = $form{'sektion'};
    $apropos  = $form{'apropos'};
    $alttitle = $form{'title'};
    $manpath  = $form{'manpath'};

    if ( $manpath =~ /^([0-9A-Za-z \.\-\/]+)$/ ) {
        $manpath = $1;
    }
    else {
        $manpath = '';
    }

    if ( !$manpath ) {
        $manpath = $manPathDefault;
    }
    elsif ( !$manPath{$manpath} ) {
        local ($m) = ( $manpath =~ y/A-Z/a-z/ );
        if ( $manPath{ $manPathAliases{$manpath} } ) {
            $manpath = $manPathAliases{$manpath};
        }
        else {
            $manpath = $manPathDefault;
        }
    }

    $format = 'html' if $no_pdf_output{$manpath} && $format =~ /^(ps|pdf)$/;

    local ($fform) = &dec($form);
    if ( $fform =~ m%^([a-zA-Z_\-\.:]+)$% ) {
        return &man( $1, '' );
    }
    elsif ( $fform =~ m%^([a-zA-Z_\-\.:]+)\(([0-9a-zA-Z]+)\)$% ) {
        return &man( $1, $2 );
    }

    # download a man hierarchy as gzip'd tar file
    return &download if ( $apropos > 1 );

    # empty query
    return &indexpage if ( $manpath && $form !~ /query=/ );

    $section = "" if $section eq "ALL" || $section eq '';

    if ( !$apropos && $query =~ m/^(.*)\(([^\)]*)\)/ ) {
        $name    = $1;
        $section = $2;
    }
    if ( $name =~ /^([\w\-:\.\+]+)$/ ) {
        $name = $1;
    }
    else { $name = ''; }

    if ( $section =~ /^([\w\-\.]+)$/ ) {
        $section = $1;
    }
    else { $section = ''; }

    $apropos ? &apropos($query, $section) : &man( $name, $section, $arch );
}

# --------------------- support routines ------------------------

sub debug {
    &http_header("text/plain");
    print @_, "\n----------\n\n\n";
}

sub get_the_sources {
    local ($file) = $0;

    open( R, $file ) || &mydie("open $file: $!\n");
    print "Content-type: text/plain\n\n";
    while (<R>) { print }
    close R;
    exit;
}

# download a manual directory as gzip'd tar archive
sub download {

    if (!$enable_download) {
    # 2019-05-31: allanjude: Disable downloading as it is being abused.
    print qq{Status: 418 No Downloads For You\n\n};
    exit(0);
    }

    $| = 1;
    my $filename = $manpath;
    $filename =~ s/\s+/_/;
    $filename = &encode_url($filename);
    $filename .= '.tgz';

    # bypass caching proxies which cannot handle streaming of large data very well
    print qq{Cache-Control: no-cache, no-store, private, max-age=0\n} if $download_streaming_caching == 0;

    print qq{Content-type: application/x-tgz\n}
      . qq{Content-disposition: attachment; filename="$filename"\n} . "\n";

    local (@m);
    local ($m) = $manPath{"$manpath"};
    foreach ( split( /:/, $m ) ) {
        push( @m, $_ . '/' ) if s%^$manLocalDir/?%%;
    }

    chdir($manLocalDir) || do {
        print "chdir: $!\n";
        exit(0);
    };

    $m = join( " ", @m );

    sleep 1;
    system("find $m -print | cpio -o --format ustar 2>/dev/null | gzip -cqf");
    exit(0);
}

sub http_header {
    local ( $content_type, $filename ) = @_;

    print qq{Content-disposition: inline; filename="$filename"\n}
      if $filename;

    if ( defined($main::plexus_configured) ) {
        &main::MIME_header( 'ok', $content_type );
    }
    else {
        print "Content-type: $content_type\n\n";
    }
}

sub env { defined( $main::ENV{ $_[0] } ) ? $main::ENV{ $_[0] } : undef; }

sub apropos {
    local ($query, $sektion) = @_;
    local ( $_,     $title,   $head, *APROPOS );
    local ( $names, $section, $msg,  $key );
    local ($prefix);

    $prefix = "Apropos ";
    if ($alttitle) {
        $prefix = "";
        $title  = &encode_title($alttitle);
        $head   = &encode_data($alttitle);
    }
    else {
        $title = &encode_title($query);
        $head  = &encode_data($query);
    }

    &http_header("text/html");
    print &html_header("Apropos $title");
    print "<br/>\n<h1>$www{'head'}</h1>\n\n";

    $section = $sektion;
    &formquery;

    local ($mpath) = $manPath{$manpath};
    if ( $debug >= 2 ) {
        foreach my $dir ( split( /:/, $mpath ) ) {
            my $whatis = $dir . '/whatis';
            warn "$manpath: no whatis file found: $whatis\n" if !-f $whatis;
        }
    }

    open( APROPOS, "env MANPATH=$mpath $command{'man'} -k . |" ) || do {
        warn "$0: Cannot open whatis database for `$mpath'\n";
        print "Cannot open whatis database for `$mpath'\n";
        print "</dl>\n</body>\n</html>\n";
        return;
    };

    local ($q) = $query;
    $q =~ s/(\W)/\\W/g;
    local ($acounter) = 0;

    print qq{<dl>\n};
    while (<APROPOS>) {
        next if !/$q/oi;
        next if $sektion && !/\($sektion\)/oi;

        $acounter++;

        # matches whatis.db lines: name[, name ...] (sect) - msg
        $names = $section = $msg = $key = undef;
        ( $key, $section ) = m/^([^()]+)\(([^)]*)\)/;
        $key =~ s/\s+$//;
        $key =~ s/.*\s+//;
        ( $names, $msg ) = m/^(.*\))\s+-\s+(.*)/;
        print "<dt><a href=\"$BASE?query=", &encode_url($key), "&amp;sektion=",
          &encode_url($section), "&amp;apropos=0", "&amp;manpath=",
          &encode_url($manpath), "\">",            &encode_data("$names"),
          "</a>\n</dt>\n<dd>", &encode_data($msg), "</dd>\n";
    }
    print qq{</dl>\n};
    close(APROPOS);

    if ( !$acounter ) {
        print "Sorry, no data found for `$query'.\n";
        print qq{You may look for other }
          . qq{<a href="https://www.freebsd.org/search/">FreeBSD Search Services</a>.<br/><br/>\n};
    }
    &html_footer;
}

sub to_filename {
    my %args = @_;

    my $name = exists $args{'name'} ? $args{'name'} : 'manpage';
    my $section = exists $args{'section'}
      && $args{'section'} ne "" ? $args{'section'} : '0';
    my $format = exists $args{'format'} ? $args{'format'} : 'unkown';

    my $filename = qq{$name.$section.$format};
    $filename =~ s/[^\w\-\.]/_/g;
    $filename =~ s/_+/_/g;

    return $filename;
}

# strip ports manual pages from path
sub manpath_without_ports {
    my $path = shift;

    my @list;
    foreach my $p (split(/:/, $path)) {
	push @list, $p if $p !~ /-ports-/;
    }

    return join(":", @list);
}

# strip trailing dots, comma etc. from an URL
sub url_strip {
    my $url = shift;
    my $part = shift;

    if ($url =~ m/(.+)([,\.])$/) {
       return ($1, $1, $2);
    } else {
       return ($url, $url, "");
    }
}

sub man {
    local ( $name, $section, $arch ) = @_;
    local ( $_, $title, $head, *MAN );
    local ( $html_name, $html_section, $prefix );
    local (@manargs);
    local ($query) = $name;

    # $section =~ s/^([0-9ln]).*$/$1/;
    $section =~ tr/A-Z/a-z/;

    $prefix = "Man ";
    if ($alttitle) {
        $prefix = "";
        $title  = &encode_title($alttitle);
        $head   = &encode_data($alttitle);
    }
    elsif ($section) {
        $title = &encode_title("${name}($section)");
        $head  = &encode_data("${name}($section)");
    }
    else {
        $title = &encode_title("${name}");
        $head  = &encode_data("${name}");
    }

    if ( $format eq "html" ) {
        &http_header("text/html");
        print &html_header("$title");
        print "<br/>\n<h1>$www{'head'}</h1>\n\n";
        &formquery;
        print "<pre>\n";
    }
    else {

        #$format =~ /^(ps|ascii|latin1)$/')
        $ENV{'NROFF_FORMAT'} = $format;

        # Content-encoding: x-gzip
        if ( $format eq "ps" ) {
            &http_header(
                "application/postscript",
                &to_filename(
                    'name'    => $name,
                    'section' => $section,
                    'format'  => 'ps'
                )
            );
        }
        elsif ( $format eq "pdf" ) {
            &http_header(
                "application/pdf",
                &to_filename(
                    'name'    => $name,
                    'section' => $section,
                    'format'  => 'pdf'
                )
            );
        }
        else {
            &http_header("text/plain");
        }
    }

    $html_name    = &encode_data($name);
    $html_section = &encode_data($section);

    if ( $name =~ /^\s*$/ ) {
	print "</pre><hr/>";
        print "Empty input. Please type a manual page and search again.\n";
	print "<hr/>\n";
        &html_footer;
        return;
    }

    if ( index( $name, '*' ) != -1 ) {
        print "Invalid character input '*': $name\n";
        return;
    }

    if ( $section !~ /^[0-9ln]\w*$/ && $section ne '' ) {
        print "Sorry, section `$section' is not valid\n";
        return;
    }

    if ( !$section ) {
        if ( $sectionpath->{$manpath} ) {
            $section = "-S " . $sectionpath->{$manpath}{'path'};
        }
        else {
            $section = '';
        }
    }
    else {
        if ( $sectionpath->{$manpath}{$section} ) {
            $section = "-S " . $sectionpath->{$manpath}{$section};
        }
        else {
            my $s = substr( $section, 0, 1 );

            # create a colon separated list of sections
            $section = "-S $section" . ( $s ne $section ? ":$s" : '' );
        }
    }

    @manargs = split( / /, $section );
    my $manpath_m = "";

    if ($manpath) {
        if ( $manPath{$manpath} ) {
            $manpath_m = $manPath{$manpath};
            &groff_path( $manPath{$manpath} );
        }
        elsif ( $manpath{ &dec($manpath) } ) {
            $manpath_m = $manPath{ &dec($manpath) };
            &groff_path( $manPath{ &dec($manpath) } );
        }
        else {

            # unset invalid manpath
            print "x $manpath x\n";
            print "x " . &dec($manpath) . "x\n";
            undef $manpath;
        }
    }

    if ( $format =~ /^(ps|pdf)$/ ) {
        push( @manargs, '-t' );
    }


    push( @manargs, ( "-m", $arch ) ) if $arch;

    # search first for base manual pages, and maybe later in ports
    if ($freebsd_base_manpages_first && $section eq "" && $manpath =~ m/ and Ports$/) {
        warn "search for base pages first: $name\n" if $debug >= 2;
	my @m = ("-M", &manpath_without_ports($manpath_m));
        warn "X $command{'man'} @m @manargs -- x $name x\n" if $debug >= 3;
        &proc( *MAN, $command{'man'}, @m,  @manargs, "--", $name )
      	    || &mydie("$0: open of $command{'man'} command failed: $!\n");

        if ( eof(MAN) ) {
            warn "search for ports pages as well: $name\n" if $debug >= 2;
	    @m = ("-M", $manpath_m);
            warn "X $command{'man'} @m @manargs -- x $name x\n" if $debug >= 3;
            &proc( *MAN, $command{'man'}, @m, @manargs, "--", $name )
      	    	|| &mydie("$0: open of $command{'man'} command failed: $!\n");
	}
    } else {
        my @m = $manpath_m ? ("-M", $manpath_m) : ();
        warn "X $command{'man'} @m @manargs -- x $name x\n" if $debug >= 3;
    	&proc( *MAN, $command{'man'}, @m, @manargs, "--", $name )
      	    || &mydie("$0: open of $command{'man'} command failed: $!\n");
    }

    if ( eof(MAN) ) {
        if ( $format eq "ascii" ) {
            print "Sorry, no data found for '$html_name'\n";
	    return;
        }

        # print "X $command{'man'} @manargs -- x $name x\n";
        print qq{</pre>\n};
        print "Sorry, no data found for `<i>$html_name</i>"
          . ( $html_section ? "($html_section)" : '' ) . "'.\n";
        print
qq{Please try a <a href="$BASE?apropos=1&amp;manpath=freebsd-release-ports&amp;query=$html_name">keyword search</a>.\n};
        print qq{<p>You may look for other }
          . qq{<a href="https://www.freebsd.org/search/">FreeBSD Search Services</a>.</p>\n};
        &html_footer;
        return;
    }

    if ( $format ne "html" ) {
        if ( $format eq "latin1" || $format eq "ascii" ) {
            while (<MAN>) { s/.//g; print; }
        }
        elsif ( $format eq "pdf" ) {

            #
            # run a PostScript to PDF converter
            #
            local (@args) = ( 'mktemp', '/tmp/_man.cgi-ps2pdf-XXXXXXXXXXXX' );
            open( TMP, "-|" )
              or exec(@args)
              or die "open @args: $!\n";
            local ($tempfile) = <TMP>;
            close TMP;

            # chomp, avoid security warnings using -T switch
            #chop($tempfile);
            if ( $tempfile =~ /(\S+)/ ) {
                $tempfile = $1;
            }

            if ( !$tempfile || !-f $tempfile ) {
                die "Cannot create tempfile: $tempfile\n";
            }

            #warn $tempfile;

            #$tempfile = '/tmp/bla2';
            open( TMP, "> $tempfile" ) or die "open $tempfile: $!\n";
            while (<MAN>) {
                print TMP $_;
            }
            close TMP;
            local ( $ENV{'PATH'} ) = '/bin:/usr/bin:/usr/local/bin';
            open( PDF, "-|" )
              or exec( '/usr/local/bin/ps2pdf', $tempfile, '/dev/stdout' )
              or die "open ps2pdf: $!\n";

            # sleep and delete the temp file
            #select(undef, undef, undef, 0.8);
            #unlink($tempfile);

            while (<PDF>) {
                print;
            }
            close PDF;
            unlink($tempfile);

        }
        else {
            while (<MAN>) { print; }
        }
        close(MAN);
        exit(0);
    }

    local ($space) = 1;
    local (@sect);
    local ( $i, $j );
    while (<MAN>) {

        # remove tailing white space
        if (/^\s+$/) {
            next if $space;
            $space = 1;
        }
        else {
            $space = 0;
        }

        $_ = &encode_data($_);

	# detect references to other manual pages and set link
	if (/^\s/) {  # skip man headers / first line
	    s,((<[IB]>)?[\w\_\.\-]+(</[IB]>)?\(([1-9ln][a-zA-Z]*)\)),&mlnk($1),oige;
        }

        # detect URLs in manpages
        if (m,\b(http|https)://,) {
            s|(https?://[^\s\)&<>'`";\]\[]+)|sprintf("<a href=\"%s\">%s</a>%s", &url_strip($1))|egi;
        }

        if (s%^(<b>.*?</b>)+\n?$% ($str = $1) =~ s,(<b>|</b>),,g; $str%ge) {
            $i = $_;
            $j = &encode_url($i);
            $j =~ s/\+/_/g;
            $_ = qq{<a name="$j" href="#end"><b>$i</b></a>\n};
            push( @sect, $i );
        }
        print;
    }
    close(MAN);
    print qq{</pre>\n<a name="end" />\n<hr />\n};

    print qq{\n<p id="section_links">\n};
    for ( $i = 0 ; $i <= $#sect ; $i++ ) {
        $j = &encode_url( $sect[$i] );
        $j =~ s/\+/_/g;

        print qq{<a href="#$j}
          . qq{">$sect[$i]</a>}
          . ( $i < $#sect ? " |\n" : "\n" );
    }
    print qq{</p>\n\n};

    if ($want_to_link_to_this_page) {
        my $url = qq{$full_url?query=$html_name};
        $url .= qq{&amp;sektion=$html_section} if $html_section != 0;
        $url .= qq{&amp;manpath=} . &encode_url($manpath);

        print qq{<p align="left">Want to link to this manual page? };
        print qq{Use this URL:<br/>&lt;<a href="$url">$url</a>&gt;</p>\n};
    }

    &html_footer;

    # Sleep 0.35 seconds to avoid DoS attacs
    select undef, undef, undef, 0.35;
}

#
# You may need to precreate some mdoc.local files for every system you
# support (every collection of man pages), maybe like:
#
# $manLocalDir/NetBSD-1.4.2/tmac
#
# and then in your cgi script itself set the GROFF_TMAC_PATH as appropriate
# like:
#
# GROFF_TMAC_PATH=$manLocalDir/NetBSD-1.4.2/tmac:/usr/share/tmac/
#
sub groff_path {
    local $manpath = shift;

    local @groff_path;
    foreach ( split( /:/, $manpath ) ) {
        push( @groff_path, $_ . '/tmac' );
    }

    $ENV{'GROFF_TMAC_PATH'} = join( ':', @groff_path, '/usr/share/tmac' );
}

sub mlnk {
    local ($matched) = @_;
    local ( $link, $section );
    ( $link = $matched ) =~ s/[\s]+//g;
    $link =~ s/<\/?[IB]>//ig;
    ( $link, $section ) = ( $link =~ m/^([^\(]*)\((.*)\)/ );
    $link    = &encode_url($link);
    $section = &encode_url($section);
    local ($manpath) = &encode_url($manpath);
    return qq{<a href="$BASE?query=$link}
      . qq{&amp;sektion=$section&amp;apropos=0&amp;manpath=$manpath">$matched</a>};
}

sub proc {
    local ( *FH, $prog, @args ) = @_;
    local ($pid) = open( FH, "-|" );
    return undef unless defined($pid);
    if ( $pid == 0 ) {
        exec( $prog, @args )
          or &mydie("exec $prog failed\n");
    }
    1;
}

# $indent is a bit of optional data processing I put in for
# formatting the data nicely when you are emailing it.
# This is derived from code by Denis Howe <dbh@doc.ic.ac.uk>
# and Thomas A Fine <fine@cis.ohio-state.edu>
sub decode_form {
    local ( $form, *data, $indent, $key, $_ ) = @_;
    foreach $_ ( split( /&/, $form ) ) {
        ( $key, $_ ) = split( /=/, $_, 2 );
        $_   =~ s/\+/ /g;                                 # + -> space
        $key =~ s/\+/ /g;                                 # + -> space
        $_   =~ s/%([\da-f]{1,2})/pack(C,hex($1))/eig;    # undo % escapes
        $key =~ s/%([\da-f]{1,2})/pack(C,hex($1))/eig;    # undo % escapes
        $_   =~ s/[\r\n]+/\n\t/g if defined($indent);     # indent data after \n
        $data{$key} = &escape($_);
    }
}

# block cross-site scripting attacks (css)
sub escape($) { $_ = $_[0]; s/&/&amp;/g; s/</&lt;/g; s/>/&gt;/g; $_; }

sub dec {
    local ($_) = @_;

    s/\+/ /g;                                             # '+'   -> space
    s/%(..)/pack("c",hex($1))/ge;                         # '%ab' -> char ab

    return ($_);
}

#
# Splits up a query request, returns an array of items.
# usage: @items = &main::splitquery($query);
#
sub splitquery {
    local ($query) = @_;
    grep( ( s/%([\da-f]{1,2})/pack(C,hex($1))/eig, 1 ), split( /\+/, $query ) );
}

# encode unknown data for use in a URL <a href="...">
sub encode_url {
    local ($_) = @_;

    # rfc1738 says that ";"|"/"|"?"|":"|"@"|"&"|"=" may be reserved.
    # And % is the escape character so we escape it along with
    # single-quote('), double-quote("), grave accent(`), less than(<),
    # greater than(>), and non-US-ASCII characters (binary data),
    # and white space.  Whew.
s/([\000-\032\;\/\?\:\@\&\=\%\'\"\`\<\>\177-\377 ])/sprintf('%%%02x',ord($1))/eg;
    s/\+/%2B/g;
    s/%20/+/g;
    $_;
}

# encode unknown data for use in <TITLE>...</TITILE>
sub encode_title {

    # like encode_url but less strict (I couldn't find docs on this)
    local ($_) = @_;
    s/([\000-\031\%\&\<\>\177-\377])/sprintf('%%%02x',ord($1))/eg;
    $_;
}

# encode unknown data for use inside markup attributes <MARKUP ATTR="...">
sub encode_attribute {

    # rfc1738 says to use entity references here
    local ($_) = @_;
    s/([\000-\031\"\'\`\%\&\<\>\177-\377])/sprintf('\&#%03d;',ord($1))/eg;
    $_;
}

sub escape_word {
    my $word = shift;

    return join( '', map { escape_char($_) } @$word );
}

sub escape_char {
    my $c = shift;

    return
        $c eq '&'             ? "&amp;"
      : $c eq '<'             ? "&lt;"
      : $c eq '>'             ? "&gt;"
      : $c eq '_BULLET_ITEM_' ? "&bull;"
      :                         $c;
}

sub tag_ib {
    my $tag  = shift;
    my $word = shift;

    my $data = escape_word($word);

    return
        $tag eq 'ib' ? "<i><b>$data</b></i>"
      : $tag eq 'b'  ? "<b>$data</b>"
      : $tag eq 'i'  ? "<i>$data</i>"
      :                $data;
}

# encode unknown text data for using as HTML,
# treats ^H as overstrike ala nroff.
sub encode_data {
    my $line = shift;

    # optimize for speed: most lines have no special characters
    if ($line !~ /[<>&\010]/) {
      return $line;
    }

    # work on a list of characters
    my @l = split( '', $line );

    my $data = "";
    my $flag = "";
    my @word = ();

    my $end_of_word = sub {
        my $new_flag = shift;

        return if !scalar(@word);

        # a tag ended, and a new started immediately
        if ( $flag ne "" && $new_flag ne $flag ) {
            $data .= tag_ib( $flag, \@word );
            @word = ();
        }
    };

    for ( my $i = 0 ; $i <= $#l ; $i++ ) {

        # 7 characters: +^H+^Ho^Ho - bullet list
        if (   $i <= ( $#l - 6 )
            && $l[$i] eq "+"
            && $l[ $i + 1 ] eq "\010"
            && $l[ $i + 2 ] eq "+"
            && $l[ $i + 3 ] eq "\010"
            && $l[ $i + 4 ] eq "o"
            && $l[ $i + 5 ] eq "\010"
            && $l[ $i + 6 ] eq "o" )
        {
            push @word, '_BULLET_ITEM_';
            $i += 6;
            $flag = 'b';
        }

        # 2 characters: +^Ho - bullet list
        elsif (   $i <= ( $#l - 2 )
            && $l[$i] eq "+"
            && $l[ $i + 1 ] eq "\010"
            && $l[ $i + 2 ] eq "o" )
        {
            push @word, '_BULLET_ITEM_';
            $i += 2;
            $flag = 'b';
        }

        # 5 characters: _\010x\010x - bold and italic
        elsif ($i <= ( $#l - 4 )
            && $l[ $i + 1 ] eq "\010"
            && $l[ $i + 3 ] eq "\010"
            && $l[ $i + 2 ] eq $l[ $i + 4 ] )
        {
            $end_of_word->('ib');
            push @word, $l[ $i + 2 ];
            $i += 4;
            $flag = 'ib';
        }

        # 3 characters: _\010 - bold or italic
        elsif ( $i <= ( $#l - 2 ) && $l[ $i + 1 ] eq "\010" ) {

            # bold
            # take care of links with underlines, which are alwasy italic
            if ( $l[$i] eq $l[ $i + 2 ] && $flag ne 'i' ) {
                $end_of_word->('b');
                push @word, $l[$i];
                $i += 2;
                $flag = 'b';
            }

            # italic
            elsif ( $l[$i] eq "_" && $i + 2 <= $#l ) {
                $end_of_word->('i');
                push @word, $l[ $i + 2 ];
                $i += 2;
                $flag = 'i';
            }
        }

        # other, one or two characters
        else {
            # italic/bold ends here
            $end_of_word->('ANY');

            # simple backslash
            if ( $l[$i] eq "\010" ) {

                # just ignore
            }
            elsif ( $i <= ( $#l - 1 ) && $l[ $i + 1 ] eq "\010" ) {
                $i++;
            }
            else {
                $data .= escape_char( $l[$i] );
            }
            $flag = "";
        }
    }

    # last character
    $end_of_word->('ANY');

    return $data;
}

sub indexpage {
    &http_header("text/html");
    print &html_header("$www{'title'}");
    print "<br/>\n<h1>$www{'head'}</h1>\n\n"; 

    # print &intro;
    &formquery;

    local ($m) = ( $manpath ? $manpath : $manPathDefault );
    $m = &encode_url($m);

    &html_footer( 'no_home_link' => 1, 'no_help_link' => 1 );
}

sub formquery {
    local ( $astring, $bstring );
    if ( !$apropos ) {
        $astring = q{ checked="checked"};
    }
    else {
        $bstring = q{ checked="checked"};
    }

    # set focus if the input field is empty 
    my $autofocus = $query ? "" : "autofocus";

    print <<ETX;
<form id="man" method="get" action="$BASE">
<!-- Manual Page or Keyword Search: -->
<span class="spaces">&nbsp;&nbsp;</span>
<input type="text" id="query" value="$query" name="query" size="36" autocapitalize="none" $autofocus />
<button type="submit" name="apropos" value="0">man</button>
<button type="submit" name="apropos" value="1">apropos</button>
<br/>
<span class="space">&nbsp;</span><br/>
<span class="spaces">&nbsp;&nbsp;</span>
ETX

    print qq{<select name="sektion">\n};
    foreach $key ( sort keys %sectionName ) {
        print "<option"
          . ( ( $key eq $section ) ? ' selected="selected" ' : ' ' )
          . qq{value="$key">$sectionName{$key}</option>\n};
    }

    print qq{</select>\n<select name="manpath">\n};

    local ($l) = ( $manpath ? $manpath : $manPathDefault );
    foreach ( &freebsd_first( &sort_manpath(\%manPath)) ) {
        $key = $_;
        print "<option"
          . ( ( $key eq $l ) ? ' selected="selected" ' : ' ' )
          . qq{value="$key">$key</option>\n};
    }

    print qq{</select>\n};

    print qq{<select name="arch">\n};
    my @arch = exists $arch{$l} ? @{ $arch{$l}->{'arch'} } : $default_arch;
    unshift @arch, 'default';

    my $a;
    # machine type selected by user
    if ($arch) { 
    	$a = $arch;
    } 

    # pickup a default machine type
    else {
        #exists $arch{$l}->{'default'} ? $arch{$l}->{'default'} : 'default';
    }

    foreach (@arch) {
	next if $_ eq "";

        my $selected = $_ eq $a ? ' selected="selected"' : "";
        my $arch_name = exists $arch_names{$_} ? $arch_names{$_} : $_;
        print qq{<option $selected value="$_">$arch_name</option>\n};
    }

    print qq{</select>\n\n};

    local ($m) = &encode_url($l);

    print <<ETX;
<select name="format">
ETX

    my @format = ();
    push( @format, ( 'html' ) ) if !$no_html_output{$manpath};
    push( @format, ( 'pdf' ) ) if !$no_pdf_output{$manpath};
    push( @format, ( 'ascii' ) );

    foreach (@format) {
        print qq{<option value="$_">$_</option>\n};
    }

    print <<ETX;
</select>
</form>

<br/>
<span class="footer_links">
  <a href="$www{'cgi_man'}">home</a> |
  <a href="$www{'cgi_man'}/help.html">help</a>
</span>
ETX
    if ($query) {
	print "<hr/>\n";
    }
}

sub faq {

    local ( @list, @list2 );
    local ($url);
    foreach ( &freebsd_first (&sort_manpath(\%manPath) )) {
        $url = &encode_url($_);
        my $download_link = $enable_download ? qq[<a href="/cgi/man.cgi?apropos=2&amp;manpath=$url">tarball</a>] : '';
        push( @list, qq{<li>$_: <a href="$BASE?manpath=$url">permalink</a> | $download_link</li>\n} );
    }

    foreach ( &freebsd_first (&sort_manpath(\%manPathAliases) )) {
        if (!$manPathAliases{$_}) {
            warn "missing release alias '$_'\n" if $debug >= 2;
            next;        
        }

        my $encode_url = &encode_url($_);
        push( @list2,
                qq[<li>"$_" -> "$manPathAliases{$_}" -> ] . 
                qq[<a href="$www{'home_man'}/cgi/man.cgi?manpath=$encode_url">$www{'home_man'}/cgi/man.cgi?manpath=$encode_url</a></li>\n] )
    }

    return qq{\
<h2>Copyright</h2>
<pre>
Copyright (c) 1996-2025 <a href="$mailtoURL">Wolfram Schneider</a>
Copyright (c) 1993-1995 Berkeley Software Design, Inc.
</pre>
<p/>

Copyright (c) for manual pages by OS vendors:
<p>
<a href="https://en.wikipedia.org/wiki/History_of_the_Berkeley_Software_Distribution">2.11 BSD</a>,
<a href="https://www.apple.com">Apple</a>,
<a href="https://www.centos.org">CentOS</a>,
<a href="https://www.debian.org">Debian</a>,
<a href="https://www.dell.com">Dell</a>,
<a href="https://www.dragonflybsd.org">DragonFly BSD</a>,
<a href="https://www.freebsd.org">FreeBSD</a>,
<a href="https://www.hp.com">HP</a>,
<a href="https://en.wikipedia.org/wiki/IRIX">IRIX</a>,
<a href="https://www.minix3.org">Minix</a>,
<a href="https://www.netbsd.org">NetBSD</a>,
<a href="https://en.wikipedia.org/wiki/NeXTSTEP">NeXTSTEP</a>,
<a href="https://www.openbsd.org">OpenBSD</a>,
<a href="https://www.openindiana.org/">OpenIndiana</a>,
<a href="https://en.wikipedia.org/wiki/OpenSolaris">OpenSolaris</a>,
<a href="https://www.opensuse.org">openSUSE</a>,
<a href="https://en.wikipedia.org/wiki/OSF/1">OSF</a>,
<a href="https://9p.io/plan9/">Plan 9</a>,
<a href="https://www.redhat.com">Red Hat</a>,
<a href="https://en.wikipedia.org/wiki/Rhapsody_(operating_system)">Rhapsody</a>,
<a href="https://rockylinux.org/">Rocky</a>,
<a href="https://www.slackware.com">Slackware</a>,
<a href="https://en.wikipedia.org/wiki/SunOS">SunOS</a>,
<a href="https://www.suse.com">SuSE</a>,
<a href="https://ubuntu.com">Ubuntu</a>,
<a href="https://en.wikipedia.org/wiki/Ultrix">ULTRIX</a>,
<a href="https://en.wikipedia.org/wiki/Version_7_Unix">Unix Seventh Edition</a>,
<a href="https://www.x.org">X11R6</a>,
<a href="https://www.xfree86.org">XFree86</a>
</p>

<h2>Shortcuts for FreeBSD manual pages</h2>

<ul>
<li>which manpage: <a href="https://man.freebsd.org/which">https://man.freebsd.org/which</a></li>
<li>socket(2) manpage: <a href="https://man.freebsd.org/socket/2">https://man.freebsd.org/socket/2</a></li>
</ul>

<p />

<ul>
<li>which manpage: <a href="$full_url?which">$full_url?which</a></li>
<li>socket(2) manpage: <a href="$full_url?socket(2)">$full_url?socket(2)</a></li>
</ul>

<h2>Updates</h2>
<p>
The FreeBSD stable/NN, current, and ports manual pages are updated 
every 3 months, usually around the time a new FreeBSD version is released.
</p>
<p>
Other operating system manual pages are updated as needed.
</p>

<h2>Release Permalinks and tarballs</h2>

<p>
Releases and releases aliases permalinks are information how 
to make a link to this script to the right OS version.
</p>

<p>
You may download the manual pages as gzip'd tar archive for private or educational purposes.
A tarball is normally 15-50 MB in size, but can be up to 350 MB for FreeBSD ports.
</p>

<ul>
@list
</ul>


<h2>Releases Aliases Permalinks</h2>

<p>
Release aliases are for lazy people. Plus, they have a longer
lifetime, eg. 'netbsd' points always to the latest NetBSD release.
</p>

<ul>
@list2
</ul>

<h2>FAQ</h2>

<ul>
<li>Get the <a href="$BASE/source">source</a> of the man.cgi script</li>
<li>Troff macros works only if defined in FreeBSD/groff. OS specific
macros like `appeared in NetBSD version 1.2' are not supported.</li>
<li>Some OSs provide only formatted manual pages (catpages), e.g., 
older NetBSD and OpenBSD releases. In this case it is not possible to create Postscript
and troff output.</li>
<li>The <a href="https://cgit.freebsd.org/src/tree/share/misc/bsd-family-tree">
Unix family tree, BSD part</a>.</li>
<li>The <a href="https://ports.freebsd.org/cgi/ports.cgi">
FreeBSD Ports Search</a> script.</li>
</ul>
};

}

sub intro {
    return qq{\
<p />
<i>Man Page Lookup</i> searches for man pages name and section as
given in the selection menu and the query dialog.  <i>Apropos
Keyword Search</i> searches the database for the string given in
the query dialog.  There are also several hypertext links provided
as short-cuts to various queries:  <i>Section Indexes</i> is apropos
listings of all man pages by section.  <i>Explanations of Man
Sections</i> contains pointers to the intro pages for various man
sections.
<p />
};
}

sub faq_output {
    &http_header("text/html");
    print &html_header( "FreeBSD manual page help", '/cgi/' );
    print "<br/>\n<h1>$www{'head'}</h1>\n";
    print &faq . "<br/>\n";
    &html_footer('no_help_link' => 1);
}

sub html_header2 {
    my ( $title, $head ) = @_;

    return qq{<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
	"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en-US" xml:lang="en-US">
<head>
<title>$title</title>
$head
</head> 
<body>
};
}

sub secure_env {
    $main::ENV{'PATH'}    = '/bin:/usr/bin';
    $main::ENV{'MANPATH'} = $manPath{$manPathDefault};
    $main::ENV{'IFS'}     = " \t\n";
    $main::ENV{'PAGER'}   = 'cat';
    $main::ENV{'SHELL'}   = '/bin/sh';
    $main::ENV{'LANG'}    = 'C';
    undef $main::ENV{'DISPLAY'};
}

sub include_output {
    local ($inc) = @_;

    &http_header("text/plain");
    open( I, "$inc" ) || do { print "open $inc: $!\n"; exit(1) };
    while (<I>) { print }
    close(I);
}

# CGI script must die with error status 0
sub mydie {
    local ($message) = @_;
    &http_header("text/html");
    print &html_header("Error");
    print $message;

    &html_footer;
    exit(0);
}

1;

