import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import mysql.connector
import time
from datetime import date

def import_database():
    mydb = mysql.connector.connect(
    host = 'scraped-jobs-db.csf6csfadawz.us-east-1.rds.amazonaws.com',
    database= 'scraped_jobs_db',
    user = 'jobs_db_user',
    password = '1jobs_p2ass_scra4ped_we6b_%'
    )
    cur = mydb.cursor()
    cur.execute('truncate table gmc_data')
    cur.execute('select ProfessionalRegistrationNumber from MAST_PERFORMER_LIST limit 100')
    urls = [f'https://www.gmc-uk.org/doctors/{x[0]}' for x in cur]
    cur.close()
    mydb.close()
    return urls

def captcha_pass(url):
    driver= uc.Chrome()
    driver.get(url)
    driver.maximize_window()
    time.sleep(10)
    return driver

def upload_to_database(data):
    mydb = mysql.connector.connect(
    host = 'scraped-jobs-db.csf6csfadawz.us-east-1.rds.amazonaws.com',
    database= 'scraped_jobs_db',
    user = 'jobs_db_user',
    password = '1jobs_p2ass_scra4ped_we6b_%'
    )
    cur = mydb.cursor()
    query = 'insert into gmc_data values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    cur.execute(query,data) 
    mydb.commit()
    cur.close()
    mydb.close()

def main():
    urls = import_database()
    driver = captcha_pass(urls[0])

    for url in urls:
        driver.get(url)
        gmc_nb = url.split('/')[-1]
        name = driver.find_element(By.XPATH,'//*[@id="doctorNameId"]').text.replace('.','').strip().split(' ')
        first_name = name[0]
        last_name = name[-1]
        middle_name = (' ').join(name[1:-1])
        if len(name)==1:
            last_name = ''
        name = (' ').join(name)
        gmc_status = driver.find_element(By.XPATH,'//*[@id="main"]/div/div/section[1]/div/div/div/div').text
        if 'Not' in gmc_status:
            gmc_status = 'Not Registered'
        doctor_register = driver.find_element(By.XPATH,'//*[@id="main"]/div/div/section[2]/div[1]/div[2]/span[2]/div').text
        if 'not' in doctor_register:
            doctor_register='NOT on GP Register'
        else:
            doctor_register='GP Register'
        try:
            date_register = (' ').join(driver.find_element(By.XPATH,'//*[@id="main"]/div/div/section[2]/div[1]/p').text.split(' ')[1:])
            conv= time.strptime(date_register,'%d %b %Y')
            date_register = time.strftime("%d %m %Y",conv).split(' ')
            date_register = date(int(date_register[2]),int(date_register[1]),int(date_register[0])) 
        except:
            date_register = ''
        
        try:
            specialist = (' ').join(driver.find_element(By.XPATH,'//*[@id="main"]/div/div/section[2]/div[2]/ul/li/span').text.split(' ')[:-4])
        except:
            specialist = ''
        try:
            trainer = driver.find_element(By.XPATH,'//*[@id="main"]/div/div/section[2]/div[1]/ul/li').text
            trainer = 'Yes'
        except:
            trainer = 'No'
        qualification = driver.find_element(By.XPATH,'//*[@id="main"]/div/div/section[3]/div[2]/div[2]/div').text.split(' ')

        for i in range(len(qualification)):
            if qualification[i].isnumeric():
                qualification_year = qualification[i]
                university = (' ').join(qualification[i+1:])
                break
        for i in range(5,10):
            gender = driver.find_element(By.XPATH,f'//*[@id="main"]/div/div/section[3]/div[2]/div[{i}]').text
            if gender == 'Gender':
                gender = driver.find_element(By.XPATH,f'//*[@id="main"]/div/div/section[3]/div[2]/div[{i+1}]').text
                registration_date = driver.find_element(By.XPATH,f'//*[@id="main"]/div/div/section[3]/div[2]/div[{i-1}]').text
                conv= time.strptime(registration_date,'%d %b %Y')
                registration_date = time.strftime("%d %m %Y",conv).split(' ')
                registration_date = date(int(registration_date[2]),int(registration_date[1]),int(registration_date[0])) 
                break
        
        data = (gmc_nb,name,first_name,middle_name,last_name,gmc_status,doctor_register,date_register,specialist,trainer,qualification_year,university,registration_date,gender)
        print(data)
        upload_to_database(data)
    driver.close()
main()
