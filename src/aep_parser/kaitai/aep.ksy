meta:
  id: aep
  endian: be
  file-extension: aep

seq:
  - id: magic1
    contents: RIFX
  - id: file_size
    type: u4
  - id: magic2
    contents: Egg!
  - id: data
    type: blocks
    size: file_size - 4
    
types:
  blocks:
    seq:
      - id: blocks
        type: block
        repeat: eos
  block:
    seq: 
      - id: block_type
        type: u4
        enum: chunk_type
      - id: block_size
        type: u4
      - id: data
        size: block_size
        type: 
          switch-on: block_type
          cases:
            'chunk_type::lst': list_body
            'chunk_type::utf8': utf8_body
            'chunk_type::cdta': cdta_body
            'chunk_type::idta': idta_body
            'chunk_type::cmta': utf8_body
            'chunk_type::fdta': fdta_body
            'chunk_type::nhed': nhed_body
            'chunk_type::sspc': sspc_body
            'chunk_type::ldta': ldta_body
            'chunk_type::opti': opti_body
            _: ascii_body
      - id: padding
        type: u1
        if: (block_size % 2) != 0
  list_body:
    seq:
      - id: identifier
        type: str
        encoding: cp1252
        size: 4
      - id: blocks
        type: blocks
  utf8_body:
    seq:
      - id: data
        type: str
        encoding: utf8
        size-eos: true
  ascii_body:
    seq:
      - id: data
        size-eos: true
  idta_body:
    seq:
      - id: item_type
        type: u2
        enum: item_type
      - id: unknown01
        size: 14
      - id: item_id
        type: u4
  fdta_body:
    seq:
      - id: unknown01
        size: 1
  cdta_body:
    seq:
      - id: unknown01
        size: 4 # 0-4
      - id: framerate_divisor
        type: u4 # 4-8
      - id: framerate_dividend
        type: u4 # 8-12
      - id: unknown02
        size: 32 # 12-44
      - id: seconds_dividend
        type: u4 # 44-48
      - id: seconds_divisor
        type: u4 # 48-52
      - id: background_color
        type: str
        size: 3 # 52-55
        encoding: cp1252
      - id: unknown03
        size: 85 # 55-140
      - id: width
        type: u2 # 140-142
      - id: height
        type: u2 # 142-144
      - id: unknown04
        size: 12 # 144-156
      - id: frame_rate
        type: u2 # 156-158
  nhed_body:
    seq:
      - id: unknown01
        size: 15
      - id: depth
        type: u2
        enum: depth
  sspc_body:
    seq:
      - id: unknown01
        size: 30 # 0-30
      - id: width
        type: u4 # 30-34
      - id: height
        type: u4 # 34-38
      - id: seconds_dividend
        type: u4 # 38-42
      - id: seconds_divisor
        type: u4 # 42-46
      - id: unknown02
        size: 10 # 46-56
      - id: framerate
        type: u4 # 56-60
      - id: framerate_dividend
        type: u2 # 60-62
  opti_body:
    seq:
      - id: unknown01
        size: 4 # 0-4
      - id: footage_type
        type: u2 # 4-6
        enum: footage_type
      - id: unknown02
        size: 'footage_type == footage_type::solid ? 20 : 4' # 6-26 or 6-10
      - id: name
        type: str
        encoding: cp1252
        size: 'footage_type == footage_type::solid ? 229 : 245' #26-255 or 10-255
  ldta_body:
    seq:
      - id: unknown01
        size: 4 # 0-4
      - id: quality
        type: u2 # 4-6
      - id: unknown02
        size: 31 # 6-37
      - id: layer_attr_bits
        size: 3 # 37-40
      - id: source_id
        type: u4 # 40-44
    instances:
      guide_enabled:
        value: '((layer_attr_bits[0] & (1 << 1)) >> 1) == 1'
      frame_blend_mode:
        value: '((layer_attr_bits[0] & (1 << 2)) >> 2)'
      sampling_mode:
        value: '((layer_attr_bits[0] & (1 << 6)) >> 6)'
      adjustment_layer_enabled:
        value: '((layer_attr_bits[1] & (1 << 1)) >> 1) == 1'
      three_d_enabled:
        value: '((layer_attr_bits[1] & (1 << 2)) >> 2) == 1'
      solo_enabled:
        value: '((layer_attr_bits[1] & (1 << 3)) >> 3) == 1'
      video_enabled:
        value: '((layer_attr_bits[2] & (1 << 0)) >> 0) == 1'
      audio_enabled:
        value: '((layer_attr_bits[2] & (1 << 1)) >> 1) == 1'
      effects_enabled:
        value: '((layer_attr_bits[2] & (1 << 2)) >> 2) == 1'
      motion_blur_enabled:
        value: '((layer_attr_bits[2] & (1 << 3)) >> 3) == 1'
      frame_blend_enabled:
        value: '((layer_attr_bits[2] & (1 << 4)) >> 4) == 1'
      lock_enabled:
        value: '((layer_attr_bits[2] & (1 << 5)) >> 5) == 1'
      shy_enabled:
        value: '((layer_attr_bits[2] & (1 << 6)) >> 6) == 1'
      collapse_transform_enabled:
        value: '((layer_attr_bits[2] & (1 << 7)) >> 7) == 1'

