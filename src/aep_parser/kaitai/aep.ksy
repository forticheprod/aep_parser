meta:
  id: aep
  endian: be
  file-extension: aep

seq:
  - id: header
    contents: [0x52, 0x49, 0x46, 0x58]
    doc: RIFF
  - id: file_size
    type: u4
  - id: format
    contents: [0x45, 0x67, 0x67, 0x21]
    doc: Egg!
  - id: data
    type: chunks
    size: file_size - format._sizeof
  - id: xmp
    type: str
    encoding: utf8
    size-eos: true
    
types:
  chunks:
    seq:
      - id: chunks
        type: chunk
        repeat: eos
  chunk:
    seq: 
      - id: chunk_type
        size: 4
        type: str
        encoding: ascii
      - id: chunk_size
        type: u4
      - id: data
        size: 'chunk_size > _io.size - _io.pos ? _io.size - _io.pos : chunk_size'
        type: 
          switch-on: chunk_type
          cases:
            '"alas"': utf8_body # File asset data in json format as a string
            '"cdat"': cdat_body # Property value(s)
            '"cdta"': cdta_body # Composition data
            '"cmta"': utf8_body # Comment data
            '"fdta"': fdta_body # Folder data
            '"head"': head_body # contains AE version and file revision
            '"idta"': idta_body # Item data
            '"ldat"': ldat_body # Data of a keyframe
            '"ldta"': ldta_body # Layer data
            '"lhd3"': lhd3_body # Number of keyframes of a property
            '"LIST"': list_body # List of chunks
            '"nhed"': nhed_body # Header data
            '"NmHd"': nmhd_body # Marker data
            '"nnhd"': nnhd_body # Project data
            '"opti"': opti_body # Asset data
            '"pard"': pard_body # property ??
            '"pjef"': utf8_body # effect names
            '"sspc"': sspc_body # Sub properties ??
            '"tdb4"': tdb4_body # property metadata
            '"tdmn"': utf8_body # Transform property group end
            '"tdsb"': tdsb_body # transform property group flags
            '"Utf8"': utf8_body
            '"fnam"': child_utf8_body # Effect name. contains a single utf-8 chunk but no list_type
            '"pdnm"': child_utf8_body # Parameter control strings. contains a single utf-8 chunk but no list_type
            '"tdsn"': child_utf8_body # user-defined label of a property. contains a single utf-8 chunk but no list_type
            # '"fiac"': ascii_body # active item, not sure about encoding
            _: ascii_body
      - id: padding
        size: 1
        if: (chunk_size % 2) != 0
  alas_body:
    seq:
      - id: contents
        type: str
        size-eos: true
        encoding: ascii
  ascii_body:
    seq:
      - id: data
        size-eos: true
  cdat_body:
    seq:
      - id: value
        type: f8
        repeat: expr
        repeat-expr: '_parent.chunk_size / 8'
  cdta_body:
    seq:
      - id: x_resolution
        type: u2 # 1-2
      - id: y_resolution
        type: u2 # 3-4
      - id: unknown01
        size: 2 # 5-6
      - id: time_scale
        type: u2 # 7-8
      - id: unknown02
        size: 2 # 9-10
      - id: framerate_dividend
        type: u2 # 11-12
      - id: unknown03
        size: 9 # 13-21
      - id: playhead
        type: u2 # 22-23
      - id: unknown04
        size: 6 # 24-29
      - id: in_time
        type: u2 # 30-31
      - id: unknown05
        size: 6 # 32-37
      - id: out_time_raw
        type: u2 # 38-39
      - id: unknown06
        size: 5 # 40-44
      - id: duration_dividend
        type: u4 # 45-48
      - id: duration_divisor
        type: u4 # 49-52
      - id: background_color
        type: u1 # 53-55
        repeat: expr
        repeat-expr: 3
      - id: unknown08
        size: 84 # 56-139
      - id: attributes
        size: 1 # 140
      - id: width
        type: u2 # 141-142
      - id: height
        type: u2 # 143-144
      - id: pixel_ratio_width
        type: u4 # 145-148
      - id: pixel_ratio_height
        type: u4 # 149-152
      - id: unknown09
        size: 4 # 153-156
      - id: frame_rate_integer
        type: u2 # 157-158
      - id: unknown10
        size: 16 # 159-174
      - id: shutter_angle
        type: u2 # 175-176
      - id: shutter_phase
        type: u4 # 177-180
      - id: unknown11
        size: 16 # 181-196
      - id: samples_limit
        type: s4 # 197-200
      - id: samples_per_frame
        type: s4 # 201-204
    instances:
      framerate:
        value: 'framerate_dividend.as<f4> / time_scale.as<f4>'
      duration_sec:
        value: 'duration_dividend.as<f4> / duration_divisor.as<f4>'
      out_time:
        value: 'out_time_raw == 0xffff ? duration_sec : out_time_raw'
      pixel_ratio:
        value: 'pixel_ratio_width.as<f4> / pixel_ratio_height.as<f4>'
      playhead_frames:
        value: 'playhead * framerate'
      in_time_frames:
        value: 'in_time * framerate'
      out_time_frames:
        value: 'out_time * framerate'
      duration_frames:
        value: 'duration_sec * framerate'
      shy_enabled:
        value: '(attributes[0] & 1) != 0'
      motion_blur_enabled:
        value: '(attributes[0] & (1 << 3)) != 0'
      frame_blend_enabled:
        value: '(attributes[0] & (1 << 4)) != 0'
      preserve_framerate:
        value: '(attributes[0] & (1 << 5)) != 0'
      preserve_resolution:
        value: '(attributes[0] & (1 << 7)) != 0'
  child_utf8_body:
    seq:
      - id: chunk
        type: chunk
  fdta_body:
    seq:
      - id: unknown01
        size: 1
  head_body:
    seq:
      - id: ae_version
        size: 6
        # enum: ae_version
      - id: unknown01
        size: 12
      - id: file_revision
        type: u2
  idta_body:
    seq:
      - id: item_type
        type: u2
        enum: item_type
      - id: unknown01
        size: 14
      - id: item_id
        type: u4
      - id: unknown02
        size: 38
      - id: label_color
        type: u1
        enum: label_color
  ldat_body:
    seq:
      - id: unknown01
        size: 1
      - id: time
        type: s2
      - id: unknown02
        size: 2
      - id: ease_mode
        type: u1
        enum: ease_mode
      - id: label_color
        type: u1
        enum: label_color
      - id: attributes
        size: 1
    instances:
      continuous_bezier:
        value: '(attributes[0] & (1 << 3)) != 0'
      auto_bezier:
        value: '(attributes[0] & (1 << 4)) != 0'
      roving_across_time:
        value: '(attributes[0] & (1 << 5)) != 0'
  ldta_body:
    seq:
      - id: layer_id
        type: u4 # 1-4
      - id: quality
        type: u2 # 5-6
        enum: layer_quality
      - id: unknown01
        size: 4 # 7-10
      - id: stretch_numerator
        type: u2 # 11-12
      - id: unknown02
        size: 1 # 13
      - id: start_time_sec
        type: s2 # 14-15
      - id: unknown03
        size: 6 # 16-21
      - id: in_time_sec
        type: u2 # 22-23
      - id: unknown04
        size: 6 # 24-29
      - id: out_time_sec
        type: u2 # 30-31
      - id: unknown05
        size: 6 # 32-37
      - id: attributes
        size: 3 # 38-40
      - id: source_id
        type: u4 # 41-44
      - id: unknown06
        size: 17 # 45-61
      - id: label_color
        type: u1 # 62
        enum: label_color
      - id: unknown07
        size: 2 # 63-64
      - id: layer_name
        size: 32 # 65-96
        type: str
        encoding: cp1250
      - id: unknown08
        size: 11 # 97-107
      - id: matte_mode
        type: u1 # 108
        enum: matte_mode
      - id: unknown09
        size: 2 # 109-110
      - id: stretch_denominator
        type: u2 # 111-112
      - id: unknown10
        size: 19 # 113-131
      - id: layer_type
        type: u1 # 132
        enum: layer_type
      - id: parent_id
        type: u4 # 133-136
      - id: unknown11
        size: 24 # 137-160
      # - id: matte_layer_id
      #   type: u4 # 161-164
      #   doc: only for AE >= 23
    instances:
      guide_enabled:
        value: '(attributes[0] & (1 << 1)) != 0'
      frame_blend_mode:
        value: '(attributes[0] & (1 << 2)) >> 2'
        enum: layer_frame_blend_mode
      sampling_mode:
        value: '(attributes[0] & (1 << 6)) >> 6'
        enum: layer_sampling_mode
      auto_orient:
        value: '(attributes[1] & 1) != 0'
      adjustment_layer_enabled:
        value: '(attributes[1] & (1 << 1)) != 0'
      three_d_enabled:
        value: '(attributes[1] & (1 << 2)) != 0'
      solo_enabled:
        value: '(attributes[1] & (1 << 3)) != 0'
      markers_locked:
        value: '(attributes[1] & (1 << 4)) != 0'
      null_layer:
        value: '(attributes[1] & (1 << 7)) != 0'
      video_enabled:
        value: '(attributes[2] & (1 << 0)) != 0'
      audio_enabled:
        value: '(attributes[2] & (1 << 1)) != 0'
      effects_enabled:
        value: '(attributes[2] & (1 << 2)) != 0'
      motion_blur_enabled:
        value: '(attributes[2] & (1 << 3)) != 0'
      frame_blend_enabled:
        value: '(attributes[2] & (1 << 4)) != 0'
      lock_enabled:
        value: '(attributes[2] & (1 << 5)) != 0'
      shy_enabled:
        value: '(attributes[2] & (1 << 6)) != 0'
      collapse_transform_enabled:
        value: '(attributes[2] & (1 << 7)) != 0'
  lhd3_body:
    seq:
      - id: unknown01
        size: 10
      - id: keyframes_count
        type: u2
      - id: unknown03
        size: 6
      - id: keyframes_size
        type: u2
      - id: unknown05
        size: 3
      - id: keyframes_type
        type: u1
    instances:
      items_type:
        value: >-
          keyframes_type == 1 ? (keyframes_size == 128 ? "LItm" : "LRdr" )
          : keyframes_type == 2 ? "Gide"
          : keyframes_size == 152 ? "color_keyframe"
          : keyframes_size == 48 ? "one_d_keyframe"
          : keyframes_size == 88 ? "two_d_keyframe"
          : keyframes_size == 104 ? "two_d_pos_keyframe"
          : keyframes_size == 128 ? "three_d_keyframe"
          : keyframes_size == 16 ? "marker_keyframe"
          : keyframes_size == 80 ? "orientation_keyframe"
          : keyframes_size == 64 ? "no_value_keyframe"
          : "unknown_keyframe"
  list_body:
    seq:
      - id: list_type
        type: str
        encoding: cp1250
        size: 4
      - id: chunks
        type: chunk
        repeat: eos
        if: list_type != "btdk"
      - id: binary_data
        size-eos: true
        if: list_type == "btdk"
  nhed_body:
    seq:
      - id: unknown01
        size: 15
      - id: depth
        type: u1
        enum: depth
  nmhd_body:
    seq:
      - id: unknown01
        size: 3
      - id: attributes
        size: 1
      - id: unknown02
        size: 4
      - id: duration_frames
        type: u4
      - id: unknown03
        size: 4
      - id: label_color
        type: u1
        enum: label_color
    instances:
      protected:
        value: '(attributes[0] & (1 << 1)) != 0'
      unknown:
        value: '(attributes[0] & (1 << 2)) != 0'
  nnhd_body:
    seq:
      - id: unknown01
        size: 14
      - id: framerate
        type: u2
      - id: unknown02
        size: 24
  opti_body:
    seq:
      - id: asset_type
        size: 4 # 1-4
        type: str
        encoding: ascii
        # enum: asset_type
      - id: asset_type_int
        type: u2 # 5-6
      - id: unknown02
        size: 4 # 7-10
        if: asset_type == "Soli"
      - id: color
        type: f4 # 11-14
        repeat: expr
        repeat-expr: 4
        if: asset_type == "Soli"
      - id: solid_name
        type: strz
        encoding: cp1250
        size: 256 # 27-282
        if: asset_type == "Soli"
      - id: unknown03
        size: 4 # 7-10
        if: asset_type_int == 2
      - id: placeholder_name
        type: strz
        encoding: cp1250
        size-eos: true # 11-268
        if: asset_type_int == 2
    instances:
      red:
        value: 'color[1]'
        if: asset_type == "Soli"
      green:
        value: 'color[2]'
        if: asset_type == "Soli"
      blue:
        value: 'color[3]'
        if: asset_type == "Soli"
      alpha:
        value: 'color[0]'
        if: asset_type == "Soli"
  pard_body:
    seq:
      - id: unknown01
        size: 15 # 1-15
      - id: property_type
        type: u1 # 16
        enum: property_type
      - id: name
        size: 32 # 17-48
        type: str
        encoding: cp1250
      - id: unknown02
        size: 8 # 49-56
      - id: last_color
        type: u1 #
        repeat: expr
        repeat-expr: 4
        if: property_type == property_type::color
      - id: default_color
        type: u1 #
        repeat: expr
        repeat-expr: 4
        if: property_type == property_type::color
      - id: last_value
        type: 
          switch-on: property_type
          cases:
            'property_type::scalar': s4
            'property_type::angle': s4
            'property_type::boolean': u4
            'property_type::enum': u4
            'property_type::slider': f8
        if: >-
          property_type == property_type::scalar
          or property_type == property_type::angle
          or property_type == property_type::boolean
          or property_type == property_type::enum
          or property_type == property_type::slider
      - id: last_value_x_raw
        type: 
          switch-on: property_type
          cases:
            'property_type::two_d': s4
            'property_type::three_d': f8
        if: >-
          property_type == property_type::two_d
          or property_type == property_type::three_d
      - id: last_value_y_raw
        type: 
          switch-on: property_type
          cases:
            'property_type::two_d': s4
            'property_type::three_d': f8
        if: >-
          property_type == property_type::two_d
          or property_type == property_type::three_d
      - id: last_value_z_raw
        type: f8
        if: property_type == property_type::three_d
      - id: option_count
        type: s4
        if: property_type == property_type::enum
      - id: default
        type: 
          switch-on: property_type
          cases:
            'property_type::boolean': u1
            'property_type::enum': s4
        if: >-
          property_type == property_type::boolean
          or property_type == property_type::enum
      - id: unknown03
        size: '(property_type == property_type::scalar ? 72 : property_type == property_type::color ? 64 : 52)'
        if: >-
          property_type == property_type::scalar
          or property_type == property_type::color
          or property_type == property_type::slider
      - id: min_value
        type: s2
        if: property_type == property_type::scalar
      - id: unknown04
        size: 2
        if: property_type == property_type::scalar
      - id: max_color
        type: u1 # 53-55
        repeat: expr
        repeat-expr: 4
        if: property_type == property_type::color
      - id: max_value
        type:
          switch-on: property_type
          cases:
            'property_type::scalar': s2
            'property_type::slider': f4
        if: >-
          property_type == property_type::scalar
          or property_type == property_type::slider
    instances:
      last_value_x:
        value: 'last_value_x_raw * (property_type == property_type::two_d ? 1/128 : 512)'
        if: >-
          property_type == property_type::two_d
          or property_type == property_type::three_d
      last_value_y:
        value: 'last_value_y_raw * (property_type == property_type::two_d ? 1/128 : 512)'
        if: >-
          property_type == property_type::two_d
          or property_type == property_type::three_d
      last_value_z:
        value: 'last_value_z_raw * 512'
        if: property_type == property_type::three_d
  sspc_body:
    seq:
      - id: unknown01
        size: 32 # 1-32
      - id: width
        type: u2 # 33-34
      - id: unknown02
        size: 2 # 35-36
      - id: height
        type: u2 # 37-38
      - id: duration_dividend
        type: u4 # 39-42
      - id: duration_divisor
        type: u4 # 43-46
      - id: unknown03
        size: 10 # 47-56
      - id: framerate_base
        type: u4 # 57-60
      - id: framerate_dividend
        type: u2 # 61-62
      - id: unknown04
        size: 110 # 61-62
      - id: start_frame
        type: u4 # 61-62
      - id: end_frame
        type: u4 # 61-62
    instances:
      duration_sec:
        value: 'duration_dividend.as<f4> / duration_divisor.as<f4>'
      framerate:
        value: 'framerate_base + (framerate_dividend.as<f4> / (1 << 16))'
      duration_frames:
        value: 'duration_sec * framerate'
  tdb4_body:
    seq:
      - id: unknown01
        size: 2
      - id: components
        type: u2
        doc: Number of values in a multi-dimensional
      - id: attributes
        size: 2
      - id: unknown02
        size: 1
      - id: unknown03
        size: 1
        doc: Some sort of flag, it has value 03 for position properties
      - id: unknown04
        size: 2
      - id: unknown05
        size: 2
      - id: unknown06
        size: 2
        doc: Always 0000 ?
      - id: unknown07
        size: 2
        doc: 2nd most significant bit always on, perhaps some kind of flag
      - id: unknown08
        type: f8
        doc: Most of the time 0.0001
      - id: unknown09
        type: f8
        doc: Most of the time 1.0, sometimes 1.777
      - id: unknown10
        type: f8
        doc: Always 1.0?
      - id: unknown11
        type: f8
        doc: Always 1.0?
      - id: unknown12
        type: f8
        doc: Always 1.0?
      - id: property_type
        size: 4
      - id: unknown13
        size: 1
        doc: Seems correlated with the previous byte, 04 for enum properties
      - id: unknown14
        size: 7
        doc: Bunch of 00
      - id: animated
        type: u1
      - id: unknown15
        size: 7
        doc: Bunch of 00
      - id: unknown16
        size: 4
        doc: Usually 0, probs flags
      - id: unknown17
        size: 4
        doc: Most likely flags, only last byte seems to contain data
      - id: unknown18
        type: f8
        doc: Always 0.0?
      - id: unknown19
        type: f8
        doc: Mostly 0.0, sometimes 0.333
      - id: unknown20
        type: f8
        doc: Always 0.0?
      - id: unknown21
        type: f8
        doc: Mostly 0.0, sometimes 0.333
      - id: unknown22
        size: 4
        doc: Probs some flags
      - id: unknown23
        size: 4
        doc: Probs some flags
    instances:
      static:
        value: '(attributes[1] & 1) != 0'
      position:
        value: '(attributes[1] & (1 << 3)) != 0'
      no_value:
        value: '(property_type[1] & 1) != 0'
      color:
        value: '(property_type[3] & 1) != 0'
      integer:
        value: '(property_type[3] & (1 << 2)) != 0'
      vector:
        value: '(property_type[3] & (1 << 3)) != 0'
  tdsb_body:
    seq:
      - id: flags
        size: 4
    instances:
      locked_ratio:
        value: '(flags[2] & 1 << 4) != 0'
      visible:
        value: '(flags[3] & 1) != 0'
      split_position:
        value: '(flags[3] & 1 << 1) != 0'
  utf8_body:
    seq:
      - id: data
        type: str
        encoding: utf8
        size-eos: true

