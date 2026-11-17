#!/usr/bin/env python
"""ask_claude.py <x_prompt.md> <x_views.png> [photo1.jpg ...]  (OPTIONAL, needs an Anthropic API key; UNTESTED here, no network in the build sandbox)
A clean-room call by construction: every API request starts without any history. Writes <x>_interpretation.json.
Windows cmd (one line): pip install anthropic && set ANTHROPIC_API_KEY=sk-... && python ask_claude.py lego3_prompt.md lego3_views.png"""
import base64, json, mimetypes, os, sys
import anthropic
prompt_file, *imgs = sys.argv[1:]
content = []
for p in imgs:
    mt = mimetypes.guess_type(p)[0] or 'image/png'
    content.append({'type': 'image', 'source': {'type': 'base64', 'media_type': mt, 'data': base64.b64encode(open(p, 'rb').read()).decode()}})
content.append({'type': 'text', 'text': open(prompt_file, encoding='utf-8').read()})
model = os.environ.get('ANTHROPIC_MODEL', 'claude-sonnet-5-5')
msg = anthropic.Anthropic().messages.create(model=model, max_tokens=6000, messages=[{'role': 'user', 'content': content}])
txt = ''.join(b.text for b in msg.content if b.type == 'text'); d = json.loads(txt[txt.index('{'):txt.rindex('}') + 1])
d['interpreter']['model_id_self_reported'] = d['interpreter'].get('model_id_self_reported') or 'unknown'
out = prompt_file.replace('_prompt.md', '_interpretation.json'); json.dump(d, open(out, 'w', encoding='utf-8'), indent=2, ensure_ascii=False); print('wrote', out)
