from flask import Flask, render_template, request, jsonify
from functools import wraps
import json
import sys
import param 
import requests 
import imghdr
from six.moves import input
from zeroconf import ServiceBrowser, Zeroconf
import socket
import pymongo
from pymongo import MongoClient
#from flask_restful import Resource, Api

from flask_discoverer import Discoverer, advertise

# Define the autodiscovery endpoint
DISCOVERER_PUBLISH_ENDPOINT = '/resources'
  # Advertise its own route within DISCOVERER_PUBLISH_ENDPOINT
DISCOVERER_SELF_PUBLISH = False
#from flask_restful import Resource, Api

app = Flask(__name__)
discoverer = Discoverer(app)

#adding authenticate method
#need to get username and password form mogoDB

led_ip = ''
led_port = 0
led_colors = ''
auth1 = ''
auth2 = ''
auth3 = ''

def check_auth(username, password):
    return (username == auth1[0] and password == auth1[1]) or (username == auth2[0] and password == auth2[1]) or (username == auth3[0] and password == auth3[1])
def authenticate():
    message = {'message': "Authenticate."}
    resp = jsonify(message)

    resp.status_code = 401
    resp.headers['WWW-Authenticate'] = 'Basic realm="Example"'

    return resp

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth: 
            return authenticate()

        elif not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/')
@requires_auth
def homepage():
    return "homepage"

@app.route("/secrets")
@requires_auth
def api_hello():
    return "Shhh this is top secret spy stuff!"

@app.route("/Canvas", methods = ['GET'])
@requires_auth
def Canvas_download():
    '''
    URL testing:
    1.http://127.0.0.1:5000/Canvas?file=a_file.txt&operation=download
    2.http://127.0.0.1:5000/Canvas?file=GeoLiteCity.dat&operation=download
    
    Error handling testing
    1.http://127.0.0.1:5000/Canvas?file=hello.txt&operation=download
        -return file not found

    2.http://127.0.0.1:5000/Canvas?file=GeoLiteCity.dat&operation=there
        -return operation method not supported
    '''

    #config param for downloading
    api_url = param.param['api_url']
    access_token = param.param['Canvas_access_token']
    file_name = request.args.get('file')
    operation = request.args.get('operation')
    headers = {'Authorization': 'Bearer %s' % access_token}
    if operation == "download":
        r = requests.get (api_url,headers = headers)
        response = r.json()

# check if canvas responses
        print(r.status_code)

# step2 search list of dicts
        for file_dict in response:
            if file_dict['filename'] == file_name:
                download_url = file_dict['url']
               
                
        
# step 3 sending get request using download url 
# error handling if the file is not found        
        try:
            response = requests.get(download_url)
        except UnboundLocalError:
            return "File not Found"


# check if download url responses
        print(response.status_code)

        with open(file_name, 'wb') as handle:
            for block in response.iter_content(1024):
                handle.write(block)
        return "File Downloaded"
    if operation != "download":
        return "the operation method is not support "

@app.route("/Canvas", methods = ['POST'])
@requires_auth
def Canvas_upload():
    '''
    tested commands will uploaded the files:

    curl -i -X POST -F "file=GeoLiteCit.dat" -F "operation=upload" http://173.30.19.222:5000/Canvas
    curl -i -X POST -F "file=a_file.txt" -F "operation=upload" http://173.30.19.222:5000/Canvas
    '''
    '''
    tested command will retrun error message, error handling 
    1. file name do not exist
    2. operations is not supported
    '''
    #canvas group page root dir
    api_url = param.param['api_url']
    #canvas token
    access_token = param.param['Canvas_access_token']
    headers = {'Authorization': 'Bearer %s' % access_token}
    
    get_file_name = request.form.get('file')
    #upload or download 
    get_operation_type = request.form.get('operation')

    operation_error = {"input_operation":get_operation_type,
                       "supported_operation:":"upload, download",
                       "error message":"operation method not supported"
                       }
    file_error = {"inputFile":get_file_name,
                  "error message:":"File is not Found"
                 }
    upload_succ = {"inputFile":get_file_name,
                   "message": "File Uploaded!!!"
                   }

    
    payload = {}
    payload['name'] = get_file_name
    payload['parent_folder_path'] = '/'

    # upload
    if get_operation_type != 'upload':
        return json.dumps(operation_error)
    elif get_operation_type == 'upload':
        r = requests.post (api_url, params = payload, headers = headers)
        r_json = r.json()
# read respond code
        print(r.status_code)
        #step2: Upload file using the token and up_load URL
        #get the repsone upload_url
        upload_url = r_json['upload_url']
        #get the upload_params key
        upload_params = list(r_json['upload_params'].items())
        #Upload the file data to the URL given in the previous response, pass in upload_params in a  payload
        try:
            with open(get_file_name, 'rb') as f:
                file_content = f.read()
        #errors handling 
        except FileNotFoundError:
           return json.dumps(file_error)
        upload_params.append((u'file', file_content)) # Append file at the end of list of tuples
        response = requests.post(upload_url, files=upload_params)
        return json.dumps(upload_succ)

