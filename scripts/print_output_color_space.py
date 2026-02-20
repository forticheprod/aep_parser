from aep_parser import parse

for aep_path in (
    r"C:\Users\aurore.delaunay\git\aep_parser\samples\models\output_module\output_color_space_wsrgb.aep",
    r"C:\Users\aurore.delaunay\git\aep_parser\samples\models\output_module\output_color_space_working_color_space.aep",
    r"C:\Users\aurore.delaunay\git\aep_parser\samples\models\output_module\output_color_space_apple_rgb.aep",
    r"C:\Users\aurore.delaunay\git\aep_parser\samples\models\output_module\output_color_space_wscrgb.aep",
    r"C:\Users\aurore.delaunay\git\aep_parser\samples\models\output_module\output_color_space_wide_gamut_rgb.aep",
    r"C:\Users\aurore.delaunay\git\aep_parser\samples\models\output_module\output_color_space_smpte-c.aep",
    r"C:\Users\aurore.delaunay\git\aep_parser\samples\models\output_module\output_color_space_p3_d65_pq.aep",
):
    p = parse(aep_path)
    for i, item in enumerate(p.project.render_queue.items):
        for j, om in enumerate(item.output_modules):
            print(f"output_color_space={om.output_color_space!r}")
