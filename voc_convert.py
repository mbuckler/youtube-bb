
########################################################################
# YouTube BoundingBox VOC2007 Converter
########################################################################
#
# This script converts the downloaded YouTube BoundingBox detection
# dataset into the VOC2007 format. This includes decoding the source
# videos into frames. If you do not yet have the source videos then
# be sure to run the download script first.
#
# Author: Mark Buckler
#
########################################################################

from __future__ import unicode_literals
import youtube_bb
import sys
import random
import os
import subprocess
from PIL import Image
from concurrent import futures
from subprocess import check_call

## Decode all the clips in a given vid
def decode_frame(clips,annot,d_set,src_dir,dest_dir):
  yt_id    = annot[0]
  class_id = annot[2]
  obj_id   = annot[4]
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

  # Extract a frame at that time stamp to the appropriate place within the
  # destination directory
  frame_dest = dest_dir+'/youtubebbdevkit/youtubebb2017/JPEGImages/'
  frame_name = yt_id+'+'+class_id+'+'+obj_id+'+'+str(annot_time)+'.jpg'
  FNULL = open(os.devnull, 'w')
  check_call(['ffmpeg',\
    '-ss', str(float(decode_time)/1000),\
    '-i', (annot_clip_path+annot_clip_name),\
    '-qscale:v','2',\
    '-vframes','1',\
    (frame_dest+frame_name)],\
    stdout=FNULL,stderr=subprocess.STDOUT )


def decode_frames(d_set,src_dir,dest_dir,num_threads,num_annots):
  # Get list of annotations
  # Download & extract the annotation list
  annotations,clips,vids = youtube_bb.parse_annotations(d_set,src_dir)

  # Filter out annotations with no matching video
  print(d_set+': Filtering out annotations for missing videos...')
  present_annots = []
  for annot in annotations:
    yt_id    = annot[0]
    class_id = annot[2]
    obj_id   = annot[4]
    annot_clip_path = src_dir+'/'+d_set+'/'+class_id+'/'
    annot_clip_name = yt_id+'+'+class_id+'+'+obj_id+'.mp4'
    if (os.path.exists(annot_clip_path+annot_clip_name)):
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
  with futures.ProcessPoolExecutor(max_workers=num_threads) as executor:
    fs = [executor.submit(decode_frame,clips,annot,d_set,src_dir,dest_dir) \
            for annot in annot_to_convert]
    for i, f in enumerate(futures.as_completed(fs)):
      # Write progress to error so that it can be seen
      sys.stderr.write( \
        "Decoded frame: {} / {} \r".format(i, len(annot_to_convert)))

  print(d_set+': Finished decoding frames!')

  return annot_to_convert

def write_xml_annot(

def write_xml_annots(dest_dir,annots):

  # For each annotation
  for annot in annots:
    # Get file details
    yt_id      = annot[0]
    annot_time = annot[1]
    class_id   = annot[2]
    obj_id     = annot[4]
    annot_name = yt_id+'+'+class_id+'+'+obj_id+'+'annot_time
    filename   = annot_name+'.jpg'

    # Get image dimensions
    img = Image.open(dest_dir + \
                     'youtubebbdevkit/youtubebb2017/JPEGImages/' + \
                     filename)
    image_width  = img.get_width()
    image_height = img.get_height()

    # Check to see if this annotation is on the border
    # (likely a truncated annotation)
    xmin_frac = float(annot[6])
    xmax_frac = float(annot[7])
    ymin_frac = float(annot[8])
    ymax_frac = float(annot[9])
    if ( (xmin_frac == 0.0) or (xmax_frac == 1.0) or \
            (ymin_frac == 0.0) or (ymax_frac == 1.0) ):
      truncated = 1
    else:
      truncated = 0

    # Convert bounding boxes to pixel dimensions
    xmin_pix = int(float(image_width)*xmin_frac)
    ymin_pix = int(float(image_height)*ymin_frac)
    xmax_pix = int(float(image_width)*xmax_frac)
    ymax_pix = int(float(image_height)*ymax_frac)

    xml_params = xml_annot( \
      annot_name,
      filename,
      annot,
      image_width,
      image_height,
      truncated,
      xmin,
      ymin,
      xmax,
      ymax)

    write_xml_annot(xml_params)


if __name__ == '__main__':

  assert(len(sys.argv) == 6), \
    ["Usage: python voc_convert.py [VID_SOURCE] [DSET_DEST] [NUM_THREADS]",
     "[NUM_TRAIN] [NUM_VAL]"]
  src_dir          = sys.argv[1]+'/'
  dest_dir         = sys.argv[2]+'/'
  num_threads      = int(sys.argv[3])
  num_train_frames = int(sys.argv[4])
  num_val_frames   = int(sys.argv[5])

  # Download VOC 2007 devkit
  devkit_link = \
    "http://host.robots.ox.ac.uk/pascal/VOC/voc2007/VOCdevkit_08-Jun-2007.tar"
  check_call(['wget','-P',dest_dir,devkit_link])

  # Extract, rename, add missing directories
  check_call(['tar','-xvf',
              dest_dir+'VOCdevkit_08-Jun-2007.tar',
              '-C',dest_dir])
  check_call(['rm',dest_dir+'VOCdevkit_08-Jun-2007.tar'])
  check_call(['mv',dest_dir+'VOCdevkit',dest_dir+'youtubebbdevkit'])
  check_call(['mkdir','-p',
              dest_dir+'youtubebbdevkit/youtubebb2017/ImageSets/Main'])
  check_call(['mkdir','-p',
              dest_dir+'youtubebbdevkit/youtubebb2017/ImageSets/Layout'])
  check_call(['mkdir','-p',
              dest_dir+'youtubebbdevkit/youtubebb2017/JPEGImages'])
  check_call(['mkdir','-p',
              dest_dir+'youtubebbdevkit/youtubebb2017/Annotations'])

  # Decode frames for training detection
  train_frame_annots = decode_frames(youtube_bb.d_sets[2],
    src_dir,
    dest_dir,
    num_threads,
    num_train_frames)

  write_xml_annots(

  # Decode frames for validation detection
  '''
  val_frame_annots = decode_frames(youtube_bb.d_sets[3],
    src_dir,
    dest_dir,
    num_threads,
    num_val_frames)
  '''

  # Write txt files
  '''
  TBD
  '''


