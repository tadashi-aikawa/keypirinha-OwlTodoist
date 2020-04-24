import sys
import os
import re

from datetime import datetime
from datetime import timedelta

import keypirinha as kp
import keypirinha_util as kpu

"""
Googleカレンダーの予定からコピペをして..

MTG のタイトル 2月 25日 (火曜日)⋅15:00～16:00
  ↓
以下のようなTodoistタスクに変換する
  ↓
:calendar: MTG のタイトル (15:00-16:00) 2/25 @30分 
"""

non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), '')

def behindMinutes(start: str, end: str) -> int:
    """
    @param start 14:56
    @param end 15:30
    """
    delta = datetime.strptime(end, "%H:%M") - datetime.strptime(start, "%H:%M")
    return int(delta.seconds / 60)


def convert2todoist(calendar_summary: str, info) -> str:
    m = re.match(
        r"(?P<title>.+) (?P<month>\d\d?)月 (?P<day>\d\d?)日 \(.曜日\)⋅(?P<start>\d\d?:\d\d?)～(?P<end>\d\d?:\d\d?)",
        calendar_summary,
    )
    if not m:
        return None
    return f" {m['title']} ({m['start']}-{m['end']}) {m['month']}/{m['day']} @{behindMinutes(m['start'], m['end'])}分".translate(non_bmp_map)


class OwlTodoist(kp.Plugin):
    ITEMCAT_RESULT = kp.ItemCategory.USER_BASE + 1

    def on_start(self):
        self.info("Welcome to OwlTodoist!!!!!!!")

    def on_catalog(self):
        catalog = self.create_item(
            category=kp.ItemCategory.REFERENCE,
            label="OwlTodoist: Covert to todoist contents",
            short_desc="Convert to todoist",
            target="Convert your input string to todoist contents.",
            args_hint=kp.ItemArgsHint.REQUIRED,
            hit_hint=kp.ItemHitHint.IGNORE,
        )
        self.set_catalog([catalog])

    def on_suggest(self, user_input, items_chain):
        if not items_chain or not user_input:
            return

        todoist_str: str = convert2todoist(user_input, self.info)
        self.info(todoist_str)
        if not todoist_str:
            return

        suggestion = self.create_item(
            category=self.ITEMCAT_RESULT,
            label=todoist_str,
            short_desc="Copy this string",
            target=todoist_str,
            args_hint=kp.ItemArgsHint.FORBIDDEN,
            hit_hint=kp.ItemHitHint.IGNORE,
        )
        self.set_suggestions([suggestion], kp.Match.ANY, kp.Sort.NONE)

    def on_execute(self, item, action):
        self.info("execute")
        if item and item.category() == self.ITEMCAT_RESULT:
            kpu.set_clipboard(item.target())

