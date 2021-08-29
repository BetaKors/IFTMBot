from datetime import datetime, timedelta
from dataclasses import dataclass
from discord.utils import find
from json import load


weekdays = ['segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sabado', 'domingo']


class Course:
    def __init__(self, name, data):
        self.name = name
        self.classes = self._load_classes(data)
        self.next_school_day_first_class = self._get_next_school_day_first_class(data)

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
            return self.next_school_day_first_class

        return sorted(classes, key=lambda c: c.dt)[offset]
    
    def get_next_class_dt(self):
        now = datetime.now()

        c = find(
            lambda c: c.dt > now,
            self.classes
        )

        return c.dt if c else self.next_school_day_first_class.dt 

    def get_notify_value(self):
        class1 = self.get_class()   # aula de agora
        class2 = self.get_class(1)  # próxima aula

        today_index = class1.dt.weekday()
        next_index  = class2.dt.weekday()
        m = ''

        if next_index > today_index:
            m = ' amanhã'

        elif next_index < today_index:
            m = f', segunda-feira,'

        return f'**Aula:** {class1.name}\n**Link:** {class1.url}\n**Próxima aula:** {class2.name}{m} às {class2.dt.strftime("%H:%M")}'        

    def _load_classes(self, data):
        # calendario.json descreve sabados letivos e dias que não tem aula
        with open('./calendario.json', 'r', encoding='utf-8') as f:
            c = load(f)

        now      = datetime.now()
        today    = now.weekday()
        now_date = now.strftime('%Y-%m-%d')

        if now_date in c.keys():
            if c[now_date] == 'não tem aula':
                return []
            else:
                weekday = c[now_date]
        
        else:
            weekday = weekdays[today]

            if weekday not in weekdays[:5]:
                return []

        return [
            Class(info[0], info[1], calculate_dt(time))
            for time, info in data[weekday].items() if info
        ]

    # EU NÃO SEI DAR NOME PRA MÉTODOS
    def _get_next_school_day_first_class(self, data):
        today           = datetime.now().weekday()
        index           = (today + 1) % len(weekdays[:5])
        next_school_day = weekdays[index]
        
        for time, info in data[next_school_day].items():
            if info:
                dt = calculate_dt(time) + timedelta(days=1)  # o dia estará errado mas isso não importa já que recarregamos os cursos todo dia
                return Class(info[0], info[1], dt)


@dataclass
class Class:
    name: str
    url : str
    dt  : datetime


def calculate_dt(time):
    return datetime.now().replace(
        hour=int(time[:2]),
        minute=int(time[-2:]),
        second=0,
        microsecond=0
    )


def load_courses():
    with open('./horarios.json', 'r', encoding='utf-8') as f:
        return [
            Course(name, data)
            for name, data in load(f).items()
        ]
