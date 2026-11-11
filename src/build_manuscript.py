"""Create the submission DOCX from the canonical Markdown and saved figures.
python src/build_manuscript.py          (requires requirements-docs.txt)
python src/build_manuscript.py --pdf    (also renders paper/manuscript.pdf with LibreOffice, if installed)
"""
from pathlib import Path
import argparse, datetime, re, json, zipfile, hashlib, shutil, subprocess, tempfile
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT
ROOT=Path(__file__).resolve().parents[1]

MINUS=re.compile(r'(?<![\w.])-(?=\d)')
def minus(s):return MINUS.sub('\u2212',s)

def inline(p,text):
    parts=re.split(r'(\*\*.*?\*\*|\*[^*]+\*|\[[^]]+\]\([^)]+\)|`[^`]+`)',text)
    for s in parts:
        if not s:continue
        link=re.fullmatch(r'\[([^]]+)\]\(([^)]+)\)',s)
        if link:
            label,url=link.groups();h=OxmlElement('w:hyperlink');h.set(qn('r:id'),p.part.relate_to(url,RT.HYPERLINK,is_external=True))
            r=OxmlElement('w:r');pr=OxmlElement('w:rPr');color=OxmlElement('w:color');color.set(qn('w:val'),'000000');pr.append(color);r.append(pr)
            t=OxmlElement('w:t');t.text=label;r.append(t);h.append(r);p._p.append(h)
        else:
            bold=s.startswith('**');italic=s.startswith('*') and not bold;code=s.startswith('`')
            value=s[2:-2] if bold else s[1:-1] if italic or code else s
            run=p.add_run(minus(value));run.bold=bold;run.italic=italic

def math_run(text):
    r=OxmlElement('m:r');t=OxmlElement('m:t');t.text=text;r.append(t);return r

def target_equation(p):
    # Native Office Math n-ary sum, with editable lower and upper limits.
    para=OxmlElement('m:oMathPara');eq=OxmlElement('m:oMath');eq.append(math_run('V(t,h) = '))
    nary=OxmlElement('m:nary');props=OxmlElement('m:naryPr');char=OxmlElement('m:chr');char.set(qn('m:val'),'∑');props.append(char)
    loc=OxmlElement('m:limLoc');loc.set(qn('m:val'),'undOvr');props.append(loc);nary.append(props)
    for tag,val in [('m:sub','k=1'),('m:sup','h'),('m:e','Q(t+k) Δt')]:
        node=OxmlElement(tag);node.append(math_run(val));nary.append(node)
    eq.append(nary);eq.append(math_run(',  Δt = 1 hour.'));para.append(eq);p._p.append(para)
    p.alignment=WD_ALIGN_PARAGRAPH.CENTER

def border(parent,tag,sides):
    node=OxmlElement(tag)
    for side,(val,size,color) in sides.items():
        b=OxmlElement('w:'+side);b.set(qn('w:val'),val)
        if val!='nil':b.set(qn('w:sz'),str(size));b.set(qn('w:space'),'0');b.set(qn('w:color'),color)
        node.append(b)
    parent.append(node)

def table(doc,rows,align):
    """Three-line academic table: rules above/below the header and at the bottom, no vertical lines.
    Every row is kept with the next one so a table is not split across pages, and the header repeats if it must."""
    n=len(rows[0]);t=doc.add_table(rows=0,cols=n);t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
    lengths=[max(len(r[j]) for r in rows) for j in range(n)]
    raw=[max(l,6)+2.5 for l in lengths];total=6.8;widths=[total*x/sum(raw) for x in raw]
    tblPr=t._tbl.tblPr
    border(tblPr,'w:tblBorders',{'top':('single',12,'000000'),'left':('nil',0,''),'bottom':('single',12,'000000'),
                                'right':('nil',0,''),'insideH':('nil',0,''),'insideV':('nil',0,'')})
    mar=OxmlElement('w:tblCellMar')
    for side,v in [('top',35),('left',85),('bottom',35),('right',85)]:
        x=OxmlElement('w:'+side);x.set(qn('w:w'),str(v));x.set(qn('w:type'),'dxa');mar.append(x)
    tblPr.append(mar)
    for col,w in zip(t.columns,widths):col.width=Inches(w)
    for i,row in enumerate(rows):
        cells=t.add_row().cells;trPr=t.rows[-1]._tr.get_or_add_trPr()
        trPr.append(OxmlElement('w:cantSplit'))
        if i==0:trPr.append(OxmlElement('w:tblHeader'))
        group_start=i>1 and row[0].strip()!='' and rows[i-1][0].strip()==''
        for j,(c,value,w) in enumerate(zip(cells,row,widths)):
            c.width=Inches(w);c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            if i==0:border(c._tc.get_or_add_tcPr(),'w:tcBorders',{'bottom':('single',6,'000000')})
            elif group_start:border(c._tc.get_or_add_tcPr(),'w:tcBorders',{'top':('single',4,'808080')})
            q=c.paragraphs[0];f=q.paragraph_format;f.space_before=Pt(0);f.space_after=Pt(0);f.line_spacing=1.0;f.keep_with_next=True
            q.alignment=WD_ALIGN_PARAGRAPH.RIGHT if align[j]=='right' else WD_ALIGN_PARAGRAPH.LEFT
            run=q.add_run(minus(value));run.font.size=Pt(9);run.bold=i==0

