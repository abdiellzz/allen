// Finite, deterministic exercises: answers and feedback share the same parameters.
// Variant identifiers remain resolvable in old attempts and exported backups.
export function variantsFor(q,index=0) {
 if(q.kind==='diagnostic')return [];
 return [1,2,3].map(v=>{
  const seed=v+(index%3)*3,a=seed+1,b=2*seed+3,n=seed+2,k=v+2;
  let item={...q,id:`${q.id}~v${v}`,baseId:q.id};
  if(q.topicId==='parts'){
   const scene=['un mosaico','una bandeja','un huerto'][(v+q.id.length)%3];
   item={...item,prompt:`Divides ${scene} en ${b} partes iguales y completas ${a}. ¿Qué fracción completaste?`,options:[`${a}/${b}`,`${b}/${a}`,`${b-a}/${b}`],answer:`${a}/${b}`,hints:['El numerador cuenta las partes completadas.','El denominador cuenta todas las partes iguales.'],feedback:`Completaste ${a} de ${b} partes: ${a}/${b}. Quedan ${b-a}/${b}; invertir los números cambia el significado.`};
  }else if(q.topicId==='equivalent'){
   item={...item,prompt:`Una receta usa ${a}/${b} de taza. Si divides cada parte en ${k}, ¿qué medida equivale?`,options:[`${a*k}/${b*k}`,`${a}/${b*k}`,`${a*k}/${b}`],answer:`${a*k}/${b*k}`,hints:['La cantidad debe permanecer igual.','Multiplica numerador y denominador por el mismo número.'],feedback:`${a}/${b} = ${a*k}/${b*k}. Multiplicamos ambos números por ${k}; cambiar solo uno cambia la cantidad.`};
  }else if(q.topicId==='sum'){
   item={...item,prompt:`Avanzas ${a}/${b} de una ruta y después 1/${b}. ¿Qué fracción recorriste?`,options:[`${a+1}/${b}`,`${a+1}/${b*2}`,`${a}/${b}`],answer:`${a+1}/${b}`,hints:['Las partes tienen el mismo tamaño.','Suma las partes recorridas y conserva el denominador.'],feedback:`${a}/${b} + 1/${b} = ${a+1}/${b}. El tamaño de las partes no cambió; no sumamos los denominadores.`};
  }else if(q.topicId==='fraction-compare'){
   item={...item,prompt:`Dos vasos iguales tienen ${a}/${b} y 1/${b} de agua. ¿Cuál contiene más?`,options:[`${a}/${b}`,`1/${b}`,'Son iguales'],answer:`${a}/${b}`,hints:['Ambas cantidades cuentan partes del mismo tamaño.','Compara los numeradores.'],feedback:`${a}/${b} es mayor: ${a} partes son más que una, y todas tienen el mismo tamaño.`};
  }else if(q.topicId==='fraction-unlike'){
   item={...item,prompt:`Una mezcla lleva 1/${n} de litro y otra 1/${n*2}. ¿Cuánto hay en total?`,options:[`3/${n*2}`,`2/${n*3}`,`2/${n*2}`],answer:`3/${n*2}`,hints:['Convierte ambas cantidades a partes del mismo tamaño.',`1/${n} equivale a 2/${n*2}.`],feedback:`1/${n} + 1/${n*2} = 2/${n*2} + 1/${n*2} = 3/${n*2} de litro.`};
  }else if(q.topicId==='fraction-amount'){
   const total=b*k;
   item={...item,prompt:`Hay ${total} libros y ${a}/${b} son cuentos. ¿Cuántos cuentos hay?`,options:[String(a*k),String(k),String(total-a*k)],answer:String(a*k),hints:['Divide el total por el denominador.','Multiplica la cantidad de cada parte por el numerador.'],feedback:`${total} ÷ ${b} = ${k} libros por parte; ${k} × ${a} = ${a*k} cuentos.`};
  }
  // Rotate all courses' choices; the answer remains a value, never a position.
  const offset=(v+q.id.length)%item.options.length;
  return {...item,options:[...item.options.slice(offset),...item.options.slice(0,offset)]};
 });
}
