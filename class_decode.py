
########################################################################
# YouTube BoundingBox Classification Decoder
########################################################################
#
# This script decodes the downloaded YouTube BoundingBox classification dataset
# into its labeled frames. If you do not yet have the source videos then be sure
# to run the download script first.
#
# Author: Mark Buckler
#
########################################################################

from __future__ import unicode_literals
import youtube_bb
import sys
import random
import os
import csv
import subprocess
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.dom import minidom
from PIL import Image
from concurrent import futures
from subprocess import check_call

## Decode all the clips in a given vid
def decode_frame(clips,
                 annot,
                 max_ratio,
                 d_set,
                 src_dir,
                 dest_dir):
  yt_id    = annot[0]
  class_id = annot[2]
  obj_id   = '0' # Set to zero since classification task has no object
  annot_clip_path = src_dir+'/'+d_set+'/'+class_id+'/'
  annot_clip_name = yt_id+'+'+class_id+'+'+obj_id+'.mp4'
  clip_name       = yt_id+'+'+class_id+'+'+obj_id

  # Find the clip in vids
  clip = next((x for x in clips if x.name == clip_name), None)
  assert(clip != None), \
    "Annotation doesn't have a corresponding clip"

  # Convert the annotation time stamp (in original video) to a time in the clip
  annot_time  = float(annot[1])
  clip_start  = float(clip.start)
  decode_time = annot_time - clip_start

  # Make the class directory if it doesn't already exist
  frame_dest = dest_dir+'/'+d_set+'/'+str(class_id)+'/'
  if not os.path.exists(frame_dest):
      os.makedirs(frame_dest)

  # Extract a frame at that time stamp to the appropriate place within the
  # destination directory
  frame_name = yt_id+'+'+class_id+'+'+obj_id+'+'+str(int(annot_time))+'.jpg'
  FNULL = open(os.devnull, 'w')
  check_call(['ffmpeg',\
      '-ss', str(float(decode_time)/1000.0),\
      '-i', (annot_clip_path+annot_clip_name),\
      '-qscale:v','2',\
      '-vframes','1',\
      '-threads','1',\
      (frame_dest+frame_name)],\
      stdout=FNULL,stderr=subprocess.STDOUT )

  with Image.open(frame_dest+frame_name) as img:
          width, height = img.size
  # If this frame's aspect ratio exheeds the maximum aspect ratio
  if ( (max_ratio!=0) and \
         ( ((width/height) > max_ratio) or
           ((height/width) > max_ratio) ) ):
      os.remove(frame_dest+frame_name)


def decode_frames(d_set,
                  src_dir,
                  dest_dir,
                  num_threads,
                  num_annots,
                  max_ratio,
                  include_absent):
  # Get list of annotations
  # Download & extract the annotation list
  annotations,clips,vids = youtube_bb.parse_annotations(d_set,src_dir)

  # Filter out annotations with no matching video
  print(d_set + \
    ': Filtering out last, missing, and or absent frames (if requested)...')
  present_annots = []
  for annot in annotations:
    yt_id    = annot[0]
    class_id = annot[2]
    obj_id   = '0' # Set to zero since classification task has no object
    annot_clip_path = src_dir+'/'+d_set+'/'+class_id+'/'
    annot_clip_name = yt_id+'+'+class_id+'+'+obj_id+'.mp4'
    clip_name = yt_id+'+'+class_id+'+'+obj_id
    # If video exists
    if (os.path.exists(annot_clip_path+annot_clip_name)):
      # If we are including all frames, or if the labeled object is present
      if ( include_absent or (annot[4]=='present') ):
        # If this is not the first or last frame
        annot_clip = next((x for x in clips if x.name == clip_name), None)
        if ((int(annot_clip.stop ) != int(annot[1])) and \
            (int(annot_clip.start) != int(annot[1]))):
          present_annots.append(annot)

  # Gather subset of random annotations
  print(d_set+': Gathering annotations/frames to decode...')
  random.shuffle(present_annots)
  if num_annots == 0: # Convert all present annotations
    annot_to_convert = present_annots
  else:
    assert(len(present_annots) >= num_annots), \
      "Number of frames requested exceeds number of present frames"
    annot_to_convert = present_annots[:num_annots]

  # Run frame decoding in parallel, extract frames from each video
  #for annot in annot_to_convert:
  #  decode_frame(clips,annot,d_set,src_dir,dest_dir)
  
  with futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
    fs = [executor.submit( \
            decode_frame,clips,annot,max_ratio,d_set,src_dir,dest_dir) \
            for annot in annot_to_convert]
    for i, f in enumerate(futures.as_completed(fs)):
      # Check for an exception in the workers.
      try:
        f.result()
      except Exception as exc:
        print('decode failed', exc)
      else:
        # Write progress to error so that it can be seen
        sys.stderr.write( \
          "Decoded frame: {} / {} \r".format(i, len(annot_to_convert)))
  
  print(d_set+': Finished decoding frames!')

  return annot_to_convert


if __name__ == '__main__':

  assert(len(sys.argv) == 8), \
    "Usage: python3 class_decode.py [VID_SOURCE] [FRAME_DEST] [NUM_THREADS] " \
    "[NUM_TRAIN] [NUM_VAL] [MAX_RATIO] [INCL_ABS]"
  src_dir          = sys.argv[1]+'/'
  dest_dir         = sys.argv[2]+'/'
  num_threads      = int(sys.argv[3])
  num_train_frames = int(sys.argv[4])
  num_val_frames   = int(sys.argv[5])
  max_ratio        = float(sys.argv[6])
  assert((sys.argv[7]=='0')or(sys.argv[7]=='1')), \
    ["Please indicate if frames with absent objects should be included with",
     "a 1, or should not be included with a 0"]
  if sys.argv[6] == '1':
    include_absent = True
  else:
    include_absent = False

  # Decode frames for training detection
  train_frame_annots = decode_frames('yt_bb_classification_train',
    src_dir,
    dest_dir,
    num_threads,
    num_train_frames,
    max_ratio,
    include_absent)

  # Decode frames for validation detection
  val_frame_annots = decode_frames('yt_bb_classification_validation',
    src_dir,
    dest_dir,
    num_threads,
    num_val_frames,
    max_ratio,
    include_absent)

