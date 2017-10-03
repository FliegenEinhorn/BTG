#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2016-2017 Conix Cybersecurity
# Copyright (c) 2016-2017 Robin Marsollier
# Copyright (c) 2017 Alexandra Toussaint
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

import sys
import warnings

from lib.io import module as mod

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from pymisp import PyMISP


class Misp:
    def __init__(self, ioc, type, config):
        self.config = config
        self.module_name = __name__.split(".")[1]
        self.types = ["MD5", "SHA1", "domain", "IPv4", "IPv6", "URL", "SHA256", "SHA512"]
        self.search_method = "Onpremises"
        self.description = "Search IOC in MISP database"
        self.author = "Conix"
        self.creation_date = "07-10-2016"
        self.type = type
        self.ioc = ioc

        if type in self.types and mod.allowedToSearch(self.search_method):
            self.Search()
        else:
            mod.display(self.module_name, "", "INFO", "MISP module not activated")

    def Search(self):
        mod.display(self.module_name, "", "INFO", "Search in misp...")
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                if ("misp_url" in self.config and
                        "misp_key" in self.config and
                        "misp_verifycert" in self.config):
                    m = PyMISP(self.config["misp_url"],
                               self.config["misp_key"],
                               self.config["misp_verifycert"],
                               'json')
                else:
                    mod.display(self.module_name,
                                message_type="ERROR",
                                string=("Check if you have misp_url, misp_key and misp_verifycert"
                                        "in config.ini"))
                    sys.exit()
        except Exception as e:
            mod.display(self.module_name, self.ioc, "ERROR", e)
            return
        result = m.search_all(self.ioc)
        try:
            for event in result["response"]:
                tag_display = ""
                try:
                    for tag in event["Event"]["Tag"]:
                        if "misp_tag_display" in self.config:
                            if tag["name"].split(":")[0] in self.config["misp_tag_display"]:
                                if len(tag_display) == 0:
                                    tag_display = "["
                                else:
                                    tag_display = "%s|"%tag_display
                                tag_display = "%s%s"%(tag_display, tag["name"])
                        else:
                            mod.display(self.module_name,
                                        message_type="ERROR",
                                        string="Check if you have misp_tag_display in config.ini")
                except:
                    pass
                if len(tag_display) != 0:
                    tag_display = "%s]"%tag_display
                mod.display(self.module_name,
                            self.ioc,
                            "FOUND",
                            "%s Event: %sevents/view/%s"%(tag_display,
                                                          self.config["misp_url"],
                                                          event["Event"]["id"]))
        except:
            try:
                if result['message'] == "No matches":
                    pass
                elif "Authentication failed" in result['message']:
                    mod.display(__name__.split(".")[1],
                                message_type="ERROR",
                                string=result['message'])
            except:
                pass
