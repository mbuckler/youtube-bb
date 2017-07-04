
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
def decode_vid(annot,src_clip,dest_dir):

  # Vid's time start from original youtube video
  vid_start = vid.clips[0].start
  for clip in vid.clips:
    # Some vids (cut videos) contain multiple clips
    # Convert the clip start time to its place in the cut video
    clip_start_in_vid = int((clip.start-vid_start) / 1000)
    num_frames = int((clip.stop - clip.start) / 1000)
    clip_stop_in_vid = clip_start_in_vid + num_frames

    for timestamp in range(clip_start_in_vid,clip_stop_in_vid+1):
      # Extract frame



def decode_frames(d_set,src_dir,dest_dir,num_threads,num_annots):
  # Get list of annotations
  # Download & extract the annotation list
  annotations,vids = youtube_bb.parse_annotations(d_set,src_dir)

  # Filter out annotations with no matching video
  present_annots = []
  for annot in annotations:
    yt_id    = annot[0]
    class_id = annot[2]
    obj_id   = annot[4]
    annot_clip_path = src_dir+'/'+d_set+'/'+class_id+'/'
    annot_clip_name = yt_id+'+'+class_id+'+'+obj_id+'.mp4'
    if (os.path.exists(annot_clip_path+annot_clip_name)):
      present_annots.append(annot)

  # Shuffle annotations
  random.shuffle(present_annots)

  # Gather subset of annotations
  if num_annots == 0: # Convert all present annotations
    annot_to_convert = present_annots
  else:
    assert(len(present_annots) >= num_annots) \
      "Number of frames requested exceeds number of present frames"
    annot_to_convert = present_annots[:num_annots]

  # Run frame decoding in parallel, extract frames from each video
  with futures.ProcessPoolExecutor(max_workers=num_threads) as executor:
    fs = [executor.submit(decode_vid,vid) for vid in downloaded_vids]
    for i, f in enumerate(futures.as_completed(fs)):
      # Write progress to error so that it can be seen
      sys.stderr.write( \
        "Decoded video: {} / {} \r".format(i, len(downloaded_vids)))


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

