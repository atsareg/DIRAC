#!/usr/bin/env python
########################################################################
# File :    dirac-dms-add-file
# Author :  Stuart Paterson
########################################################################
"""
  Upload a file to the grid storage and register it in the File Catalog
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
__RCSID__ = "$Id$"

from DIRAC.Core.Base import Script
from DIRAC import S_OK
import os
from DIRAC.Core.Utilities.DIRACScript import DIRACScript

overwrite = False


def setOverwrite(arg):
  global overwrite
  overwrite = True
  return S_OK()


def getDict(item_list):
  """
    From the input list, populate the dictionary
  """
  lfn_dict = {}
  lfn_dict['lfn'] = item_list[0].replace('LFN:', '').replace('lfn:', '')
  lfn_dict['localfile'] = item_list[1]
  lfn_dict['SE'] = item_list[2]
  guid = None
  if len(item_list) > 3:
    guid = item_list[3]
  lfn_dict['guid'] = guid
  return lfn_dict


@DIRACScript()
def main():
  global overwrite
  Script.setUsageMessage('\n'.join([
      __doc__.split('\n')[1],
      '\nUsage:',
      '  %s [option|cfgfile] ... LFN Path SE [GUID]' % Script.scriptName,
      '\nArguments:',
      '  LFN:      Logical File Name',
      '  Path:     Local path to the file',
      '  SE:       DIRAC Storage Element',
      '  GUID:     GUID to use in the registration (optional)',
      '',
      '**OR**',
      '',
      'Usage:',
      '  %s [option|cfgfile] ... LocalFile' % Script.scriptName,
      '\nArguments:',
      '  LocalFile: Path to local file containing all the above, i.e.:',
      '  lfn1 localfile1 SE [GUID1]',
      '  lfn2 localfile2 SE [GUID2]'
  ]))

  Script.registerSwitch("f", "force", "Force overwrite of existing file", setOverwrite)
  Script.parseCommandLine(ignoreErrors=True)
  args = Script.getPositionalArgs()
  if len(args) < 1 or len(args) > 4:
    Script.showHelp(exitCode=1)

  from DIRAC.DataManagementSystem.Client.DataManager import DataManager
  from DIRAC import gLogger
  import DIRAC
  exitCode = 0

  lfns = []
  if len(args) == 1:
    inputFileName = args[0]
    if os.path.exists(inputFileName):
      inputFile = open(inputFileName, 'r')
      for line in inputFile:
        line = line.rstrip()
        items = line.split()
        items[0] = items[0].replace('LFN:', '').replace('lfn:', '')
        lfns.append(getDict(items))
      inputFile.close()
    else:
      gLogger.error("Error: LFN list '%s' missing." % inputFileName)
      exitCode = 4
  else:
    lfns.append(getDict(args))

  dm = DataManager()
  for lfn in lfns:
    if not os.path.exists(lfn['localfile']):
      gLogger.error("File %s must exist locally" % lfn['localfile'])
      exitCode = 1
      continue
    if not os.path.isfile(lfn['localfile']):
      gLogger.error("%s is not a file" % lfn['localfile'])
      exitCode = 2
      continue

    gLogger.notice("\nUploading %s" % lfn['lfn'])
    res = dm.putAndRegister(lfn['lfn'], lfn['localfile'], lfn['SE'], lfn['guid'], overwrite=overwrite)
    if not res['OK']:
      exitCode = 3
      gLogger.error('Error: failed to upload %s to %s' % (lfn['lfn'], lfn['SE']))
      continue
    else:
      gLogger.notice('Successfully uploaded file to %s' % lfn['SE'])

  DIRAC.exit(exitCode)


if __name__ == "__main__":
  main()