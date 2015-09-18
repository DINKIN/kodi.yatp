# coding: utf-8
# Module: timers
# Created on: 14.07.2015
# Author: Roman Miroshnychenko aka Roman V.M. (romanvm@yandex.ua)
# Licence: GPL v.3: http://www.gnu.org/copyleft/gpl.html

from __future__ import division
import threading
import time
from datetime import datetime, timedelta
from addon import Addon

_addon = Addon()


class Timer(object):
    """
    Timer class

    Implements a repeating timer to call some function in regular intervals.
    """
    def __init__(self, interval, func, *args, **kwargs):
        """
        Class constructor

        @param interval: int - timer interval in seconds
        @param func: a callable function
        @param args: function positional args
        @param kwargs: function kwargs
        """
        self._interval = interval
        self._func = func
        self._abort_flag = threading.Event()
        self._thread = threading.Thread(target=self._runner, args=args, kwargs=kwargs)
        self._thread.daemon = True

    def _runner(self, *args, **kwargs):
        """
        Timed function runner

        @retrun:
        """
        timestamp = time.time()
        while not self._abort_flag.is_set():
            if time.time() - timestamp >= self._interval:
                self._func(*args, **kwargs)
                timestamp = time.time()
            time.sleep(0.1)

    def start(self):
        """
        Timer start

        @retrun:
        """
        self._abort_flag.clear()
        self._thread.start()

    def abort(self):
        """
        Abort timer

        @retrun:
        """
        self._abort_flag.set()
        try:
            self._thread.join()
        except RuntimeError:
            pass


def check_seeding_limits(torrenter, max_ratio, max_time, expired_action, delete_expired):
    """
    Check seding limits

    @param torrenter:
    @param max_ratio:
    @param max_time:
    @retrun:
    """
    for torrent in torrenter.get_all_torrents_info():
        try:
            ratio = torrent['total_upload'] / torrent['total_download']
        except ZeroDivisionError:
            ratio = 0
        if max_ratio and torrent['state'] == 'seeding' and ratio >= max_ratio:
            torrenter.pause_torrent(torrent['info_hash'])
        try:
            if (max_time and
                (datetime.now() - datetime.strptime(torrent['completed_time'], '%Y-%m-%d %H:%M:%S') >=
                     timedelta(hours=max_time))):
                if expired_action == 'pause' and torrent['state'] == 'seeding':
                    torrenter.pause_torrent(torrent['info_hash'])
                elif expired_action == 'delete' and torrent['state'] in ('seeding', 'paused'):
                    torrenter.remove_torrent(torrent['info_hash'], delete_expired)
        except ValueError:
            pass


def save_resume_data(torrenter):
    """
    Save torrents resume data

    @param torrenter:
    @retrun:
    """
    torrenter.save_all_resume_data()


def log_torrents(torrenter):
    """
    Log torrents in the torrent session

    @param torrenter:
    @return:
    """
    torrents = torrenter.get_all_torrents_info()
    _addon.log('Torrents:')
    for torrent in torrents:
        _addon.log(str(torrent))
