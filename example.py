import os
from rip import BDRip

# Start up an instance of BDRip.  The drive_letter is which drive is the drive
# you'll be ripping from.  The verbose flag just prints more output to the
# screen (default is False).
rip = BDRip(
    drive_letter="D", 
    verbose=True,
)
current_dir = rip.current_dir

# The options for the eac3to command.
rip.template = {
	"1": "chapters.txt",
	"2": "video.h264",
	"3": "audio.dts -core",
	"6": "subtitles.01.sup",
}

# Not really ripping by MPLS, but the closest thing I could describe it as.
# The first eac3to run will tell you which one you should select.  Put that
# number in.
rip.ripMpls( 1 )

# Right now, dgAvcIndex requires full paths.  This might also be a touch of
# lazy on the part of the developer (me) of this script.  Will most likely be
# fixed in later versions.
input_file = os.path.join( rip.current_dir, "video.h264" )
output_file = os.path.join( rip.current_dir, "video.dga" )
rip.dgAvcIndexCommand( input_file, output_file )

# As long as the source_type is defined, you won't have to change anything
# other than the crop settings (as long as the defaults work for you).  Each
# source_type has a different set of defaults.
rip.createAvsFromTemplate(
    source_type="h264",
    crop_top="132",
    crop_bottom="-132",
)

# The encoder only does CRF at the moment.  It does have some predefined
# tunings that can be selected though.  The default CRF is set to 20.
rip.setEncoderCrf( crf=20 )
rip.setEncoderTuning( tuning='default' )

# Encode the video using the predefined settings
rip.encodeVideo()

# Mux the video, audio, and chapters into a MKV file
rip.muxMkvFile(
    save_as="Looper (BDRip).mkv",
    video_title="Looper",
    audio_title="DTS 5.1",
)
