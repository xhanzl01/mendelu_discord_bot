import urllib.request
from datetime import date
import logging
from bs4 import BeautifulSoup as Bs


class Student:
    def __init__(self, login, uid, year_of_studies, program, type_of_studies):
        self.login = login
        self.uid = uid
        self.year_of_studies = year_of_studies
        self.program = program
        self.type_of_studies = type_of_studies

    def is_valid_student(self):
        req = urllib.request.Request(
            "https://is.mendelu.cz/karty/platnost.pl?cislo=" + str(self.uid) + ";datum="
            + date.strftime(date.today(), "%d.%m.%Y") + ";lang=cz",
            data=None,
            headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
                          'application/signed-exchange;v=b3;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'cs-CZ,cs;q=0.9,en;q=0.8',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'Content-Length': '47',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Cookie': 'MENDELUNavratka=1%2B7AeSQ6WepMPHhffIBLPAdo7kwV7kd7he2jzjTUAH5w; '
                          'MENDELUPrihlaska=VldvkO7hQ9Re8%2FZRcfoANQUv1yt5Y9f2J1dSvKBwbFUQ; '
                          '_ga=GA1.2.1370431451.1573144909; '
                          'UISAuth=%2ByR4vTleRuzi%2B4ZxSsmR2Qi6j%2BJzh4v97E%2FAkHnmES3A',
                'Host': 'is.mendelu.cz',
                'Origin': 'https://is.mendelu.cz',
                'Referer': 'https://is.mendelu.cz/karty/platnost.pl',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/35.0.1916.47 Safari/537.36 '
            }
        )
        fid = urllib.request.urlopen(req)
        webpage = fid.read().decode()
        soup = Bs(webpage, 'html.parser')
        try:
            if soup.find("tr", class_="sudy").find_all("td")[1].get_text() == "ano":
                return True
            return False
        except Exception as ex:
            logging.error("Error with uid: " + self.uid + " " + str(ex))
            return False
