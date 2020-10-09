## Description
The purpose of this project is to help me find a house! I wanted to practice web scraping so I decided this would be a perfect opportunity. I made sure to check the robots.txt file to confirm I was allowed to scrape the Zillow page. Zillow does have an API, but I found that it didn't really suit my needs and I was more interested in learning how to scrape for data anyways.

Another aspect I wanted to practice with this project was using MySQL. I have experience with SQL, so I wanted to set up a MySQL server on my PC to practice storing and retrieving data from a MySQL server. 

The way the script works is by using a specific url to find all of the locations within that page and return data on those locations. More details on how to run this are included below.

## Output
The output from this script is a csv of the houses located in the specific area. In addition to this, that same data is stored in the MySQL server. This was mainly just for practice, as we would not need 2 copies of the data. I have another project that links this data to Tableau and overlays local crime data to see if any locations are in bad areas, so this is another reason that I needed to save it to MySQL. Here is a sample of the csv output.

![Zillow Output](https://github.com/tficar/Portfolio/blob/master/ZillowScrape/Zillow%20Scrape%20Output.PNG)

## Setup/How to Run
Once you have all of the required libraries installed, all you need to do is go to Zillow and use the tool to draw a cirle around the area of interest. I would also add any filters you may want, such as 2+ beds, price ranges, etc. Once you have this, you can copy the urls for each page into the script and you should be able to run it. It shouldn't take too long to run. It usually finishes within 15 minutes for me. FYI the 'Save Rate' column is great for identifying the best listings. It is a column that I engineered and the best houses are always at the top of the list when it comes to 'Save Rate'.

Keep in mind that web scraping is tedious and that the html of the webpage often changes. This has happened numerous times and I have had to go in and debug. It is usually a very minor change (last time it was changing a 'u' to a 'c' in one of the regex functions). Just a heads up!
