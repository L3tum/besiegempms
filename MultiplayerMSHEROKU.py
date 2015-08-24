import argparse
import BaseHTTPServer
import urlparse
import json

HOST_NAME = 'besiegempms.herokuapp.com'

#parsed.get(key)[0] everywhere except Players!

class Serverp(object):
    name = str
    ipPort = str
    maxPlayers = int
    connectedPlayers = int
    players = []
    def __init__(self, name, ipPort, maxPlayers, connectedPlayers, Players):
        self.name = name
        self.ipPort = ipPort
        self.maxPlayers = maxPlayers
        self.connectedPlayers = connectedPlayers
        for player in Players:
            self.players.append(player)

Servers = {}

#Notes:
#To Connect a Player to a Server, send Servername as 'name', Playername as 'playerName', True as 'playerConnected'

#To Disconnect a Player from a Server, send Servername as 'name', Playername as 'playerName', True as 'playerDisconnected'

#To Shut a Server down, send Servername as 'name', True as 'serverShutdown'

#To get info to a Server, send Servername as 'name', True as 'serverInfo'
#Return is in format 'message' with Server properties and 'players' with the connected Players array

#To register a Server, send Servername as 'name', IP as 'ip', maxPlayers as 'maxPlayers', connectedPlayers as 'connectedPlayers', Players as 'Players'

#To get the List of Servers, send True as 'getServersOnline' and True as 'every' if you want full Servers as well
#Return is in format 'servers' with the Servers array

#Return is always an 'ok' with either True or False and a Message as 'message'
        

class MSHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(s):
        parsed_path = urlparse.urlparse(s.path)
        parsed = urlparse.parse_qs(parsed_path.query)
        print parsed
        returned = str
        returnDict = {}
        if parsed.has_key('name'):
            if Servers.has_key(parsed.get("name")[0]):
                Server = Servers[parsed.get('name')[0]]

                if parsed.has_key('playerConnected'):
                    if Server.connectedPlayers is not Server.maxPlayers:
                        if parsed.get('playerName')[0] in Server.players:
                            returned = "Player {} is already present on this Server!".format(parsed.get('playerName')[0])
                            print returned
                            returnDict["ok"] = False
                            returnDict["message"] = returned

                        else:
                            Server.players.append(parsed.get('playerName')[0])
                            Server.connectedPlayers += 1
                            returned = "Player {} successfully connected to this Server!".format(parsed.get('playerName')[0])
                            print returned
                            returnDict["ok"] = True
                            returnDict["message"] = returned

                    else:
                        returned = "Serverlimit reached! Unable to connect Player!"
                        print returned
                        returnDict["ok"] = False
                        returnDict["message"] = returned
        
                elif parsed.has_key('playerDisconnected'):
                    if parsed.get('playerName')[0] in Server.players:
                        Server.connectedPlayer -= 1
                        Server.players.pop(Server.player.index(parsed.get('playerName')[0]))
                        returned = "Player {} successfully disconnected from this Server!".format(parsed.get('playerName')[0])
                        print returned
                        returnDict["ok"] = True
                        returnDict["message"] = returned

                    else:
                        returned = "Player {} is not registered on this Server. Unable to disconnect!".format(parsed.get('playerName'[0]))
                        print returned
                        returnDict["ok"] = False
                        returnDict["message"] = returned

                elif parsed.has_key('serverShutdown'):
                    if Server.name in Servers:
                        Servers.pop(Server.name)
                        returned = "Server {} successfully shut down!".format(Server.name)
                        print returned
                        returnDict["ok"] = True
                        returnDict["message"] = returned

                    else:
                        returned = "Server {} is not registered! Unable to shut down!".format(Server.name)
                        print returned
                        returnDict["ok"] = False
                        returnDict["message"] = returned

                elif parsed.has_key('serverRegister'):
                    returned = "Server {} is already registered!".format(Server.name)
                    print returned
                    returnDict["ok"] = False
                    returnDict["message"] = returned

                elif parsed.has_key('serverInfo'):
                    returned = "Name: {}, IP: {}, maxPlayers: {}, connectedPlayers: {}".format(Server.name, Server.ipPort, Server.maxPlayers, Server.connectedPlayers)
                    print returned
                    returnDict["ok"] = True
                    returnDict["message"] = returned
                    returnDict["players"] = Server.players
                    
            elif parsed.has_key('serverRegister'):
                Servers[parsed.get('name')[0]] = Serverp(parsed.get('name')[0], parsed.get('ip')[0], parsed.get('maxPlayers')[0], parsed.get('connectedPlayers')[0], parsed.get('players')) 
                returned = "Server {} successfully registered!".format(parsed.get('name')[0])
                print returned
                returnDict["ok"] = True
                returnDict["message"] = returned
            
        elif parsed.has_key('getServersOnline'):
            if parsed.has_key('every'):
                returned = "Returned List of Servers!"
                print returned
                returnDict["ok"] = True
                returnDict["servers"] = Servers
                returnDict["message"] = returned

            else:
                serverList = {}
                for server in Servers.values():
                    if server.connectedPlayers is not server.maxPlayers:
                        serverList[server.name] = { 'name' : server.name, 'ip' : server.ipPort, 'maxPlayers' : server.maxPlayers, 'connectedPlayers' : server.connectedPlayers, "players" : server.players}

                returned = "Returned List of not-full Servers!"
                print returned
                returnDict["ok"] = True
                returnDict["servers"] = serverList
                returnDict["message"] = returned

        s.send_response(200)
        s.send_header("CONTENT-TYPE", "Application/JSON")
        s.end_headers()
        s.wfile.write(json.dumps(returnDict))

handler = MSHandler

httpd = BaseHTTPServer.HTTPServer((""), handler)
httpd.serve_forever()
