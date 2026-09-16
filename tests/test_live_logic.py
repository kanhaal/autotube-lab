from datetime import datetime, timezone, timedelta
from pathlib import Path
from app.analytics.learning import refresh_niche_weights
from app.domain.models import AnalyticsSnapshot
from app.storage.sqlite import Repository
from app.research.packet import build_research_packet
from app.scripting.engine import TemplateScriptEngine


def test_refresh_niche_weights_persists_adaptive_distribution(tmp_path: Path):
    repo=Repository(tmp_path/'a.db'); repo.init(); now=datetime.now(timezone.utc)
    for i in range(3):
        repo.save_analytics(AnalyticsSnapshot(f'ai{i}','kernelrush','ai_software',now-timedelta(days=8+i),now,1000,.08,500,.7,200,10,0))
        repo.save_analytics(AnalyticsSnapshot(f'os{i}','kernelrush','open_source',now-timedelta(days=8+i),now,1000,.04,100,.4,50,1,0))
    w=refresh_niche_weights(repo,'kernelrush',['ai_software','open_source'],now=now,min_samples=2)
    assert w['ai_software'] > w['open_source']
    assert repo.get_weights('kernelrush') == w


def test_script_engine_builds_substantial_original_structure():
    packet=build_research_packet('Alpha launches',{ 'title':'Alpha launches','summary':'Alpha released a new developer tool.'},[
      {'source_name':'Primary','url':'https://a','text':'Alpha released a developer tool with local execution and a public API.'},
      {'source_name':'Secondary','url':'https://b','text':'Developers are discussing Alpha because its local execution changes deployment tradeoffs.'}
    ])
    script=TemplateScriptEngine().generate(packet)
    assert 'Why it matters' in script
    assert len(script.split()) >= 250
