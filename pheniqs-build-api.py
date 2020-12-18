#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Pheniqs : PHilology ENcoder wIth Quality Statistics
# Copyright (C) 2020  Lior Galanti
# NYU Center for Genetics and System Biology

# Author: Lior Galanti <lior.galanti@nyu.edu>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import io
import os
import sys
import json
import signal
import logging
import hashlib
import platform
from copy import deepcopy
from datetime import datetime, date
from subprocess import Popen, PIPE
from argparse import ArgumentParser
import urllib.request, urllib.parse, urllib.error
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from http.client import BadStatusLine

log_levels = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}
interface_configuration = {
    "interface": {
        "argument": [
            "version",
            "verbosity"
        ],
        "instruction": {
            "description": "Lior Galanti lior.galanti@nyu.edu NYU Center for Genomics & Systems Biology"
        },
        "prototype": {
            "path": {
                "flag": [
                    "--config"
                ],
                "parameter": {
                    "help": "path",
                    "metavar": "PATH"
                }
            },
            "preset": {
                "flag": [
                    "-p",
                    "--preset"
                ],
                "parameter": {
                    "choices": [
                        "dynamic",
                        "static",
                        "gencore"
                    ],
                    "default": "static",
                    "dest": "preset",
                    "help": "build preset",
                    "metavar": "PRESET"
                }
            },
            "revision": {
                "flag": [
                    "-R",
                    "--revision"
                ],
                "parameter": {
                    "dest": "revision",
                    "help": "git revision",
                    "metavar": "REVISION"
                }
            },
            "verbosity": {
                "flag": [
                    "-v",
                    "--verbosity"
                ],
                "parameter": {
                    "choices": [
                        "debug",
                        "info",
                        "warning",
                        "error",
                        "critical"
                    ],
                    "dest": "verbosity",
                    "help": "logging verbosity level",
                    "metavar": "LEVEL"
                }
            },
            "version": {
                "flag": [
                    "--version"
                ],
                "parameter": {
                    "action": "version",
                    "version": "%[prog]s 1.0"
                }
            }
        },
        "section": {
            "action": [
                {
                    "argument": [
                        "path",
                        "preset"
                    ],
                    "implementation": "clean",
                    "instruction": {
                        "help": "clean build root environment",
                        "name": "clean"
                    }
                },
                {
                    "argument": [
                        "path",
                        "preset",
                        "revision"
                    ],
                    "implementation": "build",
                    "instruction": {
                        "help": "build build root environment",
                        "name": "build"
                    }
                }
            ],
            "instruction": {
                "description": "",
                "dest": "action",
                "help": None,
                "metavar": "ACTION",
                "title": "pipeline operations"
            }
        }
    },
    "package implementation": {
        "bcl2fastq": {
            "job implementation": "pheniqs-build-api.Bcl2Fastq"
        },
        "bz2": {
            "job implementation": "pheniqs-build-api.BZip2"
        },
        "htslib": {
            "job implementation": "pheniqs-build-api.Make"
        },
        "libdeflate": {
            "job implementation": "pheniqs-build-api.LibDeflate"
        },
        "pheniqs": {
            "job implementation": "pheniqs-build-api.Make"
        },
        "rapidjson": {
            "job implementation": "pheniqs-build-api.RapidJSON"
        },
        "samtools": {
            "job implementation": "pheniqs-build-api.SAMTools"
        },
        "xz": {
            "job implementation": "pheniqs-build-api.Make"
        },
        "zlib": {
            "job implementation": "pheniqs-build-api.Make"
        }
    },
    "pheniqs code url prefix": "https://codeload.github.com/biosails/pheniqs",
    "preset": {
        "dynamic": {
            "home": "bin",
            "package": [
                {
                    "make clean target": "distclean",
                    "name": "zlib",
                    "remote url": [
                        "https://zlib.net/zlib-1.2.11.tar.gz"
                    ],
                    "sha1": "e6d119755acdf9104d7ba236b1242696940ed6dd"
                },
                {
                    "include prefix in make": True,
                    "name": "bz2",
                    "remote url": [
                        "https://sourceware.org/pub/bzip2/bzip2-1.0.8.tar.gz"
                    ],
                    "sha1": "bf7badf7e248e0ecf465d33c2f5aeec774209227",
                    "version": "1.0.8"
                },
                {
                    "name": "xz",
                    "remote url": [
                        "https://downloads.sourceforge.net/project/lzmautils/xz-5.2.5.tar.bz2",
                        "https://tukaani.org/xz/xz-5.2.5.tar.bz2"
                    ],
                    "sha1": "19f83fb33dc51df87169864decd4b3de75dee1df"
                },
                {
                    "make build optional": [
                        "CC=gcc"
                    ],
                    "name": "libdeflate",
                    "remote filename": "libdeflate-1.6.tar.gz",
                    "remote url": [
                        "https://github.com/ebiggers/libdeflate/archive/v1.6.tar.gz"
                    ],
                    "sha1": "5f45e7e81e06c5cc4b6fe208bbf84cd07bb77088",
                    "version": "1.6"
                },
                {
                    "name": "htslib",
                    "remote url": [
                        "https://github.com/samtools/htslib/releases/download/1.11/htslib-1.11.tar.bz2"
                    ],
                    "sha1": "815b8268bfd6526c2d5fc639f5e6f7ed264dcbf7"
                },
                {
                    "name": "rapidjson",
                    "remote filename": "rapidjson-1.1.0.tar.gz",
                    "remote url": "https://github.com/miloyip/rapidjson/archive/v1.1.0.tar.gz",
                    "sha1": "a3e0d043ad3c2d7638ffefa3beb30a77c71c869f",
                    "version": "1.1.0"
                },
                {
                    "include prefix in make": True,
                    "make build optional": [
                        "PHENIQS_ZLIB_VERSION=1.2.11",
                        "PHENIQS_BZIP2_VERSION=1.0.8",
                        "PHENIQS_XZ_VERSION=5.2.5",
                        "PHENIQS_LIBDEFLATE_VERSION=1.6",
                        "PHENIQS_HTSLIB_VERSION=1.10.2",
                        "PHENIQS_RAPIDJSON_VERSION=1.1.0"
                    ],
                    "name": "pheniqs",
                    "remote filename": "pheniqs-HEAD.zip",
                    "remote url": "https://codeload.github.com/biosails/pheniqs/zip/HEAD",
                    "version": "2.0-trunk"
                }
            ]
        },
        "static": {
            "home": "bin",
            "package": [
                {
                    "make clean target": "distclean",
                    "name": "zlib",
                    "remote url": [
                        "https://zlib.net/zlib-1.2.11.tar.gz"
                    ],
                    "sha1": "e6d119755acdf9104d7ba236b1242696940ed6dd"
                },
                {
                    "include prefix in make": True,
                    "name": "bz2",
                    "remote url": [
                        "https://sourceware.org/pub/bzip2/bzip2-1.0.8.tar.gz"
                    ],
                    "sha1": "bf7badf7e248e0ecf465d33c2f5aeec774209227",
                    "version": "1.0.8"
                },
                {
                    "configure optional": [
                        "--enable-static"
                    ],
                    "name": "xz",
                    "remote url": [
                        "https://downloads.sourceforge.net/project/lzmautils/xz-5.2.5.tar.bz2",
                        "https://tukaani.org/xz/xz-5.2.5.tar.bz2"
                    ],
                    "sha1": "19f83fb33dc51df87169864decd4b3de75dee1df"
                },
                {
                    "make build optional": [
                        "CC=gcc"
                    ],
                    "name": "libdeflate",
                    "remote filename": "libdeflate-1.6.tar.gz",
                    "remote url": [
                        "https://github.com/ebiggers/libdeflate/archive/v1.6.tar.gz"
                    ],
                    "sha1": "5f45e7e81e06c5cc4b6fe208bbf84cd07bb77088",
                    "version": "1.6"
                },
                {
                    "configure optional": [
                        "--disable-libcurl"
                    ],
                    "name": "htslib",
                    "remote url": [
                        "https://github.com/samtools/htslib/releases/download/1.11/htslib-1.11.tar.bz2"
                    ],
                    "sha1": "815b8268bfd6526c2d5fc639f5e6f7ed264dcbf7"
                },
                {
                    "name": "rapidjson",
                    "remote filename": "rapidjson-1.1.0.tar.gz",
                    "remote url": [
                        "https://github.com/miloyip/rapidjson/archive/v1.1.0.tar.gz"
                    ],
                    "sha1": "a3e0d043ad3c2d7638ffefa3beb30a77c71c869f",
                    "version": "1.1.0"
                },
                {
                    "include prefix in make": True,
                    "make build optional": [
                        "with-static=1",
                        "PHENIQS_ZLIB_VERSION=1.2.11",
                        "PHENIQS_BZIP2_VERSION=1.0.8",
                        "PHENIQS_XZ_VERSION=5.2.5",
                        "PHENIQS_LIBDEFLATE_VERSION=1.6",
                        "PHENIQS_HTSLIB_VERSION=1.11",
                        "PHENIQS_RAPIDJSON_VERSION=1.1.0"
                    ],
                    "name": "pheniqs",
                    "remote filename": "pheniqs-HEAD.zip",
                    "remote url": "https://codeload.github.com/biosails/pheniqs/zip/HEAD",
                    "version": "2.0-trunk"
                }
            ]
        }
    }
}

