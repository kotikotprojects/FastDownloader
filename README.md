# FastDownloader
Download files from the internet with a simple command line interface.
Will significantly speed up loading from sites that slow down single-threaded 
download speeds. Applicable to cdn of sites with pirated films, for example.


## Installation
- Install [pipx](https://pypa.github.io/pipx/installation/)
- Run `pipx install git+https://codeberg.org/kotikotprojects/FastDownloader`

## Usage
Provide direct link to file as argument.
```
fastdl https://example.com/big_file.zip
```
Use `-h` or `--help` to see all options.

## Important
Not all sites support adding a `Range` header, so if you get an error when loading - 
it’s impossible to speed it up, try using browser downloaders. 
For example, huggingface supports `Range` header, you can try it out. Notice that
huggingface does not cut down the download speed, so this application most likely will 
not help if your Internet speed is low.
