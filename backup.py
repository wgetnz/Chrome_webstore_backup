#!/usr/bin/env python

import argparse
import os.path
import sys
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

try:
    from urllib.parse import urlparse, urlencode, unquote
    from urllib.request import urlopen
except ModuleNotFoundError:
    from urlparse import urlparse
    from urllib import urlencode, unquote
    from urllib2 import urlopen

arg_parser = argparse.ArgumentParser(description='Chrome extension downloader')
arg_parser.add_argument('-q', '--quiet',
    action='store_true',
    help='suppress all messages')
arg_parser.add_argument('-o', '--output-dir',
    required=False,
    default='.',
    help='directory to save the .CRX files')
args = arg_parser.parse_args(sys.argv[1:])

crx_base_url = 'https://clients2.google.com/service/update2/crx'

def download_extension(ext_name, ext_id, output_dir, quiet):
    crx_params = {
        'response': 'redirect',
        'prodversion': '91.0',
        'acceptformat': 'crx2,crx3',
        'x': f'id={ext_id}&uc'
    }
    crx_url = crx_base_url + '?' + urlencode(crx_params)
    crx_path = os.path.join(output_dir, f'{ext_name}_{ext_id}.crx')

    if not quiet:
        print(f'Downloading {crx_url} to {crx_path} ...')

    with open(crx_path, 'wb') as file:
        file.write(urlopen(crx_url).read())

    if not quiet:
        print('Success!')

def process_line(line):
    ext_url = urlparse(line.strip())
    ext_id = os.path.basename(ext_url.path)
    ext_name = os.path.basename(os.path.dirname(ext_url.path))
    ext_name = unquote(ext_name)  # URL 解码扩展名
    download_extension(ext_name, ext_id, args.output_dir, args.quiet)

with open('list.txt', 'r') as file:
    lines = file.readlines()

with ThreadPoolExecutor() as executor:
    executor.map(process_line, lines)
