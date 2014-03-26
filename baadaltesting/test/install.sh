
#!/bin/sh
sudo apt-get update  # To get the latest package lists
sudo apt-get install mysql.connector python 
sudo pip install selenium  
sudo apt-get install python-parimiko
if [ stderr ]; then
echo "\n \n package not available "
fi

#etc.
