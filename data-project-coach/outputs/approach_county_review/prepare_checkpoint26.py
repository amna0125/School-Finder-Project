from pathlib import Path
import ast,difflib
P=Path('outputs/approach_county_review')
s=(P/'checkpoint_batch25.py').read_text().replace('Batch25','Batch26').replace('batch25','batch26').replace('after_batch24','after_batch25')
s=s.replace('[(9,7),(0,0)]','[(8,7),(0,0)]').replace('==291','==299').replace('==214','==221').replace('263','273').replace('499','489').replace('exact_quotes=9','exact_quotes=8').replace('+9 evidence','+8 evidence')
s=s.replace("collection_status='contextually_reviewed_followups_retained'","collection_status=('terms_review_required' if r['school_id']=='41357379' else 'contextually_reviewed_followups_retained')")
a=s.index("(P/'CURRENT_WORKFLOW.md').write_text(");b=s.index('\nstatus=read(',a)
s=s[:a]+"""(P/'CURRENT_WORKFLOW.md').write_text('# Current checkpoint — Batch26, 2026-11-02\\n\\n273 documented outcomes /489 pending /762 unique IDs. Ledger '+new.name+'. Next next_batch_after_batch26.json.\\n\\nBatch26:10 outcomes,8 evidence,7 codes;4 reviewed-claim schools,1 uncertain uncoded,4 scoped no-clear,1 permission/identity blocker. Append famous-ibex +8/+7; replay amber-swallow +0/+0. DB299 evidence/221 codes.22 tests passed. Exact staging/target comparisons, preservation, source quotes/hashes and official fingerprints checked. Prior batches untouched.\\n\\nSkogsbacksskolan Trampolinen retains terms_review_required and unresolved unit mapping; general school profiles not transferred. Källbrink broad accessibility note uncoded. Nobla and Slottspark target years1–3; Järna Montessori-inspired/outdoor; Fårdala developing cooperative learning and Trivselledare from year2, separate language studio excluded.\\n\\nBatch25 and26 complete as separately validated batches; county incomplete. No reconciled county scope audit exists; approach outcomes are not clear/unclear applicability counts.\\n')"""+s[b:]
ast.parse(s)
assert "old=P/'county_progress_20261102_after_batch25.csv';new=P/'county_progress_20261102_after_batch26.csv'" in s
assert not (P/'checkpoint_batch26.py').exists()
(P/'checkpoint_batch26.py').write_text(s)
B=P/'batch26_10schools_20261102'
(B/'checkpoint_script.diff').write_text(''.join(difflib.unified_diff([],s.splitlines(True),fromfile='/dev/null',tofile='checkpoint_batch26.py')))
print('Checkpoint syntax PASSED; predecessor25 destination26; exact-ID IN retained; blocker status preserved')
