
########################################################################
# YouTube BoundingBox
########################################################################
#
# This file contains useful functions for downloading, decoding, and
# converting the YouTube BoundingBox dataset.
#
# Author: Mark Buckler
#
########################################################################

from __future__ import unicode_literals
from ffmpy import FFmpeg
from subprocess import check_call
from concurrent import futures
from random import shuffle
from datetime import datetime
import subprocess
import youtube_dl
import socket
import os
import io
import sys
import csv

# Debug flag. Set this to true if you would like to see ffmpeg errors
debug = False

# The data sets to be downloaded
d_sets = [
          'yt_bb_detection_train',
          'yt_bb_detection_validation',
          'yt_bb_classification_train',
          'yt_bb_classification_validation',
          ]

# The classes included and their indices
class_list = [\
              [0,'person'],
              [1,'bird'],
              [2,'bicycle'],
              [3,'boat'],
              [4,'bus'],
              [5,'bear'],
              [6,'cow'],
              [7,'cat'],
              [8,'giraffe'],
              [9,'potted plant'],
              [10,'horse'],
              [11,'motorcycle'],
              [12,'knife'],
              [13,'airplane'],
              [14,'skateboard'],
              [15,'train'],
              [16,'truck'],
              [17,'zebra'],
              [18,'toilet'],
              [19,'dog'],
              [20,'elephant'],
              [21,'umbrella'],
              [22,'none'],
              [23,'car'],
              ]

# Host location of segment lists
web_host = 'https://research.google.com/youtube-bb/'

# Video clip class
class video_clip(object):
  def __init__(self,
               name,
               yt_id,
               start,
               stop,
               class_id,
               obj_id,
               d_set_dir):
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

# Video class
class video(object):
  def __init__(self,yt_id,first_clip):
    self.yt_id = yt_id
    self.clips = [first_clip]
  def print_all(self):
    print(self.yt_id)
    for clip in self.clips:
      clip.print_all()

# XML detection annotation class
class xml_annot(object):
  def __init__(self,
               annot_name,
               filename,
               annotation,
               image_width,
               image_height,
               truncated,
               xmin,
               ymin,
               xmax,
               ymax):
    self.annot_name     = annot_name
    self.folder         = "youtubebb2017"
    self.filename       = filename
    self.database       = "YouTube Bounding Box"
    self.annotation     = ",".join(annotation)
    self.image_source   = "YouTube"
    self.image_flickrid = "N/A"
    self.owner_name     = "N/A"
    self.owner_flickrid = "N/A"
    self.image_width    = str(image_width)
    self.image_height   = str(image_height)
    self.image_depth    = str(3)
    self.segmented      = str(0)
    self.class_name     = annotation[3]
    self.pose           = "Unspecified"
    self.truncated      = str(truncated)
    self.difficult      = str(0)
    self.xmin           = str(xmin)
    self.ymin           = str(ymin)
    self.xmax           = str(xmax)
    self.ymax           = str(ymax)


