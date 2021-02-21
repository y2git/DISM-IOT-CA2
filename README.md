# ST0324 : INTERNET OF THINGS
## DIPLOMA IN INFOCOMM SECURITY MANAGEMENT (DISM)
## IOT 21 CA2 step-by-step tutorial
The IOT CA2 github repo of Quah Yong Yao (P1821833) and Chua Yonglin (P1804234). Team name: W and Weedy.

This link contains the Bootstrap theme for this project's web interface: https://startbootstrap.com/theme/sb-admin-2
</br></br>

# 1. Overview of Smart Doorbell
This application is a smart doorbell with Response and “At Home” Time-Out feature. The target audience are home owners which desire a simple response to visitors outside their doorstep. This app allows home owners to receive an alert of visitors outside their door where-ever they are and give a simple response to their visitors if the home owners are unable to answer the door immediately.
</br>
- This Smart Doorbell has a quick response and timeout feature to reply to anyone outside of the doorstep. 
- The doorbell records the light value using LDR attached and the time when the button is pressed and stores it into DynamoDB.
- Other than listening to button responses, the doorbell will also listen for the changes to timeout settings on the web application hosted on our AWS EC2 web server and adjust itself periodically. 
- The web application will display a real time light value recorded from the light sensor on our RPI setup, it will also provide a historical graph of the 10 most recent button presses.
- The current configuration of the smart doorbell’s simple system settings will also be displayed on the web app.
</br>
For more information on this, visit https://youtu.be/bp0hbBvVWWU for our demonstration.

## 1.1 How the final RPI setup looks like
![alt text](https://github.com/y2git/DISM-IOT-CA2/blob/main/sample_images/rpi_setup.PNG)
## 1.2 How the web application looks like
![alt_text](https://github.com/y2git/DISM-IOT-CA2/blob/main/sample_images/web1.PNG)
![alt_text](https://github.com/y2git/DISM-IOT-CA2/blob/main/sample_images/web2.PNG)
## 1.3 Telegram Notification Example
![alt_text](https://github.com/y2git/DISM-IOT-CA2/blob/main/sample_images/telegram_sample.jpg)
## 1.4 System Architecture
![alt_text](https://github.com/y2git/DISM-IOT-CA2/blob/main/sample_images/IOT_system_architecture.png)
# 2. Hardware
## 2.1 Hardware Requirements
- 1 Light-Dependant Resistor (LDR)
- 2 LEDs (Red and Yellow)
- 1 Button
- 4 10K ohms Resistors
- 1 MCP3008 ADC
## 2.2 Hardware Setup
![alt_text](https://github.com/y2git/DISM-IOT-CA2/blob/main/sample_images/CA2_fritzing.png)
# 3. Software Requirements and installation
Install via pip:
- telepot
- mysql-connector-python
- gevent 
- configparser
- awscli
- AWSIoTPythonSDK
- botocore
- boto3
# 4. Running the Application
*Note make sure all IOT Practicals regarding AWS has been completed first:

1)	First connect the hardware, as shown in Section 2: Fritzing Diagram.
2)	Set up a table called “ButtonPress” in DynamoDB.
3)	Dump your AWSCerts under the folder DISM-IOT-CA2/RPIfolder/AWSCert/
4)	Using an editor, change the details in host.cfg file located in DISM-IOT-CA2/RPIfolder/etc/ to your own details
5)	Transfer the folders “RPIfolder” and “Webserver” to your RPI and your EC2 instance respectively.
6)	On the RPI, run mainmain.py to start the Smart Doorbell device.
7)	On the EC2 instance, run server.py to start the web application.

