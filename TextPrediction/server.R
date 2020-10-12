library(shiny)
library(stringr)
library(ggplot2)
library(tm)
library(stringi)
library(dplyr)
source('predictWord.R')

shinyServer(function(input, output) {
    
    predictedWords <- reactive({predictWord(input$inputWords)})
    
    output$prediction <- renderText({
        validate(need(trimws(input$inputWords) != '', 'Please enter the beginning of the sentence.'))
        predWords <- predictedWords()
        validate({need(predWords != 'No prediction available.', "Couldn't find prediction for given text.")})
        predWords[[1,1]]
    })
    
    # output$prediction <- renderPrint({
    #     
    #     if (is.null(predictedWords())) {
    #         return()
    #     }
    #     
    #     Sys.sleep(0.5)
    #     predictedWords <-  predictWord(input$inputWords)
    #     validate({need(predictedWords != 'No prediction available.','Not available for prediction.')})
    # })

    output$plot <- renderPlot({
        predWords <- predictedWords()
        validate({need(trimws(input$inputWords) != '', 'No predicted words to graph.')})
        validate({need(predWords != 'No prediction available.',"No predicted words to graph.")})
        g <- ggplot(as.data.frame(predWords), aes(reorder(Predicted_Word,-Frequency),Frequency))
        g <- g + geom_bar(stat = 'identity', fill = 'darkseagreen3')
        g <- g + xlab('Predicted Word')
        return(g)
    })
    
})
