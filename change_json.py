import pandas as pd
import json
import re

# 파일 경로 설정
hitters_csv = 'hitters_merged.csv'
pitchers_csv = 'pitchers_merged.csv'

# 타자 열 매핑
hitters_column_mapping = {
    '순위': '순위',
    '선수명': '선수',
    '팀명': '팀명',
    'AVG': '타율',
    'G': '경기 수',
    'PA': '타석',
    'AB': '타수',
    'R': '득점',
    'H': '안타',
    '2B': '2루타',
    '3B': '3루타',
    'HR': '홈런',
    'TB': '루타',
    'RBI': '타점',
    'SAC': '희생 번트',
    'SF': '희생 플라이',
    'BB': '볼넷',
    'IBB': '고의4구',
    'HBP': '사구',
    'SO': '삼진',
    'GDP': '병살타',
    'SLG': '장타율',
    'OBP': '출루율',
    'OPS': 'OPS',
    'MH': '멀티히트',
    'RISP': '득점권 타율',
    'PH-BA': '대타 타율'
}

# 투수 열 매핑
pitchers_column_mapping = {
    '순위': '순위',
    '선수명': '선수',
    '팀명': '팀명',
    'ERA': '방어율',
    'G': '경기수',
    'W': '승',
    'L': '패',
    'SV': '세이브',
    'HLD': '홀드',
    'WPCT': '승률',
    'IP': '이닝',
    'H': '피안타',
    'HR': '피홈런',
    'BB': '볼넷',
    'HBP': '사구',
    'SO': '삼진',
    'R': '실점',
    'ER': '자책점',
    'WHIP': 'WHIP',
    'CG': '완투',
    'SHO': '완봉',
    'QS': '퀄리티스타트',
    'BSV': '블론세이브',
    'TBF': '타자수',
    'NP': '투구수',
    'AVG': '피안타율',
    '2B': '2루타',
    '3B': '3루타',
    'SAC': '희생번트',
    'SF': '희생플라이',
    'IBB': '고의사구',
    'WP': '폭투',
    'BK': '보크'
    # 추가적인 투수 기록이 있다면 여기에 추가
}

def parse_inning(inning_str):
    """
    이닝 문자열을 float으로 변환합니다.
    'x y/3' 형식을 x + y*0.1으로 변환합니다.
    '-' 또는 비어 있는 값은 None으로 반환합니다.
    """
    if pd.isna(inning_str) or inning_str.strip() == '-':
        return None
    match = re.match(r'(\d+)\s+(\d)/3', inning_str)
    if match:
        whole = int(match.group(1))
        fraction = int(match.group(2))
        return whole + fraction * 0.1
    else:
        # 만약 'x' 형식이면 그냥 float으로 변환
        try:
            return float(inning_str)
        except ValueError:
            return None

def process_players(csv_file, column_mapping, role):
    """
    CSV 파일을 읽고, 열 매핑을 적용하여 JSON 형식으로 변환합니다.
    role: '타자' 또는 '투수'
    """
    df = pd.read_csv(csv_file)
    df = df.rename(columns={'선수명': '선수'})
    
    # 필요한 열만 선택하고 매핑 적용
    df = df.rename(columns=column_mapping)
    
    players_json = []
    for _, row in df.iterrows():
        try:
            # 기록 딕셔너리 생성
            기록 = {}
            for mapped_col in column_mapping.values():
                if mapped_col not in ['순위', '선수', '팀명']:
                    value = row[mapped_col]
                    
                    # '이닝' 필드 특별 처리
                    if mapped_col == '이닝':
                        기록[mapped_col] = parse_inning(value)
                        continue
                    
                    # 데이터 타입에 맞게 변환
                    if mapped_col in ['순위']:
                        기록[mapped_col] = int(value) if not pd.isna(value) else None
                    elif mapped_col in ['타율', '장타율', '출루율', 'OPS', '득점권 타율', '대타 타율', '피안타율', '승률']:
                        기록[mapped_col] = round(float(value), 4) if not pd.isna(value) else None
                    elif mapped_col in ['이닝']:
                        기록[mapped_col] = float(value) if not pd.isna(value) else None
                    elif mapped_col in ['방어율', 'WHIP']:
                        기록[mapped_col] = round(float(value), 3) if not pd.isna(value) else None
                    else:
                        기록[mapped_col] = int(value) if not pd.isna(value) else None
            
            player = {
                "선수": row['선수'],
                "팀명": row['팀명'],
                "기록": 기록,
                "역할": role
            }
            players_json.append(player)
        except Exception as e:
            print(f"{role} 데이터 변환 오류 (선수: {row.get('선수', 'Unknown')}): {e}")
    return players_json

def main():
    # 타자 데이터 처리
    hitters_json = process_players(hitters_csv, hitters_column_mapping, "타자")
    
    # 투수 데이터 처리
    pitchers_json = process_players(pitchers_csv, pitchers_column_mapping, "투수")
    
    # 두 데이터를 합침
    combined_json = hitters_json + pitchers_json
    
    # JSON 파일로 저장
    output_json_file = 'kbo_players_2024_combined.json'
    with open(output_json_file, 'w', encoding='utf-8') as f:
        json.dump(combined_json, f, ensure_ascii=False, indent=4)
    
    print(f"JSON 파일이 성공적으로 저장되었습니다: {output_json_file}")

if __name__ == "__main__":
    main()
