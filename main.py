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
    def colector_url(address):
        driver.maximize_window()
        driver.get(url=url)
        time.sleep(3)

#Блок по вводу интересуещего адреса и выборавравренмена на завтра 15:00

        clickable_search = driver.find_element(By.CLASS_NAME, 'DesktopAddressButton_address')
        ActionChains(driver).click(clickable_search).perform()
        time.sleep(1)
        write = driver.find_element(By.XPATH, '/html/body/div[3]/div/div/div/div/div[1]/div[2]/div/div/div[1]/input')
        write.send_keys(address)
        time.sleep(1)
        write.send_keys(Keys.SPACE)
        time.sleep(2)
        clickable_place = driver.find_element(By.ID, 'react-autowhatever-1--item-0')
        ActionChains(driver).click(clickable_place).perform()
        time.sleep(1)
        ok = driver.find_element(By.XPATH, '/html/body/div[3]/div/div/div/div/div[1]/div[2]/button')
        ActionChains(driver).click(ok).perform()
        time.sleep(3)
        click_time = driver.find_element(By.XPATH,'/html/body/div[1]/div/div/div[1]/main/div/div/main/div[3]/div/div/div')
        ActionChains(driver).click(click_time).perform()
        time.sleep(1)
        click_day = driver.find_element(By.XPATH,'/html/body/div[3]/div/div/div/div/div/div[1]/button[2]')
        ActionChains(driver).click(click_day).perform()
        time.sleep(1)
        time_click = driver.find_element(By.XPATH,'/html/body/div[3]/div/div/div/div/div/div[2]/button[31]')
        driver.execute_script("arguments[0].scrollIntoView();", time_click)
        ActionChains(driver).click(time_click).perform()
        time.sleep(3)


#Блок скролла страницы и поиска Url ресторана
        a = 0
        b = 0
        url_list = []
        while True:
            driver.find_element(By.CSS_SELECTOR, 'body').send_keys(Keys.CONTROL + Keys.END)
            time.sleep(2)

            soup = BeautifulSoup(driver.page_source, 'lxml')
            find = soup.find_all('div', 'PlaceListBduItem_placesListItem PlaceListBduItem_lg')
            for i in find:
                if i.find('a'):
                    ur = f'https://eats.yandex.com{i.find('a').get('href')}'
                    url_list.append(ur)
            if a == len(find):
                print(f'Собрал: {a}')
                a = 0
                break
            else:
                a = len(find)

#Запись URL

        url_clear = list(set(url_list))

        with open(f'F:/sql_base/eda_yandex_url/{address.replace(',','').replace('/','_')}.txt','w',encoding="utf-8") as f:
            for urls in url_clear:
                f.write(f'{urls}\n')

#Запуск функции
    colector_url('Ваш адрес')

except Exception as ex:
    print(ex)
finally:
    driver.close()
    driver.quit()

