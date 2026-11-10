"""Portable PDF/HTML renderer for the Markdown manuscript; fonts supplied by matplotlib."""
from pathlib import Path
import argparse,html,re
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image,KeepTogether
from matplotlib.font_manager import findfont,FontProperties
from PIL import Image as PILImage

def inline(s):
    s=html.escape(s,quote=False)
    s=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',r'<link href="\2" color="#155d7a">\1</link>',s)
    s=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',s)
    s=re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)',r'<i>\1</i>',s)
    s=re.sub(r'`([^`]+)`',r'\1',s)
    return s

def build(source,pdfout):
    root=source.parent
    for fam,name in [('DejaVu Serif','Body'),('DejaVu Sans','Head')]:
        for suffix,weight,style in [('', 'normal','normal'),('-B','bold','normal'),('-I','normal','italic'),('-BI','bold','italic')]:
            pdfmetrics.registerFont(TTFont(name+suffix,findfont(FontProperties(family=fam,weight=weight,style=style))))
        pdfmetrics.registerFontFamily(name,normal=name,bold=name+'-B',italic=name+'-I',boldItalic=name+'-BI')
    body=ParagraphStyle('Body',fontName='Body',fontSize=10,leading=14.2,spaceAfter=8,textColor=colors.HexColor('#18232c'))
    title=ParagraphStyle('Title',fontName='Head-B',fontSize=17,leading=22,spaceAfter=15)
    h2=ParagraphStyle('H2',fontName='Head-B',fontSize=12,leading=16,spaceBefore=13,spaceAfter=8,keepWithNext=True)
    h3=ParagraphStyle('H3',fontName='Head-B',fontSize=10.5,leading=14,spaceBefore=10,spaceAfter=6,keepWithNext=True)
    cap=ParagraphStyle('Caption',parent=body,fontName='Head',fontSize=8.4,leading=11.5,spaceAfter=10)
    cell=ParagraphStyle('Cell',parent=cap,fontSize=8,leading=10.5,spaceAfter=0)
    headcell=ParagraphStyle('HeadCell',parent=cell,fontName='Head-B',textColor=colors.white)
    width=A4[0]-100
    doc=SimpleDocTemplate(str(pdfout),pagesize=A4,rightMargin=50,leftMargin=50,topMargin=49,bottomMargin=48,
      title='Configuration sensitivity and conditional reliability in wastewater inflow volume forecasting: a two-site open-data audit',author='Viet Nam Tran')
    lines=source.read_text(encoding='utf8').splitlines();story=[];web=[];j=0;pending_caption=None
    while j<len(lines):
        s=lines[j].strip()
        if not s:j+=1;continue
        if s.startswith('#'):
            level=len(s)-len(s.lstrip('#'));content=s[level:].strip();sty={1:title,2:h2}.get(level,h3)
            story.append(Paragraph(inline(content),sty));web.append(f'<h{level}>{inline(content)}</h{level}>');j+=1;continue
        if s.startswith('- '):
            story.append(Paragraph('• '+inline(s[2:]),body));web.append('<p>• '+inline(s[2:])+'</p>');j+=1;continue
        image_match=re.match(r'!\[([^]]*)\]\(([^)]+)\)',s)
        if image_match:
            path=root/image_match[2]
            with PILImage.open(path) as img:iw,ih=img.size
            fw=width;fh=fw*ih/iw
            if fh>310:fw*=310/fh;fh=310
            parts=[Spacer(1,5),Image(str(path),width=fw,height=fh)]
            j+=1
            while j<len(lines) and not lines[j].strip():j+=1
            if j<len(lines) and lines[j].startswith('**Figure'):
                parts.append(Spacer(1,6));parts.append(Paragraph(inline(lines[j]),cap));caption=inline(lines[j]);j+=1
            else:caption=''
            story.append(KeepTogether(parts));web.append(f'<figure><img src="{image_match[2]}" alt="{html.escape(image_match[1])}"><figcaption>{caption}</figcaption></figure>');continue
        if s.startswith('|'):
            rows=[]
            while j<len(lines) and lines[j].strip().startswith('|'):
                values=[v.strip() for v in lines[j].strip().strip('|').split('|')]
                if not all(re.fullmatch(r'[-: ]+',v) for v in values):rows.append(values)
                j+=1
            n=len(rows[0]);weights=[2]+[1]*(n-1)
            if n==6:weights=[1.25,1.1,.85,.85,.85,1.1]
            widths=[width*w/sum(weights) for w in weights]
            tbl=Table([[Paragraph(inline(v),headcell if k==0 else cell) for v in row] for k,row in enumerate(rows)],colWidths=widths,repeatRows=1,hAlign='LEFT')
            tbl.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#23566a')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
              ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
              ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#f0f4f6'),colors.white]),('LINEBELOW',(0,-1),(-1,-1),.6,colors.HexColor('#69818d'))]))
            story.append(KeepTogether(([pending_caption] if pending_caption else [])+[tbl,Spacer(1,10)]));pending_caption=None
            web.append('<table>'+''.join('<tr>'+''.join(f'<{"th" if k==0 else "td"}>{inline(v)}</{"th" if k==0 else "td"}>' for v in row)+'</tr>' for k,row in enumerate(rows))+'</table>');continue
        # Paragraphs in this source are separated by blank lines.
        pieces=[s];j+=1
        while j<len(lines) and lines[j].strip() and not lines[j].startswith(('#','|','![')):
            pieces.append(lines[j].strip());j+=1
        value=' '.join(pieces)
        if value.startswith('- '):value='• '+value[2:]
        sty=cap if value.startswith('**Table') else body
        para=Paragraph(inline(value),sty)
        if value.startswith('**Table'):pending_caption=para
        elif re.match(r'^\d+\. ',value):story.append(KeepTogether([para]))
        else:story.append(para)
        web.append('<p>'+inline(value)+'</p>')
    def page(canvas,doc):
        canvas.saveState();canvas.setFont('Head',7.5);canvas.setFillColor(colors.HexColor('#596975'))
        if doc.page>1:canvas.drawString(50,A4[1]-29,'Wastewater inflow forecasting | Two-site open-data audit')
        canvas.drawString(50,27,'Research manuscript v0.2.0 | 10 November 2026')
        canvas.drawRightString(A4[0]-50,27,str(doc.page));canvas.restoreState()
    doc.build(story,onFirstPage=page,onLaterPages=page)
    css='body{max-width:940px;margin:45px auto;padding:0 25px;font:17px/1.65 Georgia,serif;color:#18232c}h1,h2,h3,table,figcaption{font-family:Arial,sans-serif}h1{line-height:1.25}h2{margin-top:2em}a{color:#155d7a}table{width:100%;border-collapse:collapse;font-size:14px;margin:20px 0}td,th{padding:9px;border-bottom:1px solid #b8c5cc;text-align:left}th{background:#23566a;color:white}tr:nth-child(even){background:#f0f4f6}figure{margin:25px 0}img{max-width:100%}figcaption{font-size:14px} @media print{body{margin:0;font-size:11pt}figure,table{break-inside:avoid}}'
    # HTML uses normal anchors rather than ReportLab's link element.
    webtext='\n'.join(web).replace('<link ','<a ').replace('</link>','</a>')
    source.with_suffix('.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Wastewater inflow audit</title><style>'+css+'</style><body>'+webtext+'</body></html>',encoding='utf8')
    print(pdfout)

if __name__=='__main__':
    p=argparse.ArgumentParser();root=Path(__file__).parent;p.add_argument('--source',type=Path,default=root/'manuscript_FINAL.md');p.add_argument('--output',type=Path,default=root/'manuscript_FINAL.pdf');a=p.parse_args();build(a.source,a.output)
