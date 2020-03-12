#!/usr/bin/env python3
import sys
import os
import re
import argparse
import collections
import requests
import subprocess
import glob
import platform

from version_solver import pkg_verison_solver


def get_para():
    desc = '''
    A tool for manage WDL pipelines
    '''

    parent_parser = argparse.ArgumentParser(description=desc)

    subparsers = parent_parser.add_subparsers(title='subcommands', dest='subcommand')

    parent_parser.add_argument('-cache_dir', metavar='<directory>',
        default='_wdl_cache', help='the cache directory [%(default)s]')

    parent_parser.add_argument('-url', metavar='<url>',
        default='http://127.0.0.1:8000/',
        dest='base_url', help='Base url [%(default)s]')

    parent_parser.add_argument('-project_root', metavar='<directory>',
        default='./', help='the project_root directory [%(default)s]')

    # fetch
    fetch_paser = subparsers.add_parser('fetch', help='fetch all dep pkgs for a project.')

    fetch_paser.add_argument('-i', metavar='<file>', required=True,
        dest='query_pkg_version_file', help="query_pkg_version_file")

    # install
    install_paser = subparsers.add_parser('install', help='fetch and install all dep pkgs for a project.')

    install_paser.add_argument('-i', metavar='<file>', required=True,
        dest='query_pkg_version_file', help="query_pkg_version_file")


    # submit
    submit_paser = subparsers.add_parser('submit', help='submit a WDL pipelin to repo.')

    submit_paser.add_argument('-f', metavar='<file>', required=True,
        dest='pkg_gz_file', help="pkg_gz_file")

    submit_paser.add_argument('-u', metavar='<str>', required=True,
        dest='username', help="username")

    submit_paser.add_argument('-p', metavar='<str>', required=True,
        dest='password', help="password")


    if len(sys.argv) == 1:
        parent_parser.print_help()
        sys.exit()

    return parent_parser.parse_args()