def termination_handler(signal, frame):
    sys.exit(0)
signal.signal(signal.SIGTERM, termination_handler)
signal.signal(signal.SIGINT, termination_handler)

def to_json(ontology):
    return json.dumps(ontology, sort_keys=True, ensure_ascii=False, indent=4)

def merge(this, other):
    if this is None:
        return deepcopy(other)
    else:
        # this is not None
        if other is None:
            return deepcopy(this)
        else:
            # other is not None
            if isinstance(this, dict):
                if isinstance(other, dict):
                    merged = dict()
                    for k,v in this.items():
                        if k not in other:
                            merged[k] = deepcopy(this[k])
                    for k,v in other.items():
                        if k not in this:
                            merged[k] = deepcopy(v)
                        else:
                            merged[k] = merge(this[k], v)
                    return merged
                else:
                    raise ValueError('incompatible structure')
            else:
                return deepcopy(other)

def remove_directory(directory, log):
    if os.path.exists(directory):
        log.info('removing {}'.format(directory))
        command = [ 'rm', '-rf' ]
        command.append(directory)
        process = Popen(
            args=command,
            stdout=PIPE,
            stderr=PIPE
        )
        output, error = process.communicate()
        code = process.returncode
        if code != 0:
            print(output, error, code)
            raise CommandFailedError('failed to remove directory {}'.format(directory))

