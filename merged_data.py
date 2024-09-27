import pandas as pd

# 투수 데이터 병합
# 각 CSV 파일을 읽어옵니다.
pitcher_df1 = pd.read_csv('pitcher_data.csv')
pitcher_df2 = pd.read_csv('pitcher_data1.csv')

# 'player_name'과 'team_name'을 기준으로 두 데이터프레임을 병합합니다.
# 'outer' 조인을 사용하여 모든 데이터를 포함하고, 공통된 선수에 대해서는 데이터를 결합합니다.
pitchers_merged = pd.merge(
    pitcher_df1,
    pitcher_df2,
    on=['선수명', '팀명', 'ERA'],
    how='inner',
    suffixes=('_data', '_data1')  # 동일한 컬럼명이 있을 경우 구분을 위해 접미사를 추가합니다.
)

# 필요에 따라 중복되거나 불필요한 컬럼을 정리합니다.
# 예: ranking 컬럼이 있다면 제거할 수 있습니다.
columns_to_drop = [col for col in pitchers_merged.columns if '순위' in col.lower()]
pitchers_merged = pitchers_merged.drop(columns=columns_to_drop)

# 정리된 투수 데이터를 새로운 CSV 파일로 저장합니다.
pitchers_merged.to_csv('pitchers_merged.csv', index=False)

print("투수 데이터가 성공적으로 병합되었습니다: 'pitchers_merged.csv'")

# 타자 데이터 병합
# 각 CSV 파일을 읽어옵니다.
hitter_df1 = pd.read_csv('hitter_data.csv')
hitter_df2 = pd.read_csv('hitter_data1.csv')

# 'player_name'과 'team_name'을 기준으로 두 데이터프레임을 병합합니다.
hitters_merged = pd.merge(
    hitter_df1,
    hitter_df2,
    on=['선수명', '팀명', 'AVG'],
    how='inner',
    suffixes=('_data', '_data1')  # 동일한 컬럼명이 있을 경우 구분을 위해 접미사를 추가합니다.
)

# 필요에 따라 중복되거나 불필요한 컬럼을 정리합니다.
columns_to_drop = [col for col in hitters_merged.columns if '순위' in col.lower()]
hitters_merged = hitters_merged.drop(columns=columns_to_drop)

# 정리된 타자 데이터를 새로운 CSV 파일로 저장합니다.
hitters_merged.to_csv('hitters_merged.csv', index=False)

print("타자 데이터가 성공적으로 병합되었습니다: 'hitters_merged.csv'")