def build(pdf=False):
    source=ROOT/'paper/manuscript.md';lines=source.read_text(encoding='utf8').splitlines();doc=Document()
    sec=doc.sections[0];sec.page_width=Inches(8.5);sec.page_height=Inches(11)
    sec.left_margin=sec.right_margin=Inches(.85);sec.top_margin=sec.bottom_margin=Inches(.75)
    sec.header_distance=sec.footer_distance=Inches(.3)
    for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Heading 3','Caption','List Bullet']:
        style=doc.styles[name];style.font.name='Times New Roman';style.font.color.rgb=RGBColor(0,0,0)
        style.font.size=Pt(11)
    body=doc.styles['Normal'];body.paragraph_format.line_spacing=1.12;body.paragraph_format.space_after=Pt(6)
    for name,size in [('Title',17),('Heading 1',13),('Heading 2',11.5)]:
        st=doc.styles[name];st.font.size=Pt(size);st.font.bold=True;st.paragraph_format.keep_with_next=True;st.paragraph_format.space_before=Pt(12);st.paragraph_format.space_after=Pt(6)
    doc.styles['Caption'].font.size=Pt(9.5)
    head=sec.header.paragraphs[0];head.text='WASTEWATER INFLOW FORECASTING  |  TWO-SITE AUDIT';head.runs[0].font.size=Pt(8)
    footer=sec.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.RIGHT
    r=footer.add_run();field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');r._r.addnext(field)
    i=0;paragraphs=0
    while i<len(lines):
        line=lines[i].strip();i+=1
        if not line:continue
        if line.startswith('|'):
            rows=[[c.strip() for c in line.strip('|').split('|')]];align=['left']*len(rows[0])
            while i<len(lines) and lines[i].startswith('|'):
                cells=[c.strip() for c in lines[i].strip('|').split('|')];i+=1
                if all(re.fullmatch(r':?-+:?',c) for c in cells):align=['right' if c.endswith(':') else 'left' for c in cells]
                else:rows.append(cells)
            table(doc,rows,align);continue
        if line.startswith('*Note.*'):
            p=doc.add_paragraph(style='Caption');inline(p,line);f=p.paragraph_format
            f.space_before=Pt(3);f.space_after=Pt(12);f.line_spacing=1.0
            for r in p.runs:r.font.size=Pt(8.5)
            continue
        if line.startswith('!['):
            target=re.search(r'\]\(([^)]+)\)',line).group(1)
            p=doc.add_paragraph();p.paragraph_format.keep_with_next=True;p.alignment=WD_ALIGN_PARAGRAPH.CENTER
            run=p.add_run();shape=run.add_picture(str(source.parent/target),width=Inches(6.65));shape._inline.docPr.set('descr',line.split(']')[0][2:]);continue
        if line.startswith('**V(t,h)'):
            target_equation(doc.add_paragraph());continue
        if line.startswith('# '):p=doc.add_paragraph(style='Title');inline(p,line[2:]);continue
        if line.startswith('## '):p=doc.add_paragraph(style='Heading 1');inline(p,line[3:]);continue
        if line.startswith('### '):p=doc.add_paragraph(style='Heading 2');inline(p,line[4:]);continue
        if line.startswith('- '):p=doc.add_paragraph(style='List Bullet');inline(p,line[2:]);continue
        caption=line.startswith('**Table ') or line.startswith('**Figure ')
        p=doc.add_paragraph(style='Caption' if caption else 'Normal');inline(p,line);paragraphs+=1
        if line.startswith('**Table '):
            f=p.paragraph_format;f.keep_with_next=True;f.space_before=Pt(10);f.space_after=Pt(4);f.line_spacing=1.0
        if re.match(r'^\d+\. [A-ZÀ-ž]',line):p.paragraph_format.keep_together=True
    doc.core_properties.author='Viet Nam Tran';doc.core_properties.last_modified_by='Viet Nam Tran';doc.core_properties.comments='';doc.core_properties.created=doc.core_properties.modified=datetime.datetime(2026,11,11);doc.core_properties.title=lines[0][2:];doc.core_properties.subject='Two-site retrospective computational research'
    doc.core_properties.keywords='wastewater inflow; forecasting; open science; reproducibility'
    output=ROOT/'paper/manuscript.docx';doc.save(output)
    assert len(doc.tables)==4 and len(doc.inline_shapes)==5
    with zipfile.ZipFile(output) as z:
        xml=z.read('word/document.xml').decode('utf8');assert xml.count('<m:oMath>')==1
    meta={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'docx_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'tables':4,'figures':5,'native_equations':1,'author':'Viet Nam Tran'}
    if pdf:
        office=shutil.which('soffice') or shutil.which('libreoffice')
        if not office:raise SystemExit('--pdf needs LibreOffice (soffice) on PATH')
        with tempfile.TemporaryDirectory() as d:
            subprocess.run([office,'--headless','--convert-to','pdf','--outdir',d,str(output)],check=True,capture_output=True)
            shutil.copyfile(Path(d)/'manuscript.pdf',ROOT/'paper/manuscript.pdf')
        version=subprocess.run([office,'--version'],capture_output=True,text=True).stdout.strip()
        meta.update({'pdf_sha256':hashlib.sha256((ROOT/'paper/manuscript.pdf').read_bytes()).hexdigest(),
                     'pdf_renderer':version,'pdf_note':'Convenience rendering of manuscript.docx; the DOCX is the review document.'})
    (ROOT/'verification').mkdir(exist_ok=True);(ROOT/'verification'/'manuscript_build.json').write_text(json.dumps(meta,indent=2));print(json.dumps(meta,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--pdf',action='store_true');build(ap.parse_args().pdf)
