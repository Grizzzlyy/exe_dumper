#!/usr/bin/env python

import argparse
import smtplib
from datetime import datetime, timedelta
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

from bs4 import BeautifulSoup as bs


def send_mail(TO, msg):
    password = "trwfdogydawefhff"
    email = "exe.dumper@yandex.ru"

    with smtplib.SMTP_SSL("smtp.yandex.ru") as server:
        server.login(email, password)
        server.sendmail(email, TO, msg.as_string())


def create_mail(rec, sen, subj, path):
    msg = MIMEMultipart("alternative")
    msg["From"] = formataddr((str(Header(sen, 'utf-8')), "exe.dumper@yandex.ru"))
    msg["To"] = rec
    msg["Subject"] = subj

    html = open(path).read()
    html = bs(html, "html.parser")
    html.prettify(formatter="html")

    with open("styles.css", "r") as css_file:
        styles = css_file.read()

    style_tag = html.new_tag("style")
    style_tag.string = styles
    html.head.append(style_tag)

    now = datetime.now() - timedelta(hours=3)
    if path == 'evil_mail.html':
        if now.time() > datetime.strptime("03:00", "%H:%M").time():
            now += timedelta(days=1)
        now = now.strftime("%-d %B")
    elif path == 'evil_mail_proto.html':
        now -= timedelta(hours=1, minutes=13)
        now = now.strftime("%-d %b, %H:%M")

    html.strong.string.replace_with(now)

    html_part = MIMEText(html, "html")
    msg.attach(html_part)

    return msg


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evil mail sender")
    parser.add_argument('-r', '--recipient', type=str)
    parser.add_argument('-s', '--sender', type=str)
    parser.add_argument('-t', '--subject', type=str)
    parser.add_argument('-f', '--html_file_path', type=str, choices=['evil_mail.html', 'evil_mail_proto.html'])

    args = parser.parse_args()
    mess = create_mail(args.recipient, args.sender, args.subject, args.html_file_path)
    send_mail(args.recipient, mess)
