import urllib2
import os
import time

numba=1
while numba==1:
	req = urllib2.Request("https://psl.azure-mobile.net/api/match_api", None, {'User-agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'})
	try:
		html = urllib2.urlopen(req).read()
	except:
		print "error getting url\n"
	#response = urllib2.urlopen('https://psl.azure-mobile.net/api/match_api')
	#html=response.read()
	#fd = os.open("/vagrant/code/app/static/json.json", os.O_CREAT | os.O_WRONLY | os.O_NONBLOCK)
	#os.write(fd, html)
	#os.close(fd)
	else:
		wr = open("/vagrant/code/app/static/json.json", 'w')
		wr.write(html)
		wr.close()
	time.sleep(10)	
