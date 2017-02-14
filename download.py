
########################################################################
# YouTube BoundingBox Downloader
########################################################################
#
# This script downloads all videos within the YouTube BoundingBoxes
# dataset and cuts them to the defined clip size. It is accompanied by 
# a second script which parses the videos into single frames.
#
########################################################################

import imageio
imageio.plugins.ffmpeg.download()
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from subprocess import call
from pytube import YouTube
import pytube
import os.path
import sys
import csv

# Specify the directory to download the videos into:
dl_dir = '/home/mbuckler/datasets/youtube-bb/videos/'

# The data sets to be downloaded
d_sets = ['yt_bb_classification_train',
          'yt_bb_classification_validation',
          'yt_bb_detection_train',
          'yt_bb_detection_validation']

# Host location of segment lists
web_host = 'https://research.google.com/youtube-bb/'

# Video clip class
class video_clip(object):
  def __init__(self,name,yt_id,start,stop,class_id,obj_id):
    # name = yt_id+class_id+object_id
    self.name     = name
    self.yt_id    = yt_id
    self.start    = start
    self.stop     = stop
    self.class_id = class_id
    self.obj_id   = obj_id
  def print_all(self):
    print('['+self.name+', '+ \
              self.yt_id+', '+ \
              self.start+', '+ \
              self.stop+', '+ \
              self.class_id+', '+ \
              self.obj_id+']\n')

# Make the download directory if it doesn't already exist
call('mkdir -p '+dl_dir,shell=True)

# For each of the four datasets
for d_set in d_sets:

  # Make the directory for this dataset
  d_set_dir = dl_dir+'/'+d_set+'/'
  call('mkdir -p '+d_set_dir,shell=True)

  if ('classification' in d_set):
    class_or_det = 'class'
  elif ('detection' in d_set):
    class_or_det = 'det'

  # Download & extract the annotation list
  print (d_set+': Downloading annotations...')
  call('wget '+'\"'+web_host+d_set+'.csv.gz'+'\"',shell=True)
  print (d_set+': Unzipping annotations...')
  call('gzip -d -f '+d_set+'.csv.gz',shell=True)

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

    clip_name = yt_id+':'+class_id+':'+obj_id
                
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
        obj_id ) )
      
      # Update the current clip name
      current_clip_name = clip_name 

  # Update the final clip with its stop time
  clips[-1].stop = annotations[-1][1]

  # For each video clip
  for clip_idx, clip in enumerate(clips):
    # Inform user of progress
    print(d_set+': Downloading & cutting video ['+ \
            str(clip_idx)+'/'+str(len(clips))+']')
      
    # Use pytube to download the video
    try:
      yt = YouTube('http://youtu.be/'+clip.yt_id)
    except pytube.exceptions.PytubeError:
      print("Dead YouTube link")
      # If a dead link, skip
      continue

    yt.set_filename('temp_vid')

    # Get the highest resolution available
    video = yt.filter('mp4')[-1]
    video.download(d_set_dir)

    # Cut out the clip within the downloaded video
    ffmpeg_extract_subclip((d_set_dir+'temp_vid.mp4'), \
                           int(clip.start)/1000, \
                           int(clip.stop)/1000, \
                           targetname=(d_set_dir+clip.name+'.mp4'))

    # Remove the temporary video
    call('rm -rf '+d_set_dir+'temp_vid.mp4',shell=True)


