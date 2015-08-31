# Standard BFS Approach to travel through the link and extract images , level by level
# How it work: -scrape method makes a new buffer set of scraped urls and images at each level ,then
# 		 adds it to the model_image Set(Set handles duplicates) and updates visited links.
# 	       -scraper_url crawls through the link and scrapes urls and images
# Dependencies : lxml , requests


from lxml import html
import requests, urlparse,time
from sets import Set
#suppress ssl verification warning in log
requests.packages.urllib3.disable_warnings()

class Scraper:
	
	def __init__(self, url, depth):
		self.targer_url = url
		self.depth = depth
		self.model_Images = Set([])
		self.visited_Links = {}

	#handles images and links at each depth
	def scrape(self):
		target_urls = [self.targer_url]
		current_depth=0
		while(current_depth<=self.depth):
			#collects the images/links scrapped from each level
			links_at_level = Set([]);images_at_level = Set([])
			done=0
			for url in target_urls:
				if not self.visited_Links.has_key(url):
					newImages,newLinks = self.scrape_url(url)
				links_at_level.update(newLinks)
				images_at_level.update(newImages)
				self.visited_Links.update({url:True})
				done+=1;print "  @Link:%i" % (done)
				time.sleep(0)
			target_urls = list(links_at_level)
			self.model_Images |= images_at_level
			current_depth+=1
			print "@Depth: %d Scrapped Image Count :%d  ,Scrapped Url Count:%d"%(current_depth,images_at_level.__len__(),links_at_level.__len__())
		print "Total Unique Images Scrapped:",self.model_Images.__len__()
		return list(self.model_Images)

	#handles images and links in each link
	def scrape_url(self,link):
		response = requests.get(link)
		#check for success status code
		if(response.status_code != 200):
			return (set([]),set([]))
		elif (response.status_code == 200):
			response_text = html.fromstring(response.content)
			#scraping urls from anchor tags, generate absolute url
			links = response_text.xpath("//a/@href")
			linkList = [urlparse.urljoin(link,i) for i in links if any([urlparse.urljoin(link,i).startswith('http://'),urlparse.urljoin(link,i).startswith('ftp://'),urlparse.urljoin(link,i).startswith('tcp://'),urlparse.urljoin(link,i).startswith('sftp://')])]
			#scraping images from img tags, generate absolute url of images
			images = response_text.xpath("//img/@src")
			imageList = [urlparse.urljoin(link,i) for i in images]
			# scraping images from style attibute of all elements 
			styleList = response_text.xpath("//@style")
			for style in styleList:
				if "background:url" in style:
					relativelink = self.scrape_from_style_between(style,"background:url",")")
					absolutelink = urlparse.urljoin(link,relativelink)
					imageList.append(absolutelink)
				if "background-image:url" in style:
					relativelink = self.scrape_from_style_between(style,"background-image:url",")")
					absolutelink = urlparse.urljoin(link,relativelink)
					imageList.append(absolutelink)
			return (set(imageList),set(linkList))

	#helper method to scrap out links form style attributes		
	def scrape_from_style_between(self,style,start_pattern,end_pattern):
		start_index = style.find(start_pattern)+len(start_pattern)+1
		end_index = style.find(end_pattern,start_index,)
		relativelink=style[start_index:end_index]
		return relativelink

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
