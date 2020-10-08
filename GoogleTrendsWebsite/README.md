## Description
For this project I wanted to take a crack at building a webpage from scratch. I wanted something similar to what shiny can do in R. After some research, I found Dash from Plotly to be the best option for me.

Another aspect that I wanted to work into this project was working with Google Trends data. I had seen some posts in various reddit forums that showed visualizations using this data and I wanted to replicate it. I found the pytrends library after some research and decided to use it for this project.

The result is a public webpage hosted by https://www.pythonanywhere.com/. This site allows 1 website to be hosted publicly for free (with minimal resources). You'll notice that the webpage may take some time to load initially due to the low resources allocated to it. Another thing I want to mention is that my intention for this webpage was never to make it the most aesthetically pleasing. My goal was to understand the structure of building a webpage, how to customize it, and how to host it. I could spend weeks trying to make it look better, but the fact that I now know HOW to was the most important thing to me. 

## Output
You can visit the webpage at http://tficar.pythonanywhere.com/. There are various inputs to make it interactive, just make sure to click the submit button for the page to refresh. I mainly tested the Global and United States searches, so I wouldn't be surprised if something breaks while searching for keywords in Brazil or Sweden. If it does, let me know!

I also want to be clear on how the Index Ranking chart should be interpreted. There is a section at the top of the webpage that explains it, but I will explain it here as well. The value returned from the pytrends library is a essentially a scale of the frequency with which the specific keyword was searched over the given timeframe. The scale ranges from 0 to 100, with 0 being the time that it was search the least and 100 being the time that it was searched the most. If there are multiple keywords, it is important to understand that they are independent of each other. Both will have their own scale and therefore cannot be compared to one another.

## Setup/How to Run
Make sure to have all of the requirement.txt libraries. If you're familiar with html, you can play around with the layout of the webpage and come up with a better design!
