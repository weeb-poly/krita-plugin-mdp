# MDPフォーマットとは？

MDPフォーマットは、2006年にリリースをした、mdiapp (現在はmdiapp+) で使用されている、標準画像フォーマットです。mdiapp+, FireAlpaca, MediBang Paint, LayerPaint HD で使用されています。残念ながらソースコードを公開するわけにはいかないので、仕様だけここに記しておこうと思います。

https://nattou.org/ (mdiapp+ などが公開されています)

当初は、

* キャンバスやレイヤー情報をXMLで記録するMDIファイル (*.mdi)
* レイヤー等のバイナリデータを保存するMDIBINファイル (*.mdibin)

の２つで１セットの画像ファイルだったんですが、扱いが面倒だったので、Packするという形で、MDPファイルにまとめました。"mdi packed" という感じで命名したので、決して "MediBang Paint" から取ってMDPではありません。というわけで、MDPファイルは、

* MDP Header (20 bytes)
* MDI Part (XML format)
* MDIBIN Part (Binary)

の3パートで構成されています。

# MDP Header

MDP Headerは、MDIファイルとMDIBINファイルをまとめるためのヘッダです。

```c
#define MDIPACK_HEADER "mdipack"
#define MDIPACK_VER 0

struct TMDIPack
{
  char header[8]; // "mdipack "
  DWORD version;  // 0

  DWORD mdiSize;
  DWORD mdibinSize;
};
```

という感じで宣言されています。合計 20 bytes です。

この後、XMLパートが mdiSize 分だけ続き、その後に mdibinSize だけバイナリパートが続きます。

# XMLパート (MDI)

まずはXMLパートを読み込んでみましょう。なぜ今どきXMLフォーマットを使っているんでしょうか？ 2004～2005年辺りに実装を開始したので、許してください。

```xml
<Mdiapp width="640" height="480" dpi="350" checkerBG="true" bgColorR="255" bgColorG="255" bgColorB="255">
    <CreateTime time="1643012422" timeString="2022-01-24T17:20:22" />
    <UpdateTime time="1643012432" timeString="2022-01-24T17:20:32" rev="2" />
    <Thumb width="256" height="192" bin="thumb" />
    <Snaps />
    <Guides />
    <ICCProfiles enabled="false" cmykView="false" blackPoint="true" renderingIntent="perceptual" />
    <Animation enabled="false" showNextPrev="true" baseLayer="false" fps="24" />
    <Layers active="5">
        <Layer ofsx="0" ofsy="0" width="640" height="480" mode="normal" alpha="255" visible="true" protectAlpha="false" locked="false" clipping="false" masking="false" maskingType="0" id="0" draft="false" parentId="-1" flags="0" frameNum="1" name="Layer1" binType="2" bin="layer0img" type="32bpp" />
        <Layer ofsx="0" ofsy="0" width="640" height="480" mode="normal" alpha="255" visible="true" protectAlpha="false" locked="false" clipping="false" masking="false" maskingType="0" id="1" draft="false" parentId="-1" flags="0" frameNum="1" name="Layer2" binType="2" bin="layer1img" color="FF000000" halftoneType="none" halftoneLine="60" type="8bpp" />
        <Layer ofsx="0" ofsy="0" width="640" height="480" mode="normal" alpha="255" visible="true" protectAlpha="false" locked="false" clipping="false" masking="false" maskingType="0" id="2" draft="false" parentId="-1" flags="0" frameNum="1" name="Layer3" binType="2" bin="layer2img" color="FF000000" type="1bpp" />
        <Layer ofsx="0" ofsy="0" width="640" height="480" mode="normal" alpha="255" visible="true" protectAlpha="false" locked="false" clipping="false" masking="false" maskingType="0" id="4" draft="false" parentId="3" flags="0" frameNum="1" name="Layer4" binType="2" bin="layer3img" type="32bpp" />
        <Layer ofsx="0" ofsy="0" width="640" height="480" mode="normal" alpha="255" visible="true" protectAlpha="false" locked="false" clipping="false" masking="false" maskingType="0" id="5" draft="false" parentId="3" flags="0" frameNum="1" name="Layer5" binType="2" bin="layer4img" type="32bpp" />
        <Layer ofsx="0" ofsy="0" width="640" height="480" mode="normal" alpha="255" visible="true" protectAlpha="false" locked="false" clipping="false" masking="false" maskingType="0" id="3" draft="false" parentId="-1" flags="0" frameNum="1" name="Folder1" folderOpen="true" binType="2" bin="layer5img" type="folder" />
    </Layers>
</Mdiapp>
```

* Folder1
* * Layer5 (32bppレイヤー)
* * Layer4 (32bppレイヤー)
* Layer3 (1bppレイヤー)
* Layer2 (8bppレイヤー)
* Layer1 (32bppレイヤー)

というレイヤーが存在するキャンバスのXMLパートです。見たままなので、特に説明する必要がないですね。

レイヤーには "id" が振り分けられていて、これはユニークな値である必要があります。

Layer4, Layer5 のように、親フォルダがある時は、"parentId" に親フォルダのIDがセットされます。

"bin" は、MDIBINパートでバイナリを取り出すためのラベルで、"binType" は (10年以上変わらず) 常に2なので気にしないでください。

ちなみに、このXMLデータ部は、4バイト整合がされていません……間抜けすぎる（涙）。

というわけで、続いてのMDIBINパートの解説に行きましょう。

# バイナリパート (MDIBIN)

