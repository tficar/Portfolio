## Description
This project was a solution I had to a manual process at my job. I work as an analyst on a catastrophe modeling team for an insurance company and one of our roles is to monitor the hazard of wildfires. When I arrived, the process was to manually search the [Inciweb website](https://inciweb.nwcg.gov/) and review each wildfire. If you visit the website, you can see that this would take us some time to do. This script will scrape that public web page and store important information about each wildfire. More importantly, since this can be run easily every day, we can now have a historical record of each wildfire and understand the changes each day to see how quickly they spread. This is only one source of information we look at, but now we can extract much more information from it.

## Output
The output of this script is an excel file with all of the wildfire data. It also includes a link to the Inciweb page for each wildfire in the event that more detailed information is needed. Here is a sample output.

![Inciweb Output](https://github.com/tficar/Portfolio/blob/master/InciwebScrape/Inciweb%20Output.PNG)

## Setup/How to Run
Make sure that all libraries in the requirements.txt are installed. That is all you will need for this script.
