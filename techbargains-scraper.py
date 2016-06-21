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

old_page_no=0
old_item_no=0
isfilevalid=False
statusfilename="techbargains_status"
dstfilename="techbargains.json"

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
	global old_page_no
	global old_item_no
	global statusfilename
	#print page_html
	#print "Current page_no: "+str(page_idx)
	t_soup = BeautifulSoup(page_html)
	#dealitem       sdcat_5 sdcat_9341 sdcat_1477 sdcat_9365 sdcat_9377
	t_divs = t_soup.findAll('div',{"class":"CBoxTDealStyling"})
	item_idx=0
	for t_div in t_divs:
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
		percentage_off=None
		start_date=None

		#description
		t_divs2=t_div.findAll('div',{'class':'upperrightSort'})
		description=''.join( t_divs2[0].findAll(text=True) ).replace('\n', ' ')
		description=description.strip()
		t_divs3=t_div.findAll('div',{'class':'expiredDealIndicator'})
		try:
			strtmp=''.join( t_divs3[0].findAll(text=True) ).replace('\n', ' ')
			description="Expired Deal, "+description
		except:
			pass

		#print description

		#url
		t_as=t_divs2[0].findAll('a')
		strtmp=t_as[0]['onclick']
		#revealDeal(323538,'/jump.cfm?clkSubId=N82N2A99323538C384&afsrc=1&id=7999&arg=203739881','TBdeal_323538');
		p = re.compile(r",('|\")(?P<param>.*?)('|\")")
		m = p.search( strtmp )
		if m is not None and m.group('param') is not None:
			url=m.group('param')
			url="http://www.techbargains.com"+url
			#print url

		#staff_pick
		staff_pick="1"

		#price
		t_divs3=t_div.findAll('div',{'class':'thumbTextWrapper'})
		try:
			t_divs4=t_divs3[0].findAll('div')
			for t_div4 in t_divs4:
				if t_div4.has_key('class') and "redboldtext" in t_div4['class'] and "rbtextLeft" in t_div4['class']:
					price=''.join( t_div4.findAll(text=True) ).replace('\n', ' ')
					p = re.compile(r"(?P<param>((\d+(\.\d*)?)|\.\d+))",re.DOTALL)
					m = p.search( price )
					if m is not None and m.group('param') is not None:
						price=m.group('param').strip()
					#print price
			#percentOffBadge
			t_spans=t_div.findAll('span',{'class':'percentOffBadge'})
			strtmp=''.join( t_spans[0].findAll(text=True) ).replace('\n', ' ')
			p = re.compile(r"(?P<param>((\d+(\.\d*)?)|\.\d+))",re.DOTALL)
			m = p.search( strtmp )
			if m is not None and m.group('param') is not None:
				percentage_off=m.group('param').strip()
			#print percentage_off
		except:
			pass

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
		lst["percentage_off"]=percentage_off
		lst["start_date"]=start_date
		s = json.dumps(lst)

		f = open(dstfilename, 'a')
		if item_idx==0:
			pass
		else:
			f.write(",")
		f.write(s + "\n")
		f.close()

		item_idx+=1
		#print item_idx
	return rtn

#main process
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

str_page_url="http://www.techbargains.com/catsearch.cfm/0_6_17"
br = mechanize.Browser()
response1 = br.open(str_page_url)
page_html=response1.read()
scrape_onePage(page_html,dstfilename,0)

f = open(dstfilename, 'a')
f.write("]")
f.close()

#done successfully!
print "==================================================================================="
print "Congratulations! Scrapping successfully finished!"
print "==================================================================================="
