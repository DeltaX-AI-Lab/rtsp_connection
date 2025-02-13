import cv2
import time
import threading

class VideoStream:
    def __init__(self, url):
        self.url = url
        self.cap = cv2.VideoCapture(self.url)
        self.frame = None
        self.stopped = False
        self.lock = threading.Lock()

        if not self.cap.isOpened():
            print(f"Failed to open the RTSP stream: {self.url}")
            exit()

        # Start the thread to read frames from the video stream
        thread = threading.Thread(target=self.update, daemon=True)
        thread.start()

    def update(self):
        while not self.stopped:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.frame = frame

    def read(self):
        with self.lock:
            return self.frame

    def stop(self):
        self.stopped = True
        self.cap.release()

def main():
    # List your RTSP URLs here
    rtsp_urls = [
        'rtsp://admin:1234567s@192.168.200.132:554/Streaming/Channels/101',
        # 'rtsp://admin:1234567s@192.168.200.132:554/Streaming/Channels/201',
        # 'rtsp://admin:1234567s@192.168.200.132:554/Streaming/Channels/301',
        # 'rtsp://admin:1234567s@192.168.200.132:554/Streaming/Channels/401',
        # 'rtsp://admin:1234567s@192.168.200.132:554/Streaming/Channels/501',
        # 'rtsp://admin:1234567s@192.168.200.132:554/Streaming/Channels/601',
        # 'rtsp://admin:1234567s@192.168.200.132:554/Streaming/Channels/701',
        # 'rtsp://admin:1234567s@192.168.200.132:554/Streaming/Channels/101',
        # 'rtsp://admin:1234567s@192.168.200.132:554/Streaming/Channels/201',
        # 'rtsp://admin:1234567s@192.168.200.132:554/Streaming/Channels/301',
        # 'rtsp://admin:1234567s@192.168.200.132:554/Streaming/Channels/401',
        # 'rtsp://admin:1234567s@192.168.200.132:554/Streaming/Channels/501',
        # 'rtsp://admin:1234567s@192.168.200.132:554/Streaming/Channels/601',
        # 'rtsp://admin:1234567s@192.168.200.132:554/Streaming/Channels/701',
    ]
    # Create a VideoStream instance for each URL
    streams = [VideoStream(url) for url in rtsp_urls]

    # Maintain separate frame counters and start times for each stream
    frame_counts = [0] * len(streams)
    start_times = [time.time()] * len(streams)

    while True:
        # Loop through each stream
        for idx, stream in enumerate(streams):
            frame_start_time = time.time()  # Record the start time for latency calculation
            frame = stream.read()
            if frame is None:
                continue  # Skip if the frame isn't available yet

            # Update frame count and compute FPS for this stream
            frame_counts[idx] += 1
            elapsed_time = time.time() - start_times[idx]
            fps = frame_counts[idx] / elapsed_time if elapsed_time > 0 else 0

            # Compute latency (processing delay) in milliseconds
            frame_latency = (time.time() - frame_start_time) * 1000

            # Overlay FPS and latency on the frame
            cv2.putText(frame, f"Stream {idx} FPS: {fps:.2f}", (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Latency: {frame_latency:.2f} ms", (20, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Display the frame in its own window
            cv2.imshow(f"RTSP Stream {idx}", frame)

        # Exit if the 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Stop all streams and close windows
    for stream in streams:
        stream.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
