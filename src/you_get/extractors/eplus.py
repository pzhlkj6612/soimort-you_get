#!/usr/bin/env python

import json
import re
from urllib import request

from ..common import (
    download_url_ffmpeg,
    download_urls,
    general_m3u8_extractor,
    get_content,
    match1,
    playlist_not_supported,
    print_info,
    r1,
)
from ..extractor import VideoExtractor
from ..util import strings

__all__ = ['eplus_download', 'eplus_download_by_id']


class EPLUS(VideoExtractor):
    name = 'eplus.jp'
    stream_types = [
        {'id': '1', 'video_profile': '1280x720_2000kb/s', 'map_to': 'chapters4'},
        {'id': '2', 'video_profile': '1280x720_1200kb/s', 'map_to': 'chapters3'},
        {'id': '3', 'video_profile': '640x360_850kb/s', 'map_to': 'chapters2'},
        {'id': '4', 'video_profile': '480x270_450kb/s', 'map_to': 'chapters'},
        {'id': '5', 'video_profile': '320x180_200kb/s', 'map_to': 'lowChapters'},
    ]

    ep = 'http://vdn.apps.eplus.cn/api/getHttpVideoInfo.do?pid={}'

    def __init__(self):
        super().__init__()
        self.api_data = None

    def prepare(self, **kwargs):
        self.api_data = json.loads(get_content(self.__class__.ep.format(self.vid)))
        self.title = self.api_data['title']
        for s in self.api_data['video']:
            for st in self.__class__.stream_types:
                if st['map_to'] == s:
                    urls = self.api_data['video'][s]
                    src = [u['url'] for u in urls]
                    stream_data = dict(src=src, size=0, container='mp4', video_profile=st['video_profile'])
                    self.streams[st['id']] = stream_data


def eplus_download_by_id(rid, **kwargs):
    EPLUS().download_by_vid(rid, **kwargs)


def eplus_download(url, output_dir='.', merge=True, info_only=False,**kwargs):
    import ssl
    ssl_context = request.HTTPSHandler(
context=ssl.SSLContext(ssl.PROTOCOL_TLSv1_2))
    cookie_handler = request.HTTPCookieProcessor()
    opener = request.build_opener(ssl_context, cookie_handler)
    request.install_opener(opener)
    
    # r"https?://live\.eplus\.jp/ex/player\?ib=(?P<id>([A-Za-z\d+/=]|%2B|%2F|%3D){88})"
    content = get_content(url)
    data  = re.search(r'<script>\s*var app = (.+);\n', content).group(1)
    data_json = json.loads(data)

    playlist_url  = re.search(r'var listChannels = \["(.+)"\];\n', content).group(1)

    playlist_url =  playlist_url.replace('\\/', '/')

    m3u8_url = general_m3u8_extractor(playlist_url)

    print_info(site_info,  '?', 'm3u8', 0, m3u8_url=m3u8_url, m3u8_type='master')

    if not info_only:
        download_url_ffmpeg(m3u8_url, '?', 'ts',  output_dir=output_dir, merge=merge)

    pass

site_info = "live.eplus.jp"
download = eplus_download
download_playlist = playlist_not_supported('eplus')
