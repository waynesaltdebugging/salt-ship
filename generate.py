#!/usr/bin/env python3
import os
import sys
import subprocess

from pathlib import Path
from textwrap import dedent

salt_versions = ["2019.2", "2018.3", "2017.7"]

os_versions = {
    "centos": ["6", "7"],
    "ubuntu": ["14.04", "16.04", "18.04"],
    "debian": ["8", "9"],
    "fedora": ["27", "28"],
    "archlinux/base": ["latest"],
    # SLES, Raspbian, FreeBSD, Mac, and Windows images
    # not available.
}

installers = {
     "centos": "yum install -y",
     "fedora": "yum install -y",
     "ubuntu": "apt-get install -y",
     "debian": "apt-get install -y",
     "archlinux/base": "yes | pacman -Scc"
}

salt_types = ["master", "minion", "combo"]
root_path = Path().resolve()
for salt_version in salt_versions:
    p = root_path / salt_version
    for os_name in os_versions:
        os_path = p / os_name
        for os_version in os_versions[os_name]:
            os_ver_path = os_path / os_version
            for salt_type in salt_types:
                dockerfile_path = os_ver_path / salt_type / "Dockerfile"
                dockerfile_path.parent.mkdir(parents=True, exist_ok=True)
                dockerfile_path.write_text(
                    dedent(
                        f"""
                        FROM {os_name}:{os_version}

                        RUN {installers[os_name]} install python3
                        RUN python3 -m ensurepip
                        RUN python3 -m pip install salt
                        """
                    ).lstrip()
                )
                if "--no-build" in sys.argv:
                    continue
                os.chdir(dockerfile_path.parent)
                print("Building", dockerfile_path)
                ret = subprocess.run(
                    [
                        "docker",
                        "build",
                        "--tag",
                        f"waynew/salt/{salt_type}/{os_name}/{os_version}:{salt_version}",
                        ".",
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                if ret.returncode != 0:
                    print("Error with", dockerfile_path)
                    print(ret.stderr.decode())
