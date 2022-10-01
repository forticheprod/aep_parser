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
      - id: entries
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
            'chunk_type::list': list_body
            'chunk_type::utf8': utf8_body
            'chunk_type::cdta': cdta_body
            'chunk_type::idta': idta_body
            'chunk_type::cmta': utf8_body
            'chunk_type::fdta': fdta_body
            _: ascii_body
      - id: padding
        type: u1
        if: (block_size % 2) != 0
  list_body:
    seq:
      - id: identifier
        type: str
        encoding: ascii
        size: 4
      - id: entries
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
        type: str
        encoding: ascii
        size-eos: true
  idta_body:
    seq:
      - id: unknown1
        type: str
        size: 18
        encoding: ascii
      - id: id
        type: u2
  fdta_body:
    seq:
      - id: unknown1
        type: str
        encoding: ascii
        size: 1
  cdta_body:
    seq:
      - id: unknown1
        type: str
        size: 140
        encoding: ascii
      - id: width
        type: u2
      - id: height
        type: u2
      - id: unknown2
        type: str
        size: 12
        encoding: ascii
      - id: frame_rate
        type: u2
        
enums:
  chunk_type:
    0x4c495354: list
    0x55746638: utf8
    0x63647461: cdta # Composition data
    0x69647461: idta # Item data
    0x636d7461: cmta # Comment data
    0x66647461: fdta # Folder data
