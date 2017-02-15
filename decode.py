
########################################################################
# YouTube BoundingBox Decoder
########################################################################
#
# This script takes all of the videos within the YouTube BoundingBoxes
# dataset and parses them out into single frames for easy input to
# single-frame benchmarks. The videos must have been previously
# downloaded by the accompanying downloader script. Frames are decoded
# at 30 frames per second as per the dataset creators' recommendation.
#
# Author: Mark Buckler
#
########################################################################
#
# The data is placed into the following directory structure:
#
# /frames/d_set/class_id/clip_name/frame_idx.jpeg
#
# Note that clip name is defined as follows:
#
# clip_name = yt_id:class_id:object_id
#
########################################################################

from subprocess import check_call
from ffmpy import FFmpeg
import csv
import os
import sys
import glob

def decode(vid_dir='videos', frame_dir='frames'):
  """Using the videos downloaded in `vid_dir`, produce decoded frames in
  `frame_dir`.
  """

  # List the datasets
  d_sets = [f.path for f in os.scandir(vid_dir) if f.is_dir() ]

  # For each dataset
  for d_set in d_sets:

    # List the classes
    classes = [f.path for f in os.scandir(d_set) if f.is_dir() ]

    # For each class
    for class_ in classes:

      # List the clips
      clips = [f.path for f in os.scandir(class_) ]

      # For each clip, where clip is the path to the clip
      for clip in clips:
        clip_sub_dir = (clip.replace(vid_dir,''))[:-4]
        clip_out_dir = frame_dir + clip_sub_dir
        clip_name    = clip.split('/')[-1][:-4]

        # Change to the class directory (where the clip is)
        os.chdir(class_)

        # Decode the video into 30 fps frames with ffmpeg
        check_call(['ffmpeg', '-i', 'file:'+clip_name+'.mp4', '-vf', 'fps=30',
                    'frame_%06d.jpg'])

        # Create a directory for this clip
        check_call(['mkdir', '-p', clip_out_dir])

        # Move the results to the output directory
        for jpg in glob.glob('*.jpg'):
          check_call(['mv', jpg, clip_out_dir])

if __name__ == '__main__':
  decode(*sys.argv[1:])
