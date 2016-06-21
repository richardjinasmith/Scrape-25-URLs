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
statusfilename="slickdeals_status"
dstfilename="slickdeals.json"

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
	t_soup = BeautifulSoup(page_html)
	#dealitem       sdcat_5 sdcat_9341 sdcat_1477 sdcat_9365 sdcat_9377
	t_as = t_soup.findAll('a')
	item_idx=0
	for t_a in t_as:
		#if "class" in t_a:
		if t_a.has_key('class') and "dealitem" in t_a['class'] and t_a.has_key('rel') and "deal" in t_a['rel']:
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

			spans=t_a.findAll("span", {"class":"dealblocktext"})
			h3s=spans[0].findAll("h3")
			#strtmp=h3s[0].prettify()
			#description
			#p = re.compile(r"<h3>(?P<param>.*?)<b>",re.DOTALL)
			#m = p.search( strtmp )
			#if m is not None and m.group('param') is not None:
			#	description=m.group('param').strip()
			description=''.join( h3s[0].findAll(text=True) ).replace('\n', '')
			description=description.strip()
			description=description.replace('                    ','')
			description=description.replace('      ','')
			#print description

			#url
			url=t_a['href']
			url="http://slickdeals.net"+url
			#print url

			#retailer
			#<span class="store">at H&amp;M Stores on 11/13/12</span> - Store
			spans=t_a.findAll("span", {"class":"store"})
			strtmp=''.join( spans[0].findAll(text=True) ).replace('\n', '')
			retailer=strtmp
			p = re.compile(r"at (?P<param>.*?) on",re.DOTALL)
			m = p.search( strtmp )
			if m is not None and m.group('param') is not None:
				retailer=m.group('param').strip()
			#print retailer

			#staff_pick
			staff_pick="1"

			#likes
			#<span class="rating">+59</span>
			spans=t_a.findAll("span",{"class":"rating"})
			strtmp=''.join( spans[0].findAll(text=True) ).replace('\n', '')
			likes=strtmp
			p = re.compile(r"(?P<param>((\d+(\.\d*)?)|\.\d+))",re.DOTALL)
			m = p.search( strtmp )
			if m is not None and m.group('param') is not None:
				likes=m.group('param').strip()
			#print likes

			#shares
			#<span class="comments"><span class="icon_comments"></span>115</span>
			spans=t_a.findAll("span",{"class":"comments"})
			shares=''.join( spans[0].findAll(text=True) ).replace('\n', '')
			#print shares

			#start_date
			#<span class="store">at H&amp;M Stores on 11/13/12</span> - Store
			spans=t_a.findAll("span", {"class":"store"})
			strtmp=''.join( spans[0].findAll(text=True) ).replace('\n', '')
			start_date=strtmp
			p = re.compile(r"on (?P<param>\d+)/(?P<param2>\d+)/(?P<param3>\d+)",re.DOTALL)
			m = p.search( strtmp )
			if m is not None and m.group('param') is not None:
				if m is not None and m.group('param2') is not None:
					if m is not None and m.group('param3') is not None:
						start_date=m.group('param').strip()+"/"+m.group('param2').strip()+"/20"+m.group('param3').strip()
			#print start_date

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

def scrape_onePageForPopular(page_html,jsonfilename,page_idx):
# scrape one page of Popular deals for apparel
	rtn=0
	global PROXY_TIME_OUT
	global old_chart_no
	global old_page_no
	global old_item_no
	global statusfilename
	#print page_html
	#print "Current page_no: "+str(page_idx)
	t_soup = BeautifulSoup(page_html)
	#dealitem       sdcat_5 sdcat_9341 sdcat_1477 sdcat_9365 sdcat_9377
	t_tables = t_soup.findAll('table',{"id":"threadslist"})
	t_trs=t_tables[0].findAll("tr")
	item_idx=0
	for t_tr in t_trs:
		if item_idx==0:
			pass
		else:
			t_tds=t_tr.findAll("td")
			#print t_tds[1]
			t_as=t_tds[1].findAll("a",{"class":"fb_popular_deal_title"})
			t_a=t_as[0]
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
			description=''.join( t_a.findAll(text=True) ).replace('\n', '')
			description=description.strip()
			#print description
			#url
			url=t_a['href']
			url="http://slickdeals.net"+url
			#print url
			#staff_pick
			staff_pick="0"
			#likes
			#<span class="rating">+59</span>
			strtmp=''.join( t_tds[2].findAll(text=True) ).replace('\n', '')
			likes=strtmp
			p = re.compile(r"(?P<param>((\d+(\.\d*)?)|\.\d+))",re.DOTALL)
			m = p.search( strtmp )
			if m is not None and m.group('param') is not None:
				likes=m.group('param').strip()
			#print likes
			#shares
			strtmp=''.join( t_tds[3].findAll(text=True) ).replace('\n', '')
			shares=strtmp
			p = re.compile(r"(?P<param>((\d+(\.\d*)?)|\.\d+))",re.DOTALL)
			m = p.search( strtmp )
			if m is not None and m.group('param') is not None:
				shares=m.group('param').strip()
			#print shares

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
			#if item_idx>0:
			f.write(",")
			f.write(s + "\n")
			f.close()

		#print item_idx
		item_idx+=1
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

str_page_url="http://slickdeals.net/deals/apparel/"

br = mechanize.Browser()
response1 = br.open(str_page_url)
page_html=response1.read()
scrape_onePage(page_html,dstfilename,0)
page_idx=0
scrape_onePageForPopular(page_html,dstfilename,page_idx)

