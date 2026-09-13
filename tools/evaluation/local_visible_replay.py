"""Use the existing real Tk replay/monitor with local-only model calls and no review inference."""
import argparse
import json
import runpy
import socket
import sys
import threading
import time
from pathlib import Path

from local_models import ROOT, OUT, infer
from conversation_copilot import guidance, interpretation, memory, ask_memory

parser=argparse.ArgumentParser();parser.add_argument('--model',required=True);parser.add_argument('--smoke',action='store_true');parser.add_argument('--compact',action='store_true');parser.add_argument('--readable',action='store_true');parser.add_argument('--brief',action='store_true');args=parser.parse_args()
target=OUT/(args.model.replace(':','_')+'-visible-model'+('-compact' if args.compact else '')+('-readable' if args.readable else '')+('-brief' if args.brief else '')+'.jsonl')
lock=threading.Lock()
def local_request(schema,payload,instructions,**kw):
    if schema is not guidance.GuidanceOutput:
        raise RuntimeError('Post-call/Ask inference intentionally excluded from this live-only replay')
    started=time.time()
    result=infer(args.model,{'schema':schema.__name__,'request':{'input':json.dumps(payload,ensure_ascii=False),
        'instructions':instructions,'max_output_tokens':kw['output_limit']}},compact=args.compact,readable=args.readable,brief=args.brief)
    with lock:
        with target.open('a',encoding='utf8') as f:f.write(json.dumps({'started':started,**result},ensure_ascii=False)+'\n')
    if result.get('validation_error'):raise ValueError(result['validation_error'])
    return schema.model_validate(result['raw']),None
for module in (guidance,interpretation,memory,ask_memory):module.f06_structured_request=local_request
# Fail closed if any application code attempts a non-loopback network connection.
connect=socket.socket.connect
def local_connect(sock,address):
    if isinstance(address,tuple) and address[0] not in ('127.0.0.1','::1','localhost'):
        raise RuntimeError('External network disabled during local replay')
    return connect(sock,address)
socket.socket.connect=local_connect

source=(ROOT/'build/replay_logged_call_ui.py').read_text(encoding='utf8')
start=source.index("spend=ROOT/'build/f06-paid-spend.json'")
end=source.index('# Preserve recorded aggregate visual/vocal evidence',start)
source=source[:start]+"def persist():\n (folder/'cost.json').write_text(json.dumps({'replay_dollars':0,'method':'local only'}))\n"+source[end:]
# No post-call calls: the baseline review is already measured and is cheap/nonrecurring.
source=source.replace("ui['stop']()", "cells['start_review_job'].cell_contents=lambda *a,**k:None\n   ui['stop']()\n   (folder/'complete.json').write_text(json.dumps({'live_replay_complete':True,'post_call':'skipped','model':LOCAL_MODEL}))\n   root.after(20000,root.destroy)")
source=source.replace("root.title('Conversation Copilot — RECORDED CALL REPLAY — TEST LOGGING ON')", "root.title('Conversation Copilot — LOCAL '+LOCAL_MODEL+' — RECORDED REPLAY')\n for widget in ui['interpretation_frame'].winfo_children():\n  if isinstance(widget,tk.Label) and widget.cget('text').startswith('Live guidance:'):\n   widget.configure(text='Live guidance: local '+LOCAL_MODEL+' (test override)')\n ui['terra_controls'].pack_forget()")
source=source.replace("'model':'gpt-5.6-terra','reasoning':'low'", "'model':LOCAL_MODEL,'reasoning':'local think disabled'")
source=source.replace("root.after(15000,begin)","root.after(1500,begin)")
source=source.replace("Recorded call replay starts in 15 seconds;", "LOCAL replay starts in 1.5 seconds;")
source=source.replace("Replay finished — generating a general summary and specific memory proposals. Results stay in the test database.","Local live replay finished. Post-call inference skipped; no API charges.")
source=source.replace("SMOKE='--smoke-test' in sys.argv","SMOKE=LOCAL_SMOKE")
monitor=(ROOT/'build/f06_monitor_test.py').read_text(encoding='utf8')
expected="expected_live_model='gpt-5.6-terra', expected_reasoning='low'"
assert expected in monitor
monitor=monitor.replace(expected,"expected_live_model=LOCAL_MODEL, expected_reasoning='local think disabled'")
source=source.replace("runpy.run_path(str(ROOT/'build/f06_monitor_test.py'),run_name='__main__')",
    "exec(compile(LOCAL_MONITOR, 'local-monitor', 'exec'), {'__name__':'__main__','__file__':str(ROOT/'build/f06_monitor_test.py'),'LOCAL_MODEL':LOCAL_MODEL})")
scope={'__name__':'__main__','__file__':str(ROOT/'build/replay_logged_call_ui.py'),'LOCAL_MODEL':args.model,'LOCAL_SMOKE':args.smoke,'LOCAL_MONITOR':monitor}
sys.argv=[sys.argv[0]]
exec(compile(source,'local-visible-replay','exec'),scope)
