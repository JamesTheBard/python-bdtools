import os
from rip import Eac3toRip

rip = Eac3toRip("D")
current_dir = rip.current_dir
rip.template = {
	"1": "chapters.txt",
	"2": "video.h264",
	"3": "audio.dts -core",
	"8": "subtitles.01.sup",
}
# rip.ripMpls( 2 )
input_file = os.path.join( rip.current_dir, "video.h264" )
output_file = os.path.join( rip.current_dir, "video.dga" )
rip.dgAvcIndexCommand( input_file, output_file )
rip.avs_template = os.path.join( current_dir, "dgavcindex.avisynth.template" )
rip.createAvsFile( "video.avs", "video.dga" )
rip.setEncoderQuality( quality='default' )
rip.encodeVideo()
