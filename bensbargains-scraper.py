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
statusfilename="bensbargains_status"
dstfilename="bensbargains.json"

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
	print "Current page_no: "+str(page_idx)
	t_soup = BeautifulSoup(page_html,'html5lib')
	#dealitem       sdcat_5 sdcat_9341 sdcat_1477 sdcat_9365 sdcat_9377
	#t_divs_wdl=t_soup.findAll('div',{"class":"wbw-deals-list"})
	t_divs = t_soup.findAll('div',attrs={'class':'deal'})
	item_idx=0
	for t_div in t_divs:
		if page_idx==old_page_no and item_idx<old_item_no:
			pass
		else:
			#write status file
			fo = open(statusfilename, "wb")
			#pageno=(?P<param>\d+),item_no=(?P<param2>\d+)
			strtemp = "pageno="+str(page_idx)+",itemno="+str(item_idx)
			fo.write( strtemp);
			fo.close()

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
			expired=None

			#description
			t_divs2=t_div.findAll('div',{'class':'left'})
			description=''.join( t_divs2[0].findAll(text=True) ).replace('\n', '')
			description=description.strip()
			print description

			#url
			t_as=t_div.findAll('a',{'rel':'nofollow'})
			url="http://bensbargains.net"+t_as[0]['href']
			print url

			#retailer
			t_as=t_div.findAll('a',{'class':'deal-merchant'})
			retailer=''.join( t_as[0].findAll(text=True) ).replace('\n', '')
			retailer=retailer.strip()
			print retailer

			#staff_pick
			staff_pick="1"

			#deal-price
			try:
				t_divs2=t_div.findAll('div',{'class':'deal-price'})
				price=''.join( t_divs2[0].findAll(text=True) ).replace('\n', '')
				price=price.strip()
				p = re.compile(r"(?P<param>((\d+(\.\d*)?)|\.\d+))",re.DOTALL)
				m = p.search( price )
				if m is not None and m.group('param') is not None:
					price=m.group('param').strip()
				print price
			except:
				pass

			#expired=None
			expired="0"
			t_uls=t_div.findAll('ul',{'class':'deal-click-button'})
			try:
				strtmp=''.join( t_uls[0].findAll(text=True) ).replace('\n', '')
				strtmp=strtmp.strip()
				if strtmp=="Expired":
					expired="1"
				print strtmp
			except:
				pass


			#write to json
			lst={}
			lst["description"]=description
			lst["url"]=url
			lst["code"]=code
			lst["retailer"]=retailer
			lst["end_date"]=end_date
			#lst["staff_pick"]=staff_pick
			lst["exclusive"]=exclusive
			lst["likes"]=likes
			lst["shares"]=shares
			#lst["price"]=price
			lst["start_date"]=start_date
			lst["expired"]=expired
			s = json.dumps(lst)

			f = open(dstfilename, 'a')
			if page_idx==0 and item_idx==0:
				pass
			else:
				f.write(",")
			f.write(s + "\n")
			f.close()

		item_idx+=1
		#print item_idx
	return rtn


#str_page_url="http://bensbargains.net/categories/home-garden-85/3/"

#br = mechanize.Browser()
#response1 = br.open(str_page_url)
#page_html=response1.read()
#page_idx=0
#scrape_onePage(page_html,dstfilename,page_idx)
#sys.exit()
#main process
isfilevalid=False
try:
	ins = open( statusfilename, "r" )
	for line in ins:
		p = re.compile(r'pageno=(?P<param>\d+),itemno=(?P<param2>\d+)')
		m = p.search( line.rstrip() )
		if m is not None and m.group('param') is not None:
			old_page_no = int(m.group('param'))
			isfilevalid = True
			print "Last position - you scraped by this position."
			print "before page_no: "+str(old_page_no)
		if m is not None and m.group('param2') is not None:
			old_item_no = int(m.group('param2'))
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
	if var.lower() != "yes" and var.lower() != "y":
		sys.exit()
	var = raw_input("Did you backup all json file?(yes/no):")
	if var.lower() != "yes" and var.lower() != "y":
		sys.exit()
	#remove all json files
	if os.path.exists(dstfilename):
		os.remove(dstfilename)
	f = open(dstfilename, 'a')
	f.write("[")
	f.close()
print "==================================================================================="
print "scrapping running..."

str_page_url="http://bensbargains.net/categories/home-garden-85/"
if old_page_no>0:
	str_page_url="http://bensbargains.net/categories/home-garden-85/"+str(old_page_no+1)+"/"

br = mechanize.Browser()
response1 = br.open(str_page_url)
page_html=response1.read()
page_idx=old_page_no
scrape_onePage(page_html,dstfilename,page_idx)

page_idx+=1
link = None
link_txt="Next"
try:
	link=br.find_link(text=link_txt)
except:
	link=None
while link is not None:
# Actually clicking the link
	req=br.click_link(text=link_txt)
	br.open(req)
	page_html=br.response().read()
	scrape_onePage(page_html,dstfilename,page_idx)

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

os.remove(statusfilename)
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
