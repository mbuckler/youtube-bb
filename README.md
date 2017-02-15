# YouTube BoundingBox

This repo contains helpful scripts for using the [YouTube BoundingBoxes](
https://research.google.com/youtube-bb/index.html) 
dataset released by Google Research. The only current hosting method 
provided for the dataset is [annotations in csv
form](https://research.google.com/youtube-bb/download.html). The csv files contain links to the videos on YouTube, but it's up to you to download the video files themselves. For this
reason, these scripts are provided for downloading, cutting, and decoding
the videos into a usable form.

These scripts were written by Mark Buckler and the YouTube BoundingBoxes
dataset was created and curated by Esteban Real, Jonathon Shlens,
Stefano Mazzocchi, Xin Pan, and Vincent Vanhoucke. The dataset web page
is [here](https://research.google.com/youtube-bb/index.html) and the
accompanying whitepaper is [here](https://arxiv.org/abs/1702.00824).

## Installing the dependencies

1. Clone this repository.

2. Install majority of dependencies by running 
`pip install -r requirements.txt` in this repo's directory.

3. Install [ffmpeg](https://ffmpeg.org/). For most platforms this should
	 be straightforward, but for Ubuntu 14.04 users you will need to
update your apt-get repository before being able to install as [shown
here](https://www.faqforge.com/linux/how-to-install-ffmpeg-on-ubuntu-14-04/).

The script also requires `wget` to download files.
Some small tweaks may be needed for different software environments.
These scripts were developed and tested on Ubuntu 14.04.

## Running the scripts

### Download

The `download.py` script is provided for users who are interested in
downloading the videos which accompany the provided annotations and then
cutting these videos down to the range in which they have been
annotated.

Run `python download.py [DIR]` to download the dataset into the specified
directory. If you don't provide a path, a directory named `videos` will be
created.

Then wait (for quite a long time...).

### Decode

Once your downloading has completed you may be interested in decoding
the videos into individual still frames. If this is the case, use the
decoding script.

1. Edit `decode.py` to point to where your videos were downloaded to, and
	 also where you would like the decoded frames to go.

2. Run `python decode.py` in this repo's directory.
