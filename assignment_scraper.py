import assignment

from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup
from json import load


def _login(driver, cpf):
    driver.get('https://ava.upt.iftm.edu.br/login/index.php')
    driver.find_element_by_id('username').send_keys(f'{cpf}')
    driver.find_element_by_id('password').send_keys(f'Upt@{cpf}')
    driver.find_element_by_id('loginbtn').click()


def _get_assignments(driver):
    driver.get('https://ava.upt.iftm.edu.br/calendar/view.php')  # aba "eventos" do ava
    soup = BeautifulSoup(driver.page_source.encode('utf-8'), features='lxml')
    return [
        assignment.Assignment(str(div))
        for div in soup.find_all('div', class_='event mt-3')
    ]


def _get_cpfs():
    with open('./cpfs.json', 'r') as f:
        return load(f)


def load_assignment_groups():
    options = Options()
    options.add_argument('--headless')  # esconde a janela do browser
    options.add_experimental_option('excludeSwitches', ['enable-logging'])  # suprimindo uma mensagem que normalmente aparece no console
    
    driver = webdriver.Chrome(
        executable_path='C:\Program Files (x86)\chromedriver.exe',
        options=options
    )
    
    groups = []
    cpfs = _get_cpfs()

    try:
        for course, cpf in cpfs.items():
            _login(driver, cpf)
            
            assignments = _get_assignments(driver)

            groups.append(
                assignment.AssignmentGroup(course, assignments)
            )

    except:
        raise

    finally: # tendo certeza que driver.quit() é chamado * toda vez *
        driver.quit()
        return groups
