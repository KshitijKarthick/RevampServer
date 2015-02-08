import cherrypy
import ConfigParser
import json
import mimetypes
import os
from jinja2 import Environment, FileSystemLoader
class Server():

	@cherrypy.expose
	def index(self):

		return "Seems Like You're Lost :D"

	@cherrypy.expose
	def eventsList(self,choice):

		message="Success, Event List Obtained"
		status_code=0;
		events=[]
		try:
			if choice.title() == "Technical":
				events = technical_event_list['events']
			elif choice.title() == "Cultural":
				events = cultural_event_list['events']
			elif choice.title() == "Sports":
				events = sports_event_list['events']
			else:
				status_code=-1
				message="Failed, No Such Event Type Enlisted"
		except:
				status_code=-1
				message="Failed, Server Error! Error Occured while retreiving Event List"
		return json.dumps({'status_code':status_code,'message':message,'events':events})

	@cherrypy.expose
	def eventsStatus(self,choice):

		message="Success, Event List Obtained"
		status_code=0;
		events=[]
		try:
			if choice.title() == "Technical":
				events = technical_event_list['events']
			elif choice.title() == "Cultural":
				events = cultural_event_list['events']
			elif choice.title() == "Sports":
				events = sports_event_list['events']
			else:
				status_code=-1
				message="Failed, No Such Event Type Enlisted"
		except:
				status_code=-1
				message="Failed, Server Error! Error Occured while retreiving Event List"
		return json.dumps({'status_code':status_code,'message':message,'hash':json.dumps(events).__hash__()})

if __name__ == '__main__':
	''' Setting up the Server with Specified Configuration'''
	config = ConfigParser.RawConfigParser()
	config.read('server.conf')
	cherrypy.server.socket_host = config.get('server','host')
	cherrypy.server.socket_port = int(config.get('server','port'))
	conf = {
		'/':{
			'tools.staticdir.root': os.path.abspath(os.getcwd())
		},
	}
	list = ConfigParser.RawConfigParser()
	list.read('events')
	technical_event_list=json.loads(list.get('technicalEvents','events'))
	cultural_event_list=json.loads(list.get('culturalEvents','events'))
	sports_event_list=json.loads(list.get('sportsEvents','events'))
cherrypy.quickstart(Server(),'/',conf)