def download_file(url, outdir='./'):
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        d = r.headers['content-disposition']
        fname = re.findall("filename=(.+)", d)[0]

        outfile = os.path.join(outdir, fname)

        with open(outfile, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    # f.flush()
    return os.path.abspath(outfile)



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


def get_dep_pkgs(metadata_file=None, query_pkg_version=None):
    '''return a list of the pkg_id on metadata_file
    '''
    result = pkg_verison_solver(
        metadata_file=metadata_file,
        query_pkg_version=query_pkg_version)

    metadata_dict = collections.defaultdict(dict)
    with open(metadata_file, 'r') as fh:
        for i in fh:
            i = i.strip()
            if not i:
                continue
            line = re.split(r'\s+', i, 3)
            pkg_id, pkg_name, pkg_version = line[0:3]
            metadata_dict[pkg_name][pkg_version] = pkg_id

    pkg_ids = []
    for pkg_name, ver in result.decisions.items():
        pkg_version = str(ver)
        if pkg_name == '_root_':
            continue
        pkg_id = metadata_dict[pkg_name][pkg_version]
        pkg_ids.append(pkg_id)

    return pkg_ids[::-1]


def fetch_pkgs(args, subcommand=None):
    url = args.base_url + 'pipeline/'
    cache_dir = args.cache_dir
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    pkg_info = read_pkg_info(args.query_pkg_version_file)
    query_pkg_version = pkg_info['deps']

    remote_metadata_file = url + 'metadata/'
    local_metadata_file = download_file(remote_metadata_file, cache_dir)

    pkg_ids = get_dep_pkgs(metadata_file=local_metadata_file, query_pkg_version=query_pkg_version)

    for pkg_id in pkg_ids:
        pkd_url = url + 'download/{}/'.format(pkg_id)
        pkg_cache_gz_file = download_file(pkd_url, cache_dir)
        if subcommand == 'install':
            install_pkgs(
                pkg_cache_gz_file=pkg_cache_gz_file,
                project_root=args.project_root,
                cache_dir=args.cache_dir)


def install_pkgs(pkg_cache_gz_file, project_root='./', cache_dir='./'):
    cmd = 'tar -zxvf {0} -C {1}'.format(pkg_cache_gz_file, cache_dir)
    subprocess.check_call(cmd, shell=True)

    cache_pkg_dir = pkg_cache_gz_file.replace('.tar.gz', '')
    pkg_name = os.path.basename(pkg_cache_gz_file).split('-', 1)[0]

    # src
    cache_pkg_src_wdl = os.path.join(cache_pkg_dir, 'src', 'wdl')
    project_src_deps = os.path.join(project_root, 'src', 'deps', pkg_name)
    if not os.path.exists(project_src_deps):
        os.makedirs(project_src_deps)
    cmd = 'cp -r {0}/* {1}'.format(cache_pkg_src_wdl, project_src_deps)
    subprocess.check_call(cmd, shell=True)

    # update import paths
    update_wdl_import_paths(project_src_deps, pkg_name)


    # doc
    cache_pkg_doc = os.path.join(cache_pkg_dir, 'doc')
    project_doc_deps = os.path.join(project_root, 'doc', 'deps', pkg_name)
    if not os.path.exists(project_doc_deps):
        os.makedirs(project_doc_deps)
    cmd = 'cp -r {0}/* {1}'.format(cache_pkg_doc, project_doc_deps)
    subprocess.check_call(cmd, shell=True)

    # docker
    cache_pkg_docker = os.path.join(cache_pkg_dir, 'docker')
    project_docker_deps = os.path.join(project_root, 'docker', 'deps', pkg_name)
    if not os.path.exists(project_docker_deps):
        os.makedirs(project_docker_deps)
    cmd = 'cp -r {0}/* {1}'.format(cache_pkg_docker, project_docker_deps)
    subprocess.check_call(cmd, shell=True)


def update_wdl_import_paths(wdl_dir=None, pkg_name=None):
    wdl_files = glob.glob(wdl_dir + '/**/*.wdl', recursive=True)
    plt = platform.system()
    for f in wdl_files:
        if plt == 'Darwin':
            cmd = "sed -i '' 's#src/wdl/#src/deps/{pkg_name}/#g' {f}".format(pkg_name=pkg_name, f=f)
        else:
            cmd = "sed -i 's#src/wdl/#src/deps/{pkg_name}/#g' {f}".format(pkg_name=pkg_name, f=f)
        print(cmd)
        subprocess.check_call(cmd, shell=True)



def submit_pkg(args):
    login_url = args.base_url + 'accounts/login/'
    upload_url = args.base_url + 'pipeline/upload/'

    pkg_gz_file = args.pkg_gz_file

    payload = {
        'username': args.username,
        'password': args.password
    }
    with requests.Session() as s:
        for_cookies=s.get(login_url)
        headers = {
            'X-CSRFToken': for_cookies.headers['Set-Cookie'].split('=')[1].split(';')[0],
            'Referer': login_url,
            'X-Requested-With':'XMLHttpRequest'}

        # login first
        p = s.post(login_url, data=payload, headers=headers)


        for_cookies=s.get(upload_url)
        headers = {
            'X-CSRFToken': for_cookies.headers['Set-Cookie'].split('=')[1].split(';')[0],
            'Referer': upload_url,
            'X-Requested-With':'XMLHttpRequest'}

        pkg_gz_file_basename = os.path.basename(pkg_gz_file)
        files = {'file': (pkg_gz_file_basename, open(pkg_gz_file, 'rb'))}

        r = s.post(upload_url, files=files, headers=headers)
        print(r.text)


def main():
    args = get_para()
    if args.subcommand == 'fetch':
        fetch_pkgs(args)

    if args.subcommand == 'install':
        fetch_pkgs(args, subcommand='install')

    if args.subcommand == 'submit':
        submit_pkg(args)



if __name__ == '__main__':
    main()

