import utils

from dataclasses import dataclass
from discord.utils import find
from bs4 import BeautifulSoup


class Assignment:
    """Descreve uma tarefa"""
    def __init__(self, data):
        soup = BeautifulSoup(data, features='lxml')
        self.title        = self._get_title(soup)
        self.subject      = self._get_subject(soup)
        self.description  = self._get_desc(soup)
        self.dt           = self._get_dt(soup)
    
    def get_value(self, note):
        subject = f'**Matéria**: {self.subject}\n\n'
        title   = f'**Título**: {self.title}\n\n'
        desc    = f'**Descrição**: {self.description}\n\n'
        date    = f'**Data de entrega**: {utils.dt_as_formatted_str(self.dt)}'

        value = subject + title + desc + date

        max_length = 1024 - abs(len(value) - len(desc))

        if len(desc) >= max_length:
            desc_too_big_note = ' [...]\n\n*A descrição dessa tarefa era longa demais então teve que ser cortada*\n\n'
            
            x = max_length - len(desc_too_big_note)

            if note:
                x -= len(note)

            desc = desc[:x] + desc_too_big_note
            
            value = subject + title + desc + date

        return value

    def _get_title(self, soup):
        title = soup.find('h3', class_='name d-inline-block').text
        title = title.replace('está marcado(a) para esta data', '')
        return title.strip()

    def _get_subject(self, soup):
        subject = find(
            lambda e: e.find('a', href=lambda h: 'course' in h) is not None,
            soup.find_all('div', class_='col-11')
        ).text

        # deixando a primeira letra de cada palavra da matéria maiúscula
        return ' '.join(
            w.capitalize() if len(w) > 1 else w
            for w in subject.split()
        ).replace('2d', '2D')  # caso especial para Programação e Animação 2D

    def _get_desc(self, soup):
        desc = soup.find('div', class_='description-content col-11')
        return desc.get_text() if desc else 'Descrição não encontrada.'

    def _get_dt(self, soup):
        # <div><a href="https://ava.upt.iftm.edu.br/calendar/view.php?view=day&amp;time=1629860340">Hoje</a>, 23:59</div> ---> 
        # 1629860340">Hoje</a>, 23:59</div> [: até "] -->
        # 1629860340 (unix time string)
        # sim, seria possível apenas usar get_text() e pegar "Hoje, 23:59" por exemplo, mas talvez ter o datetime exato é útil em outros lugares
        
        element = str(
            find(
                lambda e: e.find('a', href=lambda h: 'calendar' in h) is not None,
                soup.find_all('div', class_='col-11')
            )
        ).split('=')[-1]

        index = element.find('"')

        timestamp = element[:index]

        return utils.unix_timestamp_to_local_dt(timestamp)


@dataclass
class AssignmentGroup:
    """Descreve um curso e suas tarefas"""
    course_name: str
    assignments: list
