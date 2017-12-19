# Network_MyAPI
Demonstrate web service interactions using REST
• Build Requirements
• Flask Microframework
• Including Flask-Discoverer extension
• Python Requests Library
• HTTP Basic Authentication
• Auth data maintained in MongoDB datastore
• Service Advertisement
• Zeroconf
• Supported Services
• RGB LED Controller
• Canvas Interaction
• Service of your choice accepting GET and POST requests

![image](https://user-images.githubusercontent.com/24555370/34175912-03b7ca12-e4cc-11e7-970b-c32a82b70191.png)


Service interactions:
1. Canvas_get_courses() is a GET method. The route is /Canvas/Courses. It allows the current user to get
his/her courses and stored the all the courses under the root directory inside of a course.txt file.
 Curl command used: curl -u admin:secret http://ip:5000/Canvas/Courses
2. getImage() is a GET method. The route is /googleplace. It allows the user to input a place and return a
picture of the place stored in the root directory.
 Curl command used: curl -u admin:secret http://ip:5000/googleplace?place=virginia tech
 Curl command used: curl -u admin:secret http://ip:5000/googleplace?place= Bellagio
 Curl command used: curl -u admin:secret http://ip:5000/googleplace?place= <place>
3. weather() is a POST method. The route is /weather. It allows the user to post a US zip code and return
a txt file. The returned txt file will have the same name as the zip code. For example if the input zip
code is 24061, then the output file will be 24061.txt
 Curl command used: curl -X POST -u admin:secret -F “zip=<zipcode>”
http://ip:5000/weather
4. list_func() is a POST method. The route is /LIST. It allows user to add event or delete event. The
response will be the event json.
 Curl command used: curl -X POST -u admin:secret -F “operation=<operation>”
-F “event=<event>” http://ip:5000/LIST
Note: the operation methods are “add” and “delete”
