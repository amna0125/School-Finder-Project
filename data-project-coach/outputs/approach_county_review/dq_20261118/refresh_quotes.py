"""Refresh quotes whose page was reworded or moved but still states the claim (live check 18 Nov 2026, browser-rendered)."""
import duckdb, csv
U = [  # evidence_id, url, title, new verbatim quote
 ('ae_b11_23414344_01','https://skolgrunden.se/','Aspdammskolan och Skolgrunden','Vi arbetar med små undervisningsgrupper och ett helhetsperspektiv på varje elev, där vi utgår från individuella förmågor och behov.'),
 ('ae_sr_93301103_01','https://skolgrunden.se/','Aspdammskolan och Skolgrunden','Aspdammskolan och Skolgrunden är två resursskolor med spetskompetens inom specialpedagogik som främst vänder sig till elever i årskurs 6–9 i behov av särskilt stöd.'),
 ('ae_b19_33733966_01','https://iskh.se/','International School of Kungsholmen | IB World School','The language of instruction at the International School of Kungsholmen is solely English, and we follow an international curriculum.'),
 ('ae_b19_33733966_02','https://iskh.se/primary-years-pyp','Primary Years Programme (PYP) | International School of Kungsholmen','These concepts encourage students to see the connections between content areas, and give them the skills to inquire more deeply into subject areas.'),
 ('ae_sr_52965560_01','https://vasainternationalschoolofstockholm.com/','Vasa International School of Stockholm | IB World School','Our bilingual programme follows the Swedish national curriculum (Lgr22) in combination with the International Baccalaureate framework, with teaching in both English and Swedish.'),
 ('ae_sr_79969356_01','https://europaskolan.nu/','Europaskolan — Bilingual IB World School on Södermalm','Europaskolan combines the Swedish national curriculum with the IB Primary Years and Middle Years Programmes, taught in both Swedish and English at our Södermalm campus.'),
 ('ae_sr_79969356_02','https://europaskolan.nu/','Europaskolan — Bilingual IB World School on Södermalm','A fee free, bilingual IB World School on Södermalm in Stockholm, with around 400 students and a maximum of 24 per class.'),
 ('ae_sr_84585645_01','https://hagaskolan.se/','Hagaskolan – Waldorfskolan i Norrort','Hagaskolan Waldorfskolan i Norrort'),
 ('ae_b02_11777750_01','https://www.nacka.se/valfard-skola/saltsjobadens-samskola-f9/','Saltsjöbadens Samskola F9 | Nacka kommun','Samskolan har ett aktivt Erasmussamarbete där vi erbjuder våra elever utbytesresor till olika länder i Europa, tar emot gäster ifrån våra partnerskolor samt möjliggör för fortbildning för våra lärare.'),
 ('ae_b06_16762245_01','https://www.edessaskolan.se/','Edessaskolan – Hem','Hos oss får eleverna inte bara en trygg, kunskapsrik och stimulerande skolgång utan också en möjlighet att fördjupa sig i ett kulturarv, i det arameiska språket och i orientalisk musik.'),
 ('ae_b06_16762245_02','https://www.edessaskolan.se/','Edessaskolan – Hem','På Edessaskolan har vi en tydlig profil med tvåspråkighet och musik i fokus.'),
 ('ae_sr_47705565_01','https://www.varmdo.se/barnochutbildning/skolbarn/alltomgrundskolan/grundskolorivarmdokommun/munkmoraskolan.4.2d09c46d1850f82301f90dc.html','Munkmoraskolan - Värmdö kommun','Vi arbetar långsiktigt och brett med hållbarhet i vardagen – framför allt genom vårt aktiva miljöarbete i Grön flagg samt vårt hälso- och rörelsefokus med Generation Pep.'),
 ('ae_sr_47705565_02','https://www.varmdo.se/barnochutbildning/skolbarn/alltomgrundskolan/grundskolorivarmdokommun/munkmoraskolan.4.2d09c46d1850f82301f90dc.html','Munkmoraskolan - Värmdö kommun','Vi arbetar långsiktigt och brett med hållbarhet i vardagen – framför allt genom vårt aktiva miljöarbete i Grön flagg samt vårt hälso- och rörelsefokus med Generation Pep.'),
]
con = duckdb.connect('/home/user/proj/.state/schools.duckdb'); log = []
for eid, url, title, q in U:
    old = con.execute('select source_url, quoted_text, accessed_date from Approach_evidence where evidence_id=?', [eid]).fetchone(); assert old, eid
    con.execute("update Approach_evidence set source_url=?, page_title=?, quoted_text=?, accessed_date='2026-11-18', interpretation_note=interpretation_note || ? where evidence_id=?",
                [url, title, q, f' | Quote refreshed 2026-11-18: page reworded or moved; claim still stated on the live page. Earlier quote ({old[2]}): {old[1][:160]}', eid])
    log.append(dict(evidence_id=eid, old_url=old[0], new_url=url, old_quote=old[1][:200], new_quote=q))
with open('quote_refresh_20261118.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(log[0])); w.writeheader(); w.writerows(log)
print(len(log), 'evidence rows refreshed')
