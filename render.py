"""Data-driven Korean infographic. Raises on text overflow instead of clipping."""
import json
import os
from pathlib import Path
from datetime import date
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent
S = 3
BLUE, RED, INK = '#00447e', '#c9272a', '#18222c'


def render(doc, output):
    day = date.fromisoformat(doc['date'])
    weekday = '월화수목금토일'[day.weekday()]
    im = Image.new('RGB', (922*S, 1382*S), '#edf8ff')
    draw = ImageDraw.Draw(im)
    fonts = [os.environ.get('KOREAN_FONT', ''), 'C:/Windows/Fonts/malgun.ttf',
             '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc']
    font_path = next((p for p in fonts if p and Path(p).exists()), None)
    if not font_path:
        raise ValueError('한글 폰트 설치 필요')

    def font(size):
        return ImageFont.truetype(font_path, round(size*S))

    def rect(box, fill, outline=None):
        draw.rectangle(tuple(round(v*S) for v in box), fill=fill, outline=outline, width=S)

    def text(x, y, value, size=14, color=INK, width=None):
        value = str(value)
        if width and draw.textlength(value, font=font(size)) > width*S:
            raise ValueError(f'가로 넘침: {value[:35]}')
        draw.text((x*S, y*S), value, font=font(size), fill=color, anchor='lt')

    def fit(x, y, value, size=16, color=INK, width=414):
        while size >= 10 and draw.textlength(str(value), font=font(size)) > width*S:
            size -= .5
        text(x, y, value, size, color, width)

    def wrap(x, y, values, width, bottom, size=14, step=21):
        for value in values:
            line = ''
            for c in str(value):
                if draw.textlength(line+c, font=font(size)) > width*S:
                    if y+size > bottom:
                        raise ValueError('세로 넘침')
                    text(x, y, line, size)
                    y += step
                    line = c
                else:
                    line += c
            if line:
                if y+size > bottom:
                    raise ValueError('세로 넘침')
                text(x, y, line, size)
                y += step
        return y

    def gradient(box, start=(1,43,95), end=(12,131,190)):
        x,y,w,h = box
        for i in range(h*S):
            t = i / max(1, h*S-1)
            rgb = tuple(round(a+(b-a)*t) for a,b in zip(start,end))
            draw.line((x*S,y*S+i,(x+w)*S,y*S+i), fill=rgb)

    def picture(name, x,y,w,h):
        path = ROOT/'assets'/f'{name}.jpg'
        if path.exists():
            pic = ImageOps.fit(Image.open(path).convert('RGB'), (w*S,h*S))
            im.paste(pic, (x*S,y*S))
            rect((x,y+h-13,x+w,y+h), '#243849')
            text(x+2,y+h-11,'참고 이미지',9,'white')

    def table(x,y,headers,rows,width=425):
        columns = len(headers)
        if columns < 2 or columns > 4 or len(rows) > 5:
            raise ValueError('표 크기 오류')
        cellw = width/columns
        for r,row in enumerate([headers]+rows):
            if len(row) != columns:
                raise ValueError('표 열 수 불일치')
            for c,value in enumerate(row):
                xx = x+c*cellw
                rect((xx,y+r*22,xx+cellw,y+(r+1)*22), '#e9f3f8' if r==0 else 'white', '#d9e5ee')
                fit(xx+4,y+r*22+5,value,12,BLUE if r==0 else INK,cellw-8)
        return y+22*(len(rows)+1)+6

    gradient((0,0,922,88), (0,15,49), (0,28,72))
    earth = ROOT/'assets'/'earth.jpg'
    if earth.exists():
        im.paste(ImageOps.fit(Image.open(earth).convert('RGB'),(145*S,61*S)),(546*S,0))
    fit(16,9,f'{day.month}/{day.day}({weekday}) Daily 뉴스 브리핑',40,'white',527)
    fit(16,59,'글로벌 경제·금융 이슈와 투자 인사이트',21,'#fff12b',527)
    text(700,10,f'{day:%Y. %m. %d} ({weekday})',14,'white',204)
    fit(700,35,'개인용 경제 브리핑',20,'white',204)
    fit(700,65,doc.get('checked_at','기준 시각 확인 필요'),10,'#d5eaff',204)
    # Original's fixed two-column grid: left 1–6, right 7–11.
    boxes = [(9,92,233),(9,328,201),(9,532,224),(9,759,208),(9,970,181),(9,1154,154),
             (466,92,165),(466,260,269),(466,532,217),(466,752,360),(466,1115,193)]
    for sec,(x,y,h) in zip(doc['sections'],boxes):
        n = sec['number']
        rect((x,y,x+447,y+h),'white','#b4dce9')
        gradient((x+2,y+2,443,31))
        rect((x+2,y+2,x+36,y+33),RED)
        text(x+8,y+5,n,22,'white')
        fit(x+46,y+9,sec['topic']+' · '+sec.get('title',''),17,'white',392)
        yy = y+41
        if n in (1,2,3,4,5,6,7,8,9):
            picture(str(n),x+8,yy,128,65)
            summary = sec.get('table')
            if summary:
                yy = table(x+145,yy,summary['headers'],summary['rows'],294)
            else:
                wrap(x+145,yy,[sec.get('status','확인 불가')],284,y+110,13,19)
                yy += 72
        if n == 10 and sec.get('positive') is not None:
            rect((x+8,yy,x+219,yy+98),'#f0fff5')
            rect((x+225,yy,x+439,yy+98),'#fff4f3')
            text(x+17,yy+5,'↑ 긍정 요인',18,'#277b43')
            text(x+234,yy+5,'↓ 부담 요인',18,RED)
            wrap(x+16,yy+32,sec['positive'],194,yy+95,12,19)
            wrap(x+232,yy+32,sec.get('negative',[]),194,yy+95,12,19)
            yy += 107
            gradient((x+8,yy,430,28),(226,217,254),(244,239,255))
            text(x+17,yy+5,'조건부 관찰 아이디어 3가지',17,'#5212b0')
            yy += 37
            ideas = sec.get('ideas',[])
            if len(ideas) != 3:
                raise ValueError('관찰 아이디어 3개 필요')
            for i,idea in enumerate(ideas,1):
                rect((x+12,yy,x+37,yy+24),'#5f12d3')
                text(x+18,yy+3,i,18,'white')
                wrap(x+48,yy,[idea],382,yy+46,13,20)
                yy += 48
        elif n == 11 and sec.get('table'):
            t = sec['table']
            yy = table(x+8,yy,t['headers'],t['rows'])
        else:
            yy = wrap(x+9,yy,['• '+v for v in sec.get('bullets',[])],425,y+h-39,13,19)
        fit(x+10,y+h-33,'▶ '+sec.get('impact','확인된 조건을 우선 관찰'),13,RED,424)
        fit(x+10,y+h-15,'출처 '+','.join(map(str,sec.get('source_ids',[])))+' · 정보 제공용',9,'#536171',424)
    rect((7,1313,915,1369),'white','#acddec')
    gradient((15,1320,40,40))
    text(24,1329,'↗',26,'white')
    fit(64,1331,'오늘의 한줄 코멘트',17,BLUE,179)
    wrap(251,1323,[doc.get('comment','확인된 자료와 조건을 기준으로 시장을 살펴봅니다.')],470,1368,13,21)
    text(742,1324,'사진: 원본 참고 이미지',10,'#566376',165)
    text(742,1344,'조건부 해석 · 정보 제공용',10,'#566376',165)
    rect((0,1373,922,1382),'#001b48')
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    im.save(output)
    return output


if __name__ == '__main__':
    import sys
    render(json.loads(Path(sys.argv[1]).read_text(encoding='utf-8')),sys.argv[2])
