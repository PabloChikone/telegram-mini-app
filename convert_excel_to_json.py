import pandas as pd
import json
import os
import glob
from datetime import datetime, timedelta
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SOURCE_DIR = "/home/admin/parsing_eventlog/statistics"
OUTPUT_DIR = "/home/admin/eventlog_bot/data"
REPO_DIR = "/home/admin/eventlog_bot"

def find_latest_excel():
    pattern = os.path.join(SOURCE_DIR, "statistics_*.xlsx")
    files = glob.glob(pattern)
    if not files:
        logger.error("Excel файлы не найдены")
        return None
    latest_file = max(files, key=os.path.getmtime)
    logger.info(f"Найден файл: {latest_file}")
    return latest_file

def clean_number(value):
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        cleaned = re.sub(r'[^\d]', '', str(value))
        return int(cleaned) if cleaned else 0
    return 0

def convert_excel_to_json(excel_file):
    try:
        df_year = pd.read_excel(excel_file, sheet_name="Год")
        df_today = pd.read_excel(excel_file, sheet_name="Текущие")
        
        def process_dataframe(df, sheet_name):
            df['Время проверки'] = pd.to_datetime(df['Время проверки'], format='%d.%m.%Y %H:%M')
            # Добавляем +3 часа для Московского времени
            df['Время проверки'] = df['Время проверки'] + timedelta(hours=3)
            
            for col in df.columns:
                if col != 'Время проверки':
                    df[col] = df[col].apply(clean_number)
            
            df['Время проверки'] = df['Время проверки'].dt.strftime('%Y-%m-%d %H:%M')
            logger.info(f"{sheet_name}: {len(df)} строк")
            return df
        
        df_year = process_dataframe(df_year, "Год")
        df_today = process_dataframe(df_today, "Текущие")
        
        data = {
            "last_update": (datetime.now() + timedelta(hours=3)).isoformat(),
            "source_file": os.path.basename(excel_file),
            "year": {
                "labels": df_year['Время проверки'].tolist(),
                "data": df_year.drop(columns=['Время проверки']).to_dict('list')
            },
            "today": {
                "labels": df_today['Время проверки'].tolist(),
                "data": df_today.drop(columns=['Время проверки']).to_dict('list')
            }
        }
        
        output_file = os.path.join(OUTPUT_DIR, "statistics.json")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"JSON сохранен: {output_file}")
        return output_file
        
    except Exception as e:
        logger.error(f"Ошибка конвертации: {e}")
        import traceback
        traceback.print_exc()
        return None

def copy_to_repo():
    src = os.path.join(OUTPUT_DIR, "statistics.json")
    dst = os.path.join(REPO_DIR, "statistics.json")
    if os.path.exists(src):
        import shutil
        shutil.copy2(src, dst)
        logger.info(f"JSON скопирован в репозиторий: {dst}")
        return True
    return False

def git_push():
    import subprocess
    try:
        os.chdir(REPO_DIR)
        subprocess.run(["git", "add", "statistics.json", "index.html"], check=True, capture_output=True)
        
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if not status.stdout.strip():
            logger.info("Нет изменений для коммита")
            return True
        
        commit_msg = f"Auto-update statistics {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        subprocess.run(["git", "commit", "-m", commit_msg], check=True, capture_output=True)
        subprocess.run(["git", "push"], check=True, capture_output=True)
        logger.info("Изменения отправлены в GitHub")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка Git: {e}")
        return False

def main():
    logger.info("Начинаем конвертацию Excel → JSON")
    excel_file = find_latest_excel()
    if not excel_file:
        return
    json_file = convert_excel_to_json(excel_file)
    if not json_file:
        return
    if copy_to_repo():
        git_push()

if __name__ == "__main__":
    main()
