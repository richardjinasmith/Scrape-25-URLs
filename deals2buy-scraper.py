#!/usr/bin/env python
# coding: utf-8
import sys,os
import urllib2,urllib,re,json
from datetime import datetime
from bs4 import BeautifulSoup
import mechanize
####################################################################
#rotating proxies
MAX_WAIT = 60*1 # default - 1 min
last_timestamp = datetime.now()
PROXY_TIME_OUT=100

old_chart_no=0
old_page_no=0
old_item_no=0
isfilevalid=False
statusfilename="deals2buy_status"
dstfilename="deals2buy.json"

proxies = []
def readProxies():
	global proxies
	global MAX_WAIT
	proxies = []
	ins = open( "proxies.list", "r" )
	for line in ins:
		p = re.compile(r'MAX_LIMIT_SECONDS=(?P<param>\d+)')
		m = p.search( line.rstrip() )
		if m is not None and m.group('param') is not None:
			MAX_WAIT = int(m.group('param'))
		else:
			proxies.append( line.rstrip() )

#readProxies()
#print "==================================================================================="
#print "Rotate proxies in every per " + str(MAX_WAIT) + " Seconds"
#print "proxies list:"
#print proxies
####################################################################

def scrape_onePage(page_html,jsonfilename,page_idx):
# scrape one page
	rtn=0
	global PROXY_TIME_OUT
	global old_chart_no
	global old_page_no
	global old_item_no
	global statusfilename
	#print page_html
	#print "Current page_no: "+str(page_idx)
	t_soup = BeautifulSoup(page_html,'html5lib')
	#dealitem       sdcat_5 sdcat_9341 sdcat_1477 sdcat_9365 sdcat_9377
	t_lis = t_soup.findAll('li',{'class':'detail_view '})
	item_idx=0
	for t_li in t_lis:
		description=None
		url=None
		code=None
		retailer=None
		end_date=None
		staff_pick=None
		exclusive=None
		likes=None
		shares=None
		price=None
		start_date=None

		#description
		t_divs=t_li.findAll('div',{'class':'description'})
		description=''.join( t_divs[0].findAll(text=True) ).replace('\n', '')
		t_uls=t_li.findAll('ul',{'class':'how_to'})
		description=''.join( t_uls[0].findAll(text=True) ).replace('\n', ' ')
		description=description+"   "+description.strip()
		#print description

		#url
		t_as=t_li.findAll('a',{'class':'jumplink'})
		url=t_as[0]['href']
		#print url

		#retailer
		t_h3s=t_li.findAll('h3',{'class':'store-title'})
		retailer=''.join( t_h3s[0].findAll(text=True) ).replace('\n', '')
		retailer=retailer.strip()
		#print retailer

		#staff_pick
		staff_pick="1"

		#write to json
		lst={}
		lst["description"]=description
		lst["url"]=url
		lst["code"]=code
		lst["retailer"]=retailer
		lst["end_date"]=end_date
		lst["staff_pick"]=staff_pick
		lst["exclusive"]=exclusive
		lst["likes"]=likes
		lst["shares"]=shares
		#lst["price"]=price
		lst["start_date"]=start_date
		s = json.dumps(lst)

		f = open(dstfilename, 'a')
		if item_idx>0:
			f.write(",")
		f.write(s + "\n")
		f.close()

		item_idx+=1
		#print item_idx

	return rtn

#maind process
var = raw_input("Are you going to start scraping from begin?(yes/no):")
if var.lower() != "yes" and var.lower() != "y":
	sys.exit()
var = raw_input("Did you backup json file?(yes/no):")
if var.lower() != "yes" and var.lower() != "y":
	sys.exit()
#remove all json files
if os.path.exists(dstfilename):
	os.remove(dstfilename)

print "==================================================================================="
print "scrapping running..."

f = open(dstfilename, 'a')
f.write("[")
f.close()

str_page_url="http://www.deals2buy.com/clothing/costumes/deals"

br = mechanize.Browser()
response1 = br.open(str_page_url)
page_html=response1.read()
page_idx=0
scrape_onePage(page_html,dstfilename,page_idx)

f = open(dstfilename, 'a')
f.write("]")
f.close()

#done successfully!
print "==================================================================================="
print "Congratulations! Scrapping successfully finished!"
print "==================================================================================="

#os.remove(statusfilename)
