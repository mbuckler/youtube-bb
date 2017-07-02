
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

import youtube_bb
import sys
import random
from subprocess import check_call

## Decode all the clips in a given vid
#def decode_vid(vid,src_dir,dest_dir):
#  # Vid's time start from original youtube video
#  vid_start = vid.clips[0].start
#  for clip in vid.clips:
#    # Some vids (cut videos) contain multiple clips
#    # Convert the clip start time to its place in the cut video
#    clip_start_in_vid = int((clip.start-vid_start) / 1000)
#    num_frames = int((clip.stop - clip.start) / 1000)
#    clip_stop_in_vid = clip_start_in_vid + num_frames

#    for timestamp in range(clip_start_in_vid,clip_stop_in_vid+1):
#      # Extract frame

# Schedule the decoding of all videos
#def decode_vids(vids,d_set,src_dir,dest_dir,num_threads):
#  downloaded_vids = []
#  # Check if the videos were actually downloaded
#  for vid in vids:
#    for clip in vid.clips:
#      # If video exists (if download succeeded)
#      if ( src_dir+'/'+d_set+'/'+vid.yt_id):
#        downloaded_vids.append(vid)
#  # Extract frames from each video
#  with futures.ProcessPoolExecutor(max_workers=num_threads) as executor:
#    fs = [executor.submit(decode_vid,vid) for vid in downloaded_vids]
#    for i, f in enumerate(futures.as_completed(fs)):
#      # Write progress to error so that it can be seen
#      sys.stderr.write( \
#        "Decoded video: {} / {} \r".format(i, len(downloaded_vids)))
#
#  return downloaded_vids



# The annotations are not necessarily evenly distributed throughout
# each clip, so per-annotation decoding is necessary.

# Getting a list of all the data can be done by serially going through each
# annotation and checking to see if it's video is present.

def decode_frames(d_set,src_dir,dest_dir,num_threads,num_annots):
  # Get list of annotations
  # Download & extract the annotation list
  if not os.path.exists(d_set+'.csv'):
    print (d_set+': Downloading annotations...')
    check_call(['wget', web_host+d_set+'.csv.gz'])
    print (d_set+': Unzipping annotations...')
    check_call(['gzip', '-d', '-f', d_set+'.csv.gz'])
  print (d_set+': Parsing annotations into clip data...')
  # Parse csv data
  with open((d_set+'.csv'), 'rt') as f:
    reader      = csv.reader(f)
    annotations = list(reader)

  # Filter out annotations with no matching video
  present_annots = []
  for annot in annotations:
    annot_vid_path = src_dir+'/'+d_set+'/'''''''''''''''''''''''''''
    if (os.path.exists()):
      present_annots.append(annot)

  # Shuffle annotations
  random.shuffle(annotations)

  # Gather subset of annotations
  if num_annots != 0:
    annotations
    

  # For each annotation

  # Decode selected frames

  # Generate voc annotations

  # Indicate image train/validation status

  # Indicate image class status


if __name__ == '__main__':
  assert(len(sys.argv) == 6) \
    ["Usage: python voc_convert.py [VID_SOURCE] [DSET_DEST] [NUM_THREADS]",
     "[NUM_TRAIN] [NUM_VAL]"]
  src_dir     = sys.argv[1]
  dest_dir    = sys.argv[2]
  num_threads = sys.argv[3]
  num_train   = sys.argv[4]
  num_val     = sys.argv[5]
  # Download VOC 2007 devkit
  devkit_link = \
    "http://host.robots.ox.ac.uk/pascal/VOC/voc2007/VOCdevkit_08-Jun-2007.tar"
  check_call(["wget -P "+dest_dir+" "+devkit_link])

  # Decode frames for training
  decode_frames()

  # Decode frames for validation
  decode_frames()

