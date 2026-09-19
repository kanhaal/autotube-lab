import type {EffectRenderProps} from './types';

type Point=[number,number];
const shapes:Record<string,Point[]>={
  plus:[[40,5],[60,5],[60,40],[95,40],[95,60],[60,60],[60,95],[40,95],[40,60],[5,60],[5,40],[40,40]],
  diamond:[[50,3],[66,20],[82,34],[97,50],[82,66],[66,80],[50,97],[34,80],[18,66],[3,50],[18,34],[34,20]],
  play:[[18,8],[38,18],[58,28],[78,38],[94,50],[78,62],[58,72],[38,82],[18,92],[18,72],[18,50],[18,28]],
};

const interpolate=(a:Point,b:Point,p:number):Point=>[
  a[0]+(b[0]-a[0])*p,
  a[1]+(b[1]-a[1])*p,
];

export const IconMorphEffect=({effect,frame,durationInFrames,theme}:EffectRenderProps)=>{
  const from=shapes[String(effect.from??'plus')]??shapes.plus;
  const to=shapes[String(effect.to??'play')]??shapes.play;
  const raw=Math.max(0,Math.min(1,frame/Math.max(1,durationInFrames*.55)));
  const p=raw*raw*(3-2*raw);
  const points=from.map((point,index)=>interpolate(point,to[index]??point,p)).map(([x,y])=>`${x},${y}`).join(' ');
  const size=Math.max(60,Math.min(360,Number(effect.size??150)));
  return <svg viewBox="0 0 100 100" style={{
    filter:`drop-shadow(0 0 22px ${theme.accent}66)`,
    height:size,
    left:String(effect.left??'76%'),
    position:'absolute',
    top:String(effect.top??'18%'),
    transform:`translate(-50%,-50%) rotate(${(1-p)*-18}deg) scale(${.82+p*.18})`,
    width:size,
    zIndex:27,
  }}>
    <polygon fill={theme.accent} points={points}/>
  </svg>;
};
