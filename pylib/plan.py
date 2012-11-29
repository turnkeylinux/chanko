# Copyright (c) 2012 Alon Swartz <alon@turnkeylinux.org>
#
# This file is part of Chanko
#
# Chanko is free software; you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at your
# option) any later version.

import os
from utils import makedirs, parse_inputfile

class Plan:
    def __init__(self, path):
        self.base = path
        makedirs(self.base)

    def update(self, package_names, plan_name):
        plan_path = os.path.join(self.base, plan_name)

        current_plan = []
        if os.path.exists(plan_path):
            current_plan = parse_inputfile(plan_path)

        for package_name in package_names:
            if not package_name in current_plan:
                file(plan_path, "a").write(package_name + "\n")

    def list(self):
        plans = {}
        for plan_name in os.listdir(self.base):
            plan_path = os.path.join(self.base, plan_name)
            plans[plan_name] = parse_inputfile(plan_path)

        return plans

