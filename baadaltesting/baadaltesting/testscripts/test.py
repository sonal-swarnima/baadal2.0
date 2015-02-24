import MySQLdb as mdb
import unittest
import logging
import datetime
import threading
import logging.config
import xml.etree.ElementTree as ET
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
class test(unittest.TestCase):
	
	def test_genric(self):
		db=mdb.connect("10.208.21.111","baadaltesting","test_baadal","baadal")
		tree = ET.parse('testdata.xml')# parsing the xml file
		root = tree.getroot()
		logging.config.fileConfig("logging.conf") 
		for i in xrange(0,len(root)):
			for j in xrange(0,len(root[i])):
				logger = logging.getLogger(root[i].get("name"))# create logger
				self.driver = webdriver.Firefox()#connect to server
				driver = self.driver
				driver.implicitly_wait(20)
				driver.get(root[i].get("url")) #url to the page to be hit 
				driver.find_element_by_link_text(root[i].get("href")).click()
				for k in xrange(0,len(root[i][j])):
					current_time=datetime.datetime.now()
					if root[i][j][k].get("type")=="input": #checking for input fields
						field = driver.find_element_by_id(root[i][j][k].get("id"))
						if root[i][j][k].text!=None:
							field.send_keys(root[i][j][k].text) # sending the user name/password/vm name/purpose etc
							if root[i][j][k].get("id")=="user_username":	
								usr_name=(root[i][j][k].text)
						else:
							if root[i][j][k].get("id")=="user_username":	
								usr_name=" "
							if root[i][j][k].get("id")=="vm_data_vm_name":
								field.send_keys(str(current_time))
					elif root[i][j][k].get("type")=="submit": #checking for submit button
						driver.find_element_by_xpath(root[i][j][k].text).click()
						cursor1=db.cursor()
						cursor1.execute(root[i].get("query1"),(usr_name)) 
						row= cursor1.fetchone()
						if cursor1.rowcount!=0:
							cursor2=db.cursor() #create object of database cursor
							cursor2.execute(root[i].get("query2"),(str(row[0]))) #execute sql query
							row = cursor2.fetchone()
							if cursor2.rowcount!=0:
								if  (row[0]>=current_time) | ("Logged-in" in str(row[1])):
									logger.debug(root[i][j].get("value") +': Result:Valid Login') #logging the report
								else :
									logger.debug(root[i][j].get("value") +': Result:Invalid Login') #logging the report
						else:
							logger.debug(root[i][j].get("value") +': Result:Invalid Loginss') #logging the report
					elif root[i][j][k].get("type")=="button":
						driver.find_element_by_xpath(root[i][j][k].text).click()
					elif root[i][j][k].get("type")=="href":
						driver.find_element_by_link_text(root[i][j][k].text).click()#redirecting on other page
					elif root[i][j][k].get("type")=="select":
				 		driver.find_element_by_xpath(root[i][j][k].text).click()# selecting from dropdown menu
					elif root[i][j][k].get("type")=="class":
						cursor3=db.cursor()
						cursor3.execute(root[i].get("query3"))
						cursor3.execute(root[i].get("query3"),(str(monikay)))
						query3=cursor3.fetchall()
						x=cursor3.rowcount
						field=driver.find_elements_by_tag_name("tr")
						m=0
						for n in field:
							a=n.text.split()
							if a[0]!="Name":
								print a[0]
								print query3[m][0]
								if a[0]==query3[m][0]:
									logger.debug(root[i][j].get("value") +': Result:correct input') 
								else:
									logger.debug(root[i][j].get("value") +': Result:Incorrect input') 
								m=m+1
						
					elif root[i][j][k].get("type")=="img":
						if root[i][j][k].get("name") in ["Pause","Gracefully","Forcefully","Migrate","Request","Lock","Edit","Setting","Resume"]:
								driver.find_element_by_xpath(root[i][j][k].text).click()
								
					elif root[i][j][k].get("type")=="tagname":
						field=driver.find_elements_by_tag_name("tr")
						cursor4=db.cursor()
						cursor4.execute("select host_ip from host")
						y=cursor4.fetchall()
						x=cursor4.rowcount
						for p in xrange(0,x):
							if y[p][0] in "Host IP : 10.208.21.68":
								cursor5=db.cursor()		
								cursor5.execute(root[i].get("query4"))
								query3=cursor5.fetchall()
								m=0
								for n in field:
									a=n.text.split()
									if a[0]!="Name":
										print a[0]
										print query3[m][0]
										if a[0]==query3[m][0]:
											logger.debug(root[i][j].get("value") +': Result:correct input') 
										else:
											logger.debug(root[i][j].get("value") +': Result:Incorrect input') 
										m=m+1
							
					else:
						logging.debug("report problem") #logging the report
				#self.driver.close()#disconnect from server
		'''def fun(field,query3):
		m=0
		for n in field:
			a=n.text.split()
			if a[0]!="Name":
				print a[0]
				print query3[m][0]
				if a[0]==query3[m][0]:
					logger.debug(root[i][j].get("value") +': Result:correct input') 
				else:
					logger.debug(root[i][j].get("value") +': Result:Incorrect input') 
				m=m+1'''
		
		db.commit()
		cursor1.close()
		cursor2.close()
		cursor3.close()
		cursor4.close()
		db.close()
 
if __name__ == "__main__": #to run the methods of Login_test class
    unittest.main()
   
   





































