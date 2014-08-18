#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import cookielib
from bs4 import BeautifulSoup
import ConfigParser
from os.path import expanduser
import transmissionrpc
from base64 import b64encode


def _extract_torrent_data(tag):
    """
    egy ncore box_torrent tagbol kiolvassa es visszaadja az adatokat
    :rtype : dictionary of id, nev, meret, download, seed, leech, date, status
    :param tag: a BeautifulSoup4 tag
    """
    torrent = {'id': int(tag.find_all('a')[1]['href'].split('id=')[1]),
               'nev': tag.find_all('a')[1]['title'],
               #'alt_nev': tag.find_all('span')[0]['title'],
               'tipus': tag.find('a')['href'].split('=')[1],
               #'img_url': tag.find('div', {'class': 'infobar'}).find('img')['onmouseover'].split("'")[1],
               # 'infolink': tag.find('a', {'class': 'infolink'})['href'].split('?')[1],
               # 'imdbrank': tag.find('a', {'class': 'infolink'}).text.split(':')[1].replace(']', '').strip(),
               'meret': tag.find('div', {'class': 'box_meret2'}).text,
               'downloaded': int(tag.find('div', {'class': 'box_d2'}).text),
               'seed': int(tag.find('div', {'class': 'box_s2'}).text),
               'leech': int(tag.find('div', {'class': 'box_l2'}).text),
               'date': tag.find('div', {'class': 'box_feltoltve2'}).contents[0],
               'feltolto': tag.find('div', {'class': 'box_feltolto2'}).text,
               'status': False}

    if tag.find('div', {'class': 'torrent_ok'}):
        torrent['status'] = True
    # TODO: torrent['alt_nev']
    torrent['alt_nev'] = ""
    # TODO: torrent['img_url']
    torrent['img_url'] = ""
    # TODO: torrent['infolink']
    torrent['infolink'] = ""
    # TODO: torrent['imdbrank']
    torrent['imdbrank'] = ""
    # TODO: tag-ek lekerese, izgi, mert ez masik oldalon van
    return torrent


def _get_torrent_tag_from_htmldata(html):
    """
    namost ez egy html oldalt fog kapni, amit szepen feldolgoz
    :rtype : array of dictonary of id, nev, meret, downloaded, seed, leech, date, status
    :param html: search page (html) as a string
    """
    soup = BeautifulSoup(html)
    talalatok = soup.find_all('div', {'class': 'box_torrent'})
    for talalat in talalatok:
        yield _extract_torrent_data(talalat)


def _count_pages(html):
    """
    internal function
    :rtype : number of pages in a search (max 10)
    :param html: search page html as a string
    """
    soup = BeautifulSoup(html)
    bottom = soup.find('div', id='pager_bottom')
    try:
        if len(bottom.find_all('a')) > 0:
            page_nr = int(str(bottom.find_all('a')[-1]['href']).split('oldal=')[1].split('&')[0])
            return page_nr
        else:
            return 1
    except AttributeError:
        return 0

def readconfig(configfile='~/.ncore/config'):
    config = ConfigParser.ConfigParser()
    config.read(expanduser(configfile))
    d = dict(config._sections)
    for k in d:
        d[k] = dict(config._defaults, **d[k])
        d[k].pop('__name__', None)
    return d


class nCore:
    """
    Designed to connect to ncore.cc and perform search and download torrent
    operations. This module is in pre-release status, without version info.
    Example usage:
    n = nCore()
    list = n.search('my favorite show', 'xvidser_hun')
    print_torrents(list)
    
    Optionally:
    torrentfile = n.retrieve_torrent('id')
    pioodownload(torrentfile)
    """

    def __init__(self, configfile='~/.ncore/config'):
        """
        missing doc!!!
        # TODO doc!
        :param username: login credentials
        :param password: login credentials
        :param useragent: optional web browser user agent string
        """
        self.configuration = readconfig(configfile)
        self.username = self.configuration['auth']['username']
        self.password = self.configuration['auth']['password']
        self.useragent = self.configuration['auth']['useragent']
        self.url_base = 'https://ncore.cc'
        self.url_login = self.url_base + '/login.php'
        self.url_torrents = self.url_base + '/torrents.php'
        self.login_data = urllib.urlencode({'nev': self.username, 'pass': self.password})
        self.cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))

        self.opener.addheaders = [('User-Agent', self.useragent)]
        self.opener.open(self.url_login, self.login_data)

    def retrieve_torrent(self, torrent_id):
        """
        downloads a torrent file by torrent id
        :rtype : torrent file as a string
        :param torrent_id: torrent id as integer
        """
        url = self.url_torrents + "?action=download&id=" + str(torrent_id)
        torrent_data = self.opener.open(url).read()
        return torrent_data

    def search_raw(self, mire, tipus="xvidser_hun", tags="", oldalszam=1):
        """
        search function.
        :rtype : html as a string
        :param mire: search string
        :param tipus: search category
        :param tags: tags
        :param oldalszam: number of page to return
        """
        url = self.url_torrents
        if oldalszam > 1:
            url += '?oldal=' + str(oldalszam)
        search_data = urllib.urlencode(
            {'mire': mire, 'miben': 'name', 'tipus': tipus, 'submit.x': '6', 'submit.y': '18', 'tags': tags})
        resp = self.opener.open(url, search_data)
        return resp.read()

    def get_torrents(self, mire, tipus="xvidser_hun", tags=""):
        """
        generator
        tipusok: xvid_hun, xvid, hd, hd_hun, xvidser_hun, xvidser,
             hdser_hun, hdser, mp3, mp3_en, iso, misc, mobil,
             ebook, ebook_hun
        @return: torrents array of dictionary
        """
        htmldata = self.search_raw(mire, tipus, tags)
        oldalszam = _count_pages(htmldata)
        i = 1
        while i <= oldalszam:
            for torrent in _get_torrent_tag_from_htmldata(htmldata):
                yield torrent
            i += 1
            htmldata = self.search_raw(mire, tipus, tags, i)

    def search(self, mire, tipus="xvidser_hun", tags=""):
        torrents = []
        for torrent in self.get_torrents(mire, tipus, tags):
            torrents.append(torrent)
        return torrents


def print_torrents(torrents):
    """
    print formatted torrent list
    # TODO missing doc
    :param torrents: a torrents object produced by search function
    """
    for i in range(len(torrents)):
        print("%(date)s|%(nev)s, (%(meret)s), Dwn: %(downloaded)s, S/L: %(seed)s/%(leech)s, ID: %(id)s" % torrents[i])


def main():
    n1 = nCore('myusername', 'mypassword')
    # torrents = n1.search('game of thrones', 'xvidser')
    # print_torrents(torrents)
    print_torrents(n1.search('game of thrones', 'xvidser'))


if __name__ == '__main__':
    main()
