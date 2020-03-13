# UBC-Courses-Web-Scraper
## Motivation
Initially this project was planned to replace UBC-Web-Scraper, a UBC-Courses scraper I previously wrote in JavaScript. The intention was to write more performant code and learn Python in the process, with the belief that optimizing standard Python code would be enough to make it run faster than my JavaScript implementation.

## Performance
After completing a synchronous implementation of the web scraper in Python, I realized it was quite slow, but that did not deter me as I though that it would perform significantly better after I sent the HTTP requests asynchronously. And while it did perform better than the sychnronous version, it lagged far behind the JavaScript implementation.


## Results
I tested the scrapers by running it on the UBC 2020S session. This set has a total of ~7000 pages to scrape. 
The results of the asynchronous web scrapers are as follows:
- Python - grequests: 360s
- Python - aiohttp: 163s
- JavaScript - request-promise: 60s

## Conclusion
From these results I concluded that either I am missing an significant optimization for handling asynchronous requests in Python (which is possible because this is the first program I've written in Python) or that JavaScript runs much faster. Either way, this marks the end of the Python experiment for web scrapers for me.
