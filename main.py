from selenium import webdriver
import time
from bs4 import BeautifulSoup
PATH = "./chromedriver"


def current_day():
    daytime = time.strftime("%Y-%m-%d")
    daytime = daytime.split('-')
    TY = daytime[0]
    TM = daytime[1]
    TD = daytime[2]


def get_day():
    data = input("Podaj datę w formacie DD-MM-YYYY: ")
    data_s = data.split('-')
    previous_day(data)


def przestepny(year):
    return (year % 4 == 0 and year % 100 != 0) or year % 400 == 0


def previous_day(current_date):
    # Cofnięcie o jeden dzień
    current_date = current_date.split('-')
    day = current_date[0]
    month = current_date[1]
    year = current_date[2]
    day = int(day)
    day -= 1
    if day == 0:
        if int(month) in [1, 2, 4, 6, 9, 11]:
            day = 31
        if int(month) == 3:
            if przestepny(year):
                day = 29
            else:
                day = 28
        if int(month) in [5, 7, 8, 10, 12]:
            day = 30
        month = int(month)
        month -= 1
        if month == 0:
            month = 12
            year = int(year)
            year -= 1

    year = str(year)
    month = str(month)
    day = str(day)
    if int(day) < 10:
        day = '0' + day
    return day+'-'+month+'-'+year


def get_date(date):
    date = date.split('-')
    day = date[0]
    month = date[1]
    year = date[2]
    return day, month, year


def choose_month(date):
    day, month, year = get_date(date)
    driver = webdriver.Chrome(PATH)
    driver.get("https://www.nbp.pl/home.aspx?c=/ascx/archa.ascx")
    year_pom = year[2:]
    driver.find_element_by_xpath("//select[@name='rok']/option[@value=" + year_pom + "]").click()
    driver.find_element_by_xpath("//select[@name='mies']/option[@value="+month+"]").click()
    driver.find_element_by_id('ctl22_btAscxSubmit').click()
    soup = BeautifulSoup(driver.page_source, "lxml")
    tables = soup.find_all('a')
    tables.reverse()
    tables = tables[63:len(tables)-11]
    return tables


def get_href(tables, date):
    day, month, year = get_date(date)
    href = ''
    for table in tables:
        bs = table.find_all('b')
        for b in bs:
            if b.text == year+'-'+month+'-'+day:  # or b.text == year+'-'+month+'-'+day cofniecie o dzień, dwa, trzy...:
                href = table['href']
                href = href.replace("%amp;", "&")
                break
    if href == '':
        # print("Błąd! Nie znaleziono odpowiednich danych.")
        return 0
    return href


def get_rate(href, date):
    day, month, year = get_date(date)
    driver = webdriver.Chrome(PATH)
    if not href:
        return 0
    driver.get("https://www.nbp.pl"+href)
    soup = BeautifulSoup(driver.page_source, "lxml")
    table = soup.find_all('tr')
    a = 0
    rate = 0
    for row in table:
        if a:
            break
        row_td = row.find('td', class_="left")
        split = str(row_td).split('>')
        currency = ""
        if len(split) > 1:
            currency = split[1].split('<')
            currency = currency[0]
        if currency == 'dolar amerykański':  # zmienna globalna waluta #
            row_td2 = row.find_all('td', class_='right')
            row_td2 = str(row_td2[1]).split(">")
            row_td2 = row_td2[1].split('<')
            rate = row_td2[0].replace(',', '.')
            rate = float(rate)
            driver.close()
            return rate


def wypisz(rate, date, rate_date):
    day, month, year = get_date(date)
    earnings = float(input("Wprowadź zarobek w dolarach: "))
    print("Dane do ewidencji:\n")
    print("Data zamówienia: ", day + '.' + month + '.' + year)
    print("Zarobek: ", earnings)
    print("Kurs dolara z dnia poprzedzającego ("+rate_date+"): ", rate)
    print("Przychód należny: ", round(earnings * rate, 2))


if __name__ == "__main__":
    input_date = input("Podaj datę w formacie DD-MM-YYYY: ")
    previous_date = input_date
    rate = 0
    while not rate:
        previous_date = previous_day(previous_date)
        tables = choose_month(previous_date)
        href = get_href(tables, previous_date)
        rate = get_rate(href, previous_date)
    wypisz(rate, input_date, previous_date)



