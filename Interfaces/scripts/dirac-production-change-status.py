#!/usr/bin/env python
########################################################################
# $Header: /tmp/libdirac/tmp.stZoy15380/dirac/DIRAC3/DIRAC/Interfaces/scripts/dirac-production-change-status.py,v 1.1 2008/10/16 09:28:33 paterson Exp $
# File :   dirac-production-change-status
# Author : Stuart Paterson
########################################################################
__RCSID__   = "$Id: dirac-production-change-status.py,v 1.1 2008/10/16 09:28:33 paterson Exp $"
__VERSION__ = "$Revision: 1.1 $"
from DIRACEnvironment import DIRAC
from DIRAC.Core.Base import Script
from DIRAC.Interfaces.API.DiracProduction                    import DiracProduction

Script.parseCommandLine( ignoreErrors = True )
args = Script.getPositionalArgs()

def usage():
  print 'Usage: %s <Command> <Production ID> |<Production ID>' %(Script.scriptName)
  print "Commands include: 'start', 'stop', 'manual', 'automatic'"
  DIRAC.exit(2)

if len(args) < 2:
  usage()

diracProd = DiracProduction()
exitCode = 0
errorList = []
command = args[0]

for prodID in args[1:]:

  result = diracProd.production(prodID,command,printOutput=True,disableCheck=False)
  if result.has_key('Message'):
    errorList.append( (prodID, result['Message']) )
    exitCode = 2
  elif not result:
    errorList.append( (prodID, 'Null result for getProduction() call' ) )
    exitCode = 2
  else:
    exitCode = 0

for error in errorList:
  print "ERROR %s: %s" % error

DIRAC.exit(exitCode)