def prepare_path(path, log, overwrite=True):
    def check_permission(path):
        directory = os.path.dirname(path)
        writable = os.access(directory, os.W_OK)
        present = os.path.exists(directory)

        if writable and present:
            # this hirarchy exists and is writable
            return directory

        elif not (writable or present):
            # try the next one up
            return check_permission(directory)

        elif present and not writable:
            # directory exists but it not writable
            raise PermissionDeniedError(path)

    available = check_permission(path)
    if os.path.exists(path):
        if not overwrite: raise NoOverwriteError(path)
    else:
        directory = os.path.dirname(path)
        if directory != available:
            log.debug('creating directory %s', directory)
            os.makedirs(directory)

def prepare_directory(directory, log):
    def check_permission(directory):
        writable = os.access(directory, os.W_OK)
        present = os.path.exists(directory)

        if writable and present:
            # this hirarchy exists and is writable
            return directory

        elif not (writable or present):
            # try the next one up
            return check_permission(os.path.dirname(directory))

        elif present and not writable:
            # directory exists but it not writable
            raise PermissionDeniedError(directory)

    available = check_permission(directory)
    if available != directory:
       log.debug('creating directory %s', directory)
       os.makedirs(directory)

def split_class(name):
    return (name[0:name.rfind('.')], name[name.rfind('.') + 1:])

class DownloadError(Exception):
    def __init__(self, message):
        super(Exception, self).__init__('invalid checksum {}'.format(message))

class CommandFailedError(Exception):
    def __init__(self, message):
        super(Exception, self).__init__(message)

class CommandLineParser(object):
    def __init__(self, name):
        self.ontology = {
            'name': name,
            'interface': {},
            'instruction': {}
        }
        self.parser = None
        self.load()

    def load(self):
        self.ontology = merge(self.ontology, interface_configuration)
        self.parser = ArgumentParser(**self.interface['instruction'])

        # evaluate the type for each prototype
        for prototype in self.interface['prototype'].values():
            if 'type' in prototype['parameter']:
                prototype['parameter']['type'] = eval(prototype['parameter']['type'])

        # add global arguments
        for argument in self.interface['argument']:
            prototype = self.interface['prototype'][argument]

            # See https://docs.python.org/3/library/argparse.html?highlight=add_argument#argparse.ArgumentParser.add_argument
            self.parser.add_argument(*prototype['flag'], **prototype['parameter'])

        if self.sectioned:
            # Add individual command sections
            sub = self.parser.add_subparsers(**self.interface['section']['instruction'])
            for action in self.interface['section']['action']:
                if 'prototype' in action:
                    for prototype in action['prototype'].values():
                        if 'type' in prototype['parameter']:
                            prototype['parameter']['type'] = eval(prototype['parameter']['type'])
                    action['prototype'] = merge(self.interface['prototype'], action['prototype'])
                else:
                    action['prototype'] = deepcopy(self.interface['prototype'])

                key = action['instruction']['name']
                action_parser = sub.add_parser(**action['instruction'])
                if 'argument' in action:
                    for argument in action['argument']:
                        prototype = action['prototype'][argument]
                        action_parser.add_argument(*prototype['flag'], **prototype['parameter'])

                # Add groups of arguments, if any.
                if 'group' in action:
                    for group in action['group']:
                        group_parser = action_parser.add_argument_group(**group['instruction'])
                        if 'argument' in group:
                            for argument in group['argument']:
                                prototype = action['prototype'][argument]
                                group_parser.add_argument(*prototype['flag'], **prototype['parameter'])

        for k,v in vars(self.parser.parse_args()).items():
            if v is not None:
                self.ontology['instruction'][k] = v

    @property
    def help_triggered(self):
        return self.sectioned and self.action is None

    @property
    def interface(self):
        return self.ontology['interface']

    @property
    def sectioned(self):
        return 'section' in self.interface and 'action' in self.interface['section'] and self.interface['section']['action']

    @property
    def instruction(self):
        return self.ontology['instruction']

    @property
    def configuration(self):
        configuration = deepcopy(self.ontology)
        del configuration['interface']
        return configuration

    @property
    def action(self):
        return None if 'action' not in self.instruction else self.instruction['action']

    def help(self):
        self.parser.print_help()

