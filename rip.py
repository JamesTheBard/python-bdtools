# vim:ts=4:sts=4:sw=4:et:nocp
import os
import sys
import operator
import shutil
from mako.template import Template
from error import *

class BDRip:
    '''A class dedicated to gluing all of the MeGUI tools into command-line
    goodness.
    '''
    version = "0.99.1beta"

    # Encoder defaults
    # The first entry in the 'tuning' list is considered the default.
    encoder_settings = [ 'default', 'film', 'animation', 'grain', 'psnr', 
                         'ssim', 'fast_decode' ]
    encoder_crf = 20

    # Template directory
    directory = os.path.normpath("C:/Users/JamesTheBard/Code/python-bdtools/templates")
    template = {}

    # Template defaults and filetypes
    avs_template_defs = {
        "h264": [ "h264.template", "video.dga" ],
        "vc-1": [ "vc-1.template", "video.grf" ],
        "mpeg2": [ "mpeg2.template", "video.m2v" ],
    }

    def __init__(self, drive_letter, verbose=False):
        self.is_verbose = verbose
        self.path_to_dvd = "%s:\BDMV\STREAM" % drive_letter
        self.verbosePrint( "Setting drive path to '%s'." % self.path_to_dvd )
        self.drive_letter = drive_letter
        self.current_dir = os.getcwd()
        self.encoder_tuning = self.encoder_settings[0]
        for k, v in self.avs_template_defs.items():
            self.avs_template_defs[k][0] = os.path.join( self.directory, v[0])

    def verbosePrint(self, message):
        '''Prints verbose output when self.is_verbose is True.

        Args:
            message: the message to print to the display
        '''
        if self.is_verbose:
            print "BDRip: %s" % message

    def createAvsFromTemplate(self, **kwargs):
        '''Create an Avisynth file based on the keyword arguments provided.

        Args:
            source_type: the source input type for the Avisynth script (i.e. 
                h264)
            source_file: the source input file for the Avisynth script (i.e. 
                video.h264)
            avisynth_template: the predefined template for the Avisynth file
            avisynth_file: the Avisynth script filename to save as
            crop_top: crops the top of the source (via Avisynth) by that many 
                pixels
            crop_bottom: crops the bottom of the source (via Avisynth) by that 
                many pixels
        Raises:
            SourceNotDefinedError: if source_type is not defined
            SourceNotFoundError: if source_type is a type that is not defined 
                via template
        '''

        # Ensure that there is a 'source_type' that exists with a template.
        if "source_type" not in kwargs.keys():
            raise SourceNotDefinedError( "The keyword argument 'source_type' "
                                         "is not defined." )
        if kwargs["source_type"] not in self.avs_template_defs:
            values = ", ".join(self.avs_template_defs.keys())
            raise SourceNotFoundError( 
                    "The keyword argument 'source_type' is not valid.  "
                    "Currently defined templates are: %s." % values ) 

        # Set the default values based on what the 'source_type' is.
        defaults = {
                "avisynth_file": "video.avs",
                "crop_top": "0",
                "crop_bottom": "0",
        }
        source_type = kwargs["source_type"]
        defaults["avisynth_template"] = self.avs_template_defs[source_type][0]
        defaults["source_file"] = self.avs_template_defs[source_type][1]

        # Apply the kwargs to the constructed set of defaults.
        defaults.update(kwargs)

        # Set the module Avisynth template and create the Avisynth file
        self.avs_template = defaults["avisynth_template"]
        self.verbosePrint( 
                'Avisynth set to use the "%s" source template.' % source_type )
        self._createAvsFile(
                defaults["avisynth_file"],
                defaults["source_file"], 
                defaults["crop_top"], 
                defaults["crop_bottom"], )

    def _createAvsFile(self, save_as, grf_file, crop_top=0, crop_bottom=0):
        '''Creates an Avisynth file based on the template defined as 
        self.avs_template.

        Args:
            save_as: the name of the Avisynth file to save to
            grf_file: the source file's name
            crop_top: crop the video from the top that many pixels
            crop_bottom: crop the video from the bottom that many pixels
        '''
        current_path = os.path.join(os.getcwd(), save_as)
        fullpath_grf = os.path.join(os.getcwd(), grf_file)
        self.verbosePrint( 'Creating Avisynth file: %s' % current_path )
        avs_template = self.avs_template
        template = Template(filename=avs_template)
        fd = open(save_as, "w")
        fd.write(template.render(
            directory=fullpath_grf,
            crop_top=crop_top,
            crop_bottom=crop_bottom,
        ))
        fd.close()

    def ripByRange(self, begin, end, starting_episode):
        '''Rips a range of M2TS files consecutively and associates them with
        a consecutive range of television season episodes.

        Args:
            begin: the first M2TS number (i.e. 00080.m2ts would be 80)
            end: the last M2TS number
            starting_episode: the episode number associated with the first
                M2TS file
        '''
        m2ts = range(begin, end + 1)
        self.ripByArray(m2ts_array=m2ts, starting_episode=starting_episode)

    def ripByArray(self, m2ts_array, starting_episode):
        '''Rips an ordered list of M2TS files that are in episode order.

        Args:
            m2ts_list: a list of M2TS files to be ripped (in order)
            starting_episode: the first television episode of the list
        '''
        number_of_episodes = len(m2ts_list)
        self._displayHeader(m2ts_list, starting_episode)
        for i in range(len(m2ts_list)):
            new_directory = os.path.join(
                    self.current_dir, 
                    "Episode %02i" % (starting_episode + i))
            print "BDRip: Making new directory: %s" % new_directory
            os.mkdir(new_directory)
            os.chdir(new_directory)
            self.ripM2ts(m2ts_list[i])

    def _sortTemplate(self):
        '''Sort a the self.template dictionary based on the key.'''
        return sorted(self.template.iteritems(), 
                      key=operator.itemgetter(0))

    def _displayHeader(self, m2ts_array, starting_episode):
        '''Displays the m2ts to television episode information relationship.

        Args:
            m2ts_list: a list of M2TS files to be ripped (in order)
            starting_episode: the first television episode of the list
        '''
        if not self.is_verbose:
            return
        number_of_episodes = len(m2ts_array)
        sorted_template = self._sortTemplate()
        header = [ 
            "",
            "PyRip %s Template" % self.version,
            "=" * 79,
        ]
        [header.append("%s: %s" % (k, v)) for k, v in sorted_template]
        header.append("-" * 79)
        header.append("Number of Episodes: %s" % number_of_episodes)
        temp = ", ".join(["%05i.mt2s" % m2ts for m2ts in m2ts_array])
        header.append("M2TS values: %s" % temp)
        header.append("=" * 79)
        for line in header:
            print line

    def ripM2ts(self, m2ts):
        sorted_template = self._sortTemplate()
        m2ts_file = "%05i.m2ts" % m2ts
        filename = os.path.join( self.path_to_dvd, m2ts_file )
        if not os.path.isfile( filename ):
            raise FileNotFoundError( 
                'The M2TS file "%s" does not exist or is unavailable.' 
                % filename )
        command = "eac3to %s " % (os.path.join(self.path_to_dvd, m2ts_file))
        for k, v in sorted_template:
            command += "%s:%s " % (k, v)
        self.verbosePrint( "Ripping BluRay via M2TS: '%s'." % command.strip() )
        os.system(command)

    def ripMpls(self, mpls):
        sorted_template = self._sortTemplate()
        mpls = "%s: %i) " % (self.drive_letter, mpls)
        command = "eac3to %s" % mpls
        for k, v in sorted_template:
            command += "%s:%s " % (k, v)
        self.verbosePrint( "Ripping BluRay via MPLS: '%s'" % command.strip() )
        os.system(command)

    def runDgAvcIndex(self, episodes):
        for episode in episodes:
            full_path = os.path.join(self.current_dir, "Episode %02i" % episode)
            print "Running DGAVCIndex on Episode %02i" % (episode)
            os.chdir(full_path)
            input_file = "video.h264"
            output_file = "video.dga"
            print "Input file: %s\nOutput file: %s" % (input_file, output_file)
            self.dgAvcIndexCommand(
                    input_file=input_file, 
                    output_file=output_file)

    def dgAvcIndexCommand(self, input_file, output_file):
        command = ( 'DGAVCIndex.exe -i "%s" -o "%s" -h' %
                  (input_file, output_file))
        self.verbosePrint( "DGAVCIndex is running: %s" % command )
        os.system(command)

    def dgIndexCommand(self, input_file, output_file):
        command = "DGIndex.exe -i \"%s\" -o \"%s\" -hide -exit" % (
                input_file, output_file)
        self.verbosePrint( "DGIndex is running: %s" % command )
        os.system(command)

    def createAvsFileFromEpisodes(self, episodes, grf_file="video.grf"):
        for episode in episodes:
            full_path = os.path.join(self.current_dir, "Episode %02i" % episode)
            os.chdir(full_path)
            self.createAvsFile("video.avs", grf_file)

    def muxMkvFile(self, 
            save_as="video.mkv", 
            video_file="video.mp4", video_title="None",
            audio_file="audio.dts", audio_title="None",
            chapter_file="chapters.txt", 
            default_lang="eng",
            cache_enabled=False, cache_drive_letter="H"):
        save_as = os.path.join(self.current_dir, save_as)
        video_file = os.path.join(self.current_dir, video_file)
        audio_file = os.path.join(self.current_dir, audio_file)
        chapter_file = os.path.join(self.current_dir, chapter_file)
        if cache_enabled:
            files = {
                video_file: video_file_cache,
                audio_file: audio_file_cache, 
                chapter_file: chapter_file_cache,
            }
            basepath = "%s:\\" % cache_drive_letter
            video_file_cache   = os.path.join(
                    basepath, 
                    os.path.split(video_file)[1])
            audio_file_cache   = os.path.join(
                    basepath, 
                    os.path.split(audio_file)[1])
            chapter_file_cache = os.path.join(
                    basepath, 
                    os.path.splig(chapter_file)[1])
            for src, dest in files.items():
                print "Caching '%s' in '%s'..." % (src, dest)
                shutil.copyfile(src, dest)
            video_file = video_file_cache
            audio_file = audio_file_cache
            chapter_file = chapter_file_cache
        command_template = ( 'mkvmerge.exe '
            '-o "%s" '
            '--language 0:eng --track-name "0:%s" --forced-track 0:no '
            '-d 0 -A -S -T --no-global-tags --no-chapters "(" "%s" ")" '
            '--language 0:eng --track-name "0:%s" --forced-track 0:no '
            '-a 0 -D -S -T --no-global-tags --no-chapters "(" "%s" ")" '
            '--track-order 0:0,1:0 --chapter-language eng --chapters "%s"' )
        full_command = command_template % (
            save_as, 
            video_title, 
            video_file, 
            audio_title, 
            audio_file, 
            chapter_file)
        self.verbosePrint( "Muxing video with: %s" % full_command )
        os.system(command_template % (
            save_as, 
            video_title, 
            video_file, 
            audio_title, 
            audio_file, 
            chapter_file))

    def encodeVideo(self, avs_file="video.avs", output_file="video.mp4"):
        if self.encoder_tuning != 'default':
            additional_command = "--tune %s" % self.encoder_tuning
        else:
            additional_command = ""
        command = """""C:\\Program Files (x86)\\MeGui\\tools\\x264\\x264.exe" %s --crf %2.1f --keyint 240 --sar 1:1 --output "%s" "%s\""""
        command = command % (
            additional_command, 
            self.encoder_crf, 
            output_file, 
            avs_file)
        self.verbosePrint( "Encoding video: %s" % command )
        os.system(command)

    def encodeEpisodesFromRange(self, 
                                start_episode, 
                                end_episode, 
                                avs_file, 
                                output_file):
        for episode in range(start_episode, end_episode + 1):
            base = os.path.join( self.current_dir, "Episode %02i" % episode )
            avs_file_full = os.path.join( base, avs_file )
            output_file_full = os.path.join( base, output_file )
            self.encodeVideo(avs_file_full, output_file_full)

    def setEncoderTuning(self, tuning=False):
        if not tuning:
            self.encoder_quality = self.encoder_settings[0]
        elif tuning not in self.encoder_settings:
            self.encoder_quality = self.encoder_settings[0]
        else:
            self.encoder_quality = tuning

    def setEncoderCrf(self, crf=False):
        if not crf:
            self.encoder_crf = 20
        else:
            self.encoder_crf = crf


if __name__ == "__main__":
    rip = BDRip("D")
    rip.ripByArray(m2ts_array=m2ts_files, starting_episode=16)
    rip.runDgAvcIndex(range(16,21))
    rip.avs_template = "E:\\Rips\\Grimm\\Template\\dgavcindex.avisynth.template"
    rip.createAvsFileFromEpisodes(range(16,21), grf_file="video.dga")
    rip.setEncoderTuning( tuning='default' )
    rip.setEncoderCrf( crf=19 )
    rip.encodeEpisodesFromRange(
        start_episode=16,
        end_episode=20,
        avs_file="video.avs",
        output_file="video.mp4"
    )
