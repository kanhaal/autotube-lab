from __future__ import annotations
import hashlib, re, urllib.parse
from datetime import datetime, timezone, timedelta
from app.domain.models import StoryCandidate
from app.collectors.base import get_json,get_text,parse_dt,parse_rss

def _id(prefix,url):return prefix+'-'+hashlib.sha1(url.encode()).hexdigest()[:14]
def _strip_html(s):return re.sub(r'<[^>]+>',' ',s or '').replace('&amp;','&').strip()

def github_candidates(niche='open_source',limit=15):
    date=(datetime.now(timezone.utc)-timedelta(days=7)).date().isoformat()
    q=urllib.parse.quote(f'created:>{date} stars:>50')
    data=get_json(f'https://api.github.com/search/repositories?q={q}&sort=stars&order=desc&per_page={limit}',headers={'Accept':'application/vnd.github+json'})
    now=datetime.now(timezone.utc); out=[]
    for x in data.get('items',[]):
        stars=x.get('stargazers_count',0); vel=min(1,stars/5000)
        out.append(StoryCandidate(_id('gh',x['html_url']),niche,x['full_name'],x['html_url'],'GitHub','api',parse_dt(x.get('created_at')),now,(x['name'],),x.get('description') or '',{'stars':stars,'velocity':vel},.95,'repository metadata; respect repository licenses for code/content'))
    return out

def hackernews_candidates(niche='ai_software',limit=20):
    ids=get_json('https://hacker-news.firebaseio.com/v0/topstories.json')[:limit]; now=datetime.now(timezone.utc); out=[]
    for i in ids:
        x=get_json(f'https://hacker-news.firebaseio.com/v0/item/{i}.json')
        if not x or x.get('type')!='story':continue
        url=x.get('url') or f'https://news.ycombinator.com/item?id={i}'
        score=x.get('score',0); comments=x.get('descendants',0)
        out.append(StoryCandidate(f'hn-{i}',niche,x.get('title',''),url,'Hacker News','community',parse_dt(x.get('time')),now,(),'',{'score':score,'comments':comments,'velocity':min(1,(score+comments)/1000)},.70,'discovery/community signal; corroborate primary claims'))
    return out

def huggingface_candidates(niche='ai_software',limit=15):
    data=get_json(f'https://huggingface.co/api/models?sort=trendingScore&direction=-1&limit={limit}'); now=datetime.now(timezone.utc); out=[]
    for x in data:
        mid=x.get('id') or x.get('modelId'); url='https://huggingface.co/'+mid
        likes=x.get('likes',0) or 0; downloads=x.get('downloads',0) or 0
        out.append(StoryCandidate(_id('hf',url),niche,mid,url,'Hugging Face','api',parse_dt(x.get('createdAt') or x.get('lastModified')),now,(mid.split('/')[-1],),f'Model {mid}; downloads {downloads}; likes {likes}',{'likes':likes,'downloads':downloads,'velocity':min(1,(likes/500)+(downloads/1_000_000))},.90,'model metadata only'))
    return out

def steam_news_candidates(app_ids=None,niche='gaming',per_app=5):
    app_ids=app_ids or [730,570,1091500,578080]; now=datetime.now(timezone.utc); out=[]
    for appid in app_ids:
        data=get_json(f'https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid={appid}&count={per_app}&maxlength=500&format=json')
        for x in data.get('appnews',{}).get('newsitems',[]):
            url=x.get('url') or f'https://store.steampowered.com/app/{appid}'
            out.append(StoryCandidate(_id('steam',url),niche,x.get('title',''),url,x.get('feedlabel') or 'Steam','api',parse_dt(x.get('date')),now,(str(appid),),_strip_html(x.get('contents','')),{'app_id':appid,'velocity':.5},.90,'official Steam news metadata/text'))
    return out

def rss_candidates(feed_url:str,niche:str,source_name:str,reliability=.8,limit=20):
    now=datetime.now(timezone.utc); out=[]
    for x in parse_rss(get_text(feed_url))[:limit]:
        if not x.get('url'):continue
        out.append(StoryCandidate(_id('rss',x['url']),niche,x.get('title',''),x['url'],source_name,'rss',parse_dt(x.get('published')),now,(),_strip_html(x.get('summary','')),{'velocity':.4},reliability,'RSS excerpt/metadata; verify original article usage'))
    return out

def google_news_search(query:str,niche:str,limit=12):
    url='https://news.google.com/rss/search?q='+urllib.parse.quote(query)+'&hl=en-IN&gl=IN&ceid=IN:en'
    return rss_candidates(url,niche,'Google News',.72,limit)

def google_trends_candidates(niche='internet_culture',geo='US',limit=20):
    url=f'https://trends.google.com/trending/rss?geo={geo}'
    return rss_candidates(url,niche,'Google Trends',.75,limit)

def collect_for_niche(niche:str)->list[StoryCandidate]:
    funcs={
      'ai_software': lambda: hackernews_candidates(niche,15)+huggingface_candidates(niche,15),
      'open_source': lambda: github_candidates(niche,15)+hackernews_candidates(niche,15),
      'consumer_tech': lambda: hackernews_candidates(niche,25),
      'gaming': lambda: steam_news_candidates(niche=niche),
      'internet_culture': lambda: google_trends_candidates(niche,'US',20),
    }
    return funcs[niche]()
