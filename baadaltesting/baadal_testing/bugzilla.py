from selenium import webdriver
import sys
from selenium.webdriver.common.keys import Keys


# now Firefox will run in a virtual display. 
# you will not see the browser.
driver = webdriver.Firefox()
driver.implicitly_wait(30)
driver.get('http://10.237.20.205/bugzilla/')
driver.find_element_by_link_text("Log In").click()
driver.find_element_by_id('Bugzilla_login_top').send_keys("jyoti690saini@gmail.com")
driver.find_element_by_id('Bugzilla_password_top').send_keys("jyotisaini")
driver.find_element_by_xpath("//input[@id='log_in_top']").click()
driver.find_element_by_id("enter_bug").click()
driver.find_element_by_id('short_desc').send_keys("Bug in baadal")
driver.find_element_by_id('comment').click()
driver.find_element_by_id('comment').send_keys(str(sys.argv[1]))
driver.find_element_by_id('commit').click()
driver.find_element_by_id('bz_assignee_edit_action').click()
driver.find_element_by_id('assigned_to').send_keys("sonal.swarnima@gmail.com ")
driver.find_element_by_id('commit').click()
driver.close()
