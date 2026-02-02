import json
import os
import sys
import matplotlib.pyplot as plt
from collections import Counter

def plot_clone_distribution(file_path):
    if not os.path.exists(file_path):
        print(f"Error: '{file_path}' 파일을 찾을 수 없습니다.")
        return

    print(f"Reading data from: {file_path}")
    nclones_list = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                # nclones 값 수집
                if "nclones" in data:
                    nclones_list.append(data["nclones"])

        if not nclones_list:
            print("데이터에 'nclones' 정보가 없습니다.")
            return

        # 빈도수 계산 (X: nclones 값, Y: 등장 횟수)
        counts = Counter(nclones_list)
        
        # 그래프를 그리기 위해 X축 기준으로 정렬
        sorted_x = sorted(counts.keys())
        sorted_y = [counts[x] for x in sorted_x]

        # 텍스트 통계 출력
        print("\n[Statistics]")
        print(f"{'nclones':<10} | {'Count':<10}")
        print("-" * 25)
        for x, y in zip(sorted_x, sorted_y):
            print(f"{x:<10} | {y:<10}")

        # 그래프 그리기
        plt.figure(figsize=(10, 6))
        bars = plt.bar(sorted_x, sorted_y, color='skyblue', edgecolor='black')
        
        plt.title('Distribution of Clone Group Sizes', fontsize=15)
        plt.xlabel('Number of Clones in Group (nclones)', fontsize=12)
        plt.ylabel('Number of Groups (Frequency)', fontsize=12)
        plt.xticks(sorted_x)  # X축 눈금을 정수값으로 고정
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        # 막대 위에 숫자 표시
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2.0, height, 
                     f'{int(height)}', ha='center', va='bottom')

        # 이미지 파일로 저장
        output_file = 'clone_distribution.png'
        plt.savefig(output_file)
        print(f"\nGraph saved to: {output_file}")
        print("Done.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # 파일 경로 설정 (기본값 또는 인자)
    input_file = sys.argv[1] if len(sys.argv) > 1 else "data/nicad_camel_clone_func.jsonl"
    plot_clone_distribution(input_file)