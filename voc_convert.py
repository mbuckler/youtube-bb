
########################################################################
# YouTube BoundingBox VOC2007 Converter
########################################################################
#
# This script converts the downloaded YouTube BoundingBox detection
# dataset into the VOC2007 format. This includes decoding the source
# videos into frames. If you do not yet have the source videos then
# be sure to run the download script first.
#
# Original VOC 2007 Dataset devkit documentation:
# http://host.robots.ox.ac.uk/pascal/VOC/voc2007/devkit_doc_07-Jun-2007.pdf
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
  frame_dest = dest_dir+'/youtubebbdevkit2017/youtubebb2017/JPEGImages/'
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
    obj_id   = annot[4]
    annot_clip_path = src_dir+'/'+d_set+'/'+class_id+'/'
    annot_clip_name = yt_id+'+'+class_id+'+'+obj_id+'.mp4'
    clip_name = yt_id+'+'+class_id+'+'+obj_id
    # If video exists
    if (os.path.exists(annot_clip_path+annot_clip_name)):
      # If we are including all frames, or if the labeled object is present
      if ( include_absent or (annot[5]=='present') ):
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

def write_xml_annot(dest_dir,xml_params):
  # Write the xml annotation to file
  xml_annot = Element('annotation')

  folder = SubElement(xml_annot, 'folder')
  folder.text = xml_params.folder

  filename = SubElement(xml_annot, 'filename')
  filename.text = xml_params.filename

  source = SubElement(xml_annot, 'source')
  database = SubElement(source, 'database')
  database.text = xml_params.database
  annotation = SubElement(source, 'annotation')
  annotation.text = xml_params.annotation
  image_source = SubElement(source, 'image')
  image_source.text = xml_params.image_source
  image_flickrid = SubElement(source, 'flickrid')
  image_flickrid.text = xml_params.image_flickrid

  owner = SubElement(xml_annot, 'owner')
  owner_flickrid = SubElement(owner, 'flickrid')
  owner_flickrid.text = xml_params.owner_flickrid
  owner_name = SubElement(owner, 'name')
  owner_name.text = xml_params.owner_name

  size = SubElement(xml_annot, 'size')
  width = SubElement(size, 'width')
  width.text = xml_params.image_width
  height = SubElement(size, 'height')
  height.text = xml_params.image_height
  depth = SubElement(size, 'depth')
  depth.text = xml_params.image_depth

  segmented = SubElement(xml_annot, 'segmented')
  segmented.text = xml_params.segmented

  if ('present' in xml_params.annotation):
    object_ = SubElement(xml_annot, 'object')
    class_name = SubElement(object_, 'name')
    class_name.text = xml_params.class_name
    pose = SubElement(object_, 'pose')
    pose.text = xml_params.pose
    truncated = SubElement(object_, 'truncated')
    truncated.text = xml_params.truncated
    difficult = SubElement(object_, 'difficult')
    difficult.text = xml_params.difficult
    bndbox = SubElement(object_, 'bndbox')
    xmin = SubElement(bndbox, 'xmin')
    xmin.text = xml_params.xmin
    ymin = SubElement(bndbox, 'ymin')
    ymin.text = xml_params.ymin
    xmax = SubElement(bndbox, 'xmax')
    xmax.text = xml_params.xmax
    ymax = SubElement(bndbox, 'ymax')
    ymax.text = xml_params.ymax

  # Write the XML file
  xml_str = minidom.parseString(tostring(xml_annot)).toprettyxml(indent="   ")
  with open(dest_dir + \
            'youtubebbdevkit2017/youtubebb2017/Annotations/' + \
            xml_params.annot_name + \
            '.xml', 'w') as f:
    f.write(xml_str)

def write_xml_annots(dest_dir,annots):
  xml_annots = []
  # For each annotation
  for annot in annots:
    # Get file details
    yt_id      = annot[0]
    annot_time = annot[1]
    class_id   = annot[2]
    obj_id     = annot[4]
    annot_name = yt_id+'+'+class_id+'+'+obj_id+'+'+annot_time
    filename   = annot_name+'.jpg'
    frame_path = dest_dir + 'youtubebbdevkit2017/youtubebb2017/JPEGImages/'

    # Check to verify the frame was extracted
    if (os.path.exists(frame_path+filename)):
      # Get image dimensions
      img = Image.open(frame_path+filename)
      image_width,image_height  = img.size

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

      # Convert bounding boxes to pixel dimensions, set minimum as 1
      xmin_pix = int(float(image_width)*xmin_frac)
      if xmin_pix == 0: xmin_pix = 1
      ymin_pix = int(float(image_height)*ymin_frac)
      if ymin_pix == 0: ymin_pix = 1
      xmax_pix = int(float(image_width)*xmax_frac)
      ymax_pix = int(float(image_height)*ymax_frac)

      xml_params = youtube_bb.xml_annot( \
        annot_name,
        filename,
        annot,
        image_width,
        image_height,
        truncated,
        xmin_pix,
        ymin_pix,
        xmax_pix,
        ymax_pix)

      write_xml_annot(dest_dir,xml_params)
      xml_annots.append(xml_params)
  return xml_annots


