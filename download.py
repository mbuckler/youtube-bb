from pytube import YouTube
from subprocess import call
import csv

########################################################################
# YouTube BoundingBox Downloader
########################################################################
#
# This script downloads all videos within the YouTube BoundingBoxes
# dataset and parses them out into single frames for easy input to 
# single-frame benchmarks.
#
########################################################################
# 
# The data is parsed into the specified download directory as follows:
#
# dl_dir/class_id/youtube_id+object_id/time_stamp.jpeg
#
########################################################################

# Specify the directory to download dataset to:
dl_dir = '~/datasets/youtube-bb/'

# The data sets to be downloaded
d_sets = ['yt_bb_classification_train']
'''d_sets = ['yt_bb_classification_train',
          'yt_bb_classification_validation',
          'yt_bb_detection_train',
          'yt_bb_detection_validation']'''

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

# For each of the four datasets
for d_set in d_sets:
  if ('classification' in d_set):
    class_or_det = 'class'
  elif ('detection' in d_set):
    class_or_det = 'det'

  # Download & extract the annotation list
  print ('Now downloading annotations for '+d_set)
  call('wget '+'\"'+web_host+d_set+'.csv.gz'+'\"',shell=True)
  print ('Now unzipping annotations for '+d_set)
  call('gzip -d -f '+d_set+'.csv.gz',shell=True)

  print ('Now parsing '+d_set+' annotations into clip data')
  # Parse csv data
  with open((d_set+'.csv'), 'rt') as f:
    reader      = csv.reader(f)
    annotations = list(reader)

  current_clip_name = ['blank']
  clip_started      = False
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

    clip_name = yt_id+'_'+class_id+'_'+obj_id
                
    # If this is a new clip
    if clip_name != current_clip_name:
      current_clip_name = clip_name
      # If this clip hasn't started yet
      if clip_started == False:
        clip_start = annotation[1]

        # Add the clip to the list of clips
        clips.append( video_clip( \
          clip_name, \
          yt_id, \
          clip_start, \
          '0', \
          class_id, \
          obj_id ) )
        
        clip_started = True
      # STILL NEED TO END THE CLIP
      # If this clip is finishing
      elif clip_started == True:
      #  clip_stop = annotation[1]
      #  # Update the clip
      #  clips[-1].stop = clip_stop
        clip_started = False

  selection = clips[:5]
  for clip in selection:
    clip.print_all()




