
###################### TASK 0 START ######################

# Read data
con <- file('Data/final/en_US/en_US.blogs.txt','r')
blogs <- readLines(con, encoding = 'UTF-8', skipNul = TRUE, warn= FALSE)
close(con)

con <- file('Data/final/en_US/en_US.news.txt','r')
news <- readLines(con, encoding = 'UTF-8', skipNul = TRUE, warn= FALSE)
close(con)

con <- file('Data/final/en_US/en_US.twitter.txt','r')
twitter <- readLines(con, encoding = 'UTF-8', skipNul = TRUE, warn= FALSE)
close(con)

# Explore with some summary stats
library(ngram)
library(tibble)

blogsWords <- wordcount(blogs)
newsWords <- wordcount(news)
twitterWords <- wordcount(twitter)

blogsLines <- length(blogs)
newsLines <- length(news)
twitterLines <- length(twitter)

summStats <- data.frame(Source = c('blogs','news','twitter'),WordCount = c(blogsWords, newsWords, twitterWords),
                        Lines = c(blogsLines, newsLines, twitterLines)) %>%
    add_row(Source = 'Total', WordCount = sum(blogsWords,newsWords,twitterWords),
            Lines = sum(blogsLines,newsLines,twitterLines))

# Set seed for reproducibility
set.seed(13)

# Subset our data, only taking 25%
samplePct <- 0.25

blogsSample <- blogs[sample(seq_len(blogsLines),blogsLines*samplePct)]
newsSample <- news[sample(seq_len(newsLines),newsLines*samplePct)]
twitterSample <- twitter[sample(seq_len(twitterLines),twitterLines*samplePct)]

# Save our sample data for re-use
writeLines(blogsSample, con = 'Data/Sample/blogs.txt', sep = '\n', useBytes = FALSE)
writeLines(newsSample, con = 'Data/Sample/news.txt', sep = '\n', useBytes = FALSE)
writeLines(twitterSample, con = 'Data/Sample/twitter.txt', sep = '\n', useBytes = FALSE)

rm(blogs,news,twitter,blogsLines,newsLines,twitterLines)

###################### TASK 0 END ######################

###################### TASK 1 START ######################

# Create a corpus
library(tm)
library(RWeka)
# Increase heap space for package
options(java.parameters = "-Xmx15g")
library(stringi)

sampleCorp <- VCorpus(DirSource('Data/Sample', pattern = '.txt', encoding = 'UTF-8'))

# Save corpus
save(sampleCorp, file = 'Data/Sample/sampleCorp.RData')

rm(blogsSample,newsSample,twitterSample)

# Load profanity list for later use
profanity <- readLines('profanity.txt', encoding = 'UTF-8')
profanity <- iconv(profanity, "latin1", "ASCII", sub = "")

# Remove URL and email characters
sampleCorp <- tm_map(sampleCorp, content_transformer(function(x, pattern) gsub(pattern, " ", x)),"(f|ht)tp(s?)://(.*)[.][a-z]+")
sampleCorp <- tm_map(sampleCorp, content_transformer(function(x, pattern) gsub(pattern, " ", x)),"@[^\\s]+")
sampleCorp <- tm_map(sampleCorp, content_transformer(function(x, pattern) gsub(pattern, " ", x)),"\\b[A-Z a-z 0-9._ - ]*[@](.*?)[.]{1,3} \\b")

# Remove common stopwords
# sampleCorp <- tm_map(sampleCorp, removeWords, stopwords('english'))

# Remove profanity
sampleCorp <- tm_map(sampleCorp, removeWords, profanity)

# Lower case
sampleCorp <- tm_map(sampleCorp, content_transformer(tolower))

# Remove punctuation and numbers
sampleCorp <- tm_map(sampleCorp, content_transformer(removePunctuation))
sampleCorp <- tm_map(sampleCorp, content_transformer(removeNumbers))
sampleCorp <- tm_map(sampleCorp, stripWhitespace)

# Save file as .rds
saveRDS(sampleCorp, file = 'finalCorpus.rds')

###################### TASK 1 END ######################

###################### TASK 2 START ######################

# Now let's begin our exploratory analysis
library(RColorBrewer)
library(gridExtra)
library(wordcloud2)
library(ggplot2)
library(textmineR)
library(quanteda)

# Make ngrams
unigram <- tokens(x = corpus(sampleCorp), ngrams = 1, remove_numbers = TRUE, remove_punct = TRUE,
                  remove_symbols = TRUE, remove_separators = TRUE, remove_twitter = TRUE,
                  remove_url = TRUE, verbose = TRUE) %>%
    dfm() %>%
    textstat_frequency()

bigram <- tokens(x = corpus(sampleCorp), ngrams = 2, remove_numbers = TRUE, remove_punct = TRUE,
                 remove_symbols = TRUE, remove_separators = TRUE, remove_twitter = TRUE,
                 remove_url = TRUE, verbose = TRUE) %>%
    dfm() %>%
    textstat_frequency()

trigram <- tokens(x = corpus(sampleCorp), ngrams = 3, remove_numbers = TRUE, remove_punct = TRUE,
                  remove_symbols = TRUE, remove_separators = TRUE, remove_twitter = TRUE,
                  remove_url = TRUE, verbose = TRUE) %>%
    dfm() %>%
    textstat_frequency()

