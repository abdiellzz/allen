import {icon} from './ui.js';
import {AllenPose} from './fair-mascot.js';
import {escapeHTML as esc} from './markdown.js';

export function AchievementCard(achievement,{state='unlocked',date=''}={}){
 const label={locked:'Por descubrir',unlocked:'Desbloqueado',new:'Nuevo'}[state]||'Desbloqueado';
 return `<article class="achievement-card achievement-${state}"><span class="achievement-icon">${icon(achievement.icon||'trophy',24)}</span><div><strong>${esc(achievement.name)}</strong><p>${esc(achievement.description||'Sigue aprendiendo con Allen para descubrir este logro.')}</p><div class="achievement-meta">${Number(achievement.points)>0?`<span>+${Number(achievement.points)} puntos</span>`:''}${date?`<time>${esc(date)}</time>`:''}<span>${label}</span></div></div>${state==='new'?'<span class="achievement-new">NUEVO</span>':''}</article>`;
}

export function AchievementModal(achievement,{score=0,ranks=[],date=''}={}){
 const rank=ranks.length?[...ranks].reverse().find(item=>score>=item.min)||ranks[0]:null,next=rank?ranks[ranks.indexOf(rank)+1]:null;
 const progress=rank?(next?{value:score-rank.min,max:next.min-rank.min}: {value:1,max:1}):null;
 return `<div class="achievement-modal-content">${AllenPose('achievement','medium')}<span class="eyebrow">LOGRO DESBLOQUEADO</span><h2 id="achievement-title">${esc(achievement.name)}</h2><p>${esc(achievement.description||'Cada paso que das cuenta. Sigue aprendiendo con Allen.')}</p>${Number(achievement.points)>0?`<strong class="achievement-points">+${Number(achievement.points)} puntos</strong>`:''}${date?`<time>${esc(date)}</time>`:''}${rank?`<section class="achievement-rank"><strong>${esc(rank.name)}</strong><progress value="${progress.value}" max="${progress.max}" aria-label="Progreso de rango"></progress><small>${score.toLocaleString('es')} puntos${next?` · ${next.min.toLocaleString('es')} para el siguiente rango`: ' · rango máximo'}</small></section>`:''}<button class="primary" data-achievement-close>Continuar</button></div>`;
}
