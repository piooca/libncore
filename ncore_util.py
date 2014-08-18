#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from nCore import *
from os.path import expanduser
import ConfigParser

__author__ = 'pioo'

def usage():
    print '[*] Usage: search:'
    print '[+] s: game of thrones[, xvidser, vigjatek horror]'
    print '[+] download:'
    print '[+] d: torrentid'
    print '[+] exit: exit'
    print '[+] help: this help text'
    print '[+] categories: categories, second parameter'
    print ''

def categories():
    print '[*] Categories list:'
    print '[+] Film: xvid_hun, xvid, dvd_hun, dvd, dvd9_hun, dvd9, hd_hun, hd'
    print '[+] Sorozat: xvidser_hun, xvidser, dvdser_hun, dvdser, hdser_hun, hdser'
    print '[+] Zene: mp3_hun, mp3, lossless_hun, lossless, clip'
    print '[+] XXX: xxx_xvid, xxx_dvd, imageset, xxx_hd'
    print '[+] Jatek: game_iso, game_rip, console'
    print '[+] Program: iso, misc, mobil '
    print '[+] Konyv: ebook_hun, ebook'
    print ''

def pioodownload(torrent, started=True):
    """
    uploads torrent file to a transmission instance
    """
    server_host = config['download']['server_host']
    tc = transmissionrpc.Client(server_host)
    params = {'paused': False}
    torrent = b64encode(torrent)
    if started:
        tc.add_torrent(torrent, None, **params)
    else:
        tc.add_torrent(torrent)

def readconfig():
    config = ConfigParser.ConfigParser()
    config.read(expanduser('~/.ncore/config'))
    d = dict(config._sections)
    for k in d:
        d[k] = dict(config._defaults, **d[k])
        d[k].pop('__name__', None)
    return d

def torrent_search(mit, miben, tags):
    print 'searching for "%s" in "%s" (tags: %s)' % (mit, miben, tags)
    print_torrents(n.search(mit, miben, tags))

print '[*] Starting nCore shell v0.1 at ' + str(datetime.datetime.now())
config = readconfig()
# print config
username = config['auth']['username']
password = config['auth']['password']
default_category = config['search']['category']
default_tags = config['search']['tags']

n = nCore(username, password)
print '[+] Successfully logged in.'
usage()
#categories()
nCoreCMD = ''
while nCoreCMD != 'exit':
    nCoreCMD = raw_input('nCore> ')
    nCoreCMD = nCoreCMD.strip()

    if nCoreCMD[0:2] == 'd:':
        print 'downloading %s' % nCoreCMD
        pioodownload(n.retrieve_torrent(int(nCoreCMD.replace('d:', '', 1).strip())))
    elif nCoreCMD[0:2] == 's:':
        search_string = nCoreCMD.replace('s:', '', 1).lstrip().split(',')
        if len(search_string) == 1:
            mit = search_string[0].strip()
            miben = default_category
            tags = default_tags
            torrent_search(mit, default_category, default_tags)
        elif len(search_string) == 2:
            mit = search_string[0].strip()
            miben = search_string[1].strip()
            torrent_search(mit, miben, default_tags)
        elif len(search_string) == 3:
            mit = search_string[0].strip()
            miben = search_string[1].strip()
            tags = search_string[2].strip()
            torrent_search(mit, miben, tags)
    elif nCoreCMD.isdigit():
        print 'downloading %s' % nCoreCMD
        pioodownload(n.retrieve_torrent(int(nCoreCMD.strip())))

    elif nCoreCMD.replace(' ', '1').isalnum():
        if nCoreCMD.lower() == 'help':
            usage()
        elif nCoreCMD.lower() == 'categories':
            categories()
        elif nCoreCMD.lower() == 'exit':
            exit()
        else:
            torrent_search(nCoreCMD, default_category, default_tags)

