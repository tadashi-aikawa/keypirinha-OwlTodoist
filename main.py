import os
import re

from datetime import datetime
from datetime import timedelta

import keypirinha as kp
import keypirinha_util as kpu

"""
時刻表データ転送高速化の今後の予定決め
Dec 12 from 4:00 PM to 4:30 PM at 2F

:dancer:【確保】
Tomorrow from 11:30 AM to 12:00 PM
"""


def convert24h(timestr: str) -> str:
    """ 2:00 PM => 14:00
        2:00 AM => 2:00
    """
    return datetime.strptime(timestr, "%I:%M %p").strftime("%H:%M")


def behindMinutes(start: str, end: str) -> int:
    """
    @param start 14:56 PM
    @param end 15:30 PM
    """
    delta = datetime.strptime(end, "%I:%M %p") - \
        datetime.strptime(start, "%I:%M %p")
    return int(delta.seconds / 60)


def convert_yy_mm_dd(datestr: str) -> str:
    """ If today is 2018-12-10
        Dec 12 => 2018-12-12
        Jan 7  => 2019-01-07
    """
    if datestr == "Today":
        d = datetime.today()
    elif datestr == "Tomorrow":
        d = datetime.today() + timedelta(days=1)
    else:
        d = datetime.strptime(f'{datestr} {datetime.now().year}', "%b %d %Y")
        if d < datetime.now():
            d = datetime(d.year + 1, d.month, d.day)
    return d.strftime("%Y-%m-%d")


def convert2todoist(calendar_summary: str) -> str:
    m = re.match(
        r'(?P<title>.+) (?P<date>((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d\d?|Today|Tomorrow)) from (?P<start>\d\d?:\d\d? [AP]M) to (?P<end>\d\d?:\d\d? [AP]M).*',
        calendar_summary,
    )
    if not m:
        return None
    return f":calendar: {m['title']} ({convert24h(m['start'])}-{convert24h(m['end'])}) {convert_yy_mm_dd(m['date'])} @{behindMinutes(m['start'], m['end'])}分"


class OwlTodoist(kp.Plugin):
    ITEMCAT_RESULT = kp.ItemCategory.USER_BASE + 1

    def on_start(self):
        self.info("Welcome to OwlTodoist!!")

    def on_catalog(self):
        catalog = self.create_item(
            category=kp.ItemCategory.REFERENCE,
            label='OwlTodoist: Covert to todoist contents',
            short_desc='Convert to todoist',
            target='Convert your input string to todoist contents.',
            args_hint=kp.ItemArgsHint.REQUIRED,
            hit_hint=kp.ItemHitHint.IGNORE
        )
        self.set_catalog([catalog])

    def on_suggest(self, user_input, items_chain):
        if not items_chain or not user_input:
            return

        todoist_str: str = convert2todoist(user_input)
        if not todoist_str:
            return

        suggestion = self.create_item(
            category=self.ITEMCAT_RESULT,
            label=todoist_str,
            short_desc='Copy this string',
            target=todoist_str,
            args_hint=kp.ItemArgsHint.FORBIDDEN,
            hit_hint=kp.ItemHitHint.IGNORE
        )
        self.set_suggestions([suggestion], kp.Match.ANY, kp.Sort.NONE)

    def on_execute(self, item, action):
        self.info('execute')
        if item and item.category() == self.ITEMCAT_RESULT:
            kpu.set_clipboard(item.target())