class Package(object):
    def __init__(self, pipeline, node):
        self.log = logging.getLogger('Package')
        self.pipeline = pipeline
        for key in [
            'sha1',
            'version',
            'remote url',
            'package url',
            'download url',
            'remote filename',
            'remote basename',
            'extension',
            'compression',
            'display name',
            'path in archive',
            'document sha1 digest',
        ]:
            if key not in node:
                node[key] = None

        if node['remote url'] is not None:

            if isinstance(node['remote url'], list):
                remote_url = node['remote url'][0]
            else:
                remote_url = node['remote url']

            if node['remote filename'] is None:
                remote_dirname, node['remote filename'] = os.path.split(remote_url)

            remote_basename, compression = os.path.splitext(node['remote filename'])
            if node['compression'] is None and compression:
                node['compression'] = compression.strip('.')

            remote_basename, extension = os.path.splitext(remote_basename)
            if node['extension'] is None and extension:
                node['extension'] = extension.strip('.')

            if node['remote basename'] is None and remote_basename:
                 node['remote basename'] = remote_basename

            if node['download url'] is None:
                node['download url'] = os.path.join(self.download_prefix, node['remote filename'])

            if node['path in archive'] is None:
                node['path in archive'] = node['remote basename']

            if node['version'] is None and node['remote basename']:
                node['version'] = node['remote basename'].strip(node['name']).strip('-')

        if node['package url'] is None and node['path in archive'] is not None:
            node['package url'] = os.path.join(self.package_prefix, node['path in archive'])

        if node['display name'] is None:
            node['display name'] = node['name']
            if node['version'] is not None:
                node['display name'] = ' '.join([node['display name'], node['version']])

        for url in [
            'package url',
            'download url'
        ]:
            if node[url] is not None:
                node[url] = os.path.abspath(os.path.expanduser(os.path.expandvars(node[url])))

        content = json.dumps(node, sort_keys=True, ensure_ascii=False)
        node['document sha1 digest'] = hashlib.sha1(content.encode('utf8')).hexdigest()

        if node['document sha1 digest'] not in self.pipeline.persisted_instruction['package']:
            node['unpacked'] = False
            node['configured'] = False
            node['built'] = False
            node['installed'] = False
            self.pipeline.persisted_instruction['package'][node['document sha1 digest']] = node

        self.node = self.pipeline.persisted_instruction['package'][node['document sha1 digest']]

    @classmethod
    def create(cls, pipeline, ontology):
        instance = None
        if pipeline and ontology:
            if 'job implementation' in ontology:
                module, name  = split_class(ontology['job implementation'])
                try:
                    implementation_module = __import__(module, fromlist=[name])
                    implementation_class = getattr(implementation_module, name)
                    instance = implementation_class(pipeline, ontology)
                except ImportError as e:
                    pipeline.log.error('no module named %s found when attempting to instantiate %s job implementation', module, ontology['action'])
                    pipeline.log.debug(e)
                except AttributeError as e:
                    pipeline.log.error('class %s not defined in module %s when attempting to instantiate job implementation', name, module)
                    pipeline.log.debug(e)
                except Exception as e:
                    pipeline.log.error('%s %s', type(e), e)
            else:
                pipeline.log.error('unknown job implementation')

        return instance

    @property
    def env(self):
        if 'env' not in self.node or self.node['env'] is None:
            self.node['env'] = os.environ.copy()
        return self.node['env']

    @property
    def platform(self):
        return self.pipeline.platform

    @property
    def name(self):
        return self.node['name']

    @property
    def unpacked(self):
        return self.node['unpacked']

    @property
    def configured(self):
        return self.node['configured']

    @property
    def built(self):
        return self.node['built']

    @property
    def installed(self):
        return self.node['installed']

    @property
    def display_name(self):
        return self.node['display name']

    @property
    def stdout(self):
        return self.pipeline.stdout

    @property
    def stderr(self):
        return self.pipeline.stderr

    @property
    def install_prefix(self):
        return self.pipeline.install_prefix

    @property
    def download_prefix(self):
        return self.pipeline.download_prefix

    @property
    def package_prefix(self):
        return self.pipeline.package_prefix

    @property
    def bin_prefix(self):
        return self.pipeline.bin_prefix

    @property
    def include_prefix(self):
        return self.pipeline.include_prefix

    @property
    def lib_prefix(self):
        return self.pipeline.lib_prefix

    @property
    def extension(self):
        return self.node['extension']

    @property
    def compression(self):
        return self.node['compression']

    @property
    def path_in_archive(self):
        return self.node['path in archive']

    @property
    def remote_url(self):
        return self.node['remote url']

    @property
    def download_url(self):
        return self.node['download url']

    @property
    def package_url(self):
        return self.node['package url']

    @property
    def version(self):
        return self.node['version']

    @property
    def sha1(self):
        return self.node['sha1']

    def download(self):
        if self.download_url is not None:
            content = None
            if self.sha1 is None:
                if os.path.exists(self.download_url):
                    self.log.debug('removing old real time archive %s', self.download_url)
                    os.remove(self.download_url)

            if os.path.exists(self.download_url):
                with open(self.download_url, 'rb') as local:
                    content = local.read()
                    checksum = hashlib.sha1(content).hexdigest()
                    if self.sha1 is not None and checksum != self.sha1:
                        self.log.warning('removing corrupt archive %s', self.download_url)
                        os.remove(self.download_url)
                        content = None

            if content is None:
                remote_url = self.remote_url
                if not isinstance(self.remote_url, list):
                    remote_url = [ self.remote_url ]


                error = None
                success = False
                for url in remote_url:
                    self.log.debug('fetching %s', url)
                    request = Request(url, None)
                    try:
                        response = urlopen(request)
                    except BadStatusLine as e:
                        error = 'Bad http status error when requesting {}'.format(url)
                        self.log.warning(error)
                    except HTTPError as e:
                        error = 'Server returned an error when requesting {}: {}'.format(url, e.code)
                        self.log.warning(error)
                    except URLError as e:
                        error = 'Could not reach server when requesting {}: {}'.format(url, e.reason)
                        self.log.warning(error)
                    else:
                        content = response.read()
                        checksum = hashlib.sha1(content).hexdigest()
                        if self.sha1 is not None and checksum != self.sha1:
                            error = '{} checksum {} differs from {}'.format(self.display_name, checksum, self.sha1)
                            self.log.warning(error)
                        else:
                            prepare_path(self.download_url, self.log)
                            with open(self.download_url, 'wb') as local:
                                local.write(content)
                            self.log.info('downloaded archive saved %s %s', self.display_name, self.sha1)
                            success = True
                            break

                if not success:
                    raise DownloadError(error)

    def clean_package(self):
        if self.download_url is not None:
            remove_directory(self.package_url, self.log)
            self.node['unpacked'] = False
            self.node['configured'] = False
            self.node['built'] = False
            self.node['installed'] = False

    def clean(self):
        self.node['configured'] = False
        self.node['built'] = False
        self.node['installed'] = False

    def unpack(self):
        if not self.node['unpacked']:
            self.clean_package()
            if self.download_url is not None:
                self.download()

                self.log.info('unpacking %s', self.display_name)
                command = []
                if self.compression in [ 'gz', 'bz2']:
                    command.append('tar')
                    command.append('-x')
                    if self.compression == 'gz':
                        command.append('-z')
                    elif self.compression == 'bz2':
                        command.append('-j')
                    command.append('-f')
                    command.append(self.download_url)

                elif self.compression in [ 'zip' ]:
                    command.append('unzip')
                    command.append('-x')
                    command.append(self.download_url)

                process = Popen(
                    args=command,
                    env=self.env,
                    cwd=self.package_prefix,
                    stdout=PIPE,
                    stderr=PIPE
                )
                output, error = process.communicate()
                code = process.returncode
                if code == 0:
                    self.node['unpacked'] = True
                    self.stdout.write(output.decode('utf8'))
                    self.stderr.write(error.decode('utf8'))
                else:
                    print(code)
                    print(output.decode('utf8'))
                    print(error.decode('utf8'))
                    raise CommandFailedError('tar returned {}'.format(code))

    def configure(self):
        if not self.node['configured']:
            self.unpack()
            self.node['configured'] = True

    def build(self):
        if not self.node['built']:
            self.configure()
            self.node['built'] = True

    def install(self):
        if not self.node['installed']:
            self.build()
            self.node['installed'] = True