enums:
  chunk_type:
    0x4c495354:
      id: lst
      doc: List data
    0x55746638: utf8
    0x63647461:
      id: cdta
      doc: Composition data
    0x69647461:
      id: idta
      doc: Item data
    0x636d7461:
      id: cmta
      doc: Comment data
    0x66647461:
      id: fdta
      doc: Folder data
    0x6E686564:
      id: nhed
      doc: Header data
    0x73737063:
      id: sspc
      doc: Sub properties ?
    0x6c647461:
      id: ldta
      doc: Layer data
    0x6f707469:
      id: opti
      doc: Footage data
    0x74646770:
      id: tdgp
      doc: Transform properties group
    0x67647461:
      id: gdta
      doc: ?? data
    0x73766170: svap
    0x68656164: head
    0x6e6e6864: nnhd
    0x61646672: adfr
    0x71746c67: qtlg
    0x73666964: sfid
    0x61636572: acer
    0x63706964: cpid
    0x64776761: dwga
    0x6e756d53: nums
    0x63647270: cdrp
    0x7072696e: prin
    0x70726461: prda
    0x74647362: tdsb
    0x7464736e: tdsn
    0x74646d6e: tdmn
    0x7464756d: tdum
    0x74646234: tdb4
    0x63646174: cdat
    0x43707243: cprc
    0x43734374: csct
    0x4361704c: capl
    0x4350546d: cptm
    0x43524f49: croi
    0x43634374: ccct
    0x6f746c6e: otln
    0x73657120: seq
    0x41437369: acsi
    0x41437369: acsi
    0x66766476: fvdv
    0x66696f70: fiop
    0x66747473: ftts
    0x666f6163: foac
    0x666f7473: fots
    0x666f7474: fott
    0x666f7663: fovc
    0x666f7669: fovi
    0x66696163: fiac
    0x66697473: fits
    0x66697474: fitt
    0x66697663: fivc
    0x66697669: fivi
    0x66697063: fipc
    0x66696469: fidi
    0x6669706c: fipl
    0x66696d72: fimr
    0x66697073: fips
    0x6669666c: fifl
    0x77736e73: wsns
    0x77736e6d: wsnm
    0x66636964: fcid
    0x6f616363: oacc
    0x41467369: afsi
    0x52686564: rhed
    0x526f7574: rout
    0x6c686433: lhd3
    0x41527369: arsi
    0x66747764: ftwd
  depth: # project bit depth
    0x00: bpc_8
    0x01: bpc_16
    0x02: bpc_32
  footage_type:
    0x09: solid
    0x02: placeholder
  item_type: # type of item. See: http://docs.aenhancers.com/items/item/#item-item_type
    0x01:
      id: folder
      doc: Folder item which may contain additional items
    0x04:
      id: composition
      doc: Composition item which has a dimension, length, framerate and child layers
    0x07:
      id: footage
      doc: AVItem that has a source (an image or video file)
