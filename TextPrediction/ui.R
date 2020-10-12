library(shiny)

shinyUI(fluidPage(

    headerPanel("Text Prediction"),

    sidebarLayout(
        sidebarPanel(
            p('This app is meant to predict the next word given some text. The most likely word will appear,
              as well as a graph of the top 5 most frequent words (if available). Simply enter text into the
              box on the right and then click the Submit button.')
            # textInput("inputWords","Please enter your text below.",value = ''),
            # submitButton('Submit')
        ),

        mainPanel(
            textInput("inputWords",h4("Please enter your text below."),value = ''),
            submitButton('Submit'),
            h4('Predicted Word'),
            verbatimTextOutput('prediction'),
            h4('Graph of Most Frequent Prediction'),
            plotOutput('plot')
        )
    )
))