class Make(Package):
    def __init__(self, pipeline, node):
        Package.__init__(self, pipeline, node)
        for key in [
            'configure optional',
            'make build optional',
            'make build target',
        ]:
            if key not in node:
                self.node[key] = None

        if 'make install target' not in self.node:
            self.node['make install target'] = 'install'

        if 'make clean target' not in self.node:
            self.node['make clean target'] = 'clean'

        if 'include prefix in make' not in self.node:
            self.node['include prefix in make'] = False

        self.env['CFLAGS'] = '-I{}'.format(self.include_prefix)
        self.env['LDFLAGS'] = '-L{}'.format(self.lib_prefix)

    @property
    def configure_optional(self):
        return self.node['configure optional']

    @property
    def make_build_optional(self):
        return self.node['make build optional']

    @property
    def make_build_target(self):
        return self.node['make build target']

    @property
    def make_install_target(self):
        return self.node['make install target']

    @property
    def make_clean_target(self):
        return self.node['make clean target']

    @property
    def include_prefix_in_make(self):
        return self.node['include prefix in make']

    def clean(self):
        if self.package_url is not None:
            if os.path.exists(os.path.join(self.package_url, 'Makefile')) and self.make_clean_target:
                self.log.info('cleaning make environment %s', self.display_name)
                command = [ 'make', self.make_clean_target ]

                if self.include_prefix_in_make:
                    command.append('PREFIX={}'.format(self.install_prefix))

                self.log.debug(' '.join([str(i) for i in command]))

                process = Popen(
                    args=command,
                    env=self.env,
                    cwd=self.package_url,
                    stdout=PIPE,
                    stderr=PIPE
                )
                output, error = process.communicate()
                code = process.returncode
                if code == 0:
                    self.node['configured'] = False
                    self.node['built'] = False
                    self.node['installed'] = False
                    self.stdout.write(output.decode('utf8'))
                    self.stderr.write(error.decode('utf8'))
                else:
                    print(code)
                    print(output.decode('utf8'))
                    print(error.decode('utf8'))
                    raise CommandFailedError('make clean returned {}'.format(code))
            else:
                self.node['configured'] = False
                self.node['built'] = False
                self.node['installed'] = False

    def configure(self):
        if not self.node['configured']:
            if self.package_url is not None:
                self.unpack()
                if os.path.exists(os.path.join(self.package_url, 'configure')):
                    self.log.info('configuring make environment %s', self.display_name)
                    command = [ './configure', '--prefix={}'.format(self.install_prefix) ]

                    if self.configure_optional:
                        command.extend(self.configure_optional)

                    self.log.debug(' '.join([str(i) for i in command]))

                    process = Popen(
                        args=command,
                        env=self.env,
                        cwd=self.package_url,
                        stdout=PIPE,
                        stderr=PIPE
                    )
                    output, error = process.communicate()
                    code = process.returncode
                    if code == 0:
                        self.node['configured'] = True
                        self.stdout.write(output.decode('utf8'))
                        self.stderr.write(error.decode('utf8'))
                    else:
                        print(code)
                        print(output.decode('utf8'))
                        print(error.decode('utf8'))
                        raise CommandFailedError('configure returned {}'.format(code))
                else:
                    self.node['configured'] = True

    def build(self):
        if not self.node['built']:
            self.configure()
            if self.package_url is not None:
                self.log.info('building with make %s', self.display_name)
                command = [ 'make' ]

                if self.make_build_target:
                    command.append(self.make_build_target)

                if self.include_prefix_in_make:
                    command.append('PREFIX={}'.format(self.install_prefix))

                if self.make_build_optional:
                    command.extend(self.make_build_optional)

                self.log.debug(' '.join([str(i) for i in command]))

                process = Popen(
                    args=command,
                    env=self.env,
                    cwd=self.package_url,
                    stdout=PIPE,
                    stderr=PIPE
                )
                output, error = process.communicate()
                code = process.returncode
                if code == 0:
                    self.node['built'] = True
                    self.stdout.write(output.decode('utf8'))
                    self.stderr.write(error.decode('utf8'))
                else:
                    print(code)
                    print(output.decode('utf8'))
                    print(error.decode('utf8'))
                    raise CommandFailedError('make returned {}'.format(code))

    def install(self):
        if not self.node['installed']:
            self.build()
            if self.package_url is not None:
                self.log.info('installing with make %s', self.display_name)
                command = [ 'make' , self.make_install_target ]

                if self.include_prefix_in_make:
                    command.append('PREFIX={}'.format(self.install_prefix))

                if self.make_build_optional:
                    command.extend(self.make_build_optional)

                self.log.debug(' '.join([str(i) for i in command]))

                process = Popen(
                    args=command,
                    env=self.env,
                    cwd=self.package_url,
                    stdout=PIPE,
                    stderr=PIPE
                )
                output, error = process.communicate()
                code = process.returncode
                if code == 0:
                    self.node['installed'] = True
                    self.stdout.write(output.decode('utf8'))
                    self.stderr.write(error.decode('utf8'))
                else:
                    print(code)
                    print(output.decode('utf8'))
                    print(error.decode('utf8'))
                    raise CommandFailedError('make install returned {}'.format(code))

