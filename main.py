from selenium import webdriver
import time
import datetime
import tkinter as tk
import tkinter.font as font
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')
PATH = "./chromedriver"

root = tk.Tk()
root.configure(bg="#a7ab38")
root.title("Webscraping NBP")
width = root.winfo_screenwidth()
height = root.winfo_screenheight()
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
root.geometry("%dx%d" % (width, height))

# czcionki
entryFont = font.Font(size=30, family="Rasa")
welcomeFont = font.Font(size=25, family="Rasa")
welcomeFontBold = font.Font(size=25, family="Open Sans", weight="bold")
mainFont = font.Font(size=20, family="Rasa")
descFont = font.Font(size=15, family="Rasa")
calendarFont = font.Font(size=15, family="Courier")

# ramki
frameMain = tk.Frame(root, bg="#a7ab38")
frameAddWord = tk.Frame(root, bg="#a7ab38")
frameRandomWord = tk.Frame(root, bg="#a7ab38")
frameTestYourself = tk.Frame(root, bg="#a7ab38")
infoFrame = tk.Frame(root, bg="#a7ab38")
currencyFrame = tk.Frame(root, bg="#a7ab38")
amountFrame = tk.Frame(root, bg="#a7ab38")
calendarFrame = tk.Frame(amountFrame)
resultsFrame = tk.Frame(root, bg="#a7ab38")

calendarFrame.grid(columnspan=2)
currencyList = {'dolar amerykański': '1 USD', 'euro': '1 EUR', 'frank szwajcarski': '1 CHF', 'funt szterling': '1 GBP',
                'hrywna (Ukraina)': '1 UAH'}
chosenCurrency = ''
chosenDate = []
framesDict = {}
dateRate = {}

daytime = time.strftime("%Y-%m-%d")
daytime = daytime.split('-')
currentYear = daytime[0]
clickedButton = 0


# ----- FUNKCJE POMOCNICZE -----


# funkcja chowająca i pokazująca ramki z oknami
def showAndHideFrames(frameToShow, frameToHide=frameMain):
    if frameToHide is None:
        frameToShow.grid()
        return
    if frameToHide not in (frameMain, amountFrame, framesDict.values()):
        for child in frameToHide.winfo_children():
            child.destroy()
    frameToHide.grid_remove()
    frameToShow.grid()


def shCalendarFrames(frameToShow, frameToHide):
    if frameToHide is None:
        frameToShow.grid()
        return
    frameToHide.grid_remove()
    frameToShow.grid()


# Funkcja wypisująca wyniki
def wypisz(rate, date, rate_date, earnings):
    curr = list(currencyList.keys())[list(currencyList.values()).index(chosenCurrency)]
    dateComplete = "Data zamówienia: " + date
    earningsComplete = "Zarobek: " + str(earnings)
    rateComplete = "Kurs z dnia poprzedzającego ("+curr+', '+rate_date+"): " + str(rate)
    gainComplete = "Przychód należny: " + str(round(earnings * rate, 2))

    showAndHideFrames(resultsFrame, amountFrame)
    introLabel = tk.Label(resultsFrame, text="Dane do ewidencji:\n", font=entryFont, bg="#a7ab38")
    dateLabel = tk.Label(resultsFrame, text=dateComplete, font=mainFont, bg="#a7ab38")
    earningsLabel = tk.Label(resultsFrame, text=earningsComplete, font=mainFont, bg="#a7ab38")
    rateLabel = tk.Label(resultsFrame, text=rateComplete, font=mainFont, bg="#a7ab38")
    gainLabel = tk.Label(resultsFrame, text=gainComplete, font=mainFont, bg="#a7ab38")
    returnButton = tk.Button(resultsFrame, text="Powrót do ekranu głównego", font=mainFont, bg="#fffdbd",
                             activebackground="#e3e08f", command=lambda: [showAndHideFrames(frameMain, resultsFrame)])

    introLabel.grid(row=0)
    dateLabel.grid(row=1)
    earningsLabel.grid(row=2)
    rateLabel.grid(row=3)
    gainLabel.grid(row=4)
    returnButton.grid(row=5, pady=10)

    for frame in framesDict:
        framesDict[frame].destroy()
    framesDict.clear()


