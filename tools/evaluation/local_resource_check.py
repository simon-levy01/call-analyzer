"""Local live-analysis latency alone, on CPU, and while Whisper uses the GPU."""
import argparse
import json
import subprocess
import threading
import time
import wave
import numpy as np
from local_models import OUT, ROOT, load, infer, rpc
from conversation_copilot import audio

p=argparse.ArgumentParser();p.add_argument('--model',required=True);p.add_argument('--compact',action='store_true');p.add_argument('--readable',action='store_true');p.add_argument('--brief',action='store_true');a=p.parse_args()
target=OUT/(a.model.replace(':','_')+'-resources'+('-compact' if a.compact else '')+('-readable' if a.readable else '')+('-brief' if a.brief else '')+'.json');assert not target.exists()
case=next(c for c in load(OUT/'corpus.json') if c['id']=='current/frozen/vague_job_user_script/4/14')
report={'model':a.model,'api_cost':0,'runs':[],'whisper_model':audio.MODEL_NAME,'whisper_options':audio.TRANSCRIBE_OPTIONS,'chunk_seconds':4,'interval_seconds':4}
def save():target.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
def gpu():return subprocess.check_output(['nvidia-smi','--query-gpu=name,memory.used,utilization.gpu,power.draw','--format=csv,noheader'],text=True).strip()
for mode in ('gpu_alone','cpu_only'):
    rpc('chat',{'model':a.model,'messages':[],'keep_alive':0,'stream':False})
    for repeat in range(2):
        row={'mode':mode,'repeat':repeat,'before':gpu()};report['runs'].append(row);save()
        try:row.update(infer(a.model,case,cpu=mode=='cpu_only',compact=a.compact,readable=a.readable,brief=a.brief))
        except Exception as e:row['error']=str(e)
        if mode=='cpu_only' and row.get('placement'):
            row['cpu_placement_verified']=all(m.get('size_vram',0)==0 for m in row['placement']['models'])
        row['after']=gpu();save();print(mode,repeat,row.get('seconds',row.get('error')),flush=True)
rpc('chat',{'model':a.model,'messages':[],'keep_alive':0,'stream':False})
audio.prepare_transcription_runtime()
whisper=audio._load_local_model()
report['whisper_device']=whisper.model.device
manifest=load(ROOT/'conversation_copilot/assets/f04/basic-video-chat.json')
wav=ROOT/'conversation_copilot/assets/f04'/manifest['assets']['contact_audio']['file']
with wave.open(str(wav),'rb') as f:
    samples=np.frombuffer(f.readframes(f.getnframes()),dtype=np.int16).astype(np.float32)/32768
stop=threading.Event();report['transcription_chunks']=[]
def transcribe():
    i=0
    while not stop.is_set():
        start=time.perf_counter();offset=(i*4*16000)%max(1,len(samples)-4*16000)
        try:
            segments,_=whisper.transcribe(samples[offset:offset+4*16000],language='en',**audio.TRANSCRIBE_OPTIONS)
            text=' '.join(s.text for s in segments)
            report['transcription_chunks'].append({'seconds':time.perf_counter()-start,'text':text,'offset_samples':offset})
        except Exception as e:report['transcription_error']=str(e);break
        i+=1;stop.wait(max(0,4-(time.perf_counter()-start)))
worker=threading.Thread(target=transcribe);worker.start()
try:
    for repeat in range(3):
        row={'mode':'gpu_with_whisper','repeat':repeat,'before':gpu()};report['runs'].append(row);save()
        try:row.update(infer(a.model,case,compact=a.compact,readable=a.readable,brief=a.brief))
        except Exception as e:row['error']=str(e)
        row['after']=gpu();save();print('gpu_with_whisper',repeat,row.get('seconds',row.get('error')),flush=True)
finally:stop.set();worker.join();report['complete']=True;save()