class BZip2(Make):
    def __init__(self, pipeline, node):
        Make.__init__(self, pipeline, node)

    def install_dynamic(self):
        so_basename = 'libbz2.so'
        full_versioned_so_basename = '{}.{}'.format(so_basename, self.version)
        full_versioned_so_package_path = os.path.join(self.package_url, full_versioned_so_basename)
        full_versioned_so_install_path = os.path.join(self.lib_prefix, full_versioned_so_basename)

        self.log.debug('copying %s to %s', full_versioned_so_package_path, full_versioned_so_install_path)
        command = [ 'rsync', '--copy-links', full_versioned_so_package_path, full_versioned_so_install_path ]
        process = Popen(
            args=command,
            env=self.env,
            cwd=self.package_url,
            stdout=PIPE,
            stderr=PIPE
        )
        output, error = process.communicate()
        code = process.returncode
        if code == 0:
            self.stdout.write(output.decode('utf8'))
            self.stderr.write(error.decode('utf8'))
        else:
            print(code)
            print(output.decode('utf8'))
            print(error.decode('utf8'))
            raise CommandFailedError('rsync returned {}'.format(code))

        split_version = self.version.split('.')
        while(len(split_version) > 1):
            split_version = split_version[:-1]
            partial_version = '.'.join(split_version)
            partial_versioned_so_basename = '{}.{}'.format(so_basename, partial_version)
            partial_versioned_so_install_path = os.path.join(self.lib_prefix, partial_versioned_so_basename)

            self.log.info('symlinking %s to %s', full_versioned_so_basename, partial_versioned_so_install_path)
            os.symlink(full_versioned_so_basename, partial_versioned_so_install_path)

    def build(self):
        if self.platform == 'Linux':
            if not self.node['built']:
                self.configure()
                if self.package_url is not None:
                    self.log.info('building %s dynamic library', self.display_name)
                    command = [ 'make', '--file', 'Makefile-libbz2_so' ]

                    if self.include_prefix_in_make:
                        command.append('PREFIX={}'.format(self.install_prefix))

                    self.log.debug(' '.join([str(i) for i in command]))

                    process = Popen(
                        args=command,
                        env=self.env,
                        cwd=self.package_url,
                        stdout=PIPE,
                        stderr=PIPE
                    )
                    output, error = process.communicate()
                    code = process.returncode
                    if code == 0:
                        self.stdout.write(output.decode('utf8'))
                        self.stderr.write(error.decode('utf8'))
                        self.install_dynamic()
                        Make.build(self)
                    else:
                        print(code)
                        print(output.decode('utf8'))
                        print(error.decode('utf8'))
                        raise CommandFailedError('make returned {}'.format(code))
        else:
            Make.build(self)

