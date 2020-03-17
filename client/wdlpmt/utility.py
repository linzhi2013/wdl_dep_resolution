#!/usr/bin/env python3
import os
import re
import collections
import requests

from version_solver import pkg_verison_solver


def download_file(url, outdir='./'):
    if not os.path.exists(outdir):
        os.makedirs(outdir)

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


def login_db(session, url, username, password):
    payload = {
        'username': username,
        'password': password
    }

    for_cookies = session.get(url)
    headers = {
        'X-CSRFToken': for_cookies.headers['Set-Cookie'].split('=')[1].split(';')[0],
        'Referer': url,
        'X-Requested-With':'XMLHttpRequest'}

    # login first
    p = session.post(url, data=payload, headers=headers)

    return session


def get_metadata_dict(metadata_file):
    metadata_dict = collections.defaultdict(dict)
    with open(metadata_file, 'r') as fh:
        for i in fh:
            i = i.strip()
            if not i:
                continue
            line = re.split(r'\s+', i, 3)
            pkg_id, pkg_name, pkg_version = line[0:3]
            metadata_dict[pkg_name][pkg_version] = pkg_id


def get_dep_pkgs(metadata_file=None, query_pkg_version=None):
    '''return a list of the pkg_id on metadata_file
    '''
    result = pkg_verison_solver(
        metadata_file=metadata_file,
        query_pkg_version=query_pkg_version)

    metadata_dict = get_metadata_dict(metadata_file)

    pkg_ids = []
    for pkg_name, ver in result.decisions.items():
        pkg_version = str(ver)
        if pkg_name == '_root_':
            continue
        pkg_id = metadata_dict[pkg_name][pkg_version]
        pkg_ids.append(pkg_id)

    return pkg_ids[::-1]
