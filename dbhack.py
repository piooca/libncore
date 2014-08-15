#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'pioo'

import nCore
import sqlite3
from os.path import exists


_dbfile = "ncore.db"  # TODO find dbfile's place
_memdb = ":memory:"

if not exists(_dbfile):
    _needs_init = True
else:
    _needs_init = False
_conn = sqlite3.connect(_memdb)
_cur = _conn.cursor()


def insert_into_db(torrent):
    sqlstatement = 'INSERT INTO TorrentData VALUES(:id, :nev, :alt_nev, :tipus, :img_url, :infolink, :imdbrank, ' \
                   ':meret, :downloaded, :seed, :leech, :date, :feltolto, :status)'
    _cur.execute(sqlstatement, {
        'id': torrent['id'],
        'nev': torrent['nev'],
        'alt_nev': torrent['alt_nev'],
        'tipus': torrent['tipus'],
        'img_url': torrent['img_url'],
        'infolink': torrent['infolink'],
        'imdbrank': torrent['imdbrank'],
        'meret': torrent['meret'],
        'downloaded': torrent['downloaded'],
        'seed': torrent['seed'],
        'leech': torrent['leech'],
        'date': torrent['date'],
        'feltolto': torrent['feltolto'],
        'status': torrent['status']})
    _conn.commit()
    return


def _create_torrent_db(cur):
    cur.execute("CREATE TABLE Params (ParamKey TEXT PRIMARY KEY, ParamValue TEXT)")
    cur.execute(
        'CREATE TABLE TorrentData (id TEXT PRIMARY KEY, nev TEXT, alt_nev TEXT, tipus TEXT, img_url TEXT, '
        'infolink TEXT, imdbrank TEXT, meret TEXT, downloaded NUMBER, seed NUMBER, leech NUMBER, date NUMBER, '
        'feltolto TEXT, status TEXT)')
    cur.execute("CREATE TABLE Tagek (TagID NUMBER PRIMARY KEY, Tag TEXT)")
    cur.execute("CREATE TABLE TorrentTags (TorrentID NUMBER, TagID NUMBER)")
    return


def _is_id_available(torrentid):
    _cur.execute('SELECT count(id) FROM TorrentData WHERE id = ?', (torrentid, ))
    row = _cur.fetchone()
    if row[0] == 0:
        return True
    else:
        return False


_create_torrent_db(_cur)
# replace username and password
n1 = nCore.nCore('username', 'password')
print "[+] Logged in"
i = 0
for torrent in n1.get_torrents('', 'xvid_hun'):
    #if i >= 33:
    #    break
    if _is_id_available(torrent['id']):
        i += 1
        print "[+]", i, torrent['id'], torrent['nev']
        insert_into_db(torrent)

print "[+] Dumping memory database into file"
query = "".join(line for line in _conn.iterdump())
new_db = sqlite3.connect(_dbfile)
new_db.executescript(query)
