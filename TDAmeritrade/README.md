## Description
This project is a very specific and simple solution to a problem I was having. As those of you using TD Ameritrade as a broker may know, there is no report on their website that shows how your account is performing net of any cash flows made to or from the account. This is commonly referred to as the time-weighted rate of return (TWRR). After scouring the web (namely Reddit) I realized that, although I was not alone in my search for a solution, most people simply paid for a service or app to link up with their TDA account to help them visualize their portfolio performance. Being savvy (and frugal), I thought it would be a good opportunity to put my programming skills to use. This project allows me to see how my accounts are doing relative to a benchmark (SPY in this case). 

## Output
The output is simply 2 things: 1) an html webpage produced with plotly of the portfolio returns and 2) a csv file of high level summary statistics for each account. Since I have different strategies I experiment with, I wanted to break out each strategy in the summary table. See example snippet below.

![Output Example](https://github.com/tficar/Portfolio/blob/master/TDAmeritrade/TDA%20Report%20Output.PNG)

## Setup/How to Run
Make sure you have installed all packages in the requirements.txt file. There are a couple of things that need to be modified to run the .py script. I could not find a way to automatically download the reports I needed from TDA. Their API does not have this capability and a bot could not be authenticated. Due to this, I have to manually download the reports. You will need to change the paths in the script to match where your files are downloaded. In addition, I have hidden my account numbers, so that will also need to updated.

Once it is set up, you should be able to successfully run the script. It will ask for a start and end date. These need to be within the dates that you downloaded the reports on TDA for. For example, today is 9/30. I downloaded the reports as YTD (so 1/1). Therefore, my options for start and end date must fall within those values. I could run the script for 1/1 - 3/31, or 6/30 - 9/30, or 1/1 - 9/30.
