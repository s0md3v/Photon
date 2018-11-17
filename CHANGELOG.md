#### v1.1.4
- Added `-v` option
- Fixed progress animation for Python 2
- Added `developer.facebook.com` API for Ninja mode

#### v1.1.3
- Added `--stdout` option
- Fixed a bug in `zap()` function
- Fixed crashing when target is an IP address
- Minor refactor

#### v1.1.2
- Added `--wayback`
- Fixed progress bar for Python > 3.2 
- Added `/core/config.py` for easy customization
- `--dns` now saves subdomains in `subdomains.txt`

#### v1.1.1
- Use of `ThreadPoolExecutor` for x2 speed (for Python > 3.2)
- Fixed mishandling of urls starting with `//`
- Removed a redundant try-except statement
- Evaluate entropy of found keys to avoid false positives

#### v1.1.0
- Added `--keys` option
- Fixed a bug related to SSL certificate verification

#### v1.0.9
- Code refactor
- Better identification of external URLs
- Fixed a major bug that made several intel URLs pass under the radar
- Fixed a major bug that caused non-html type content to be marked a crawlable URL

#### v1.0.8
- added `--exclude` option
- Better regex and code logic to favor performance
- Fixed a bug that caused dnsdumpster to fail if target was a subdomain
- Fixed a bug that caused a crash if run outside "Photon" directory
- Fixed a bug in file saving (specific to Python 3)

#### v1.0.7
- Added `--timeout` option
- Added `--output` option
- Added `--user-agent` option
- Replaced lxml with regex
- Better logic for favoring performance
- Added bigger and separate file for user-agents

#### v1.0.6
- Fixed lot of bugs
- Suppress SSL warnings in MAC
- x100 speed by code optimization
- Simplified code of `exporter` plugin

#### v1.0.5
- Added `exporter` plugin
- Added seamless update ability
- Fixed a bug in update function

#### v1.0.4
- Fixed an issue which caused regular links to be saved in robots.txt
- Simplified `flash` function
- Removed `-n` as an alias of `--ninja`
- Added `--only-urls` option
- Refactored code for readability
- Skip saving files if the content is empty

#### v1.0.3
- Introduced plugins
- Added `dnsdumpster` plugin
- Fixed non-ascii character handling, again
- 404 pages are now added to `failed` list
- Handling exceptions in `jscanner`

#### v1.0.2
- Proper handling of null response from `robots.txt` & `sitemap.xml`
- Python2 compatibility
- Proper handling of non-ascii chars
- Added ability to specify custom regex pattern
- Display total time taken and average time per request

#### v1.0.1
- Disabled colors on Windows and macOS
- Cross platform file handling

#### v1.0.0
- First stable release
