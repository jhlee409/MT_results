import cv2
import mediapipe as mp
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
import absl.logging


absl.logging.set_verbosity(absl.logging.ERROR)

# 사용자에게 파일 선택 창 표시
def select_video_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi;*.mov")])
    return file_path

# 홍채의 상대적 위치를 기반으로 5x11 그리드 위치 계산
def classify_eye_grid(horizontal_ratio, vertical_ratio):
    col = int(horizontal_ratio * 11)  # 가로 그리드 위치 (0~10)
    row = int(vertical_ratio * 5)  # 세로 그리드 위치 (0~4)

    # 그리드 범위를 벗어나는 경우 처리
    col = min(max(col, 0), 10)
    row = min(max(row, 0), 4)

    return row, col

# 5x11 그리드 시각화 (눈 영역에 한정)
def plot_eye_grid(activation_map):
    fig, ax = plt.subplots(figsize=(22, 10))  # 가로 크기 증가

    # 데이터 정규화 및 비율 계산
    total_frames = np.sum(activation_map)
    percentage_map = (activation_map / total_frames) * 100 if total_frames > 0 else activation_map
    max_percentage = np.max(percentage_map)  # 최대 비율

    # 5x11 그리드 생성
    for i in range(5):
        for j in range(11):
            # 최대값 대비 상대적인 비율로 색상 계산
            relative_intensity = percentage_map[i, j] / max_percentage if max_percentage > 0 else 0
            color = plt.cm.Reds(relative_intensity)  # 흰색(0%)에서 적색(최대값)으로 변화
            ax.fill([j, j+1, j+1, j], [i, i, i+1, i+1], color=color)

            # 각 셀의 중앙에 값 표시 (%로 표시)
            if percentage_map[i, j] > 0:
                ax.text(j+0.5, i+0.5, f"{percentage_map[i, j]:.1f}%", 
                        ha='center', va='center', 
                        color='black' if relative_intensity < 0.5 else 'white',
                        fontsize=10)

    ax.grid(True)
    ax.set_title("Iris Dwell Time Distribution (5x11 Grid)")
    ax.set_xlabel("Horizontal Area")
    ax.set_ylabel("Vertical Area")

    # 컬러바 추가 (최대값 기준)
    sm = plt.cm.ScalarMappable(cmap=plt.cm.Reds, norm=plt.Normalize(0, max_percentage))
    plt.colorbar(sm, ax=ax, label='Dwell Time Ratio (%)')

    ax.set_xticks(np.arange(0, 12, 1))
    ax.set_yticks(np.arange(0, 6, 1))
    ax.invert_yaxis()  # y축 방향 반전

    plt.tight_layout()
    plt.show()

# 비디오 분석 (눈 영역 내 5x11 그리드 기반)
def analyze_eye_gaze_with_grid(video_path):
    cap = cv2.VideoCapture(video_path)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # 5x11 활성화 맵 초기화
    activation_map = np.zeros((5, 11), dtype=np.int32)

    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # 눈 영역 수정: 눈과 그 주변 영역으로 경계 조정
                left_eye_region = np.array([
                    (face_landmarks.landmark[i].x * frame_width, face_landmarks.landmark[i].y * frame_height)
                    for i in [33, 133, 173, 155, 154, 153, 145, 144, 163, 7]
                ])

                # 홍채 중심 좌표 계산 (468: 왼쪽 홍채 중심)
                iris_center = (
                    face_landmarks.landmark[468].x * frame_width,
                    face_landmarks.landmark[468].y * frame_height
                )

                left = np.min(left_eye_region[:, 0]) + 0.3 * (np.max(left_eye_region[:, 0]) - np.min(left_eye_region[:, 0]))
                right = np.max(left_eye_region[:, 0]) - 0.25 * (np.max(left_eye_region[:, 0]) - np.min(left_eye_region[:, 0]))
                bottom = np.max(left_eye_region[:, 1]) - (np.max(left_eye_region[:, 1]) - np.min(left_eye_region[:, 1])) / 3.5
                top = bottom - 2 * (bottom - np.min(left_eye_region[:, 1]))

                # 상대 위치 계산
                horizontal_ratio = (iris_center[0] - left) / (right - left)
                vertical_ratio = (iris_center[1] - top) / (bottom - top)

                # 시선 위치를 5x11 그리드로 매핑
                row, col = classify_eye_grid(horizontal_ratio, vertical_ratio)

                if 0 <= row < 5 and 0 <= col < 11:
                    activation_map[row, col] += 1

                # 시선 위치 시각화
                cv2.circle(frame, (int(iris_center[0]), int(iris_center[1])), 5, (0, 255, 0), -1)
                cv2.rectangle(frame, (int(left), int(top)), (int(right), int(bottom)), (255, 0, 0), 1)

        cv2.imshow("Eye Gaze Tracking", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    face_mesh.close()

    return activation_map

# 실행 코드
if __name__ == "__main__":
    video_path = select_video_file()
    if video_path:
        activation_map = analyze_eye_gaze_with_grid(video_path)
        plot_eye_grid(activation_map)
    else:
        print("No video file selected.")
