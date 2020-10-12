# Load ngrams
load(file = "Data/Sample/unigram.Rda")
load(file = "Data/Sample/bigram.Rda")
load(file = "Data/Sample/trigram.Rda")
load(file = "Data/Sample/quadgram.Rda")

# Function to clean input text
cleanInput <- function(inputText){
    cleanText <- tolower(inputText)
    cleanText <- removePunctuation(cleanText)
    cleanText <- removeNumbers(cleanText)
    cleanText <- stri_replace_all_regex(cleanText, "[^[:alnum:][:space:]\'\\.\\?!]", "")
    cleanText <- stripWhitespace(cleanText)
}

predictWord <- function(userInput){
    userInput <- cleanInput(userInput)
    userInputLen <- length(strsplit(userInput,' ')[[1]])
    
    # Adjust for scenario where user enters long input
    if (userInputLen > 3) {
        searchStr <- word(userInput, userInputLen-2, userInputLen)
    } else if (userInputLen > 0) {
        searchStr <- userInput
    } else {
        searchStr <- ''
    }
    searchStrLen <- length(strsplit(searchStr,' ')[[1]])
    search <- searchStr
    
    # print(searchStr)
    # print(searchStrLen)
    
    # Determine which ngram to use depending on the input length and whether or not there is a match
    if (searchStrLen == 3) {
        
        quad <- sum(ifelse(gsub(search,'MATCH',quadgram$feat1feat2feat3) == 'MATCH', 1, 0))
        
        search <- word(search, searchStrLen - 1, searchStrLen)
        tri <- sum(ifelse(gsub(search,'MATCH',trigram$feat1feat2) == 'MATCH', 1, 0))
        
        search <- word(search, searchStrLen - 1, searchStrLen - 1)
        bi <- sum(ifelse(gsub(search,'MATCH',bigram$feat1) == 'MATCH', 1, 0))
        
    } else if (searchStrLen == 2) {
        
        quad <- 0
        
        tri <- sum(ifelse(gsub(search,'MATCH',trigram$feat1feat2) == 'MATCH', 1, 0))
        
        search <- word(search, searchStrLen - 1, searchStrLen - 1)
        bi <- sum(ifelse(gsub(search,'MATCH',bigram$feat1) == 'MATCH', 1, 0))
        
    } else if (searchStrLen == 1) {
        
        quad <- 0
        
        tri <- 0
        
        bi <- sum(ifelse(gsub(search,'MATCH',bigram$feat1) == 'MATCH', 1, 0))
        
    } else {
        
        quad <- 0
        
        tri <- 0
        
        bi <- 0
        
    }
    
    # print(bi)
    # print(tri)
    # print(quad)
    # print(searchStrLen)
    
    # Now that we have an ngram, set up a dataframe using that specific ngram
    # Logic is as follows: if we have a match in quadgram, use that. Next check trigram, then check bigram
    if (quad != 0 && searchStrLen == 3) {
        
        predWords <- data.frame(index = which(ifelse(gsub(searchStr,'MATCH',quadgram$feat1feat2feat3) == 'MATCH', 1, 0) == 1))
        predWords <- left_join(predWords, mutate(.data = quadgram, row = as.integer(rownames(quadgram))), by = c('index' = 'row'))
        predWords <- predWords[c('resp','frequency')]
        colnames(predWords) <- c('Predicted_Word','Frequency')
        predWords <- predWords[order(predWords$Frequency, decreasing = TRUE), ]
        predWords <- head(predWords,5)
        
    } else if (tri != 0 && searchStrLen == 3) {
        
        searchStr <- word(searchStr, searchStrLen - 1, searchStrLen)
        predWords <- data.frame(index = which(ifelse(gsub(searchStr,'MATCH',trigram$feat1feat2) == 'MATCH', 1, 0) == 1))
        predWords <- left_join(predWords, mutate(.data = trigram, row = as.integer(rownames(trigram))), by = c('index' = 'row'))
        predWords <- predWords[c('resp','frequency')]
        colnames(predWords) <- c('Predicted_Word','Frequency')
        predWords <- predWords[order(predWords$Frequency, decreasing = TRUE), ]
        predWords <- head(predWords,5)
        
    } else if (bi != 0 && searchStrLen == 3) {
        
        searchStr <- word(searchStr, searchStrLen, searchStrLen)
        predWords <- data.frame(index = which(ifelse(gsub(searchStr,'MATCH',bigram$feat1) == 'MATCH', 1, 0) == 1))
        predWords <- left_join(predWords, mutate(.data = bigram, row = as.integer(rownames(bigram))), by = c('index' = 'row'))
        predWords <- predWords[c('resp','frequency')]
        colnames(predWords) <- c('Predicted_Word','Frequency')
        predWords <- predWords[order(predWords$Frequency, decreasing = TRUE), ]
        predWords <- head(predWords,5)
        
    } else if (tri != 0 && searchStrLen == 2) {
        
        predWords <- data.frame(index = which(ifelse(gsub(searchStr,'MATCH',trigram$feat1feat2) == 'MATCH', 1, 0) == 1))
        predWords <- left_join(predWords, mutate(.data = trigram, row = as.integer(rownames(trigram))), by = c('index' = 'row'))
        predWords <- predWords[c('resp','frequency')]
        colnames(predWords) <- c('Predicted_Word','Frequency')
        predWords <- predWords[order(predWords$Frequency, decreasing = TRUE), ]
        predWords <- head(predWords,5)
        
        
    } else if (bi != 0 && searchStrLen == 2) {
        
        searchStr <- word(searchStr, searchStrLen, searchStrLen)
        predWords <- data.frame(index = which(ifelse(gsub(searchStr,'MATCH',bigram$feat1) == 'MATCH', 1, 0) == 1))
        predWords <- left_join(predWords, mutate(.data = bigram, row = as.integer(rownames(bigram))), by = c('index' = 'row'))
        predWords <- predWords[c('resp','frequency')]
        colnames(predWords) <- c('Predicted_Word','Frequency')
        predWords <- predWords[order(predWords$Frequency, decreasing = TRUE), ]
        predWords <- head(predWords,5)
        
    } else if (bi != 0 && searchStrLen == 1) {
        
        predWords <- data.frame(index = which(ifelse(gsub(searchStr,'MATCH',bigram$feat1) == 'MATCH', 1, 0) == 1))
        predWords <- left_join(predWords, mutate(.data = bigram, row = as.integer(rownames(bigram))), by = c('index' = 'row'))
        predWords <- predWords[c('resp','frequency')]
        colnames(predWords) <- c('Predicted_Word','Frequency')
        predWords <- predWords[order(predWords$Frequency, decreasing = TRUE), ]
        predWords <- head(predWords,5)
        
    } else {
        
        predWords <- 'No prediction available.'
        
    }
    
    predWords
}