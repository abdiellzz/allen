let token='';
export function setToken(value){token=value;}
async function localFetch(path,options){
 try{return await fetch(path,options);}catch(error){if(error.name==='AbortError')throw error;throw new Error('No pudimos conectar con Allen. Revisa que la aplicación esté iniciada y vuelve a intentarlo.');}
}
async function readJSON(response){try{return await response.json();}catch{throw new Error('Allen no pudo leer esta respuesta. Recarga la aplicación e inténtalo de nuevo.');}}
export async function api(path,method='GET',body){
 const response=await localFetch('/api'+path,{method,headers:{'Content-Type':'application/json','X-Allen-Token':token},body:body===undefined?undefined:JSON.stringify(body)});
 const data=await readJSON(response);if(!response.ok){if(data.license_required)window.dispatchEvent(new CustomEvent('allen-license-required'));if(data.teacher_auth_required)window.dispatchEvent(new CustomEvent('allen-teacher-auth-required'));throw new Error(data.error||'No pudimos completar esta acción.');}return data;
}
export async function streamChat(body,signal,onEvent){
 const response=await localFetch('/api/chat?stream=true',{method:'POST',headers:{'Content-Type':'application/json','X-Allen-Token':token},body:JSON.stringify(body),signal});
 if(!response.ok){const data=await readJSON(response);throw new Error(data.error||'No pudimos conectar con Allen.');}
 const reader=response.body.getReader(),decoder=new TextDecoder();let pending='';
 try{while(true){const {value,done}=await reader.read();pending+=decoder.decode(value,{stream:!done});let end;
  while((end=pending.indexOf('\n'))>=0){const line=pending.slice(0,end);pending=pending.slice(end+1);if(line.trim()){let event;try{event=JSON.parse(line);}catch{throw new Error('La respuesta se interrumpió. Inténtalo de nuevo.');}onEvent(event);}}if(done)break;}
 }catch(error){if(error.name==='TypeError')throw new Error('La conexión con Allen se interrumpió. Inténtalo de nuevo.');throw error;
 }finally{reader.releaseLock();}
}
