from pathlib import Path
import pytest
from start_local_ai import command

def config(tmp_path):
    exe=tmp_path/'llama-server.exe';exe.touch()
    model=tmp_path/'modelo con espacios.gguf';model.touch()
    return {'executable':str(exe),'model':str(model)}

def test_model_path_is_single_argument(tmp_path):
    value=config(tmp_path);args=command(value,{'context_size':8192})
    assert args[args.index('-m')+1]==value['model']
    assert args[args.index('--host')+1]=='127.0.0.1'
    assert args[args.index('-c')+1]=='8192'
    assert '--log-disable' in args

def test_launcher_external_address_rejected(tmp_path):
    with pytest.raises(ValueError):command(config(tmp_path),{'ai_server':'http://example.com:8080'})

def test_launcher_wrong_executable_rejected(tmp_path):
    value=config(tmp_path);other=tmp_path/'cmd.exe';other.touch();value['executable']=str(other)
    with pytest.raises(ValueError):command(value,{})