# Sekcja "O programie"
def showInfo():
    showAndHideFrames(infoFrame)
    infoLabel = tk.Label(infoFrame, anchor='w', justify="left",
                         text='Witaj w programie Kursy Walut!', font=entryFont, background="#a7ab38",
                         foreground="#fdffba", pady=30)
    infoLabel2 = tk.Label(infoFrame, anchor='w', justify="left",
                          text='Mój program ułatwi Ci wyszukanie odpowiedniego kursu, jeśli nie zarabiasz w złotówkach'
                               '\ni prowadzisz ewidencję z uwzględnieniem aktualnych kursów walut, '
                               'podanych na stronie NBP. \n\n'
                               'Instrukcja obsługi:\n'
                               '1) Wybierz odpowiednią walutę spośród podanych.\n'
                               '2) Wybierz odpowiednią datę.\n'
                               '3) Podaj zarobioną kwotę.\n\n'
                               'Po wykonaniu szeregu operacji, program poda na wyjściu kurs waluty z'
                               'odpowiedniego dnia \n'
                               'oraz przeliczoną na złotówki kwotę, którą możesz wpisać do ewidencji. Powodzenia!',
                               font=welcomeFont, background="#a7ab38", foreground="#fdffba")
    returnButton = tk.Button(infoFrame, text="Powrót do ekranu głównego", font=welcomeFont, bg="#fffdbd",
                             activebackground="#e3e08f", command=lambda: [showAndHideFrames(frameMain, infoFrame)])
    infoLabel.grid(row=1, column=0)
    infoLabel2.grid(row=2, column=0)
    returnButton.grid(row=3, pady=30)


# Funkcja zwracająca liczbę dni w danym miesiącu
def howManyDays(month, year):
    if month in (1, 3, 5, 7, 8, 10, 12):
        return 31
    if month in (4, 6, 9, 11):
        return 30
    if przestepny(year):
        return 29
    return 28


# Funkcja zmieniająca numer miesiąca na jego nazwę
def monthToStr(month):
    if month == 1:
        return "Styczeń"
    if month == 2:
        return "Luty"
    if month == 3:
        return "Marzec"
    if month == 4:
        return "Kwiecień"
    if month == 5:
        return "Maj"
    if month == 6:
        return "Czerwiec"
    if month == 7:
        return "Lipiec"
    if month == 8:
        return "Sierpień"
    if month == 9:
        return "Wrzesień"
    if month == 10:
        return "Październik"
    if month == 11:
        return "Listopad"
    if month == 12:
        return "Grudzień"


