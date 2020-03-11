#!/usr/bin/env python3
import sys
import os
import re
import argparse
import glob
import subprocess
import collections



def get_para():
    desc = '''
    To collect package information, e.g. name, version, dependencies.
    '''

    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('-d', dest='repo_url', metavar='<directory>', default='./',
        help="the repository directory [%(default)s]")

    parser.add_argument('-o', metavar='<file>', default='wdl_package_info.txt',
        help="outfile name [%(default)s] ")


    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()

    return parser.parse_args()



def get_repo_pkgs(repo_url=None):
    '''
    get all available pkgs in repo_url
    '''

    pkg_version_path = collections.defaultdict(dict)

    files = glob.glob(repo_url + '/**/*gz')
    for f in files:
        f = os.path.abspath(f)
        f_base = os.path.basename(f)
        line = f_base.split('-', 1)

        pkg_name = line[0]
        pkg_version = re.sub('.tar.gz', '', line[1])
        pkg_version_path[pkg_name][pkg_version] = f

    return pkg_version_path


def read_pkg_info(pkg_info_file=None):
    pkg_info = {}
    with open(pkg_info_file, 'r') as fh:
        for i in fh:
            i = i.strip()
            if not i or i.startswith('#'):
                continue

            key, value = i.split(':', 1)
            key, value = [j.strip() for j in (key, value)]
            if value:
                pkg_info[key] = value

            if key == 'deps':
                value = re.sub(r'\s+', '', value)
                other_wdls = value.split(',')
                pkg_info[key] = other_wdls

    return pkg_info


def main():
    args = get_para()

    tmp_dir = 'tmp_pkg_info_dir'

    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)

    pkg_version_path = get_repo_pkgs(args.repo_url)

    fhout = open(args.o, 'w')

    os.chdir(tmp_dir)
    for pkg_name in pkg_version_path:
        for pkg_version in pkg_version_path[pkg_name]:
            pkg_path = pkg_version_path[pkg_name][pkg_version]
            pkg_dir = os.path.basename(pkg_path).replace('.tar.gz', '')

            cmd = 'tar -zxf {0}'.format(pkg_path)
            subprocess.check_call(cmd, shell=True)

            pkg_info_file = os.path.join(pkg_dir, 'packaging_info.txt')
            if not os.path.exists(pkg_info_file):
                print(pkg_info_file, 'not found for', pkg_name, pkg_version, file=sys.stderr)
                continue

            pkg_info = read_pkg_info(pkg_info_file)
            print(pkg_info['name'], pkg_info['version'], pkg_path, ",".join(pkg_info['deps']), sep='\t', file=fhout)


            cmd2 = 'rm -rf ' + pkg_dir
            subprocess.check_call(cmd2, shell=True)

























if __name__ == '__main__':
    main()

