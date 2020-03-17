#!/usr/bin/env python3
import sys
import os
import re
import argparse
import glob

def get_para(parser):

    parser.add_argument('-project_root', metavar='<directory>',
        default='./',
        help='the project_root directory [%(default)s]')

    parser.add_argument('-i', metavar='<file>', required=True,
        dest='pkg_info_file', help="pkg_info.txt file")

    parser.add_argument('-d', action='store_true',
        dest='pack_deps', default=False,
        help="Also package the 'src/deps' directory [%(default)s]")

    parser.add_argument('-b', metavar='<directory>',
        default='_build',
        dest='build_dir', help="build directory name [%(default)s]")


    return parser



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



def main(parser=None, paras=None):

    if not parser:
        parser = argparse.ArgumentParser()

    parser = get_para(parser)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()

    args = parser.parse_args(paras)
    args.project_root = os.path.abspath(args.project_root)

    print(args)

    pkg_info = read_pkg_info(args.pkg_info_file)

    pkg_info['name'] = pkg_info['name'].replace('-', '_').lower()

    src_dir = os.path.join(args.project_root, 'src')
    src_wdl_dir = os.path.join(args.project_root, 'src', 'wdl')

    if args.pack_deps:
        src_files = get_src_files(src_dir=src_dir)
    else:
        src_files = get_src_files(src_dir=src_wdl_dir)

    create_dist(
        build_dir=args.build_dir,
        pkg_name=pkg_info['name'],
        vesion=pkg_info['version'],
        src_files=src_files)


if __name__ == '__main__':
    main(paras=sys.argv[1:])

