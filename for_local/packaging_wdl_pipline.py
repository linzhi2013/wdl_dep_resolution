#!/usr/bin/env python3
import sys
import os
import re
import argparse
import subprocess
import glob


def get_para():
    desc = '''

    '''

    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('-c', metavar='<file>',
        help="packaging_info.txt file")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()

    return parser.parse_args()



def create_dist(build_dir='_build', pkg_name='out', vesion='1.0', src_files=None):
    pkg_name = pkg_name + '-' + vesion
    pkg_dir = os.path.join(build_dir, pkg_name)

    os.makedirs(pkg_dir)
    for f in src_files:
        cmd1 = 'cp -r {0} {1}'.format(f, pkg_dir)
        subprocess.check_call(cmd1, shell=True)

    os.chdir(build_dir)

    cmd2 = "tar -zcf {pkg_name}.tar.gz {pkg_name}".format(pkg_name=pkg_name)
    subprocess.check_call(cmd2, shell=True)

    cmd3 = 'rm -rf ' + pkg_name
    subprocess.check_call(cmd3, shell=True)

    built_file = "{pkg_name}.tar.gz".format(pkg_name=pkg_name)
    built_file = os.path.abspath(built_file)

    print('built file:', built_file)

    return built_file


def get_src_files(src_dir='./'):
    files = glob.glob(src_dir + '/*')
    return files


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

            elif key == 'deps':
                other_wdls = value.split(',')
                pkg_info[key] = other_wdls

    return pkg_info


def main():
    args = get_para()

    pkg_info = read_pkg_info(args.c)


    src_files = get_src_files(src_dir='./')

    create_dist(
        build_dir='_build',
        pkg_name=pkg_info['name'],
        vesion=pkg_info['version'],
        src_files=src_files)






if __name__ == '__main__':
    main()

