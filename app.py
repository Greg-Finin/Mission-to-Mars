#Import Dependencies
from flask import Flask, render_template
from flask_pymongo import PyMongo
import scraping

#Initialize Flask
app = Flask(__name__)

# Use flask_pymongo to set up mongo connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_app"
mongo = PyMongo(app)

@app.route("/")
def index():
   mars = mongo.db.mars.find_one()
   return render_template("indexhope.html", mars=mars)

@app.route("/scrape")
def scrape():
   mars = mongo.db.mars
   mars_data = scraping.scrape_all()
   mars.update({}, mars_data, upsert=True)
   return "Scraping Successful!"

if __name__ == "__main__":
   app.run()

# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt


def scrape_all():
    # Initiate headless driver for deployment
    browser = Browser("chrome", executable_path="chromedriver", headless=True)

    news_title, news_paragraph = mars_news(browser)

    hemisphere_dict, hemispheres, cerebuss = mars_hempispheres(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemispheres":hemispheres,
        "hemisphere_dict":hemisphere_dict,
        "cerebus":cerebuss
        
    }

    # Stop webdriver and return data
    browser.quit()
    return data


def mars_news(browser):

    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one("ul.item_list li.slide")
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find("div", class_="content_title").get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find("div", class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None

    return news_title, news_p


def featured_image(browser):
    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')[0]
    full_image_elem.click()

    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.links.find_by_partial_text('more info')
    more_info_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'

    return img_url

def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('http://space-facts.com/mars/')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")

def mars_hempispheres(browser):
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    # Write the code to collect urls and titles.
    html = browser.html
    tracker = 0
    titles = []
    urls = []
    hemispheres = {}
    mars_soup = soup(html, 'html.parser')
    thumbs = mars_soup.find_all('img', class_='thumb')
    for thumb in thumbs:
        browser.find_by_css('img.thumb')[tracker].click()
        html = browser.html
        mars_soup = soup(html, 'html.parser')
        title = mars_soup.find('h2', 'title').get_text()
        img = mars_soup.find('a', target='_blank', text='Sample')['href']
        if title not in titles:
            titles.append(title)
        if img not in urls:
            urls.append(img)
        hemispheres[title] = img
        tracker = tracker + 1
        browser.back()
    combined_list = titles+urls
    combined_list
    combined_list.insert(1, combined_list.pop(4))
    combined_list
    combined_list.insert(3, combined_list.pop(5))
    combined_list
    combined_list.insert(5, combined_list.pop(6))
    combined_list
    hemisphere_prep = ['title', 'img_url']
    n = len(combined_list) 
    hemisphere_dict = [{hemisphere_prep[0]: combined_list[idx], hemisphere_prep[1]: combined_list[idx + 1]} 
       for idx in range(0, n, 2)]
    cerebuss = hemisphere_dict[0:2]
    return(hemisphere_dict, hemispheres, cerebuss)



if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())