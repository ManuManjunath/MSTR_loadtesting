# Purpose: To auto login users to MSTR Merch OIDC
""" Logs into MSTR as test users and logs response times. """

# References -
# http://getstatuscode.com/200
# https://selenium-python.readthedocs.io/api.html
# https://blog.testproject.io/2018/02/20/chrome-headless-selenium-python-linux-servers/ - To run Chrome in headless mode


import csv
import multiprocessing
import os
import datetime
from selenium import webdriver
import timeit
import time
import socket
import random
# import sys

cpu_count = os.cpu_count()
# sys.stdout = open("Logs.txt", "a")
mstr_url = 'https://mstr.enterprise.com/MicroStrategy/servlet/mstrWeb'
open_rep = 'https://mstr.enterprise.com/MicroStrategy/servlet/mstrWeb?Server=blah&Project=blah&Port=blah&evt=4001&src=mstrWeb&visMode=0&reportViewMode=1&reportID=blah'
log_type = 'browser'
InputFile = "/etc/loadtest/LTESTIDPWD.csv"
hostname = socket.gethostname()
TestResults = "/etc/loadtest/logs/Results_Merch_" + hostname + ".csv"


def msamerch(row):
    TestStartTime = ">" + str(datetime.datetime.now())
    print("########", TestStartTime)
    test_user_id = row[0]
    print("Running test for - ", row[0], " - ", row[2])
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(executable_path='/etc/loadtest/chromedriver2',chrome_options=chrome_options, service_args=['--verbose', '--log-path=/tmp/chromedriver.log'])
    # On mac - driver = webdriver.Chrome("/Users/z0019z3/Downloads/Chrome_driver/mac/chromedriver")
    # driver = webdriver.Chrome()
    driver.set_page_load_timeout(30)
    driver.delete_all_cookies()
    Start_Launch = timeit.default_timer()
    driver.implicitly_wait(20)
    try:
        driver.get(mstr_url)
        driver.maximize_window()
        print("Page redirected to - ", driver.current_url)
        validate_launch = driver.find_element_by_id("loginID").is_enabled()
        # print("MSTR Page launched? = ", validate_launch)
        Launch_Logs = driver.get_log(log_type)
        if validate_launch == True:
            LnchRespCode = 'Success'
        elif "the server responded with a status of" in str(Launch_Logs):
            ForLnchRespCode = str(Launch_Logs).split("the server responded with a status of ", 1)[1]
            LnchRespCode = ForLnchRespCode[:3]
        else:
            LnchRespCode = 'Unknown Error'
    except:
        print("Not the right page")
        Launch_Logs = driver.get_log(log_type)
        if "the server responded with a status of" in str(Launch_Logs):
            ForLnchRespCode = str(Launch_Logs).split("the server responded with a status of ", 1)[1]
            LnchRespCode = ForLnchRespCode[:3]
        else:
            LnchRespCode = 'Unknown Error'
        LgnRespCode = "Page didn't Launch"
        Resp_Time_Login = ""
    finally:
        print(Launch_Logs)
    End_Launch = timeit.default_timer()
    Resp_Time_Launch = round(float(format(End_Launch - Start_Launch)), 2)
    time.sleep(10)
    try:
        Start_Login = timeit.default_timer()
        driver.find_element_by_id("loginID").send_keys(row[0])
        driver.find_element_by_id("pass").send_keys(row[1])
        driver.find_element_by_class_name("submit-button").click()
        mstrLogo = str(driver.find_element_by_id("mstrLogo").is_enabled())
        # validate_login = driver.find_element_by_class_name("mstrInstruct").text
        # User_Assert = "Welcome " + row[2]
        Login_Logs = driver.get_log(log_type)
        if mstrLogo == "True":
            print("Login successful")
            LgnRespCode = 'Success'
        elif "the server responded with a status of" in str(Login_Logs):
            ForLgnRespCode = str(Login_Logs).split("the server responded with a status of ", 1)[1]
            LgnRespCode = ForLgnRespCode[:3]
        else:
            LgnRespCode = "Unknown Error"
    except:
        print("Problem during login")
        Login_Logs = driver.get_log(log_type)
        if "the server responded with a status of" in str(Login_Logs):
            ForLgnRespCode = str(Login_Logs).split("the server responded with a status of ", 1)[1]
            LgnRespCode = ForLgnRespCode[:3]
        else:
            LgnRespCode = "Unknown Error"
    finally:
        print(Login_Logs)
    End_Login = timeit.default_timer()
    Resp_Time_Login = round(float(format(End_Login - Start_Login)), 2)
    time.sleep(10)
    # Now run Report
    try:
        Start_Run_Rep = timeit.default_timer()
        driver.get(open_rep)
        Run_Logs = driver.get_log(log_type)
        if "the server responded with a status of" in str(Run_Logs):
            ForRunRespCode = str(Run_Logs).split("the server responded with a status of ", 1)[1]
            RunRespCode = ForRunRespCode[:3]
        else:
            RunRespCode = 'Success'
    except:
        print("Problem during report execution")
        RunRespCode = 'Unknown Error'
    finally:
        Run_Logs = driver.get_log(log_type)
        print(Run_Logs)
    End_Run_Rep = timeit.default_timer()
    Resp_Time_Run = round(float(format(End_Run_Rep - Start_Run_Rep)), 2)
    driver.close()
    driver.quit()
    results_list = [test_user_id, TestStartTime, Resp_Time_Launch, LnchRespCode, Resp_Time_Login, LgnRespCode, Resp_Time_Run, RunRespCode]
    print(results_list)
    with open(TestResults, "a", newline='') as WriteFile:
        wr = csv.writer(WriteFile, dialect='excel')
        wr.writerow(results_list)
    WriteFile.close()


"""
if __name__ == '__main__':
    with open(InputFile, 'r') as csvFile:
        reader = csv.reader(csvFile)
        with multiprocessing.Pool(cpu_count) as p:
            buffer = []
            for row_num, row in enumerate(reader):
                if row_num == 0:
                    continue
                buffer.append(row)
                # Call function once enough rows are read
                if row_num % cpu_count == 0:
                    p.map(msastores, buffer)
                    # Clear the buffer
                    buffer = []
                else:
                    # process left over rows
                    p.map(msamerch, buffer)
"""

if __name__ == '__main__':
    with open(InputFile, 'r') as csvFile:
        test_users = []        
        reader = csv.reader(csvFile)
        for row_num, row in enumerate(reader):
            test_users.append(row)
    random.shuffle(test_users)
    for a in test_users:
            msamerch(a)
