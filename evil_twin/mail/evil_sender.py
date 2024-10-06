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
    password = "bolgragtofyqnmho"
    email = "exe.dumper@yandex.ru"

    with smtplib.SMTP_SSL("smtp.yandex.ru") as server:
        server.login(email, password)
        server.sendmail(email, TO, msg.as_string())


def create_mail(rec, sen, subj, path):
    msg = MIMEMultipart("alternative")
    msg["From"] = formataddr((str(Header(sen, 'utf-8')), "exe.dumper@yandex.ru"))
    msg["To"] = rec
    msg["Subject"] = subj

    google_pixel_id = "G-V1FEE03L5L"

    user, mail_domain = rec.split("@")

    html = open(path).read()
    html = html.replace("utm_medium=email", f"utm_medium={mail_domain}")
    html = bs(html, "html.parser")

    with open("styles.css", "r") as css_file:
        styles = css_file.read()

    style_tag = html.new_tag("style")
    style_tag.string = styles
    html.head.append(style_tag)

    subj_formatted = subj.replace(" ", "%")
    tracking_pixel_url = f"https://www.google-analytics.com/collect?v=1&tid={google_pixel_id}&cid={user}&t=event&ec=emails&ea=open&dt={subj_formatted}"
    tracking_pixel = f'<img src="{tracking_pixel_url}">'

    html.body.append(bs(tracking_pixel, "html.parser"))

    html.prettify(formatter="html")

    now = datetime.now() - timedelta(hours=3)
    if path == 'evil_mail.html':
        if now.time() > datetime.strptime("03:00", "%H:%M").time():
            now += timedelta(days=1)
        now = now.strftime("%-d %b")
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
    parser.add_argument('-t', '--subject', type=str, default="")
    parser.add_argument('-f', '--html_file_path', type=str, choices=['evil_mail.html', 'evil_mail_proto.html'])

    args = parser.parse_args()
    mess = create_mail(args.recipient, args.sender, args.subject, args.html_file_path)
    send_mail(args.recipient, mess)

