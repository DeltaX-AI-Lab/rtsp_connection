"""
File Name: run_ffmpeg_oop.py
Created Date: 2025.02.10
Programmer: Yuntae Jeon
Description: ffmpeg-based RTSP streaming in OOP style with multiple windows
"""

import cv2
import time

class RTSPstreamer:
    def __init__(self, rtsp_url, window_name):
        """
        Initialize RTSPstreamer with backend type and RTSP URL.
        
        :param rtsp_url: str, RTSP stream URL of the camera
        :param window_name: str, Name of the window to display stream
        """
        self.rtsp_url = rtsp_url
        self.window_name = window_name
        self.cap = None 

    def __connect_server(self, try_times, try_interval):
        """
        Attempt to access the RTSP stream server.
        
        :param try_times: int, Number of connection retry attempts
        :param try_interval: int, Waiting time (in seconds) between retries
        :return: cv2.VideoCapture object if successful, else None
        """
        for i in range(try_times):
            try:
                cap = cv2.VideoCapture(self.rtsp_url)
                ret, frame = cap.read()
            except Exception as e:
                print(f"예외 발생 ({self.window_name}): {e}. 재시도합니다... Try{i+1}!")
                time.sleep(try_interval)
                continue

            if not ret or frame is None:
                print(f"프레임 읽기 실패 ({self.window_name}). 스트림을 재시도합니다... Try{i+1}!")
                cap.release()
                time.sleep(try_interval)
            else:
                self.cap = cap
                return True
        return False
    
    def visualize_frame(self, frame):
        """
        Display the current frame in a window.
        
        :param frame: numpy.ndarray, Image frame to display
        """
        cv2.imshow(self.window_name, frame)

    def run(self, try_times, try_interval):
        """
        Continuously load frames from the RTSP stream and display them.
        
        :param try_times: int, Number of connection retry attempts
        :param try_interval: int, Waiting time (in seconds) between retries
        :return: bool, True if connection was successful, False otherwise
        """
        if not self.__connect_server(try_times, try_interval):
            print(f"서버 연결 실패 ({self.window_name})")
            return False
        
        ret, frame = self.cap.read()
        if not ret or frame is None:
            print(f"프레임 읽기 실패 ({self.window_name})")
            self.cap.release()
            return False

        self.visualize_frame(frame)
        return True

    def read_next_frame(self):
        """
        Read the next frame from the stream.
        
        :return: tuple (bool, numpy.ndarray), Success flag and frame
        """
        if self.cap is None:
            return False, None
        return self.cap.read()

    def release(self):
        """Release the video capture resources."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None


def main():
    rtsp_urls = [
        'rtsp://admin:1234567s@192.168.200.132:554/Streaming/Channels/101',
        'rtsp://admin:password@192.168.200.132:554/Streaming/Channels/201',
        'rtsp://admin:password@192.168.200.132:554/Streaming/Channels/301',
        'rtsp://admin:password@192.168.200.132:554/Streaming/Channels/401',
        'rtsp://admin:password@192.168.200.132:554/Streaming/Channels/501',
        'rtsp://admin:password@192.168.200.132:554/Streaming/Channels/601',
        'rtsp://admin:password@192.168.200.132:554/Streaming/Channels/701'
    ]

    streamers = []
    # For each RTSP URL, create 3 streamer instances
    for url in rtsp_urls:
        window_name = f"Stream_{url.split('/')[-1]}"
        streamer = RTSPstreamer(url, window_name)
        streamers.append(streamer)

    # Initialize all streamers
    active_streamers = []
    for streamer in streamers:
        if streamer.run(2, 2):  # Initial connection and first frame
            active_streamers.append(streamer)

    try:
        while True:
            for streamer in active_streamers:
                ret, frame = streamer.read_next_frame()
                
                if not ret or frame is None:
                    print(f"프레임 읽기 실패 ({streamer.window_name}). 스트림을 재시도합니다...")
                    streamer.release()
                    if not streamer.run(2, 2):
                        active_streamers.remove(streamer)
                        continue
                else:
                    streamer.visualize_frame(frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("종료 키(q)가 입력됨 - 루프 종료")
                break

    except KeyboardInterrupt:
        print("\n키보드 인터럽트 감지. 종료합니다...")
    finally:
        # Cleanup
        for streamer in streamers:
            streamer.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()