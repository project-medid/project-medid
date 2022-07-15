'''
Original function taken from: https://github.com/pearcetm/svs-deidentifier with MIT License
'''
import os
import shutil
import struct
import traceback
import uuid

import tifffile


# Read/modify TIFF files (as in the SVS files) using tiffparser library (stripped down tifffile lib)

# delete_associated_image will remove a label or macro image from an SVS file
def delete_associated_image(slide_path, image_type):
    # THIS WILL ONLY WORK FOR STRIPED IMAGES CURRENTLY, NOT TILED

    allowed_image_types = ['label', 'macro'];
    if image_type not in allowed_image_types:
        raise Exception('Invalid image type requested for deletion')

    fp = open(slide_path, 'r+b')
    t = tifffile.TiffFile(fp)

    # logic here will depend on file type. AT2 and older SVS files have "label" and "macro"
    # strings in the page descriptions, which identifies the relevant pages to modify.
    # in contrast, the GT450 scanner creates svs files which do not have this, but the label
    # and macro images are always the last two pages and are striped, not tiled.
    # The header of the first page will contain a description that indicates which file type it is
    first_page = t.pages[0]
    filtered_pages = []
    if 'Aperio Image Library' in first_page.description:
        filtered_pages = [page for page in t.pages if image_type in page.description]
    elif 'Aperio Leica Biosystems GT450' in first_page.description:
        if image_type == 'label':
            filtered_pages = [t.pages[-2]]
        else:
            filtered_pages = [t.pages[-1]]
    else:
        # default to old-style labeled pages
        filtered_pages = [page for page in t.pages if image_type in page.description]

    num_results = len(filtered_pages)
    if num_results > 1:
        raise Exception(f'Invalid SVS format: duplicate associated {image_type} images found')
    if num_results == 0:
        # No image of this type in the WSI file; no need to delete it
        return

    # At this point, exactly 1 image has been identified to remove
    page = filtered_pages[0]

    # get the list of IFDs for the various pages
    offsetformat = t.tiff.offsetformat
    offsetsize = t.tiff.offsetsize
    tagnoformat = t.tiff.tagnoformat
    tagnosize = t.tiff.tagnosize
    tagsize = t.tiff.tagsize
    unpack = struct.unpack

    # start by saving this page's IFD offset
    ifds = [{'this': p.offset} for p in t.pages]
    # now add the next page's location and offset to that pointer
    for p in ifds:
        # move to the start of this page
        fp.seek(p['this'])
        # read the number of tags in this page
        (num_tags,) = unpack(tagnoformat, fp.read(tagnosize))

        # move forward past the tag defintions
        fp.seek(num_tags * tagsize, 1)
        # add the current location as the offset to the IFD of the next page
        p['next_ifd_offset'] = fp.tell()
        # read and save the value of the offset to the next page
        (p['next_ifd_value'],) = unpack(offsetformat, fp.read(offsetsize))

    # filter out the entry corresponding to the desired page to remove
    pageifd = [i for i in ifds if i['this'] == page.offset][0]
    # find the page pointing to this one in the IFD list
    previfd = [i for i in ifds if i['next_ifd_value'] == page.offset]
    # check for errors
    if len(previfd) == 0:
        raise Exception('No page points to this one')
        return
    else:
        previfd = previfd[0]

    # get the strip offsets and byte counts
    offsets = page.tags['StripOffsets'].value
    bytecounts = page.tags['StripByteCounts'].value

    # iterate over the strips and erase the data
    # print('Deleting pixel data from image strips')
    for (o, b) in zip(offsets, bytecounts):
        fp.seek(o)
        fp.write(b'\0' * b)

    # iterate over all tags and erase values if necessary
    # print('Deleting tag values')
    for key, tag in page.tags.items():
        fp.seek(tag.valueoffset)
        fp.write(b'\0' * tag.count)

    offsetsize = t.tiff.offsetsize
    offsetformat = t.tiff.offsetformat
    pagebytes = (pageifd['next_ifd_offset'] - pageifd['this']) + offsetsize

    # next, zero out the data in this page's header
    # print('Deleting page header')
    fp.seek(pageifd['this'])
    fp.write(b'\0' * pagebytes)

    # finally, point the previous page's IFD to this one's IFD instead
    # this will make it not show up the next time the file is opened
    fp.seek(previfd['next_ifd_offset'])
    fp.write(struct.pack(offsetformat, pageifd['next_ifd_value']))

    fp.close()


def deident_svs_file(original_file_path, deident_file_path):
    try:
        dst_path = os.path.dirname(deident_file_path)
        tmp_file = os.path.join(dst_path, str(uuid.uuid1()))
        # create a tmp file to strip information
        shutil.copyfile(original_file_path, tmp_file)

        delete_associated_image(tmp_file, 'label')
        delete_associated_image(tmp_file, 'macro')

        shutil.move(tmp_file, deident_file_path)
        return True
    except:
        traceback.print_exc()
        return False
