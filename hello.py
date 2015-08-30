# Standard BFS Approach to travel through the link and extract images , level by level
# How it work: -scrape method ,at each Level makes a new list of scraped urls and images 
# 				, then it removes duplicates within the list,adds it to the Model and updates visited links.
# 			   -scraper_url crawls through the link and scrapes unique urls and images
#			   
#			   
# Duplicates are handled
# Dependencies : lxml , requests

from lxml import html
import requests
import urlparse
import time

class Scraper:
	
	def __init__(self, url, depth):
		self.targer_url = url 
		self.depth = depth
		self.model_Images = []
		self.model_Links = []
		self.visited_Links = {}

	# helper method to remove Duplicates ,not the best approach though
	def removeDuplicates(self,temp):
			return list(set(temp))
	# 
	def scrape(self):
		self.model_Links.append(self.targer_url)
		current_depth=0
		while(current_depth<=self.depth):
			newListOfLinks = []
			newImageList = []
			done = 0;
			
			print "--------At Depth:%i---------" % (current_depth)
			for url in self.model_Links:
				
				newLinks=[];newImages=[]
				
				if not self.visited_Links.has_key(url):
					newImages,newLinks = self.scrape_url(url)
				
				self.visited_Links.update({url:True})
				newListOfLinks.extend(newLinks)
				newImageList.extend(newImages)
				done+=1;print "At Link:%i" % (done)
				time.sleep(2)
			self.model_Links = self.removeDuplicates(newListOfLinks)
			self.model_Images.extend(newImageList)
			self.model_Images = self.removeDuplicates(self.model_Images)
			current_depth+=1
			print "Image Count :%d  ,Urls Count:%d"%(len(newImageList),len(newListOfLinks))
			
		print "--------------------printing images----------------------"
		for img in self.model_Images:
			print img
		print "--------------------printing links----------------------"	
		for link in self.model_Links:
			print link	
		
	
		return list(self.model_Images)
	
	def scrape_url(self,link):

		response = requests.get(link)

		if(response.status_code != 200):
			return ([],[])
		elif (response.status_code == 200):
		    
		    response_text = html.fromstring(response.content)
		    
		    #scraping urls from anchor tags, generate absolute url, remove duplicates
		    links = response_text.xpath("//*/a/@href")
		    linkList = [urlparse.urljoin(link,i) for i in links if any([urlparse.urljoin(link,i).startswith('http://'),urlparse.urljoin(link,i).startswith('ftp://'),urlparse.urljoin(link,i).startswith('tcp://'),urlparse.urljoin(link,i).startswith('sftp://')])]
		    linkList = self.removeDuplicates(linkList)
		    #scraping images from img tags, generate absolute url of images
		    images = response_text.xpath("//img/@src")
		    imageList = [urlparse.urljoin(link,i) for i in images if any([urlparse.urljoin(link,i).endswith('tif'),urlparse.urljoin(link,i).endswith('jpg'),urlparse.urljoin(link,i).endswith('gif'),urlparse.urljoin(link,i).endswith('bmp'),urlparse.urljoin(link,i).endswith('png')])]
		    imageList=self.removeDuplicates(imageList)
		    #scraping images from style attibute of divs 
		    styles = response_text.xpath("//*/div/@style")
		    for sub in styles:
		     if "background:url" in sub:
		       offset= sub.find("background:url")
		       start = sub.find("(",offset,)
		       end = sub.find(" ",offset+start,)
		       relativelink=sub[start+1:end-1]
		       absolutelink = urlparse.urljoin(link,relativelink)
		       imageList.append(absolutelink)
    
		    return (imageList,linkList)

from flask import Flask, render_template, request

hello = Flask(__name__)
@hello.route("/")
def main():
	
	return render_template('crawlerapp.html',title='Web Crawler x.1v')

@hello.route('/crawl',methods=['POST'])
def crawl():
	website = (request.form['website']).strip()
	depth = int(request.form['level'])
	crawler = Scraper(website,depth)
	imageList = crawler.scrape()
	images_len = len(imageList)
	return render_template('crawlerapp.html',website=website,depth=depth,images=imageList,number=images_len)
if __name__ == "__main__":
    hello.run(debug=True)   
