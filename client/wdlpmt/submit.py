import requests
import sys
import argparse
import os

from .utility import login_db


def get_para(parser):
    # submit
    parser.add_argument('-url', metavar='<url>',
        default='http://127.0.0.1:8000/',
        dest='base_url', help='Base url [%(default)s]')

    parser.add_argument('-f', metavar='<file>', required=True,
        dest='pkg_gz_file', help="pkg_gz_file")

    parser.add_argument('-u', metavar='<str>', required=True,
        dest='username', help="username")

    parser.add_argument('-p', metavar='<str>', required=True,
        dest='password', help="password")

    return parser


def submit_pkg(base_url='127.0.0.1:8000/', pkg_gz_file=None, username=None, password=None):
    login_url = base_url + 'accounts/login/'
    upload_url = base_url + 'pipeline/upload/'

    with requests.Session() as s:
        session = login_db(
            session=s,
            url=login_url,
            username=username,
            password=password)

        for_cookies=session.get(upload_url)
        headers = {
            'X-CSRFToken': for_cookies.headers['Set-Cookie'].split('=')[1].split(';')[0],
            'Referer': upload_url,
            'X-Requested-With':'XMLHttpRequest'}

        pkg_gz_file_basename = os.path.basename(pkg_gz_file)
        files = {'file': (pkg_gz_file_basename, open(pkg_gz_file, 'rb'))}

        r = session.post(upload_url, files=files, headers=headers)
        print(r.text)


def main(parser=None, paras=None):

    if not parser:
        parser = argparse.ArgumentParser()

    parser = get_para(parser)

    if len(sys.argv) == 1 or len(paras) == 0:
        parser.print_help()
        sys.exit()

    args = parser.parse_args(paras)
    print(args)

    submit_pkg(
        base_url=args.base_url,
        pkg_gz_file=args.pkg_gz_file,
        username=args.username,
        password=args.password)

if __name__ == '__main__':
    main(paras=sys.argv[1:])


