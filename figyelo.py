#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'pioo'

import nCore
import sqlite3
from os.path import exists, expanduser
import datetime

_config = nCore.readconfig()
#print _config
_dbfile = expanduser(_config['figyelo']['database'])

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
    # TODO design DB scheme
    cur.execute("CREATE TABLE figyelo (figyelo INTEGER PRIMARY KEY AUTOINCREMENT, szuro TEXT, kategoria TEXT)")
    cur.execute(
        'CREATE TABLE TorrentData ('
        'id NUMBER,'
        'nev TEXT,'
        'alt_nev TEXT,'
        'tipus TEXT,'
        'img_url TEXT, '
        'infolink TEXT,'
        'imdbrank TEXT,'
        'meret TEXT,'
        'downloaded NUMBER,'
        'seed NUMBER,'
        'leech NUMBER,'
        'date NUMBER, '
        'feltolto TEXT,'
        'status TEXT,'
        'figyelo NUMBER,'
        'PRIMARY KEY (id)')
    return


def list_figyelo():
    _cur.execute("SELECT * FROM figyelo")
    return _cur.fetchall()

def get_figyelo(figyeloid):
    _cur.execute("SELECT * FROM figyelo WHERE figyelo = ?", (figyeloid, ))
    return _cur.fetchall()


def print_figyelo():
    figyelok = list_figyelo()
    for figyelo in figyelok:
        print("%s %s\t\t%s" % (figyelo[0], figyelo[1], figyelo[2]))


def add_figyelo(szuro, kategoria="xvidser_hun"):
    _cur.execute("INSERT INTO figyelo (szuro, kategoria) "
                 "VALUES (:szuro, :kategoria)",
                 {'szuro': szuro, 'kategoria': kategoria})
    _conn.commit()


def del_figyelo(szuro):
    _cur.execute("DELETE FROM figyelo WHERE szuro=:szuro", {'szuro': szuro})
    # TODO delete from TorrentData where TorrentData.figyelo = figyeloid
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


def last_torrentid_of_figyelo(figyeloid):
    _cur.execute('SELECT MAX(id) FROM TorrentData WHERE figyelo = ?', (figyeloid, ))
    row = _cur.fetchone()
    if row[0]:
        return row[0]
    else:
        return 0


def _is_id_available(torrentid):
    _cur.execute('SELECT count(id) FROM TorrentData WHERE id = ?', (torrentid, ))
    row = _cur.fetchone()
    if row[0] == 0:
        return True
    else:
        return False


def list_new_torrents(ncore, figyeloid):
    figyelo = get_figyelo(figyeloid)[0]
    lastid = last_torrentid_of_figyelo(figyeloid)
    new_torrents = []
    # TODO innen ki kellene szedni a printeket
    print '\n[*] "%s" in %s (last id: %s)' % (figyelo[1], figyelo[2], lastid)
    #print '[I] utolso ismert torrent torrent id: %s' % lastid
    for torrent in ncore.get_torrents(figyelo[1], figyelo[2]):
        #print '[I] talalt torrent id %s' % torrent['id']
        if int(torrent['id']) <= int(lastid):
            #print '[I] nincs ujabb torrent'
            break
        nCore.print_torrents([torrent])
        new_torrents.append(torrent)
        if not _is_id_available(torrent['id']):
            print '[W] duplicate torrent: %s, %s' % (torrent['id'], torrent['nev'])
    return new_torrents


def pioodownload(torrent, started=True):
    """
    uploads torrent file to a transmission instance
    """
    server_host = _config['download']['server_host']
    tc = transmissionrpc.Client(server_host)
    params = {'paused': False}
    torrent = b64encode(torrent)
    if started:
        tc.add_torrent(torrent, None, **params)
    else:
        tc.add_torrent(torrent)



def main():
    if _needs_init:
        _create_figyelo_db(_cur)

    # TODO from now on we must parse cmdline options, or move figyelo functionality into ncore_util.py
    #days = 30
    #datum = str(datetime.date.today()-datetime.timedelta(days=days))

    update_db = True
    auto_download = False

    # please replace username and password
    n1 = nCore.nCore()
    print "[I] Logged in"
    print "[I] Listing figyelo DB:"
    print_figyelo()
    print "[I] Listing search results\n"
    if update_db:
        print('[D] Auto update database is enabled')
    if auto_download:
        print('[D] Auto download of torrents is enabled')

    for figyelo in list_figyelo():
        torrents = list_new_torrents(n1, figyelo[0])
        # TODO itt kellene printelni az adatokat
        if update_db and len(torrents)>0:
            print("[I] inserting torrents into database")
            for torrent in torrents:
                if _is_id_available(torrent['id']):
                    insert_into_db(torrent, figyelo[0])
        if auto_download:
            for torrent in torrents:
                print("[D] downloading (%s) %s" % (torrent['id'], torrent['nev']))
                #pioodownload(n1.retrieve_torrent(int(torrent['id'])))
        #print

if __name__ == "__main__":
    main()