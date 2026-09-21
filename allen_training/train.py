"""Validate by default. Preparing data and LoRA training require explicit flags."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import os
from pathlib import Path
import random
import sys

ROOT=Path(__file__).resolve().parent

def read_jsonl(path):
    rows=[]
    with Path(path).open(encoding='utf-8') as handle:
        for number,line in enumerate(handle,1):
            if not line.strip():raise ValueError(f'{path.name}, línea {number}: línea vacía.')
            try:rows.append(json.loads(line))
            except json.JSONDecodeError as exc:raise ValueError(f'{path.name}, línea {number}: JSON no válido.') from exc
    return rows

def digest(record):
    return hashlib.sha256(json.dumps(record,ensure_ascii=False,sort_keys=True).encode('utf-8')).hexdigest()

def validate(dataset,metadata):
    rows=read_jsonl(dataset);meta=read_jsonl(metadata)
    if not rows or len(rows)!=len(meta):raise ValueError('Dataset y metadatos deben contener la misma cantidad de líneas, mayor que cero.')
    seen=set();areas=Counter();groups=set();assistant_texts=Counter();max_words=0;multiturn=0;reviewed=0
    for number,(row,m) in enumerate(zip(rows,meta),1):
        if not isinstance(row,dict) or set(row)!={'messages'}:raise ValueError(f'Línea {number}: se requiere únicamente el campo messages.')
        turns=row['messages']
        if not isinstance(turns,list) or len(turns)<2 or len(turns)%2:raise ValueError(f'Línea {number}: se esperan pares user/assistant completos.')
        for i,turn in enumerate(turns):
            if not isinstance(turn,dict) or set(turn)!={'role','content'}:raise ValueError(f'Línea {number}: mensaje no válido.')
            if turn['role']!=('user' if i%2==0 else 'assistant'):raise ValueError(f'Línea {number}: roles desordenados.')
            text=turn['content']
            if not isinstance(text,str) or not text.strip() or len(text)>6000:raise ValueError(f'Línea {number}: contenido vacío o demasiado largo.')
            if '\ufffd' in text or '\x00' in text:raise ValueError(f'Línea {number}: carácter de codificación no válido.')
            if i%2:
                words=len(text.split());max_words=max(max_words,words)
                if words>260:raise ValueError(f'Línea {number}: respuesta de más de 260 palabras; revisa su extensión.')
                assistant_texts[text]+=1
        h=digest(row)
        if h in seen:raise ValueError(f'Línea {number}: conversación duplicada.')
        seen.add(h)
        if not isinstance(m,dict) or m.get('sha256')!=h or m.get('id')!=h[:16]:raise ValueError(f'Línea {number}: metadatos desactualizados; revisa el hash.')
        for key in ['area','topic','group','variant','origin']:
            if not isinstance(m.get(key),str) or not m[key]:raise ValueError(f'Línea {number}: falta metadato {key}.')
        if m.get('human_review') not in ('pending','approved','rejected'):raise ValueError(f'Línea {number}: estado de revisión no válido.')
        if m['human_review']=='approved':reviewed+=1
        groups.add(m['group']);areas[m['area']]+=1;multiturn+=len(turns)>2
    report={'examples':len(rows),'by_area':dict(sorted(areas.items())),'concept_groups':len(groups),
            'multiturn_conversations':multiturn,'duplicate_conversations':0,'unique_assistant_messages':len(assistant_texts),
            'total_assistant_messages':sum(assistant_texts.values()),'maximum_assistant_words':max_words,
            'human_approved':reviewed,'human_pending':sum(m['human_review']=='pending' for m in meta),
            'human_rejected':sum(m['human_review']=='rejected' for m in meta),
            'dataset_sha256':hashlib.sha256(Path(dataset).read_bytes()).hexdigest(),
            'status':'valid_format_not_a_pedagogical_certification'}
    return rows,meta,report

def split_groups(rows,metadata,seed=42,fraction=0.1):
    if not 0<fraction<0.5:raise ValueError('La fracción de evaluación debe ser mayor que 0 y menor que 0.5.')
    groups=defaultdict(list)
    for i,m in enumerate(metadata):groups[m['group']].append(i)
    if len(groups)<2:raise ValueError('Se necesitan al menos dos grupos conceptuales para separar datos.')
    totals=Counter(m['area'] for m in metadata)
    target={a:max(1,round(n*fraction)) for a,n in totals.items()}
    chosen=set();counts=Counter();names=sorted(groups);random.Random(seed).shuffle(names)
    for name in names:
        additions=Counter(metadata[i]['area'] for i in groups[name])
        before=sum(abs(counts[a]-target[a]) for a in target)
        after=sum(abs(counts[a]+additions[a]-target[a]) for a in target)
        if after<before and all(counts[a]+additions[a]<totals[a] for a in additions):
            chosen.add(name);counts.update(additions)
    if not chosen:raise ValueError('No se pudo crear evaluación independiente con estos grupos.')
    train=[i for i,m in enumerate(metadata) if m['group'] not in chosen]
    evaluation=[i for i,m in enumerate(metadata) if m['group'] in chosen]
    return train,evaluation

def prepare(rows,meta,destination,seed=42):
    train,evaluation=split_groups(rows,meta,seed)
    destination=Path(destination)
    if destination.exists() and any(destination.iterdir()):raise ValueError('La carpeta de splits ya contiene archivos. Usa otra para conservar las revisiones anteriores.')
    destination.mkdir(parents=True,exist_ok=True)
    for name,indices in [('train',train),('eval',evaluation)]:
        (destination/f'{name}.jsonl').write_text(''.join(json.dumps(rows[i],ensure_ascii=False)+'\n' for i in indices),encoding='utf-8')
        (destination/f'{name}_metadata.jsonl').write_text(''.join(json.dumps(meta[i],ensure_ascii=False)+'\n' for i in indices),encoding='utf-8')
    info={'seed':seed,'train':len(train),'eval':len(evaluation),
          'train_by_area':dict(Counter(meta[i]['area'] for i in train)),
          'eval_by_area':dict(Counter(meta[i]['area'] for i in evaluation)),
          'shared_groups':len({meta[i]['group'] for i in train}&{meta[i]['group'] for i in evaluation})}
    (destination/'manifest.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return info

def completion_examples(rows):
    """One prompt/completion per assistant turn, without training on user text."""
    output=[]
    for row in rows:
        for i in range(1,len(row['messages']),2):
            output.append({'prompt':row['messages'][:i],'completion':[row['messages'][i]]})
    return output

def run_training(args,rows,meta):
    if not args.model or not args.model.is_dir():raise ValueError('--model debe ser una carpeta local de un modelo Transformers, no un GGUF ni un identificador remoto.')
    if args.output.exists() and any(args.output.iterdir()):raise ValueError('La carpeta de salida ya contiene archivos. Usa una nueva para no sobrescribir un entrenamiento.')
    if any(m['human_review']=='rejected' for m in meta):raise ValueError('Hay ejemplos rechazados. Retíralos del dataset antes de entrenar.')
    if not args.allow_unreviewed and any(m['human_review']!='approved' for m in meta):
        raise ValueError('Falta revisión humana. Revisa TRAINING_RULES.md. Para un experimento con datos sintéticos sin aprobar existe --allow-unreviewed; no certifica su calidad.')
    # Environment is set before importing any Hugging Face dependency.
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_DATASETS_OFFLINE='1',HF_HUB_DISABLE_TELEMETRY='1',WANDB_DISABLED='true')
    try:
        import torch
        from datasets import Dataset
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from peft import LoraConfig
        from trl import SFTConfig,SFTTrainer
    except ImportError as exc:
        raise ValueError('Faltan dependencias opcionales de entrenamiento. Consulta allen_training/README.md; no se instalan al ejecutar Allen.') from exc
    if not torch.cuda.is_available() and not args.allow_cpu:
        raise ValueError('No se detecta CUDA. El entrenamiento no comenzó. --allow-cpu permite un experimento lento si conoces los requisitos de memoria.')
    use_bf16=torch.cuda.is_available() and torch.cuda.is_bf16_supported()
    dtype=torch.bfloat16 if use_bf16 else torch.float32
    tokenizer=AutoTokenizer.from_pretrained(str(args.model),local_files_only=True,trust_remote_code=False)
    if not tokenizer.chat_template:raise ValueError('El tokenizer necesita una plantilla de chat compatible. No se inventará una para este modelo.')
    if tokenizer.eos_token is None:raise ValueError('El tokenizer debe tener un token de fin de secuencia configurado.')
    if tokenizer.pad_token is None:tokenizer.pad_token=tokenizer.eos_token
    train_indices,eval_indices=split_groups(rows,meta,args.seed)
    train_rows=completion_examples([rows[i] for i in train_indices])
    eval_rows=completion_examples([rows[i] for i in eval_indices])
    # Refuse silent truncation: a discarded completion would corrupt supervision.
    for row in train_rows+eval_rows:
        length=len(tokenizer.apply_chat_template(row['prompt']+row['completion'],tokenize=True,add_generation_prompt=False))
        if length>args.max_length:raise ValueError('Hay ejemplos que superan --max-length con este tokenizer. Ajusta el límite o revisa los ejemplos antes de entrenar.')
    model=AutoModelForCausalLM.from_pretrained(str(args.model),local_files_only=True,trust_remote_code=False,torch_dtype=dtype)
    model.config.use_cache=False
    config=SFTConfig(output_dir=str(args.output),num_train_epochs=args.epochs,max_length=args.max_length,
                     per_device_train_batch_size=1,per_device_eval_batch_size=1,gradient_accumulation_steps=8,
                     learning_rate=1e-4,gradient_checkpointing=True,gradient_checkpointing_kwargs={'use_reentrant':False},
                     bf16=use_bf16,fp16=False,use_cpu=not torch.cuda.is_available(),report_to='none',push_to_hub=False,
                     eval_strategy='epoch',save_strategy='epoch',save_total_limit=2,logging_steps=10,
                     seed=args.seed,data_seed=args.seed,dataloader_num_workers=0,packing=False,
                     completion_only_loss=True,assistant_only_loss=False)
    trainer=SFTTrainer(model=model,args=config,train_dataset=Dataset.from_list(train_rows),eval_dataset=Dataset.from_list(eval_rows),
                       processing_class=tokenizer,peft_config=LoraConfig(r=8,lora_alpha=16,lora_dropout=0.05,
                       target_modules='all-linear',bias='none',task_type='CAUSAL_LM'))
    trainer.train()
    trainer.save_model(str(args.output));tokenizer.save_pretrained(str(args.output))
    print('Adaptador LoRA guardado. No se ha convertido a GGUF ni conectado automáticamente a Allen.')

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset',type=Path,default=ROOT/'data/allen_dataset.jsonl')
    parser.add_argument('--metadata',type=Path,default=ROOT/'data/allen_metadata.jsonl')
    modes=parser.add_mutually_exclusive_group()
    modes.add_argument('--validate',action='store_true',help='Validar sin entrenar (predeterminado).')
    modes.add_argument('--prepare',action='store_true',help='Crear splits agrupados, sin entrenar.')
    modes.add_argument('--train',action='store_true',help='Iniciar SFT LoRA explícitamente.')
    parser.add_argument('--split-dir',type=Path,default=ROOT/'data/splits')
    parser.add_argument('--report',type=Path)
    parser.add_argument('--model',type=Path)
    parser.add_argument('--output',type=Path,default=ROOT/'output/allen-lora')
    parser.add_argument('--seed',type=int,default=42)
    parser.add_argument('--epochs',type=float,default=1)
    parser.add_argument('--max-length',type=int,default=2048)
    parser.add_argument('--allow-unreviewed',action='store_true')
    parser.add_argument('--allow-cpu',action='store_true')
    args=parser.parse_args(argv)
    try:
        if not 0<args.epochs<=20 or not 128<=args.max_length<=32768:raise ValueError('Revisa epochs (0–20) y max-length (128–32768).')
        rows,meta,report=validate(args.dataset,args.metadata)
        if args.report:
            if args.report.resolve() in {args.dataset.resolve(),args.metadata.resolve()}:raise ValueError('El informe no puede sobrescribir el dataset ni sus metadatos.')
            args.report.parent.mkdir(parents=True,exist_ok=True)
            args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(report,ensure_ascii=False,indent=2))
        if args.prepare:print(json.dumps(prepare(rows,meta,args.split_dir,args.seed),ensure_ascii=False,indent=2))
        if args.train:run_training(args,rows,meta)
        return 0
    except (ValueError,OSError) as exc:
        print(f'No se completó la operación: {exc}',file=sys.stderr)
        return 1

if __name__=='__main__':
    raise SystemExit(main())
