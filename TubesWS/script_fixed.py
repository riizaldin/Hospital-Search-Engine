import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException

def get_pagination_xpath(page_number):
    return f"/html[1]/body[1]/div[2]/div[1]/section[1]/div[1]/div[1]/div[3]/div[1]/div[2]/div[1]/div[2]/div[2]/div[3]/div[2]/div[1]/ul[1]/li[{page_number}]/a[1]"
def get_tenaga_xpath(page_number):
    return f"/html[1]/body[1]/div[2]/div[1]/section[1]/div[1]/div[1]/div[3]/div[1]/div[2]/div[1]/div[3]/div[2]/div[3]/div[2]/div[1]/ul[1]/li[{page_number}]/a[1]"

# Initialize a Chrome WebDriver instance
driver = webdriver.Chrome()

driver.get("https://sirs.kemkes.go.id/fo/home/dashboard_rs?id=12")
# hospital_list = driver.find_element(By.ID, "example3")
wait = WebDriverWait(driver, 10)
hospital_list = wait.until(EC.presence_of_element_located((By.ID, "example3")))
hospitals = WebDriverWait(hospital_list, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'tr')))
links = []
data_list = []
counter_link = 1
counter = 1
for hospital in hospitals:
    try:
        link = hospital.find_element(By.TAG_NAME, "a")
    except NoSuchElementException:
        continue
    link = link.get_attribute("href")
    if counter_link != 133:
        links.append(link)
    counter_link += 1

