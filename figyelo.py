#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'pioo'

import nCore
import sqlite3
from os.path import exists, expanduser
import argparse
#import datetime
import transmissionrpc
from base64 import b64encode

__version__ = '0.1a'
_config = nCore.readconfig()
# print _config
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
    cur.execute('CREATE TABLE figyelo ('
                'figyelo INTEGER PRIMARY KEY AUTOINCREMENT,'
                'szuro TEXT, kategoria TEXT)')
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


def list_torrents(name, id, count):
    if name:
        query = "SELECT * FROM TorrentData " \
        "JOIN figyelo " \
        "ON TorrentData.figyelo = figyelo.figyelo " \
        "WHERE figyelo.szuro=? " \
        "ORDER BY id DESC"
        _cur.execute(query, (name,))
    elif id:
        query = "SELECT * FROM TorrentData " \
        "JOIN figyelo " \
        "ON TorrentData.figyelo = figyelo.figyelo " \
        "WHERE figyelo.figyelo=? " \
        "ORDER BY id DESC"
        _cur.execute(query, (id,))
    else:
        query = "SELECT * FROM TorrentData ORDER BY id DESC LIMIT ?"
        _cur.execute(query, (count,))
    return _cur.fetchall()


def get_figyelo(figyeloid):
    _cur.execute("SELECT * FROM figyelo WHERE figyelo = ?", (figyeloid, ))
    return _cur.fetchall()


def print_figyelo():
    figyelok = list_figyelo()
    for figyelo in figyelok:
        print("%s %s\t\t%s" % (figyelo[0], figyelo[1], figyelo[2]))


def print_torrents(name=None, id=None, count=True):
    if count is True:
        count = 40
    torrents = list_torrents(name, id, count)
    for torrent in torrents:
        print torrent[11], torrent[1], torrent[3], torrent[7], torrent[0]


def add_figyelo(szuro, kategoria="xvidser_hun"):
    _cur.execute("INSERT INTO figyelo (szuro, kategoria) "
                 "VALUES (:szuro, :kategoria) ",
                 {'szuro': szuro, 'kategoria': kategoria})
    _conn.commit()


def del_figyelo(szuro):
    _cur.execute("DELETE FROM figyelo WHERE szuro=:szuro", {'szuro': szuro})
    #TODO delete from TorrentData where TorrentData.figyelo = figyeloid
    _conn.commit()


def insert_into_db(torrent, figyelo):
    sqlstatement = 'INSERT INTO TorrentData ' \
    'VALUES(:id, :nev, :alt_nev, :tipus, :img_url, :infolink, :imdbrank, ' \
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
    _cur.execute('SELECT MAX(id) '
                 'FROM TorrentData '
                 'WHERE figyelo = ?', (figyeloid, ))
    row = _cur.fetchone()
    if row[0]:
        return row[0]
    else:
        return 0


def _is_id_available(torrentid):
    _cur.execute('SELECT count(id) '
                 'FROM TorrentData '
                 'WHERE id = ?', (torrentid, ))
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
    # print '[I] utolso ismert torrent torrent id: %s' % lastid
    for torrent in ncore.get_torrents(figyelo[1], figyelo[2]):
        # print '[I] talalt torrent id %s' % torrent['id']
        if int(torrent['id']) <= int(lastid):
            # print '[I] nincs ujabb torrent'
            break
        nCore.print_torrents([torrent])
        new_torrents.append(torrent)
        if not _is_id_available(torrent['id']):
            print '[W] duplicate torrent: %s, %s' % (
                torrent['id'], torrent['nev'])
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


def run():
    # TODO ezt itten configbol vagy parameterbol kell szedni
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
        if update_db and len(torrents) > 0:
            print("[I] inserting torrents into database")
            for torrent in torrents:
                if _is_id_available(torrent['id']):
                    insert_into_db(torrent, figyelo[0])
        if auto_download:
            for torrent in torrents:
                print("[D] downloading (%s) %s" % (
                    torrent['id'], torrent['nev']))
                # pioodownload(n1.retrieve_torrent(int(torrent['id'])))


def parse_args():
    """
    Argument parsing as usual.
    Hence this is a command line application this def is the
    interface.
    """
    description = "nCore figyelo"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--version', action="version", version=__version__)

    task_group = parser.add_argument_group('foo1')
    task_group.add_argument('-a', '--add',
                            dest="add_figyelo",
                            metavar="ADD",
                            nargs="*",
                            help="add new figyelo to db")
    task_group.add_argument('-d', '--delete',
                            dest="delete_figyelo",
                            metavar="DELETEID",
                            help="remove a figyelo")
    task_group.add_argument('-l', '--list',
                            dest='list_figyelo',
                            nargs='?',
                            const=True,
                            help='list figyelo')

    table_group = parser.add_argument_group('bar1')
    table_group.add_argument('-r', '--run',
                             dest="update_figyelo",
                             nargs='?',
                             const=True,
                             metavar='update_data',
                             help="update figyelo db")
    table_group.add_argument('--print-by-id',
                             dest="list_by_id",
                             nargs=1,
                             metavar="figyelo_id",
                             help="print figyelo db")
    table_group.add_argument('--print-by-name',
                             dest="list_by_name",
                             nargs=1,
                             metavar="figyelo_nev",
                             help="print figyelo db")
    table_group.add_argument('--print-last',
                             dest="list_db",
                             nargs='?',
                             const=True,
                             metavar="list_data",
                             help="print figyelo db")

    main_group = parser.add_argument_group('main argument')
    main_group.add_argument('figyelo',
                            nargs="*",
                            help="update figyelo database")
    return parser, parser.parse_args()


def main():
    if _needs_init:
        _create_figyelo_db(_cur)

    # TODO from now on we must parse cmdline options,
    # or move figyelo functionality into ncore_util.py
    # days = 30
    # datum = str(datetime.date.today()-datetime.timedelta(days=days))

    parser, args = parse_args()
    print args
    if args.update_figyelo:
        run()
    elif args.add_figyelo:
        pass
    elif args.delete_figyelo:
        pass
    elif args.list_figyelo:
        print_figyelo()
    elif args.list_by_id:
        print_torrents(id=args.list_by_id[0])
    elif args.list_by_name:
        print_torrents(name=args.list_by_name[0])
    elif args.list_db:
        print_torrents(count=args.list_db)
    elif args.figyelo:
        pass
    else:
        # parameter nelkul
        run()


if __name__ == "__main__":
    main()
