#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\cherrypy\tutorial\tut02_expose_methods.py
import cherrypy

class HelloWorld:

    def index(self):
        return 'We have an <a href="showMessage">important message</a> for you!'

    index.exposed = True

    def showMessage(self):
        return 'Hello world!'

    showMessage.exposed = True


import os.path
tutconf = os.path.join(os.path.dirname(__file__), 'tutorial.conf')
if __name__ == '__main__':
    cherrypy.quickstart(HelloWorld(), config=tutconf)
else:
    cherrypy.tree.mount(HelloWorld(), config=tutconf)
