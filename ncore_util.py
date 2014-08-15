#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from nCore import *

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

print '[*] Starting nCore shell v0.1 at ' + str(datetime.datetime.now())

# replace username and password
n = nCore('username', 'password')
print '[+] Successfully logged in.'
usage()
categories()
nCoreCMD = ''
while nCoreCMD != 'exit':
    nCoreCMD = raw_input('nCore> ')
    if 's:' in nCoreCMD:
        search_string = nCoreCMD.replace('s:', '', 1).lstrip().split(',')
        if len(search_string) == 1:
            mit = search_string[0].strip()
            print 'searching for "' + mit +'"'
            print_torrents(n.search(mit))
        elif len(search_string) == 2:
            mit = search_string[0].strip()
            miben = search_string[1].strip()
            print 'searching for "' + mit + '" in "' + miben + '"'
            print_torrents(n.search(mit, miben))
        elif len(search_string) == 3:
            mit = search_string[0].strip()
            miben = search_string[1].strip()
            tags = search_string[2].strip()
            print 'searching for "' + mit + '" in "' + miben + '" tags: "' + tags + '"'
            print_torrents(n.search(mit, miben, tags))
    elif 'd:' in nCoreCMD:
        pioodownload(n.retrieve_torrent(int(nCoreCMD.replace('d:', '', 1).strip())))
    elif 'help' in nCoreCMD.lower():
        usage()
    elif 'categories' in nCoreCMD.lower():
        categories()
    elif 'exit!' in nCoreCMD.lower():
        exit()
