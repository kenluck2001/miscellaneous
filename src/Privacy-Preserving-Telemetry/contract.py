from aserver import AServer
from aclient import AClient
import helper

SEED = 2023

if __name__ == '__main__':
    '''
    We take a shortcut, rather than creating a server-client using a REST API for sake of limited time in this research, we have two instances, client and server. The client creates snapshots and sends to the server for processing.
    '''
    client = AClient()
    settings = client.getSettings()
    helper = helper.Helper(settings, SEED)

    hashFamily = helper.HashFamily()

    textlist = ["ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "ken", "sam", "jane", "jane", "jane"]
    snapshotLst = client.CreateBulkRecords (textlist, hashFamily)
    print ("snapshotLst: {}".format(snapshotLst))


    ##################### logical  Boundary for client server interaction in our mind, as we did not implement a REST API due to time constrainst#####################

    server = AServer()
    mHmat = server.SketchHCMS(snapshotLst)
    print ("mHmat: {}".format(mHmat))

    eventLst = ["ken", "sam", "jane"]
    freqDict = server.Histogram (eventLst, mHmat, hashFamily)
    print ("freqDict: {}".format(freqDict))
