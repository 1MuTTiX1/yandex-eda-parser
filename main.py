from selenium import webdriver
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup


fireFoxOptions = webdriver.FirefoxOptions()
fireFoxOptions.add_argument("--window-size=1920,1080")
fireFoxOptions.add_argument('--start-maximized')
fireFoxOptions.add_argument('--disable-gpu')
fireFoxOptions.add_argument("--headless")

driver = webdriver.Firefox(options=fireFoxOptions)
url = 'https://eats.yandex.com/ru-am/Yerevan?shippingType=delivery'
try:

#Функция принимает адреса в качестве аргумента и выдаёт список Url адресов всех ресторанов в txt для дальнейшей обработки    
    def colector_url(address):
        driver.maximize_window()
        driver.get(url=url)
        time.sleep(3)

#Блок по вводу интересуещего адреса

        clickable_search = driver.find_element(By.CLASS_NAME, 'DesktopAddressButton_address')
        ActionChains(driver).click(clickable_search).perform()
        time.sleep(1)
        write = driver.find_element(By.XPATH, '/html/body/div[3]/div/div/div/div/div[1]/div[2]/div/div/div[1]/input')
        write.send_keys(address)
        time.sleep(3)
        write.send_keys(Keys.SPACE)
        time.sleep(3)
        clickable_place = driver.find_element(By.ID, 'react-autowhatever-1--item-0')
        ActionChains(driver).click(clickable_place).perform()
        time.sleep(2)
        ok = driver.find_element(By.XPATH, '/html/body/div[3]/div/div/div/div/div[1]/div[2]/button')
        ActionChains(driver).click(ok).perform()

#Блок скролла страницы если есть вариант более производительней пишите(если знаете как сделать скрол через selenium и более оптимизированно, жду откликов)
        a = 0
        while True:
            driver.find_element(By.CSS_SELECTOR, 'body').send_keys(Keys.CONTROL + Keys.END)
            time.sleep(4)
            soup = BeautifulSoup(driver.page_source, 'lxml')
            find = soup.find_all('div', 'PlaceListBduItem_placesListItem PlaceListBduItem_lg')
            if a == len(find):
                print(f'Собрал: {a}')
                a = 0
                break
            else:
                a = len(find)
        time.sleep(5)


#Поиск URL
        carts = soup.find_all('div', 'PlaceListBduItem_placesListItem PlaceListBduItem_lg')
        url_list = []
        for i in carts:
            ur = f'https://eats.yandex.com{i.find('a').get('href')}'
            url_list.append(ur)

#Запись URL(Если наете как более красово сделать запись со спец знаками и более оптимизировано жду отзывов)
        with open(f'{address.replace(',','').replace('/','_')}.txt','w',encoding="utf-8") as f:
            for urls in url_list:
                f.write(f'{urls}\n')





except Exception as ex:
    print(ex)
finally:
    driver.close()
    driver.quit()
