from datetime import datetime, timezone, timedelta
from pathlib import Path

from app.domain.models import StoryCandidate, AnalyticsSnapshot, Publication
from app.scoring.trends import score_candidate, deduplicate_candidates
from app.experiments.allocation import performance_score, compute_niche_weights, choose_niche
from app.validation.facts import validate_script
from app.storage.sqlite import Repository
from app.orchestration.pipeline import research_supports_candidate


def test_candidate_score_rewards_fresh_velocity_and_reliability():
    c = StoryCandidate('1','open_source','Tool explodes','https://x','GitHub','api',
        datetime.now(timezone.utc)-timedelta(hours=1), datetime.now(timezone.utc),
        ('Tool',),'summary',{'velocity':0.9},0.95,'metadata only')
    assert score_candidate(c) > 0.75


def test_deduplicate_prefers_high_reliability_same_url():
    now = datetime.now(timezone.utc)
    a = StoryCandidate('a','ai_software','A','https://x?a=1','A','api',now,now,(),'',{},0.5,'')
    b = StoryCandidate('b','ai_software','B','https://x?a=1','B','api',now,now,(),'',{},0.9,'')
    assert deduplicate_candidates([a,b]) == [b]


def test_performance_score_matches_weights_and_renormalizes_missing():
    metrics = dict(retention=0.70, views_ratio=1.2, ctr=0.08, subs_per_1k=10, watch_per_1k_imp=120)
    s = performance_score(metrics)
    assert 0 < s < 2
    s2 = performance_score({'retention': .7, 'ctr': .08})
    assert s2 > 0


def test_niche_weights_keep_floor_and_cap():
    scores = {'ai_software':[1.8,1.7,1.9], 'open_source':[1,1,1], 'consumer_tech':[.5,.6,.4]}
    w = compute_niche_weights(scores, floor=.10, cap=.80)
    assert abs(sum(w.values())-1) < 1e-9
    assert min(w.values()) >= .10
    assert max(w.values()) <= .80


def test_choose_niche_exploration_rotates_evenly():
    niches=['a','b','c']
    assert [choose_niche(niches, day_index=i, exploration_days=45) for i in range(6)] == ['a','b','c','a','b','c']


def test_fact_gate_blocks_unsupported_numbers():
    packet = {'sources':[{'text':'Tool launched this week.'},{'text':'The project is open source.'}], 'entities':['Tool']}
    result = validate_script('Tool gained 8,000 stars today.', packet)
    assert not result.ok


def test_research_requires_distinct_corroborating_sources():
    c = StoryCandidate('1','ai_software','Alpha launch','u','A','api',datetime.now(timezone.utc),datetime.now(timezone.utc),('Alpha',),'',{},.9,'')
    assert not research_supports_candidate(c,[c])
    b = StoryCandidate('2','ai_software','Alpha launches new model','v','B','rss',c.published_at,c.fetched_at,('Alpha',),'Alpha new model launch',{},.8,'')
    assert research_supports_candidate(c,[c,b])


def test_sqlite_roundtrip(tmp_path: Path):
    repo=Repository(tmp_path/'x.db')
    repo.init()
    p=Publication('ep1','kernelrush','vid123','private',datetime.now(timezone.utc))
    repo.save_publication(p)
    assert repo.get_publication('ep1').youtube_video_id == 'vid123'


def test_analytics_maturity_filters_under_7_days(tmp_path: Path):
    repo=Repository(tmp_path/'x.db'); repo.init()
    now=datetime.now(timezone.utc)
    repo.save_analytics(AnalyticsSnapshot('v1','kernelrush','ai_software',now-timedelta(days=3),now,1000,.05,100,.5,50,1,0))
    repo.save_analytics(AnalyticsSnapshot('v2','kernelrush','open_source',now-timedelta(days=8),now,1000,.05,100,.5,50,1,0))
    mature=repo.mature_analytics('kernelrush', now=now, min_age_days=7)
    assert [x.video_id for x in mature] == ['v2']
