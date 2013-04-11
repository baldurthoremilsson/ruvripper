#!/usr/bin/env python

from cStringIO import StringIO
import requests
import sys
import re
import time


def parse_page(url):
    r = requests.get(url)
    text = r.text

    tengi_url_match = re.findall('(http://load.cache.is/.*?)"', text)
    filematch = re.findall("(:1935.*)'", text)
    r = requests.get(tengi_url_match[0])
    tengi_ip_match = re.findall('var tengipunktur="(.*?)"', r.text)
    playlisturl = 'http://{}{}'.format(tengi_ip_match[0], filematch[0])
    baseurl = playlisturl[:playlisturl.rfind('/')+1]

    return baseurl, playlisturl


def get_playlist(url):
    r = requests.get(url)
    streams = []
    for line in r.text.split('\n'):
        if line.startswith('#') or not line.strip():
            continue
        streams.append(line)
    return streams


def main(url, filename):
    baseurl, playlisturl = parse_page(url)

    streams = get_playlist(playlisturl)
    streams = get_playlist(baseurl + streams[0])

    ss = StringIO()
    length = len(streams)
    for i, stream in enumerate(streams):
        start = time.time()
        r = requests.get(baseurl + stream)
        stop = time.time()
        t = stop-start
        print('%3d/%3d - %ds, %dkb, %dkb/s' % (i+1, length, t, len(r.content)/1024, (len(r.content)/1024)/t))
        ss.write(r.content)

    with open(filename, 'wb') as f:
        f.write(ss.getvalue())


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Use: {} video-url file.mp4".format(sys.argv[0]))
        sys.exit(1)

    url = sys.argv[1]
    filename = sys.argv[2]
    main(url, filename)
