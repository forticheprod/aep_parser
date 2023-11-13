meta:
  id: aep
  endian: be
  file-extension: aep

seq:
  - id: header
    contents: [0x52, 0x49, 0x46, 0x58]
    doc: RIFX
  - id: len_data
    type: u4
  - id: format
    contents: [0x45, 0x67, 0x67, 0x21]
    doc: Egg!
  - id: data
    type: chunks
    size: len_data - format._sizeof
  - id: xmp_packet
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
      - id: len_data
        type: u4
      - id: data
        size: 'len_data > _io.size - _io.pos ? _io.size - _io.pos : len_data'
        type:
          switch-on: chunk_type
          cases:
            '"LIST"': list_body # List of chunks
            '"tdmn"': utf8_body # Property or parameter name
            '"Utf8"': utf8_body # Contains text
            '"tdsb"': tdsb_body # Transform property group flags
            '"tdsn"': child_utf8_body # User-defined name of a property. Contains a single utf-8 chunk but no list_type
            '"tdb4"': tdb4_body # Property metadata
            '"cdat"': cdat_body # Property value(s)
            '"pard"': pard_body # Property default values and ranges
            '"lhd3"': lhd3_body # Number of keyframes and keyframe size for a property
            '"ldta"': ldta_body # Layer data
            '"pdnm"': child_utf8_body # Parameter control strings. Contains a single utf-8 chunk but no list_type
            '"ldat"': ldat_body # Data of a keyframe
            '"sspc"': sspc_body # Footage data
            '"fnam"': child_utf8_body # Effect name. Contains a single utf-8 chunk but no list_type
            '"idta"': idta_body # Item data
            '"opti"': opti_body # Footage data
            '"alas"': utf8_body # File footage data in json format as a string, contains file path
            '"NmHd"': nmhd_body # Marker data
            '"cdta"': cdta_body # Composition data
            '"pjef"': utf8_body # Effect names
            '"cmta"': utf8_body # Comment data
            '"fdta"': fdta_body # Folder data
            '"nnhd"': nnhd_body # Project data
            '"head"': head_body # Contains AE version and file revision
            _: ascii_body
      - id: padding
        size: 1
        if: (len_data % 2) != 0
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
        repeat-expr: '_parent.len_data / 8'
  cdta_body:
    seq:
      - id: resolution_factor
        type: u2
        repeat: expr
        repeat-expr: 2
      - size: 1
      - id: time_scale
        type: u2
      - size: 2
      - id: frame_rate_dividend
        type: u2
      - size: 10
      - id: time_raw
        type: u2
      - size: 6
      - id: in_point_raw
        type: u2
      - size: 6
      - id: out_point_raw
        type: u2
      - size: 5
      - id: duration_dividend
        type: u4
      - id: duration_divisor
        type: u4
      - id: bg_color
        type: u1
        repeat: expr
        repeat-expr: 3
      - size: 84
      - id: attributes
        size: 1
      - id: width
        type: u2
      - id: height
        type: u2
      - id: pixel_ratio_width
        type: u4
      - id: pixel_ratio_height
        type: u4
      - size: 4
      - id: frame_rate_integer  # probably a divisor
        type: u2
      - size: 6
      - id: display_start_time_dividend
        type: u4
      - id: display_start_time_divisor
        type: u4
      - size: 2
      - id: shutter_angle
        type: u2
      - id: shutter_phase
        type: u4
      - size: 16
      - id: motion_blur_adaptive_sample_limit
        type: s4
      - id: motion_blur_samples_per_frame
        type: s4
    instances:
      display_start_time:
        value: 'display_start_time_dividend.as<f4> / display_start_time_divisor.as<f4>'
      frame_rate:
        value: 'frame_rate_dividend.as<f4> / time_scale.as<f4>'
      display_start_frame:
        value: 'display_start_time * frame_rate'
      duration:
        value: 'duration_dividend.as<f4> / duration_divisor.as<f4>'
      frame_duration:
        value: 'duration * frame_rate'
      display_start_time:
        value: 'display_start_frame.as<f4> / frame_rate'
      pixel_aspect:
        value: 'pixel_ratio_width.as<f4> / pixel_ratio_height.as<f4>'
      frame_time:
        value: 'time_raw / time_scale'
      time:
        value: 'frame_time / frame_rate'
      frame_in_point:
        value: 'display_start_frame + in_point_raw / time_scale'
      in_point:
        value: 'frame_in_point / frame_rate'
      frame_out_point:
        value: 'display_start_frame + (out_point_raw == 0xffff ? frame_duration : (out_point_raw / time_scale))'
      out_point:
        value: 'frame_out_point / frame_rate'
      hide_shy_layers:
        value: '(attributes[0] & 1) != 0'
      motion_blur:
        value: '(attributes[0] & (1 << 3)) != 0'
      frame_blending:
        value: '(attributes[0] & (1 << 4)) != 0'
      preserve_nested_frame_rate:
        value: '(attributes[0] & (1 << 5)) != 0'
      preserve_nested_resolution:
        value: '(attributes[0] & (1 << 7)) != 0'
  child_utf8_body:
    seq:
      - id: chunk
        type: chunk
  fdta_body:
    seq:
      - size: 1
  head_body:
    seq:
      - id: ae_version
        size: 6
        # enum: ae_version
      - size: 12
      - id: file_revision
        type: u2
  idta_body:
    seq:
      - id: item_type
        type: u2
        enum: item_type
      - size: 14
      - id: item_id
        type: u4
      - size: 38
      - id: label
        type: u1
        enum: label
  ldat_body:
    seq:
      - id: keyframes
        size-eos: true
  keyframe:
    params:
      - id: key_type
        type: u1
        enum: property_value_type
    seq:
      - size: 1
      - id: time_raw
        type: u2
      - size: 2
      - id: keyframe_interpolation_type
        type: u1
        enum: keyframe_interpolation_type
      - id: label
        type: u1
        enum: label
      - id: attributes
        size: 1
      - id: kf_data
        type:
          switch-on: key_type
          cases:
            'property_value_type::unknown': kf_unknown_data
            'property_value_type::lrdr': kf_unknown_data
            'property_value_type::litm': kf_unknown_data
            'property_value_type::gide': kf_unknown_data
            'property_value_type::color': kf_color
            'property_value_type::three_d_spatial': kf_position(3)
            'property_value_type::three_d': kf_multi_dimensional(3)
            'property_value_type::two_d_spatial': kf_position(2)
            'property_value_type::two_d': kf_multi_dimensional(2)
            'property_value_type::orientation': kf_multi_dimensional(1)
            'property_value_type::no_value': kf_no_value
            'property_value_type::one_d': kf_multi_dimensional(1)
            'property_value_type::marker': kf_unknown_data
    instances:
      continuous_bezier:
        value: '(attributes[0] & (1 << 3)) != 0'
      auto_bezier:
        value: '(attributes[0] & (1 << 4)) != 0'
      roving_across_time:
        value: '(attributes[0] & (1 << 5)) != 0'
  kf_unknown_data:
    seq:
      - id: data
        size-eos: true
  kf_no_value:
    seq:
      - type: u8
      - type: f8
      - id: in_speed
        type: f8
      - id: in_influence
        type: f8
      - id: out_speed
        type: f8
      - id: out_influence
        type: f8
  kf_color:
    seq:
      - type: u8
      - type: f8
      - id: in_speed
        type: f8
      - id: in_influence
        type: f8
      - id: out_speed
        type: f8
      - id: out_influence
        type: f8
      - id: value
        type: f8
        repeat: expr
        repeat-expr: 4
      - type: f8
        repeat: expr
        repeat-expr: 8
  kf_position:
    params:
      - id: nb_dimensions
        type: u1
    seq:
      - type: u8
      - type: f8
      - id: in_speed
        type: f8
      - id: in_influence
        type: f8
      - id: out_speed
        type: f8
      - id: out_influence
        type: f8
      - id: value
        type: f8
        repeat: expr
        repeat-expr: nb_dimensions
      - id: tan_in
        type: f8
        repeat: expr
        repeat-expr: nb_dimensions
      - id: tan_out
        type: f8
        repeat: expr
        repeat-expr: nb_dimensions
  kf_multi_dimensional:
    params:
      - id: nb_dimensions
        type: u1
    seq:
      - id: value
        type: f8
        repeat: expr
        repeat-expr: nb_dimensions
      - id: in_speed
        type: f8
        repeat: expr
        repeat-expr: nb_dimensions
      - id: in_influence
        type: f8
        repeat: expr
        repeat-expr: nb_dimensions
      - id: out_speed
        type: f8
        repeat: expr
        repeat-expr: nb_dimensions
      - id: out_influence
        type: f8
        repeat: expr
        repeat-expr: nb_dimensions
  ldta_body:
    seq:
      - id: layer_id
        type: u4
      - id: quality
        type: u2
        enum: layer_quality
      - size: 4
      - id: stretch_dividend
        type: u2
      - id: start_time_dividend
        type: u4
      - id: start_time_divisor
        type: u4
      - id: in_point_dividend
        type: u4
      - id: in_point_divisor
        type: u4
      - id: out_point_dividend
        type: u4
      - id: out_point_divisor
        type: u4
      - size: 1
      - id: attributes
        size: 3
      - id: source_id
        type: u4
      - size: 17
      - id: label
        type: u1
        enum: label
      - size: 2
      - id: layer_name
        size: 32
        type: str
        encoding: cp1250
      - size: 3
      - id: blending_mode
        type: u1
        enum: blending_mode
      - size: 3
      - id: preserve_transparency
        type: u1
      - size: 3
      - id: track_matte_type
        type: u1
        enum: track_matte_type
      - size: 2
      - id: stretch_divisor
        type: u2
      - size: 19
      - id: layer_type
        type: u1
        enum: layer_type
      - id: parent_id
        type: u4
      - size: 24
      # - id: matte_layer_id
      #   type: u4
      #   doc: only for AE >= 23
    instances:
      start_time:
        value: 'start_time_dividend.as<f4> / start_time_divisor.as<f4>'
      in_point:
        value: 'in_point_dividend.as<f4> / in_point_divisor.as<f4>'
      out_point:
        value: 'out_point_dividend.as<f4> / out_point_divisor.as<f4>'
      environment_layer:
        value: '(attributes[0] & (1 << 5)) != 0'
      guide_layer:
        value: '(attributes[0] & (1 << 1)) != 0'
      frame_blending_type:
        value: '(attributes[0] & (1 << 2)) >> 2'
        enum: frame_blending_type
      sampling_quality:
        value: '(attributes[0] & (1 << 6)) >> 6'
        enum: sampling_quality
      auto_orient:
        value: '(attributes[1] & 1) != 0'
      adjustment_layer:
        value: '(attributes[1] & (1 << 1)) != 0'
      three_d_layer:
        value: '(attributes[1] & (1 << 2)) != 0'
      solo:
        value: '(attributes[1] & (1 << 3)) != 0'
      markers_locked:
        value: '(attributes[1] & (1 << 4)) != 0'
      null_layer:
        value: '(attributes[1] & (1 << 7)) != 0'
      enabled:
        value: '(attributes[2] & (1 << 0)) != 0'
      audio_enabled:
        value: '(attributes[2] & (1 << 1)) != 0'
      effects_active:
        value: '(attributes[2] & (1 << 2)) != 0'
      motion_blur:
        value: '(attributes[2] & (1 << 3)) != 0'
      frame_blending:
        value: '(attributes[2] & (1 << 4)) != 0'
      locked:
        value: '(attributes[2] & (1 << 5)) != 0'
      shy:
        value: '(attributes[2] & (1 << 6)) != 0'
      collapse_transformation:
        value: '(attributes[2] & (1 << 7)) != 0'
  lhd3_body:
    seq:
      - size: 10
      - id: nb_keyframes
        type: u2
      - size: 6
      - id: len_keyframe
        type: u2
      - size: 3
      - id: keyframes_type_raw
        type: u1
    instances:
      keyframes_type:
        value: >-
          keyframes_type_raw == 1 and len_keyframe == 2246 ? property_value_type::lrdr :
          keyframes_type_raw == 1 and len_keyframe == 128 ? property_value_type::litm :
          keyframes_type_raw == 2 and len_keyframe == 1 ? property_value_type::gide :
          keyframes_type_raw == 4 and len_keyframe == 152 ? property_value_type::color :
          keyframes_type_raw == 4 and len_keyframe == 128 ? property_value_type::three_d :
          keyframes_type_raw == 4 and len_keyframe == 104 ? property_value_type::two_d_spatial :
          keyframes_type_raw == 4 and len_keyframe == 88 ? property_value_type::two_d :
          keyframes_type_raw == 4 and len_keyframe == 80 ? property_value_type::orientation :
          keyframes_type_raw == 4 and len_keyframe == 64 ? property_value_type::no_value :
          keyframes_type_raw == 4 and len_keyframe == 48 ? property_value_type::one_d :
          keyframes_type_raw == 4 and len_keyframe == 16 ? property_value_type::marker :
          property_value_type::unknown
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
  nmhd_body:
    seq:
      - size: 3
      - id: attributes
        size: 1
      - size: 4
      - id: frame_duration
        type: u4
      - size: 4
      - id: label
        type: u1
        enum: label
    instances:
      navigation:
        value: '(attributes[0] & 1) != 0'
      protected_region:
        value: '(attributes[0] & (1 << 1)) != 0'
      unknown:
        value: '(attributes[0] & (1 << 2)) != 0'
  nnhd_body:
    seq:
      - size: 8
      - id: time_display_type
        type: u1
        enum: time_display_type
      - id: footage_timecode_display_start_type
        type: u1
        enum: footage_timecode_display_start_type
      - size: 4
      - id: frame_rate
        type: u2
      - size: 4
      - id: frames_count_type
        type: u1
        enum: frames_count_type
      - size: 3
      - id: bits_per_channel
        type: u1
        enum: bits_per_channel
      - size: 15
  opti_body:
    seq:
      - id: asset_type
        size: 4
        type: strz
        encoding: ascii
        # enum: asset_type
      - id: asset_type_int
        type: u2
      - size: 4
        if: asset_type == "Soli"
      - id: color
        type: f4
        repeat: expr
        repeat-expr: 4
        if: asset_type == "Soli"
      - id: solid_name
        type: strz
        encoding: cp1250
        size: 256
        if: asset_type == "Soli"
      - size: 4
        if: asset_type_int == 2
      - id: placeholder_name
        type: strz
        encoding: cp1250
        size-eos: true
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
      - size: 15
      - id: property_control_type
        type: u1
        enum: property_control_type
      - id: name
        size: 32
        type: strz
        encoding: cp1250
      - size: 8
      - id: last_color
        type: u1
        repeat: expr
        repeat-expr: 4
        if: property_control_type == property_control_type::color
      - id: default_color
        type: u1
        repeat: expr
        repeat-expr: 4
        if: property_control_type == property_control_type::color
      - id: last_value
        type:
          switch-on: property_control_type
          cases:
            'property_control_type::scalar': s4
            'property_control_type::angle': s4
            'property_control_type::boolean': u4
            'property_control_type::enum': u4
            'property_control_type::slider': f8
        if: >-
          property_control_type == property_control_type::scalar
          or property_control_type == property_control_type::angle
          or property_control_type == property_control_type::boolean
          or property_control_type == property_control_type::enum
          or property_control_type == property_control_type::slider
      - id: last_value_x_raw
        type:
          switch-on: property_control_type
          cases:
            'property_control_type::two_d': s4
            'property_control_type::three_d': f8
        if: >-
          property_control_type == property_control_type::two_d
          or property_control_type == property_control_type::three_d
      - id: last_value_y_raw
        type:
          switch-on: property_control_type
          cases:
            'property_control_type::two_d': s4
            'property_control_type::three_d': f8
        if: >-
          property_control_type == property_control_type::two_d
          or property_control_type == property_control_type::three_d
      - id: last_value_z_raw
        type: f8
        if: property_control_type == property_control_type::three_d
      - id: nb_options
        type: s4
        if: property_control_type == property_control_type::enum
      - id: default
        type:
          switch-on: property_control_type
          cases:
            'property_control_type::boolean': u1
            'property_control_type::enum': s4
        if: >-
          property_control_type == property_control_type::boolean
          or property_control_type == property_control_type::enum
      - size: '(property_control_type == property_control_type::scalar ? 72 : property_control_type == property_control_type::color ? 64 : 52)'
        if: >-
          property_control_type == property_control_type::scalar
          or property_control_type == property_control_type::color
          or property_control_type == property_control_type::slider
      - id: min_value
        type: s2
        if: property_control_type == property_control_type::scalar
      - size: 2
        if: property_control_type == property_control_type::scalar
      - id: max_color
        type: u1
        repeat: expr
        repeat-expr: 4
        if: property_control_type == property_control_type::color
      - id: max_value
        type:
          switch-on: property_control_type
          cases:
            'property_control_type::scalar': s2
            'property_control_type::slider': f4
        if: >-
          property_control_type == property_control_type::scalar
          or property_control_type == property_control_type::slider
    instances:
      last_value_x:
        value: 'last_value_x_raw * (property_control_type == property_control_type::two_d ? 1/128 : 512)'
        if: >-
          property_control_type == property_control_type::two_d
          or property_control_type == property_control_type::three_d
      last_value_y:
        value: 'last_value_y_raw * (property_control_type == property_control_type::two_d ? 1/128 : 512)'
        if: >-
          property_control_type == property_control_type::two_d
          or property_control_type == property_control_type::three_d
      last_value_z:
        value: 'last_value_z_raw * 512'
        if: property_control_type == property_control_type::three_d
  sspc_body:
    seq:
      - size: 32
      - id: width
        type: u2
      - size: 2
      - id: height
        type: u2
      - id: duration_dividend
        type: u4
      - id: duration_divisor
        type: u4
      - size: 10
      - id: frame_rate_base
        type: u4
      - id: frame_rate_dividend
        type: u2
      - size: 110
      - id: start_frame
        type: u4
      - id: end_frame
        type: u4
    instances:
      duration:
        value: 'duration_dividend.as<f4> / duration_divisor.as<f4>'
      frame_rate:
        value: 'frame_rate_base + (frame_rate_dividend.as<f4> / (1 << 16))'
      frame_duration:
        value: 'duration * frame_rate'
  tdb4_body:
    seq:
      - size: 2
      - id: dimensions
        type: u2
        doc: Number of values in a multi-dimensional
      - id: attributes
        size: 2
      - size: 1
      - size: 1
        doc: Some sort of flag, it has value 03 for position properties
      - size: 2
      - size: 2
      - size: 2
        doc: Always 0000 ?
      - size: 2
        doc: 2nd most significant bit always on, perhaps some kind of flag
      - type: f8
        doc: Most of the time 0.0001
      - type: f8
        doc: Most of the time 1.0, sometimes 1.777
      - type: f8
        doc: Always 1.0?
      - type: f8
        doc: Always 1.0?
      - type: f8
        doc: Always 1.0?
      - id: property_control_type
        size: 4
      - size: 1
        doc: Seems correlated with the previous byte, 04 for enum properties
      - size: 7
        doc: Bunch of 00
      - id: animated
        type: u1
      - size: 7
        doc: Bunch of 00
      - size: 4
        doc: Usually 0, probs flags
      - size: 4
        doc: Most likely flags, only last byte seems to contain data
      - type: f8
        doc: Always 0.0?
      - type: f8
        doc: Mostly 0.0, sometimes 0.333
      - type: f8
        doc: Always 0.0?
      - type: f8
        doc: Mostly 0.0, sometimes 0.333
      - id: expression_flags
        size: 4
      - size: 4
        doc: Probs some flags
    instances:
      static:
        value: '(attributes[1] & 1) != 0'
      is_spatial:
        value: '(attributes[1] & (1 << 3)) != 0'
      no_value:
        value: '(property_control_type[1] & 1) != 0'
      color:
        value: '(property_control_type[3] & 1) != 0'
      integer:
        value: '(property_control_type[3] & (1 << 2)) != 0'
      vector:
        value: '(property_control_type[3] & (1 << 3)) != 0'
      expression_enabled:
        value: '(expression_flags[3] & 1) == 0'
  tdsb_body:
    seq:
      - id: flags
        size: 4
    instances:
      locked_ratio:
        value: '(flags[2] & 1 << 4) != 0'
      enabled:
        value: '(flags[3] & 1) != 0'
      dimensions_separated:
        value: '(flags[3] & 1 << 1) != 0'
  utf8_body:
    seq:
      - id: data
        type: str
        encoding: utf8
        size-eos: true

