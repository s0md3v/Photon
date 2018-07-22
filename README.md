# Photon

Photon is a lightning fast web crawler which extracts URLs, files, intel & endpoints from a target.

![demo](https://image.ibb.co/bTNwBy/Screenshot_2018_07_22_12_07_30.png)

## Why Photon?

#### Intelligent Multi-Threading
Here's a secret, most of the tools floating on the internet aren't properly multi-threaded. They either supply a list of items to threads which results in multiple threads accessing the same item or they simply put a thread lock and end up rendering multi-threading useless.\
But **Photon** is different or should I "genius"? Take a look at [this](https://github.com/s0md3v/Photon/blob/38f64100d101fce897b4e0a5cfafdaeb129491d2/photon.py#L282) and decide yourself.

#### Ninja Mode
In **Ninja Mode**, 3 online services are used to make requests to the target on your behalf.\
So basically, now you have 4 clients making requests to the same server simultaneously which gives you a speed boost as well as delays requests from a single client.
Here's a comparison:
![ninja demo](https://image.ibb.co/mcNbTd/ninj.png)

#### Not Your Regular Crawler
Crawlers are supposed to recursively extract links right? Yeah but that's kinda boring so **Photon** goes beyond that.
It extracts & saves following information:
- URLs (in-scope & out-of-scope)
- URLs with parameters (`example.com/gallery.php?id=2`)
- Intel (emails, social media accounts, amazon buckets etc.)
- Files (pdf, png, xml etc.)
- JavaScript files & Endpoints present in them

### Usage

#### `-u --url`

Specifies the URL to crawl.

`python photon.py -u http://example.com`

#### `-l --level`

It specifies how much deeper should photon crawl

`python photon.py -u http://example.com -l 3`

Default Value: `2`

#### `-d --delay`

It specifies the delay between requests.

`python photon.py -u http://example.com -d 1`

Default Value: `0`

#### `-t --threads`

The number of threads to use.

`python photon.py -u http://example.com -t 10`

Default Value: `2`
The optimal number of threads depends on your connection speed as well as nature of the target server. If you have a decent network connection and the server doesn't have any rate limiting in place, you can use up to `100` threads.\
I like to use 10 threads most of the time.

#### `-c --cookie`

Cookie to send.\
`python photon.py -u http://example.com -c "PHPSSID=821b32d21"`

#### `-n --ninja`

It toggles Ninja Mode on/off.\

`python photon.py -u http://example.com --ninja`

Default Value: `False`

#### `-s --seeds`

Let's you add custom seeds, sperated by commas.

`python photon -u http://example.com -s "http://example.com/portals.html,http://example.com/blog/2018"`

### License
**Photon** is licensed under [GPL v3.0 license](https://www.gnu.org/licenses/gpl-3.0.en.html).
