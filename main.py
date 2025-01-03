import aisuite as ai
import time
import pandas as pd
import subprocess 
import sys

client = ai.Client()

def get_ollama_llms():
    try:
        result = subprocess.run(['ollama', 'ls'], capture_output=True, text=True)
        if result.returncode == 0:
            # ヘッダー行をスキップし、各行からNAME部分（最初のカラム）を抽出
            lines = result.stdout.strip().split('\n')[1:]  
            models = []
            for line in lines:
                # 空白で分割し、最初のカラム（NAME）を取得
                name = line.split()[0]
                models.append(f"ollama:{name}")
            print(f"これらのモデルが検出されました：{models}")
            return models
        else:
            print("ollamaコマンドの実行に失敗しました")
            return []
    except FileNotFoundError:
        print("ollamaコマンドが見つかりません")
        return []
    

def compare_llm(llms, messages):
    execution_times = []
    responses = []
    for llm in llms:
        try:
            print(f"\n{llm}のテストを開始します...")
            start_time = time.time()
            response = client.chat.completions.create(model=llm, messages=messages)
            end_time = time.time()
            execution_time = end_time - start_time
            responses.append(response.choices[0].message.content.strip())
            execution_times.append(execution_time)
            print(f"{llm} - {execution_time:.2f} seconds: {response.choices[0].message.content.strip()}")
        except Exception as e:
            print(f"\n{llm}でエラーが発生しました：")
            print(f"エラー内容: {str(e)}")
            responses.append(f"エラー: {str(e)}")
            execution_times.append(-1)
            continue
    return responses, execution_times

def get_messages(mcontent):
    return [
        {"role": "user", "content": mcontent},
    ]


def get_table(llms, execution_times, responses, save = False):
    data = {
        'Provider:Model Name': llms,
        'Execution Time': execution_times,
        'Model Response ': responses
    }
    
    df = pd.DataFrame(data)
    df.index = df.index + 1
    styled_df = df.style.set_table_styles(
        [{'selector': 'th', 'props': [('text-align', 'center')]}, 
         {'selector': 'td', 'props': [('text-align', 'center')]}]
    ).set_properties(**{'text-align': 'center'})
    if save:
        df.to_csv("table.csv", index=False)
    return styled_df

def display_table(table):
    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_columns', None)
    print(table)

if __name__ == "__main__":
    args = sys.argv
    if len(args) > 1:
        messages = get_messages(args[1])
        print(f"こちらのテストを実行します。{messages}")
    else:
        messages = get_messages("スマートフォンへのAI搭載の影響について考察してください。日本語で回答してください。")
        print(f"こちらのテストを実行します。{messages}")
    llms = get_ollama_llms()
    responses, execution_times = compare_llm(llms, messages)
    table = get_table(llms, execution_times, responses, save = True)
    display_table(table)

