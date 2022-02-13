# pyjjy
電波時計の時刻合わせに使用される標準電波JJYをPythonとPyAudioで再現するスクリプトです。shogo82148氏の[web-jjy](https://github.com/shogo82148/web-jjy)と同様に、一般的な機器で出力可能な13.333kHzを出力し、第3高調波がJJYおおたかどや山標準電波送信所の送信波周波数である40kHzとなることを利用しています。PortAudioとPyAudioに依存します。

## インストール
PyIPから最新版をインストール可能です。
```
pip install pyjjy --upgrade
```

## 使い方
10分間のJJY信号を送信する実行方法の例を以下に示します。
```
$ python -m pyjjy -d 600
```
Python内からの呼び出しも可能です。
```python
>>> from pyjjy import JJYsignal
>>> jj = JJYsignal(duration=600)
>>> jj.play()
```

Mac環境では、例えば次のような運用により自動時刻合わせも可能です。
1. 音声出力を"外部ヘッドフォン"に切り替えた後にスリープさせる(Automatorでapp化を推奨)
1. 自動受信時刻前にスリープを解除するようスケジュール設定する
1. cronやlaunchdを用いてJJYシグナルを出すスクリプトを自動実行し、"外部ヘッドフォン"からJJY信号を出力する
1. cronやlaunchdを用いてスリープに入るAppleScriptを自動実行する

## 動作環境
以下の環境で動作を確認しています。

- Mac mini (M1, 2020)
- macOS Monterey 12.0.1
- portaudio 19.7.0 (installed via homebrew)
- Python 3.7.6 (installed via miniconda)
- PyAudio 0.2.11 (installed via conda)
- アンテナ (AMループアンテナを鉄釘に巻き直したバーアンテナ)
- 電波時計 (CITIZEN AT8181-63E)

## 免責事項
利用の結果生じた損害について、一切責任を負いません。

## ライセンス
MITライセンスです。[LICENSE](https://github.com/ehki/pyjjy/blob/fa0ab6afabf93bb23cc5add16d9ead583435134b/LICENSE)を参照ください。
