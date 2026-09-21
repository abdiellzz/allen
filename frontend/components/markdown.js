// A deliberately small Markdown renderer. Raw HTML, images and links are text.
export const escapeHTML = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function inline(text){return escapeHTML(text).replace(/`([^`]+)`/g,'<code>$1</code>').replace(/\*\*([^*]+)\*\*/g,'<strong>$1</strong>');}
export function markdown(text){
 const lines=String(text).split('\n');let out='',code=null,list=false;
 const close=()=>{if(list){out+='</ul>';list=false;}};
 for(let i=0;i<lines.length;i++){
  const line=lines[i];
  if(line.startsWith('```')){close();if(code!==null){out+='<pre><code>'+escapeHTML(code.join('\n'))+'</code></pre>';code=null;}else code=[];continue;}
  if(code!==null){code.push(line);continue;}
  if(line.includes('|') && i+1<lines.length && /^\s*\|?[\s:|-]+\|/.test(lines[i+1])){
   close();const cells=l=>l.replace(/^\||\|$/g,'').split('|');
   out+='<table><thead><tr>'+cells(line).map(c=>'<th>'+inline(c.trim())+'</th>').join('')+'</tr></thead><tbody>';i++;
   while(i+1<lines.length&&lines[i+1].includes('|')){i++;out+='<tr>'+cells(lines[i]).map(c=>'<td>'+inline(c.trim())+'</td>').join('')+'</tr>';}
   out+='</tbody></table>';continue;
  }
  const heading=line.match(/^(#{1,3})\s+(.+)/);if(heading){close();out+=`<h${heading[1].length+1}>${inline(heading[2])}</h${heading[1].length+1}>`;continue;}
  const bullet=line.match(/^\s*(?:[-*]|\d+\.)\s+(.+)/);if(bullet){if(!list){out+='<ul>';list=true;}out+='<li>'+inline(bullet[1])+'</li>';continue;}
  close();if(line.trim())out+='<p>'+inline(line)+'</p>';
 }
 close();if(code!==null)out+='<pre><code>'+escapeHTML(code.join('\n'))+'</code></pre>';return out;
}
