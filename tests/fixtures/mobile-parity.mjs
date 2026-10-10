// Called by the Python parity test. No browser needed.
import {computeMastery,recommendForState} from '../../public/mobile/engine.mjs';
let input='';for await(const chunk of process.stdin)input+=chunk;
const {cases,now}=JSON.parse(input);
process.stdout.write(JSON.stringify(cases.map(c=>{const m=computeMastery(c,new Date(now));return {mastery:m,recommendation:recommendForState({mastery_score:m.score,status:m.status,topic:'Fracciones'})};})));
