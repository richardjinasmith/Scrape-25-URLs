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
statusfilename="dealspl_status"
dstfilename="dealspl.json"

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
	t_soup = BeautifulSoup(page_html)
	#dealitem       sdcat_5 sdcat_9341 sdcat_1477 sdcat_9365 sdcat_9377
	t_tables = t_soup.findAll('table',{"class":"product_table_grid"})
	item_idx=0
	for t_table in t_tables:
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

			t_trs=t_table.findAll('tr')
			#strtmp=h3s[0].prettify()
			#description
			#p = re.compile(r"<h3>(?P<param>.*?)<b>",re.DOTALL)
			#m = p.search( strtmp )
			#if m is not None and m.group('param') is not None:
			#	description=m.group('param').strip()
			t_divs=t_trs[1].findAll('div',{'class':'product-title-grid'})

			#description=''.join( t_divs[0].findAll(text=True) ).replace('\n', '')
			t_as=t_divs[0].findAll('a')
			description_tail=""
			try:
				#url
				url="http://dealspl.us"+t_as[0]['href']
				#print url

				description=''.join( t_as[0].findAll(text=True) ).replace('\n', '')
				description=description+"  @"+''.join( t_as[1].findAll(text=True) ).replace('\n', '')
				t_divs2=t_divs[0].findAll('div',{'class':'product-price-grid'})

				strtmp=t_divs2[0].prettify()
				p = re.compile(r"<br>(?P<param>.*?)<div",re.DOTALL)
				m = p.search( strtmp )
				if m is not None and m.group('param') is not None:
					description_tail=m.group('param').strip()
				t_divs3=t_divs2[0].findAll('div')
				strtmp2=''.join( t_divs3[0].findAll(text=True) ).replace('\n', '')
				#start_date
				start_date=strtmp2.strip()
				description_tail=description_tail+"  "+strtmp2.strip()

				t_spans=t_divs2[0].findAll('span',{'class':'nprice-g'})
				newprice=''.join( t_spans[0].findAll(text=True) ).replace('\n', '')
				p = re.compile(r"(?P<param>((\d+(\.\d*)?)|\.\d+))",re.DOTALL)
				description=description+"  new price: "+newprice
				m = p.search( newprice )
				if m is not None and m.group('param') is not None:
					price=m.group('param').strip()

				t_spans=t_divs2[0].findAll('span',{'class':'oprice-g'})
				oldprice=''.join( t_spans[0].findAll(text=True) ).replace('\n', '')
				description=description+"  old price: "+oldprice
			except:
				pass
			description=description.strip()+"  "+description_tail.strip()
			#print description
			#print t_divs[0]

			#staff_pick
			staff_pick="1"
			#likes
			t_as=t_trs[1].findAll('a',{'class':'plusButtonCount'})
			try:
				likes=''.join( t_as[0].findAll(text=True) ).replace('\n', '')
				#print "likes: "+likes
				#iconMap iconBalloonText
				t_as=t_trs[1].findAll('a')
				for t_a in t_as:
					if t_a.has_key('class') and "iconMap" in t_a['class'] and "iconBalloonText" in t_a['class']:
						#shares
						shares=''.join( t_a.findAll(text=True) ).replace('\n', '')
						#print "shares: "+shares
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
			lst["start_date"]=start_date
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

str_page_url="http://dealspl.us/Shoes_deals"
if old_page_no>0:
	str_page_url="http://dealspl.us/Shoes_deals/newest/"+str(old_page_no+1)

br = mechanize.Browser()
response1 = br.open(str_page_url)
page_html=response1.read()
page_idx=old_page_no
scrape_onePage(page_html,dstfilename,page_idx)

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
