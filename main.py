from selenium import webdriver
import time
import datetime
import tkinter as tk
import tkinter.font as font
from bs4 import BeautifulSoup

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
currencyList = ['dolar amerykański', 'euro', 'frank szwajcarski', 'funt szterling', 'hrywna (Ukraina)']
chosenCurrency = ''
chosenDate = ''
framesDict = {}

daytime = time.strftime("%Y-%m-%d")
daytime = daytime.split('-')
currentYear = daytime[0]


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
    dateComplete = "Data zamówienia: " + date
    earningsComplete = "Zarobek: " + str(earnings)
    rateComplete = "Kurs z dnia poprzedzającego ("+chosenCurrency+', '+rate_date+"): " + str(rate)
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
            chosenDate = str(day) + '-' + str(month) + '-' + str(year)
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
        YEARS = [str(i) for i in range(int(currentYear), 2004, -1)]
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
def saveCurrency(nr):
    global chosenCurrency
    chosenCurrency = currencyList[nr]
    chooseAmount()


# Obsługa okna wybrania waluty
def chooseCurrency():
    showAndHideFrames(currencyFrame)
    global chosenCurrency
    i = 0
    for el in currencyList:
        tk.Button(currencyFrame, text=el, bg="#fffdbd", activebackground="#e3e08f", font=descFont,
                  command=lambda i=i: [saveCurrency(i)]).grid(row=i, pady=(0,10))
        i += 1
    closeBtn = tk.Button(currencyFrame, text="Powrót", font=welcomeFont, bg="#fffdbd", fg="#a30000",
                         activebackground="#910000", activeforeground="white",
                         command=lambda:[showAndHideFrames(frameMain, currencyFrame)])
    closeBtn.grid(row=i, pady=10)


# Obsługa okna wybierania daty i kwoty
def chooseAmount():
    def saveAmount():
        previous_date = chosenDate
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
            wypisz(rate, chosenDate, previous_date, amount)
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
        if currency == chosenCurrency:  # zmienna globalna waluta #
            row_td2 = row.find_all('td', class_='right')
            row_td2 = str(row_td2[1]).split(">")
            row_td2 = row_td2[1].split('<')
            rate = row_td2[0].replace(',', '.')
            rate = float(rate)
            driver.close()
            return rate


if __name__ == "__main__":

    # ------------- EKRAN GŁÓWNY -------------

    # ekran główny, elementy
    frameMain.grid(row=0, column=0, columnspan=3, sticky='')
    welcomeText = tk.Label(frameMain, bg="#a7ab38",fg="#fdffba",
                           text="Witaj w Kalkulatorze Walut.\n\nWybierz z poniższych opcji, co chcesz zrobić:",
                           font=welcomeFontBold)

    info = tk.Button(frameMain, text="O programie", font=welcomeFont, bg="#fffdbd", fg="#5c2500",
                     activebackground="#e3e08f", activeforeground="#5c2500", pady=10, padx=20, command=showInfo)
    chooseCurrency = tk.Button(frameMain, text="Wybierz walutę", font=welcomeFont, bg="#fffdbd", fg="#475b11",
                               activebackground="#e3e08f", activeforeground="#475b11", pady=10, padx=20,
                               command=chooseCurrency)
    checkRates = tk.Button(frameMain, text="Zbadaj kurs waluty", font=welcomeFont, bg="#fffdbd", fg="#030054",
                           activebackground="#e3e08f", activeforeground="#030054", pady=10, padx=20)#, command=show)
    close = tk.Button(frameMain, text="Wyjdź", font=welcomeFont, bg="#fffdbd", pady=10, fg="#a30000",
                      activebackground="#910000", activeforeground="white", padx=20, command=root.destroy)

    # ekran główny, ułożenie elementów
    welcomeText.grid(row=0, column=0, columnspan=4, sticky="")
    info.grid(row=1, column=0, padx=(0, 40), pady=80)
    chooseCurrency.grid(row=1, column=1, padx=40)

    checkRates.grid(row=1, column=2, padx=(0, 40))
    close.grid(row=2, column=2)

    root.mainloop()