def write_class_det_files(dest_dir, filename, xml_annots):
  out_file =  open((dest_dir + \
                    'youtubebbdevkit2017/youtubebb2017/ImageSets/Main/' + \
                    filename),
                    "w")
  for Layout_annot in xml_annots:
    out_file.write(Layout_annot.annot_name+'\n')
  out_file.close()

def write_class_files(dest_dir, filename, xml_annots, class_):
  out_file =  open((dest_dir + \
                    'youtubebbdevkit2017/youtubebb2017/ImageSets/Main/' + \
                    filename),
                   "w")
  # If this is not an empty list
  for Main_annot in xml_annots:
    if ((Main_annot.class_name == class_[1]) and \
        ('present' in Main_annot.annotation)):
      # Class of interest is present
      present_flag = '1'
    else:
      present_flag = '-1'
    out_file.write(Main_annot.annot_name+' '+present_flag+'\n')
  out_file.close()

def write_txt_files(dest_dir, train_xml_annots, val_xml_annots):

  # Get the list of classes
  class_list = youtube_bb.class_list

  # NOTE:
  # VOC converted test: YouTube BoundingBox validation
  # VOC converted train: YouTube BoundingBox training
  # VOC converted validation: Empty
  d_set_sections = ['test',
                    'train',
                    'trainval',
                    'val',
                    ]
  section_annots = [val_xml_annots,
                    train_xml_annots,
                    train_xml_annots,
                    [],
                    ]
  # Print Classification/Detection task files (test, train, trainval, val)
  for idx in range(len(d_set_sections)):
    write_class_det_files(dest_dir,
                      (d_set_sections[idx]+'.txt'),
                      section_annots[idx])

  # Print Classification task files (all classes for each dataset)
  for idx in range(len(d_set_sections)):
    for class_ in class_list:
      # Skip the None class (no examples for detection)
      if class_[1] != 'none':
        write_class_files(dest_dir,
                        (class_[1]+'_'+d_set_sections[idx]+'.txt'),
                        section_annots[idx],
                        class_)

if __name__ == '__main__':

  assert(len(sys.argv) == 8), \
    "Usage: python voc_convert.py [VID_SOURCE] [DSET_DEST] [NUM_THREADS] " \
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

  # Download VOC 2007 devkit
  devkit_link = \
    "http://host.robots.ox.ac.uk/pascal/VOC/voc2007/VOCdevkit_08-Jun-2007.tar"
  check_call(['wget','-P',dest_dir,devkit_link])

  # Extract, rename, add missing directories
  check_call(['tar','-xvf',
              dest_dir+'VOCdevkit_08-Jun-2007.tar',
              '-C',dest_dir])
  check_call(['rm',dest_dir+'VOCdevkit_08-Jun-2007.tar'])
  check_call(['mv',dest_dir+'VOCdevkit',dest_dir+'youtubebbdevkit2017'])
  check_call(['mkdir','-p',
              dest_dir+'youtubebbdevkit2017/youtubebb2017/ImageSets/Main'])
  check_call(['mkdir','-p',
              dest_dir+'youtubebbdevkit2017/youtubebb2017/JPEGImages'])
  check_call(['mkdir','-p',
              dest_dir+'youtubebbdevkit2017/youtubebb2017/Annotations'])
  check_call(['mkdir','-p',
              dest_dir+'youtubebbdevkit2017/results/youtubebb2017/Main'])

  # Decode frames for training detection
  train_frame_annots = decode_frames('yt_bb_detection_train',
    src_dir,
    dest_dir,
    num_threads,
    num_train_frames,
    max_ratio,
    include_absent)

  # Write the xml annotations for training detection
  train_xml_annots = write_xml_annots(dest_dir,train_frame_annots)

  # Decode frames for validation detection
  val_frame_annots = decode_frames('yt_bb_detection_validation',
    src_dir,
    dest_dir,
    num_threads,
    num_val_frames,
    max_ratio,
    include_absent)

  # Write the xml annotations for validation detection
  val_xml_annots = write_xml_annots(dest_dir,val_frame_annots)

  # Write txt files
  write_txt_files(dest_dir, train_xml_annots, val_xml_annots)