#Get request
#adding new route for canvas course for current user
@app.route("/Canvas/Courses", methods =['GET'])
@requires_auth
def Canvas_get_courses():
    api_url = 'https://canvas.vt.edu/api/v1/courses'
    Canvas_access_token = param.param['Canvas_access_token']
    headers = {'Authorization': 'Bearer %s' % Canvas_access_token}
    r = requests.get(api_url, headers = headers)
    r_json = r.json()
    text_file = open('course.txt','w')
    for course in r_json:
        currentCourt = course['name']
        text_file.write(course['name']+'\n')
    return ("Course Names Get!")

#Get request
#adding new route to googleplace, param = place name
@app.route("/googleplace", methods = ['GET'])
@requires_auth
def getImage():
    place = request.args.get('place')
    search_url = param.param['search_url']
    photos_url = param.param['photos_url']
   
    googlePlace_token =param.param['googlePlace_token']
    search_payload = {"key":googlePlace_token, "query":place}
    search_req = requests.get(search_url, params=search_payload)
    search_json = search_req.json()
    # error handling for invaild place names 
    try:
        photo_id = search_json["results"][0]["photos"][0]["photo_reference"]
    except IndexError:
        return "your place is not found"
    photo_payload = {"key" : googlePlace_token, "maxwidth" : 500, "maxwidth" : 500, "photoreference" : photo_id}
    photo_request = requests.get(photos_url, params=photo_payload)
    photo_type = imghdr.what("", photo_request.content)
    photo_name = " " + place + "." + photo_type
    with open(photo_name, "wb") as photo:
        photo.write(photo_request.content)
    return("image downloaded")
 

#POST requet
#It will return the temperature giving the right curl command
#the input will be the us zip code 
@app.route("/weather", methods = ['POST'])
@requires_auth
def weather():
    POST_succ = {"CODE":"200",
                 "message": "The temp log saved!!!"
                   }
    #resource found at https://www.youtube.com/watch?v=sbYXa6HJJ5M&t=182s
    #This is a post request
    zipcode = request.form['zip']
    #new_data = json.loads(data)
    #zipcode = new_data['zip']
    weather_api_key = param.param['weather_api_key']
    payload = ','+ 'us&appid='+ weather_api_key
    r = requests.get('http://api.openweathermap.org/data/2.5/weather?zip='+zipcode+payload)
    json_object = r.json()
    #print(json_object)
    temp_k = float(json_object['main']['temp'])
    temp_f = (temp_k - 273.15) * 1.8 + 32
    tem = int(temp_f)
    text_file = open(zipcode+'.txt','w')
    text_file.write("The current temperature at  zip code: " + zipcode + " is " + str(tem) + ' F')
    return json.dumps(POST_succ)

to_do_list = ["To Do List:"]
@app.route("/LIST", methods = ['POST'])
@requires_auth
def list_func():
    option = request.form.get('option')
    event = request.form.get('event')
    if option == "add":
        to_do_list.append(event)

    elif option == "delete":
        to_do_list.remove(event)

    return json.dumps(to_do_list)



@app.route("/LED", methods = ['GET'])
@requires_auth
def getLED():
    global led_ip
    global led_port
    addressToGet = 'http://' + led_ip + ":" + str(led_port) + "/LED"
    r = requests.get(addressToGet)
    return r.text

@app.route("/LED", methods=['POST'])
@requires_auth
def send_to_LED():
    global led_ip
    global led_port
    global led_colors
    statusValue = request.args.get('status')
    colorValue = request.args.get('color')
    intensityValue = request.args.get('intensity')
    if (statusValue is not None and colorValue is not None and intensityValue is not None and
        (statusValue == "on" or statusValue == "off") and int(intensityValue) > -1 and
        int(intensityValue) < 101 and colorValue in led_colors):
        payload = {'status':statusValue, 'color':colorValue, 'intensity':intensityValue}
        data = 'http://' + led_ip + ":" + str(led_port) + "/LED"
        r = requests.post(data, params = payload)
        return r.text
    else:
        response = "Improper Values"
        return response
    
class MyListener(object):
    def remove_service(self, zeroconf, type, name):
        print("Service %s removed" % (name,))

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if "team03_led_pi" in name:
            global led_ip
            global led_port
            global led_colors
            led_ip = getIP(info.address)
            led_port = info.port
            led_colors = getColors("colors", info.properties)
            print("Name: ", name)
            print("IP: ", led_ip)
            print("Port: ", led_port)
            print("Properties: ", led_colors)
            led_colors = led_colors.split(",")
            zeroconf.close()
    
# pass in the hex for the ip address  
def getIP(address):
    # they are hex values
    return socket.inet_ntoa(address)
    
#pass in key for colors property and the Dict
def getColors(key, propertiesDict):
    key = key.encode()
    return propertiesDict.get(key).decode()

def main():
    dbclient = MongoClient()
    databaseName = "ECE4564_Assignment_3"
    db = dbclient[databaseName]
    counter = 1
    for x in db.service_auth.find():
        user = x.get("username")
        password = x.get("password")
        if counter == 1:
            global auth1
            auth1 = [user, password]
        elif counter == 2:
            global auth2
            auth2 = [user,password]
        elif counter == 3:
            global auth3
            auth3 = [user,password]
        counter+=1
    print (auth1, auth2, auth3)
    print("Connected to database '", databaseName, "' on MongoDB Server at 'localhost'")
    zeroconf = Zeroconf()
    listener = MyListener()
    browser = ServiceBrowser(zeroconf, "_http._tcp.local.", listener)
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    main()   




    

