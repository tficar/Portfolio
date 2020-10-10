## Description
For this project my goal was to make a simple application that can access Twitter through their API and analyze the sentiment of tweets. I debated on making a web page similar to the Google Trends project but never ended up doing it (still thinking about it).

This app will interact with the user and ask them to enter a specific keyword to search Twitter for. It will prompt them with a few other questions and then gathers tweets. Since I am using a free Twitter dev account, I am limited in the number of tweets that I am able to get. I believe the limit is 5000, but I set the limit to 1000. In reality, we would want at least hundreds of thousands of tweets to truly get an accurate understanding of sentiment for a keyword, so keep that in mind.

## Output
The output for this project is a chart that plots the sentiment of the keyword entered. If the user requests, it can also output the top positive or negative tweets gathered. Here is a sample of the output.

![Twitter Output](https://github.com/tficar/Portfolio/blob/master/TwitterSentiment/Twitter%20Output.PNG)

## Setup/How to Run
To run this, first make sure you have everything in the requirements.txt. After that, you will need to create a Twitter dev account. You can go [here](https://developer.twitter.com/en/apply-for-access) to apply for an account. They will just ask you what you are planning to do with the tweets to make sure you aren't doing anything bad. NOTE THAT THEY ARE REALLY SLOW AT REPLYING TO REQUESTS. It took me over 2 months to hear back from them about my account.

Once you have an account, you will need all of your keys and tokens. These need to be entered on lines 16-19 of the TwitterSentiment.py script. Once this is done, you should be able to run the script and interact at the command line.