MDIBINパートから、レイヤーの画像バイナリを取り出します。バイナリ値は、リトルエンディアンです、おめでとうございます。
先程のXMLに "bin="layer0img" という箇所がありましたが、バイナリが layer0img というラベルが付けられて MDIBIN 部に保存されているので、"layer0img" をキーにシークしていきます。

MDIBIN部は、こんな感じの非常にシンプルなフォーマットになっています。

```
[TPackerHeader 0]
[data 0]
[TPackerHeader 1]
[data 1]
[TPackerHeader 2]
[data 2]
[TPackerHeader 3]
[data 3]
...
```

TPackHeader と バイナリ (streamSize bytes) が、対になって保存されています。

```cpp
#define PAC_MAX_NANE 64
#define PAC_RESERVED 48

//////////////////////////////////////////////////////////////////////////////
// PACヘッダ (132 byte)
//////////////////////////////////////////////////////////////////////////////
#pragma pack (push,1)
struct TPackerHeader
{
  // 4 byte
  char identifier[4]; // 'PAC '

  // 16 byte
  DWORD chunkSize;  // 全体サイズ (ヘッダ + データ)
  DWORD streamType; // ストリームデータタイプ (無圧縮 or ZLIB or OTHER)
  DWORD streamSize; // ストリームサイズ
  DWORD outSize;    // 展開後サイズ

  // 48 byte
  BYTE reserved[PAC_RESERVED]; // 予約

  // 64 byte
  char archiveName[PAC_MAX_NANE]; // アーカイブ名 (ラベル名 "layer0img" など
};
#pragma pack(pop)
```

TPackerHeader はこんな感じに初期化しています。

```cpp
bool CPackerEncode::InitHeader( TPackerHeader& header, const char* archiveName, DWORD comp )
{
  // ヘッダ定義
  header.identifier[0] = 'P';
  header.identifier[1] = 'A';
  header.identifier[2] = 'C';
  header.identifier[3] = ' ';
  header.streamType = comp;

  // 予約
  for (int i=0; i<PAC_RESERVED; i++) header.reserved[i] = 0;

  // 名前（長すぎない？）
  int sl = strlen( archiveName );
  if (sl >= PAC_MAX_NANE) return false;
  memset( &header.archiveName[0], 0, PAC_MAX_NANE );
  strncpy( &header.archiveName[0], archiveName, sl );

  return true;
}
```

streamType は、
```cpp
  static const DWORD COMP_NONE = 0;
  static const DWORD COMP_ZLIB = 1;
```
となっていて、0なら無圧縮、1ならzlibで圧縮されています。MDPフォーマットの場合、タイル情報 (後述) をzlib圧縮しているので、ここは常に0 (無圧縮) のはずです。

指定のバイナリを取得する方法を疑似コードで書くならば、

```cpp
while (true)
{
  // TPackerHeader を読み込む
  TPackerHeader header;
  Read( file, &header, sizeof(header) );

  // layerBinName かどうかチェック
  if (Find( &header.archiveName, layerBinName ))
  {
    // マッチしたので、レイヤーを読み込み
    ReadLayerBinary( file, &header );
  }
  else
  {
    // 違ったので飛ばす
    Seek( file, header.streamSize );
  }
}
```

といった感じになるでしょうか。

# タイル化された画像データ

実際に、書き込まれていくデータ ([data 0] [data 1] ...) が問題ですね。

MDPフォーマットの画像は、128 * 128 px単位でタイル化されて保存されています。レイヤーの一部分しか使われていない事が大半なので、レイヤー全体を保存するのは無駄だからです。[data 0] のバイナリデータは、以下のようになっています。
```
総タイル数 [4 byte] // 総タイル数が0なら、以下のデータはなし

タイルサイズ (幅＝高さ) [4 byte] // 128 固定

1番目タイルデータ [XXX byte]
2番目タイルデータ [XXX byte]
3番目タイルデータ [XXX byte]

... タイル数だけ続く
```

となっています。タイル情報は、具体的にどんなデータが書き込まれているでしょうか？

「空タイル（透明な領域）」は、不要なので無視します。保存しないでください（保存されていません）。

「中身があるタイル」なら、

* タイルの横座標 [4 byte]
* タイルの縦座標 [4 byte]
* 圧縮方式 [4 byte] (0:zlib, 1:snappy, 2:FastLZ)
* 圧縮済みデータサイズ [4 byte]
* 圧縮データ [任意 byte]

が保存されます。圧縮データは、[data 0] 内のでオフセット位置 (MDPファイル内ではない) で、4 byte 整合してください (0を詰めておいてください)。

タイル座標は、レイヤー座標のように 0,128,256... ではなく、タイル的な位置なので 0,1,2,3... という値が入ります。

384 * 256 px のレイヤーなら、最大 3 * 2 タイル分のタイルデータを保存します。
385 * 257 px なら、4 * 3 タイルになります。

* 32bppレイヤーなら、展開後サイズは 128 * 128 * 4 bytes
* 8bppレイヤーなら、展開後サイズは 128 * 128 bytes
* 1bppレイヤーなら、展開後サイズは 128 * 128 / 8 bytes

になります。これがタイル数だけ続くだけです。簡単ですね。

# サムネイル画像の取得

サムネイル情報は Thumbタグに存在し、bin="thumb" とあり、MDIBINに thumb をキーに取り出せます。

ARGB (32bpp) 、width * height の画像（タイル化なしの、連続したメモリ列）として保存されています。

# 終わりに

以上、PSDフォーマットに比べたら極めて単純なので、実装は容易なのではないでしょうか？