from archappl.client import ArchiverMgmtClient


client = ArchiverMgmtClient()
client.url = 'http://127.0.0.1:17665'

all_pvs = client.get_all_pvs()
print(all_pvs)
# [u'TST:fakeGaussianNoise', u'TST:gaussianNoise', u'TST:uniformNoise']
