#!/usr/bin/env python3
import sys
import os
import re
import argparse
import glob
import subprocess

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

    parser.add_argument('-o', metavar='<file-or-directory>', nargs='*',
        dest='other_files', help="Other files or directories you want to ship with. By default, only the src/ directory will be packaged.")


    return parser



def create_dist(project_root='./', build_dir='_build', pkg_name='out', vesion='1.0', pkg_info_file=None, pack_deps=False, other_files=None):

    # go to the project_root first.
    os.chdir(project_root)

    pkg_name = pkg_name + '-' + vesion
    pkg_dir = os.path.join(build_dir, pkg_name)
    os.makedirs(pkg_dir, exist_ok=True)

    # pkg_info_file
    cmd1_0 = "cp {pkg_info_file} {pkg_dir}".format(pkg_info_file=pkg_info_file, pkg_dir=pkg_dir)
    subprocess.check_call(cmd1_0, shell=True)

    # the src and src/wdl directory
    dest_src_dir = os.path.join(pkg_dir, 'src')
    dest_src_wdl_dir = os.path.join(pkg_dir, 'src', 'wdl')
    if pack_deps:
        os.makedirs(dest_src_dir, exist_ok=True)
        cmd1 = 'cp -rf src/* {}'.format(dest_src_dir)
    else:
        os.makedirs(dest_src_wdl_dir, exist_ok=True)
        cmd1 = 'cp -rf src/wdl/* {}'.format(dest_src_wdl_dir)
    subprocess.check_call(cmd1, shell=True)

    if other_files:
        for f in other_files:
            cmd1_1 = 'cp -rf {0} {1}'.format(f, pkg_dir)
            subprocess.check_call(cmd1_1, shell=True)

    os.chdir(build_dir)

    cmd2 = "tar -zcf {pkg_name}.tar.gz {pkg_name}".format(pkg_name=pkg_name)
    subprocess.check_call(cmd2, shell=True)

    cmd3 = 'rm -rf ' + pkg_name
    subprocess.check_call(cmd3, shell=True)

    built_file = "{pkg_name}.tar.gz".format(pkg_name=pkg_name)
    built_file = os.path.abspath(built_file)

    print('built file:', built_file)

    return built_file


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

    if len(sys.argv) == 1 or len(paras) == 0:
        parser.print_help()
        sys.exit()

    args = parser.parse_args(paras)
    args.project_root = os.path.abspath(args.project_root)

    print(args)

    pkg_info = read_pkg_info(args.pkg_info_file)

    pkg_info['name'] = pkg_info['name'].replace('-', '_').lower()

    create_dist(
        project_root=args.project_root,
        build_dir=args.build_dir,
        pkg_name=pkg_info['name'],
        vesion=pkg_info['version'],
        pkg_info_file=args.pkg_info_file,
        pack_deps=args.pack_deps,
        other_files=args.other_files)


if __name__ == '__main__':
    main(paras=sys.argv[1:])