# Download and cut a clip to size
def dl_and_cut(vid):

  d_set_dir = vid.clips[0].d_set_dir

  # Use youtube_dl to download the video
  FNULL = open(os.devnull, 'w')
  check_call(['youtube-dl', \
    #'--no-progress', \
    '-f','best[ext=mp4]', \
    '-o',d_set_dir+'/'+vid.yt_id+'_temp.mp4', \
    'youtu.be/'+vid.yt_id ], \
     stdout=FNULL,stderr=subprocess.STDOUT )

  for clip in vid.clips:
    # Verify that the video has been downloaded. Skip otherwise
    if os.path.exists(d_set_dir+'/'+vid.yt_id+'_temp.mp4'):
      # Make the class directory if it doesn't exist yet
      class_dir = d_set_dir+'/'+str(clip.class_id)
      check_call(' '.join(['mkdir', '-p', class_dir]), shell=True)

      # Cut out the clip within the downloaded video and save the clip
      # in the correct class directory. Full re-encoding is used to maintain
      # frame accuracy. See here for more detail:
      # http://www.markbuckler.com/post/cutting-ffmpeg/
      if debug:
          check_call(['ffmpeg',\
            '-i','file:'+d_set_dir+'/'+vid.yt_id+'_temp.mp4',\
            '-ss', str(float(clip.start)/1000),\
            '-strict','-2',\
            '-t', str((float(clip.stop)-float(clip.start))/1000),\
            '-threads','1',\
            class_dir+'/'+clip.name+'.mp4'])
      else:
          # If not debugging, hide the error outputs from failed downloads
          check_call(['ffmpeg',\
            '-i','file:'+d_set_dir+'/'+vid.yt_id+'_temp.mp4',\
            '-ss', str(float(clip.start)/1000),\
            '-strict','-2',\
            '-t', str((float(clip.stop)-float(clip.start))/1000),\
            '-threads','1',\
            class_dir+'/'+clip.name+'.mp4'],
            stdout=FNULL,stderr=subprocess.STDOUT )

  # Remove the temporary video
  os.remove(d_set_dir+'/'+vid.yt_id+'_temp.mp4')


# Parse the annotation csv file and schedule downloads and cuts
def parse_annotations(d_set,dl_dir):

  d_set_dir = dl_dir+'/'+d_set+'/'

  # Download & extract the annotation list
  if not os.path.exists(d_set+'.csv'):
    print (d_set+': Downloading annotations...')
    check_call(' '.join(['wget', web_host+d_set+'.csv.gz']),shell=True)
    print (d_set+': Unzipping annotations...')
    check_call(' '.join(['gzip', '-d', '-f', d_set+'.csv.gz']), shell=True)

  print (d_set+': Parsing annotations into clip data...')

  # Parse csv data.
  annotations = []
  with open((d_set+'.csv'), 'rt') as f:
    reader = csv.reader(f)
    annotations = list(reader)

  # Sort to de-interleave the annotations for easier parsing. We use
  # `int(l[1])` to sort by the timestamps numerically; the other fields are
  # sorted lexicographically as strings.
  print(d_set + ': Sorting annotations...')
  if ('classification' in d_set):
    class_or_det = 'class'
    # Sort by youtube_id, class, and then timestamp
    annotations.sort(key=lambda l: (l[0], l[2], int(l[1])))
  elif ('detection' in d_set):
    class_or_det = 'det'
    # Sort by youtube_id, class, obj_id and then timestamp
    annotations.sort(key=lambda l: (l[0], l[2], l[4], int(l[1])))

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

  # Sort the clips by youtube id
  clips.sort(key=lambda x: x.yt_id)

  # Create list of videos to download (possibility of multiple clips
  # from one video)
  current_vid_id = ['blank']
  vids = []
  for clip in clips:

    vid_id = clip.yt_id

    # If this is a new video
    if vid_id != current_vid_id:
      # Add the new video with its first clip
      vids.append( video ( \
        clip.yt_id, \
        clip ) )
    # If this is a new clip for the same video
    else:
      # Add the new clip to the video
      vids[-1].clips.append(clip)

    # Update the current video name
    current_vid_id = vid_id

  return annotations,clips,vids

def sched_downloads(d_set,dl_dir,num_threads,vids):
  d_set_dir = dl_dir+'/'+d_set+'/'

  # Make the directory for this dataset
  check_call(' '.join(['mkdir', '-p', d_set_dir]), shell=True)

  # Tell the user when downloads were started
  datetime.now().strftime("%Y-%m-%d %H:%M:%S")

  # Download and cut in parallel threads giving
  with futures.ProcessPoolExecutor(max_workers=num_threads) as executor:
    fs = [executor.submit(dl_and_cut,vid) for vid in vids]
    for i, f in enumerate(futures.as_completed(fs)):
      # Write progress to error so that it can be seen
      sys.stderr.write( \
        "Downloaded video: {} / {} \r".format(i, len(vids)))

  print( d_set+': All videos downloaded' )

