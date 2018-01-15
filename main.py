# dependency for Selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from pyvirtualdisplay import Display

# Dependency for wait element
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException, ElementNotInteractableException

# Dependancy for other element
import urllib
import time
import pickle
import string
import os
from PIL import Image
from config_bot import *
import sys
import re
import concurrent.futures
from bs4 import BeautifulSoup



class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNYELLOW = '\033[1;33m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# Cookie saver
def save_cookies(driver, file_path):
    LINE = "{domain} False {path} {secure} {expiry} {name} {value}\n"
    with open(file_path, 'w') as file:
        for cookie in driver.get_cookies():
            file.write(
                LINE.format(
                    **cookie))


def load_cookies(driver, file_path):
    with open(file_path, 'r') as file:
        driver.execute_script(
            file.read())

def image_diff(i1, i2):
    i1 = Image.open(i1)
    i2 = Image.open(i2)
    assert i1.mode == i2.mode, "Different kinds of images."
    assert i1.size == i2.size, "Different sizes."
 
    pairs = zip(i1.getdata(), i2.getdata())
    if len(i1.getbands()) == 1:
       # for gray-scale jpegs
       dif = sum(abs(p1-p2) for p1,p2 in pairs)
    else:
       dif = sum(abs(c1-c2) for p1,p2 in pairs for c1,c2 in zip(p1,p2))
 
    ncomponents = i1.size[0] * i1.size[1] * 3
    return (dif / 255.0 * 100) / ncomponents

def check_images(image1, image2):
    pourcent = image_diff(image1, image2)
    #print(pourcent)
    if pourcent <= 0.19:
        return True
    else:
        return False

