# Photon
Photon crawls a website for webpages, javascript files and endpoints present in javascript files.

![Photon demo](https://i.imgur.com/E9ij1jf.png)

### Usage
Crawling a website is this simple:
```
python photon.py http://example.com
```
You can also use a cookie:
```
python photon.py http://example.com --cookie="your_cookie_here"
```
Delaying requests is also possible as follows:
```
python photon.py http://example.com --delay=1.5
```

### Features
- [x] Extract URLs
- [x] Extract JavaScript files
- [x] Extract endpoints from JavaScripts files
- [x] Seperate list for fuzzable URLs
- [x] robots.txt & sitemap.xml scrapping
- [x] Cookie Support
- [ ] Better multithreading
- [ ] Other features :D
