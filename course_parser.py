import utils

from datetime import datetime, timedelta
from dataclasses import dataclass
from discord.utils import find
from json import load


class Course:
    def __init__(self, name, data):
        self.name = name
        self.classes = self._load_today_classes(data)
        # "tomorrow" não é necessariamente amanhã, mas sim uma forma mais fácil de se referir ao próximo dia de aula
        self.tomorrow_classes = self._load_tomorrow_classes(data)

    def __str__(self):
        classes = ', '.join(c.name for c in self.classes)
        return f'{self.name} - [{classes}]'

    def get_class(self, offset=0):
        now = datetime.now()
        classes = [
            c
            for c in self.classes
            if c.dt >= now - timedelta(seconds=10)  # tirando 10s pra evitar um bug
        ]

        if offset >= len(classes):
            return self.tomorrow_classes[0]

        return sorted(classes, key=lambda c: c.dt)[offset]

    def get_next_class_dt(self):
        now = datetime.now()

        c = find(
            lambda c: c.dt > now,
            self.classes
        )

        if not c:
            if self.tomorrow_classes:
                c = self.tomorrow_classes[0]
            else:
                return now + timedelta(days=2)

        return c.dt

    def get_notify_value(self):
        class1 = self.get_class()   # aula de agora
        class2 = self.get_class(1)  # próxima aula

        m = utils.dt_as_formatted_str(class2.dt).lower()

        return f'**Aula:** {class1.name}\n**Link:** {class1.url}\n**Próxima aula:** {class2.name} {m}'        

    def _load_today_classes(self, data):
        calendar = self._load_calendar()

        today    = datetime.today()
        str_date = today.strftime('%Y-%m-%d')

        if str_date in calendar.keys():
            if calendar[str_date] == 'não tem aula':
                return []
            else:
                weekday = calendar[str_date]

        else:
            weekday = utils.dt_to_weekday(today)

            if weekday not in utils.weekdays[:5]:
                return []

        return [
            Class(info[0], info[1], self._calculate_class_dt(datetime.now(), time))
            for time, info in data[weekday].items() if info
        ]

    def _load_tomorrow_classes(self, data):
        dt, weekday = self._find_tomorrow_dt_weekday()

        return [
            Class(info[0], info[1], self._calculate_class_dt(dt, time))
            for time, info in data[weekday].items() if info
        ]

    def _find_tomorrow_dt_weekday(self):
        calendar = self._load_calendar()

        today      = datetime.today()
        current_dt = today + timedelta(days=1)

        while True:
            str_date = current_dt.strftime('%Y-%m-%d')

            if str_date in calendar.keys():
                if calendar[str_date] != 'não tem aula':
                    return current_dt, calendar[str_date]

            else:
                weekday = utils.dt_to_weekday(current_dt)
                if weekday in utils.weekdays[:5]:
                    return current_dt, weekday

            current_dt += timedelta(days=1)
    
    def _load_calendar(self):
        # calendario.json descreve sabados letivos e dias que não tem aula
        with open('./calendario.json', 'r', encoding='utf-8') as f:
            return load(f)
    
    def _calculate_class_dt(self, dt, time):
        return dt.replace(
            hour=int(time[:2]),
            minute=int(time[-2:]),
            second=0,
            microsecond=0
        )


@dataclass
class Class:
    name: str
    url : str
    dt  : datetime


def load_courses():
    with open('./horarios.json', 'r', encoding='utf-8') as f:
        return [
            Course(name, data)
            for name, data in load(f).items()
        ]
