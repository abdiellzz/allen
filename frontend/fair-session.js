// The visitor belongs to this tab. Aggregate counters never contain a name.
export const freshVisitor=()=>({visitorId:globalThis.crypto?.randomUUID?.()||`${Date.now()}-${Math.random().toString(36).slice(2)}`,name:'',difficulty:'Normal',currentExperience:'welcome',sessionStartedAt:null,score:0,level:1,rank:'Explorador',streak:0,activitiesCompleted:0,achievements:[],achievementIds:[],newAchievements:[],viewedAchievements:[],achievementDates:{},ready:false,rewards:[],completedLessons:[],assessments:{},routes:{},projects:{},metrics:{challenges:0,simulations:0,games:0,projects:0,routes:0},preAssessmentScore:null,postAssessmentScore:null,lastGameResult:null});
export function readVisitor(storage){
 try{const v=JSON.parse(storage.getItem('visitorSession'));if(v&&typeof v==='object'&&['Fácil','Normal','Difícil','Sorpréndeme'].includes(v.difficulty))return {...freshVisitor(),...v,projects:v.projects||{}};}catch{}
 return freshVisitor();
}
export function saveVisitor(storage,visitor){try{storage.setItem('visitorSession',JSON.stringify({...visitor,updatedAt:Date.now()}));}catch{}}
export function effectiveDifficulty(visitor){
 if(visitor.difficulty!=='Sorpréndeme')return visitor.difficulty;
 return visitor.score>=600?'Difícil':visitor.score>=200?'Normal':'Fácil';
}
export function rankFor(score,ranks){return [...ranks].reverse().find(r=>score>=r.min)||ranks[0];}
export function rankProgress(score,ranks){const rank=rankFor(score,ranks),index=ranks.indexOf(rank),next=ranks[index+1];return {rank,next,remaining:next?next.min-score:0,value:next?score-rank.min:1,max:next?next.min-rank.min:1};}
export function award(visitor,points,achievement,key=''){
 if(key&&visitor.rewards.includes(key))return false;
 if(key)visitor.rewards.push(key);
 visitor.score+=points;if(achievement&&!visitor.achievements.includes(achievement))visitor.achievements.push(achievement);
 return true;
}
export function markAchievementViewed(visitor,id){
 visitor.newAchievements=(visitor.newAchievements||[]).filter(item=>item!==id);
 if(!(visitor.viewedAchievements||[]).includes(id))visitor.viewedAchievements=[...(visitor.viewedAchievements||[]),id];
 return visitor;
}
export function buildSessionSummary(visitor,endedAt=Date.now(),routeNames=[]){
 const routeProgress=Object.entries(visitor.routes||{}).filter(([,state])=>state&&typeof state==='object'&&(state.modules?.length||state.challenge||state.project||state.complete)).map(([id,state])=>({id,name:routeNames.find(route=>route.id===id)?.name||id,modulesCompleted:state.modules?.length||0,challengeCompleted:!!state.challenge,projectCompleted:!!state.project,completed:!!state.complete}));
 const summary={visitorId:visitor.visitorId,userName:visitor.name||'',difficulty:visitor.difficulty,sessionStartedAt:visitor.sessionStartedAt||null,sessionEndedAt:endedAt,pointsEarned:visitor.score||0,activitiesCompleted:visitor.activitiesCompleted||0,gamesCompleted:visitor.metrics?.games||0,challengesCompleted:visitor.metrics?.challenges||0,projectsCompleted:visitor.metrics?.projects||0,simulationsCompleted:visitor.metrics?.simulations||0,routesCompleted:visitor.metrics?.routes||0,lessonsCompleted:visitor.completedLessons?.length||0,achievementsUnlocked:[...(visitor.achievements||[])],routeProgress,rank:visitor.rank||'',projectHistory:JSON.parse(JSON.stringify(visitor.projects||{})),routeHistory:JSON.parse(JSON.stringify(visitor.routes||{}))};
 if(visitor.sessionStartedAt&&endedAt>=visitor.sessionStartedAt)summary.durationSeconds=Math.floor((endedAt-visitor.sessionStartedAt)/1000);
 return summary;
}
export function saveSessionSummary(storage,summary){
 try{const history=JSON.parse(storage.getItem('allenSessionHistory')||'[]');if(!Array.isArray(history))return false;if(history.some(item=>item.visitorId===summary.visitorId))return true;history.push(summary);storage.setItem('allenSessionHistory',JSON.stringify(history));return true;}catch{return false;}
}
export function answerPoints(correct,attempts,hinted){return !correct?0:attempts>1?50:hinted?75:100;}
export function chooseQuestions(questions,category,difficulty,count,random=Math.random){
 const pool=[...new Map(questions.filter(q=>category==='Mixto'||q.category===category).map(q=>[q.question,q])).values()];
 const shuffled=pool.map(q=>({q,key:random()})).sort((a,b)=>a.key-b.key).map(x=>x.q);
 const matching=shuffled.filter(q=>q.difficulty===difficulty);
 // Never repeat questions just to make a longer round.
 const fallback=shuffled.filter(q=>q.difficulty!==difficulty).sort((a,b)=>{
  const order=difficulty==='Fácil'?['Normal','Difícil']:['Fácil','Normal','Difícil'];
  return order.indexOf(a.difficulty)-order.indexOf(b.difficulty);
 });
 return [...matching,...fallback].slice(0,count);
}