enums:
  bits_per_channel: # project bit bits_per_channel
    0: bpc_8
    1: bpc_16
    2: bpc_32
  item_type: # type of item. See: http://docs.aenhancers.com/items/item/#item-item_type
    1: folder
    4: composition
    7: footage
  asset_type:
    2: placeholder
    9: solid
  layer_type:
    0: footage
    1: light
    2: camera
    3: text
    4: shape
  track_matte_type:
    0: none
    1: no_track_matte
    2: alpha
    3: alpha_inverted
    4: luma
    5: luma_inverted
  label:
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
  layer_quality:
    0: wireframe
    1: draft
    2: best
  frame_blending_type:
    0: frame_mix
    1: pixel_motion
    2: no_frame_blend
  sampling_quality:
    0: bilinear
    1: bicubic
  keyframe_interpolation_type:
    1: linear
    2: bezier
    3: hold
  property_control_type:
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
  blending_mode:
    2: normal
    3: dissolve
    4: add
    5: multiply
    6: screen
    7: overlay
    8: soft_light
    9: hard_light
    10: darken
    11: lighten
    12: classic_difference
    13: hue
    14: saturation
    15: color
    16: luminosity
    17: stencil_alpha
    18: stencil_luma
    19: silhouette_alpha
    20: silhouette_luma
    21: luminescent_premul
    22: alpha_add
    23: classic_color_dodge
    24: classic_color_burn
    25: exclusion
    26: difference
    27: color_dodge
    28: color_burn
    29: linear_dodge
    30: linear_burn
    31: linear_light
    32: vivid_light
    33: pin_light
    34: hard_mix
    35: lighter_color
    36: darker_color
    37: subtract
    38: divide
  time_display_type:
    0: timecode
    1: frames
  footage_timecode_display_start_type:
    0: ftcs_start_0
    1: ftcs_use_source_media
  frames_count_type:
    0: fc_start_0
    1: fc_start_1
    2: fc_timecode_conversion
  property_value_type:
    0:
      id: unknown
      doc: unknown
    1:
      id: no_value
      doc: Stores no data
    2:
      id: three_d_spatial
      doc: |
        Array of three floating-point positional values.
        For example, an Anchor Point value might be [10.0, 20.2, 0.0]
    3:
      id: three_d
      doc: |
        Array of three floating-point quantitative values.
        For example, a Scale value might be [100.0, 20.2, 0.0]
    4:
      id: two_d_spatial
      doc: |
        Array of 2 floating-point positional values.
        For example, an Anchor Point value might be [5.1, 10.0]
    5:
      id: two_d
      doc: |
        Array of 2 floating-point quantitative values.
        For example, a Scale value might be [5.1, 100.0]
    6:
      id: one_d
      doc: A floating-point value.
    7:
      id: color
      doc: |
        Array of 4 floating-point values in the range [0.0..1.0].
        For example, [0.8, 0.3, 0.1, 1.0]
    8:
      id: custom_value
      doc: Custom property value, such as the Histogram property for the Levels effect.
    9:
      id: marker
      doc: MarkerValue object
    10:
      id: layer_index
      doc: Integer; a value of 0 means no layer.
    11:
      id: mask_index
      doc: Integer; a value of 0 means no mask.
    12:
      id: shape
      doc: Shape object
    13:
      id: text_document
      doc: TextDocument object
    14:
      id: lrdr
      doc: Render queue data
    15:
      id: litm
      doc: Render Queue items
    16:
      id: gide
      doc: ??
    17:
      id: orientation
      doc: ??
  # ae_version:
  #   0x5c06073806b4: v15_0
  #   0x5d040b0006eb: v16_0
  #   0x5d040b000e30: v16_0_1
  #   0x5d050b009637: v16_1_2
  #   0x5d050b009e05: v16_1_3
  #   0x5d094b08062b: v17_0
  #   0x5d0b0b08263b: v17_0_4
  #   0x5d1b0b110e08: v18_2_1
  #   0x5d1d0b120626: v18_4
  #   0x5d1d0b70066f: v22_0
  #   0x5d2b0b33063b: v22_6
  #   0x5e030b390e03: v23_2_1