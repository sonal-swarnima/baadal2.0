from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from pyvirtualdisplay import Display


display = Display(visible=0, size=(800, 600))
display.start()

# now Firefox will run in a virtual display. 
# you will not see the browser.
driver = webdriver.Firefox()
driver.implicitly_wait(10)
driver.get('http://127.0.0.1:8000/testapp/')
driver.find_element_by_xpath("//input[@value='3']").click()
driver.find_element_by_xpath("//input[@type='submit']").click()



display.stop()
