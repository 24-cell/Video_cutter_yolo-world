import os
import tempfile
from pathlib import Path

import cv2
import streamlit as st
from ultralytics import YOLO


st.set_page_config(page_title="Video Cutter", layout="wide")


@st.cache_resource
def load_model():
    model = YOLO("yolov8l-world.pt")
    return model


def save_uploaded_file(uploaded_file) -> str:
    suffix = Path(uploaded_file.name).suffix if uploaded_file.name else ".mp4"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        tmp_file.write(uploaded_file.read())
        return tmp_file.name


def detect_intervals(
    model,
    input_video_path: str,
    class_names: list[str],
    sample_every_n_frames: int = 10,
    conf: float = 0.1,
    iou: float = 0.4,
    imgsz: int = 384,
    output_size: float = 0.5,
    add_margin_frames: int = 5
):
    """
    Возвращает интервалы кадров, где объект найден.
    """
    model.set_classes(class_names)

    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
        raise Exception("Не удалось открыть видео")

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 25.0

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    detect_frames = []

    frame_index = 0
    progress_placeholder = st.empty()
    progress_bar = st.progress(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_index % sample_every_n_frames == 0:
            resized_frame = cv2.resize(
                frame,
                (int(frame_width * output_size), int(frame_height * output_size))
            )

            results = model.predict(
                resized_frame,
                conf=conf,
                iou=iou,
                imgsz=imgsz,
                verbose=False
            )

            found = False
            if len(results) > 0 and results[0].boxes is not None:
                if results[0].boxes.cls is not None and len(results[0].boxes.cls) > 0:
                    found = True

            if found:
                detect_frames.append(frame_index)

        frame_index += 1

        if total_frames > 0:
            progress = min(frame_index / total_frames, 1.0)
            progress_bar.progress(progress)
            progress_placeholder.text(f"Анализ видео: {frame_index}/{total_frames} кадров")

    cap.release()
    progress_placeholder.empty()
    progress_bar.empty()

    if not detect_frames:
        return [], int(fps), frame_width, frame_height, total_frames

    intervals = []
    start = detect_frames[0]
    prev = detect_frames[0]

    for current in detect_frames[1:]:
        if current - prev <= sample_every_n_frames * 2:
            prev = current
        else:
            intervals.append((max(0, start - add_margin_frames), min(total_frames - 1, prev + add_margin_frames)))
            start = current
            prev = current

    intervals.append((max(0, start - add_margin_frames), min(total_frames - 1, prev + add_margin_frames)))

    return intervals, int(fps), frame_width, frame_height, total_frames


def build_keep_intervals(detect_intervals_list, total_frames: int, mode: str):
    """
    mode:
    - keep_detected: оставить только найденные интервалы
    - cut_detected: вырезать найденные интервалы, оставить остальное
    """
    if mode == "keep_detected":
        return detect_intervals_list

    if mode == "cut_detected":
        if not detect_intervals_list:
            return [(0, total_frames - 1)]

        keep_intervals = []
        current_start = 0

        for start, end in detect_intervals_list:
            if current_start < start:
                keep_intervals.append((current_start, start - 1))
            current_start = end + 1

        if current_start < total_frames:
            keep_intervals.append((current_start, total_frames - 1))

        return keep_intervals

    return []


def write_output_video(
    input_video_path: str,
    output_video_path: str,
    keep_intervals: list[tuple[int, int]],
    fps: int,
    frame_width: int,
    frame_height: int,
    output_size: float = 0.5
):
    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
        raise Exception("Не удалось открыть видео для сохранения результата")

    out_width = int(frame_width * output_size)
    out_height = int(frame_height * output_size)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (out_width, out_height))

    current_interval_index = 0
    frame_index = 0

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    progress_placeholder = st.empty()
    progress_bar = st.progress(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        while current_interval_index < len(keep_intervals) and frame_index > keep_intervals[current_interval_index][1]:
            current_interval_index += 1

        should_write = False
        if current_interval_index < len(keep_intervals):
            start, end = keep_intervals[current_interval_index]
            if start <= frame_index <= end:
                should_write = True

        if should_write:
            resized_frame = cv2.resize(frame, (out_width, out_height))
            out.write(resized_frame)

        frame_index += 1

        if total_frames > 0:
            progress = min(frame_index / total_frames, 1.0)
            progress_bar.progress(progress)
            progress_placeholder.text(f"Сборка результата: {frame_index}/{total_frames} кадров")

    cap.release()
    out.release()
    progress_placeholder.empty()
    progress_bar.empty()


def format_intervals(intervals: list[tuple[int, int]], fps: int) -> list[str]:
    result = []
    for start, end in intervals:
        start_sec = start / fps if fps > 0 else 0
        end_sec = end / fps if fps > 0 else 0
        result.append(f"{start_sec:.2f}s - {end_sec:.2f}s")
    return result


def main():
    st.title("Вырезка фрагментов из видео")
    st.write("Загрузи видео, укажи что искать, и приложение соберет итоговый ролик.")

    uploaded_file = st.file_uploader("Загрузи видео", type=["mp4", "avi", "mov", "mkv"])

    with st.sidebar:
        st.header("Настройки")

        class_input = st.text_input(
            "Что искать",
            value="person",
            help="Через запятую, например: person, car, dog"
        )

        mode_label = st.selectbox(
            "Что делать с найденными фрагментами",
            options=[
                "Оставить только фрагменты с объектом",
                "Вырезать фрагменты с объектом"
            ]
        )

        sample_every_n_frames = st.slider("Проверять каждый N-й кадр", 1, 30, 10)
        conf = st.slider("Уверенность", 0.01, 0.95, 0.10, 0.01)
        iou = st.slider("IoU", 0.01, 0.95, 0.40, 0.01)
        imgsz = st.select_slider("Размер входного изображения", options=[320, 384, 480, 640], value=384)
        output_size = st.slider("Масштаб выходного видео", 0.2, 1.0, 0.5, 0.1)
        add_margin_frames = st.slider("Добавить кадров по краям фрагмента", 0, 30, 5)

    if uploaded_file is not None:
        input_video_path = save_uploaded_file(uploaded_file)

        st.subheader("Исходное видео")
        st.video(input_video_path)

        if st.button("Обработать видео", type="primary"):
            class_names = [item.strip() for item in class_input.split(",") if item.strip()]
            if not class_names:
                st.error("Нужно указать хотя бы один класс для поиска")
                return

            mode = "keep_detected"
            if mode_label == "Вырезать фрагменты с объектом":
                mode = "cut_detected"

            try:
                with st.spinner("Загружается модель и идет обработка..."):
                    model = load_model()

                    detect_intervals_list, fps, frame_width, frame_height, total_frames = detect_intervals(
                        model=model,
                        input_video_path=input_video_path,
                        class_names=class_names,
                        sample_every_n_frames=sample_every_n_frames,
                        conf=conf,
                        iou=iou,
                        imgsz=imgsz,
                        output_size=output_size,
                        add_margin_frames=add_margin_frames
                    )

                    keep_intervals = build_keep_intervals(
                        detect_intervals_list=detect_intervals_list,
                        total_frames=total_frames,
                        mode=mode
                    )

                    output_video_path = os.path.join(tempfile.gettempdir(), "streamlit_output_video.mp4")

                    write_output_video(
                        input_video_path=input_video_path,
                        output_video_path=output_video_path,
                        keep_intervals=keep_intervals,
                        fps=fps,
                        frame_width=frame_width,
                        frame_height=frame_height,
                        output_size=output_size
                    )

                st.success("Готово")

                st.subheader("Найденные интервалы")
                if detect_intervals_list:
                    formatted = format_intervals(detect_intervals_list, fps)
                    for item in formatted:
                        st.write(item)
                else:
                    st.write("Ничего не найдено")

                st.subheader("Результат")
                st.video(output_video_path)

                with open(output_video_path, "rb") as f:
                    st.download_button(
                        label="Скачать итоговое видео",
                        data=f,
                        file_name="result.mp4",
                        mime="video/mp4"
                    )

            except Exception as e:
                st.error(f"Ошибка: {e}")


if __name__ == "__main__":
    main()