class PoleEmplois():

    def __init__(self, compte, password, display):
        start_time = time.time()
        self.display = self.Afficheur(display) 
        self.navigateur = self.Connection(compte)

        navigationStart = self.navigateur.execute_script("return window.performance.timing.navigationStart")
        responseStart = self.navigateur.execute_script("return window.performance.timing.responseStart")
        domComplete = self.navigateur.execute_script("return window.performance.timing.domComplete")

        backendPerformance = responseStart - navigationStart
        frontendPerformance = domComplete - responseStart

        start_time_login = time.time()
        
        self.InputLogin(self.navigateur, compte, password)
        interval_login = time.time() - start_time_login
        print("\033[92m" + 'Total time login in seconds:', str(interval_login) + "\033[0m")

        try:
           if sys.argv[3] == "cv":
                self.cv(self.navigateur)

           if sys.argv[3] == "check":
                actualisationcheck = self.actualisation(self.navigateur)
                if actualisationcheck == False:
                    print(bcolors.FAIL + "Vous êtes déja actualisez... ou le bouton n'est pas mis en avant." + bcolors.ENDC)
           if sys.argv[3] == "search":
                search = self.search(self.navigateur)

        except (IndexError, TimeoutException):
            try:
                for i in range(0, 9):
                    if sys.argv[3] == "cv":
                        cv = self.cv(self.navigateur)
                        if cv:
                            break

                    if sys.argv[3] == "check":
                        actualisationcheck = self.actualisation(self.navigateur)
                        if actualisationcheck == False:
                            print(bcolors.FAIL + "Vous êtes déja actualisez... ou le bouton n'est pas mis en avant." + bcolors.ENDC)
                            break
                
                    if sys.argv[3] == "search":
                        search = self.search(self.navigateur)
                        if search:
                            break
            except TimeoutException:
                pass


        print()
        print("\033[95m \033[1mBack End: %s ms \033[0m" % backendPerformance)
        print("\033[95m \033[1mFront End: %s ms \033[0m" % frontendPerformance)

        interval = time.time() - start_time
        print('\033[95m \033[1mTotal time in seconds:',str(interval) + "\033[0m")
        print()

        try:
            if sys.argv[4] != "noclose" and len(sys.argv) == 4:
                print("close normal")
                self.close(self.navigateur)
            elif sys.argv[3] != "noclose" and len(sys.argv) == 3:
                print("close normal")
                self.close(self.navigateur)
        except IndexError:
            #pass
            print("close normal")
            self.close(self.navigateur)


    def Afficheur(self, display):
        if display == True:
            afficheur = Display(visible=1, size=(1024, 800))
            afficheur.start()
        else:
            afficheur = Display(visible=0, size=(1024, 800))
            afficheur.start()


    def Connection(self, account):
        print(bcolors.OKGREEN + "Connection au Pole Emploi" + bcolors.ENDC)

        url = "https://candidat.pole-emploi.fr/candidat/espacepersonnel/authentification/"
        profile = webdriver.FirefoxProfile()
        if os.path.isdir("/home/" + account) == False:
            os.makedirs("/home/" + account)
        profile.set_preference('browser.download.folderList', 2)
        profile.set_preference('browser.download.manager.showWhenStarting', False)
        profile.set_preference("javascript.enabled", 0)
        profile.set_preference('browser.download.dir', "/home/" + account + "/")
        profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
        profile.set_preference("pdfjs.disabled", True)
        navigateur = webdriver.Firefox(profile)
        navigateur.get(url)

        return navigateur

    def InputLogin(self, navigateur, account, password):

        # input ID
        try:
            inputEmail = WebDriverWait(navigateur, 2).until(EC.presence_of_element_located((By.ID, "identifiant")))
            print(bcolors.OKBLUE + "Enter ID with input" + bcolors.ENDC)
            inputEmail.send_keys(account)
            #button = navigateur.find_element_by_id("boutonContinuer")
            button = WebDriverWait(navigateur, 2).until(EC.presence_of_element_located((By.ID, "submit")))
            button.click()
        except TimeoutException:
            for i in range(0, 3):
                try:
                    print("try for login.... (" + str(i)+")")
                    print(bcolors.FAIL + "Timeout check element recheck..." + bcolors.ENDC)
                    inputEmail = WebDriverWait(navigateur, 5).until(EC.presence_of_element_located((By.XPATH, "//input[@id='identifiant']")))
                    print(bcolors.OKBLUE + "Enter ID with input" + bcolors.ENDC)
                    inputEmail.click()
                    inputEmail.send_keys(account)
                    #button = navigateur.find_element_by_id("boutonContinuer")
                    button = WebDriverWait(navigateur, 5).until(EC.presence_of_element_located((By.ID, "submit")))
                    if button and inputEmail:
                        button.click()
                        break
                except TimeoutException:
                    pass
                    
        time.sleep(0.3)
        start_time_login = time.time()
        cel_0 = WebDriverWait(navigateur, 5).until(EC.presence_of_element_located((By.ID, "val_cel_0")))
        cel_9 = WebDriverWait(navigateur, 5).until(EC.presence_of_element_located((By.ID, "val_cel_9")))

        if cel_0 and cel_9:
            navigateur.save_screenshot('images/screenshot.png')
            liste = list(password)
        else:
            exit()

        for i in range(0,10):
            cel_0 = WebDriverWait(navigateur, 0.01).until(EC.presence_of_element_located((By.ID, "val_cel_"+str(i))))
            location = cel_0.location
            size = cel_0.size
            im = Image.open('images/screenshot.png')
            left = location['x']
            top = location['y']
            right = location['x'] + size['width']
            bottom = location['y'] + size['height']
            im = im.crop((left, top, right, bottom)) # defines crop points
            im.save('images/Downloads/cel_'+str(i)+'.png') # saves new cropped image

        dict_pass = {}
        if os.path.isdir("images/Downloads") == False:
            os.makedirs("images/Downloads")
        
        # prepare list for password dual loop [(0,0), (0, 1), ... (0, 9), (1, 0), (1, 1), ...]
        listes = [(x, y) for x in range(0, 10) for y in range(0, 10)]
        
        print(bcolors.OKBLUE + "Analysing Pad ... please wait" + bcolors.ENDC)
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            for a, i in listes:
                lineexec = executor.submit(check_images, 'images/Downloads/cel_'+ str(i) +'.png', 'images/Templates/normal/'+str(a)+'.png')
                if lineexec.result() == True:
                    #print("cel_"+str(i), " = "+str(a))
                    elem = WebDriverWait(navigateur, 0.01).until(EC.presence_of_element_located((By.XPATH, "//button[@id='"+"val_cel_"+str(i)+"']")))
                    dict_pass[elem.get_attribute("class")] = list()
                    dict_pass[elem.get_attribute("class")].append(a)
                    dict_pass[elem.get_attribute("class")].append(elem.get_attribute("id"))
        
        if len(dict_pass.keys()) < 9:
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                for a, i in listes:
                    lineexec = executor.submit(check_images, 'images/Downloads/cel_'+ str(i) +'.png', 'images/Templates/1600x900/'+str(a)+'.png')
                    if lineexec.result() == True:
                        #print("cel_"+str(i), " = "+str(a))
                        elem = WebDriverWait(navigateur, 0.01).until(EC.presence_of_element_located((By.XPATH, "//button[@id='"+"val_cel_"+str(i)+"']")))
                        dict_pass[elem.get_attribute("class")] = list()
                        dict_pass[elem.get_attribute("class")].append(a)
                        dict_pass[elem.get_attribute("class")].append(elem.get_attribute("id"))

        callback_string = ""
        listes = [(x, y, z) for x in liste for y, z in dict_pass.items()]
        for attrib, key, value in listes:
            if int(attrib) == value[0]:
                #button = WebDriverWait(navigateur, 0.01).until(EC.presence_of_element_located((By.XPATH, "//button[@class='"+key+"']")))
                #print(key, value[0], value[1])
                callback_string += value[1]
                #button.click()

        navigateur.execute_script("document.getElementById(\"idTouchesCliques\").value=\""+ callback_string +"\";")
        elem = WebDriverWait(navigateur, 0.01).until(EC.presence_of_element_located((By.XPATH, "//input[@id='idTouchesCliques']")))
        print(bcolors.OKBLUE + "resolved pad touch '" + callback_string + "'"+ bcolors.ENDC)
        
        interval_login = time.time() - start_time_login
        print( bcolors.UNDERLINE + bcolors.BOLD + bcolors.OKBLUE + 'resolve pad time in seconds:',str(interval_login) + bcolors.ENDC)
        
        #inputPostal = navigateur.find_element_by_id("champTexteCodePostal")
        inputPostal = WebDriverWait(
            navigateur, 3).until(
            EC.presence_of_element_located(
                (By.ID, "codepostal")))
        inputPostal.send_keys(Profile[sys.argv[2]][2])
        inputPostal.send_keys(Keys.RETURN)


    def deletepopup(self, navigateur):
        try:
            inputspan = WebDriverWait(navigateur, 5).until(EC.presence_of_element_located((By.XPATH, "//button[@class='js-close-popin']")))
            inputspan.click()
            return True
        except:
            return False

    def cleanhtml(self, raw_html):
        raw_html = re.sub('<[^<]+?>', '', raw_html)
        raw_html = re.sub(r'\([^)]*\)', '', raw_html)
        cleantext = re.sub('(rafraîchir ce CV)', '', raw_html)
        return cleantext

    def cleanhtmls(self, raw_html):
        raw_html = raw_html.replace('<br>', ' ')
        raw_html = re.sub('<[^<]+?>', '', raw_html)
        raw_html = re.sub('&nbsp;', ' ', raw_html)
        raw_html = re.sub('&amp;', '&', raw_html)
        raw_html = raw_html.replace('\t', ' ')
        raw_html = raw_html.replace('\n', ' ')
        return raw_html

    def search_result(self, navigateur, ids, back, page_start, page_stop, row):
        ids = ids-(row*10)
        elem = WebDriverWait(navigateur, 1).until(EC.presence_of_element_located((By.XPATH, "//ul[@id='page_"+page_start+"-"+page_stop+"']/li[@class='result']["+str(ids+1)+"]/div[@id='"+str(ids)+"']/div[@class='media-body']/h2/a")))
        elem.click()

        time.sleep(1)
        for i, elem in enumerate(WebDriverWait(navigateur, 8).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@id='detailOffreVolet']")))):
             soup = BeautifulSoup(elem.get_attribute("innerHTML"), 'lxml') # Parse the HTML as a string
             print()
             print(bcolors.WARNYELLOW + self.cleanhtmls(str(soup.find_all("h2", class_="t2 title")[0])) + bcolors.ENDC)
             print(bcolors.OKGREEN + self.cleanhtmls(str(soup.find_all("p", class_="t4 title-complementary")[0])) + bcolors.ENDC)
             print(bcolors.OKGREEN + self.cleanhtmls(str(soup.find_all("p", class_="t5 title-complementary")[0])) + bcolors.ENDC)
             print()
             print(bcolors.OKBLUE + self.cleanhtmls(str(soup.find_all("div", class_="description col-sm-8 col-md-7")[0])) + bcolors.ENDC)
             print()
             for i in soup.find_all("dd"):
                print(bcolors.OKBLUE + self.cleanhtmls(str(i)) + bcolors.ENDC)
             print()
             print(bcolors.WARNYELLOW + "Profil souhaité" + bcolors.ENDC)
             print()
             for a, i in enumerate(soup.find_all("ul", class_="skill-list list-unstyled")):
                if a == 0:
                    print(bcolors.OKBLUE + "[Expérience]" + bcolors.ENDC)
                    print(bcolors.OKGREEN + self.cleanhtmls(str(i)) + bcolors.ENDC)
                if a == 1:
                    print(bcolors.OKBLUE + "[Compétences]" + bcolors.ENDC)
                    c = i.find_all("span", class_="skill-name")
                    d = i.find_all("span", class_="skill-required")
                    c.append("")
                    d.append("")
                    for x, y in zip(c, d):
                        if x and y:
                           print(self.cleanhtmls(str(x)) +" - " + bcolors.WARNING + self.cleanhtmls(str(y)) + bcolors.ENDC)
                        else:
                           print(self.cleanhtmls(str(x)))
                    
                if a == 2:
                    print(bcolors.OKBLUE + "[Formation]" + bcolors.ENDC)
                    c = i.find_all("span", class_="skill-name")
                    d = i.find_all("span", class_="skill-required")
                    c.append("")
                    d.append("")
                    for x, y in zip(c, d):
                        if x and y:
                           print(self.cleanhtmls(str(x)) +" - " + bcolors.WARNING + self.cleanhtmls(str(y)) + bcolors.ENDC)
                        else:
                           print(self.cleanhtmls(str(x)))
                print()


        while 1:

            select = input(" [p] pour postuler \n [x] pour quitter \n Séléctionner l'action qui vous intéresse: ")

            """try:
                elem = WebDriverWait(navigateur, 5).until(EC.presence_of_element_located((By.XPATH, "//span[@class='close glaze-exclude']")))
                elem.click()
            except TimeoutException:
                continue"""

            if select == "p":
                pass

            if select == "x" or select == "X":
                navigateur.get(back)
                break
                return False

        return True


    def search(self, navigateur):
        for elem in WebDriverWait(navigateur, 8).until(EC.presence_of_all_elements_located((By.XPATH, "//h2[@class='category-title']/a"))):
            if elem.get_attribute("innerHTML") == "Ma recherche <br>d'offres":
                print(bcolors.OKGREEN + "click on '" + elem.get_attribute("innerHTML")+"'" + bcolors.ENDC)
                elem.click()
                break

        for elem in WebDriverWait(navigateur, 8).until(EC.presence_of_all_elements_located((By.XPATH, "//h2[@class='category-title']/a"))):
            if elem.get_attribute("innerHTML") == "La recherche<br>d'offres":
                print(bcolors.OKGREEN + "click on '" + elem.get_attribute("innerHTML")+"'" + bcolors.ENDC)
                elem.click()
                break


        navigateur.execute_script("document.getElementById(\"idoffresPartenaires\").checked = false;")
        search_input = input("Séléctionner votre recherche: ")
        inputs = WebDriverWait(navigateur, 5).until(EC.presence_of_element_located((By.XPATH, "//input[@id='idmotsCles-selectized']")))
        inputs.send_keys(search_input)
        time.sleep(0.05)

        valide = WebDriverWait(navigateur, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='selectize-dropdown-content']/div")))
        valide.click()
        
        position_input = input("Séléctionner votre lieux de recherche: ")
        inputs = WebDriverWait(navigateur, 5).until(EC.presence_of_element_located((By.XPATH, "//input[@id='idlieux-selectized']")))
        inputs.click()

        for i in range(0, len(position_input)):
            time.sleep(0.01)
            inputs.send_keys(position_input[i])

        try:
            valide = WebDriverWait(navigateur, 3).until(EC.presence_of_element_located((By.XPATH, "//div[@class='selectize-dropdown-content'][1]/div[2]")))
            valide.click()
        except (TimeoutException, ElementNotInteractableException):
            try:
                for i in range(0, 500):
                    time.sleep(0.1)
                    valide = WebDriverWait(navigateur, 5).until(EC.presence_of_element_located((By.XPATH, "//div[@class='selectize-dropdown-content'][1]/div[1]/div[@class='option active']")))
                    if valide:
                        print(bcolors.OKBLUE + "séléction automatique '" + self.cleanhtmls(valide.get_attribute("innerHTML")) +"'" + bcolors.ENDC)
                        valide.click()
                        break
            except (TimeoutException, ElementNotInteractableException):
                pass
        
        button = WebDriverWait(navigateur, 10).until(EC.presence_of_element_located((By.XPATH, "//a[@id='btnSubmitRechercheForm']")))
        print(bcolors.OKBLUE + "click on '"+self.cleanhtmls(button.get_attribute("innerHTML")) +"'" + bcolors.ENDC)
        button.click()


        print(""" RESULT SEARCH """)
        for i, elem in enumerate(WebDriverWait(navigateur, 8).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='media-body']")))):
            soup = BeautifulSoup(elem.get_attribute("innerHTML"), 'lxml') # Parse the HTML as a string
            print(str(i) +" " + bcolors.WARNYELLOW + self.cleanhtmls(str(soup.find_all("h2")[0])).strip() + bcolors.ENDC)
            for a in range(0, len(soup.find_all("p"))):
                if a == 0:
                    print(bcolors.OKGREEN + self.cleanhtmls(str(soup.find_all("p")[0])) +  bcolors.ENDC + "\n" + bcolors.OKBLUE + self.cleanhtmls(str(soup.find_all("p")[1])) + bcolors.ENDC)
                if a == 1:
                    print(bcolors.OKGREEN + self.cleanhtmls(str(soup.find_all("p")[2])) +  bcolors.ENDC + "\n" + bcolors.OKBLUE + self.cleanhtmls(str(soup.find_all("p")[3])) + bcolors.ENDC)

            print()
            #print(self.cleanhtmls(str(soup.find_all("h2")[0])).strip() + bcolors.ENDC)
        
        row = 0
        urls = []
        while 1:
            if row == 0:
                start = 0
                end = 9
                start_row = 10
                end_row = 19

            select = input(" ["+ str(start) + "-" + str(end) +"] ou pour plus de recherche [+] \n [s] pour revoir la liste des offres \n [x] pour quitter \n Séléctionner l'offre qui vous intéresse: ")
            try:
                if re.search('\d+', select):
                    if int(select) >= start and int(select) <= end:
                        urls.append(navigateur.current_url)
                        try:
                            button = WebDriverWait(navigateur, 1).until(EC.presence_of_element_located((By.XPATH, "//button[@class='eupopup-closebutton btn-reset']")))
                            button.click()
                            print(bcolors.OKBLUE + "close automatical 'fancy box'" +  bcolors.ENDC)
                        except (TimeoutException, ElementNotInteractableException):
                            pass
                        try:
                            result = self.search_result(navigateur, int(select), urls[0], str(start), str(end), row)
                        except (TimeoutException, ElementNotInteractableException):
                            for i in range(0, 3):
                                #print("trying... resolve search")
                                try:
                                    result = self.search_result(navigateur, int(select), urls[0], str(start), str(end), row)
                                except (TimeoutException, ElementNotInteractableException):
                                    navigateur.get(navigateur.current_url)
                                    time.sleep(0.5)

                                    for i in range(0, row):
                                        time.sleep(0.3)
                                        plus = WebDriverWait(navigateur, 10).until(EC.presence_of_element_located((By.XPATH, "//p[@id='zoneAfficherPlus']/a")))
                                        plus.click()

                                    result = self.search_result(navigateur, int(select), urls[0], str(start), str(end), row)
                                if result == False or result:
                                    break



            except ValueError:
                pass

            if isinstance(select, str) and select == "x" or select == "X":
                break

            if isinstance(select, str) and select == "s" or select == "S":
                for i, elem in enumerate(WebDriverWait(navigateur, 8).until(EC.presence_of_all_elements_located((By.XPATH, "//ul[@id='page_"+str(start)+"-"+str(end)+"']/li[@class='result']/div/div[@class='media-body']")))):
                    soup = BeautifulSoup(elem.get_attribute("innerHTML"), 'lxml') # Parse the HTML as a string
                    print(str(start+i) +" " + bcolors.WARNYELLOW + self.cleanhtmls(str(soup.find_all("h2")[0])).strip() + bcolors.ENDC)
                    for a in range(0, len(soup.find_all("p"))):
                        if a == 0:
                            print(bcolors.OKGREEN + self.cleanhtmls(str(soup.find_all("p")[0])) +  bcolors.ENDC + "\n" + bcolors.OKBLUE + self.cleanhtmls(str(soup.find_all("p")[1])) + bcolors.ENDC)
                        if a == 1:
                            print(bcolors.OKGREEN + self.cleanhtmls(str(soup.find_all("p")[2])) +  bcolors.ENDC + "\n" + bcolors.OKBLUE + self.cleanhtmls(str(soup.find_all("p")[3])) + bcolors.ENDC)
                    print()
                

            if isinstance(select, str) and select == "+":
                try:
                    button = WebDriverWait(navigateur, 10).until(EC.presence_of_element_located((By.XPATH, "//button[@class='eupopup-closebutton btn-reset']")))
                    button.click()
                    print(bcolors.OKBLUE + "close automatical 'fancy box'" +  bcolors.ENDC)
                except (TimeoutException, ElementNotInteractableException):
                    pass

                plus = WebDriverWait(navigateur, 10).until(EC.presence_of_element_located((By.XPATH, "//p[@id='zoneAfficherPlus']/a")))
                plus.click()
            

                print(""" RESULT SEARCH """)
                start = end+1
                end = start+9
                start_row = end_row+1
                end_row = start_row+9

                time.sleep(0.1)
                for i, elem in enumerate(WebDriverWait(navigateur, 8).until(EC.presence_of_all_elements_located((By.XPATH, "//ul[@id='page_"+str(start)+"-"+str(end)+"']/li[@class='result']/div/div[@class='media-body']")))):
                    soup = BeautifulSoup(elem.get_attribute("innerHTML"), 'lxml') # Parse the HTML as a string
                    print(str(start+i) +" " + bcolors.WARNYELLOW + self.cleanhtmls(str(soup.find_all("h2")[0])).strip() + bcolors.ENDC)
                    for a in range(0, len(soup.find_all("p"))):
                        if a == 0:
                            print(bcolors.OKGREEN + self.cleanhtmls(str(soup.find_all("p")[0])) +  bcolors.ENDC + "\n" + bcolors.OKBLUE + self.cleanhtmls(str(soup.find_all("p")[1])) + bcolors.ENDC)
                        if a == 1:
                            print(bcolors.OKGREEN + self.cleanhtmls(str(soup.find_all("p")[2])) +  bcolors.ENDC + "\n" + bcolors.OKBLUE + self.cleanhtmls(str(soup.find_all("p")[3])) + bcolors.ENDC)
                    print()
                row = row + 1

                print()

        return True

    def cv(self, navigateur):
        print()

        for elem in WebDriverWait(navigateur, 8).until(EC.presence_of_all_elements_located((By.XPATH, "//h2[@class='category-title']/a"))):
            if elem.get_attribute("innerHTML") == "Mes candidatures,<br> CV et propositions":
                print(bcolors.OKGREEN + "click on '" + elem.get_attribute("innerHTML")+"'" + bcolors.ENDC)
                elem.click()
                break

        for elem in WebDriverWait(navigateur, 8).until(EC.presence_of_all_elements_located((By.XPATH, "//h2[@class='category-title']/a"))):
            if elem.get_attribute("innerHTML") == "Mes <br>CV":
                print(bcolors.OKGREEN + "click on '" + elem.get_attribute("innerHTML")+"'"+ bcolors.ENDC)
                elem.click()
                break


        for i, elem in enumerate(WebDriverWait(navigateur, 8).until(EC.presence_of_all_elements_located((By.XPATH, "//h2[@class='block-title']/a")))):
            print()
            cvspan = WebDriverWait(navigateur, 8).until(EC.presence_of_all_elements_located((By.XPATH, "//h2[@class='block-title']/span[@class='date-refresh ng-scope']")))
            print(bcolors.OKBLUE + elem.get_attribute("innerHTML") + " ( " + self.cleanhtml(cvspan[i].get_attribute("outerHTML")).strip() + "(s) ) "+ bcolors.ENDC)
            
            try:
               cvsupdate = WebDriverWait(navigateur, 8).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='hd']/span[@class='flag-unit']/span[@class='flag-txt ng-binding']")))
               print("\033[0;33m" + bcolors.UNDERLINE + bcolors.BOLD +" > " +cvsupdate[i].get_attribute("innerHTML")+ " < \033[0m")
            except:
               pass

            cvspan = WebDriverWait(navigateur, 8).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='primary']/div[@class='parallel-unit']/span[@class='value ng-binding']")))
            print(" > " + cvspan[i].get_attribute("innerHTML"))


    def actualisation(self, navigateur):
        try:
            try:
                check_actualisation = WebDriverWait(navigateur, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='feature-unit row-2 u-feature span-3']/div[2]/div[2]/p")))
                if "Vous avez déjà déclaré votre situation pour cette période" in check_actualisation.get_attribute("innerHTML"):
                    print(bcolors.FAIL + "Vous êtes déjà actualiser." + bcolors.ENDC)
                    return False
            except:
                return False

            for elem in WebDriverWait(navigateur, 8).until(EC.presence_of_all_elements_located((By.XPATH, "//span/a"))):
                if elem.get_attribute("innerHTML") == "Je m'actualise ?":
                    print("click on '" + elem.get_attribute("innerHTML")+"' ")
                    elem.click()
                    break

            # Etes-vous inscrit à une session de formation ou suivez-vous une formation ?
            formationOui = WebDriverWait(navigateur, 8).until(EC.presence_of_element_located((By.XPATH, "//label[@for='formationOui']/strong")))
            formationNon = WebDriverWait(navigateur, 8).until(EC.presence_of_element_located((By.XPATH, "//label[@for='formationNon']/strong")))
 
            if Profile[sys.argv[2]][3] == "Oui" or Profile[sys.argv[2]][3] == "oui":
                print("Etes-vous inscrit à une session de formation ou suivez-vous une formation ? click on 'Oui'")
                formationOui.click()

            if Profile[sys.argv[2]][3] == "Non" or Profile[sys.argv[2]][3] == "non":
                print("Etes-vous inscrit à une session de formation ou suivez-vous une formation ? click on 'Non'")
                formationNon.click()

            for elem in WebDriverWait(navigateur, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//button[@class='js-only']"))):
                if elem.get_attribute("innerHTML") == "Valider":
                    elem.click()
                    break

            #Avez-vous travaillé ?
            TravailleOui = WebDriverWait(navigateur, 10).until(EC.presence_of_element_located((By.XPATH, "//label[@for='blocTravail-open']/input")))
            TravailleNon = WebDriverWait(navigateur, 10).until(EC.presence_of_element_located((By.XPATH, "//label[@for='blocTravail-close']/input")))

            if Profile[sys.argv[2]][4] == "Oui" or Profile[sys.argv[2]][4] == "oui":
                print("Avez-vous travaillé ? click on 'Oui'")
                TravailleOui.click()

            if Profile[sys.argv[2]][4] == "Non" or Profile[sys.argv[2]][4] == "non":
                print("Avez-vous travaillé ? click on 'Non'")
                TravailleNon.click()


            #Avez-vous été en stage ?
            StageOui = WebDriverWait(navigateur, 10).until(EC.presence_of_element_located((By.XPATH, "//label[@for='blocStage-open']/input")))
            StageNon = WebDriverWait(navigateur, 10).until(EC.presence_of_element_located((By.XPATH, "//label[@for='blocStage-close']/input")))

            if Profile[sys.argv[2]][5] == "Oui" or Profile[sys.argv[2]][5] == "oui":
                print("Avez-vous été en stage ? click on 'Oui'")
                StageOui.click()

            if Profile[sys.argv[2]][5] == "Non" or Profile[sys.argv[2]][5] == "non":
                print("Avez-vous été en stage ? click on 'Non'")
                StageNon.click()
           
            #Avez-vous été en arrêt maladie ?
            MaladieOui = WebDriverWait(navigateur, 10).until(EC.presence_of_element_located((By.XPATH, "//label[@for='blocMaladie-open']/input")))
            MaladieNon = WebDriverWait(navigateur, 10).until(EC.presence_of_element_located((By.XPATH, "//label[@for='blocMaladie-close']/input")))

            if Profile[sys.argv[2]][6] == "Oui" or Profile[sys.argv[2]][6] == "oui":
                print("Avez-vous été en arrêt maladie ? click on 'Oui'")
                MaladieOui.click()

            if Profile[sys.argv[2]][6] == "Non" or Profile[sys.argv[2]][6] == "non":
                print("Avez-vous été en arrêt maladie ? click on 'Non'")
                MaladieNon.click()
            
            #Percevez-vous une nouvelle pension retraite ?
            RetraiteOui = WebDriverWait(navigateur, 10).until(EC.presence_of_element_located((By.XPATH, "//label[@for='blocRetraite-open']/input")))
            RetraiteNon = WebDriverWait(navigateur, 10).until(EC.presence_of_element_located((By.XPATH, "//label[@for='blocRetraite-close']/input")))

            if Profile[sys.argv[2]][7] == "Oui" or Profile[sys.argv[2]][7] == "oui":
                print("Percevez-vous une nouvelle pension retraite ? click on 'Oui'")
                RetraiteOui.click()

            if Profile[sys.argv[2]][7] == "Non" or Profile[sys.argv[2]][7] == "non":
                print("Percevez-vous une nouvelle pension retraite ? click on 'Non'")
                RetraiteNon.click()

            #Percevez-vous une nouvelle pension d'invalidité de 2ème ou 3ème catégorie ?
            InvaliditeOui = WebDriverWait(navigateur, 10).until(EC.presence_of_element_located((By.XPATH, "//label[@for='blocInvalidite-open']/input")))
            InvaliditeNon = WebDriverWait(navigateur, 10).until(EC.presence_of_element_located((By.XPATH, "//label[@for='blocInvalidite-close']/input")))

            if Profile[sys.argv[2]][8] == "Oui" or Profile[sys.argv[2]][8] == "oui":
                print("Percevez-vous une nouvelle pension d'invalidité de 2ème ou 3ème catégorie ? click on 'Oui'")
                InvaliditeOui.click()

            if Profile[sys.argv[2]][8] == "Non" or Profile[sys.argv[2]][8] == "non":
                print("Percevez-vous une nouvelle pension d'invalidité de 2ème ou 3ème catégorie ? click on 'Non'")
                InvaliditeNon.click()
            

            #Etes-vous toujours à la recherche d'un emploi ?
            RechercheOui = WebDriverWait(navigateur, 10).until(EC.presence_of_element_located((By.XPATH, "//label[@for='blocRecherche-close']/input")))
            RechercheNon = WebDriverWait(navigateur, 10).until(EC.presence_of_element_located((By.XPATH, "//label[@for='blocRecherche-open']/input")))

            if Profile[sys.argv[2]][9] == "Oui" or Profile[sys.argv[2]][9] == "oui":
                print("Etes-vous toujours à la recherche d'un emploi ? click on 'Oui'")
                RechercheOui.click()

            if Profile[sys.argv[2]][9] == "Non" or Profile[sys.argv[2]][9] == "non":
                print("Etes-vous toujours à la recherche d'un emploi ? click on 'Non'")
                RechercheNon.click()
        except:
            return False

    def close(self, navigateur):
        navigateur.close()
        exit()

if __name__ == '__main__':
    navigateur = PoleEmplois(Profile[sys.argv[2]][0], Profile[sys.argv[2]][1], False)
