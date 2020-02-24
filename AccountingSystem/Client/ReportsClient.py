""" Module that holds the ReportsClient Client class
"""

__RCSID__ = "$Id$"

import tempfile

from DIRAC import S_OK, S_ERROR
from DIRAC.Core.Base.Client import Client
from DIRAC.Core.DISET.TransferClient import TransferClient
from DIRAC.Core.Utilities.Plotting.FileCoding import codeRequestInFileId


class ReportsClient(Client):

  def __init__(self, transferClient=None, **kwargs):
    """ c'tor
    """
    super(ReportsClient, self).__init__(**kwargs)
    self.setServer('Accounting/ReportGenerator')

    self.transferClient = transferClient

  def __getTransferClient(self):
    if not self.transferClient:
      return TransferClient('Accounting/ReportGenerator')
    else:
      return self.transferClient

  def listReports(self, typeName):
    result = self._getRPC().listReports(typeName)
    if 'rpcStub' in result:
      del(result['rpcStub'])
    return result

  def getReport(self, typeName, reportName, startTime, endTime, condDict, grouping, extraArgs=None):

    if not isinstance(extraArgs, dict):
      extraArgs = {}
    plotRequest = {'typeName': typeName,
                   'reportName': reportName,
                   'startTime': startTime,
                   'endTime': endTime,
                   'condDict': condDict,
                   'grouping': grouping,
                   'extraArgs': extraArgs}
    result = self._getRPC().getReport(plotRequest)
    if 'rpcStub' in result:
      del(result['rpcStub'])
    return result

  def generatePlot(self, typeName, reportName, startTime, endTime, condDict, grouping, extraArgs=None):
    if not isinstance(extraArgs, dict):
      extraArgs = {}
    plotRequest = {'typeName': typeName,
                   'reportName': reportName,
                   'startTime': startTime,
                   'endTime': endTime,
                   'condDict': condDict,
                   'grouping': grouping,
                   'extraArgs': extraArgs}
    result = self._getRPC().generatePlot(plotRequest)
    if 'rpcStub' in result:
      del(result['rpcStub'])
    return result

  def generateDelayedPlot(
          self,
          typeName,
          reportName,
          startTime,
          endTime,
          condDict,
          grouping,
          extraArgs=None,
          compress=True):
    if not isinstance(extraArgs, dict):
      extraArgs = {}
    plotRequest = {'typeName': typeName,
                   'reportName': reportName,
                   'startTime': startTime,
                   'endTime': endTime,
                   'condDict': condDict,
                   'grouping': grouping,
                   'extraArgs': extraArgs}
    return codeRequestInFileId(plotRequest, compress)

  def getPlotToMem(self, plotName):
    transferClient = self.__getTransferClient()
    tmpFile = tempfile.TemporaryFile()
    retVal = transferClient.receiveFile(tmpFile, plotName)
    if not retVal['OK']:
      return retVal
    tmpFile.seek(0)
    data = tmpFile.read()
    tmpFile.close()
    return S_OK(data)

  def getPlotToDirectory(self, plotName, dirDestination):
    transferClient = self.__getTransferClient()
    try:
      destFilename = "%s/%s" % (dirDestination, plotName)
      with open(destFilename, "wb") as destFile:
        retVal = transferClient.receiveFile(destFile, plotName)
        if not retVal['OK']:
          return retVal
    except Exception as e:
      return S_ERROR("Can't open file %s for writing: %s" % (destFilename, str(e)))
    return S_OK()
