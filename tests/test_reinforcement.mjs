import test from 'node:test';
import assert from 'node:assert/strict';
import {courses,allTopics,questionById} from '../public/mobile/course.mjs';
import {newState,startSession,advance,submitAnswer,requestHelp,recommendation} from '../public/mobile/engine.mjs';
import {exportBackup,parseBackup,validateState} from '../public/mobile/storage.mjs';
import {correctAnswer,feedbackFor} from '../public/mobile/activities.mjs';
import {newDraft,draftAnswer,visualExplanation} from '../public/mobile/activity-ui.mjs';
const fresh=()=>({...newState({id:crypto.randomUUID(),name:'Ana',goal:'school',level:'bases',minutes:5}),revision:1});
function finish(s){if(s.session.phase==='lesson')advance(s);while(s.session.phase==='practice'){const q=questionById(s.session.questionIds[s.session.index]);submitAnswer(s,q.answer);advance(s);}}
test('all 56 modules have complete content and earlier prerequisites within their course',()=>{
 assert.equal(allTopics.length,143);assert.equal(new Set(allTopics.map(t=>t.id)).size,143);
 for(const c of courses){assert.equal(new Set(c.topics.map(t=>t.module)).size,4);for(const [i,t]of c.topics.entries()){assert.ok(t.explanation&&t.example&&t.alternative);if(t.prerequisite)assert.ok(c.topics.slice(0,i).some(p=>p.id===t.prerequisite));assert.equal(t.questions.filter(q=>q.kind==='check').length,1);}}
});
test('interactive answers obey deterministic rules, preserve wrong attempts and reject forged grades',()=>{
 const s=fresh();startSession(s,'diagnostic');finish(s);startSession(s,'learn','parts');finish(s);startSession(s,'learn','math-decimal');advance(s);
 const q=questionById(s.session.questionIds[0]);assert.equal(q.activity,'input');assert.equal(correctAnswer(q,' 0,25 '),true);assert.equal(correctAnswer(q,'1/4'),false);assert.equal(correctAnswer(q,'0.250'),true);
 const help=requestHelp(s,'simple');assert.ok(help.text.includes(q.prompt));assert.equal(s.session.answers.length,0);
 submitAnswer(s,'0,25');const copy=parseBackup(exportBackup(s));assert.equal(copy.session.answers[0].correct,true);assert.match(recommendation(copy).reason,/Estábamos practicando/);
 const forged=structuredClone(copy);forged.session.answers[0].correct=false;assert.throws(()=>validateState(forged));
 advance(copy);const match=questionById(copy.session.questionIds[1]),draft=newDraft(match);draft.matches=match.pairs.map(p=>p[1]);assert.equal(correctAnswer(match,draftAnswer(match,draft)),true);draft.matches.reverse();assert.equal(correctAnswer(match,draftAnswer(match,draft)),false);
 submitAnswer(copy,match.answer);advance(copy);const check=questionById(copy.session.questionIds[2]);assert.match(feedbackFor(check,'0.07').text,/centésimas/);submitAnswer(copy,'0.07');advance(copy);assert.ok(!copy.completed.includes('math-decimal'));validateState(copy);
});
test('ordering can be corrected without revealing grades; prepared visual code explains state',()=>{
 const q=questionById('math-decimal-add-0'),draft=newDraft(q);assert.equal(correctAnswer(q,draftAnswer(q,draft)),false);draft.order=[...q.steps];assert.equal(correctAnswer(q,draftAnswer(q,draft)),true);
 const html=visualExplanation(allTopics.find(t=>t.id==='python-arithmetic'));assert.match(html,/visual-step/);assert.match(html,/14/);
});