class LibDeflate(Make):
    def __init__(self, pipeline, node):
        Make.__init__(self, pipeline, node)

    def install(self):
        if not self.node['installed']:
            self.build()
            if self.package_url is not None:
                static_library_path = os.path.join(self.package_url, 'libdeflate.a')
                self.log.debug('copying %s to %s', static_library_path, self.lib_prefix)
                command = [ 'rsync', '--copy-links', static_library_path, self.lib_prefix ]
                process = Popen(
                    args=command,
                    env=self.env,
                    cwd=self.package_url,
                    stdout=PIPE,
                    stderr=PIPE
                )
                output, error = process.communicate()
                code = process.returncode
                if code == 0:
                    self.stdout.write(output.decode('utf8'))
                    self.stderr.write(error.decode('utf8'))
                else:
                    print(code)
                    print(output.decode('utf8'))
                    print(error.decode('utf8'))
                    raise CommandFailedError('rsync returned {}'.format(code))

                library_header_path = os.path.join(self.package_url, 'libdeflate.h')
                self.log.debug('copying %s to %s', library_header_path, self.include_prefix)
                command = [ 'rsync', '--copy-links', library_header_path, self.include_prefix ]
                process = Popen(
                    args=command,
                    env=self.env,
                    cwd=self.package_url,
                    stdout=PIPE,
                    stderr=PIPE
                )
                output, error = process.communicate()
                code = process.returncode
                if code == 0:
                    self.stdout.write(output.decode('utf8'))
                    self.stderr.write(error.decode('utf8'))
                else:
                    print(code)
                    print(output.decode('utf8'))
                    print(error.decode('utf8'))
                    raise CommandFailedError('rsync returned {}'.format(code))

                if self.platform == 'Linux':
                    dynamic_library_path = os.path.join(self.package_url, 'libdeflate.so')
                    self.log.debug('copying %s to %s', dynamic_library_path, self.lib_prefix)
                    command = [ 'rsync', '--copy-links', dynamic_library_path, self.lib_prefix ]
                    process = Popen(
                        args=command,
                        env=self.env,
                        cwd=self.package_url,
                        stdout=PIPE,
                        stderr=PIPE
                    )
                    output, error = process.communicate()
                    code = process.returncode
                    if code == 0:
                        self.stdout.write(output.decode('utf8'))
                        self.stderr.write(error.decode('utf8'))
                    else:
                        print(code)
                        print(output.decode('utf8'))
                        print(error.decode('utf8'))
                        raise CommandFailedError('rsync returned {}'.format(code))

                self.node['installed'] = True

class RapidJSON(Package):
    def __init__(self, pipeline, node):
        Package.__init__(self, pipeline, node)

    def install(self):
        if not self.node['installed']:
            self.build()
            if self.package_url is not None:
                self.log.debug('copying %s header files to %s', self.display_name, self.include_prefix)
                command = [ 'rsync' , '--recursive', os.path.join(self.package_url, 'include/'), self.include_prefix ]
                process = Popen(
                    args=command,
                    env=self.env,
                    cwd=self.package_url,
                    stdout=PIPE,
                    stderr=PIPE
                )
                output, error = process.communicate()
                code = process.returncode
                if code == 0:
                    self.node['installed'] = True
                    self.stdout.write(output.decode('utf8'))
                    self.stderr.write(error.decode('utf8'))
                else:
                    print(code)
                    print(output.decode('utf8'))
                    print(error.decode('utf8'))
                    raise CommandFailedError('rsync returned {}'.format(code))

class SAMTools(Make):
    def __init__(self, pipeline, node):
        Make.__init__(self, pipeline, node)
        self.node['configure optional'] = [ '--with-htslib={}'.format(self.install_prefix) ]

