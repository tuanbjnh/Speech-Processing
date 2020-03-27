import argparse
import os
import tempfile
import queue
import sys
import keyboard
import sounddevice as sd
import soundfile as sf
import numpy
assert numpy
import time
import io
def int_or_str(text):
    try:
        return int(text)
    except ValueError:
        return text


parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    '-l', '--list-devices', action='store_true',
    help='show list of audio devices and exit')
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    'filename', nargs='?', metavar='FILENAME',
    help='audio file to store recording to')
parser.add_argument(
    '-d', '--device', type=int_or_str,
    help='input device (numeric ID or substring)')
parser.add_argument(
    '-r', '--samplerate', type=int, help='sampling rate')
parser.add_argument(
    '-c', '--channels', type=int, default=1, help='number of input channels')
parser.add_argument(
    '-t', '--subtype', type=str, help='sound file subtype (e.g. "PCM_24")')
args = parser.parse_args(remaining)

q = queue.Queue()


def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(indata.copy())

def recorder( file_name):
    if args.samplerate is None:
        device_info = sd.query_devices(args.device, 'input')
        # soundfile expects an int, sounddevice provides a float:
        args.samplerate = int(device_info['default_samplerate'])

    #open(file_name, 'w')
    # Make sure the file is opened before recording anything:
    try:
        os.remove(file_name)
    except:
        pass
    with sf.SoundFile(file_name, mode='x', samplerate=args.samplerate,
                      channels=args.channels, subtype=args.subtype) as file:
        with sd.InputStream(samplerate=args.samplerate, device=args.device,
                            channels=args.channels, callback=callback):
            while True:
                file.write(q.get())
                if( keyboard.is_pressed("down")):
                    break

data = io.open("input.text",'r',encoding='utf8').read()
for i in range(100):
    data = data.replace("  ", " ")
    data = data.replace(". ", ".")
    data = data.replace("\n", ".")
    data = data.replace("..", ".")
sentences = data.split(".")
id = 0
detail = ""
for sentence in sentences:
    if sentence == "":
        continue
    id += 1
    print(id)  
    print(sentence)
    print("\n")
    print("Nhấn phím 'space' để bắt đầu ghi âm\n Phím mũi tên down để dừng\n Phím mũi tên <- để ghi âm lại\n Phím mũi tên -> để chọn câu tiếp theo")
    detail += id.__str__() + ".wav\n";
    detail += sentence + "\n";
    while(True):
        while not keyboard.is_pressed("space"):
            pass
        print("start")
        recorder(id.__str__() + ".wav")
        print("stop")
        check = False
        while True:
            if( keyboard.is_pressed("right")):
                check = True
                break
            if( keyboard.is_pressed("left")):
                print("again")
                break
        if check:
            break
f = io.open("detail.text",'w',encoding='utf8')
f.write(detail)
f.close()
