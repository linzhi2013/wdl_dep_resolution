#!/usr/bin/env python3
import sys
import os
import re
import argparse
import subprocess


def get_para():
    desc = '''
    To push the packaged WDL *.tar.gz file to remote repository.
    '''

    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('-r', dest='repo_url', metavar='<url>',
        help="remote repo url")

    parser.add_argument('-w', metavar='<file>',
        help="packaged WDL *.tar.gz file")


    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()

    return parser.parse_args()



def main():
    args = get_para()

    local_pkg_gz_file = args.w

    pkg_basename = os.path.basename(local_pkg_gz_file)
    pkg_basename_dir = pkg_basename.split('-')[0]

    remote_pkg_dir = os.path.join(args.repo_url, pkg_basename_dir)

    if not os.path.exists(remote_pkg_dir):
        os.makedirs(remote_pkg_dir)

    cmd = 'cp {0} {1}'.format(local_pkg_gz_file, remote_pkg_dir)
    subprocess.check_call(cmd, shell=True)






if __name__ == '__main__':
    main()

