# -*-coding:utf-8 -*-
'''
Created on 2013-10-15

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
'''

import threading
import time
import redis

from django.conf import settings

from models import EmailWaiting
from common.log_utils import set_log


conn = redis.Redis()
senders = []


class EmailSendingThread(threading.Thread):
    """
    This thread is to send emails gotten from queue.
    """
    def __init__(self, block=True):
        threading.Thread.__init__(self)
        self.block = block
        self.is_working = False

    def run(self):
        set_log('info', 'Email sending thread ({0}) started.'.format(self))
        while True:
            try:
                if self.block:
                    eid = conn.brpop(settings.EMAIL_PRESENDING_POOL)[1]
                else:
                    eid = conn.rpop(settings.EMAIL_PRESENDING_POOL)
                    if not eid:
                        senders.remove(self)
                        break
                self.is_working = True
                sending_attempt_count = 0

                email = EmailWaiting.objects.get(id=eid)
                while True:
                    if not email.send() and sending_attempt_count <= 3:
                        sending_attempt_count += 1
                        time.sleep(settings.THREAD_SEND_FAILED_SLEEPTIME)
                        conn.lpush(settings.EMAIL_PRESENDING_POOL, eid)
                        continue
                    break
            except Exception, e:
                set_log('error', e)
                time.sleep(settings.THREAD_EXCEPTION_SLEEPTIME)
                if hasattr(self, 'eid'):
                    conn.lpush(settings.EMAIL_PRESENDING_POOL, eid)
            finally:
                self.is_working = False


class EmailManagingThread(threading.Thread):
    """
    This thread is to generate threads for email sending and
    load all emails need to be sent to the queue.
    """

    def __init__(self):
        threading.Thread.__init__(self)

    def init_sending_threads(self, num):
        for i in range(num):
            new_thread = EmailSendingThread()
            new_thread.setDaemon(True)
            senders.append(new_thread)
            new_thread.start()

    def init_tmp_threads(self, num):
        for i in range(num):
            new_thread = EmailSendingThread(False)
            senders.append(new_thread)
            new_thread.start()

    def run(self):
        set_log('info', 'Email sending manager thead started.')
        self.init_sending_threads(settings.MIN_THREADS_NUM)

        while True:
            try:
                c_mails = conn.llen(settings.EMAIL_PRESENDING_POOL)
                #if not reduce(lambda x, y: x or y, [item.is_working for item in senders]:
                if not c_mails:
                    mail_ids = EmailWaiting.objects.get_unconfirmed_email_ids()
                    if mail_ids:
                        conn.lpush(settings.EMAIL_PRESENDING_POOL, *mail_ids)

                c_threads = len(senders)
                if c_threads < c_mails / 10 and c_threads < settings.MAX_THREADS_NUM:
                    self.init_tmp_threads(min(c_mails / 10, settings.MAX_THREADS_NUM))

                set_log('debug', '{0} mail sending threads are working now.'.format(len(senders)))
                time.sleep(settings.MANAGER_SCANNING_SLEEPTIME)
            except Exception, e:
                set_log('error', str(e))
                time.sleep(settings.MANAGER_EXCEPTION_SLEEPTIME)


import socket
passs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def run_email_sending_thread():
    """
    start email sending thread.
    Try to bind a port to check whether the thread had been started.
    """

    try:
        passs.bind(("127.0.0.1", 12121))
        new_thread = EmailManagingThread()
        new_thread.setDaemon(True)
        new_thread.start()
    except:
        pass
