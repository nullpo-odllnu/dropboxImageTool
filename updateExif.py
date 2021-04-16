import os
from typing import List
import glob
from multiprocessing import Pool
from functools import partial
import shutil
import datetime

import fire
from tqdm import tqdm
from PIL import Image
import piexif


def task(imagepath : str, out : str) -> List[int]:
    filename, ext = os.path.splitext(os.path.basename(imagepath))

    image = Image.open(imagepath)

    # pngファイルの場合には別途対応
    if ext == '.png':
        # RGBA変換後、白背景に貼り付けたRGB画像として扱う
        image = image.convert('RGBA')
        background = Image.new('RGB', image.size, (255, 255, 255))
        background.paste(image, mask = image.split()[3])
        image = background

    findExifKey = 'exif' in image.info.keys()
    exif = {}
    if findExifKey:
        # exif取得
        exif = piexif.load(image.info['exif'])
        # 撮影日時があるか調べる
        findDatetimeOriginal = piexif.ExifIFD.DateTimeOriginal in exif['Exif'].keys()
        if findDatetimeOriginal is False:
            # exifはあるけど、撮影日時タグがない場合は入れる場所だけ確保
            exif['Exif'][piexif.ExifIFD.DateTimeOriginal] = None
    else:
        # exifと、撮影日時タグを入れる場所を確保
        exif['Exif'] = {}
        exif['Exif'][piexif.ExifIFD.DateTimeOriginal] = None

    # 既に撮影日時が入っている場合には以降の処理は行わずに画像コピーだけ
    if exif['Exif'][piexif.ExifIFD.DateTimeOriginal] is not None:
        shutil.copy(imagepath, os.path.join(out, filename + ext))
        return 0
    # ファイル更新日時を撮影日時としてセット
    else:
        updateDatetimeDesc = os.stat(imagepath).st_mtime
        updateDatetime = datetime.datetime.fromtimestamp(updateDatetimeDesc)
        updateDatetimeString = updateDatetime.strftime('%Y:%m:%d %H:%M:%S')
        exif['Exif'][piexif.ExifIFD.DateTimeOriginal] = updateDatetimeString
        exifDump = piexif.dump(exif)
        image.save(os.path.join(out, filename + '.jpg'), 'JPEG', quality = 95, exif = exifDump)
        return 1


def getImagepathList(directoryPath : str) -> List[str]:
    jpgList = list(glob.glob(os.path.join(directoryPath, '*.jpg')))
    pngList = list(glob.glob(os.path.join(directoryPath, '*.png')))

    return jpgList + pngList


def main(image : str, out : str,
         cpu_scale : float = 0.5):
    """
    画像の撮影日時を編集する

    既に格納されている場合には何もしない、
    格納されていない場合にはファイル更新日時を使用する
    pngファイルはjpegとして保存する

    Args:
        image: 画像が格納されたディレクトリパス サブディレクトリは走査しない jpg / pngをターゲットにする
        out: 出力先のディレクトリパス　存在しない場合には新規作成する
        cpu_scale: マルチプロセス時に使用するコア数に対する係数
    """
    print('[{}]'.format(__file__))
    print('input directory path : {}'.format(image))
    print('output directory path : {}'.format(out))
    print('cpu scale : {}({:.0f} cores)'.format(cpu_scale, os.cpu_count() * cpu_scale))

    print('------ find image')
    imagepathList = getImagepathList(image)

    print('------ process loop')
    os.makedirs(out, exist_ok = True)

    processedImages = 0
    with Pool(int(os.cpu_count() * cpu_scale)) as pool:
        for processed in pool.imap_unordered(partial(task, out = out), tqdm(imagepathList, ascii = True)):
            processedImages += processed

    print('----- stat')
    print('processed images : {} / {}'.format(processedImages, len(imagepathList)))


if __name__ == '__main__':
    fire.Fire(main)
