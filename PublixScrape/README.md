## Description
Those fortunate enough to live in the southeast US know the greatness that is Publix. For those who do not, I pity you. Publix is a highly praised grocery store full of happiness and good experiences. One of their staples is their buy one get one free (BOGO) weekly deals. Every week, from Thursday through Wednesday, they have anywhere from 50-100 products that are BOGO. Usually included in this is at least 1 red wine. This project is meant to find that red wine that's on sale and send an email notifying me. I have also included a couple of my favorite products that are occasionally BOGO.

## Output
The output for this project is an email that contains the specified deals. Publix deals change on Thursday morning, so I have a Windows task that runs every Thursday to find the new deals. Here is a sample of the output.

![Publix](https://github.com/tficar/Portfolio/blob/master/PublixScrape/Publix%20Output.PNG)

## Setup/How to Run
To run this, you will need a few things. First, make sure you have everything in the requirements.txt. This includes downloading the web driver needed to run Selenium. Once you have this, you will need to update the email information on lines 83, 102, and 105 to reflect your email address, server, and login information, respectively. Lastly, you will need to update the zip code located on line 36 to reflect the zip code closest to you.
