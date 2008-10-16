#!/usr/bin/env python
########################################################################
# $Header: /tmp/libdirac/tmp.stZoy15380/dirac/DIRAC3/DIRAC/Interfaces/scripts/dirac-production-mc-extend.py,v 1.1 2008/10/16 09:28:34 paterson Exp $
# File :   dirac-production-mc-extend
# Author : Stuart Paterson
########################################################################
__RCSID__   = "$Id: dirac-production-mc-extend.py,v 1.1 2008/10/16 09:28:34 paterson Exp $"
__VERSION__ = "$Revision: 1.1 $"
from DIRACEnvironment import DIRAC
from DIRAC.Core.Base import Script
from DIRAC.Interfaces.API.DiracProduction                    import DiracProduction

Script.parseCommandLine( ignoreErrors = True )
args = Script.getPositionalArgs()

def usage():
  print 'Usage: %s <Production ID> <Number Of Jobs>' %(Script.scriptName)
  DIRAC.exit(2)

if len(args)<2 or len(args)>2:
  usage()

diracProd = DiracProduction()
prodID = args[0]
number = args[1]

result = diracProd.extendProduction(prodID,number,printOutput=True)
if result['OK']:
  DIRAC.exit(0)
elif result.has_key('Message'):
  print 'Extending production failed with message:\n%s' %(result['Message'])
  DIRAC.exit(2)
else:
  print 'Null result for extendProduction() call'
  DIRAC.exit(2)