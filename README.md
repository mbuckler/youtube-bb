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

3. Install wget, [ffmpeg](https://ffmpeg.org/) and 
[youtube-dl](https://github.com/rg3/youtube-dl) through your package 
manager. For most platforms this should be straightforward, but for 
Ubuntu 14.04 users you will need to update your apt-get repository 
before being able to install ffmpeg as [shown
here](https://www.faqforge.com/linux/how-to-install-ffmpeg-on-ubuntu-14-04/).

Some small tweaks may be needed for different software environments.
These scripts were developed and tested on Ubuntu 14.04.

## Running the scripts

Note: You will need to use at least Python 3.0. This script was developed with Python 3.5.2.

### Download

The `download.py` script is provided for users who are interested in
downloading the videos which accompany the provided annotations. It also
cuts these videos down to the range in which they have been
annotated. Parallel video downloads are supported so that you can
saturate your download bandwith even though YouTube throttles per-video.
I was able to download the Detection Validation videos (412 GB) in
roughly 3 hours.

Run `python download.py [VIDEO_DIR] [NUM_THREADS]` to download the dataset into the specified
directory. If you don't provide a path, a directory named `videos` will be
created. 

### Decode

Once your downloading has completed you may be interested in decoding
the videos into individual still frames. If this is the case, use the
decoding script. The script decodes all frames within the clips at 30
frames per second.

Run `python decode.py [VIDEO_DIR] [FRAME_DIR]`. The first parameter is the directory where your videos were downloaded to (default: `videos`), and the second is where you would like the decoded frames to go (default: `frames`).
