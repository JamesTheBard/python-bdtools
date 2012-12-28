# vim:ts=4:et:nocp
import os
import sys
import operator
import shutil
from mako.template import Template

class Eac3toRip:

    template = {}
    version = "0.99.1beta"
    encoder_settings = { 
        "tuning": [ 'default', 'film', 'animation', 'grain', 'psnr', 'ssim', 'fast_decode' ],
    }
    encoder_crf = 20

    def __init__(self, drive_letter):
        self.path_to_dvd = "%s:\BDMV\STREAM" % drive_letter
        self.drive_letter = drive_letter
        self.current_dir = os.getcwd()
        self.encoder_tuning = self.encoder_settings['tuning'][0]

    def ripByRange(self, begin, end, starting_episode):
        m2ts = range(begin, end + 1)
        self.ripByArray(m2ts_array=m2ts, starting_episode=starting_episode)

    def ripByArray(self, m2ts_array, starting_episode):
        number_of_episodes = len(m2ts_array)
        self.displayHeader(m2ts_array, starting_episode)
        for i in range(len(m2ts_array)):
            new_directory = os.path.join(self.current_dir, "Episode %02i" % (starting_episode + i))
            print "PyRip: Making new directory: %s" % new_directory
            os.mkdir(new_directory)
            os.chdir(new_directory)
            self.ripM2ts(m2ts_array[i])

    def sortTemplate(self):
            return sorted(self.template.iteritems(), key=operator.itemgetter(0))


    def displayHeader(self, m2ts_array, starting_episode):
        number_of_episodes = len(m2ts_array)
        sorted_template = self.sortTemplate()
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
        sorted_template = self.sortTemplate()
        if len(self.template) == 0:
            print "ERROR: No template defined, exiting."
            sys.exit(1)
        m2ts_file = "%05i.m2ts" % m2ts
        command = "eac3to %s " % (os.path.join(self.path_to_dvd, m2ts_file))
        for k, v in sorted_template:
            command += "%s:%s " % (k, v)
        print "PyRip: '%s'" % command.strip()
        os.system(command)

    def ripMpls(self, mpls):
        sorted_template = self.sortTemplate()
        if len(self.template) == 0:
            print "ERROR: No template defined, exiting."
            sys.exit(1)
        mpls = "%s: %i) " % (self.drive_letter, mpls)
        command = "eac3to %s" % mpls
        for k, v in sorted_template:
            command += "%s:%s " % (k, v)
        print "PyRip: '%s'" % command.strip()
        os.system(command)

    def runDgAvcIndex(self, episodes):
        for episode in episodes:
            full_path = os.path.join(self.current_dir, "Episode %02i" % episode)
            print "Running DGAVCIndex on Episode %02i" % (episode)
            os.chdir(full_path)
            input_file = "video.h264"
            output_file = "video.dga"
            print "Input file: %s\nOutput file: %s" % (input_file, output_file)
            self.dgAvcIndexCommand(input_file=input_file, output_file=output_file)

    def dgAvcIndexCommand(self, input_file, output_file):
        command = "DGAVCIndex.exe -i \"%s\" -o \"%s\" -h" % (input_file, output_file)
        print "DGAVCIndex: %s" % command
        os.system(command)

    def createAvsFileFromEpisodes(self, episodes, grf_file="video.grf"):
        for episode in episodes:
            full_path = os.path.join(self.current_dir, "Episode %02i" % episode)
            os.chdir(full_path)
            self.createAvsFile("video.avs", grf_file)

    def createAvsFile(self, save_as, grf_file):
        current_path = os.path.join(os.getcwd(),save_as)
        fullpath_grf = os.path.join(os.getcwd(),grf_file)
        print "Creating: %s" % current_path
        avs_template = self.avs_template
        template = Template(filename=avs_template)
        fd = open(save_as, "w")
        fd.write(template.render(directory=fullpath_grf))
        fd.close()

    def muxMkvFile(self, 
            save_as="video.mkv", 
            video_file="video.mp4", video_title="None",
            audio_file="audio.dts", audio_title="None",
            chapter_file="chapters.txt", 
            default_lang="eng",
            cache_enabled=False, cache_drive_letter="H"):
        save_as = os.path.join(self.current_path)
        if cache_enabled:
            files = {
                video_file: video_file_cache,
                audio_file: audio_file_cache, 
                chapter_file: chapter_file_cache,
            }
            basepath = "%s:\\" % cache_drive_letter
            video_file_cache   = os.path.join(basepath, os.path.split(video_file)[1])
            audio_file_cache   = os.path.join(basepath, os.path.split(audio_file)[1])
            chapter_file_cache = os.path.join(basepath, os.path.splig(chapter_file)[1])
            for src, dest in files.items():
                print "Caching '%s' in '%s'..." % (src, dest)
                shutil.copyfile(src, dest)
            video_file = video_file_cache
            audio_file = audio_file_cache
            chapter_file = chapter_file_cache
        command_template = "C:\Program Files (x86)\MKVToolNix\mkvmerge.exe " \
            "-o \"%s\" " \
            "--language 0:eng \"--track-name 0:%s\" --forced-track 0:no -d 0 -A -S -T --no-global-tags --no-chapters (%s) " \
            "--language 0:eng \"--track-name 0:%s\" --forced-track            0:no -a 0 -D -S -T --no-global-tags --no-chapters (%s) " \
            "--track-order 0:0,1:0 --chapter-language eng --chapters %s"
        os.system(command_template % (save_as, video_title, video_file, audio_title, audio_file, chapters_file))

    def encodeVideo(self, avs_file="video.avs", output_file="video.mp4"):
        if self.encoder_tuning != 'default':
            additional_command = "--tune %s" % self.encoder_tuning
        else:
            additional_command = ""
        command = """""C:\\Program Files (x86)\\MeGui\\tools\\x264\\x264.exe" %s --crf %2.1f --keyint 240 --sar 1:1 --output "%s" "%s\""""
        command = command % (additional_command, self.encoder_crf, output_file, avs_file)
        print "Encoding video: %s" % command
        os.system(command)

    def encodeEpisodesFromRange(self, start_episode, end_episode, avs_file, output_file):
        for episode in range(start_episode, end_episode + 1):
            base = os.path.join( self.current_dir, "Episode %02i" % episode )
            avs_file_full = os.path.join( base, avs_file )
            output_file_full = os.path.join( base, output_file )
            self.encodeVideo(avs_file_full, output_file_full)

    def setEncoderQuality(self, quality=False):
        if not quality:
            self.encoder_quality = self.encoder_settings["tuning"][0]
        elif quality not in self.encoder_settings["tuning"]:
            self.encoder_quality = self.encoder_settings["tuning"][0]
        else:
            self.encoder_quality = quality

    def setEncoderCrf(self, crf=False):
        if not crf:
            self.encoder_crf = 20
        else:
            self.encoder_crf = crf

if __name__ == "__main__":
    rip = Eac3toRip("D")
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
