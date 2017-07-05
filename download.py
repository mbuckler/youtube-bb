
########################################################################
# YouTube BoundingBox Downloader
########################################################################
#
# This script downloads all videos within the YouTube BoundingBoxes
# dataset and cuts them to the defined clip size. It is accompanied by
# a second script which decodes the videos into single frames.
#
# Author: Mark Buckler
#
########################################################################
#
# The data is placed into the following directory structure:
#
# dl_dir/videos/d_set/class_id/clip_name.mp4
#
########################################################################

import youtube_bb
import sys
from subprocess import check_call

# Parse the annotation csv file and schedule downloads and cuts
def parse_and_sched(dl_dir='videos',num_threads=4):
  """Download the entire youtube-bb data set into `dl_dir`.
  """

  # Make the download directory if it doesn't already exist
  check_call(['mkdir', '-p', dl_dir])

  # For each of the four datasets
  for d_set in youtube_bb.d_sets:
    annotations,clips,vids = youtube_bb.parse_annotations(d_set,dl_dir)
    youtube_bb.sched_downloads(d_set,dl_dir,num_threads,vids)

if __name__ == '__main__':

  assert(len(sys.argv) == 3), \
          "Usage: python download.py [VIDEO_DIR] [NUM_THREADS]"
  # Use the directory `videos` in the current working directory by
  # default, or a directory specified on the command line.
  parse_and_sched(sys.argv[1],int(sys.argv[2]))