for link in links:
    driver.get(link)
    list_group = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'list-group-item')))
    all_info = []
    for list_item in list_group:
        try:
            info_rs = list_item.find_element(By.TAG_NAME, "a").text
        except NoSuchElementException:
            continue
        all_info.append(info_rs)
    nama = driver.find_element(By.XPATH, "/html[1]/body[1]/div[2]/div[1]/section[1]/div[1]/div[1]/div[2]/div[1]/div[2]/div[1]/div[1]/h3[1]").text
    alamat = driver.find_element(By.XPATH, "/html[1]/body[1]/div[2]/div[1]/section[1]/div[1]/div[1]/div[2]/div[1]/div[2]/ul[1]/li[1]/p[1]").text
    telepon = driver.find_element(By.XPATH, "/html[1]/body[1]/div[2]/div[1]/section[1]/div[1]/div[1]/div[2]/div[1]/div[2]/ul[1]/li[1]/p[2]").text
    jenis = all_info[0]
    kelas = all_info[1]
    blu = all_info[2]
    direktur = all_info[4]
    luas_tanah = all_info[5]
    luas_bangunan = all_info[6]

    tempat_tidur = []
    for i in range (1,50):
        try:
            kelas = driver.find_element(By.XPATH, "/html[1]/body[1]/div[2]/div[1]/section[1]/div[1]/div[1]/div[3]/div[1]/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/table[1]/tbody[1]/tr["+str(i)+"]/td[2]").text
            kapasitas = driver.find_element(By.XPATH, "/html[1]/body[1]/div[2]/div[1]/section[1]/div[1]/div[1]/div[3]/div[1]/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/table[1]/tbody[1]/tr["+str(i)+"]/td[3]").text
            if int(kapasitas) != 0:
                tempat_tidur.append({"kelas":kelas, "kapasitas":kapasitas})
        except NoSuchElementException:
            break


    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html[1]/body[1]/div[2]/div[1]/section[1]/div[1]/div[1]/div[3]/div[1]/div[1]/ul[1]/li[2]/a[1]"))).click()
    pelayanan = []
    pagination = driver.find_elements(By.CSS_SELECTOR,'#example6_paginate .pagination li a')
    if len(pagination) >= 2:  
        second_last = pagination[-2] 
        if second_last.text != "Previous":
            number_pelayanan = second_last.text
        else:
            number_pelayanan = 0
        number_pelayanan = int(number_pelayanan) + 3
        print("Text from second-to-last element:", number_pelayanan)
    else:
        print("Not enough elements in pagination")

    print(len(pagination))
    try:
        check_dot = driver.find_element(By.XPATH, "/html[1]/body[1]/div[2]/div[1]/section[1]/div[1]/div[1]/div[3]/div[1]/div[2]/div[1]/div[2]/div[2]/div[3]/div[2]/div[1]/ul[1]/li[7]").text
        try:
            int(check_dot)
            banyak = False
        except ValueError:
            if check_dot == "Next":
                banyak = False
            else:
                banyak = True
    except NoSuchElementException:
        banyak = False
    
    for i in range (3,number_pelayanan):
        for j in range (1,11):
            try:
                hasil = driver.find_element(By.XPATH, "/html[1]/body[1]/div[2]/div[1]/section[1]/div[1]/div[1]/div[3]/div[1]/div[2]/div[1]/div[2]/div[2]/div[2]/div[1]/table[1]/tbody[1]/tr["+str(j)+"]/td[2]").text
                pelayanan.append(hasil)
            except NoSuchElementException:
                continue
            
        if not banyak:
            try:
                element_to_click = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, get_pagination_xpath(i)))).click()
            except ElementClickInterceptedException:
                break
        else:
            if i <= 6:
                try:
                    element_to_click = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,get_pagination_xpath(i)))).click()
                except ElementClickInterceptedException:
                    break
            elif i <= number_pelayanan- 4:
                try:
                    element_to_click = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, get_pagination_xpath(6)))).click()
                except ElementClickInterceptedException:
                    break
            elif i == number_pelayanan - 3:
                try:
                    element_to_click = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, get_pagination_xpath(7)))).click()
                except ElementClickInterceptedException:
                    break
            else:
                try:
                    element_to_click = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, get_pagination_xpath(8)))).click()
                except ElementClickInterceptedException:
                    break
    
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html[1]/body[1]/div[2]/div[1]/section[1]/div[1]/div[1]/div[3]/div[1]/div[1]/ul[1]/li[3]/a[1]"))).click()
    tenaga = []
    pagination_tenaga = driver.find_elements(By.CSS_SELECTOR,'#example7_paginate .pagination li a')
    if len(pagination_tenaga) >= 2:  
        second_last_tenaga = pagination_tenaga[-2] 
        if second_last_tenaga.text != "Previous":
            number_tenaga = second_last_tenaga.text
        else:
            number_tenaga = 0
        number_tenaga = int(number_tenaga) + 3
        print("Text from second-to-last tenaga element:", number_tenaga)
    else:
        print("Not enough elements in pagination")

    print(len(pagination_tenaga))
    try:
        check_dot_2 = driver.find_element(By.XPATH, "/html[1]/body[1]/div[2]/div[1]/section[1]/div[1]/div[1]/div[3]/div[1]/div[2]/div[1]/div[3]/div[2]/div[3]/div[2]/div[1]/ul[1]/li[7]").text
        try:
            int(check_dot_2)
            banyak_tenaga = False
        except ValueError:
            if check_dot_2 == "Next":
                banyak_tenaga = False
            else:
                banyak_tenaga = True

    except NoSuchElementException:
        banyak_tenaga = False

    print(banyak_tenaga)
    for i in range (3,number_tenaga):
        for j in range (1,11):
            try:
                grup = driver.find_element(By.XPATH, "/html[1]/body[1]/div[2]/div[1]/section[1]/div[1]/div[1]/div[3]/div[1]/div[2]/div[1]/div[3]/div[2]/div[2]/div[1]/table[1]/tbody[1]/tr["+str(j)+"]/td[2]").text
                sdm = driver.find_element(By.XPATH, "/html[1]/body[1]/div[2]/div[1]/section[1]/div[1]/div[1]/div[3]/div[1]/div[2]/div[1]/div[3]/div[2]/div[2]/div[1]/table[1]/tbody[1]/tr["+str(j)+"]/td[3]").text
                jumlah = driver.find_element(By.XPATH, "/html[1]/body[1]/div[2]/div[1]/section[1]/div[1]/div[1]/div[3]/div[1]/div[2]/div[1]/div[3]/div[2]/div[2]/div[1]/table[1]/tbody[1]/tr["+str(j)+"]/td[4]").text
                tenaga.append({"grup":grup, "sdm":sdm, "jumlah":jumlah})
            except NoSuchElementException:
                continue
        if not banyak_tenaga:
            try:
                element_to_click = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, get_tenaga_xpath(i)))).click()
            except ElementClickInterceptedException:
                break
        else:
            if i <= 6:
                try:
                    element_to_click = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, get_tenaga_xpath(i)))).click()
                except ElementClickInterceptedException:
                    break
            elif i <= number_tenaga - 4:
                print(i)
                try:
                    element_to_click = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, get_tenaga_xpath(6)))).click()
                except ElementClickInterceptedException:
                    break
            elif i == number_tenaga - 3:
                try:
                    element_to_click = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, get_tenaga_xpath(7)))).click()
                except ElementClickInterceptedException:
                    break
            else:
                try:
                    element_to_click = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, get_tenaga_xpath(8)))).click()
                except ElementClickInterceptedException:
                    break
    hospital = "Hospital" + str(counter)
    data = {
        "@type": "Hospital",
        "@id": hospital,
        "nama": nama,
        "jenis": jenis,
        "kelas": kelas,
        "blu": blu,
        "direktur": direktur,
        "luas_tanah": luas_tanah,
        "luas_bangunan": luas_bangunan,
        "alamat": alamat,
        "telepon": telepon,
        "pelayanan": pelayanan,
        "tempat_tidur": tempat_tidur,
        "tenaga": tenaga
    }
    data_list.append(data)
    counter += 1
    # Save data to JSON file
    with open('result.json', 'w') as json_file:
        json.dump(data_list, json_file, indent=2)

    
# Quit the Chrome WebDriver
driver.quit()