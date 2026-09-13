"""Verify CPU-only placement on the separate cloud-disabled CPU server at 11435."""
import json
import local_models as lm

lm.BASE = 'http://127.0.0.1:11435'
target = lm.OUT / 'verified-cpu.json'
assert not target.exists()
case = next(c for c in lm.load(lm.OUT/'corpus.json') if c['id']=='current/frozen/vague_job_user_script/4/14')
rows = []
for model in ('gemma3:4b', 'qwen3.5:4b'):
    lm.rpc('chat', {'model':model, 'messages':[], 'keep_alive':0, 'stream':False})
    for repeat in range(2):
        row = lm.infer(model, case, cpu=True, readable=model.startswith('qwen'))
        row.update(model=model, repeat=repeat)
        rows.append(row)
        target.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf8')
        assert row['placement']['models'] and all(m['size_vram']==0 for m in row['placement']['models']), 'CPU test used GPU memory'
        print(model, repeat, row['seconds'], flush=True)
    lm.rpc('chat', {'model':model, 'messages':[], 'keep_alive':0, 'stream':False})
