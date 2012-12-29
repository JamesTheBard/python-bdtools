import os
from rip import BDRip

rip = BDRip("D")
current_dir = rip.current_dir
rip.template = {
	"1": "chapters.txt",
	"2": "video.h264",
	"3": "audio.dts -core",
	"9": "subtitles.01.sup",
}
rip.ripMpls( 1 )
input_file = os.path.join( rip.current_dir, "video.h264" )
output_file = os.path.join( rip.current_dir, "video.dga" )
rip.dgAvcIndexCommand( input_file, output_file ) 
rip.createAvsFromTemplate( "h264", "video.avs", "video.dga", "130", "-130" )
rip.setEncoderQuality( quality='default' )
rip.encodeVideo()
rip.muxMkvFile(
    save_as="Dodgeball (BDRip).mkv",
    video_title="Dodgeball",
    audio_title="DTS 5.1",
)