# Funkcja tworząca nową ramkę kalendarza
def createFrame(year, month):
    if framesDict.get(str(year)+'-'+str(month)) is None:
        month = int(month)
        year = int(year)
        newFrame = tk.Frame(calendarFrame)
        buttons = []

        def saveDate(day, month, year):
            buttons[day+j-1]['state'] = tk.DISABLED
            if month == datetime.datetime.today().month and year == currentYear:
                for button in buttons[:datetime.datetime.today().day+j]:
                    if button != buttons[day+j-1]:
                        button['state'] = tk.NORMAL
            else:
                for button in buttons:
                    if button != buttons[day+j-1]:
                        button['state'] = tk.NORMAL

            global chosenDate
            date = str(day) + '-' + str(month) + '-' + str(year)
            if month < 10:
                date = str(day) + '-0' + str(month) + '-' + str(year)
            if day < 10:
                date = '0' + date
            chosenDate = [date]
        j = 0
        for i in range(datetime.datetime(int(year), int(month), 1).weekday()):
            buttons.append(tk.Button(newFrame, text="  ", font=calendarFont))
            j += 1

        for i in range(j, howManyDays(month, year)+j):
            if i-j+1 < 10:
                t = '0' + str(i-j+1)
            else:
                t = str(i-j+1)
            buttons.append(tk.Button(newFrame, text=t, font=calendarFont,
                                     command=lambda i=i: [saveDate(i-j + 1, month, year)]))
        if datetime.datetime.today().month == month and year == datetime.datetime.today().year:
            for button in buttons[j+datetime.datetime.today().day:]:
                button['command'] = ''
                button['text'] = '  '
        YEARS = [str(i) for i in range(int(currentYear), 2001, -1)]
        variable = tk.StringVar(newFrame)
        variable.set(YEARS[0])
        w = tk.OptionMenu(newFrame, variable, *YEARS)
        w.grid(row=0, column=8)
        tk.Button(newFrame, text='Wybierz', command=lambda: [changeMonth(int(variable.get()), 1, month, year)]).grid(
            row=1, column=8)
        tk.Label(newFrame, text=monthToStr(month) + ' ' + str(year), font=mainFont).grid(row=0, columnspan=8, rowspan=2, pady=15)
        tk.Button(newFrame, text='Poprzedni', command=lambda: [changeMonth(year, month-1, month, year, buttons)])\
            .grid(row=2, column=8, padx=10)
        if month != datetime.datetime.today().month or year != datetime.datetime.today().year:
            tk.Button(newFrame, text='Następny', command=lambda: [changeMonth(year, month+1, month, year, buttons)])\
                .grid(row=3, column=8, padx=10)

        for i in range(len(buttons)):
            buttons[i].grid(row=(i // 7)+2, column=i % 7)
        framesDict[str(year)+'-'+str(month)] = newFrame
    return framesDict[str(year)+'-'+str(month)]


# Funkcja zmieniająca okno kalendarza
def changeMonth(year, month, previousMonth, previousYear, buttons=[]):
    if previousMonth != month or previousYear != year:
        for button in buttons:
            button['state'] = tk.NORMAL
    if month == 13:
        month = 1
        year += 1
    if month == 0:
        month = 12
        year -= 1
    currentFrame = framesDict.get(str(previousYear)+'-'+str(previousMonth))
    newFrame = createFrame(year, month)
    shCalendarFrames(newFrame, currentFrame)


# Funkcja zapisująca wybraną walutę do zmiennej globalnej
def saveCurrency(currency):
    global chosenCurrency
    chosenCurrency = currencyList[currency]
    chooseAmount()


# Obsługa okna wybrania waluty
def chooseCurrency():
    showAndHideFrames(currencyFrame)
    global chosenCurrency
    i = 0
    for el in currencyList:
        tk.Button(currencyFrame, text=el, bg="#fffdbd", activebackground="#e3e08f", font=descFont,
                  command=lambda el=el: [saveCurrency(el)]).grid(row=i, pady=(0,10))
        i += 1
    closeBtn = tk.Button(currencyFrame, text="Powrót", font=welcomeFont, bg="#fffdbd", fg="#a30000",
                         activebackground="#910000", activeforeground="white",
                         command=lambda:[showAndHideFrames(frameMain, currencyFrame)])
    closeBtn.grid(row=i, pady=10)


# Obsługa okna wybierania daty i kwoty
def chooseAmount():
    def saveAmount():
        previous_date = chosenDate[0]
        amount = float(entryAmount.get())
        rate = 0
        triesNumber = 0
        while not rate and triesNumber != 5:
            previous_date = previous_day(previous_date)
            tables = choose_month(previous_date)
            href = get_href(tables, previous_date)
            rate = get_rate(href, previous_date)
            triesNumber += 1
        if triesNumber == 5:
            showAndHideFrames(resultsFrame, amountFrame)
            introLabel = tk.Label(resultsFrame, text="Nie znaleziono odpowiednich danych. Przepraszam.",
                                  font=mainFont, bg="#a7ab38")
            returnButton = tk.Button(resultsFrame, text="Powrót do ekranu głównego", font=mainFont, bg="#a7ab38",
                                     command=lambda: [showAndHideFrames(frameMain, resultsFrame)])

            introLabel.grid(row=0)
            returnButton.grid(row=5)
        else:
            wypisz(rate, chosenDate[0], previous_date, amount)
    shCalendarFrames(amountFrame, currencyFrame)
    daytime = time.strftime("%Y-%m-%d")
    daytime = daytime.split('-')
    TY = daytime[0]
    TM = daytime[1]
    changeMonth(int(TY), int(TM), int(TM), int(TY))
    amountLabel = tk.Label(amountFrame, text="Podaj zarobioną kwotę: ", bg="#a7ab38", font=mainFont, pady=20)
    entryAmount = tk.Entry(amountFrame, font=welcomeFont)

    saveButton = tk.Button(amountFrame, text="Wybierz", command=saveAmount, font=mainFont,
                           bg="#fffdbd", activebackground="#e3e08f")
    closeBtn = tk.Button(amountFrame, text="Powrót", font=mainFont, bg="#910000", fg="#fffdbd",
                         activebackground="#c50000", activeforeground="white",
                         command=lambda: [shCalendarFrames(currencyFrame, amountFrame)])
    amountLabel.grid(row=1, column=0)
    entryAmount.grid(row=1, column=1)
    saveButton.grid(row=2, column=1, sticky='e', pady=10)
    closeBtn.grid(row=3, column=1, sticky='e', pady=10)


# Czy rok przestępny
def przestepny(year):
    return (year % 4 == 0 and year % 100 != 0) or year % 400 == 0


# Cofnięcie się o jeden dzień
def previous_day(current_date):
    current_date = current_date.split('-')
    day = current_date[0]
    month = current_date[1]
    year = current_date[2]
    day = int(day)
    month = int(month)
    day -= 1
    if day == 0:
        if month in (1, 2, 4, 6, 9, 11):
            day = 31
        elif month in (5, 7, 8, 10, 12):
            day = 30
        elif przestepny(year):
            day = 29
        else:
            day = 28

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
    if int(month) < 10:
        month = '0' + month
    return day+'-'+month+'-'+year


# Jeden dzień naprzód
def next_day(current_date):
    current_date = current_date.split('-')
    day = current_date[0]
    month = current_date[1]
    year = current_date[2]
    day = int(day)
    month = int(month)
    day += 1
    if (month in (1, 3, 5, 7, 8, 10, 12) and day == 32) or (month in (4,6,9,11) and day == 31) or \
            (month == 2 and not przestepny(year) and day == 29) or (month == 2 and przestepny(year) and day == 30):
        day = 1
        month += 1
        if month == 12:
            month = 1
            year = int(year)
            year += 1

    year = str(year)
    month = str(month)
    day = str(day)
    if int(day) < 10:
        day = '0' + day
    if int(month) < 10:
        month = '0' + month
    return day+'-'+month+'-'+year


# Funkcja rozbijająca datę na części
def get_date(date):
    date = date.split('-')
    day = date[0]
    month = date[1]
    year = date[2]
    return day, month, year


# Funkcja zwracająca tablicę z całego miesiąca
def choose_month(date):
    day, month, year = get_date(date)
    driver = webdriver.Chrome(PATH, options=options)
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


# Funkcja zwracająca odnośnik do odpowiedniej tabeli
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
        return 0
    return href


# Funkcja pobierająca odpowiedni kurs waluty z tabeli
def get_rate(href, date):
    day, month, year = get_date(date)
    driver = webdriver.Chrome(PATH, options=options)
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
        row_td = row.find('td', class_="right")
        split = str(row_td).split('>')
        currency = ""
        if len(split) > 1:
            currency = split[1].split('<')
            currency = currency[0].replace('\xa0', ' ')
        if currency == chosenCurrency:  # zmienna globalna waluta #
            row_td2 = row.find_all('td', class_='right')
            row_td2 = str(row_td2[1]).split(">")
            row_td2 = row_td2[1].split('<')
            rate = row_td2[0].replace(',', '.')
            rate = float(rate)
            #driver.close()
            return rate


def chooseCurrencyRate():
    showAndHideFrames(currencyFrame)
    global chosenCurrency
    i = 0
    for el in currencyList:
        tk.Button(currencyFrame, text=el, bg="#fffdbd", activebackground="#e3e08f", font=descFont,
                  command=lambda el=el: [saveCurrencyRate(el)]).grid(row=i, pady=(0, 10))
        i += 1
    closeBtn = tk.Button(currencyFrame, text="Powrót", font=welcomeFont, bg="#fffdbd", fg="#a30000",
                         activebackground="#910000", activeforeground="white",
                         command=lambda: [showAndHideFrames(frameMain, currencyFrame)])
    closeBtn.grid(row=i, pady=10)


# Funkcja zapisująca wybraną walutę do zmiennej globalnej
def saveCurrencyRate(currency):
    global chosenCurrency
    chosenCurrency = currencyList[currency]
    shCalendarFrames(amountFrame, currencyFrame)
    for child in amountFrame.winfo_children():
        if str(child)[-5:] != 'frame':
            child.grid_remove()
    daytime = time.strftime("%Y-%m-%d")
    daytime = daytime.split('-')
    TY = daytime[0]
    TM = daytime[1]
    changeMonthRate(int(TY), int(TM), int(TM), int(TY))
    closeBtn = tk.Button(amountFrame, text="Powrót", font=mainFont, bg="#910000", fg="#fffdbd",
                         activebackground="#c50000", activeforeground="white",
                         command=lambda: [shCalendarFrames(currencyFrame, amountFrame)])
    closeBtn.grid(row=3, column=1, sticky='e', pady=10)


# Funkcja zmieniająca okno kalendarza
def changeMonthRate(year, month, previousMonth, previousYear, buttons=[]):

    if month == 13:
        month = 1
        year += 1
    if month == 0:
        month = 12
        year -= 1
    currentFrame = framesDict.get(str(previousYear)+'-'+str(previousMonth))
    newFrame = createFrameRate(year, month)
    shCalendarFrames(newFrame, currentFrame)


# Funkcja tworząca nową ramkę kalendarza
def createFrameRate(year, month):
    if framesDict.get(str(year)+'-'+str(month)) is None:
        month = int(month)
        year = int(year)
        newFrame = tk.Frame(calendarFrame)
        buttons = []

        def saveDate(day, month, year):
            buttons[day+j-1]['state'] = tk.DISABLED
            global chosenDate
            date = str(day) + '-' + str(month) + '-' + str(year)
            if month < 10:
                date = str(day) + '-0' + str(month) + '-' + str(year)
            if day < 10:
                date = '0' + date
            chosenDate.append(date)
            if len(chosenDate) == 2:
                getRateFromDate()
        j = 0
        for i in range(datetime.datetime(int(year), int(month), 1).weekday()):
            buttons.append(tk.Button(newFrame, text="  ", font=calendarFont))
            j += 1

        for i in range(j, howManyDays(month, year)+j):
            if i-j+1 < 10:
                t = '0' + str(i-j+1)
            else:
                t = str(i-j+1)
            buttons.append(tk.Button(newFrame, text=t, font=calendarFont,
                                     command=lambda i=i: [saveDate(i-j + 1, month, year)]))
        if datetime.datetime.today().month == month and year == datetime.datetime.today().year:
            for button in buttons[j+datetime.datetime.today().day:]:
                button['command'] = ''
                button['text'] = '  '
        YEARS = [str(i) for i in range(int(currentYear), 2001, -1)]
        variable = tk.StringVar(newFrame)
        variable.set(YEARS[0])
        w = tk.OptionMenu(newFrame, variable, *YEARS)
        w.grid(row=0, column=8)
        tk.Button(newFrame, text='Wybierz', command=lambda: [changeMonthRate(int(variable.get()), 1, month, year)]).grid(
            row=1, column=8)
        tk.Label(newFrame, text=monthToStr(month) + ' ' + str(year), font=mainFont).grid(row=0, columnspan=8, rowspan=2, pady=15)
        tk.Button(newFrame, text='Poprzedni', command=lambda: [changeMonthRate(year, month-1, month, year, buttons)])\
            .grid(row=2, column=8, padx=10)
        if month != datetime.datetime.today().month or year != datetime.datetime.today().year:
            tk.Button(newFrame, text='Następny', command=lambda: [changeMonthRate(year, month+1, month, year, buttons)])\
                .grid(row=3, column=8, padx=10)

        for i in range(len(buttons)):
            buttons[i].grid(row=(i // 7)+2, column=i % 7)
        framesDict[str(year)+'-'+str(month)] = newFrame
    return framesDict[str(year)+'-'+str(month)]


def getHrefsRate(tables, date, finalDate):
    day, month, year = get_date(date)
    dayF, monthF, yearF = get_date(finalDate)
    a = 0
    for i in range(len(tables)):
        bs = tables[i].find_all('b')
        for b in bs:
            date = b.text.split('-')
            if len(date) < 3:
                continue
            if int(date[0]) > int(yearF) or (date[1] == yearF and int(date[1]) > int(monthF)) or\
                    (date[0] == yearF and date[1] == monthF and int(date[2]) > int(dayF)):
                a += 1
            if b.text == year + '-' + month + '-' + day or i == len(tables)-1:  # or b.text == year+'-'+month+'-'+day cofniecie o dzień, dwa, trzy...:
                return tables[a:i+1]
    return 0


def getRateFromDate():
    d1 = chosenDate[0].split('-')
    d2 = chosenDate[1].split('-')

    if int(d1[2]) < int(d2[2]) or (d1[2] == d2[2] and int(d1[1]) < int(d2[1])) or\
            (d1[2] == d2[2] and d1[1] == d2[1] and int(d1[0]) < int(d2[0])):
        earlier = chosenDate[0]
        later = chosenDate[1]
    else:
        earlier = chosenDate[1]
        later = chosenDate[0]
    rate = 0
    triesNumber = 0
    hrefs = []
    while triesNumber != 1:
        tables = choose_month(earlier)
        hrefs = getHrefsRate(tables, earlier, later)
        for href in hrefs:
            date = str(href).split('<b>')[2]
            date = date.split('</b>')[0]
            href = href['href'].replace("%amp;", "&")
            rate = get_rate(href, earlier)
            dateRate[date] = rate
        triesNumber += 1
        earlier = next_day(earlier)
    dates = list(dateRate.keys())
    values = list(dateRate.values())
    # for key in dates[::-1]:
    #     data = key.split('-')
    #     data = data[::-1]
    #     data = "-".join(data)
    #     print(data)
    #     newData = next_day(data)
    #     newData = newData.split('-')
    #     newData = newData[::-1]
    #     newData = '-'.join(newData)
    #
    #     if dateRate.get(newData) is None:
    #         print(key, newData)
    #         dateRate[newData] = dateRate[key]
    dates = list(dateRate.keys())
    values = list(dateRate.values())
    plt.plot(dates[::-1], values[::-1])
    plt.xticks(rotation=45)
    plt.show()
    if triesNumber == 5:
        showAndHideFrames(resultsFrame, amountFrame)
        introLabel = tk.Label(resultsFrame, text="Nie znaleziono odpowiednich danych. Przepraszam.",
                              font=mainFont, bg="#a7ab38")
        returnButton = tk.Button(resultsFrame, text="Powrót do ekranu głównego", font=mainFont, bg="#a7ab38",
                                 command=lambda: [showAndHideFrames(frameMain, resultsFrame)])

        introLabel.grid(row=0)
        returnButton.grid(row=5)
    else:
        wypisz(rate, chosenDate[0], earlier, 0)

# TODO: Połączenie miesięcy (zakres szerszy)
# TODO: Usunięcie ostatniego ekranu z analizy kursów
# TODO: Informacja, że się robi


if __name__ == "__main__":

    # ------------- EKRAN GŁÓWNY -------------

    # ekran główny, elementy
    frameMain.grid(row=0, column=0, columnspan=3, sticky='')
    welcomeText = tk.Label(frameMain, bg="#a7ab38",fg="#fdffba",
                           text="Witaj w Kalkulatorze Walut.\n\nWybierz z poniższych opcji, co chcesz zrobić:",
                           font=welcomeFontBold)

    info = tk.Button(frameMain, text="O programie", font=welcomeFont, bg="#fffdbd", fg="#5c2500",
                     activebackground="#e3e08f", activeforeground="#5c2500", pady=10, padx=20, command=showInfo)
    chooseCurr = tk.Button(frameMain, text="Wybierz walutę", font=welcomeFont, bg="#fffdbd", fg="#475b11",
                               activebackground="#e3e08f", activeforeground="#475b11", pady=10, padx=20,
                               command=chooseCurrency)
    checkRates = tk.Button(frameMain, text="Zbadaj kurs waluty", font=welcomeFont, bg="#fffdbd", fg="#030054",
                           activebackground="#e3e08f", activeforeground="#030054", pady=10, padx=20,
                           command=chooseCurrencyRate)
    close = tk.Button(frameMain, text="Wyjdź", font=welcomeFont, bg="#fffdbd", pady=10, fg="#a30000",
                      activebackground="#910000", activeforeground="white", padx=20, command=root.destroy)

    # ekran główny, ułożenie elementów
    welcomeText.grid(row=0, column=0, columnspan=4, sticky="")
    info.grid(row=1, column=0, padx=(0, 40), pady=80)
    chooseCurr.grid(row=1, column=1, padx=40)

    checkRates.grid(row=1, column=2, padx=(0, 40))
    close.grid(row=2, column=2)

    root.mainloop()
