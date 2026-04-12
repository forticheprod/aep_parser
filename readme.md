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

### uv (recommended)
```sh
uv add aep-parser
```

### pip
```sh
pip install aep-parser
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>




<!-- USAGE EXAMPLES -->
## Usage

```python
import aep_parser

app = aep_parser.parse("myproject.aep")
comp = app.project.compositions[0]

# Modify composition settings
comp.frame_rate = 24

# Modify a layer property
comp.layers[0].transform.opacity.value = 50

# Save to a new file
app.save("modified.aep")
```

_For more examples, see the [Quick Start guide](https://forticheprod.github.io/aep_parser/quickstart/)._

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
