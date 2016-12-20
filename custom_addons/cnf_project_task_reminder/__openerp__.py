# -*- coding: utf-8 -*-
# Copyright 2016
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Project task reminder",
    "summary": "Send mail when project task expired",
    "version": "9.0.1.0.0",
    "category": "Project",
    "website": "https://canifa.com",
    "author": "Canifa",
    "application": False,
    "installable": True,
    "depends": [
        "project",
    ],
    "data": [
        "views/template_reminder.xml",
    ],
}
