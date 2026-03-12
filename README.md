# Video Cutter with YOLO-World

Simple web application that cuts or extracts fragments from videos using object detection with **YOLO-World**.

The app allows users to upload a video, specify which objects to detect (for example `person`, `car`, `dog`), and automatically generate a new video based on detected scenes.

Built with:

- **Streamlit** — web interface
- **YOLO-World (Ultralytics)** — object detection
- **OpenCV** — video processing



---

# Вырезка фрагментов из видео с помощью YOLO-World

Простое веб-приложение для автоматической вырезки или извлечения фрагментов из видео на основе детекции объектов с помощью **YOLO-World**.

Пользователь может загрузить видео, указать какие объекты нужно искать (например `person`, `car`, `dog`), после чего приложение автоматически сформирует новое видео на основе найденных сцен.

Используемые технологии:

- **Streamlit** — веб-интерфейс  
- **YOLO-World (Ultralytics)** — детекция объектов  
- **OpenCV** — обработка видео



---

# Features

- Upload your own video
- Detect objects using YOLO-World
- Choose objects to detect (`person`, `car`, etc.)
- Two processing modes:
  - keep fragments with detected objects
  - cut fragments with detected objects
- Adjustable detection parameters
- Download processed video



---

# Возможности

- загрузка собственного видео
- поиск объектов с помощью YOLO-World
- указание классов объектов (`person`, `car`, и др.)
- два режима обработки:
  - оставить фрагменты с найденными объектами
  - удалить фрагменты с найденными объектами
- настройка параметров детекции
- скачивание обработанного видео



---

# Demo Workflow

1. Upload a video file  
2. Specify which objects should be detected  
3. Select processing mode  
4. The model scans frames and detects objects  
5. The application generates a new video based on detected scenes  



---

# Принцип работы

1. Пользователь загружает видео  
2. Указывает какие объекты нужно искать  
3. Выбирает режим обработки  
4. Модель анализирует кадры видео  
5. На основе найденных сцен формируется новое видео  



---

# Installation

Clone the repository:

```bash
git clone https://github.com/your_repo/video_cutter_yolo-world.git
cd video_cutter_yolo-world
```

Create virtual environment:

```bash
python -m venv .venv
```

Activate environment.

Windows:

```bash
.venv\Scripts\activate
```

Linux / Mac:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run application:

```bash
streamlit run app.py
```



---

# Установка

Клонировать репозиторий:

```bash
git clone https://github.com/your_repo/video_cutter_yolo-world.git
cd video_cutter_yolo-world
```

Создать виртуальное окружение:

```bash
python -m venv .venv
```

Активировать окружение.

Windows:

```bash
.venv\Scripts\activate
```

Linux / Mac:

```bash
source .venv/bin/activate
```

Установить зависимости:

```bash
pip install -r requirements.txt
```

Запустить приложение:

```bash
streamlit run app.py
```



---

# Project Structure

```
video_cutter_yolo-world
│
├── app.py
├── requirements.txt
├── packages.txt
└── README.md
```



---

# Структура проекта

```
video_cutter_yolo-world
│
├── app.py
├── requirements.txt
├── packages.txt
└── README.md
```



---

# Notes

- For web deployment **opencv-python-headless** is used instead of standard OpenCV
- Large videos may take longer to process
- Detection speed depends on model size and available hardware



---

# Примечания

- Для веб-версии используется **opencv-python-headless**
- Обработка больших видео может занимать больше времени
- Скорость детекции зависит от выбранной модели и ресурсов системы



---

# License

This project is provided for educational purposes.



---

# Лицензия

Проект предоставляется в учебных целях.
