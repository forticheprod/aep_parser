meta:
  id: aep
  endian: be
  file-extension: aep

seq:
  - id: header
    contents: RIFX
  - id: len_data
    type: u4
  - id: format
    contents: "Egg!"
  - id: data
    type: chunks
    size: len_data - format._sizeof
  - id: xmp_packet
    type: str
    encoding: UTF-8
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
        encoding: ASCII
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
            '"cdrp"': cdrp_body # Composition drop frame
            '"pjef"': utf8_body # Effect names
            '"cmta"': utf8_body # Comment data
            '"fdta"': fdta_body # Folder data
            '"RCom"': child_utf8_body # Render queue item comment. Contains a single utf-8 chunk
            '"nnhd"': nnhd_body # Project data
            '"head"': head_body # Contains AE version and file revision
            '"Roou"': roou_body # Output module settings
            '"Rout"': rout_body # Render queue item flags
            '"acer"': acer_body # Compensate for Scene-Referred Profiles setting
            '"dwga"': dwga_body # Working gamma setting
            '"fips"': fips_body # Folder item panel settings (viewer state)
            '"fcid"': fcid_body # Active composition item ID
            '"foac"': foac_body # Viewer outer tab active flag
            '"fiac"': fiac_body # Viewer inner tab active flag
            '"fitt"': fitt_body # Viewer inner tab type label
            '"fivi"': fivi_body # Viewer inner active view index
            '"fivc"': fivc_body # Viewer inner view count
            _: ascii_body
      - id: padding
        size: 1
        if: (len_data % 2) != 0
  acer_body:
    doc: |
      Compensate for Scene-Referred Profiles setting in Project Settings.
      This setting affects how scene-referred color profiles are handled.
    seq:
      - id: compensate_for_scene_referred_profiles
        type: u1
        doc: Whether to compensate for scene-referred profiles (0=false, 1=true)
  dwga_body:
    doc: |
      Working gamma setting. Indicates the gamma value used for color management.
    seq:
      - id: working_gamma_selector
        type: u1
        doc: Working gamma selector (0=2.2, 1=2.4)
      - size: 3
        doc: Unknown bytes 1-3
  ascii_body:
    seq:
      - id: contents
        size-eos: true
  cdat_body:
    seq:
      - id: value
        type: f8
        repeat: expr
        repeat-expr: '_parent.len_data / 8'
  cdrp_body:
    doc: |
      Composition drop frame setting.
      When true, the composition uses drop-frame timecode.
    seq:
      - id: drop_frame
        type: u1
        doc: Whether the composition uses drop-frame timecode (0=false, 1=true)
  fips_body:
    doc: |
      Folder item panel settings. Stores viewer panel state including
      Draft 3D mode, view options (channels, exposure, zoom, etc.), and
      toggle flags (guides, rulers, grid, etc.). There are typically 4
      fips chunks per viewer group, one for each AE composition viewer
      panel. Total size is 96 bytes.
    seq:
      # Bytes 0-6: unknown
      - size: 7
        doc: Unknown bytes 0-6
      # Byte 7: channel display mode
      - id: channels
        type: u1
        doc: |
          Channel display mode. 0=RGB, 1=Red, 2=Green, 3=Blue,
          4=Alpha, 8=RGB Straight.
      # Bytes 8-10: unknown
      - size: 3
        doc: Unknown bytes 8-10
      # Byte 11: proportional_grid and title_action_safe flags
      - type: b6  # skip bits 7-2
      - id: proportional_grid
        type: b1  # bit 1 (value 0x02)
        doc: Whether the proportional grid overlay is displayed
      - id: title_action_safe
        type: b1  # bit 0 (value 0x01)
        doc: Whether title/action safe guides are displayed
      # Byte 12: draft_3d flag
      - type: b5  # skip bits 7-3
      - id: draft_3d
        type: b1  # bit 2 (value 0x04)
        doc: Whether Draft 3D mode is enabled for this viewer panel
      - type: b2  # skip bits 1-0
      # Byte 13: fast_preview_adaptive flag
      - type: b7  # skip bits 7-1
      - id: fast_preview_adaptive
        type: b1  # bit 0 (value 0x01)
        doc: Whether adaptive resolution fast preview is enabled
      # Byte 14: roi, rulers, fast_preview_wireframe flags
      - id: region_of_interest
        type: b1  # bit 7 (value 0x80)
        doc: Whether the region of interest selection is active
      - id: rulers
        type: b1  # bit 6 (value 0x40)
        doc: Whether rulers are displayed
      - type: b1  # skip bit 5
      - id: fast_preview_wireframe
        type: b1  # bit 4 (value 0x10)
        doc: Whether wireframe fast preview mode is enabled
      - type: b4  # skip bits 3-0
      # Byte 15: transparency_grid, mask_and_shape_path flags
      - id: transparency_grid
        type: b1  # bit 7 (value 0x80)
        doc: Whether the transparency checkerboard is displayed
      - type: b2  # skip bits 6-5
      - id: mask_and_shape_path
        type: b1  # bit 4 (value 0x10)
        doc: Whether mask and shape paths are visible
      - type: b4  # skip bits 3-0
      # Bytes 16-22: unknown
      - size: 7
        doc: Unknown bytes 16-22
      # Byte 23: grid and guides flags
      - type: b4  # skip bits 7-4
      - id: grid
        type: b1  # bit 3 (value 0x08)
        doc: Whether the grid overlay is displayed
      - type: b2  # skip bits 2-1
      - id: guides_visibility
        type: b1  # bit 0 (value 0x01)
        doc: Whether guides are visible
      # Bytes 24-68: viewport data and unknown
      - size: 45
        doc: Unknown bytes 24-68 (includes viewport coordinates)
      # Byte 69: zoom type
      - id: zoom_type
        type: u1
        doc: |
          Zoom mode. 0=custom manual zoom, 1=fit, 2=fit up to 100%%.
      # Bytes 70-71: unknown
      - size: 2
        doc: Unknown bytes 70-71
      # Bytes 72-79: zoom level (float64 big-endian)
      - id: zoom
        type: f8be
        doc: |
          Zoom factor where 1.0 = 100%%. E.g. 0.25 = 25%%,
          16.0 = 1600%%.
      # Bytes 80-83: exposure (float32 big-endian)
      - id: exposure
        type: f4be
        doc: |
          Exposure value in stops. 0.0 = no adjustment.
          Range is -40.0 to 40.0.
      # Byte 84: unknown
      - size: 1
        doc: Unknown byte 84
      # Byte 85: use_display_color_management flag
      - type: b7  # skip bits 7-1
      - id: use_display_color_management
        type: b1  # bit 0 (value 0x01)
        doc: Whether display color management is enabled
      # Byte 86: auto_resolution flag
      - type: b7  # skip bits 7-1
      - id: auto_resolution
        type: b1  # bit 0 (value 0x01)
        doc: Whether auto resolution is enabled for the viewer
      # Bytes 87-95: remaining unknown bytes
      - size-eos: true
  foac_body:
    doc: |
      Viewer outer tab active flag. When non-zero, the outer panel
      (e.g. Timeline) is focused.
    seq:
      - id: active
        type: u1
        doc: Whether the outer tab is active (0=false, 1=true)
  fiac_body:
    doc: |
      Viewer inner tab active flag. When non-zero, the inner tab
      (e.g. Composition, Layer, Footage) is focused.
    seq:
      - id: active
        type: u1
        doc: Whether the inner tab is active (0=false, 1=true)
  fitt_body:
    doc: |
      Viewer inner tab type label. An ASCII string identifying the
      viewer type (e.g. "AE Composition", "AE Layer", "AE Footage").
    seq:
      - id: label
        type: str
        encoding: ASCII
        size-eos: true
        doc: The inner tab type label
  fivi_body:
    doc: |
      Viewer inner active view index. The zero-based index of the
      currently active view within the inner tab.
    seq:
      - id: active_view_index
        type: u4
        doc: Zero-based index of the active view
  fivc_body:
    doc: |
      Viewer inner view count. The number of views in the inner tab.
    seq:
      - id: view_count
        type: u2
        doc: Number of views in the inner tab
  fcid_body:
    doc: |
      Active composition item ID. Stores the item ID of the currently
      active (most recently focused) composition in the project.
    seq:
      - id: active_item_id
        type: u4
        doc: The item ID of the active composition
  cdta_body:
    seq:
      - id: resolution_factor
        type: u2
        repeat: expr
        repeat-expr: 2
      - size: 1
      - id: time_scale
        type: u2
      - size: 14
      - id: time_raw
        type: s2
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
      - id: preserve_nested_resolution
        type: b1  # bit 7
      - type: b1  # skip bit 6
      - id: preserve_nested_frame_rate
        type: b1  # bit 5
      - id: frame_blending
        type: b1  # bit 4
      - id: motion_blur
        type: b1  # bit 3
      - type: b2  # skip bits 2-1
      - id: hide_shy_layers
        type: b1  # bit 0
      - id: width
        type: u2
      - id: height
        type: u2
      - id: pixel_ratio_width
        type: u4
      - id: pixel_ratio_height
        type: u4
      - size: 4
      - id: frame_rate_integer
        type: u2
      - id: frame_rate_fractional
        type: u2
      - size: 4
      - id: display_start_time_dividend
        type: s4
        doc: |
          Signed 32-bit dividend for display start time. Negative values
          represent compositions whose timeline starts before frame 0.
      - id: display_start_time_divisor
        type: u4
      - size: 2
      - id: shutter_angle
        type: u2
      - size: 4
      - id: shutter_phase
        type: s4
      - size: 12
      - id: motion_blur_adaptive_sample_limit
        type: s4
      - id: motion_blur_samples_per_frame
        type: s4
    instances:
      display_start_time:
        value: 'display_start_time_dividend * 1.0 / display_start_time_divisor'
      frame_rate:
        value: 'frame_rate_integer + (frame_rate_fractional * 1.0 / 65536)'
      display_start_frame:
        value: 'display_start_time * frame_rate'
      duration:
        value: 'duration_dividend * 1.0 / duration_divisor'
      frame_duration:
        value: 'duration * frame_rate'
      pixel_aspect:
        value: 'pixel_ratio_width * 1.0 / pixel_ratio_height'
      frame_time:
        value: 'time_raw * 1.0 / time_scale'
      time:
        value: 'frame_time / frame_rate'
      frame_in_point:
        value: 'display_start_frame + in_point_raw * 1.0 / time_scale'
      in_point:
        value: 'frame_in_point / frame_rate'
      frame_out_point:
        value: 'display_start_frame + (out_point_raw == 0xffff ? frame_duration : (out_point_raw * 1.0 / time_scale))'
      out_point:
        value: 'frame_out_point / frame_rate'
  child_utf8_body:
    seq:
      - id: chunk
        type: chunk
  fdta_body:
    seq:
      - size: 1
  head_body:
    doc: |
      After Effects file header. Contains version info encoded as a 32-bit value.
      Major version = MAJOR-A * 8 + MAJOR-B
      See: https://github.com/tinogithub/aftereffects-version-check
    seq:
      - size: 4
        doc: Reserved/unknown bytes before version
      # Version bits (32 bits total, MSB first)
      - type: b1
        doc: Bit 31 - reserved
      - id: ae_version_major_a
        type: b5
        doc: Bits 30-26 - high bits of major version
      - id: ae_version_os
        type: b4
        doc: Bits 25-22 - OS code (12=Windows, 13=Mac, 14=Mac ARM64)
      - id: ae_version_major_b
        type: b3
        doc: Bits 21-19 - low bits of major version
      - id: ae_version_minor
        type: b4
        doc: Bits 18-15 - minor version number
      - id: ae_version_patch
        type: b4
        doc: Bits 14-11 - patch version number
      - type: b1
        doc: Bit 10 - reserved
      - id: ae_version_beta_flag
        type: b1
        doc: Bit 9 - beta flag (false=beta, true=release)
      - type: b1
        doc: Bit 8 - reserved
      - id: ae_build_number
        type: b8
        doc: Bits 7-0 - build number
      - size: 10
        doc: Padding before file_revision
      - id: file_revision
        type: u2
    instances:
      ae_version_major:
        value: ae_version_major_a * 8 + ae_version_major_b
        doc: Full major version number (e.g., 25)
      ae_version_beta:
        value: not ae_version_beta_flag
        doc: True if beta version
  idta_body:
    seq:
      - id: item_type
        type: u2
        enum: item_type
      - size: 14
      - id: id
        type: u4
      - size: 38
      - id: label
        type: u1
        enum: label
  ldat_body:
    seq:
      - id: items
        size-eos: true
  roou_body:
    doc: Output module settings (154 bytes)
    seq:
      - id: magic
        size: 4
        doc: Magic bytes, typically "FXTC"
      - id: video_codec
        type: str
        size: 4
        encoding: ASCII
        doc: Video codec 4-char code
      - size: 8
        doc: Unknown bytes 8-15
      - id: starting_number
        type: u4
        doc: Starting frame number for image sequence output (bytes 16-19)
      - size: 6
        doc: Unknown bytes 20-25
      - id: format_id
        type: str
        size: 4
        encoding: ASCII
        doc: |
          Output format 4-char identifier (e.g. ".AVI", "H264", "TIF ", "8BPS",
          "png!", "JPEG", "MooV", "oEXR", "AIFF", "wao_", "Mp3 ", "sDPX",
          "SGI ", "IFF ", "TPIC", "RHDR")
      - size: 2
        doc: Unknown bytes 30-31
      - size: 4
        doc: Unknown bytes 32-35
      - id: width
        type: u2
        doc: Output width in pixels (0 when video disabled)
      - size: 2
        doc: Unknown bytes 38-39
      - id: height
        type: u2
        doc: Output height in pixels (0 when video disabled)
      - size: 25
        doc: Unknown bytes 42-66
      - id: frame_rate
        type: u1
        doc: Frame rate in fps
      - size: 3
        doc: Unknown bytes 68-70
      - id: depth
        type: u1
        doc: Color depth in bits per pixel (24=Millions/8bpc, 48=Trillions/16bpc, 96=Floating/32bpc)
      - size: 5
        doc: Unknown bytes 72-76
      - id: color_premultiplied
        type: u1
        doc: Color premultiplied flag (0=no, 1=yes)
      - size: 3
        doc: Unknown bytes 78-80
      - id: color_matted
        type: u1
        doc: Color matted flag (0=no, 1=yes)
      - size: 18
        doc: Unknown bytes 82-99
      - id: audio_sample_rate
        type: f8
        doc: Audio sample rate in Hz (e.g. 8000, 22050, 44100, 48000, 96000)
      - id: audio_disabled_hi
        type: u1
        doc: High byte of audio disabled flag (0xFF when disabled)
      - id: audio_format
        type: u1
        doc: Audio format/depth indicator (2=16-bit, 3=24-bit, 4=32-bit)
      - size: 1
        doc: Unknown byte 110
      - id: audio_bit_depth
        type: u1
        doc: Audio bit depth indicator (1=8-bit, 2=16-bit, 4=32-bit)
      - size: 1
        doc: Unknown byte 112
      - id: audio_channels
        type: u1
        doc: Audio channels (1=mono, 2=stereo)
      - id: remaining
        size-eos: true
        doc: Remaining bytes to end of chunk
    instances:
      video_output:
        value: width > 0 or height > 0
        doc: True when video output is enabled (width or height non-zero)
      output_audio:
        value: audio_disabled_hi != 0xFF
  rout_body:
    doc: Render queue item flags (4-byte header + 4 bytes per item)
    seq:
      - size: 4
        doc: Header bytes
      - id: items
        type: rout_item
        repeat: eos
  rout_item:
    doc: Per-item render queue flags (4 bytes)
    seq:
      - type: b1  # skip bit 7
      - id: render
        type: b1  # bit 6
        doc: True when item is set to render when queue is started
      - type: b6  # skip bits 5-0
      - size: 3
        doc: Remaining bytes
  output_module_settings_ldat_body:
    doc: |
      Per-output-module settings chunk (128 bytes).
      Used under LIST:list within LIST:LItm for each render queue item.
      Note: The actual comp_id is stored in render_settings_ldat_body, not here.
    seq:
      - size: 7
        doc: Unknown bytes 0-6
      - type: b1
        doc: Unknown bit 7
      - id: include_source_xmp
        type: b1
        doc: Include source XMP metadata in output (bit 6)
      - type: b1
        doc: Unknown bit 5
      - id: use_region_of_interest
        type: b1
        doc: Use Region of Interest checkbox (bit 4)
      - id: use_comp_frame_number
        type: b1
        doc: Use Comp Frame Number checkbox (bit 3)
      - type: b3
        doc: Unknown bits 2-0
      - id: post_render_target_comp_id
        type: u4
        doc: |
          Composition ID for post-render action target.
          Only used when post_render_use_comp is 1 (use custom comp).
          When 0, uses the render queue item's comp.
      - size: 4
        doc: Unknown bytes 12-15
      - size: 3
        doc: Unknown bytes 16-18
      - id: channels
        type: u1
        doc: Output channels (0=RGB, 1=RGBA, 2=Alpha)
      - size: 3
        doc: Unknown bytes 20-22
      - id: resize_quality
        type: u1
        doc: Resize quality (byte 23, 0=low, 1=high)
      - size: 3
        doc: Unknown bytes 24-26
      - id: resize
        type: u1
        doc: Resize checkbox (byte 27, 0=off, 1=on)
      - size: 1
        doc: Unknown byte 28
      - id: lock_aspect_ratio
        type: u1
        doc: Lock Aspect Ratio checkbox (byte 29, 0=off, 1=on)
      - size: 1
        doc: Unknown byte 30
      - type: b7
        doc: Unknown bits 7-1 of byte 31
      - id: crop
        type: b1
        doc: Crop checkbox enabled (bit 0 of byte 31)
      - id: crop_top
        type: u2
        doc: Crop top value in pixels (bytes 32-33)
      - id: crop_left
        type: u2
        doc: Crop left value in pixels (bytes 34-35)
      - id: crop_bottom
        type: u2
        doc: Crop bottom value in pixels (bytes 36-37)
      - id: crop_right
        type: u2
        doc: Crop right value in pixels (bytes 38-39)
      - size: 7
        doc: Unknown bytes 40-46
      - id: include_project_link
        type: u1
        doc: Include project link in output (byte 47, 0=off, 1=on)
      - id: post_render_action
        type: u4
        doc: Post-render action (0=NONE, 1=IMPORT, 2=IMPORT_AND_REPLACE, 3=SET_PROXY)
      - id: post_render_use_comp
        type: u4
        doc: Post-render action target comp (0=use render queue item comp, 1=use custom comp)
      - id: remaining
        size: 72
        doc: Remaining bytes (56-127)
  render_settings_ldat_body:
    doc: Render settings ldat chunk (2246 bytes)
    seq:
      - size: 7
        doc: Unknown bytes 0-6
      - type: b5
        doc: Unknown bits 7-3
      - id: queue_item_notify
        type: b1
        doc: Queue item notify flag (bit 2)
      - type: b2
        doc: Unknown bits 1-0
      - id: comp_id
        type: u4
        doc: Composition ID being rendered
      - id: status
        type: u4
        doc: Render queue item status (0=NEEDS_OUTPUT, 1=UNQUEUED, 2=QUEUED, 3=RENDERING, 4=USER_STOPPED, 5=ERR_STOPPED, 6=DONE)
      - size: 4
        doc: Unknown bytes 16-19
      - id: time_span_start_frames
        type: u4
        doc: Time span start numerator (frame count)
      - id: time_span_start_timebase
        type: u4
        doc: Time span start denominator (timebase fps)
      - id: time_span_duration_frames
        type: u4
        doc: Time span duration numerator (frame count)
      - id: time_span_duration_timebase
        type: u4
        doc: Time span duration denominator (timebase fps)
      - size: 8
        doc: Unknown bytes 36-43
      - id: frame_rate_integer
        type: u2
        doc: Frame rate integer part in fps
      - id: frame_rate_fractional
        type: u2
        doc: Frame rate fractional part (divide by 65536)
      - size: 2
        doc: Unknown bytes 48-49
      - id: field_render
        type: u2
        doc: Field render setting (0=off, 1=upper first, 2=lower first)
      - size: 2
        doc: Unknown bytes 52-53
      - id: pulldown
        type: u2
        doc: 3:2 Pulldown setting (0=off, 1=WSSWW, 2=SSWWW, 3=SWWWS, 4=WWWSS, 5=WWSSW)
      - id: quality
        type: u2
        doc: Render quality (0=wireframe, 1=draft, 2=best)
      - id: resolution_x
        type: u2
        doc: Resolution factor X
      - id: resolution_y
        type: u2
        doc: Resolution factor Y
      - size: 2
        doc: Unknown bytes 62-63
      - id: effects
        type: u2
        doc: Effects setting (0=all on, 1=all off, 2=current settings)
      - size: 2
        doc: Unknown bytes 66-67
      - id: proxy_use
        type: u2
        doc: Proxy use setting (0=use all proxies, 1=use comp proxies only, 3=use no proxies)
      - size: 2
        doc: Unknown bytes 70-71
      - id: motion_blur
        type: u2
        doc: Motion blur setting (0=current settings, 1=off for all layers, 2=on for checked layers)
      - size: 2
        doc: Unknown bytes 74-75
      - id: frame_blending
        type: u2
        doc: Frame blending setting (0=current settings, 1=off for all layers, 2=on for checked layers)
      - size: 2
        doc: Unknown bytes 78-79
      - id: log_type
        type: u2
        doc: Log type (0=errors only, 1=errors+settings, 2=errors+per frame info)
      - size: 2
        doc: Unknown bytes 82-83
      - id: skip_existing_files
        type: u2
        doc: Skip existing files (0=off, 1=on)
      - size: 4
        doc: Unknown bytes 86-89
      - id: template_name
        type: strz
        size: 64
        encoding: ASCII
        doc: Render settings template name
      - size: 1990
        doc: Unknown bytes 154-2143
      - id: use_this_frame_rate
        type: u2
        doc: Use this frame rate flag (1=use custom frame rate)
      - size: 2
        doc: Unknown bytes 2146-2147
      - id: time_span_source
        type: u2
        doc: Time span source (0=length of comp, 1=work area only, 2=custom)
      - size: 14
        doc: Unknown bytes 2150-2163
      - id: solo_switches
        type: u2
        doc: Solo switches setting (0=current settings, 2=all off)
      - size: 2
        doc: Unknown bytes 2166-2167
      - id: disk_cache
        type: u2
        doc: Disk cache setting (0=read only, 2=current settings)
      - size: 2
        doc: Unknown bytes 2170-2171
      - id: guide_layers
        type: u2
        doc: Guide layers setting (0=current settings, 2=all off)
      - size: 6
        doc: Unknown bytes 2174-2179
      - id: color_depth
        type: u2
        doc: Color depth setting (0xFFFF=current, 0=8bpc, 1=16bpc, 2=32bpc)
      - size: 16
        doc: Unknown bytes 2182-2197
      - id: start_time
        type: u4
        doc: Render start timestamp (seconds since Mac HFS+ epoch Jan 1, 1904)
      - id: elapsed_seconds
        type: u4
        doc: Elapsed render time in seconds
      - id: remaining
        size: 40
        doc: Remaining bytes (2206-2245)
    instances:
      time_span_start:
        value: 'time_span_start_timebase != 0 ? time_span_start_frames * 1.0 / time_span_start_timebase : 0'
        doc: Time span start in seconds
      time_span_duration:
        value: 'time_span_duration_timebase != 0 ? time_span_duration_frames * 1.0 / time_span_duration_timebase : 0'
        doc: Time span duration in seconds
      frame_rate:
        value: 'frame_rate_integer + (frame_rate_fractional * 1.0 / 65536)'
        doc: Frame rate in fps (integer + fractional)
  ldat_item:
    params:
      - id: item_type
        type: u1
        enum: ldat_item_type
    seq:
      - size: 1
      - id: time_raw
        type: s2
        doc: |
          Keyframe time in time-scale units. Signed 16-bit; negative values
          occur for keyframes positioned before the layer's start (e.g.
          composition markers).
      - size: 2
      - id: keyframe_interpolation_type
        type: u1
      - id: label
        type: u1
        enum: label
      - type: b2  # skip first 2 bits
      - id: roving_across_time
        type: b1  # bit 5
      - id: auto_bezier
        type: b1  # bit 4
      - id: continuous_bezier
        type: b1  # bit 3
      - type: b3  # skip remaining 3 bits
      - id: kf_data
        type:
          switch-on: item_type
          cases:
            'ldat_item_type::unknown': kf_unknown_data
            'ldat_item_type::lrdr': render_settings_ldat_body
            'ldat_item_type::litm': output_module_settings_ldat_body
            'ldat_item_type::gide': kf_unknown_data
            'ldat_item_type::color': kf_color
            'ldat_item_type::three_d_spatial': kf_position(3)
            'ldat_item_type::three_d': kf_multi_dimensional(3)
            'ldat_item_type::two_d_spatial': kf_position(2)
            'ldat_item_type::two_d': kf_multi_dimensional(2)
            'ldat_item_type::orientation': kf_multi_dimensional(1)
            'ldat_item_type::no_value': kf_no_value
            'ldat_item_type::one_d': kf_multi_dimensional(1)
            'ldat_item_type::marker': kf_unknown_data
  kf_unknown_data:
    seq:
      - id: contents
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
      - id: num_value
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
        repeat-expr: num_value
      - id: tan_in
        type: f8
        repeat: expr
        repeat-expr: num_value
      - id: tan_out
        type: f8
        repeat: expr
        repeat-expr: num_value
  kf_multi_dimensional:
    params:
      - id: num_value
        type: u1
    seq:
      - id: value
        type: f8
        repeat: expr
        repeat-expr: num_value
      - id: in_speed
        type: f8
        repeat: expr
        repeat-expr: num_value
      - id: in_influence
        type: f8
        repeat: expr
        repeat-expr: num_value
      - id: out_speed
        type: f8
        repeat: expr
        repeat-expr: num_value
      - id: out_influence
        type: f8
        repeat: expr
        repeat-expr: num_value
  ldta_body:
    seq:
      - id: layer_id
        type: u4
      - id: quality
        type: u2
      - size: 2
      - id: stretch_dividend
        type: s4
      - id: start_time_dividend
        type: s4
        doc: Signed to allow negative start times
      - id: start_time_divisor
        type: u4
      - id: in_point_dividend
        type: s4
        doc: Signed, stored relative to start_time. Add start_time to get absolute in_point.
      - id: in_point_divisor
        type: u4
      - id: out_point_dividend
        type: s4
        doc: Signed, stored relative to start_time. Add start_time to get absolute out_point.
      - id: out_point_divisor
        type: u4
      - size: 1
      - type: b1  # skip bit 7
      - id: sampling_quality
        type: b1  # bit 6
      - id: environment_layer
        type: b1  # bit 5
      - id: characters_toward_camera
        type: b2  # bits 4-3
        doc: When value is 3 (0b11), layer has CHARACTERS_TOWARD_CAMERA auto-orient mode
      - id: frame_blending_type
        type: b1  # bit 2
      - id: guide_layer
        type: b1  # bit 1
      - type: b1  # skip bit 0
      - id: null_layer
        type: b1  # bit 7
      - type: b1  # skip bit 6
      - id: camera_or_poi_auto_orient
        type: b1  # bit 5
        doc: When true and three_d_layer is true, layer has CAMERA_OR_POINT_OF_INTEREST auto-orient mode
      - id: markers_locked
        type: b1  # bit 4
      - id: solo
        type: b1  # bit 3
      - id: three_d_layer
        type: b1  # bit 2
      - id: adjustment_layer
        type: b1  # bit 1
      - id: auto_orient_along_path
        type: b1  # bit 0
        doc: When true, layer has ALONG_PATH auto-orient mode
      - id: collapse_transformation
        type: b1  # bit 7
      - id: shy
        type: b1  # bit 6
      - id: locked
        type: b1  # bit 5
      - id: frame_blending
        type: b1  # bit 4
      - id: motion_blur
        type: b1  # bit 3
      - id: effects_active
        type: b1  # bit 2
      - id: audio_enabled
        type: b1  # bit 1
      - id: enabled
        type: b1  # bit 0
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
        encoding: windows-1252
      - size: 3
      - id: blending_mode
        type: u1
      - size: 3
      - id: preserve_transparency
        type: u1
      - size: 3
      - id: track_matte_type
        type: u1
      - id: stretch_divisor
        type: u4
      - size: 19
      - id: layer_type
        type: u1
        enum: layer_type
      - id: parent_id
        type: u4
      - size: 3
      - id: light_type
        type: u1
        doc: Type of light for light layers (0=parallel, 1=spot, 2=point, 3=ambient)
      - size: 20
      # - id: matte_layer_id
      #   type: u4
      #   doc: only for AE >= 23
    instances:
      start_time:
        value: 'start_time_dividend * 1.0 / start_time_divisor'
      in_point:
        value: 'in_point_dividend * 1.0 / in_point_divisor'
      out_point:
        value: 'out_point_dividend * 1.0 / out_point_divisor'
  lhd3_body:
    doc: |
      Header for item/keyframe lists. AE reuses this structure for:
      - Property keyframes (count = keyframe count, item_size = keyframe data size)
      - Render queue items (count = item count, item_size = 2246 for settings)
      - Output module items (count = item count, item_size = 128 for settings)
    seq:
      - size: 10
      - id: count
        type: u2
        doc: Number of items/keyframes in the associated ldat chunk
      - size: 6
      - id: item_size
        type: u2
        doc: Size in bytes of each item/keyframe in the associated ldat chunk
      - size: 3
      - id: item_type_raw
        type: u1
    instances:
      item_type:
        value: >-
          item_type_raw == 1 and item_size == 2246 ? ldat_item_type::lrdr :
          item_type_raw == 1 and item_size == 128 ? ldat_item_type::litm :
          item_type_raw == 2 and item_size == 1 ? ldat_item_type::gide :
          item_type_raw == 4 and item_size == 152 ? ldat_item_type::color :
          item_type_raw == 4 and item_size == 128 ? ldat_item_type::three_d :
          item_type_raw == 4 and item_size == 104 ? ldat_item_type::two_d_spatial :
          item_type_raw == 4 and item_size == 88 ? ldat_item_type::two_d :
          item_type_raw == 4 and item_size == 80 ? ldat_item_type::orientation :
          item_type_raw == 4 and item_size == 64 ? ldat_item_type::no_value :
          item_type_raw == 4 and item_size == 48 ? ldat_item_type::one_d :
          item_type_raw == 4 and item_size == 16 ? ldat_item_type::marker :
          ldat_item_type::unknown
  list_body:
    seq:
      - id: list_type
        type: str
        encoding: windows-1252
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
      - type: b5  # skip first 5 bits
      - id: unknown
        type: b1  # bit 2
      - id: protected_region
        type: b1  # bit 1
      - id: navigation
        type: b1  # bit 0
      - size: 4
      - id: frame_duration
        type: u4
      - size: 4
      - id: label
        type: u1
        enum: label
  nnhd_body:
    seq:
      - size: 8
      - id: feet_frames_film_type
        type: b1
        doc: Feet+Frames film type (0=MM35, 1=MM16)
      - id: time_display_type
        type: b7
        doc: Time display type (0=TIMECODE, 1=FRAMES)
      - id: footage_timecode_display_start_type
        type: u1
      - size: 1
      - type: b7
      - id: frames_use_feet_frames
        type: b1
        doc: Whether to use feet+frames for timecode display (0=false, 1=true)
      - size: 2
      - id: frame_rate
        type: u2
      - size: 4
      - id: frames_count_type
        type: u1
      - size: 3
      - id: bits_per_channel
        type: u1
      - id: transparency_grid_thumbnails
        type: u1
        doc: Whether transparency grid is shown in thumbnails (0=false, 1=true)
      - size: 5
        doc: Unknown bytes 26-30
      - type: b2
        doc: Unknown bits 7-6
      - id: linearize_working_space
        type: b1
        doc: Whether to linearize working space for blending (0=false, 1=true)
      - type: b5
        doc: Unknown bits 4-0
      - size: 8
        doc: Unknown bytes 32-39
  opti_body:
    seq:
      - id: asset_type
        size: 4
        type: strz
        encoding: ASCII
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
        encoding: windows-1252
        size: 256
        if: asset_type == "Soli"
      - size: 4
        if: asset_type_int == 2
      - id: placeholder_name
        type: strz
        encoding: windows-1252
        size-eos: true
        if: asset_type_int == 2
      # PSD-specific fields (Photoshop document layers)
      # Note: PSD sub-structure seems to use little-endian byte order...
      - size: 10
        if: asset_type == "8BPS"
        doc: Unknown PSD bytes 6-15
      - id: psd_layer_index
        type: u2
        if: asset_type == "8BPS"
        doc: |
          Zero-based index of this layer within the source PSD file.
          0 is typically the Background layer. 0xFFFF means
          merged/flattened (no specific layer).
      - size: 4
        if: asset_type == "8BPS"
        doc: Unknown PSD bytes 18-21 (contains reversed magic "SPB8")
      - size: 4
        if: asset_type == "8BPS"
        doc: Unknown PSD bytes 22-25
      - size: 4
        if: asset_type == "8BPS"
        doc: Unknown PSD bytes 26-29
      - id: psd_channels
        type: u1
        if: asset_type == "8BPS"
        doc: Number of color channels (3=RGB, 4=RGBA or CMYK)
      - size: 1
        if: asset_type == "8BPS"
        doc: Unknown PSD byte 31
      - id: psd_canvas_height
        type: u2le
        if: asset_type == "8BPS"
        doc: Full PSD canvas height in pixels
      - size: 2
        if: asset_type == "8BPS"
        doc: Unknown PSD bytes 34-35
      - id: psd_canvas_width
        type: u2le
        if: asset_type == "8BPS"
        doc: Full PSD canvas width in pixels
      - size: 2
        if: asset_type == "8BPS"
        doc: Unknown PSD bytes 38-39
      - id: psd_bit_depth
        type: u1
        if: asset_type == "8BPS"
        doc: Bit depth per channel (8=8bpc, 16=16bpc)
      - size: 7
        if: asset_type == "8BPS"
        doc: Unknown PSD bytes 41-47
      - id: psd_layer_count
        type: u1
        if: asset_type == "8BPS"
        doc: Total number of layers in the source PSD file
      - size: 29
        if: asset_type == "8BPS"
        doc: Unknown PSD bytes 49-77
      - id: psd_layer_top
        type: s4le
        if: asset_type == "8BPS"
        doc: Layer bounding box top coordinate in pixels (can be negative)
      - id: psd_layer_left
        type: s4le
        if: asset_type == "8BPS"
        doc: Layer bounding box left coordinate in pixels (can be negative)
      - id: psd_layer_bottom
        type: s4le
        if: asset_type == "8BPS"
        doc: Layer bounding box bottom coordinate in pixels
      - id: psd_layer_right
        type: s4le
        if: asset_type == "8BPS"
        doc: Layer bounding box right coordinate in pixels
      - size: 250
        if: asset_type == "8BPS"
        doc: Unknown PSD bytes 94-343
      - id: psd_group_name
        type: strz
        encoding: UTF-8
        size-eos: true
        if: asset_type == "8BPS"
        doc: PSD group/folder name that this layer belongs to (e.g. "PAINT 02")
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
        encoding: windows-1252
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
        value: 'last_value_x_raw * (property_control_type == property_control_type::two_d ? 1.0/128 : 512)'
        if: >-
          property_control_type == property_control_type::two_d
          or property_control_type == property_control_type::three_d
      last_value_y:
        value: 'last_value_y_raw * (property_control_type == property_control_type::two_d ? 1.0/128 : 512)'
        if: >-
          property_control_type == property_control_type::two_d
          or property_control_type == property_control_type::three_d
      last_value_z:
        value: 'last_value_z_raw * 512'
        if: property_control_type == property_control_type::three_d
  sspc_body:
    doc: |
      Source footage settings chunk. Contains dimension, timing, and alpha/field settings.
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
      - id: frame_rate_fractional
        type: u2
      - size: 7
      # Byte 69: alpha flags
      - type: b6  # skip bits 7-2
      - id: invert_alpha
        type: b1  # bit 1
        doc: True if the alpha channel should be inverted
      - id: premultiplied
        type: b1  # bit 0
        doc: True if alpha is premultiplied (matches alpha_mode=PREMULTIPLIED)
      # Bytes 70-72: premul color (RGB, 0-255)
      - id: premul_color_r
        type: u1
        doc: Red component of premultiply color (0-255)
      - id: premul_color_g
        type: u1
        doc: Green component of premultiply color (0-255)
      - id: premul_color_b
        type: u1
        doc: Blue component of premultiply color (0-255)
      - id: alpha_mode_raw
        type: u1
        doc: |
          Alpha interpretation mode. When no_alpha (3), the footage has no alpha channel.
      - size: 9
      - id: field_separation_type_raw
        type: u1
        doc: |
          0 = OFF, 1 = enabled (check field_order for UPPER vs LOWER)
      - size: 3
      - id: field_order
        type: u1
        doc: |
          Field order when field separation is enabled
      - size: 41
      - id: loop
        type: u1
        doc: Number of times to loop the footage (1 = no loop, 2+ = loop count)
      - size: 6
      - id: pixel_ratio_width
        type: u4
      - id: pixel_ratio_height
        type: u4
      - size: 5
      - id: conform_frame_rate
        type: u1
        doc: Target frame rate for conforming. 0 = no conforming.
      - size: 9
      - id: high_quality_field_separation
        type: u1
        doc: |
          When true (1), After Effects uses special algorithms for high-quality field separation.
      - size: 12
      - id: start_frame
        type: u4
      - id: end_frame
        type: u4
      - id: frame_padding
        type: u4
        doc: |
          Number of zero-padded digits used for frame numbers in image
          sequences. For example, 4 means frames are numbered as 0001,
          0002 etc. 0 for non-sequence footage.
    instances:
      duration:
        value: 'duration_dividend * 1.0 / duration_divisor'
      frame_rate:
        value: 'frame_rate_base + (frame_rate_fractional * 1.0 / 65536)'
      frame_duration:
        value: 'duration * frame_rate'
      pixel_aspect:
        value: 'pixel_ratio_width * 1.0 / pixel_ratio_height'
      has_alpha:
        value: alpha_mode_raw != 3
        doc: True if footage has an alpha channel (3 means no_alpha)
  tdb4_body:
    seq:
      - size: 2
      - id: dimensions
        type: u2
        doc: Number of values in a multi-dimensional
      - size: 1
      - type: b4  # skip bits 7-4
      - id: is_spatial
        type: b1  # bit 3
      - type: b2  # skip bits 2-1
      - id: static
        type: b1  # bit 0
      - size: 10
        doc: Unknown bytes including flags
      - id: unknown_floats
        type: f8
        repeat: expr
        repeat-expr: 5
        doc: Unknown f8 values (usually 0.0001, 1.0, 1.0, 1.0, 1.0)
      # property_control_type - 4 bytes
      - size: 1
      - type: b7  # skip bits 7-1
      - id: no_value
        type: b1  # bit 0
      - size: 1
      - type: b4  # skip bits 7-4
      - id: vector
        type: b1  # bit 3
      - id: integer
        type: b1  # bit 2
      - type: b1  # skip bit 1
      - id: color
        type: b1  # bit 0
      - size: 8
        doc: Unknown bytes including type correlated byte
      - id: animated
        type: u1
      - size: 15
        doc: Unknown bytes and flags
      - id: unknown_floats_2
        type: f8
        repeat: expr
        repeat-expr: 4
        doc: Unknown f8 values (usually 0.0, sometimes 0.333)
      - size: 3
      - type: b7  # skip first 7 bits
      - id: expression_disabled
        type: b1  # bit 0
      - size: 4
        doc: Unknown flags
    instances:
      expression_enabled:
        value: 'not expression_disabled'
  tdsb_body:
    seq:
      - size: 2   # skip first 2 bytes
      - type: b3  # skip first 3 bits
      - id: locked_ratio
        type: b1  # bit 4
      - type: b4  # skip remaining 4 bits
      - type: b6  # skip first 6 bits
      - id: dimensions_separated  
        type: b1  # bit 1
      - id: enabled
        type: b1  # bit 0
  utf8_body:
    seq:
      - id: contents
        type: str
        encoding: UTF-8
        size-eos: true

enums:
  item_type: # type of item. See: https://ae-scripting.docsforadobe.dev/item/item/#itemtypename
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
  ldat_item_type:
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
      doc: Render Queue Item settings
    15:
      id: litm
      doc: Output Module settings
    16:
      id: gide
      doc: ??
    17:
      id: orientation
      doc: ??
