#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2016-2017 Conix Cybersecurity
#
# This file is part of BTG.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

import urllib
import urllib2
from json import loads
from random import choice, randint
from time import sleep

from lib.io import module as mod
import ast


class Virustotal:
    """
        This module allow you to search IOC in Virustotal
    """
    def __init__(self, ioc, type, config):
        self.config = config
        self.module_name = __name__.split(".")[1]
        self.types = ["MD5", "SHA1", "SHA256", "URL", "IPv4", "domain"]
        self.search_method = "Online"
        self.description = "Search IOC in VirusTotal database"
        self.author = "Conix"
        self.creation_date = "13-09-2016"
        self.type = type
        self.ioc = ioc
        if type in self.types and mod.allowedToSearch(self.search_method):
            self.search()
        else:
            mod.display(self.module_name, "", "INFO", "VirusTotal module not activated")

    def search(self):
        mod.display(self.module_name, "", "INFO", "Search in VirusTotal ...")
        if "proxy_host" in self.config:
            if len(self.config["proxy_host"]["https"]) > 0:
                proxy = urllib2.ProxyHandler({'https': self.config["proxy_host"]["https"]})
                opener = urllib2.build_opener(proxy)
            else:
                opener = urllib2.build_opener()
        else:
            mod.display(self.module_name,
                        message_type="ERROR",
                        string="Please check if you have proxy_host field in config.ini")
        urllib2.install_opener(opener)
        try:
            if "virustotal_api_keys" in self.config:
                self.key = choice(self.config["virustotal_api_keys"])
            else:
                mod.display(self.module_name,
                            message_type="ERROR",
                            string="Check if you have virustotal_api_keys field in config.ini")
        except:
            mod.display(self.module_name, self.ioc, "ERROR", "Please provide your authkey.")
            return

        if self.type in ["URL", "domain", "IPv4"]:
            self.searchURL()
        else:
            self.searchReport()

    def searchReport(self):
        self.url = "https://www.virustotal.com/vtapi/v2/file/report"
        parameters = {"resource": self.ioc,
                      "apikey": self.key,
                      "allinfo": 1}
        data = urllib.urlencode(parameters)
        req = urllib2.Request(self.url, data)
        response = urllib2.urlopen(req)
        if response.getcode() == 200 :
            response_content = response.read()
            try:
                import simplejson
                json_content = simplejson.loads(response_content)
            except :
                mod.display(self.module_name, self.ioc, "ERROR", "Virustotal json decode fail. Blacklisted/Bad API key? (Sleep 10sec).")
                sleep(randint(5, 10))
            try:
                if json_content["positives"]:
                    mod.display(self.module_name,
                                self.ioc,
                                "FOUND",
                                "Score: %s/%s | %s"%(json_content["positives"],
                                                     json_content["total"],
                                                     json_content["permalink"]))
            except:
                pass
        else :
            mod.display(self.module_name, self.ioc, "ERROR", "VirusTotal returned "+ str(response.getcode()))

    def searchURL(self):
        self.url = "http://www.virustotal.com/vtapi/v2/url/report"
        parameters = {"resource": self.ioc,
                      "apikey": self.key}
        data = urllib.urlencode(parameters)
        req = urllib2.Request(self.url, data)
        while True:
            try:
                response = urllib2.urlopen(req).read()
                json_content = loads(response)
                break
            except:
                mod.display(self.module_name,
                            self.ioc,
                            "INFO",
                            "Virustotal json decode fail. Blacklisted/Bad API key? (Sleep 10sec).")
                sleep(randint(5, 10))
                pass
        try:
            if json_content["positives"]:
                mod.display(self.module_name,
                            self.ioc,
                            "FOUND",
                            "Score: %s/%s | %s"%(json_content["positives"],
                                                 json_content["total"],
                                                 json_content["permalink"]))
        except:
            pass
