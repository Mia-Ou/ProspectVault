import re

with open('_app/template.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace secs array: only keep reportSec(r) and ivSecHTML(r)
old_secs_pattern = re.compile(
    r'  const secs=\[\s*\n'
    r'    reportSec\(r\),\s*\n'
    r'    reqSec\(r\),\s*\n'
    r'    textSec\([^\)]+\),\s*\n'
    r'    textSec\([^\)]+\),\s*\n'
    r'    textSec\([^\)]+\),\s*\n'
    r'    textSec\([^\)]+\),\s*\n'
    r'    listSec\([^\)]+\),\s*\n'
    r'    listSec\([^\)]+\),\s*\n'
    r'    listSec\([^\)]+\),\s*\n'
    r'    listSec\([^\)]+\),\s*\n'
    r'    linkSec\([^\)]+\),\s*\n'
    r'    ivSecHTML\(r\)\s*\n'
    r'  \];',
    re.DOTALL
)

new_secs = """  const secs=[
    reportSec(r),
    ivSecHTML(r)
  ];"""

if old_secs_pattern.search(content):
    content = old_secs_pattern.sub(new_secs, content)
    print('OK: replaced secs array')
else:
    print('WARN: secs pattern not found, trying manual match')
    # try to find it
    idx = content.find('const secs=[')
    if idx >= 0:
        # find the closing ];
        end = content.find('];', idx)
        if end >= 0:
            block = content[idx:end+2]
            print(f'Found block ({len(block)} chars):')
            print(repr(block[:300]))

# 2. Remove old functions: textSec, listSec, linkSec, reqSec, buildReqObj, rsGenReq, rsCopyOut, rsDownloadReq, rsCloseOut, rsImportResult, rsCloseIn, decodeMaybe, rsApplyResult, rsCopyReq
# These are all between reqSec and ivSecHTML (the reqSec block)
# Find the start of reqSec and end of rsCopyReq function

req_start = content.find('\nfunction reqSec(r){')
if req_start >= 0:
    # Find the next function after rsCopyReq (which is ivSecHTML)
    rs_copy_req_end = content.find('\nfunction ivSecHTML(r){', req_start)
    if rs_copy_req_end >= 0:
        # Also remove textSec, listSec, linkSec functions which are after the secs block
        # Find textSec start
        textsec_start = content.find('\nfunction textSec(', req_start)
        if textsec_start >= 0:
            # Remove from reqSec to just before ivSecHTML
            removed = content[req_start:rs_copy_req_end]
            content = content[:req_start] + content[rs_copy_req_end:]
            print(f'OK: removed old functions ({len(removed)} chars: reqSec, textSec, listSec, linkSec, rs* helpers)')
        else:
            print('WARN: textSec not found after reqSec')
    else:
        print('WARN: ivSecHTML not found after reqSec')
else:
    print('WARN: reqSec function not found (already removed?)')

with open('_app/template.html', 'w', encoding='utf-8') as f:
    f.write(content)
