# dropboxImageTool

## なにこれ
---
- Dropboxの画像一覧に対するスクリプト置き場

## モジュール群
---
- fire
- tqdm
- pillow
- piexif

## updateExif
---
- 画像リストに対して以下のアクションを行う
    1. 撮影日時(exif)が存在する場合
        - 出力ディレクトリにそのままコピー
    1. 撮影日時(exif)が存在しない場合
        - ファイル更新日時を撮影日時として出力
    1. 画像ファイルがpngの場合
        - 白背景のRGBフォーマットとして変換後、2.の対応を行う

### 実行例
---
`python updateExif -i input_image_directory_path -o output_image_directory_path`

### 備考
---
- 詳しくはヘルプ(`-h`)参照
- マルチプロセス実行に対応
    - デフォルトではCPUコアの半分を使ったマルチプロセスを実行する

