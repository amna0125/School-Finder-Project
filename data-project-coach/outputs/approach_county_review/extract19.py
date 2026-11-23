from html.parser import HTMLParser
import re,sys
from pathlib import Path
class Text(HTMLParser):
 def __init__(self):super().__init__();self.parts=[];self.skip=0;self.links=[]
 def handle_starttag(self,t,a):
  if t in ('script','style'):self.skip+=1
  if t=='a':self.links.extend(v for k,v in a if k=='href' and v)
 def handle_endtag(self,t):
  if t in ('script','style'):self.skip=max(0,self.skip-1)
 def handle_data(self,d):
  if not self.skip:self.parts.append(d)
def parse(p):
 t=Text();t.feed(Path(p).read_text());return re.sub(r'\s+',' ',' '.join(t.parts)).strip(),t.links
if __name__=='__main__':
 s,l=parse('outputs/approach_county_review/batch19_10schools_20261030/sources/'+sys.argv[1]+'.html');i=s.find(sys.argv[2]);print(s[i:i+int(sys.argv[3])]);print('LINKS', [u for u in l if any(k in u for k in ['pedagog','profil','om-skolan','var-skola','arbet','vision','verksamhet'])][:18])
