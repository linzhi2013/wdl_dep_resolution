#!/usr/bin/env python3
import sys
import os
import re
import argparse
import subprocess
import glob
import collections
from version_solver import pkg_verison_solver


def get_para():
    desc = '''

    '''

    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('-c', metavar='<file>',
        help="packaging_info.txt file")

    parser.add_argument('-repo_url', metavar='<str>',
        help="repository path")

    parser.add_argument('-o', dest='cache_dir', metavar='<dir>', default='./wdl_repo_cache',
    help='output directory [./]')

    parser.add_argument('-p', dest='project_root', metavar='<dir>', default='./new_wdl_project',
    help='new project_root directory')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()

    return parser.parse_args()




def read_pkg_info(pkg_info_file=None):
    pkg_info = {}
    with open(pkg_info_file, 'r') as fh:
        for i in fh:
            i = i.strip()
            if not i or i.startswith('#'):
                continue

            key, value = re.split(r'\:\s*', i, 1)
            if value:
                pkg_info[key] = value

            if key == 'deps':
                dep_pkgs = {}
                dep = value.split(',')
                for k in dep:
                    k = k.strip()
                    line2 = re.split(r'\:\s*', k, 1)
                    dep_pkg_name = line2[0]
                    dep_pkg_vesions = '>0.0'
                    if len(line2) == 2:
                        dep_pkg_vesions = line2[1]
                    dep_pkgs[dep_pkg_name] = dep_pkg_vesions

                pkg_info['deps'] = dep_pkgs

    return pkg_info


def download_dep_pkgs(result=None, cache_dir=None, pkg_version_path=None, project_root='new_wdl_project'):

    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    for pkg, ver in result.decisions.items():
        ver = str(ver)
        if pkg == '_root_':
            continue

        remote_path = pkg_version_path[pkg][ver]
        if not os.path.exists(remote_path):
            print(remote_path, 'not found!', file=sys.stderr)
            continue

        cmd = 'cp {0} {1} '.format(remote_path, cache_dir)
        subprocess.check_call(cmd, shell=True)

        pkg_basename = os.path.basename(remote_path)
        cache_pkg_gz_file = os.path.join(cache_dir, pkg_basename)
        cache_pkg_dir = cache_pkg_gz_file.replace('.tar.gz', '')


        cmd2 = 'tar -zxvf {0} -C {1}'.format(cache_pkg_gz_file, cache_dir)
        subprocess.check_call(cmd2, shell=True)


        # src
        cache_pkg_src_dir = os.path.join(cache_pkg_dir, 'src')
        project_src = os.path.join(project_root, 'src', 'deps', pkg)
        if not os.path.exists(project_src):
            os.makedirs(project_src)
        cmd3 = 'cp -r {0}/* {1}'.format(cache_pkg_src_dir, project_src)
        subprocess.check_call(cmd3, shell=True)

        # docker
        cache_pkg_docker_dir = os.path.join(cache_pkg_dir, 'docker')
        project_docker = os.path.join(project_root, 'docker', 'deps', pkg)
        if not os.path.exists(project_docker):
            os.makedirs(project_docker)
        cmd4 = 'cp -r {0}/* {1}'.format(cache_pkg_docker_dir, project_docker)
        subprocess.check_call(cmd4, shell=True)

        # doc
        cache_pkg_doc_dir = os.path.join(cache_pkg_dir, 'doc')
        project_doc = os.path.join(project_root, 'doc', 'deps', pkg)
        if not os.path.exists(project_doc):
            os.makedirs(project_doc)
        cmd5 = 'cp -r {0}/* {1}'.format(cache_pkg_doc_dir, project_doc)
        subprocess.check_call(cmd5, shell=True)


def get_pkg_ver_path(wdl_package_info_file=None):
    pkg_version_path = collections.defaultdict(dict)
    with open(wdl_package_info_file, 'r') as fh:
        for i in fh:
            i = i.strip()
            if not i:
                continue
            line = re.split(r'\s+', i, 3)
            pkg_name, pkg_version, pkg_path = line[0:3]
            pkg_version_path[pkg_name][pkg_version] = pkg_path

    return pkg_version_path



def main():
    args = get_para()

    #wdl_package_info_file = os.path.join(args.repo_url, 'wdl_package_info.txt')

    wdl_package_info_file = 'wdl_package_info.txt'

    pkg_version_path = get_pkg_ver_path(wdl_package_info_file)


    pkg_info = read_pkg_info(args.c)
    query_pkg_version = pkg_info['deps']


    result = pkg_verison_solver(wdl_package_info_file, query_pkg_version)

    download_dep_pkgs(
        result=result,
        cache_dir=args.cache_dir,
        pkg_version_path=pkg_version_path,
        project_root=args.project_root)



if __name__ == '__main__':
    main()