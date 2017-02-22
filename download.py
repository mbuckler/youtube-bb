
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

from __future__ import unicode_literals
import imageio
from ffmpy import FFmpeg
from subprocess import check_call
from concurrent import futures
from random import shuffle
import subprocess
import youtube_dl
import socket
import os
import io
import sys
import csv

# The data sets to be downloaded
#d_sets = ['yt_bb_classification_validation']
d_sets = ['yt_bb_classification_train',
          'yt_bb_classification_validation',
          'yt_bb_detection_train',
          'yt_bb_detection_validation']


# Host location of segment lists
web_host = 'https://research.google.com/youtube-bb/'

# Video clip class
class video_clip(object):
  def __init__(self,name,yt_id,start,stop,class_id,obj_id,d_set_dir):
    # name = yt_id+class_id+object_id
    self.name     = name
    self.yt_id    = yt_id
    self.start    = start
    self.stop     = stop
    self.class_id = class_id
    self.obj_id   = obj_id
    self.d_set_dir = d_set_dir
  def print_all(self):
    print('['+self.name+', '+ \
              self.yt_id+', '+ \
              self.start+', '+ \
              self.stop+', '+ \
              self.class_id+', '+ \
              self.obj_id+']\n')

# Download and cut a clip to size
def dl_and_cut(clip):

  d_set_dir = clip.d_set_dir

  # Make the class directory if it doesn't exist yet
  class_dir = d_set_dir+'/'+str(clip.class_id)
  check_call(['mkdir', '-p', class_dir])

# Create a temporary folder for this download to proceed in
  check_call(['mkdir', '-p', d_set_dir+'/'+clip.name+'/'])

  # Use youtube_dl to download the video
  FNULL = open(os.devnull, 'w')
  check_call(['youtube-dl', \
    #'--no-part', \
    '--no-progress', \
    '-f','best[ext=mp4]', \
    '-o',d_set_dir+'/'+clip.name+'/'+clip.name+'_temp.mp4', \
    'youtu.be/'+clip.yt_id ], \
     stdout=FNULL,stderr=subprocess.STDOUT )

  # Verify that the file has been downloaded. Skip otherwise
  if os.path.exists(d_set_dir+'/'+clip.name+'/'+clip.name+'_temp.mp4'):
    # Cut out the clip within the downloaded video and save the clip
    # in the correct class directory. Note that the -ss argument coming
    # first tells ffmpeg to start off with an I frame (no frozen start).
    check_call(['ffmpeg',\
      '-ss', str(float(clip.start)/1000),\
      '-i','file:'+d_set_dir+'/'+clip.name+'/'+clip.name+'_temp.mp4',\
      '-t', str((float(clip.start)+float(clip.stop))/1000),\
      '-c','copy',class_dir+'/'+clip.name+'.mp4'],
        stdout=FNULL,stderr=subprocess.STDOUT)

    # Remove the temporary video
    check_call(['rm','-rf',d_set_dir+'/'+clip.name])


# Parse the annotation csv file and schedule downloads and cuts
def parse_and_sched(dl_dir='videos',num_threads=4):
  """Download the entire youtube-bb data set into `dl_dir`.
  """

  # Make the download directory if it doesn't already exist
  check_call(['mkdir', '-p', dl_dir])

  # For each of the four datasets
  for d_set in d_sets:

    # Make the directory for this dataset
    d_set_dir = dl_dir+'/'+d_set+'/'
    check_call(['mkdir', '-p', d_set_dir])

    if ('classification' in d_set):
      class_or_det = 'class'
    elif ('detection' in d_set):
      class_or_det = 'det'

    # Download & extract the annotation list
    print (d_set+': Downloading annotations...')
    check_call(['wget', web_host+d_set+'.csv.gz'])
    print (d_set+': Unzipping annotations...')
    check_call(['gzip', '-d', '-f', d_set+'.csv.gz'])

    print (d_set+': Parsing annotations into clip data...')
    # Parse csv data
    with open((d_set+'.csv'), 'rt') as f:
      reader      = csv.reader(f)
      annotations = list(reader)

    current_clip_name = ['blank']
    clips             = []

    # Parse annotations into list of clips with names, youtube ids, start
    # times and stop times
    for idx, annotation in enumerate(annotations):
      # If this is for a classify dataset there is no object id
      if (class_or_det == 'class'):
        obj_id = '0'
      elif (class_or_det == 'det'):
        obj_id = annotation[4]
      yt_id    = annotation[0]
      class_id = annotation[2]

      clip_name = yt_id+'+'+class_id+'+'+obj_id

      # If this is a new clip
      if clip_name != current_clip_name:

        # Update the finishing clip
        if idx != 0: # If this isnt the first clip
          clips[-1].stop = annotations[idx-1][1]

        # Add the starting clip
        clip_start = annotation[1]
        clips.append( video_clip( \
          clip_name, \
          yt_id, \
          clip_start, \
          '0', \
          class_id, \
          obj_id, \
          d_set_dir) )

        # Update the current clip name
        current_clip_name = clip_name

    # Update the final clip with its stop time
    clips[-1].stop = annotations[-1][1]

    # Shuffle the clips 
    shuffle(clips)

    # Download and cut in parallel threads giving 
    with futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
      fs = [executor.submit(dl_and_cut,clip) for clip in clips]
      for i, f in enumerate(futures.as_completed(fs)):
        # Write progress to error so that it can be seen
        sys.stderr.write( \
          "Downloaded clip: {} / {} \r".format(i, len(clips)))
    
    print( d_set+': All clips downloaded' )

if __name__ == '__main__':
  # Use the directory `videos` in the current working directory by
  # default, or a directory specified on the command line.
  print(sys.argv[1])
  print(sys.argv[2])
  parse_and_sched(sys.argv[1],int(sys.argv[2]))
