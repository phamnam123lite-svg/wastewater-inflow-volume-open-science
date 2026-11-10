from pathlib import Path
import re,html
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image,PageBreak,KeepTogether
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_JUSTIFY
P=Path(__file__).resolve().parents[1];source=(P/'paper/manuscript.md').read_text(encoding='utf8')
pdfmetrics.registerFont(TTFont('Body','C:/Windows/Fonts/times.ttf'))
pdfmetrics.registerFont(TTFont('BodyBold','C:/Windows/Fonts/timesbd.ttf'))
pdfmetrics.registerFont(TTFont('BodyItalic','C:/Windows/Fonts/timesi.ttf'))
pdfmetrics.registerFontFamily('Body',normal='Body',bold='BodyBold',italic='BodyItalic',boldItalic='BodyBold')
st=getSampleStyleSheet()
st.add(ParagraphStyle(name='Text',fontName='Body',fontSize=11,leading=14.5,spaceAfter=7,alignment=TA_JUSTIFY))
st.add(ParagraphStyle(name='CellText',fontName='Body',fontSize=8.3,leading=10.5))
for name,size in [('Title',17),('Heading1',13),('Heading2',11.5)]:
 st[name].fontName='BodyBold';st[name].fontSize=size;st[name].leading=size+3;st[name].textColor=colors.black;st[name].keepWithNext=True
def inline(s):
 s=html.escape(s)
 s=re.sub(r'\[([^\]]+)\]\((https?[^)]+)\)',r'<link href="\2" color="#174c7b">\1</link>',s)
 s=re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',s);s=re.sub(r'\*(.*?)\*',r'<i>\1</i>',s);s=re.sub(r'`(.*?)`',r'\1',s)
 return s
story=[];lines=source.splitlines();i=0
while i<len(lines):
 line=lines[i].strip();i+=1
 if not line:continue
 if line=='## Figure captions':break
 if line.startswith('\\['):
  while i<len(lines) and not lines[i].startswith('\\]'):i+=1
  i+=1;story.append(Paragraph('V(t,h) = sum of Q(t+k) × Δt for k = 1,...,h; Δt = 1 hour.',st['Text']));continue
 if line.startswith('|'):
  rows=[line]
  while i<len(lines) and lines[i].startswith('|'):rows.append(lines[i]);i+=1
  cells=[[Paragraph(inline(c.strip()),st['CellText']) for c in row.strip('|').split('|')] for row in rows if not re.match(r'^\|[\s:|\-]+\|$',row)]
  cols=len(cells[0]);widths=([170]+[(463-170)/(cols-1)]*(cols-1)) if cols==5 else [130,70]+[65.75]*4
  table=Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT')
  table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e9edf1')),('LINEBELOW',(0,0),(-1,0),.6,colors.black),('BOTTOMPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6)]))
  story.extend([table,Spacer(1,10)]);continue
 if line.startswith('# '):story.append(Paragraph(inline(line[2:]),st['Title']))
 elif line.startswith('### '):story.append(Paragraph(inline(line[4:]),st['Heading2']))
 elif line.startswith('## '):story.append(Paragraph(inline(line[3:]),st['Heading1']))
 else:story.append(Paragraph(inline(line[2:] if line.startswith('- ') else line),st['Text']))
captions=source.split('## Figure captions')[1].strip().split('\n\n')
figs=sorted((P/'figures').glob('*.png')) if (P/'figures').exists() else sorted((P/'research/figures').glob('*.png'))
for f,cap in zip(figs,captions):
 story.append(PageBreak());im=Image(str(f));ratio=im.imageHeight/im.imageWidth;im.drawWidth=463;im.drawHeight=463*ratio
 story.extend([im,Spacer(1,14),Paragraph(inline(cap.split(' File:')[0]),st['Text'])])
def footer(c,doc):
 c.setFont('Body',9);c.drawRightString(529,30,str(doc.page))
doc=SimpleDocTemplate(str(P/'paper/manuscript.pdf'),pagesize=(595.28,841.89),rightMargin=66,leftMargin=66,topMargin=48,bottomMargin=48,title=source.splitlines()[0][2:],author='Viet Nam Tran')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print('Created manuscript PDF')
