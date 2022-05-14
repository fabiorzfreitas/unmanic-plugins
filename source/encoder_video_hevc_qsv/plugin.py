#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    plugins.plugin.py

    Written by:               Josh.5 <jsunnex@gmail.com>
    Date:                     17 Nov 2021, (6:08 PM)

    Copyright:
        Copyright (C) 2021 Josh Sunnex

        This program is free software: you can redistribute it and/or modify it under the terms of the GNU General
        Public License as published by the Free Software Foundation, version 3.

        This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
        implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
        for more details.

        You should have received a copy of the GNU General Public License along with this program.
        If not, see <https://www.gnu.org/licenses/>.

"""
import logging
import os

from unmanic.libs.unplugins.settings import PluginSettings

from encoder_video_hevc_qsv.lib.ffmpeg import StreamMapper, Probe, Parser

# Configure plugin logger
logger = logging.getLogger("Unmanic.Plugin.encoder_video_hevc_qsv")


class Settings(PluginSettings):
    settings = {
        "advanced":                   False,
        "max_muxing_queue_size":      2048,
        "preset":                     "slow",
        "tune":                       "film",
        "encoder_ratecontrol_method": "LA_ICQ",
        "constant_quantizer_scale":   "25",
        "constant_quality_scale":     "23",
        "average_bitrate":            "5",
        "main_options":               "",
        "advanced_options":           "-strict -2\n"
                                      "-max_muxing_queue_size 2048\n",
        "custom_options":             "-preset slow\n"
                                      "-tune film\n"
                                      "-global_quality 23\n"
                                      "-look_ahead 1\n",
        "keep_container":             True,
        "dest_container":             "mkv",
    }

    def __init__(self, *args, **kwargs):
        super(Settings, self).__init__(*args, **kwargs)
        self.form_settings = {
            "advanced":                   {
                "label": "Write your own FFmpeg params",
            },
            "max_muxing_queue_size":      self.__set_max_muxing_queue_size_form_settings(),
            "preset":                     self.__set_preset_form_settings(),
            "tune":                       self.__set_tune_form_settings(),
            "encoder_ratecontrol_method": self.__set_encoder_ratecontrol_method_form_settings(),
            "constant_quantizer_scale":   self.__set_constant_quantizer_scale_form_settings(),
            "constant_quality_scale":     self.__set_constant_quality_scale_form_settings(),
            "average_bitrate":            self.__set_average_bitrate_form_settings(),
            "main_options":               self.__set_main_options_form_settings(),
            "advanced_options":           self.__set_advanced_options_form_settings(),
            "custom_options":             self.__set_custom_options_form_settings(),
            "keep_container":             {
                "label": "Keep the same container",
            },
            "dest_container":             self.__set_destination_container(),
        }

    def __set_max_muxing_queue_size_form_settings(self):
        values = {
            "label":          "Max input stream packet buffer",
            "input_type":     "slider",
            "slider_options": {
                "min": 1024,
                "max": 10240,
            },
        }
        if self.get_setting('advanced'):
            values["display"] = 'hidden'
        return values

    def __set_preset_form_settings(self):
        values = {
            "label":          "Encoder quality preset",
            "input_type":     "select",
            "select_options": [
                {
                    'value': "veryfast",
                    'label': "Very fast - Fastest setting, biggest quality drop",
                },
                {
                    'value': "faster",
                    'label': "Faster - Close to medium/fast quality, faster performance",
                },
                {
                    'value': "fast",
                    'label': "Fast",
                },
                {
                    'value': "medium",
                    'label': "Medium - Balanced performance and quality",
                },
                {
                    'value': "slow",
                    'label': "Slow",
                },
                {
                    'value': "slower",
                    'label': "Slower - Close to 'very slow' quality, faster performance",
                },
                {
                    'value': "veryslow",
                    'label': "Very Slow - Best quality",
                },
            ],
        }
        if self.get_setting('advanced'):
            values["display"] = 'hidden'
        return values

    def __set_tune_form_settings(self):
        values = {
            "label":          "Tune for a particular type of source or situation",
            "input_type":     "select",
            "select_options": [
                {
                    'value': "film",
                    'label': "Film – use for high quality movie content; lowers deblocking",
                },
                {
                    'value': "animation",
                    'label': "Animation – good for cartoons; uses higher deblocking and more reference frames",
                },
                {
                    'value': "grain",
                    'label': "Grain – preserves the grain structure in old, grainy film material",
                },
                {
                    'value': "stillimage",
                    'label': "Still image – good for slideshow-like content",
                },
                {
                    'value': "fastdecode",
                    'label': "Fast decode – allows faster decoding by disabling certain filters",
                },
                {
                    'value': "zerolatency",
                    'label': "Zero latency – good for fast encoding and low-latency streaming",
                },
            ],
        }
        if self.get_setting('advanced'):
            values["display"] = 'hidden'
        return values

    def __set_encoder_ratecontrol_method_form_settings(self):
        values = {
            "label":          "Encoder ratecontrol method",
            "input_type":     "select",
            "select_options": [
                {
                    'value': "CQP",
                    'label': "CQP - Quality based mode using constant quantizer scale",
                },
                {
                    'value': "ICQ",
                    'label': "ICQ - Quality based mode using intelligent constant quality",
                },
                {
                    'value': "LA_ICQ",
                    'label': "LA_ICQ - Quality based mode using intelligent constant quality with lookahead",
                },
                {
                    'value': "VBR",
                    'label': "VBR - Bitrate based mode using variable bitrate",
                },
                {
                    'value': "LA",
                    'label': "LA - Bitrate based mode using VBR with lookahead",
                },
                {
                    'value': "CBR",
                    'label': "CBR - Bitrate based mode using constant bitrate",
                },
            ],
        }
        if self.get_setting('advanced'):
            values["display"] = 'hidden'
        return values

    def __set_constant_quantizer_scale_form_settings(self):
        # Lower is better
        values = {
            "label":          "Constant quantizer scale",
            "input_type":     "slider",
            "slider_options": {
                "min": 0,
                "max": 51,
            },
        }
        if self.get_setting('advanced'):
            values["display"] = 'hidden'
        if self.get_setting('encoder_ratecontrol_method') != 'CQP':
            values["display"] = 'hidden'
        return values

    def __set_constant_quality_scale_form_settings(self):
        # Lower is better
        values = {
            "label":          "Constant quality scale",
            "input_type":     "slider",
            "slider_options": {
                "min": 1,
                "max": 51,
            },
        }
        if self.get_setting('advanced'):
            values["display"] = 'hidden'
        if self.get_setting('encoder_ratecontrol_method') not in ['LA_ICQ', 'ICQ']:
            values["display"] = 'hidden'
        return values

    def __set_average_bitrate_form_settings(self):
        values = {
            "label":          "Bitrate",
            "input_type":     "slider",
            "slider_options": {
                "min":    1,
                "max":    20,
                "suffix": "M"
            },
        }
        if self.get_setting('advanced'):
            values["display"] = 'hidden'
        if self.get_setting('encoder_ratecontrol_method') not in ['VBR', 'LA', 'CBR']:
            values["display"] = 'hidden'
        return values

    def __set_main_options_form_settings(self):
        values = {
            "label":      "Write your own custom main options",
            "input_type": "textarea",
        }
        if not self.get_setting('advanced'):
            values["display"] = 'hidden'
        return values

    def __set_advanced_options_form_settings(self):
        values = {
            "label":      "Write your own custom advanced options",
            "input_type": "textarea",
        }
        if not self.get_setting('advanced'):
            values["display"] = 'hidden'
        return values

    def __set_custom_options_form_settings(self):
        values = {
            "label":      "Write your own custom video options",
            "input_type": "textarea",
        }
        if not self.get_setting('advanced'):
            values["display"] = 'hidden'
        return values

    def __set_destination_container(self):
        values = {
            "label":          "Set the output container",
            "input_type":     "select",
            "select_options": [
                {
                    'value': "mkv",
                    'label': ".mkv - Matroska",
                },
                {
                    'value': "avi",
                    'label': ".avi - AVI (Audio Video Interleaved)",
                },
                {
                    'value': "mp4",
                    'label': ".mp4 - MP4 (MPEG-4 Part 14)",
                },
            ],
        }
        if self.get_setting('keep_container'):
            values["display"] = 'hidden'
        return values


class PluginStreamMapper(StreamMapper):
    image_video_codecs = [
        'alias_pix',
        'apng',
        'brender_pix',
        'dds',
        'dpx',
        'exr',
        'fits',
        'gif',
        'mjpeg',
        'mjpegb',
        'pam',
        'pbm',
        'pcx',
        'pfm',
        'pgm',
        'pgmyuv',
        'pgx',
        'photocd',
        'pictor',
        'pixlet',
        'png',
        'ppm',
        'ptx',
        'sgi',
        'sunrast',
        'tiff',
        'vc1image',
        'wmv3image',
        'xbm',
        'xface',
        'xpm',
        'xwd',
    ]

    def __init__(self):
        super(PluginStreamMapper, self).__init__(logger, ['video'])
        self.settings = None

    def set_settings(self, settings):
        self.settings = settings

    def test_stream_needs_processing(self, stream_info: dict):
        if stream_info.get('codec_name').lower() in self.image_video_codecs:
            return False
        elif stream_info.get('codec_name').lower() in ['h265', 'hevc']:
            return False
        return True

    def custom_stream_mapping(self, stream_info: dict, stream_id: int):
        if self.settings.get_setting('advanced'):
            stream_encoding = ['-c:v:{}'.format(stream_id), 'hevc_qsv']
            stream_encoding += self.settings.get_setting('custom_options').split()
        else:
            stream_encoding = [
                '-c:v:{}'.format(stream_id), 'hevc_qsv',
            ]

            # Add the preset and tune
            stream_encoding += [
                '-preset', str(self.settings.get_setting('preset')),
                '-tune', str(self.settings.get_setting('tune')),
            ]

            if self.settings.get_setting('encoder_ratecontrol_method') in ['CQP', 'LA_ICQ', 'ICQ']:
                # Configure QSV encoder with a quality-based mode
                if self.settings.get_setting('encoder_ratecontrol_method') == 'CQP':
                    # Set values for constant quantizer scale
                    stream_encoding += [
                        '-q', str(self.settings.get_setting('constant_quantizer_scale')),
                    ]
                elif self.settings.get_setting('encoder_ratecontrol_method') in ['LA_ICQ', 'ICQ']:
                    # Set the global quality
                    stream_encoding += [
                        '-global_quality', str(self.settings.get_setting('constant_quality_scale')),
                    ]
                    # Set values for constant quality scale
                    if self.settings.get_setting('encoder_ratecontrol_method') == 'LA_ICQ':
                        # Add lookahead
                        stream_encoding += [
                            '-look_ahead', '1',
                        ]
            else:
                # Configure the QSV encoder with a bitrate-based mode
                # Set the max and average bitrate (used by all bitrate-based modes)
                stream_encoding += [
                    '-b:v:{}'.format(stream_id), '{}M'.format(self.settings.get_setting('average_bitrate')),
                ]
                if self.settings.get_setting('encoder_ratecontrol_method') == 'LA':
                    # Add lookahead
                    stream_encoding += [
                        '-look_ahead', '1',
                    ]
                elif self.settings.get_setting('encoder_ratecontrol_method') == 'CBR':
                    # Add 'maxrate' with the same value to make CBR mode
                    stream_encoding += [
                        '-maxrate', '{}M'.format(self.settings.get_setting('average_bitrate')),
                    ]

        return {
            'stream_mapping':  ['-map', '0:v:{}'.format(stream_id)],
            'stream_encoding': stream_encoding,
        }

    def generate_default_qsv_args(self):
        """
        Generate a list of args for using a QSV decoder
        :return:
        """
        # Encode only (no decoding)
        #   REF: https://trac.ffmpeg.org/wiki/Hardware/QuickSync#Transcode
        generic_kwargs = {
            "-init_hw_device":   "qsv=hw",
            "-filter_hw_device": "hw",
        }
        self.set_ffmpeg_generic_options(**generic_kwargs)
        advanced_kwargs = {
            "-vf": "hwupload=extra_hw_frames=64,format=qsv",
        }
        self.set_ffmpeg_advanced_options(**advanced_kwargs)


def on_library_management_file_test(data):
    """
    Runner function - enables additional actions during the library management file tests.

    The 'data' object argument includes:
        library_id                      - The library that the current task is associated with
        path                            - String containing the full path to the file being tested.
        issues                          - List of currently found issues for not processing the file.
        add_file_to_pending_tasks       - Boolean, is the file currently marked to be added to the queue for processing.
        priority_score                  - Integer, an additional score that can be added to set the position of the new task in the task queue.
        shared_info                     - Dictionary, information provided by previous plugin runners. This can be appended to for subsequent runners.

    :param data:
    :return:

    """
    # Get the path to the file
    abspath = data.get('path')

    # Get file probe
    probe = Probe.init_probe(data, logger)
    if not probe.file(abspath):
        # File probe failed, skip the rest of this test
        return data

    # Configure settings object (maintain compatibility with v1 plugins)
    if data.get('library_id'):
        settings = Settings(library_id=data.get('library_id'))
    else:
        settings = Settings()

    # Get stream mapper
    mapper = PluginStreamMapper()
    mapper.set_settings(settings)
    mapper.set_probe(probe)

    if mapper.streams_need_processing():
        # Mark this file to be added to the pending tasks
        data['add_file_to_pending_tasks'] = True
        logger.debug("File '{}' should be added to task list. Probe found streams require processing.".format(abspath))
    else:
        logger.debug("File '{}' does not contain streams require processing.".format(abspath))

    return data


def on_worker_process(data):
    """
    Runner function - enables additional configured processing jobs during the worker stages of a task.

    The 'data' object argument includes:
        exec_command            - A command that Unmanic should execute. Can be empty.
        command_progress_parser - A function that Unmanic can use to parse the STDOUT of the command to collect progress stats. Can be empty.
        file_in                 - The source file to be processed by the command.
        file_out                - The destination that the command should output (may be the same as the file_in if necessary).
        original_file_path      - The absolute path to the original file.
        repeat                  - Boolean, should this runner be executed again once completed with the same variables.

    :param data:
    :return:

    """
    # Default to no FFMPEG command required. This prevents the FFMPEG command from running if it is not required
    data['exec_command'] = []
    data['repeat'] = False

    # Get the path to the file
    abspath = data.get('file_in')

    # Get file probe
    probe = Probe(logger, allowed_mimetypes=['video'])
    if not probe.file(abspath):
        # File probe failed, skip the rest of this test
        return data

    # Configure settings object (maintain compatibility with v1 plugins)
    if data.get('library_id'):
        settings = Settings(library_id=data.get('library_id'))
    else:
        settings = Settings()

    # Get stream mapper
    mapper = PluginStreamMapper()
    mapper.set_settings(settings)
    mapper.set_probe(probe)

    if mapper.streams_need_processing():
        # Set the input file
        mapper.set_input_file(abspath)

        # Set the output file
        if settings.get_setting('keep_container'):
            # Do not remux the file. Keep the file out in the same container
            mapper.set_output_file(data.get('file_out'))
        else:
            # Force the remux to the configured container
            container_extension = settings.get_setting('dest_container')
            split_file_out = os.path.splitext(data.get('file_out'))
            new_file_out = "{}.{}".format(split_file_out[0], container_extension.lstrip('.'))
            mapper.set_output_file(new_file_out)
            data['file_out'] = new_file_out

        # Setup required HW acceleration args
        mapper.generate_default_qsv_args()

        # Setup the advanced settings (this will overwrite a lot of other settings)
        if settings.get_setting('advanced'):

            # If any main options are provided, overwrite them
            main_options = settings.get_setting('main_options').split()
            if main_options:
                # Overwrite all main options
                mapper.main_options = main_options

            advanced_options = settings.get_setting('advanced_options').split()
            if advanced_options:
                # Overwrite all advanced options
                mapper.advanced_options = advanced_options

        else:
            advanced_kwargs = {
                '-max_muxing_queue_size': str(settings.get_setting('max_muxing_queue_size'))
            }
            mapper.set_ffmpeg_advanced_options(**advanced_kwargs)

        # Get generated ffmpeg args
        ffmpeg_args = mapper.get_ffmpeg_args()

        # Apply ffmpeg args to command
        data['exec_command'] = ['ffmpeg']
        data['exec_command'] += ffmpeg_args

        # Set the parser
        parser = Parser(logger)
        parser.set_probe(probe)
        data['command_progress_parser'] = parser.parse_progress

    return data
