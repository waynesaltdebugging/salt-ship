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
    "sles": ["11", "12"],
    "raspbian": ["jessie"],
    "fedora": ["27", "28"],
    "arch": ["latest"],
    "freebsd": ["9", "10"],
}

salt_types = ["master", "minion"]

for salt_version in salt_versions:
    p = Path(salt_version)
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
                        """
                    ).lstrip()
                )
                if "--no-build" in sys.argv:
                    continue
                os.chdir(dockerfile_path.parent)
                subprocess.run(
                    [
                        "docker",
                        "build",
                        "--tag",
                        f"waynew/salt/{salt_type}/{os_name}/{os_version}:{salt_version}",
                        ".",
                    ]
                )