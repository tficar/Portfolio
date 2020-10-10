## Description
One of my favorite hobbies is investing. I have loved it since I was first introduced in college. For the past 2-3 years I have been actively managing my own portfolio of stocks and options. With so many stocks and information constantly changing, I needed a way to keep up with all of the new information on companies I am interested in. This project is meant to do just that.

It works by combining a few lists of stocks. First, it reads in a list that I am interested in. In addition to this, it uses Investor's Business Daily to gather another stock list, filters out the top results, and then combines it with the original list. Once it has the final list, it scrapes a few different sources and combines all of the data. Sources include Zack's, Yahoo Finance, and finviz.

I made an amateur attempt at calculating my own weighted factor of all the metrics. It compares each stock to it's sector average and ranks them accordingly. The summary tab of the output is sorted by this factor. It did not fully work as intended, and there are a lot of oil/gas stocks at the top of the list that I do not think belong there. Regardless, you can use the metrics yourself to make your own decisions.

## Output
The output of this script is an excel file with 4 separate tabs, 1 being a high level summary of the results. From this, you could filter out specific things (e.g. companies with reasonable valuations, good earnings growth, low debt, etc.). Here is a sample of the excel output.

![Stock Output](https://github.com/tficar/Portfolio/blob/master/StockDataScrape/Stock%20Output.PNG)

## Setup/How to Run
There are a few things needed in order to run this. First, as always, make sure you have all libraries in the requirements.txt. After this, you will need to adjust a few file paths. First, you will need to change the path for the stock_list variable to point to wherever your stock list excel sheet is. This is located on line 35. You will also need to change the path for where it is saved. This can be found on line 250.

It is important to note that I have had issues with the header and have had to change it in the past. This usually only occurs when I have had to run it a few times in the same day while debugging. This script can take awhile to complete depending on the number of stocks. I have around 300 stocks on my list and it takes ~2hrs to complete.
