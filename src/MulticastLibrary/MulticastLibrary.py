#!/usr/bin/env python3
import ffmpeg
import ping3
import vlc
import os
import cv2
import socket
import numpy
import struct
import threading
import time
from pathlib import Path
from robot.api.deco import keyword


class MulticastLibrary(object):
    stop_sending = threading.Event()

    @keyword("Get Frame Counts")
    def Get_Frame_count(self, video_file: str) -> int:
        """
        Get frame counts from the given video file and return frame count.

        :param video_file: Path to the video file to extract frames from.
        :return: Frame counts of given file.
        """

        if (os.path.exists(video_file)):
            frame_count = 0
            video_obj = cv2.VideoCapture(video_file)
            while True:
                ret, frame = video_obj.read()
                if not ret:
                    break
                frame_count += 1
            video_obj.release()
            return frame_count
        else:
            raise FileNotFoundError(f"{file} file does not exist!")


    @keyword("Extracting Video Frames")
    def Extracting_Video_Frames(self, video_file: str, file_format: str = "jpg", output_dir :str = None) -> list:
        """
        Extract frames from the given video file and save them as image files.

        :param video_file: Path to the video file to extract frames from.
        :param file_format: The file format for the extracted frames (default is 'jpg').
        :param output_dir: Directory to save the extracted frames (default is the current working directory).
        :return: List of file paths where frames have been saved.
        """
        if not os.path.exists(video_file):
            raise FileNotFoundError(f"{video_file} file does not exist!")

        if output_dir is None:
            directory_path = Path.cwd()
        else:
            os.makedirs(output_dir, exist_ok=True)
            directory_path = Path(output_dir)

        video_frames = []
        frame_count = 0
        video_obj = cv2.VideoCapture(video_file)
        while True:
            ret, frame = video_obj.read()
            if not ret:
                break
            filename = os.path.join(directory_path, f"frame_{frame_count:04d}.{file_format}")
            cv2.imwrite(filename, frame)
            frame_count += 1
            if os.path.exists(filename):
                video_frames.append(filename)
            else:
                raise FileNotFoundError(f"{video_file} file does not exist!")
        video_obj.release()
        return video_frames


    @keyword("Removing Video Frame Files")
    def Removing_Video_Frame_Files(self, file_format: str = "jpg", directory: str = None):
        """
        Removes all files with the specified format from the given directory.

        :param file_format: The file extension of the files to be deleted (default is 'jpg').
        :param directory: The directory from which to delete the files (default is the current working directory).
        """
        if directory is None:
            directory_path = Path.cwd()
        else:
            directory_path = Path(directory)

        if not directory_path.exists():
            raise FileNotFoundError(f"The directory {directory_path} does not exist!")

        for file in directory_path.glob(f"*.{file_format}"):
            try:
                file.unlink()
            except Exception as e:
                print(f"Error deleting {file}: {e}")


    @keyword("Ping")
    def ping(self, remote_host: str = '127.0.0.1') -> bool:
        """
        Pings a remote host and returns bool value. True If the host is reachable, False otherwise.

        :param remote_host: The IP address or hostname of the remote host. The default value for remote_host is localhost
        :return: True if the host responds to the ping, False otherwise.
        """
        if remote_host.count(".") == 3:
            try:
                if ping3.ping(remote_host, timeout=1):
                    return True
                else:
                    return False
            except (TypeError, OSError) as e:
                return False
            except NameError as e:
                return (f"module {e}")
        else:
            return False


    @keyword("Should Be Equal As Frames")
    def Should_Be_Equal_As_Frames(self, source_img: str, destination_img: str) -> bool:
        """
        Compares the given frames and returns a boolean value.

        :param source_img: Specifies the source image file.
        :param destination_img: Specifies the destination image file.
        :return: True if the frames match, False otherwise.
        """
        if not os.path.isfile(source_img):
            raise FileNotFoundError(f"{source_img} file does not exist!")

        if not os.path.isfile(destination_img):
            raise FileNotFoundError(f"{destination_img} file does not exist!")

        src_img = cv2.imread(source_img)
        dst_img = cv2.imread(destination_img)

        if src_img.shape == dst_img.shape:
            diff = cv2.absdiff(src_img, dst_img)
            gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            _, threshold_diff = cv2.threshold(gray_diff, 50, 255, cv2.THRESH_BINARY)
            if numpy.sum(threshold_diff) > 0:
                return False
            else:
                return True
        else:
            return False


    @staticmethod
    @keyword("Create Send Socket")
    def Create_Send_Socket(ttl: int = 5) -> socket.socket:
        """
        Create a Sending Multicast socket.

        :param sock: An object representing the multicast socket (e.g., from Create Multicast Socket).
        :param ttl: The TTL value to be set. Defaults to 5.
        :return: The socket object with the updated TTL value.
        """
        send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        ttl_bytes = struct.pack('b', ttl)
        send_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl_bytes)
        return send_sock


    @staticmethod
    @keyword("Create Receive Socket")
    def Create_Receive_Socket(multicast_group: str = "239.239.239.239", port: int = 5999) -> socket.socket:
        """
        Create a receiving Multicast socket

        :param multicast_group: The multicast_group value to be set. Defaults to '239.239.239.239'.
        :param port: The port value to be set. Defaults to 5999.
        :return: Receiving socket object with the updated multicast group and port values.
        """
        recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        recv_sock.bind(('', port))
        mreq = struct.pack("4sl", socket.inet_aton(multicast_group), socket.INADDR_ANY)
        recv_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        return recv_sock


    @staticmethod
    @keyword("Send Multicast Message")
    def Send_Multicast_Message(send_sock: socket.socket, multicast_group: str, port: int, message: str, interval: float = 1, duration: float = 5):
        """
        Sends multicast messages periodically in a separate thread.

        :param send_sock: An object representing the sending multicast socket.
        :param multicast_group: The multicast_group value to be set. Defaults to '239.239.239.239'.
        :param port: The port value to be set. Defaults to 5999.
        :param message: A message value to be set.
        :param interval: Wait for a sending message
        :param duration: thread duration
        :return: An encoded value message string should be returned.
        """
        def send_loop():
            start_time = time.time()
            while not MulticastLibrary.stop_sending.is_set():
                if time.time() - start_time > duration:
                    break
                encoded_message = message.encode()
                send_sock.sendto(encoded_message, (multicast_group, port))
                time.sleep(interval)

        sender_thread = threading.Thread(target=send_loop, daemon=True)
        sender_thread.start()
        sender_thread.join()


    @staticmethod
    @keyword("Receive Multicast Message")
    def Receive_Multicast_Message(recv_sock: socket.socket, timeout: float = 5) -> list:
        """
        Receives multicast messages within a timeout period.

        :param send_sock: An object representing the receiving multicast socket.
        :param timeout: Wait for a receiving message timeout
        :return: received a message.
        """
        recv_sock.settimeout(timeout)
        received_messages = []

        try:
            while True:
                data, _ = recv_sock.recvfrom(1024)
                received_messages.append(data.decode())
        except socket.timeout:
            pass

        return received_messages


    @staticmethod
    @keyword("Should Messages Be Equal")
    def Should_Messages_Be_Equal(sent_msg: str, recv_msg: list):
        """
        Verifies if the sent message is equal to the received message.

        :param sent_msg: The message that was sent.
        :param received_msg: The message that was received.
        :raises AssertionError: If the sent message is not equal to the received message.
        """
        if sent_msg not in recv_msg:
            raise AssertionError(f"'{sent_msg}' is not found in the received message")
    

    @staticmethod
    @keyword("Should Messages Not Be Equal")
    def Should_Messages_Not_Be_Equal(sent_msg: str, recv_msg: list):
        """
        Verifies if the sent message is not equal to the received message.

        :param sent_msg: The message that was sent.
        :param received_msg: The message that was received.
        :raises AssertionError: If the sent message is equal to the received message.
        """
        if sent_msg in recv_msg:
            raise AssertionError(f"'{sent_msg}' is found in the received message")
    

    @staticmethod
    @keyword("Stop Sending")
    def Stop_Sending_Messages():
        """
        Signal the sending thread to stop.
        """
        MulticastLibrary.stop_sending.set()

    
    @keyword("Get Streaming Frame")
    def Get_Streaming_Frame(self, multicast_url: str) -> numpy.ndarray:
        """
        Captures and returns the current frame from the video stream.
        
        :param multicast_url: Specify a url like udp, 
        :return: The current frame as a NumPy array.
        """
        capture_video = cv2.VideoCapture(multicast_url)

        if not capture_video.isOpened():
            raise ValueError(f"Failed to open video stream: {multicast_url}")
        
        ret, frame = capture_video.read()
        capture_video.release()

        if not ret:
            raise ValueError("Failed to capture frame from stream")
        return frame


    @keyword("Convert Frame To Image")
    def Convert_Frame_To_Image(self, frame: numpy.ndarray, filename: str, width: int = None, height: int = None) -> str:
        """
        Converts the given frame to an image and saves it with the specified filename.
        
        :param frame: The frame (image) to be saved.
        :param filename: The path where the image will be saved.
        :param width: The desired width of the output image. (Optional)
        :param height: The desired height of the output image. (Optional)
        :return: The path of the saved image file.
        """
        if not isinstance(frame, numpy.ndarray):
            raise TypeError("Frame must be a numpy.ndarray.")

        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        if width and height:
            frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)

        success = cv2.imwrite(filename, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
        
        if not success:
            raise ValueError(f"Failed to save the image: {filename}")

        return filename
