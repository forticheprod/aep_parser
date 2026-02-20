from aep_parser import parse
from pathlib import Path

samples = [
    "samples/models/output_module/output_color_space_wsrgb.aep",
    "samples/models/output_module/output_color_space_working_color_space.aep",
    "samples/models/output_module/output_color_space_apple_rgb.aep",
    "samples/models/output_module/output_color_space_wscrgb.aep",
    "samples/models/output_module/output_color_space_wide_gamut_rgb.aep",
    "samples/models/output_module/output_color_space_smpte-c.aep",
    "samples/models/output_module/output_color_space_p3_d65_pq.aep",
]

for sp in samples:
    p = parse(sp)
    print(f"File: {Path(sp).name}")
    for i, item in enumerate(p.project.render_queue.items):
        for j, om in enumerate(item.output_modules):
            profile_id = getattr(om, 'output_profile_id', None)
            if profile_id is None:
                # check settings
                profile_hex = om.settings.get('Output Profile ID')
            else:
                # Kaitai may expose raw bytes on the ldat object; our parser stores it in settings too
                try:
                    profile_hex = profile_id.hex()
                except Exception:
                    profile_hex = repr(profile_id)
            print(f"  item={i} om={j} output_profile_id={profile_hex} output_color_space={getattr(om,'output_color_space', None)} settings_output_color_space={om.settings.get('Output Color Space')} profile_name={om.settings.get('Output Profile Name')}")
    print()
