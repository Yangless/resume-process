import re
import dateparser
from datetime import datetime

# 你提供的函数（略作整理）
def extract_dates_comprehensive(text):
    chinese_patterns = [
        r'\d{4}\s*年\s*\d{1,2}\s*月\s*(\d{1,2}\s*日)?(?!\d)',
        r'\d{4}\s*年\s*\d{1,2}\s*月\s*(\d{1,2}\s*号)?(?!\d)',
        r'\b\d{2}\s*年\s*\d{1,2}\s*月\s*(\d{1,2}\s*[日,号])?(?!\d)',
        r'\d{4}\s*-\s*\d{1,2}(\s*-\d{1,2})?(?!\d)',
        r'\d{4}\s*/\s*\d{1,2}\s*/?\s*\d{0,2}(?!\d)',
        r'\d{1,2}\s*-\s*\d{1,2}\s*-\s*\d{4}',
        r'\d{4}\s*/\s*\d{1,2}(?<!-)$',
        r'\b\d{4}\s*[/.]\s*\d{1,2}\s*-\s*\d{1,2}(?!\d)',
        r'\d{4}\s*\.\s*\d{1,2}(\s*\.\s*\d{1,2})?(?!\d)'
    ]

    found_dates = []
    try:
        for pattern in chinese_patterns:
            for match in re.finditer(pattern, text):
                matches = match.group()
                start = match.start()
                end = match.end()

                # 特殊处理
                if pattern == r'\d{2}年\d{1,2}月\d{0,2}[日,号]?':
                    matches = '20' + matches
                elif pattern == r'\b\d{4}[/.]\d{1,2}-\d{1,2}(?!\d)':
                    match_ = re.findall(r'(\d{4}[/.])\d{1,2}-(\d{1,2})', matches)
                    if match_:
                        matches = ''.join(match_[0])

                found_dates.append([matches, start, end])
    except Exception as e:
        print(e)
    return found_dates

def normalize_dates_in_text(text):
    dates = extract_dates_comprehensive(text)
    year=0
    for date_str, start, end in sorted(dates, key=lambda x: -x[1]):
        try:
            parsed_date = dateparser.parse(date_str.replace(' ',''))
            if parsed_date:
                normalized = parsed_date.strftime('%Y年%m月%d日')
                year=max(year,int(parsed_date.year))
                #if parsed_date.year>1950:
                    #text = text[:start] + normalized + text[end:]
        except Exception as e:
            print(f"Error parsing date: {date_str}, error: {e}")
            return 0
    return year

#t="2025/6-2026/7"
#print(normalize_dates_in_text(t))
#print(dateparser.parse(value.replace(' ','')).strftime('%Y年%m月%d日'))
