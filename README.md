# YouTube BoundingBox

This repo contains helpful scripts for using the [YouTube BoundingBoxes](
https://research.google.com/youtube-bb/index.html) dataset released by Google
Research. The only current hosting method provided for the dataset is
[annotations in csv form](https://research.google.com/youtube-bb/download.html).
The csv files contain links to the videos on YouTube, but it's up to you to
download the video files themselves. For this reason, these scripts are provided
for downloading, cutting, and decoding the videos into a usable form.

These scripts were written by Mark Buckler and the YouTube BoundingBoxes dataset
was created and curated by Esteban Real, Jonathon Shlens, Stefano Mazzocchi, Xin
Pan, and Vincent Vanhoucke. The dataset web page is
[here](https://research.google.com/youtube-bb/index.html) and the accompanying
whitepaper is [here](https://arxiv.org/abs/1702.00824).

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

The `download.py` script is provided for the annoted videos. It also
cuts these videos down to the range in which they have been
annotated. Parallel video downloads are supported so that you can
saturate your download bandwith even though YouTube throttles per-video. Because
video clips are cut with FFmpeg re-encoding ([see here for
why](http://www.markbuckler.com/post/cutting-ffmpeg/)) the bottleneck is
compute speed rather than download speed. For this reason, set the number of
threads to the number of cores on your machine for best results.

	python3 download.py [VID_DIR] [NUM_THREADS]

- `[VID_DIR]` Directory to download videos into
- `[NUM_THREADS` Number of threads to use for downloading and cutting

### VOC 2007 Converter

For the detection task, a script for decoding frames and converting
the CSV annotations into the VOC 2007 XML format is provided. For
documentatation about the original VOC 2007 development kit and format [see
here](http://host.robots.ox.ac.uk/pascal/VOC/voc2007/devkit_doc_07-Jun-2007.pdf).
If you are interested in training [Faster RCNN](https://arxiv.org/abs/1506.01497)
on this dataset, [see here](https://github.com/mbuckler/py-faster-rcnn-youtubebb)
for my updates to the PyCaffe implementation of Faster RCNN.

	python3 voc_convert.py [VID_DIR] [DSET_DEST] [NUM_THREADS] [NUM_TRAIN] [NUM_VAL] [MAX_RATIO] [INCL_ABS]


- `[VID_DIR]` The source directory where you downloaded videos into
- `[DSET_DEST]` The destination directory for the converted dataset
- `[NUM_THREADS]` The number of threads to use for frame decoding
- `[NUM_TRAIN]` The number of training images to decode. Use 0 to decode all
  annotated frames
- `[NUM_VAL]` The number of validation images to decode. Use 0 to decode all
  annotated frames
- `[MAX_RATIO]` The maximum aspect ratio allowed. If the value is set to 0 then
  all frames will be decoded. Otherwise all frames with aspect ratios greater
  than the maximum will be deleted and not included in xml annotations.
- `[INCL_ABS]` Flag to include (1) or not include (0) frames in which the object
   of interest is absent.

### Full Decode

If you are interested in decoding all videos into still frames, a full decode
script is also provided. The script decodes all frames within the clips at 30
frames per second.

	python3 decode.py [VID_DIR] [FRAME_DIR]

- `[VID_DIR]` The source directory where you downloaded videos into
- `[FRAME_DIR]` The destination directory where you want the decoded frames
