# EDA Report

Документ описывает процесс анализа временных рядов.

## 1. Данные
- Источник: Prometheus (`data/raw/*.csv`).
- Основные метрики: `cpu_metrics`, `memory_metrics`, `request_rate`.
- Формат: timestamp (UTC), value (float), promql, labels.

## 2. Обработка
- Ресемплинг до 1 минуты (`preprocessor/config.yaml`).
- Интерполяция пропусков (метод `time`).
- Фильтрация аномалий: Z-score > 3.0 удаляется.
- Скейлинг: StandardScaler с сохранением `scaler.pkl`.

## 3. Визуализация
- Используйте `notebooks/research-data.ipynb` для графиков.
- Сравниваем тренды/сезонность по метрикам.
- Вычисляем статистики: mean/median/std, STL (TODO), корреляции (TODO).

## 4. Нагрузочные сценарии
- Docker Compose сервис `load-generator` для постоянной нагрузки.
- Kubernetes Deployment `load-generator` для кластера.
- Доступны Locust/k6 скрипты (`tools/load_generator`).

## 5. Следующие шаги
- Расширить EDA на latency и RPS.
- Добавить автоматы по сохранению графиков в `docs/figures/`.
- Сравнить паттерны synthetic vs real data.
