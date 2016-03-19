#!../.env/bin/python
from gevent import monkey; monkey.patch_all()
from app import app
from gevent.wsgi import WSGIServer
import resource
resource.setrlimit(resource.RLIMIT_NOFILE, (65536, 65536))

http_server = WSGIServer(('',8080), app)
http_server.serve_forever()

#app.run(debug=True, port=5000, host='0.0.0.0')

