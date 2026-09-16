from app.cli import refresh_live_learning
class FakeRepo: pass
class FakeClient: pass

def test_refresh_live_learning_uses_channel_niches(monkeypatch):
    called={}
    def fake(client,repo,channel_id,niches,**kwargs):
        called.update(client=client,repo=repo,channel_id=channel_id,niches=niches); return {'snapshots':2,'weights':{'a':1.0}}
    monkeypatch.setattr('app.cli.refresh_channel_analytics',fake)
    monkeypatch.setattr('app.cli.channel_config',lambda cid:{'id':cid,'niches':['a','b']})
    out=refresh_live_learning(FakeClient(),FakeRepo(),'kernelrush')
    assert out['snapshots']==2
    assert called['niches']==['a','b']
