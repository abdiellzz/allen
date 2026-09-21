import json
from pathlib import Path
from fractions import Fraction
import subprocess
import sys

import pytest

from allen_training.build_dataset import corpus,TARGETS,math_problem,ROOT
from allen_training.train import validate,split_groups,prepare,completion_examples,main

def test_training_corpus_distribution_and_reproducibility():
    records,metadata=corpus()
    actual,meta,report=validate(ROOT/'data/allen_dataset.jsonl',ROOT/'data/allen_metadata.jsonl')
    assert records==actual and metadata==meta
    assert report['examples']==2800 and report['by_area']==TARGETS
    assert report['duplicate_conversations']==0 and report['maximum_assistant_words']<=260
    assert report['human_approved']==0
    assert report['multiturn_conversations']>800

def test_user_examples_preserved():
    rows,metadata=corpus()
    examples=[r for r,m in zip(rows,metadata) if m['origin']=='ejemplo_aportado_por_usuario']
    assert len(examples)==3
    assert any(r['messages'][0]['content']=='¿Cuánto es 18 x 7?' for r in examples)
    assert any('caja con una etiqueta' in r['messages'][1]['content'] for r in examples)

def test_splits_keep_repeated_concept_groups_together(tmp_path):
    rows,metadata=corpus()
    train,evaluation=split_groups(rows,metadata)
    assert set(train).isdisjoint(evaluation)
    assert sorted(train+evaluation)==list(range(2800))
    assert {metadata[i]['group'] for i in train}.isdisjoint({metadata[i]['group'] for i in evaluation})
    assert {metadata[i]['area'] for i in evaluation}==set(TARGETS)
    info=prepare(rows,metadata,tmp_path/'split')
    assert info['shared_groups']==0 and info['train']+info['eval']==2800
    with pytest.raises(ValueError,match='ya contiene'):prepare(rows,metadata,tmp_path/'split')

def test_format_and_stale_metadata_are_rejected(tmp_path):
    dataset=tmp_path/'data.jsonl';meta=tmp_path/'metadata.jsonl'
    rows,metadata=corpus()
    dataset.write_text(json.dumps(rows[0])+'\n',encoding='utf-8')
    meta.write_text(json.dumps(metadata[0])+'\n',encoding='utf-8')
    validate(dataset,meta)
    changed=json.loads(json.dumps(rows[0]));changed['messages'][1]['content']='Cambio no registrado'
    dataset.write_text(json.dumps(changed)+'\n',encoding='utf-8')
    with pytest.raises(ValueError,match='metadatos desactualizados'):validate(dataset,meta)
    dataset.write_text('{broken\n',encoding='utf-8')
    with pytest.raises(ValueError,match='JSON no válido'):validate(dataset,meta)

def test_default_cli_does_not_load_training_dependencies():
    result=subprocess.run([sys.executable,str(ROOT/'train.py'),'--validate'],capture_output=True,text=True)
    assert result.returncode==0 and '2800' in result.stdout
    assert 'torch' not in result.stderr and 'trainer' not in result.stderr.lower()

def test_training_requires_local_model_and_review(tmp_path,capsys):
    assert main(['--train','--model',str(tmp_path/'missing')])==1
    assert 'carpeta local' in capsys.readouterr().err
    model=tmp_path/'model';model.mkdir()
    assert main(['--train','--model',str(model)])==1
    assert 'Falta revisión humana' in capsys.readouterr().err

def test_completion_conversion_masks_previous_turns_by_design():
    rows=[{'messages':[{'role':'user','content':'q1'},{'role':'assistant','content':'a1'},
                       {'role':'user','content':'q2'},{'role':'assistant','content':'a2'}]}]
    expanded=completion_examples(rows)
    assert len(expanded)==2
    assert [m['content'] for m in expanded[1]['prompt']]==['q1','a1','q2']
    assert expanded[1]['completion']==[{'role':'assistant','content':'a2'}]

def test_known_training_math_results():
    expected={'suma':5,'resta':3,'multiplicacion':6,'division':3,'fracciones_suma':Fraction(1,2),
              'fracciones_equivalentes':Fraction(1,3),'porcentaje':6,'descuento':45,'proporcion':12,
              'ecuacion':3,'algebra':11,'potencias':9,'perimetro':10,'area_rectangulo':6,
              'area_triangulo':6,'media':5,'mediana':5,'probabilidad':Fraction(1,3),'unidades':300,'enteros':-3}
    for family,value in expected.items():assert Fraction(math_problem(family,0)[1])==value

def test_summaries_are_shorter_than_source():
    rows,meta=corpus()
    for row,m in zip(rows,meta):
        if m['variant']=='resumen_apunte':
            assert len(row['messages'][1]['content'])<len(row['messages'][0]['content'].split('\n',1)[1])