enums:
  depth: # project bit depth
    0: bpc_8
    1: bpc_16
    2: bpc_32
  item_type: # type of item. See: http://docs.aenhancers.com/items/item/#item-item_type
    1: folder
    4: composition
    7: asset
  asset_type:
    2: placeholder
    9: solid
  layer_type:
    0: asset
    1: light
    2: camera
    3: text
    4: shape
  matte_mode:
    0: none
    1: no_matte
    2: alpha
    3: inverted_alpha
    4: luma
    5: inverted_luma
  label_color:
    0: none
    1: red
    2: yellow
    3: aqua
    4: pink
    5: lavender
    6: peach
    7: sea_foam
    8: blue
    9: green
    10: purple
    11: orange
    12: brown
    13: fuchsia
    14: cyan
    15: sandstone
    16: dark_green
  property_type:
    0: layer
    # 1: integer ?
    2: scalar
    3: angle
    4: boolean
    5: color
    6: two_d
    7: enum
    9: paint_group
    10: slider
    11: curve
    # 12: mask ?
    13: group
    # 14: ??
    15: unknown
    18: three_d
  layer_quality:
    0: wireframe
    1: draft
    2: best
  layer_frame_blend_mode:
    0: frame_mix
    1: pixel_motion
  layer_sampling_mode:
    0: bilinear
    1: bicubic
  ease_mode:
    1: linear
    2: ease
    3: hold
  # ae_version:
  #   0x5c06073806b4: 15.0
  #   0x5d040b0006eb: 16.0
  #   0x5d040b000e30: 16.0.1
  #   0x5d050b009637: 16.1.2
  #   0x5d050b009e05: 16.1.3
  #   0x5d094b08062b: 17.0
  #   0x5d0b0b08263b: 17.0.4
  #   0x5d1b0b110e08: 18.2.1
  #   0x5d1d0b120626: 18.4
  #   0x5d1d0b70066f: 22.0
  #   0x5d2b0b33063b: 22.6
  #   0x5e030b390e03: 23.2.1