quadgram <- tokens(x = corpus(sampleCorp), ngrams = 4, remove_numbers = TRUE, remove_punct = TRUE,
                   remove_symbols = TRUE, remove_separators = TRUE, remove_twitter = TRUE,
                   remove_url = TRUE, verbose = TRUE) %>%
    dfm() %>%
    textstat_frequency()

# Only keep terms that appear more than 1 time
unigram <- unigram[unigram$frequency >= 2, ]
bigram <- bigram[bigram$frequency >= 2, ]
trigram <- trigram[trigram$frequency >= 2, ]
quadgram <- quadgram[quadgram$frequency >= 2, ]

# Save ngrams
save(unigram, file = "Data/Sample/unigram.Rda")

save(bigram, file = "Data/Sample/bigram.Rda")

save(trigram, file = "Data/Sample/trigram.Rda")

save(quadgram, file = "Data/Sample/quadgram.Rda")

# Plot 15 most frequent words
unigramExclStop <- tokens_select(tokens(x = corpus(sampleCorp), ngrams = 1, remove_numbers = TRUE, remove_punct = TRUE,
                                        remove_symbols = TRUE, remove_separators = TRUE, remove_twitter = TRUE,
                                        remove_url = TRUE, verbose = TRUE), pattern = stopwords('en'),
                                 selection = 'remove') %>%
    dfm() %>%
    textstat_frequency()

bigramExclStop <- tokens_select(tokens(x = corpus(sampleCorp), ngrams = 2, remove_numbers = TRUE, remove_punct = TRUE,
                                       remove_symbols = TRUE, remove_separators = TRUE, remove_twitter = TRUE,
                                       remove_url = TRUE, verbose = TRUE), pattern = stopwords('en'),
                                selection = 'remove') %>%
    dfm() %>%
    textstat_frequency()

trigramExclStop <- tokens_select(tokens(x = corpus(sampleCorp), ngrams = 3, remove_numbers = TRUE, remove_punct = TRUE,
                                        remove_symbols = TRUE, remove_separators = TRUE, remove_twitter = TRUE,
                                        remove_url = TRUE, verbose = TRUE), pattern = stopwords('en'),
                                 selection = 'remove') %>%
    dfm() %>%
    textstat_frequency()

quadgramExclStop <- tokens_select(tokens(x = corpus(sampleCorp), ngrams = 4, remove_numbers = TRUE, remove_punct = TRUE,
                                         remove_symbols = TRUE, remove_separators = TRUE, remove_twitter = TRUE,
                                         remove_url = TRUE, verbose = TRUE), pattern = stopwords('en'),
                                  selection = 'remove') %>%
    dfm() %>%
    textstat_frequency()

g <- ggplot(data = unigramExclStop[1:15,], aes(x = reorder(unigramExclStop[1:15,]$feature,-unigramExclStop[1:15,]$frequency),
                                               y = unigramExclStop[1:15,]$frequency)) +
    geom_bar(fill = "darkseagreen3", stat = 'identity') +
    labs(x = '', y = 'Word Count', title = 'Top 15 Most Common Unigrams') +
    theme(axis.text.x = element_text(angle = 45, hjust = 1))
g

h <- ggplot(data = bigramExclStop[1:15,], aes(x = reorder(bigramExclStop[1:15,]$feature,-bigramExclStop[1:15,]$frequency),
                                              y = bigramExclStop[1:15,]$frequency)) +
    geom_bar(fill = "darkseagreen3", stat = 'identity') +
    labs(x = '', y = 'Word Count', title = 'Top 15 Most Common Bigrams') +
    theme(axis.text.x = element_text(angle = 45, hjust = 1))
h

i <- ggplot(data = trigramExclStop[1:10,], aes(x = reorder(trigramExclStop[1:10,]$feature,-trigramExclStop[1:10,]$frequency),
                                               y = trigramExclStop[1:10,]$frequency)) +
    geom_bar(fill = "darkseagreen3", stat = 'identity') +
    labs(x = '', y = 'Word Count', title = 'Top 10 Most Common Trigrams') +
    theme(axis.text.x = element_text(angle = 45, hjust = 1))
i

j <- ggplot(data = quadgramExclStop[1:10,], aes(x = reorder(quadgramExclStop[1:10,]$feature,-quadgramExclStop[1:10,]$frequency),
                                        y = quadgramExclStop[1:10,]$frequency)) +
    geom_bar(fill = "darkseagreen3", stat = 'identity') +
    labs(x = '', y = 'Word Count', title = 'Top 10 Most Common Quadgram') +
    theme(axis.text.x = element_text(angle = 45, hjust = 1))
j

grid.arrange(g,h,i,j,nrow = 2)

# Create wordcloud
wordcloud2(unigramExclStop[1:500,1:2], color = "random-light", backgroundColor = "grey", minRotation = -pi/4,
           maxRotation = pi/4, size = 0.5)

###################### TASK 2 END ######################

###################### TASK 3 START ######################

# Build text prediction
library(stringr)
library(stringi)
library(dplyr)

bigram$feat1 <- word(bigram$feature, 1, sep = '_')
bigram$resp <- word(bigram$feature, -1, sep = '_')

trigram$feat1feat2 <- gsub('_', ' ', word(trigram$feature, 1, 2, sep = '_'))
trigram$resp <- word(trigram$feature, -1, sep = '_')

quadgram$feat1feat2feat3 <- gsub('_', ' ', word(quadgram$feature, 1, 3, sep = '_'))
quadgram$resp <- word(quadgram$feature, -1, sep = '_')

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