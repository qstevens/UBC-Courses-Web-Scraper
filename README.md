# UBC-Courses-Web-Scraper
## Motivation
Initially this project was meant to replace [UBC-Web-Scraper](https://github.com/qstevens/UBC-Web-Scraper), a UBC-Courses scraper I previously wrote in JavaScript. The intention was to write more performant code and learn Python in the process, with the belief that optimizing standard Python code would make it run faster than my JavaScript implementation.

## Realization
After web scraper in synchronous Python code, I realized it was quite slow, but that did not deter me as I thought that it would perform significantly better after started sending HTTP requests asynchronously. And while this did perform better than the sychnronous version, it lagged far behind the JavaScript implementation. I though perhaps this may be due to the library I was using (grequests), so I looked into aiohttp. aiohttp performed about twice as well as grequests, but still not as good as JavaScript's request-promise.

## Performance
I tested the scrapers by running it on the UBC 2020S session. This set has a total of ~7000 pages to scrape. 
The results of the asynchronous web scrapers are as follows:
- Python - grequests: 360s
- Python - aiohttp: 163s
- JavaScript - request-promise: 60s

## Conclusion
From these results I concluded that either I am missing an significant optimization for handling asynchronous requests in Python (which is possible because this is the first program I've written in Python) or that JavaScript runs much faster. Either way, this marks the end of the Python experiment for web scrapers for me.