class PackageManager(object):
    def __init__(self, ontology):
        self.log = logging.getLogger('PackageManager')
        self.package = None
        self.cache = None
        self.stdout = None
        self.stderr = None
        self.stack = {}
        default = {
            'instruction': {
                'home': '~/.pheniqs',
                'platform': platform.system(),
                'current working directoy': os.getcwd(),
            },
        }
        self.ontology = merge(default, ontology)
        self.instruction['home'] = os.path.realpath(os.path.abspath(os.path.expanduser(os.path.expandvars(self.instruction['home']))))
        if 'verbosity' in self.instruction and self.instruction['verbosity']:
            self.log.setLevel(log_levels[self.instruction['verbosity']])

    @property
    def instruction(self):
        return self.ontology['instruction']

    @property
    def home(self):
        return self.instruction['home']

    @property
    def action(self):
        return self.instruction['action']

    @property
    def platform(self):
        return self.instruction['platform']

    def load_cache(self):
        if 'cache path' in self.instruction:
            if os.path.exists(self.cache_path):
                with io.open(self.cache_path, 'rb') as file:
                    self.cache = json.loads(file.read().decode('utf8'))

            if self.cache is None:
                self.cache = {
                    'environment': {},
                    'created': str(datetime.now()),
                }

            self.cache['loaded'] = str(datetime.now())

    def save_cache(self):
        if 'cache path' in self.ontology:
            self.log.debug('persisting cache')
            with io.open(self.cache_path, 'wb') as file:
                self.cache['saved'] = str(datetime.now())
                content = json.dumps(self.cache, sort_keys=True, ensure_ascii=False, indent=4).encode('utf8')
                file.write(content)

    @property
    def package_implementation(self):
        return self.ontology['package implementation']

    @property
    def cache_path(self):
        return self.instruction['cache path']

    @property
    def install_prefix(self):
        return self.instruction['install prefix']

    @property
    def download_prefix(self):
        return self.instruction['download prefix']

    @property
    def package_prefix(self):
        return self.instruction['package prefix']

    @property
    def bin_prefix(self):
        return self.instruction['bin prefix']

    @property
    def include_prefix(self):
        return self.instruction['include prefix']

    @property
    def lib_prefix(self):
        return self.instruction['lib prefix']

    def execute(self):
        preset = None
        if 'path' in self.instruction:
            resolved = os.path.abspath(os.path.realpath(os.path.expanduser(os.path.expandvars(self.instruction['path']))))
            if os.path.exists(resolved):
                self.log.debug('loading %s', self.instruction['path'])
                with io.open(resolved, 'rb') as file:
                    preset = json.loads(file.read().decode('utf8'))
                    preset['document sha1 digest'] = hashlib.sha1(resolved.encode('utf8')).hexdigest()
            else:
                raise CommandFailedError('failed to open {}'.format(self.instruction['path']))

        elif 'preset' in self.instruction:
            if self.instruction['preset'] in self.ontology['preset'].keys():
                revision = 'HEAD'
                if 'revision' in self.instruction:
                    revision = self.instruction['revision']
                name = '{}-{}'.format(self.instruction['preset'], revision)
                preset = self.ontology['preset'][self.instruction['preset']]
                preset['home'] = os.path.join(preset['home'], name)

                for package in preset['package']:
                    if package['name'] == 'pheniqs':
                        package['make build optional'].append('PHENIQS_VERSION=git-{}'.format(revision))
                        package['remote filename'] = 'pheniqs-{}.zip'.format(revision)
                        package['remote url'] = '{}/zip/{}'.format(self.ontology['pheniqs code url prefix'], revision)
                        package['version'] = 'git-{}'.format(revision)
                preset['document sha1 digest'] = hashlib.sha1(name.encode('utf8')).hexdigest()
            else:
                raise CommandFailedError('preset {} does not exist'.format(self.instruction['preset']))
        else:
            raise CommandFailedError('uknown preset to execute')

        for key in [
            'home',
            'platform',
            'package',
            'cache path',
            'install prefix',
            'download prefix',
            'package prefix',
            'bin prefix',
            'include prefix',
            'lib prefix',
        ]:
            if key not in preset: preset[key] = None

        if not preset['home']:            preset['home'] =              '~/.pheniqs'
        if not preset['platform']:        preset['platform'] =          platform.system()
        if not preset['cache path']:      preset['cache path'] =        os.path.join(preset['home'], 'cache.json')
        if not preset['install prefix']:  preset['install prefix'] =    os.path.join(preset['home'], 'install')
        if not preset['download prefix']: preset['download prefix'] =   os.path.join(preset['home'], 'download')
        if not preset['package prefix']:  preset['package prefix'] =    os.path.join(preset['home'], 'package')
        if not preset['bin prefix']:      preset['bin prefix'] =        os.path.join(preset['install prefix'], 'bin')
        if not preset['include prefix']:  preset['include prefix'] =    os.path.join(preset['install prefix'], 'include')
        if not preset['lib prefix']:      preset['lib prefix'] =        os.path.join(preset['install prefix'], 'lib')

        for path in [
            'home',
            'cache path',
            'install prefix',
            'download prefix',
            'package prefix',
            'bin prefix',
            'include prefix',
            'lib prefix',
        ]:
            preset[path] = os.path.abspath(os.path.expanduser(os.path.expandvars(preset[path])))

        self.ontology['instruction'] = merge(self.instruction, preset)
        self.load_cache()
        if self.instruction['document sha1 digest'] not in self.cache['environment']:
            self.cache['environment'][self.instruction['document sha1 digest']] = { 'package': {} }

        self.persisted_instruction = self.cache['environment'][self.instruction['document sha1 digest']]

        if self.instruction['package']:
            self.stack['package'] = []
            prepare_directory(self.home, self.log)
            prepare_directory(self.install_prefix, self.log)
            prepare_directory(self.download_prefix, self.log)
            prepare_directory(self.package_prefix, self.log)
            self.stdout = io.open(os.path.join(self.home, 'output'), 'a')
            self.stderr = io.open(os.path.join(self.home, 'error'), 'a')

            for o in self.instruction['package']:
                key = o['name']
                if key in self.package_implementation:
                    o = merge(o, self.package_implementation[key])

                package = Package.create(self, o)
                if package:
                    self.stack['package'].append(package)
                    if self.action == 'clean':
                        self.log.info('cleaning %s', package.display_name)
                        package.clean()

                    elif self.action == 'build':
                        if not package.installed:
                            package.install()
                        else:
                            self.log.info('%s is already installed', package.display_name)

                    elif self.action == 'clean.package':
                        self.log.info('clearing %s', package.display_name)
                        package.clean_package()

                    self.save_cache()

    def close(self):
        self.save_cache()

        if self.stdout:
            self.stdout.close();
        if self.stderr:
            self.stderr.close();

        Job.close(self)

def main():
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    pipeline = None

    try:
        command = CommandLineParser('build api')
        if command.help_triggered:
            command.help()
            sys.exit(0)
        else:
            if 'verbosity' in command.instruction and command.instruction['verbosity']:
                logging.getLogger().setLevel(log_levels[command.instruction['verbosity']])

            job = PackageManager(command.configuration)
            job.execute()

    except (
        DownloadError,
        CommandFailedError
    ) as e:
        logging.getLogger('main').critical(e)
        sys.exit(1)

    except(KeyboardInterrupt, SystemExit) as e:
        if e.code != 0:
            logging.getLogger('main').critical(e)
            sys.exit(1)

    finally:
        if pipeline: pipeline.close()

    sys.exit(0)

if __name__ == '__main__':
    main()
