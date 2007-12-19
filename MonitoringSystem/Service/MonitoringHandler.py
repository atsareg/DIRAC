# $Header: /tmp/libdirac/tmp.stZoy15380/dirac/DIRAC3/DIRAC/MonitoringSystem/Service/MonitoringHandler.py,v 1.3 2007/12/19 18:05:03 acasajus Exp $
__RCSID__ = "$Id: MonitoringHandler.py,v 1.3 2007/12/19 18:05:03 acasajus Exp $"
import types
import os
from DIRAC import gLogger, gConfig, rootPath, S_OK, S_ERROR
from DIRAC.Core.DISET.RequestHandler import RequestHandler
from DIRAC.Core.Utilities import DEncode
from DIRAC.MonitoringSystem.Client.MonitoringClient import gMonitor
from DIRAC.ConfigurationSystem.Client import PathFinder

from DIRAC.MonitoringSystem.private.ServiceInterface import gServiceInterface

def initializeMonitoringHandler( serviceInfo ):
  #Check that the path is writable
  monitoringSection = PathFinder.getServiceSection( "Monitoring/Server" )
  #Get data location
  retDict = gConfig.getOption( "%s/DataLocation" % monitoringSection )
  if not retDict[ 'OK' ]:
    return retDict
  dataPath = retDict[ 'Value' ].strip()
  if "/" != dataPath[0]:
    dataPath = os.path.realpath( "%s/%s" % ( rootPath, dataPath ) )
  gLogger.info( "Data will be written into %s" % dataPath )
  try:
    os.makedirs( dataPath )
  except:
    pass
  try:
    testFile = "%s/mon.jarl.test" % dataPath
    fd = file( testFile, "w" )
    fd.close()
    os.unlink( testFile )
  except IOError:
    gLogger.fatal( "Can't write to %s" % dataPath )
    return S_ERROR( "Data location is not writable" )
  #Define globals
  gServiceInterface.initialize( dataPath )
  if not gServiceInterface.initializeDB():
    return S_ERROR( "Can't start db engine" )
  gMonitor.registerActivity( "cachedplots", "Cached plot images", "Monitoring plots", "plots", gMonitor.OP_SUM )
  gMonitor.registerActivity( "drawnplots", "Drawn plot images", "Monitoring plots", "plots", gMonitor.OP_SUM )
  return S_OK()

class MonitoringHandler( RequestHandler ):

  types_registerActivities = [ types.DictType, types.DictType ]
  def export_registerActivities( self, sourceDict, activitiesDict ):
    """
    Registers new activities
    """
    return gServiceInterface.registerActivities( sourceDict, activitiesDict)

  types_commitMarks = [ types.IntType, types.DictType ]
  def export_commitMarks( self, sourceId, activitiesDict ):
    """
    Adds marks for activities
    """
    return gServiceInterface.commitMarks( sourceId, activitiesDict )

  types_queryField = [ types.StringType, types.DictType ]
  def export_queryField( self, field, definedFields ):
    """
    Returns available values for a field., given a set of fields and values,
    """
    definedFields[ 'sources.setup' ] = self.serviceInfoDict[ 'clientSetup' ]
    return gServiceInterface.fieldValue( field, definedFields )

  types_tryView = [ types.IntType, types.IntType, types.StringType ]
  def export_tryView( self, fromSecs, toSecs, viewDescriptionStub ):
    """
      Generates plots based on a DEncoded view description
    """
    viewDescription, stubLength = DEncode.decode( viewDescriptionStub )
    if not 'definition' in viewDescription:
      return S_ERROR( "No plot definition given" )
    defDict = viewDescription[ 'definition' ]
    defDict[ 'sources.setup' ] = self.serviceInfoDict[ 'clientSetup' ]
    return gServiceInterface.generatePlots( fromSecs, toSecs, viewDescription )

  types_saveView = [ types.StringType, types.StringType ]
  def export_saveView( self, viewName, viewDescriptionStub ):
    """
    Saves a view
    """
    if len( viewName ) == 0:
      return S_OK( "View name not valid" )
    viewDescription, stubLength = DEncode.decode( viewDescriptionStub )
    if not 'definition' in viewDescription:
      return S_ERROR( "No plot definition given" )
    defDict = viewDescription[ 'definition' ]
    defDict[ 'sources.setup' ] = self.serviceInfoDict[ 'clientSetup' ]
    return gServiceInterface.saveView( viewName, viewDescription )

  types_getViews = []
  def export_getViews( self, onlyStatic = True ):
    """
    Returns a list of stored views
    """
    return gServiceInterface.getViews( onlyStatic )

  types_plotView = [ types.DictType ]
  def export_plotView( self, viewRequest ):
    """
    Generates plots for a view
    """
    for required in ( "fromSecs", "toSecs", "id" ):
      if required not in viewRequest:
        return S_ERROR( "Missing %s field in request" % required )
    if not "size" in viewRequest:
      viewRequest[ 'size' ] = 1
    if viewRequest[ 'size' ] not in ( 0, 1, 2, 3 ):
      return S_ERROR( "Invalid size" )
    return gServiceInterface.plotView( viewRequest )

  types_deleteView = [ types.IntType ]
  def export_deleteView( self, viewId ):
    """
    Deletes a view
    """
    return gServiceInterface.deleteView( viewId )

  def transfer_toClient( self, fileId, token, fileHelper ):
    retVal = gServiceInterface.getGraphData( fileId )
    if not retVal[ 'OK' ]:
      return retVal
    retVal = fileHelper.sendData( retVal[ 'Value' ] )
    if not retVal[ 'OK' ]:
      return retVal
    fileHelper.sendEOF()
    return S_OK()