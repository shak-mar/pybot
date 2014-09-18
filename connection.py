import logging
import socket
import time

config = {}
s = socket.socket()
connected = False
reconnect_wait = 15

def send_privmsg(channel, message):
    send_message("PRIVMSG %s :%s" % (channel, message))
    logging.append_to_log("bot: " + message)

def send_message(message):
    s.send(message+"\r\n")

def __load_config():
    print "Loading config..."
    logging.append_to_log("Loading config...")
    f = open("config")

    for line in f:
        line = line[0:len(line)-1]
        parts = line.split(":")

        if parts[0] == "channels":
            config["channels"] = parts[1].split(" ")
        else:
            config[parts[0]] = parts[1]
            
def __connect():
    global connected
    global s
    global reconnect_wait

    connected = False
    print "Connecting to %s" % config["host"]
    logging.append_to_log("Connecting to %s" % config["host"])
    reconnect_wait = 15

    while not connected:
        s.close()
        s = socket.socket()
        try:
            s.connect((config["host"],6667))
            connected = True

        except socket.gaierror:
            print "Connecting failed, will retry in %d seconds..." % reconnect_wait
            logging.append_to_log("Connecting failed, will retry in %d seconds..." % reconnect_wait)
            time.sleep(reconnect_wait)
            reconnect_wait = reconnect_wait * 2
            if reconnect_wait > 300:
                reconnect_wait = 300

    send_message("NICK "+config["name"])
    send_message("USER bot localhost localhost : An IRC-bot written in python")

    connected = False
    while not connected:
        readline = s.recv(4096)
        readlines = readline.splitlines()
        
        for line in readlines:
            print line

            if "PING" in line:
                line.replace("PING", "PONG")
                send_message(line)

            elif " 433 " in line:
                print "433: Name already taken. Trying to reconnect in 2 minutes."
                logging.append_to_log("433: Name already taken. Trying to reconnect in 2 minutes.")
                time.sleep(120)
                __connect()
                break

            elif ":%s MODE %s :" % (config["name"], config["name"])  in line:
                print "Connection established!"
                logging.append_to_log("Connection established!")
                connected = True
                channels = config["channels"]
                for channel in channels:
                    print "Joining %s..." % channel
                    logging.append_to_log("Joining %s..." % channel)
                    send_message("JOIN " + channel)

                break

def read_lines():
    s.settimeout(200)
    try:
        readline = s.recv(4096)
        readline = readline[0:-2]
        readlines = readline.splitlines()
        return readlines

    except socket.timeout:
        print "Connection lost. Reconnecting:"
        logging.append_to_log("Connection lost. Reconnecting...")
        __connect()
        return read_lines()


def init():
    __load_config()
    __connect()
