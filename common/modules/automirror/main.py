#!/usr/bin/env python3

# Copyright (C) 2018 Simon Quigley <tsimonq2@ubuntu.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import json
import subprocess
import libcalamares
from time import strftime
from urllib import request
from lsb_release import get_distro_information

global sources
sources = """# Automatically generated by Calamares on DATE.
# Lines starting with "deb" are mandatory, while lines starting with "deb-src"
# are for more detailed package information.

## See http://help.ubuntu.com/community/UpgradeNotes for how to upgrade to
## newer versions of DISTRIBUTION.
deb URL/ubuntu/ CODENAME main restricted
# deb-src URL/ubuntu/ CODENAME main restricted

## Major bug fix updates produced after the final release of DISTRIBUTION.
## Have you noticed a regression? Please report it!
## https://wiki.ubuntu.com/StableReleaseUpdates#Regressions
deb URL/ubuntu/ CODENAME-updates main restricted
# deb-src URL/ubuntu/ CODENAME-updates main restricted

## Software from this repository is ENTIRELY UNSUPPORTED by the Ubuntu team.
## Also, please note that software in Universe WILL NOT receive any review or
## updates from the Ubuntu security team directly. Updates in this repository
## are provided by volunteers, but most come from Debian.
deb URL/ubuntu/ CODENAME universe
# deb-src URL/ubuntu/ CODENAME universe
deb URL/ubuntu/ CODENAME-updates universe
# deb-src URL/ubuntu/ CODENAME-updates universe

## Software from this repository is ENTIRELY UNSUPPORTED by the Ubuntu team,
## and may not be under a free licence. Please satisfy yourself as your rights
## to use the software. Also, please note that software in Multiverse WILL NOT
## receive any review or updates from the Ubuntu security team directly.
deb URL/ubuntu/ CODENAME multiverse
# deb-src URL/ubuntu/ CODENAME multiverse
deb URL/ubuntu/ CODENAME-updates multiverse
# deb-src URL/ubuntu/ CODENAME-updates multiverse

## Software from this repository contains tested security updates from the
## Ubuntu security team.
deb http://security.ubuntu.com/ubuntu CODENAME-security main restricted
# deb-src http://security.ubuntu.com/ubuntu CODENAME-security main restricted
deb http://security.ubuntu.com/ubuntu CODENAME-security universe
# deb-src http://security.ubuntu.com/ubuntu CODENAME-security universe
deb http://security.ubuntu.com/ubuntu CODENAME-security multiverse
# deb-src http://security.ubuntu.com/ubuntu CODENAME-security multiverse

## Software from this repository may not have been tested as extensively as
## software contained in the main release, although it includes newer versions
## of some applications which may provide useful features. Also, please note
## that software in Backports WILL NOT receive any review or updates from the
## Ubuntu security team.
deb URL/ubuntu/ CODENAME-backports main restricted universe multiverse
# deb-src URL/ubuntu/ CODENAME-backports main restricted universe multiverse

## Uncomment the following two lines to add software from Canonical's
## "partner" repository.
## This software is not part of Ubuntu, but is offered by Canonical and the
## respective vendors as a service to Ubuntu users.
# deb http://archive.canonical.com/ubuntu CODENAME partner
# deb-src http://archive.canonical.com/ubuntu CODENAME partner"""

def getcountry():
    # This is hardcoded for now, but should eventually be put into the config
    with request.urlopen("https://ipapi.co/json") as url:
        localedata = json.loads(url.read().decode())
    return localedata["country"]

def getmirror(country):
    with request.urlopen(libcalamares.job.configuration["mirrorList"]) as url:
        mirrors = json.loads(url.read().decode())
    if country in mirrors.keys():
        return mirrors[country] + "."
    else:
        return ""

def getcodename():
    return get_distro_information()["CODENAME"]

def changesources(prefix):
    root = libcalamares.globalstorage.value("rootMountPoint")

    url = prefix + libcalamares.job.configuration["baseUrl"]
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url

    if libcalamares.job.configuration["backend"] == "apt":
        distro = libcalamares.job.configuration["distribution"]
        if "ubuntu" in distro.lower():
            global sources
            sources = sources.replace("DISTRIBUTION", distro)
            sources = sources.replace("CODENAME", getcodename())
            sources = sources.replace("URL", url)
            sources = sources.replace("DATE", strftime("%Y-%m-%d"))

            with open(root + "/etc/apt/sources.list", "r+") as sourcesfile:
                sourcesfile.seek(0)
                sourcesfile.write(sources)
                sourcesfile.truncate()

def run():
    """Autoselect a mirror from a list."""
    if libcalamares.globalstorage.value("hasInternet"):
        country = getcountry()
        prefix = getmirror(country)
    else:
        prefix = ""

    changesources(prefix)