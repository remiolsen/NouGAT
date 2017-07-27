from __future__ import absolute_import
from __future__ import print_function
import argparse
import os
import glob
import re
import subprocess
import yaml
import click

def main(arg):

    sample_configs = glob.glob(arg.source+"*/report/*_QCcontrol.yaml")
    projects = []
    for config in sample_configs:
        with open(config) as f:
            sample_config = yaml.load(f)
            try:
                projects.append(sample_config["projectName"])
            except KeyError:
                print("Check sample config yaml file")
                raise
    if len(projects) == 0:
        raise RuntimeError("Did not find any sample configs in source: {}".format(arg.source))
    if projects.count(projects[0]) != len(projects):
        raise RuntimeError("Sample configs contain inconsistent project names")
    project = projects[0]

    dest = "/proj/{}/INBOX/".format(arg.uppnexid)
    if not os.path.exists(dest) and arg.destpath == None:
        print("did not find the UPPNEX project at {}. Consider specifying the path manually using the option --destpath".format(dest))
        exit(1)
    elif not os.path.exists(dest):
        dest = arg.destpath
    if arg.destpath != None and not os.path.exists(arg.destpath):
        print("No such destpath: {}".format(arg.destpath))
        exit(1)

    dest = os.path.join(dest,project)
    samples_to_copy = map(lambda x: os.path.dirname(os.path.dirname(x)), sample_configs)
    cmds = []
    print("Commands to be run:")
    for sample in samples_to_copy:
        sample_name = os.path.basename(os.path.normpath(sample))
        sample_dest = os.path.join(dest, sample_name)
        cmd = ["rsync", "-auhvr",  sample, sample_dest]
        print("\t"+" ".join(cmd))
        cmds.append(cmd)

    if click.confirm("Do you want to continue?"):
        try:
            os.makedirs(os.path.join(dest,project))
        except OSError:
            print("Check if the destination path already exist and that you have write permissions: {}".format(dest))
        for cmd in cmds:
            subprocess.call(cmd)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type = str,
            help= "Path to the staged delivery folder")
    parser.add_argument("--uppnexid", required=True, type = str,
            help =("Destination Uppnex id"))
    parser.add_argument("--destpath", type = str,
            help =("Path to UPPNEX project INBOX, eg. /pica/v123/a1234567/INBOX"))
    projectID = parser.parse_args()
    main(projectID)


