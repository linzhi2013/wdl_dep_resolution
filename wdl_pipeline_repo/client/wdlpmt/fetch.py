#!/usr/bin/env python3
import sys
import argparse

from utility import read_pkg_info, download_file, get_dep_pkgs


def get_para(parser):
    # fetch
    parser.add_argument('-i', metavar='<file>', required=True,
        dest='pkg_info_file', help="pkg_info.txt file")

    parser.add_argument('-url', metavar='<url>',
        default='http://127.0.0.1:8000/',
        dest='base_url', help='Base url [%(default)s]')

    parser.add_argument('-cache_dir', metavar='<directory>',
        default='_wdl_cache', help='the cache directory [%(default)s]')

    return parser


def fetch_pkgs(base_url='127.0.0.1:8000/', cache_dir='./', pkg_info_file=None):
    url = base_url + 'pipeline/'
    remote_metadata_file = url + 'metadata/'

    local_metadata_file = download_file(remote_metadata_file, cache_dir)

    pkg_info = read_pkg_info(pkg_info_file)
    query_pkg_version = pkg_info['deps']


    # get the package ids
    pkg_ids = get_dep_pkgs(
        metadata_file=local_metadata_file,
        query_pkg_version=query_pkg_version)

    # download package
    downloaded_files = []
    for pkg_id in pkg_ids:
        pkg_url = url + 'download/{}/'.format(pkg_id)
        pkg_cache_gz_file = download_file(pkg_url, cache_dir)
        downloaded_files.append(pkg_cache_gz_file)

    return downloaded_files


def main(parser=None, paras=None):

    if not parser:
        parser = argparse.ArgumentParser()

    parser = get_para(parser)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()

    args = parser.parse_args(paras)

    print(args)

    fetch_pkgs(
        base_url=args.base_url,
        cache_dir=args.cache_dir,
        pkg_info_file=args.pkg_info_file)

if __name__ == '__main__':
    main(paras=sys.argv[1:])




