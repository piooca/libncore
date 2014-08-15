#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'pioo'

import nCore
import sqlite3
from os.path import exists
import datetime

_dbfile = "figyelo.db"  # TODO find dbfile's place

if not exists(_dbfile):
    _needs_init = True
else:
    _needs_init = False
_conn = sqlite3.connect(_dbfile)
_cur = _conn.cursor()


def _create_figyelo_db(cur):
    """
    Creates an empty database
    Initialises the DB on first start
    :param cur:
    :return:
    """
    # TODO desing DB scheme
    cur.execute("CREATE TABLE figyelo (figyelo INTEGER PRIMARY KEY AUTOINCREMENT, szuro TEXT, kategoria TEXT)")
    cur.execute(
        'CREATE TABLE TorrentData (id TEXT PRIMARY KEY, nev TEXT, alt_nev TEXT, tipus TEXT, img_url TEXT, '
        'infolink TEXT, imdbrank TEXT, meret TEXT, downloaded NUMBER, seed NUMBER, leech NUMBER, date NUMBER, '
        'feltolto TEXT, status TEXT, figyelo NUMBER)')
    return


def list_figyelo():
    _cur.execute("SELECT * FROM figyelo")
    return _cur.fetchall()


def print_figyelo():
    figyelok = list_figyelo()
    for figyelo in figyelok:
        print figyelo[1] + "\t\t" + figyelo[2]


def add_figyelo(szuro, kategoria=""):
    _cur.execute("INSERT INTO figyelo (szuro, kategoria) "
                 "VALUES (:szuro, :kategoria)",
                 {'szuro': szuro, 'kategoria': kategoria})
    _conn.commit()


def del_figyelo(szuro):
    _cur.execute("DELETE FROM figyelo WHERE szuro=:szuro", {'szuro': szuro})
    _conn.commit()


def insert_into_db(torrent, figyelo):
    sqlstatement = 'INSERT INTO TorrentData VALUES(:id, :nev, :alt_nev, :tipus, :img_url, :infolink, :imdbrank, ' \
                   ':meret, :downloaded, :seed, :leech, :date, :feltolto, :status, :figyelo)'
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
        'status': torrent['status'],
        'figyelo': figyelo})
    _conn.commit()
    return


def _is_id_available(torrentid):
    _cur.execute('SELECT count(id) FROM TorrentData WHERE id = ?', (torrentid, ))
    row = _cur.fetchone()
    if row[0] == 0:
        return True
    else:
        return False


def main():
    if _needs_init:
        _create_figyelo_db(_cur)

    days = 30
    datum = str(datetime.date.today()-datetime.timedelta(days=days))

    # please replace username and password
    n1 = nCore.nCore('username', 'password')
    print "[+] Logged in"
    print "[+] Listing figyelo DB:"
    print_figyelo()
    print "[+] Listing search results for last %s days:" % days
    for keres in list_figyelo():
        print "[*] kereses: \"" + keres[1] + "\" in " + keres[2]
        for torrent in n1.get_torrents(keres[1]):
            #print torrent['nev']
            if torrent['date'] < datum:
                break
            nCore.print_torrents([torrent])
        print


if __name__ == "__main__":
    main()