page_idx+=1
link = None
link_txt="Next »"
try:
	link=br.find_link(text=link_txt)
except:
	link=None
while link is not None:
# Actually clicking the link
	req=br.click_link(text=link_txt)
	br.open(req)
	page_html=br.response().read()
	scrape_onePageForPopular(page_html,dstfilename,page_idx)

	page_idx+=1
	try:
		link = br.find_link(text=link_txt)
	except:
		link = None

f = open(dstfilename, 'a')
f.write("]")
f.close()

#done successfully!
print "==================================================================================="
print "Congratulations! Scrapping successfully finished!"
print "==================================================================================="

#os.remove(statusfilename)
"""
			description=None
			url=None
			code=None
			retailer=None
			end_date=None
			staff_pick=None
			exclusive=None
			likes=None
			shares=None
			start_date=None

			spans=t_a.findAll("span", {"class":"dealblocktext"})
			h3s=spans[0].findAll("h3")
			#strtmp=h3s[0].prettify()
			#description
			#p = re.compile(r"<h3>(?P<param>.*?)<b>",re.DOTALL)
			#m = p.search( strtmp )
			#if m is not None and m.group('param') is not None:
			#	description=m.group('param').strip()
			description=''.join( h3s[0].findAll(text=True) ).replace('\n', '')
			description=description.strip()
			description=description.replace('                    ','')
			description=description.replace('      ','')
			print description

			#url
			url=t_a['href']
			url="http://slickdeals.net"+url
			print url

			#retailer
			#<span class="store">at H&amp;M Stores on 11/13/12</span> - Store
			spans=t_a.findAll("span", {"class":"store"})
			strtmp=''.join( spans[0].findAll(text=True) ).replace('\n', '')
			retailer=strtmp
			p = re.compile(r"at (?P<param>.*?) on",re.DOTALL)
			m = p.search( strtmp )
			if m is not None and m.group('param') is not None:
				retailer=m.group('param').strip()
			print retailer

			#staff_pick
			staff_pick="1"

			#likes
			#<span class="rating">+59</span>
			spans=t_a.findAll("span",{"class":"rating"})
			strtmp=''.join( spans[0].findAll(text=True) ).replace('\n', '')
			likes=strtmp
			p = re.compile(r"\+(?P<param>((\d+(\.\d*)?)|\.\d+))",re.DOTALL)
			m = p.search( strtmp )
			if m is not None and m.group('param') is not None:
				likes=m.group('param').strip()
			print likes

			#shares
			#<span class="comments"><span class="icon_comments"></span>115</span>
			spans=t_a.findAll("span",{"class":"comments"})
			shares=''.join( spans[0].findAll(text=True) ).replace('\n', '')
			print shares

			#start_date
			#<span class="store">at H&amp;M Stores on 11/13/12</span> - Store
			spans=t_a.findAll("span", {"class":"store"})
			strtmp=''.join( spans[0].findAll(text=True) ).replace('\n', '')
			start_date=strtmp
			p = re.compile(r"on (?P<param>\d+)/(?P<param2>\d+)/(?P<param3>\d+)",re.DOTALL)
			m = p.search( strtmp )
			if m is not None and m.group('param') is not None:
				if m is not None and m.group('param2') is not None:
					if m is not None and m.group('param3') is not None:
						start_date=m.group('param').strip()+"/"+m.group('param2').strip()+"/20"+m.group('param3').strip()
			print start_date

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
			lst["start_date"]=start_date
			s = json.dumps(lst)

			f = open(dstfilename, 'a')
			if item_idx>0:
				f.write(",")
			f.write(s + "\n")
			f.close()
"""
"""
try:
	ins = open( statusfilename, "r" )
	for line in ins:
		p = re.compile(r'chartno=(?P<param>\d+),page_no=(?P<param2>\d+),item_no=(?P<param3>\d+)')
		m = p.search( line.rstrip() )
		if m is not None and m.group('param') is not None:
			old_chart_no = int(m.group('param'))
			isfilevalid = True
			print "Last position - you scraped by this position."
			print "before chart_no: "+str(old_chart_no)
		if m is not None and m.group('param2') is not None:
			old_page_no = int(m.group('param2'))
			isfilevalid = True
			print "before page_no: "+str(old_page_no)
		if m is not None and m.group('param3') is not None:
			old_item_no = int(m.group('param3'))
			isfilevalid = True
			print "before item_no: "+str(old_item_no)
except:
	pass

if isfilevalid == False:
#already done or start from begin
	print "==============================================================================="
	print "<"+statusfilename+"> file stands for saving scraping staus. Don't touch this file!"
	print "Saving status into this file, scraper continues from the last position."
	print "In the case when scraper is terminated unsuccessfully, scraper continues from the position in the next time."
	var = raw_input("Are you going to start scraping from begin?(yes/no):")
	if var.lower() != "yes":
		sys.exit()
	var = raw_input("Did you backup all csv file?(yes/no):")
	if var.lower() != "yes":
		sys.exit()
		#remove all csv files
	if os.path.exists(csvfilename):
		os.remove(csvfilename)

print "==================================================================================="
print "scraping running..."

if not os.path.exists(csvfilename):
	with open(csvfilename,'wb') as f:
		fdWriter = csv.writer(f)
		fdWriter.writerow(['Chart Name','Current Rank','Song Title','Song Artist','Last Week\'s Position','Weeks On Chart','Peak'])
		print csvfilename+" newly created!"
"""
