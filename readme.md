<a name="readme-top"></a>

<!-- PROJECT NAME -->
<br />
<div align="center">
  <h3 align="center">aep_parser</h3>
  <p align="center">
    An After Effects file parser in Python!
    <br />
    <a href="https://forticheprod.github.io/aep_parser/"><strong>Explore the docs »</strong></a>
    <br />
  </p>
</div>



<!-- ABOUT THE PROJECT -->
## About The Project


This as a .aep (After Effects Project) parser in Python. After Effects files (.aep) are mostly binary files, encoded in RIFX format. This parser uses [Kaitai Struct](https://kaitai.io/) to parse .aep files and return a Project object containing items, layers, effects and properties. The API is as close as possible to the [ExtendScript API](https://ae-scripting.docsforadobe.dev/), with a few nice additions like iterators instead of collection items.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- INSTALLATION -->
## Installation

```sh
pip install aep-parser
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>




<!-- USAGE EXAMPLES -->
## Usage

```python
import aep_parser

# Parse an After Effects project
app = aep_parser.parse("path/to/project.aep")
project = app.project

# Access application-level info
print(f"AE Version: {app.version}")

# Access every item
for item in project:
    print(f"{item.name} ({type(item).__name__})")

# Get a composition by name and its layers
comp = next(c for c in project.compositions if c.name == "Comp 1")
for layer in comp.layers:
    print(f"  Layer: {layer.name}, in={layer.in_point}s, out={layer.out_point}s")

    # Access layer's source (for AVLayer)
    if hasattr(layer, "source") and layer.source:
        print(f"    Source: {layer.source.name}")
        # Get file path if source is footage with a file
        if hasattr(layer.source, "file"):
            print(f"    File: {layer.source.file}")

# Access render queue
for rq_item in project.render_queue.items:
    print(f"Render: {rq_item.comp_name}")
    for om in rq_item.output_modules:
        # Settings are a dict with ExtendScript keys
        video_on = om.settings.get("Video Output", False)
        print(f"  Output: {om.name}, video={video_on}")
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>




<!-- ROADMAP -->
## Roadmap

See the [open issues](https://github.com/forticheprod/aep_parser/issues) for a full list of proposed features and known issues.

If you encounter a bug, please submit an issue and attach a basic scene to reproduce your issue.

<p align="right">(<a href="#readme-top">back to top</a>)</p>




<!-- CONTRIBUTING -->
## Contributing

See the full [Contributing Guide](https://github.com/forticheprod/aep_parser/blob/main/CONTRIBUTING.md) on GitHub.

<p align="right">(<a href="#readme-top">back to top</a>)</p>




<!-- LICENSE -->
## License

Distributed under the MIT License.

<p align="right">(<a href="#readme-top">back to top</a>)</p>




<!-- CONTACT -->
## Contact

Aurore Delaunay - del-github@blurme.net

<p align="right">(<a href="#readme-top">back to top</a>)</p>




<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [aftereffects-aep-parser in Go](https://github.com/boltframe/aftereffects-aep-parser)
* [Kaitai Struct](https://kaitai.io)
* [The invaluable Lottie Docs](https://github.com/hunger-zh/lottie-docs/blob/main/docs/aep.md)
* [After Effects Scripting Guide](https://ae-scripting.docsforadobe.dev/)
* [AE version parsing](https://github.com/tinogithub/aftereffects-version-check)

<p align="right">(<a href="#readme-top">back to top</a>)</p>
