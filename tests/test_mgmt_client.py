from archappl.client import ArchiverMgmtClient


client = ArchiverMgmtClient()

all_pvs = client.get_all_pvs("*")
print(all_pvs)
# [u'TST:fakeGaussianNoise', u'TST:gaussianNoise', u'TST:uniformNoise']
